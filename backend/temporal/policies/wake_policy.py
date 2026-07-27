# backend/temporal/policies/wake_policy.py
class WakeClassifier:
    BASE_RULES = {
        "payment_failed": True,
        "payment_confirmed": False,
        "shipment_delayed": True,
        "shipment_created": False,
        "delivered": True,
        "refund_requested": True,
        "customer_message_received": True,
        "order_created": True,
        "no_update_for_n_hours": False,
    }

    def __init__(self, aggressiveness: str = "normal", agent_guidance: dict = None):
        self.aggressiveness = aggressiveness
        self.agent_guidance = agent_guidance or {}

    def should_wake_now(self, event_type: str) -> tuple:
        # Agent guidance takes highest priority
        if event_type in self.agent_guidance:
            return self.agent_guidance[event_type], "agent_guidance"

        # Unknown events - escalate (safety first)
        if event_type not in self.BASE_RULES:
            return True, "unknown_event_escalation"

        base_decision = self.BASE_RULES[event_type]

        # Adjust based on aggressiveness
        if self.aggressiveness == "high" and not base_decision:
            return True, "high_aggressiveness_override"
        elif self.aggressiveness == "low" and base_decision:
            return False, "low_aggressiveness_override"

        return base_decision, "base_rule" if base_decision else "low_priority"