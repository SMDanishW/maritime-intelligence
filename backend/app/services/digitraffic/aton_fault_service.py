from typing import Any
from .base_client import digitraffic_client


async def get_aton_faults(language: str = "en") -> Any:
    return await digitraffic_client.get("/api/aton/v1/faults", params={"language": language})
