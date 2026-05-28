import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings

logger = logging.getLogger(__name__)

_CLIENT_HEADERS = {
    "Accept": "application/json",
    "Digitraffic-User": "marine-intelligence/0.1",
}


def _make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=settings.digitraffic_base_url,
        timeout=httpx.Timeout(settings.digitraffic_timeout_seconds),
        headers=_CLIENT_HEADERS,
        follow_redirects=True,
    )


class DigitraficClient:
    """Async HTTP client for Digitraffic Marine APIs.

    Uses a fresh AsyncClient per request so there is no event-loop binding —
    safe across pytest's per-test loops and inside a FastAPI lifespan.
    In Phase 2, Redis caching sits in front of these calls so the lack of
    persistent connection pooling has negligible latency impact.
    """

    @retry(
        stop=stop_after_attempt(settings.digitraffic_retry_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        reraise=True,
    )
    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        logger.debug("GET %s params=%s", path, params)
        async with _make_client() as client:
            response = await client.get(path, params=params)
            response.raise_for_status()
            return response.json()


digitraffic_client = DigitraficClient()
