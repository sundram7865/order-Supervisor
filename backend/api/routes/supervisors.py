# backend/api/routes/supervisors.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel
from api.dependencies import get_db
from db.models import Supervisor

router = APIRouter(prefix="/supervisors", tags=["supervisors"])


class CreateSupervisorRequest(BaseModel):
    name: str
    base_instruction: str
    available_actions: list[str] = []
    wake_aggressiveness: str = "normal"
    llm_config: dict = {}


@router.post("")
async def create_supervisor(req: CreateSupervisorRequest, db: AsyncSession = Depends(get_db)):
    s = Supervisor(
        name=req.name,
        base_instruction=req.base_instruction,
        available_actions=req.available_actions,
        wake_aggressiveness=req.wake_aggressiveness,
        model_config=req.llm_config,
    )
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return {
        "id": str(s.id),
        "name": s.name,
        "base_instruction": s.base_instruction,
        "available_actions": s.available_actions,
        "wake_aggressiveness": s.wake_aggressiveness,
        "model_config": s.model_config,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }


@router.get("")
async def list_supervisors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supervisor).order_by(Supervisor.created_at.desc()))
    supervisors = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "name": s.name,
            "base_instruction": s.base_instruction,
            "available_actions": s.available_actions,
            "wake_aggressiveness": s.wake_aggressiveness,
            "model_config": s.model_config,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in supervisors
    ]


@router.get("/{supervisor_id}")
async def get_supervisor(supervisor_id: str, db: AsyncSession = Depends(get_db)):
    s = (await db.execute(select(Supervisor).where(Supervisor.id == supervisor_id))).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "id": str(s.id),
        "name": s.name,
        "base_instruction": s.base_instruction,
        "available_actions": s.available_actions,
        "wake_aggressiveness": s.wake_aggressiveness,
        "model_config": s.model_config,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }