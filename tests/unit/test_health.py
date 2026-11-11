"""Tests for the Redis probe in api/routes/health.py"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException
from redis.exceptions import ConnectionError as RedisConnectionError

from api.routes.health import health_check
from core.config import settings


@pytest.mark.unit
class TestHealthRedisProbe:
    """Test suite for the Redis entry of the /health route."""

    @pytest.fixture
    def db(self):
        """Create a database session whose queries succeed."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_redis_healthy_when_ping_succeeds(self, db):
        """The probe builds its client from redis_url and reports healthy."""
        client = Mock()
        with patch("redis.Redis.from_url", return_value=client) as from_url:
            result = await health_check(db=db)

        from_url.assert_called_once_with(settings.redis_url, decode_responses=True)
        client.ping.assert_called_once()
        assert result["dependencies"]["redis"] == "healthy"

    @pytest.mark.asyncio
    async def test_redis_unhealthy_when_ping_fails(self, db):
        """A connection error from Redis is reported as unhealthy with a 503."""
        client = Mock()
        client.ping.side_effect = RedisConnectionError("connection refused")
        with (
            patch("redis.Redis.from_url", return_value=client),
            pytest.raises(HTTPException) as exc_info,
        ):
            await health_check(db=db)

        assert exc_info.value.status_code == 503
        assert exc_info.value.detail["dependencies"]["redis"] == "unhealthy"
