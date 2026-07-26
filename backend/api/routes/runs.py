from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..dependencies import get_db, get_temporal_client
from ...db.models import Run, Supervisor, ActivityLog
from ...temporal.models.workflow_io import OrderSupervisorInput, SupervisorConfig
from ...temporal.workflow import OrderSupervisorWorkflow

router = APIRouter(prefix="/runs", tags=["runs"])


class StartRunRequest(BaseModel):
    supervisor_id: str
    order_id: str
    order_context: dict = {}


class RunResponse(BaseModel):
    id: str
    supervisor_id: str
    order_id: str
    workflow_id: str
    status: str
    memory_summary: str
    next_wake_at: Optional[str]
    order_context: dict
    extra_instructions: list[str]
    final_summary: Optional[dict]
    event_count: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=RunResponse)
async def start_run(req: StartRunRequest, db: AsyncSession = Depends(get_db)):
    # Get supervisor config
    result = await db.execute(select(Supervisor).where(Supervisor.id == UUID(req.supervisor_id)))
    supervisor = result.scalar_one_or_none()
    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor not found")

    # Create run record
    run = Run(
        supervisor_id=UUID(req.supervisor_id),
        order_id=req.order_id,
        workflow_id=str(UUID(req.supervisor_id)),  # Will be updated after workflow start
        order_context=req.order_context,
        status="active",
    )
    db.add(run)
    await db.commit()

    # Update workflow_id to match run_id
    run.workflow_id = str(run.id)
    await db.commit()
    await db.refresh(run)

    # Start Temporal workflow
    temporal_client = await get_temporal_client()
    await temporal_client.start_workflow(
        OrderSupervisorWorkflow.run,
        OrderSupervisorInput(
            run_id=str(run.id),
            supervisor_config=SupervisorConfig(
                name=supervisor.name,
                base_instruction=supervisor.base_instruction,
                available_actions=supervisor.available_actions,
                wake_aggressiveness=supervisor.wake_aggressiveness,
                model_config=supervisor.model_config,
            ),
            order_context=req.order_context,
        ),
        id=str(run.id),
        task_queue="order-supervisor",
    )

    return run


@router.get("", response_model=list[RunResponse])
async def list_runs(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(Run).order_by(Run.created_at.desc())
    if status:
        query = query.where(Run.status == status)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{run_id}/timeline")
async def get_run_timeline(
    run_id: UUID,
    kind: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = select(ActivityLog).where(ActivityLog.run_id == run_id)
    if kind:
        query = query.where(ActivityLog.kind == kind)
    query = query.order_by(ActivityLog.created_at.desc()).limit(limit)
    result = await db.execute(query)
    activities = result.scalars().all()
    return {"activities": list(reversed(activities)), "count": len(activities)}