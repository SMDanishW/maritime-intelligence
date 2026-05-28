"""Quick smoke test of FastAPI routes via ASGI transport (no server needed)."""
import asyncio
import httpx


async def smoke():
    from app.main import app

    routes = [
        "/health",
        "/api/test/ais",
        "/api/test/vessels",
        "/api/test/port-calls",
        "/api/test/aton-faults",
        "/api/test/winter-navigation",
        "/api/test/sea-state",
    ]

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as c:
        for path in routes:
            r = await c.get(path)
            data = r.json()
            summary = {k: v for k, v in data.items() if k not in ("sample", "data", "dirways_sample", "vessels_sample")}
            print(f"  {r.status_code}  {path:<35} {summary}")


if __name__ == "__main__":
    asyncio.run(smoke())
