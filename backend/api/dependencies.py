# backend/api/dependencies.py
from functools import lru_cache
from temporalio.client import Client
from ..db.database import get_db
import os


@lru_cache()
async def get_temporal_client() -> Client:
    return await Client.connect(
        os.getenv("TEMPORAL_HOST", "localhost:7233"),
        namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
    )