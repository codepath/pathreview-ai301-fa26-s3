"""Rate limiting middleware.

Applies :class:`safety.rate_limiter.RateLimiter` to every incoming request. Each
request is checked against a per-client-IP bucket, and additionally against a
per-user bucket when the request carries a decodable bearer token.

Both buckets must have capacity for the request to proceed, so an authenticated
caller cannot exceed the IP budget by signing in, and an anonymous flood from a
single host is capped even though it has no user ID.
"""

import asyncio
from collections.abc import Awaitable, Callable

import redis
import structlog
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from core.config import settings
from core.security import decode_access_token
from safety.rate_limiter import RateLimiter

log = structlog.get_logger()

# Paths that are never rate limited. Health checks are polled by monitoring on a
# fixed interval and must not be throttled, and the schema/docs routes are static.
DEFAULT_EXEMPT_PATHS = frozenset(
    {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    }
)

UNKNOWN_CLIENT = "unknown"


def build_redis_client() -> redis.Redis:
    """Build the Redis client used for rate limit counters.

    Returns:
        A Redis client pointed at ``settings.redis_url``. ``redis.from_url`` is
        lazy, so this does not connect and does not raise when Redis is down.
    """
    return redis.from_url(settings.redis_url, decode_responses=True)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enforce per-IP and per-user rate limits on every request.

    Attributes:
        limiter: The rate limiter backing the counters.
        ip_limit: Maximum requests per window from a single client IP.
        user_limit: Maximum requests per window from a single authenticated user.
        window_seconds: Length of the rolling window, in seconds.
        exempt_paths: Paths that bypass rate limiting entirely.
    """

    def __init__(
        self,
        app: ASGIApp,
        limiter: RateLimiter | None = None,
        ip_limit: int | None = None,
        user_limit: int | None = None,
        window_seconds: int | None = None,
        exempt_paths: frozenset[str] | None = None,
    ) -> None:
        """Initialize the middleware.

        Args:
            app: The ASGI application being wrapped.
            limiter: Rate limiter to use. Defaults to one backed by Redis.
            ip_limit: Per-IP request budget. Defaults to the configured value.
            user_limit: Per-user request budget. Defaults to the configured value.
            window_seconds: Rolling window length. Defaults to the configured value.
            exempt_paths: Paths to skip. Defaults to :data:`DEFAULT_EXEMPT_PATHS`.
        """
        super().__init__(app)
        self.limiter = limiter if limiter is not None else RateLimiter(build_redis_client())
        self.ip_limit = ip_limit if ip_limit is not None else settings.rate_limit_per_ip_per_minute
        self.user_limit = user_limit if user_limit is not None else settings.rate_limit_per_minute
        self.window_seconds = (
            window_seconds if window_seconds is not None else settings.rate_limit_window_seconds
        )
        self.exempt_paths = exempt_paths if exempt_paths is not None else DEFAULT_EXEMPT_PATHS

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Check the request against each applicable bucket before handling it.

        Args:
            request: The incoming request.
            call_next: The next handler in the middleware chain.

        Returns:
            A ``429`` response if any bucket is exhausted, otherwise the
            downstream response with ``X-RateLimit-*`` headers attached.
        """
        if not self._should_limit(request):
            return await call_next(request)

        buckets: list[tuple[str, str, int]] = [
            ("ip", f"ip:{self._client_ip(request)}", self.ip_limit)
        ]
        user_id = self._user_id(request)
        if user_id is not None:
            buckets.append(("user", f"user:{user_id}", self.user_limit))

        # Headers report the tightest bucket, i.e. whichever is closest to denial.
        tightest_limit = self.ip_limit
        tightest_remaining: int | None = None

        for scope, identifier, limit in buckets:
            try:
                allowed, remaining = await asyncio.to_thread(
                    self.limiter.check_rate_limit, identifier, limit, self.window_seconds
                )
            except Exception as exc:
                # Fail open: a limiter outage must not take the API down. The
                # limiter already swallows Redis errors itself; this guards
                # against anything it does not catch.
                log.error("rate_limit_check_failed", scope=scope, error=str(exc))
                continue

            if not allowed:
                log.warning(
                    "rate_limit_rejected",
                    scope=scope,
                    identifier=identifier,
                    limit=limit,
                    path=request.url.path,
                    method=request.method,
                )
                return self._rate_limited_response(request, scope, limit)

            if tightest_remaining is None or remaining < tightest_remaining:
                tightest_remaining = remaining
                tightest_limit = limit

        response = await call_next(request)
        if tightest_remaining is not None:
            response.headers["X-RateLimit-Limit"] = str(tightest_limit)
            response.headers["X-RateLimit-Remaining"] = str(tightest_remaining)
            response.headers["X-RateLimit-Window"] = str(self.window_seconds)
        return response

    def _should_limit(self, request: Request) -> bool:
        """Report whether this request is subject to rate limiting.

        Args:
            request: The incoming request.

        Returns:
            False for disabled limiting, CORS preflight requests and exempt
            paths; True otherwise.
        """
        if not settings.rate_limit_enabled:
            return False
        # Preflight requests carry no credentials and must always succeed, or
        # the browser reports a CORS failure instead of the real 429.
        if request.method == "OPTIONS":
            return False
        return request.url.path not in self.exempt_paths

    @staticmethod
    def _client_ip(request: Request) -> str:
        """Return the client IP for this request.

        Uses the peer address from the connection rather than ``X-Forwarded-For``,
        which a caller can set freely and so cannot be trusted without a known
        proxy in front of the app.

        Args:
            request: The incoming request.

        Returns:
            The client IP, or ``"unknown"`` when the server reports no peer.
        """
        if request.client is None or not request.client.host:
            return UNKNOWN_CLIENT
        return request.client.host

    @staticmethod
    def _user_id(request: Request) -> str | None:
        """Extract the user ID from the request's bearer token, if any.

        The token is decoded locally and no database lookup is performed, so an
        unauthenticated or invalid token costs nothing here. Rejecting bad
        tokens stays the job of the route's auth dependency; this only decides
        whether a per-user bucket applies.

        Args:
            request: The incoming request.

        Returns:
            The ``sub`` claim as a string, or None when absent or undecodable.
        """
        header = request.headers.get("Authorization")
        if not header:
            return None

        scheme, _, token = header.partition(" ")
        if scheme.lower() != "bearer" or not token:
            return None

        payload = decode_access_token(token.strip())
        if not payload:
            return None

        subject = payload.get("sub")
        return str(subject) if subject else None

    def _rate_limited_response(self, request: Request, scope: str, limit: int) -> JSONResponse:
        """Build the 429 response for an exhausted bucket.

        Args:
            request: The incoming request.
            scope: Which bucket was exhausted, ``"ip"`` or ``"user"``.
            limit: The budget for that bucket.

        Returns:
            A ``429 Too Many Requests`` response.
        """
        content: dict[str, object] = {
            "detail": (
                f"Rate limit exceeded: more than {limit} requests per "
                f"{self.window_seconds} seconds from this {scope}. "
                f"Retry after {self.window_seconds} seconds."
            ),
            "scope": scope,
        }

        request_id = getattr(request.state, "request_id", None)
        if request_id:
            content["request_id"] = request_id

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=content,
            headers={
                # The limiter reports remaining capacity but not when the oldest
                # entry leaves the window, so the full window is the safe upper
                # bound to advertise.
                "Retry-After": str(self.window_seconds),
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Window": str(self.window_seconds),
            },
        )
