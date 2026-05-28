from typing import Any
from .base_client import digitraffic_client


async def get_vessel_details() -> Any:
    return await digitraffic_client.get("/api/port-call/v1/vessel-details")


async def get_vessel_detail(vessel_id: int) -> Any:
    return await digitraffic_client.get(f"/api/port-call/v1/vessel-details/{vessel_id}")
