import json
from datetime import datetime, timedelta
from temporalio import activity
from llm.client import get_llm_client
from llm.prompts import ANALYSIS_PROMPT, TOOL_SELECTION_PROMPT, MEMORY_UPDATE_PROMPT, WAKE_STRATEGY_PROMPT
from temporal.models.agent_decisions import Action
from temporal.activities.persistence import log_activity


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
    llm = get_llm_client()

    recent_events_str = json.dumps(
        [{"type": e.get("event_type"), "payload": e.get("payload")} for e in unprocessed_events[:10]],
        indent=2,
    )

    analysis_prompt = ANALYSIS_PROMPT.format(
        order_id=order_context.get("order_id", "Unknown"),
        base_instruction=supervisor_config.get("base_instruction", ""),
        extra_instructions="\n".join(extra_instructions) if extra_instructions else "None",
        memory_summary=memory_summary or "No prior memory",
        recent_events=recent_events_str or "No new events",
        trigger=trigger,
        order_context=json.dumps(order_context, indent=2),
    )

    # Try LLM call with fallback
    try:
        analysis = await llm.complete_json(analysis_prompt)
        await log_activity(
            run_id=run_id,
            kind="reasoning",
            payload={"trigger": trigger, "analysis": analysis, "timestamp": datetime.utcnow().isoformat()},
        )
    except Exception as e:
        print(f"⚠️  LLM analysis failed: {e}")
        # FALLBACK: Simple rule-based response when LLM is unavailable
        analysis = {
            "reasoning": f"Automated analysis (LLM unavailable): Processing {len(unprocessed_events)} events triggered by {trigger}.",
            "needs_action": False,
            "priority": "normal",
            "concerns": [],
            "is_terminal": False,
        }
        # Still log the fallback reasoning
        await log_activity(
            run_id=run_id,
            kind="reasoning",
            payload={"trigger": trigger, "analysis": analysis, "fallback": True, "error": str(e)[:200]},
        )

    # Rest of the function stays the same...
    actions = []
    if analysis.get("needs_action"):
        available_tools = "\n".join([f"- {t}" for t in supervisor_config.get("available_actions", [])])
        tool_prompt = TOOL_SELECTION_PROMPT.format(
            analysis=analysis.get("reasoning", ""),
            available_tools=available_tools,
            order_context=json.dumps(order_context, indent=2),
        )
        try:
            tool_response = await llm.complete_json(tool_prompt)
            for ad in tool_response.get("actions", []):
                actions.append(Action(name=ad.get("name", ""), args=ad.get("args", {}), reasoning=ad.get("reasoning", "")))
        except Exception as e:
            print(f"⚠️  Tool selection failed: {e}")
            # If payment failed, at least message customer
            has_payment_failed = any(e.get("event_type") == "payment_failed" for e in unprocessed_events)
            if has_payment_failed:
                actions.append(Action(name="message_customer", args={"message": "Payment issue detected. Please update payment method."}, reasoning="Automatic fallback"))
                actions.append(Action(name="create_internal_note", args={"note": "Payment failure detected - automated fallback response"}, reasoning="Automatic fallback"))

    # Memory update - works even if LLM is down
    events_summary = ", ".join([e.get("event_type", "unknown") for e in unprocessed_events[:5]])
    actions_summary = ", ".join([a.name for a in actions]) if actions else "none"
    
    if memory_summary:
        updated_memory = f"{memory_summary} | {trigger}: {events_summary}. Actions: {actions_summary}."
    else:
        updated_memory = f"Order monitoring started. {trigger}: {events_summary}. Actions: {actions_summary}."

    # Try LLM for better memory, fall back to rule-based
    try:
        memory_prompt = MEMORY_UPDATE_PROMPT.format(
            current_summary=memory_summary or "No prior memory",
            new_events=recent_events_str,
            reasoning=analysis.get("reasoning", ""),
            actions_taken=actions_summary,
        )
        memory_response = await llm.complete_json(memory_prompt)
        updated_memory = memory_response.get("updated_summary", updated_memory)
    except Exception:
        pass  # Use the rule-based memory above

    # Wake strategy
    try:
        wake_prompt = WAKE_STRATEGY_PROMPT.format(
            current_state=analysis.get("reasoning", ""),
            memory=updated_memory,
            aggressiveness=supervisor_config.get("wake_aggressiveness", "normal"),
        )
        wr = await llm.complete_json(wake_prompt)
        next_wake_at = datetime.fromisoformat(wr["next_wake_at"]) if wr.get("next_wake_at") else (datetime.utcnow() + timedelta(hours=1))
        wake_guidance = wr.get("wake_guidance", {})
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