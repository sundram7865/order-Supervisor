from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from api.dependencies import get_db, get_temporal_client
from db.models import Run
from temporal.models.workflow_io import OrderEvent

router = APIRouter(tags=["events"])


class InjectEventRequest(BaseModel):
    event_type: str
    payload: dict = {}


class AddInstructionRequest(BaseModel):
    instruction: str


class TerminateRequest(BaseModel):
    reason: str = "Manual termination"


@router.post("/runs/{run_id}/events")
async def inject_event(run_id: UUID, req: InjectEventRequest):
    try:
        tc = await get_temporal_client()
        handle = tc.get_workflow_handle(str(run_id))
        
        event = OrderEvent(
            event_type=req.event_type,
            payload=req.payload,
            timestamp=datetime.utcnow().isoformat(),
        )
        
        await handle.signal("order_event", event)
        return {"success": True, "event_type": req.event_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/runs/{run_id}/instructions")
async def add_instruction(run_id: UUID, req: AddInstructionRequest, db: AsyncSession = Depends(get_db)):
    r = (await db.execute(select(Run).where(Run.id == run_id))).scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    
    r.extra_instructions = (r.extra_instructions or []) + [req.instruction]
    await db.commit()
    
    tc = await get_temporal_client()
    handle = tc.get_workflow_handle(str(run_id))
    await handle.signal("add_instruction", req.instruction)
    
    return {"success": True}


@router.post("/runs/{run_id}/interrupt")
async def interrupt(run_id: UUID):
    tc = await get_temporal_client()
    handle = tc.get_workflow_handle(str(run_id))
    await handle.signal("interrupt")
    return {"success": True}


@router.post("/runs/{run_id}/resume")
async def resume(run_id: UUID):
    tc = await get_temporal_client()
    handle = tc.get_workflow_handle(str(run_id))
    await handle.signal("resume")
    return {"success": True}


@router.post("/runs/{run_id}/terminate")
async def terminate(run_id: UUID, req: TerminateRequest):
    tc = await get_temporal_client()
    handle = tc.get_workflow_handle(str(run_id))
    await handle.signal("terminate_run", req.reason)
    return {"success": True}