"""Regression tests for issue #62: the /health Redis probe must use settings.redis_url."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import redis
from fastapi import HTTPException

from api.routes.health import health_check
from core.config import settings


def test_redis_probe_uses_settings_url():
    """With Redis up, the probe builds its client from settings.redis_url and reports healthy."""
    client = MagicMock()
    client.ping.return_value = True
    db = AsyncMock()
    with patch("redis.Redis.from_url", return_value=client) as from_url:
        result = asyncio.run(health_check(db=db))
    from_url.assert_called_once()
    assert settings.redis_url in from_url.call_args.args
    assert result["dependencies"]["redis"] == "healthy"


def test_redis_probe_reports_unhealthy_on_connection_error():
    """With Redis down, the probe reports unhealthy and the route raises 503."""
    client = MagicMock()
    client.ping.side_effect = redis.ConnectionError("connection refused")
    db = AsyncMock()
    with (
        patch("redis.Redis.from_url", return_value=client),
        pytest.raises(HTTPException) as excinfo,
    ):
        asyncio.run(health_check(db=db))
    assert excinfo.value.status_code == 503
    assert excinfo.value.detail["dependencies"]["redis"] == "unhealthy"
