"""Rate limiting end to end: the real app, the real Redis, and the configured limit."""

import pytest
import redis
from fastapi.testclient import TestClient

from api.main import app
from core.config import settings

INTEGRATION_CLIENT = ("203.0.113.9", 50001)
KEY = f"rate_limit:{INTEGRATION_CLIENT[0]}"


@pytest.mark.integration
def test_limit_is_enforced_with_real_redis() -> None:
    """The first `limit` requests pass with decreasing remaining counts; the next one gets 429."""
    limit = settings.rate_limit_per_minute
    store = redis.Redis.from_url(settings.redis_url)
    store.delete(KEY)
    client = TestClient(app, client=INTEGRATION_CLIENT)

    try:
        for i in range(1, limit + 1):
            response = client.get("/")
            assert response.status_code == 200, f"request {i} was not allowed"
            assert response.headers["X-RateLimit-Limit"] == str(limit)
            assert response.headers["X-RateLimit-Remaining"] == str(limit - i)

        denied = client.get("/")
        assert denied.status_code == 429
        assert denied.headers["Retry-After"] == "60"
        assert denied.headers["X-RateLimit-Remaining"] == "0"
        assert "X-Request-ID" in denied.headers
    finally:
        store.delete(KEY)
