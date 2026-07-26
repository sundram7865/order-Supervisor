from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Action:
    name: str
    args: dict = field(default_factory=dict)
    reasoning: str = ""


@dataclass
class AgentDecision:
    reasoning: str
    actions: list[Action]
    updated_memory_summary: str
    next_wake_at: Optional[datetime] = None
    wake_guidance: dict = field(default_factory=dict)
    recommend_completion: bool = False


@dataclass
class ClassifierDecision:
    should_wake: bool
    reason: str
    importance: str = "normal"