"""Per-client-IP rate limiting for API requests."""

from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from safety.rate_limiter import RateLimiter

log = structlog.get_logger()

RATE_LIMIT_WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limit requests per client IP and report the limit in response headers.

    Requests to an exempt path, and OPTIONS requests (CORS preflight), pass
    through unchanged. Allowed responses carry X-RateLimit-Limit and
    X-RateLimit-Remaining. Denied requests get HTTP 429 with a Retry-After
    header.
    """

    def __init__(
        self,
        app: ASGIApp,
        limiter: RateLimiter,
        limit: int,
        window_seconds: int = RATE_LIMIT_WINDOW_SECONDS,
        exempt_paths: tuple[str, ...] = ("/health",),
    ) -> None:
        """Initialize the middleware.

        Args:
            app: The ASGI application to wrap.
            limiter: Limiter that counts requests per identifier.
            limit: Maximum requests allowed per window.
            window_seconds: Length of the rolling window in seconds.
            exempt_paths: Request paths that are never limited.
        """
        super().__init__(app)
        self.limiter = limiter
        self.limit = limit
        self.window_seconds = window_seconds
        self.exempt_paths = exempt_paths

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Check the limit for this request, then forward it or reject it.

        Args:
            request: The incoming request.
            call_next: Calls the rest of the middleware stack.

        Returns:
            The downstream response with rate-limit headers, or a 429 response.
        """
        if request.method == "OPTIONS" or request.url.path in self.exempt_paths:
            return await call_next(request)

        identifier = request.client.host if request.client else "unknown"
        allowed, remaining = await run_in_threadpool(
            self.limiter.check_rate_limit, identifier, self.limit, self.window_seconds
        )

        if not allowed:
            log.warning("request_rate_limited", identifier=identifier, path=request.url.path)
            response: Response = JSONResponse(
                {"detail": "Rate limit exceeded"},
                status_code=429,
                headers={"Retry-After": str(self.window_seconds)},
            )
            response.headers["X-RateLimit-Remaining"] = "0"
        else:
            response = await call_next(request)
            response.headers["X-RateLimit-Remaining"] = str(remaining)

        response.headers["X-RateLimit-Limit"] = str(self.limit)
        return response
