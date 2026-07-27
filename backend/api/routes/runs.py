from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from api.dependencies import get_db, get_temporal_client
from db.models import Run, Supervisor, ActivityLog
from temporal.models.workflow_io import OrderSupervisorInput, SupervisorConfig
from temporal.workflow import OrderSupervisorWorkflow

router = APIRouter(prefix="/runs", tags=["runs"])


class StartRunRequest(BaseModel):
    supervisor_id: str
    order_id: str
    order_context: dict = {}


def run_to_dict(run) -> dict:
    return {
        "id": str(run.id),
        "supervisor_id": str(run.supervisor_id),
        "order_id": run.order_id,
        "workflow_id": run.workflow_id,
        "status": run.status,
        "memory_summary": run.memory_summary,
        "next_wake_at": run.next_wake_at.isoformat() if run.next_wake_at else None,
        "order_context": run.order_context,
        "extra_instructions": run.extra_instructions,
        "final_summary": run.final_summary,
        "event_count": run.event_count,
        "created_at": run.created_at.isoformat(),
        "updated_at": run.updated_at.isoformat(),
    }


@router.post("")
async def start_run(req: StartRunRequest, db: AsyncSession = Depends(get_db)):
    sup = (await db.execute(select(Supervisor).where(Supervisor.id == UUID(req.supervisor_id)))).scalar_one_or_none()
    if not sup:
        raise HTTPException(status_code=404, detail="Supervisor not found")

    run = Run(
        supervisor_id=UUID(req.supervisor_id),
        order_id=req.order_id,
        workflow_id="pending",
        order_context=req.order_context,
        status="active",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)

    run.workflow_id = str(run.id)
    await db.commit()
    await db.refresh(run)

    tc = await get_temporal_client()
    await tc.start_workflow(
        OrderSupervisorWorkflow.run,
        OrderSupervisorInput(
            run_id=str(run.id),
            supervisor_config=SupervisorConfig(
                name=sup.name,
                base_instruction=sup.base_instruction,
                available_actions=sup.available_actions,
                wake_aggressiveness=sup.wake_aggressiveness,
                model_config=sup.model_config,
            ),
            order_context=req.order_context,
        ),
        id=str(run.id),
        task_queue="order-supervisor",
    )
    return run_to_dict(run)


@router.get("")
async def list_runs(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    q = select(Run).order_by(Run.created_at.desc())
    if status:
        q = q.where(Run.status == status)
    runs = (await db.execute(q)).scalars().all()
    return [run_to_dict(r) for r in runs]


@router.get("/{run_id}")
async def get_run(run_id: UUID, db: AsyncSession = Depends(get_db)):
    r = (await db.execute(select(Run).where(Run.id == run_id))).scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    return run_to_dict(r)


@router.get("/{run_id}/timeline")
async def get_timeline(run_id: UUID, kind: Optional[str] = None, limit: int = 50, db: AsyncSession = Depends(get_db)):
    q = select(ActivityLog).where(ActivityLog.run_id == run_id).order_by(ActivityLog.created_at.desc()).limit(limit)
    if kind:
        q = q.where(ActivityLog.kind == kind)
    acts = (await db.execute(q)).scalars().all()
    return {
        "activities": [
            {
                "id": str(a.id),
                "run_id": str(a.run_id),
                "kind": a.kind,
                "payload": a.payload,
                "importance": a.importance,
                "created_at": a.created_at.isoformat(),
            }
            for a in reversed(acts)
        ],
        "count": len(acts),
    }