"""Tests for api/middleware/rate_limit.py"""

from collections import defaultdict

import pytest
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from api.middleware.auth import oauth2_scheme
from api.middleware.rate_limit import RateLimitMiddleware
from core.security import create_access_token


class FakeLimiter:
    """In-memory stand-in for RateLimiter with the same call signature."""

    def __init__(self, fail_with: Exception | None = None) -> None:
        self.counts: defaultdict[str, int] = defaultdict(int)
        self.calls: list[tuple[str, int, int]] = []
        self.fail_with = fail_with

    def check_rate_limit(
        self, identifier: str, limit: int, window_seconds: int = 60
    ) -> tuple[bool, int]:
        self.calls.append((identifier, limit, window_seconds))
        if self.fail_with is not None:
            raise self.fail_with
        if self.counts[identifier] >= limit:
            return False, 0
        self.counts[identifier] += 1
        return True, limit - self.counts[identifier]


def build_app(limiter: FakeLimiter, **kwargs) -> FastAPI:
    """Build a minimal app wrapped in the middleware under test."""
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, limiter=limiter, **kwargs)

    @app.get("/ping")
    async def ping() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    @app.get("/secure")
    async def secure(token: str = Depends(oauth2_scheme)) -> dict[str, str]:
        return {"status": "ok"}

    return app


def client_for(limiter: FakeLimiter, ip: str = "203.0.113.10", **kwargs) -> TestClient:
    return TestClient(build_app(limiter, **kwargs), client=(ip, 51000))


def bearer(user_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {create_access_token({'sub': user_id})}"}


@pytest.mark.unit
class TestRateLimitMiddlewareAnonymous:
    """Requests with no token are limited by client IP alone."""

    def test_requests_under_limit_allowed(self):
        limiter = FakeLimiter()
        client = client_for(limiter, ip_limit=3)

        for _ in range(3):
            assert client.get("/ping").status_code == 200

    def test_request_over_ip_limit_returns_429(self):
        limiter = FakeLimiter()
        client = client_for(limiter, ip_limit=2)

        client.get("/ping")
        client.get("/ping")
        response = client.get("/ping")

        assert response.status_code == 429
        assert response.json()["scope"] == "ip"

    def test_429_carries_retry_after_and_limit_headers(self):
        limiter = FakeLimiter()
        client = client_for(limiter, ip_limit=1, window_seconds=30)

        client.get("/ping")
        response = client.get("/ping")

        assert response.status_code == 429
        assert response.headers["Retry-After"] == "30"
        assert response.headers["X-RateLimit-Limit"] == "1"
        assert response.headers["X-RateLimit-Remaining"] == "0"

    def test_allowed_response_reports_remaining(self):
        limiter = FakeLimiter()
        client = client_for(limiter, ip_limit=5)

        first = client.get("/ping")
        second = client.get("/ping")

        assert first.headers["X-RateLimit-Remaining"] == "4"
        assert second.headers["X-RateLimit-Remaining"] == "3"

    def test_separate_ips_have_separate_budgets(self):
        limiter = FakeLimiter()
        app_kwargs = {"ip_limit": 1}

        first_ip = client_for(limiter, ip="203.0.113.10", **app_kwargs)
        # A second client against a *shared* limiter, from a different address.
        second_ip = TestClient(build_app(limiter, **app_kwargs), client=("203.0.113.99", 51000))

        assert first_ip.get("/ping").status_code == 200
        assert first_ip.get("/ping").status_code == 429
        assert second_ip.get("/ping").status_code == 200

    def test_identifier_is_namespaced_by_scope(self):
        limiter = FakeLimiter()
        client = client_for(limiter, ip="203.0.113.10")

        client.get("/ping")

        assert limiter.calls[0][0] == "ip:203.0.113.10"


@pytest.mark.unit
class TestRateLimitMiddlewareAuthenticated:
    """A bearer token adds a per-user bucket on top of the per-IP bucket."""

    def test_token_adds_user_bucket(self):
        limiter = FakeLimiter()
        client = client_for(limiter)

        client.get("/secure", headers=bearer("user-abc"))

        identifiers = [call[0] for call in limiter.calls]
        assert identifiers == ["ip:203.0.113.10", "user:user-abc"]

    def test_user_limit_applies_within_ip_budget(self):
        limiter = FakeLimiter()
        client = client_for(limiter, ip_limit=100, user_limit=2)
        headers = bearer("user-abc")

        client.get("/secure", headers=headers)
        client.get("/secure", headers=headers)
        response = client.get("/secure", headers=headers)

        assert response.status_code == 429
        assert response.json()["scope"] == "user"

    def test_two_users_behind_one_ip_share_the_ip_budget(self):
        limiter = FakeLimiter()
        client = client_for(limiter, ip_limit=2, user_limit=100)

        assert client.get("/secure", headers=bearer("user-a")).status_code == 200
        assert client.get("/secure", headers=bearer("user-b")).status_code == 200
        # Third request is within both user budgets but over the shared IP budget.
        response = client.get("/secure", headers=bearer("user-c"))

        assert response.status_code == 429
        assert response.json()["scope"] == "ip"

    def test_two_users_have_independent_user_budgets(self):
        limiter = FakeLimiter()
        client = client_for(limiter, ip_limit=100, user_limit=1)

        assert client.get("/secure", headers=bearer("user-a")).status_code == 200
        assert client.get("/secure", headers=bearer("user-a")).status_code == 429
        assert client.get("/secure", headers=bearer("user-b")).status_code == 200

    @pytest.mark.parametrize(
        "header",
        [
            "Bearer not-a-real-token",
            "Bearer ",
            "Basic dXNlcjpwYXNz",
            "token-without-scheme",
        ],
    )
    def test_undecodable_token_falls_back_to_ip_only(self, header):
        limiter = FakeLimiter()
        client = client_for(limiter)

        client.get("/ping", headers={"Authorization": header})

        identifiers = [call[0] for call in limiter.calls]
        assert identifiers == ["ip:203.0.113.10"]

    def test_bad_token_is_not_rejected_by_the_middleware(self):
        """Auth stays the route's job; the middleware only picks a bucket."""
        limiter = FakeLimiter()
        client = client_for(limiter)

        response = client.get("/ping", headers={"Authorization": "Bearer garbage"})

        assert response.status_code == 200


@pytest.mark.unit
class TestRateLimitMiddlewareExemptions:
    """Paths and methods that must never be throttled."""

    def test_health_is_exempt(self):
        limiter = FakeLimiter()
        client = client_for(limiter, ip_limit=1)

        for _ in range(5):
            assert client.get("/health").status_code == 200
        assert limiter.calls == []

    def test_options_preflight_is_exempt(self):
        limiter = FakeLimiter()
        app = build_app(limiter, ip_limit=1)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        client = TestClient(app, client=("203.0.113.10", 51000))

        for _ in range(3):
            response = client.options(
                "/ping",
                headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "GET",
                },
            )
            assert response.status_code == 200
        assert limiter.calls == []

    def test_429_passes_through_cors_with_headers(self):
        limiter = FakeLimiter()
        app = build_app(limiter, ip_limit=1)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        client = TestClient(app, client=("203.0.113.10", 51000))
        origin = {"Origin": "http://localhost:5173"}

        client.get("/ping", headers=origin)
        response = client.get("/ping", headers=origin)

        assert response.status_code == 429
        assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

    def test_disabled_by_setting(self, monkeypatch):
        from api.middleware import rate_limit

        monkeypatch.setattr(rate_limit.settings, "rate_limit_enabled", False)
        limiter = FakeLimiter()
        client = client_for(limiter, ip_limit=1)

        for _ in range(5):
            assert client.get("/ping").status_code == 200
        assert limiter.calls == []


@pytest.mark.unit
class TestRateLimitMiddlewareResilience:
    """A broken limiter must not break the API."""

    def test_limiter_exception_fails_open(self):
        limiter = FakeLimiter(fail_with=RuntimeError("redis is down"))
        client = client_for(limiter, ip_limit=1)

        for _ in range(3):
            assert client.get("/ping").status_code == 200

    def test_failed_check_omits_rate_limit_headers(self):
        limiter = FakeLimiter(fail_with=RuntimeError("redis is down"))
        client = client_for(limiter)

        response = client.get("/ping")

        assert "X-RateLimit-Remaining" not in response.headers

    def test_window_is_passed_through_to_the_limiter(self):
        limiter = FakeLimiter()
        client = client_for(limiter, window_seconds=120)

        client.get("/ping")

        assert limiter.calls[0][2] == 120


@pytest.mark.unit
class TestRateLimitMiddlewareWiring:
    """The real application must have the middleware installed."""

    def test_installed_on_the_app(self):
        from api.main import app

        installed = [m.cls for m in app.user_middleware]
        assert RateLimitMiddleware in installed

    def test_installed_inside_cors(self):
        """CORS must wrap rate limiting so a 429 keeps its CORS headers."""
        from api.main import app

        installed = [m.cls for m in app.user_middleware]
        # Starlette runs user_middleware[0] outermost.
        assert installed.index(CORSMiddleware) < installed.index(RateLimitMiddleware)
