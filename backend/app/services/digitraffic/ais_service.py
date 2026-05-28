from typing import Any
from .base_client import digitraffic_client


async def get_vessel_locations() -> Any:
    return await digitraffic_client.get("/api/ais/v1/locations")


async def get_vessel_location(mmsi: int) -> Any:
    return await digitraffic_client.get(f"/api/ais/v1/locations/{mmsi}")
