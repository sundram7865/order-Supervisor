ANALYSIS_PROMPT = """You are an order supervisor overseeing order {order_id}.

== BASE INSTRUCTIONS ==
{base_instruction}

== EXTRA INSTRUCTIONS ==
{extra_instructions}

== CURRENT MEMORY ==
{memory_summary}

== RECENT EVENTS ==
{recent_events}

== TRIGGER ==
{trigger}

== ORDER CONTEXT ==
{order_context}

Analyze the situation. Return valid JSON:
{{
    "reasoning": "Your detailed analysis of the current situation",
    "order_state": "Current state of the order (processing/shipped/delayed/etc)",
    "needs_action": true/false,
    "priority": "critical/normal/low",
    "concerns": ["Any specific concerns to address"],
    "is_terminal": true/false
}}"""

TOOL_SELECTION_PROMPT = """Based on your analysis, select appropriate actions.

== ANALYSIS ==
{analysis}

== AVAILABLE TOOLS ==
{available_tools}

== ORDER CONTEXT ==
{order_context}

Select tools to address the situation. Return JSON:
{{
    "reasoning": "Why these tools are needed",
    "actions": [
        {{
            "name": "tool_name",
            "args": {{"key": "value"}},
            "reasoning": "Why this action"
        }}
    ]
}}

Rules:
- message_fulfillment_team: For warehouse/fulfillment issues
- message_payments_team: For payment/billing issues
- message_logistics_team: For shipping/delivery issues
- message_customer: To communicate with customer
- create_internal_note: To document important info for human review"""

MEMORY_UPDATE_PROMPT = """Update the memory summary for this order.

== CURRENT SUMMARY ==
{current_summary}

== NEW EVENTS ==
{new_events}

== REASONING ==
{reasoning}

== ACTIONS TAKEN ==
{actions_taken}

Return JSON:
{{
    "updated_summary": "A concise summary (max 500 chars) of all important info",
    "key_facts": ["Important fact 1", "Important fact 2"],
    "outstanding_issues": ["Any unresolved issues"]
}}"""

WAKE_STRATEGY_PROMPT = """Decide when the supervisor should wake up next.

== CURRENT STATE ==
{current_state}

== MEMORY ==
{memory}

== DEFAULT AGGRESSIVENESS ==
{aggressiveness}

Return JSON:
{{
    "next_wake_at": "ISO timestamp or null if no scheduled wake needed",
    "reasoning": "Why this wake time was chosen",
    "wake_guidance": {{
        "payment_failed": true,
        "shipment_delayed": true
    }}
}}"""