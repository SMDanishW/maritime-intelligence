import pytest
import app.services.cache as _cache_module


@pytest.fixture(autouse=True)
async def reset_redis_pool():
    """Reset Redis connection pool before each test.

    The pool is a module-level singleton. pytest-asyncio creates a fresh event
    loop per test function, so a pool from a previous test's loop fails when
    its connections try to clean up against the now-closed loop. Resetting the
    pool pointer forces a fresh pool (and fresh connections) bound to the
    current loop on first use.
    """
    _cache_module._pool = None
    yield
    _cache_module._pool = None
