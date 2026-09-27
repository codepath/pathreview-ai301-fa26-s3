"""Tests for api/routes/health.py"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from api.routes.health import health_check


@pytest.mark.unit
class TestHealthCheckRedisProbe:
    """Regression tests for issue #62: the Redis probe must build its
    client from settings.redis_url, which actually exists on Settings,
    not settings.redis_host/redis_port, which do not."""

    @pytest.fixture
    def mock_db(self):
        db = Mock()
        db.execute = AsyncMock(return_value=None)
        return db

    @pytest.mark.asyncio
    async def test_redis_healthy_when_reachable(self, mock_db):
        """Regression: previously raised AttributeError on
        settings.redis_host and always reported "unhealthy", even when
        Redis was reachable."""
        with patch("redis.from_url") as mock_from_url:
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_from_url.return_value = mock_client

            result = await health_check(db=mock_db)

        assert result["dependencies"]["redis"] == "healthy"
        mock_client.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_redis_client_built_from_redis_url(self, mock_db):
        """The probe must call redis.from_url with settings.redis_url,
        not construct a client from host/port fields that don't exist."""
        from core.config import settings

        with patch("redis.from_url") as mock_from_url:
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_from_url.return_value = mock_client

            await health_check(db=mock_db)

        mock_from_url.assert_called_once_with(settings.redis_url, decode_responses=True)

    @pytest.mark.asyncio
    async def test_redis_unhealthy_when_unreachable(self, mock_db):
        """The probe still correctly reports "unhealthy" (and the
        overall status 503) when Redis is genuinely unreachable, not
        just always "healthy" after the fix."""
        with patch("redis.from_url") as mock_from_url:
            mock_client = Mock()
            mock_client.ping.side_effect = ConnectionError("connection refused")
            mock_from_url.return_value = mock_client

            with pytest.raises(Exception) as exc_info:
                await health_check(db=mock_db)

        detail = exc_info.value.detail
        assert detail["dependencies"]["redis"] == "unhealthy"
        assert detail["status"] == "unhealthy"
