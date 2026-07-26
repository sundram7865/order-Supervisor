import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from ..temporal.models.workflow_io import (
        OrderSupervisorInput,
        OrderEvent,
        WorkflowState,
    )
    from ..temporal.models.agent_decisions import AgentDecision, ClassifierDecision


@workflow.defn
class OrderSupervisorWorkflow:
    def __init__(self):
        self._pending_events: list[OrderEvent] = []
        self._queued_events: list[OrderEvent] = []
        self._terminated = False
        self._termination_reason = ""
        self._paused = False
        self._state: Optional[WorkflowState] = None
        self._agent_guidance: dict = {}
        self._event_count = 0

    @workflow.run
    async def run(self, input: OrderSupervisorInput) -> dict:
        self._state = WorkflowState(
            run_id=input.run_id,
            supervisor_config=input.supervisor_config,
            order_context=input.order_context,
        )

        # Trigger 1: Workflow start
        await self._run_agent_cycle("start")

        while not self._should_complete():
            woke_by_signal = await self._wait_for_next_trigger()

            if self._terminated:
                break

            if woke_by_signal:
                # Trigger 2: Incoming signal
                await self._run_agent_cycle("signal")
            else:
                # Trigger 3: Scheduled wake-up
                await self._run_agent_cycle("scheduled")

        return await self._finalize()

    async def _wait_for_next_trigger(self) -> bool:
        if self._paused:
            await workflow.wait_condition(lambda: not self._paused or self._terminated)
            if self._terminated:
                return False

        timeout = self._time_until_next_wake()
        try:
            await workflow.wait_condition(
                lambda: bool(self._pending_events) or self._terminated,
                timeout=timeout,
            )
            return bool(self._pending_events)
        except asyncio.TimeoutError:
            return False

    def _time_until_next_wake(self) -> Optional[float]:
        if not self._state or not self._state.next_wake_at:
            return 3600.0  # Default: 1 hour

        delta = (self._state.next_wake_at - workflow.now()).total_seconds()
        return max(0.0, delta) if delta > 0 else 0.1

    async def _run_agent_cycle(self, trigger: str):
        # Gather events to process
        events_to_process = self._pending_events + self._queued_events
        self._pending_events.clear()
        self._queued_events.clear()

        # Call agent reasoning activity
        decision = await workflow.execute_activity(
            "run_agent_reasoning",
            args=[
                self._state.run_id,
                trigger,
                {
                    "name": self._state.supervisor_config.name,
                    "base_instruction": self._state.supervisor_config.base_instruction,
                    "available_actions": self._state.supervisor_config.available_actions,
                    "wake_aggressiveness": self._state.supervisor_config.wake_aggressiveness,
                },
                self._state.memory_summary,
                self._state.extra_instructions,
                [{"event_type": e.event_type, "payload": e.payload} for e in events_to_process],
                self._state.order_context,
            ],
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=3,
            ),
        )

        # Execute actions
        for action_data in decision.get("actions", []):
            await workflow.execute_activity(
                "execute_action",
                args=[action_data["name"], self._state.run_id, action_data["args"]],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )

        # Update state
        self._state.memory_summary = decision.get("updated_memory_summary", self._state.memory_summary)
        self._state.next_wake_at = (
            datetime.fromisoformat(decision["next_wake_at"])
            if decision.get("next_wake_at")
            else None
        )
        self._agent_guidance = decision.get("wake_guidance", {})
        self._state.agent_recommends_completion = decision.get("recommend_completion", False)
        self._event_count += len(events_to_process)
        self._state.event_count = self._event_count

        # Persist state
        await workflow.execute_activity(
            "persist_run_state",
            args=[
                self._state.run_id,
                {
                    "memory_summary": self._state.memory_summary,
                    "next_wake_at": self._state.next_wake_at,
                    "status": "sleeping",
                    "event_count": self._event_count,
                },
            ],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=5),
        )

        # Check if we need continue_as_new
        if self._event_count > 500:
            workflow.continue_as_new(
                OrderSupervisorInput(
                    run_id=self._state.run_id,
                    supervisor_config=self._state.supervisor_config,
                    order_context=self._state.order_context,
                )
            )

    def _should_complete(self) -> bool:
        if self._terminated:
            return True
        if self._state.order_reached_terminal_state():
            return True
        if self._state.created_at and (workflow.now() - self._state.created_at) > timedelta(days=30):
            return True
        return False

    async def _finalize(self) -> dict:
        if self._terminated:
            await workflow.execute_activity(
                "persist_run_state",
                args=[self._state.run_id, {"status": "terminated"}],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=5),
            )
            return {"status": "terminated", "reason": self._termination_reason}

        final_summary = await workflow.execute_activity(
            "generate_final_summary",
            args=[self._state.run_id],
            start_to_close_timeout=timedelta(seconds=120),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
        return {"status": "completed", "final_summary": final_summary}

    @workflow.signal
    async def order_event(self, event: OrderEvent):
        # Classify event
        classifier_decision = await workflow.execute_activity(
            "classify_event",
            args=[
                event.event_type,
                self._state.supervisor_config.wake_aggressiveness,
                self._agent_guidance,
            ],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        # Log event
        await workflow.execute_activity(
            "log_activity",
            args=[
                self._state.run_id,
                "event",
                {"event_type": event.event_type, "payload": event.payload, "timestamp": event.timestamp},
                classifier_decision.get("importance", "normal"),
            ],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        if classifier_decision.get("should_wake", False):
            self._pending_events.append(event)
        else:
            self._queued_events.append(event)

    @workflow.signal
    async def add_instruction(self, instruction: str):
        self._state.extra_instructions.append(instruction)
        await workflow.execute_activity(
            "log_activity",
            args=[
                self._state.run_id,
                "instruction",
                {"instruction": instruction, "timestamp": workflow.now().isoformat()},
                "normal",
            ],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

    @workflow.signal
    async def interrupt(self):
        self._paused = True
        await workflow.execute_activity(
            "log_activity",
            args=[self._state.run_id, "sleep_decision", {"action": "interrupted"}, "critical"],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

    @workflow.signal
    async def resume(self):
        self._paused = False
        await workflow.execute_activity(
            "log_activity",
            args=[self._state.run_id, "sleep_decision", {"action": "resumed"}, "normal"],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

    @workflow.signal
    async def terminate_run(self, reason: str):
        self._terminated = True
        self._termination_reason = reason

    @workflow.query
    def get_state(self) -> dict:
        if not self._state:
            return {"status": "initializing"}
        return {
            "status": self._state.status,
            "next_wake_at": self._state.next_wake_at.isoformat() if self._state.next_wake_at else None,
            "memory_summary": self._state.memory_summary,
            "pending_events": len(self._pending_events),
            "queued_events": len(self._queued_events),
            "event_count": self._event_count,
            "paused": self._paused,
        }