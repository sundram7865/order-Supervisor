from temporalio import activity
from ..models.agent_decisions import ClassifierDecision
from ..policies.wake_policy import WakeClassifier


@activity.defn
async def classify_event(
    event_type: str, aggressiveness: str, agent_guidance: dict = None
) -> ClassifierDecision:
    classifier = WakeClassifier(aggressiveness, agent_guidance)
    should_wake, reason = classifier.should_wake_now(event_type)

    importance = "normal"
    if reason in ("agent_guidance", "unknown_event_escalation"):
        importance = "critical"

    return ClassifierDecision(should_wake=should_wake, reason=reason, importance=importance)