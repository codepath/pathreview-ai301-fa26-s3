"""Tests for api/routes/health.py"""

import contextlib
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.sql.elements import TextClause

from api.routes.health import health_check


@pytest.mark.unit
class TestHealthCheck:
    """Test suite for the /health route's PostgreSQL probe (issue #61)."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock async database session whose execute() succeeds."""
        session = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_postgres_probe_uses_text_construct(self, mock_db_session):
        """The probe must pass a SQLAlchemy text() construct, not a raw string.

        SQLAlchemy 2.x rejects a bare string with ArgumentError before any
        database I/O happens (see issue #61). Asserting on the argument's
        type catches that regression without needing a live database: this
        fails against the pre-fix `db.execute("SELECT 1")` (a plain str) and
        passes once it is wrapped in `text(...)`.

        The route also checks Redis, which raises on this fixture (the
        unrelated #62 bug), so `health_check()` raises `HTTPException`
        regardless of the postgres outcome; that happens after `db.execute`
        has already been awaited, so it doesn't affect this assertion.
        """
        with contextlib.suppress(HTTPException):
            await health_check(db=mock_db_session)

        mock_db_session.execute.assert_awaited_once()
        (statement,) = mock_db_session.execute.await_args.args
        assert isinstance(statement, TextClause), (
            f"expected a sqlalchemy text() construct, got {type(statement)!r}: "
            "a raw string is rejected by SQLAlchemy 2.x's textual-SQL coercion"
        )

    @pytest.mark.asyncio
    async def test_postgres_probe_reports_healthy_when_reachable(self, mock_db_session):
        """When the probe's execute() succeeds, postgres reports healthy.

        The route also checks Redis and the vector DB; this environment has
        no real Redis, so the unrelated #62 bug (`settings.redis_host` does
        not exist) still trips the route's overall status to unhealthy (503).
        That is expected and not part of this issue, so this test reads the
        `postgres` field specifically out of either the 200 body or the 503
        detail, rather than asserting on the overall status.
        """
        try:
            result = await health_check(db=mock_db_session)
        except HTTPException as exc:
            result = exc.detail

        assert result["dependencies"]["postgres"] == "healthy"
