"""Rate limiting with rolling window."""

import time
import uuid

import redis
import structlog

logger = structlog.get_logger()

# Prune expired entries, count the window, and admit the request in one atomic Redis call,
# so concurrent requests cannot all read a count below the limit.
# ARGV: now, window_seconds, limit, member. Returns {1, remaining} if admitted, {0, 0} if not.
SLIDING_WINDOW_SCRIPT = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local count = redis.call('ZCARD', key)
if count < limit then
  redis.call('ZADD', key, now, ARGV[4])
  redis.call('EXPIRE', key, window + 1)
  return {1, limit - count - 1}
end
return {0, 0}
"""


class RateLimiter:
    """Rate limiter using Redis sorted sets for rolling window."""

    def __init__(self, redis_client: redis.Redis):
        """Initialize rate limiter.

        Args:
            redis_client: Redis client
        """
        self.redis = redis_client
        self._check_script = redis_client.register_script(SLIDING_WINDOW_SCRIPT)

    def check_rate_limit(
        self, identifier: str, limit: int, window_seconds: int = 60
    ) -> tuple[bool, int]:
        """Check if request is within rate limit.

        The check and the admission happen atomically in Redis. Each request is stored under
        a unique member, so requests that share a timestamp are still counted separately.

        Args:
            identifier: Request identifier (user_id, ip_address, etc.)
            limit: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (allowed, remaining_requests)
        """
        key = f"rate_limit:{identifier}"
        now = time.time()
        member = f"{now}:{uuid.uuid4().hex}"

        try:
            allowed, remaining = self._check_script(
                keys=[key], args=[now, window_seconds, limit, member]
            )
        except Exception as e:
            logger.error("rate_limiter_error", identifier=identifier, error=str(e))
            # Fail open on Redis error
            return True, limit

        if allowed:
            logger.info(
                "rate_limit_allowed",
                identifier=identifier,
                current_count=limit - remaining,
                limit=limit,
            )
            return True, int(remaining)

        logger.warning("rate_limit_exceeded", identifier=identifier, limit=limit)
        return False, 0
