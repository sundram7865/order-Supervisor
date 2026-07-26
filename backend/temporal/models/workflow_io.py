from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID
from temporalio import workflow


@dataclass
class SupervisorConfig:
    name: str
    base_instruction: str
    available_actions: list[str]
    wake_aggressiveness: str = "normal"
    model_config: dict = field(default_factory=dict)


@dataclass
class OrderSupervisorInput:
    run_id: str
    supervisor_config: SupervisorConfig
    order_context: dict


@dataclass
class OrderEvent:
    event_type: str
    payload: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: workflow.now().isoformat())


@dataclass
class WorkflowState:
    run_id: str
    supervisor_config: SupervisorConfig
    order_context: dict
    status: str = "active"
    memory_summary: str = ""
    next_wake_at: Optional[datetime] = None
    extra_instructions: list[str] = field(default_factory=list)
    event_count: int = 0
    created_at: datetime = field(default_factory=lambda: workflow.now())
    agent_recommends_completion: bool = False
    _terminal_states: set = field(
        default_factory=lambda: {"delivered", "refund_resolved", "cancelled"}
    )

    def order_reached_terminal_state(self) -> bool:
        if self.order_context.get("status"):
            return self.order_context["status"] in self._terminal_states
        return False