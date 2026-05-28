import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.routes import test, dashboard, vessels, ports, sea_state, aton, winter_navigation, risk, chat

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    from app.services.cache import ping as redis_ping
    await redis_ping()
    logger.info("Redis connection verified")
    yield


app = FastAPI(
    title="Finnish Marine Traffic Intelligence API",
    description="Real-time marine traffic data from Digitraffic with LangGraph AI agent",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test routes (Phase 1)
app.include_router(test.router, prefix="/api/test", tags=["test"])

# Production routes (Phase 2)
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(vessels.router, prefix="/api/vessels", tags=["vessels"])
app.include_router(ports.router, prefix="/api/ports", tags=["ports"])
app.include_router(sea_state.router, prefix="/api/sea-state", tags=["sea-state"])
app.include_router(aton.router, prefix="/api/aton", tags=["aton"])
app.include_router(winter_navigation.router, prefix="/api/winter-navigation", tags=["winter-navigation"])
app.include_router(risk.router, prefix="/api/risk", tags=["risk"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])


@app.get("/health", tags=["ops"])
async def health():
    from app.services.cache import ping as redis_ping
    redis_ok = await redis_ping()
    return {"status": "ok", "env": settings.app_env, "redis": redis_ok}


@app.get("/metrics", tags=["ops"])
async def metrics():
    # Prometheus metrics exposed here in Phase 8
    return {"message": "metrics endpoint — Prometheus integration in Phase 8"}
