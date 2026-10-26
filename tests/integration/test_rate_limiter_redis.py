"""RateLimiter against a real Redis: the Lua script's counts, pruning, TTL, and concurrency."""

import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
import redis

from core.config import settings
from safety.rate_limiter import RateLimiter


@pytest.fixture
def store() -> redis.Redis:
    """Real Redis client from settings."""
    return redis.Redis.from_url(settings.redis_url)


@pytest.fixture
def identifier(store: redis.Redis):
    """A unique identifier per test, with its key removed afterwards."""
    ident = f"test-{uuid.uuid4().hex}"
    yield ident
    store.delete(f"rate_limit:{ident}")


@pytest.mark.integration
class TestRateLimiterRedis:
    """Behavior of RateLimiter.check_rate_limit against a real Redis."""

    def test_counts_remaining_and_denies_at_limit(self, store, identifier):
        """Three allowed requests report 2, 1, 0 remaining; the fourth is denied."""
        limiter = RateLimiter(store)

        results = [limiter.check_rate_limit(identifier, limit=3) for _ in range(4)]

        assert results == [(True, 2), (True, 1), (True, 0), (False, 0)]

    def test_entries_outside_window_are_pruned(self, store, identifier):
        """After the window passes, previously counted requests stop counting."""
        limiter = RateLimiter(store)

        assert limiter.check_rate_limit(identifier, limit=2, window_seconds=1) == (True, 1)
        assert limiter.check_rate_limit(identifier, limit=2, window_seconds=1) == (True, 0)
        assert limiter.check_rate_limit(identifier, limit=2, window_seconds=1) == (False, 0)

        time.sleep(1.1)

        assert limiter.check_rate_limit(identifier, limit=2, window_seconds=1) == (True, 1)

    def test_key_expires_after_window_plus_one(self, store, identifier):
        """The key's TTL is set to window_seconds + 1, as the original implementation did."""
        limiter = RateLimiter(store)

        limiter.check_rate_limit(identifier, limit=10, window_seconds=60)

        ttl = store.ttl(f"rate_limit:{identifier}")
        assert 59 <= ttl <= 61

    def test_concurrent_requests_admit_exactly_the_limit(self, store, identifier):
        """Regression: 20 simultaneous requests with limit 10 admit exactly 10.

        Before the atomic script, concurrent requests could all read a count below the
        limit and all be admitted.
        """
        limiter = RateLimiter(store)
        limit = 10

        with ThreadPoolExecutor(max_workers=20) as pool:
            results = list(
                pool.map(lambda _: limiter.check_rate_limit(identifier, limit), range(20))
            )

        assert sum(1 for allowed, _ in results if allowed) == limit
        assert sum(1 for allowed, _ in results if not allowed) == 20 - limit
        # Every admitted request left its own member in the sorted set.
        assert store.zcard(f"rate_limit:{identifier}") == limit

    def test_fails_open_when_redis_is_unreachable(self):
        """With no Redis listening, the limiter returns (True, limit) instead of raising."""
        unreachable = redis.Redis(host="127.0.0.1", port=1, socket_connect_timeout=0.2)
        limiter = RateLimiter(unreachable)

        assert limiter.check_rate_limit("unreachable-test", limit=10) == (True, 10)
