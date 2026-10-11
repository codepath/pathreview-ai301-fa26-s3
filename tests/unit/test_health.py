"""Tests for the Redis probe in api/routes/health.py"""

import asyncio
from unittest.mock import Mock, patch

import pytest
import redis
from fastapi import HTTPException

from api.routes.health import health_check
from core.config import settings


class FakeDb:
    """Stand-in database session whose probe query always succeeds."""

    async def execute(self, *args, **kwargs):
        return None


def run_health_check():
    """Call the endpoint function and return its dependencies dict."""
    try:
        result = asyncio.run(health_check(db=FakeDb()))
    except HTTPException as exc:
        result = exc.detail
    return result["dependencies"]


@pytest.mark.unit
class TestRedisHealthProbe:
    """Test suite for the Redis probe in the /health endpoint."""

    def test_reachable_redis_reports_healthy(self):
        """A Redis that answers ping is reported healthy, built from redis_url."""
        client = Mock()
        client.ping.return_value = True

        with patch("redis.Redis.from_url", return_value=client) as from_url:
            deps = run_health_check()

        assert deps["redis"] == "healthy"
        assert from_url.call_args.args[0] == settings.redis_url

    def test_unreachable_redis_reports_unhealthy(self):
        """A Redis that refuses the connection is still reported unhealthy."""
        client = Mock()
        client.ping.side_effect = redis.ConnectionError("connection refused")

        with patch("redis.Redis.from_url", return_value=client):
            deps = run_health_check()

        assert deps["redis"] == "unhealthy"
