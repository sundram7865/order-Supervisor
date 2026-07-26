from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from ..dependencies import get_db
from ...db.models import Supervisor

router = APIRouter(prefix="/supervisors", tags=["supervisors"])


class CreateSupervisorRequest(BaseModel):
    name: str
    base_instruction: str
    available_actions: list[str] = []
    wake_aggressiveness: str = "normal"
    model_config: dict = {}


class SupervisorResponse(BaseModel):
    id: str
    name: str
    base_instruction: str
    available_actions: list[str]
    wake_aggressiveness: str
    model_config: dict
    created_at: str

    class Config:
        from_attributes = True


@router.post("", response_model=SupervisorResponse)
async def create_supervisor(req: CreateSupervisorRequest, db: AsyncSession = Depends(get_db)):
    supervisor = Supervisor(
        name=req.name,
        base_instruction=req.base_instruction,
        available_actions=req.available_actions,
        wake_aggressiveness=req.wake_aggressiveness,
        model_config=req.model_config,
    )
    db.add(supervisor)
    await db.commit()
    await db.refresh(supervisor)
    return supervisor


@router.get("", response_model=list[SupervisorResponse])
async def list_supervisors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supervisor).order_by(Supervisor.created_at.desc()))
    return result.scalars().all()


@router.get("/{supervisor_id}", response_model=SupervisorResponse)
async def get_supervisor(supervisor_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supervisor).where(Supervisor.id == supervisor_id))
    supervisor = result.scalar_one_or_none()
    if not supervisor:
        raise HTTPException(status_code=404, detail="Supervisor not found")
    return supervisor