from typing import Any
from .base_client import digitraffic_client


async def get_port_calls(locode: str | None = None) -> Any:
    params = {"locode": locode} if locode else None
    return await digitraffic_client.get("/api/port-call/v1/port-calls", params=params)


async def get_ports() -> Any:
    return await digitraffic_client.get("/api/port-call/v1/ports")
