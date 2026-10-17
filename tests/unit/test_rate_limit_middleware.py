"""Tests for RateLimitMiddleware, using a stub limiter (no Redis)."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.middleware.rate_limit import RateLimitMiddleware

CLIENT_IP = "203.0.113.7"


class StubLimiter:
    """Records calls and returns a fixed decision."""

    def __init__(self, allowed: bool = True, remaining: int = 59) -> None:
        self.allowed = allowed
        self.remaining = remaining
        self.calls: list[tuple[str, int, int]] = []

    def check_rate_limit(
        self, identifier: str, limit: int, window_seconds: int = 60
    ) -> tuple[bool, int]:
        self.calls.append((identifier, limit, window_seconds))
        return self.allowed, self.remaining


def make_client(limiter: StubLimiter, limit: int = 60) -> TestClient:
    """Build a small app with the middleware and return a client for it."""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, limiter=limiter, limit=limit)

    @app.get("/")
    async def root() -> dict[str, bool]:
        return {"ok": True}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return TestClient(app, client=(CLIENT_IP, 50000))


@pytest.mark.unit
class TestRateLimitMiddleware:
    """Headers, 429 handling, exemptions, and identifier for RateLimitMiddleware."""

    def test_allowed_request_has_rate_limit_headers(self) -> None:
        limiter = StubLimiter(allowed=True, remaining=59)
        client = make_client(limiter)

        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["X-RateLimit-Limit"] == "60"
        assert response.headers["X-RateLimit-Remaining"] == "59"

    def test_denied_request_returns_429_with_retry_after(self) -> None:
        limiter = StubLimiter(allowed=False, remaining=0)
        client = make_client(limiter)

        response = client.get("/")

        assert response.status_code == 429
        assert response.json() == {"detail": "Rate limit exceeded"}
        assert response.headers["Retry-After"] == "60"
        assert response.headers["X-RateLimit-Limit"] == "60"
        assert response.headers["X-RateLimit-Remaining"] == "0"

    def test_health_is_exempt_from_limiting(self) -> None:
        limiter = StubLimiter(allowed=False, remaining=0)
        client = make_client(limiter)

        response = client.get("/health")

        assert response.status_code == 200
        assert limiter.calls == []
        assert "X-RateLimit-Limit" not in response.headers

    def test_options_requests_are_not_limited(self) -> None:
        limiter = StubLimiter(allowed=False, remaining=0)
        client = make_client(limiter)

        response = client.options("/")

        assert limiter.calls == []
        assert "X-RateLimit-Limit" not in response.headers

    def test_identifier_is_client_host(self) -> None:
        limiter = StubLimiter()
        client = make_client(limiter, limit=60)

        client.get("/")

        assert limiter.calls == [(CLIENT_IP, 60, 60)]

    @pytest.mark.parametrize("remaining", [59, 30, 0])
    def test_remaining_value_comes_from_limiter(self, remaining: int) -> None:
        limiter = StubLimiter(allowed=True, remaining=remaining)
        client = make_client(limiter)

        response = client.get("/")

        assert response.headers["X-RateLimit-Remaining"] == str(remaining)

    def test_fail_open_reports_limit_as_remaining(self) -> None:
        """Documents the outage behavior: the limiter fails open and returns (True, limit)."""
        limiter = StubLimiter(allowed=True, remaining=60)
        client = make_client(limiter, limit=60)

        response = client.get("/")

        assert response.status_code == 200
        assert response.headers["X-RateLimit-Remaining"] == "60"
