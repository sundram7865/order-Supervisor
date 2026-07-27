# scripts/seed_supervisors.py
"""Create default supervisor templates"""
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from db.database import async_session, init_db
from db.models import Supervisor
from sqlalchemy import select


async def seed():
    await init_db()

    templates = [
        {
            "name": "Standard Order Monitor",
            "base_instruction": "Monitor orders from creation to delivery. Alert on payment failures and shipping delays. Keep customers informed.",
            "available_actions": [
                "message_customer",
                "create_internal_note",
                "message_payments_team",
                "message_logistics_team",
            ],
            "wake_aggressiveness": "normal",
        },
        {
            "name": "Aggressive Escalator",
            "base_instruction": "Proactively monitor orders. Escalate immediately on any issues. Prioritize speed over cost.",
            "available_actions": [
                "message_fulfillment_team",
                "message_payments_team",
                "message_logistics_team",
                "message_customer",
                "create_internal_note",
            ],
            "wake_aggressiveness": "high",
        },
    ]

    async with async_session() as session:
        # Check existing
        result = await session.execute(select(Supervisor))
        existing = result.scalars().all()
        if existing:
            print(f"Already seeded {len(existing)} supervisors:")
            for s in existing:
                print(f"  ID: {s.id} - {s.name}")
            return

        for template in templates:
            supervisor = Supervisor(**template)
            session.add(supervisor)
        await session.commit()
        print(f"Seeded {len(templates)} supervisor templates")


if __name__ == "__main__":
    asyncio.run(seed())