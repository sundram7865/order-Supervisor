from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select, update
from temporalio import activity
from db.database import async_session
from db.models import Run, ActivityLog


@activity.defn
async def log_activity(run_id: str, kind: str, payload: dict, importance: str = "normal"):
    async with async_session() as session:
        a = ActivityLog(
            run_id=run_id,
            kind=kind,
            payload=payload,
            importance=importance,
            created_at=datetime.utcnow(),
        )
        session.add(a)
        await session.commit()


@activity.defn
async def persist_run_state(run_id: str, updates: dict):
    async with async_session() as session:
        # Convert next_wake_at string to naive datetime for PostgreSQL
        if "next_wake_at" in updates:
            val = updates["next_wake_at"]
            if isinstance(val, str) and val:
                dt = datetime.fromisoformat(val)
                # Remove timezone info for TIMESTAMP WITHOUT TIME ZONE column
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                updates["next_wake_at"] = dt
            elif val is None or val == "":
                updates["next_wake_at"] = None
        
        # Make sure updated_at is naive datetime
        updates["updated_at"] = datetime.utcnow()
        
        await session.execute(update(Run).where(Run.id == run_id).values(**updates))
        await session.commit()


@activity.defn
async def get_run_context(run_id: str) -> dict:
    async with async_session() as session:
        result = await session.execute(select(Run).where(Run.id == run_id))
        run = result.scalar_one_or_none()
        if not run:
            return {}
        result = await session.execute(
            select(ActivityLog)
            .where(ActivityLog.run_id == run_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(20)
        )
        return {
            "run": run,
            "recent_activities": list(reversed(result.scalars().all())),
            "total_events": run.event_count,
        }