from temporalio import activity
from datetime import datetime
from .persistence import log_activity


@activity.defn
async def execute_action(action_name: str, run_id: str, args: dict):
    """Execute a business action and log it. All actions are mocked."""
    action_messages = {
        "message_fulfillment_team": f"📦 Fulfillment Team notified: {args.get('message', 'No details')}",
        "message_payments_team": f"💳 Payments Team notified: {args.get('message', 'No details')}",
        "message_logistics_team": f"🚚 Logistics Team notified: {args.get('message', 'No details')}",
        "message_customer": f"📧 Customer contacted: {args.get('message', 'No details')}",
        "create_internal_note": f"📝 Internal note created: {args.get('note', 'No details')}",
    }

    result = action_messages.get(action_name, f"Unknown action: {action_name}")

    await log_activity(
        run_id=run_id,
        kind="action",
        payload={
            "action": action_name,
            "args": args,
            "result": result,
            "timestamp": datetime.utcnow().isoformat(),
        },
        importance="normal",
    )

    return {"success": True, "action": action_name, "result": result}