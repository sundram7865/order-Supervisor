"""Simulate a realistic order lifecycle"""
import asyncio
import httpx
import sys


async def simulate(api_base: str, run_id: str):
    events = [
        ("order_created", {"order_id": "SIM-001"}),
        ("payment_confirmed", {"amount": 150}),
        ("shipment_created", {"tracking": "TRK-123"}),
        ("shipment_delayed", {"reason": "weather", "new_eta": "2 days"}),
        ("customer_message_received", {"message": "Where is my order?"}),
        ("delivered", {"timestamp": "now"}),
    ]

    async with httpx.AsyncClient() as client:
        for event_type, payload in events:
            print(f"Sending: {event_type}")
            resp = await client.post(
                f"{api_base}/api/runs/{run_id}/events",
                json={"event_type": event_type, "payload": payload},
            )
            print(f"  Response: {resp.json()}")
            await asyncio.sleep(2)  # Wait between events


if __name__ == "__main__":
    api_base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    run_id = sys.argv[2] if len(sys.argv) > 2 else input("Enter run ID: ")
    asyncio.run(simulate(api_base, run_id))