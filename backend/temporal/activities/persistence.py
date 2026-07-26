from datetime import datetime
from uuid import UUID
from sqlalchemy import select, update
from ...db.database import async_session
from ...db.models import Run, ActivityLog


async def log_activity(run_id: str, kind: str, payload: dict, importance: str = "normal"):
    async with async_session() as session:
        activity = ActivityLog(
            run_id=UUID(run_id),
            kind=kind,
            payload=payload,
            importance=importance,
            created_at=datetime.utcnow(),
        )
        session.add(activity)
        await session.commit()


async def persist_run_state(run_id: str, updates: dict):
    async with async_session() as session:
        updates["updated_at"] = datetime.utcnow()
        stmt = update(Run).where(Run.id == UUID(run_id)).values(**updates)
        await session.execute(stmt)
        await session.commit()


async def get_run_context(run_id: str) -> dict:
    async with async_session() as session:
        result = await session.execute(select(Run).where(Run.id == UUID(run_id)))
        run = result.scalar_one_or_none()
        if not run:
            return {}

        result = await session.execute(
            select(ActivityLog)
            .where(ActivityLog.run_id == UUID(run_id))
            .order_by(ActivityLog.created_at.desc())
            .limit(20)
        )
        recent_activities = result.scalars().all()

        return {
            "run": run,
            "recent_activities": list(reversed(recent_activities)),
            "total_events": run.event_count,
        }