from typing import Any
from .base_client import digitraffic_client

# Confirmed live: v2 (v1 returns 404)


async def get_dirways() -> Any:
    return await digitraffic_client.get("/api/winter-navigation/v2/dirways")


async def get_vessels() -> Any:
    # Returns {"lastUpdated": ..., "vessels": [...]}
    return await digitraffic_client.get("/api/winter-navigation/v2/vessels")
