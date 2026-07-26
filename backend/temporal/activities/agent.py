import json
from datetime import datetime, timedelta
from temporalio import activity
from ...llm.client import get_llm_client
from ...llm.prompts import (
    ANALYSIS_PROMPT,
    TOOL_SELECTION_PROMPT,
    MEMORY_UPDATE_PROMPT,
    WAKE_STRATEGY_PROMPT,
)
from ..models.agent_decisions import AgentDecision, Action
from .persistence import get_run_context, persist_run_state, log_activity


@activity.defn
async def run_agent_reasoning(
    run_id: str,
    trigger: str,
    supervisor_config: dict,
    memory_summary: str,
    extra_instructions: list,
    unprocessed_events: list,
    order_context: dict,
) -> dict:
    """Main agent reasoning activity - calls LLM for analysis and decisions."""

    llm = get_llm_client()

    # Step 1: Assemble context
    recent_events_str = json.dumps(
        [{"type": e.get("event_type"), "payload": e.get("payload")} for e in unprocessed_events[:10]],
        indent=2,
    )

    # Step 2: Analyze situation
    analysis_prompt = ANALYSIS_PROMPT.format(
        order_id=order_context.get("order_id", "Unknown"),
        base_instruction=supervisor_config.get("base_instruction", ""),
        extra_instructions="\n".join(extra_instructions) if extra_instructions else "None",
        memory_summary=memory_summary or "No prior memory",
        recent_events=recent_events_str or "No new events",
        trigger=trigger,
        order_context=json.dumps(order_context, indent=2),
    )

    try:
        analysis = await llm.complete_json(analysis_prompt)

        # Log the reasoning
        await log_activity(
            run_id=run_id,
            kind="reasoning",
            payload={
                "trigger": trigger,
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
    except Exception as e:
        # Graceful degradation on LLM error
        return {
            "reasoning": f"Error during analysis: {str(e)[:200]}",
            "actions": [],
            "updated_memory_summary": memory_summary,
            "next_wake_at": (datetime.utcnow() + timedelta(minutes=15)).isoformat(),
            "wake_guidance": {},
            "recommend_completion": False,
        }

    # Step 3: Select and execute tools if needed
    actions = []
    if analysis.get("needs_action"):
        available_tools = "\n".join(
            [f"- {tool}" for tool in supervisor_config.get("available_actions", [])]
        )

        tool_prompt = TOOL_SELECTION_PROMPT.format(
            analysis=analysis.get("reasoning", ""),
            available_tools=available_tools,
            order_context=json.dumps(order_context, indent=2),
        )

        try:
            tool_response = await llm.complete_json(tool_prompt)
            for action_data in tool_response.get("actions", []):
                actions.append(
                    Action(
                        name=action_data.get("name", ""),
                        args=action_data.get("args", {}),
                        reasoning=action_data.get("reasoning", ""),
                    )
                )
        except Exception:
            pass  # No actions if tool selection fails

    # Step 4: Update memory
    memory_prompt = MEMORY_UPDATE_PROMPT.format(
        current_summary=memory_summary or "No prior memory",
        new_events=recent_events_str,
        reasoning=analysis.get("reasoning", ""),
        actions_taken=", ".join([a.name for a in actions]) if actions else "None",
    )

    try:
        memory_response = await llm.complete_json(memory_prompt)
        updated_memory = memory_response.get("updated_summary", memory_summary)
    except Exception:
        updated_memory = memory_summary

    # Step 5: Decide wake strategy
    wake_prompt = WAKE_STRATEGY_PROMPT.format(
        current_state=analysis.get("reasoning", ""),
        memory=updated_memory,
        aggressiveness=supervisor_config.get("wake_aggressiveness", "normal"),
    )

    try:
        wake_response = await llm.complete_json(wake_prompt)
        next_wake_str = wake_response.get("next_wake_at")
        next_wake_at = datetime.fromisoformat(next_wake_str) if next_wake_str else None
        wake_guidance = wake_response.get("wake_guidance", {})
    except Exception:
        next_wake_at = datetime.utcnow() + timedelta(hours=1)
        wake_guidance = {}

    return {
        "reasoning": analysis.get("reasoning", ""),
        "actions": [{"name": a.name, "args": a.args, "reasoning": a.reasoning} for a in actions],
        "updated_memory_summary": updated_memory,
        "next_wake_at": next_wake_at.isoformat() if next_wake_at else None,
        "wake_guidance": wake_guidance,
        "recommend_completion": analysis.get("is_terminal", False),
    }