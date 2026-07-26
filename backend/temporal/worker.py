import asyncio
import os
from temporalio.client import Client
from temporalio.worker import Worker
from dotenv import load_dotenv

from .workflow import OrderSupervisorWorkflow
from .activities.agent import run_agent_reasoning
from .activities.actions import execute_action
from .activities.classifier import classify_event
from .activities.persistence import log_activity, persist_run_state, get_run_context
from .activities.summarization import generate_final_summary

load_dotenv()


async def main():
    client = await Client.connect(
        os.getenv("TEMPORAL_HOST", "localhost:7233"),
        namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
    )

    worker = Worker(
        client,
        task_queue=os.getenv("TEMPORAL_TASK_QUEUE", "order-supervisor"),
        workflows=[OrderSupervisorWorkflow],
        activities=[
            run_agent_reasoning,
            execute_action,
            classify_event,
            log_activity,
            persist_run_state,
            get_run_context,
            generate_final_summary,
        ],
    )

    print(f"Worker started on task queue: {os.getenv('TEMPORAL_TASK_QUEUE', 'order-supervisor')}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())