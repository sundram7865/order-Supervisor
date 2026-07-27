import json
from temporalio import activity
from llm.client import get_llm_client
from temporal.activities.persistence import get_run_context, persist_run_state, log_activity


@activity.defn
async def generate_final_summary(run_id: str) -> dict:
    llm = get_llm_client()
    context = await get_run_context(run_id)

    run = context.get("run")
    activities = context.get("recent_activities", [])

    actions_taken = []
    events = []
    for a in activities:
        if a.kind == "action":
            actions_taken.append(a.payload)
        elif a.kind == "event":
            events.append(a.payload)

    prompt = f"""Generate a final summary for this completed order run.

== ORDER CONTEXT ==
{json.dumps(run.order_context if run else {}, indent=2)}

== MEMORY SUMMARY ==
{run.memory_summary if run else "No memory"}

== ACTIONS TAKEN ==
{json.dumps(actions_taken, indent=2)}

== ALL EVENTS ==
{json.dumps(events, indent=2)}

Return JSON with: summary, important_actions, key_learnings, feedback, metrics"""

    try:
        summary = await llm.complete_json(prompt)
    except Exception as e:
        summary = {
            "summary": f"Error generating summary: {str(e)[:200]}",
            "important_actions": [],
            "key_learnings": ["Automated summary generation failed"],
            "feedback": "Manual review recommended",
        }

    await persist_run_state(run_id, {"final_summary": summary, "status": "completed"})
    await log_activity(run_id=run_id, kind="final_output", payload=summary, importance="critical")
    return summary