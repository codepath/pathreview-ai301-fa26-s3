"""Tests for api/routes/health.py"""

import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from api.routes.health import health_check


@pytest.mark.unit
class TestHealthCheck:
    """Test suite for the /health route's dependency probes."""

    @pytest.fixture
    def sqlite_session_factory(self):
        """A lightweight in-memory async session, standing in for Postgres."""
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        return async_sessionmaker(engine, expire_on_commit=False)

    def test_postgres_probe_reports_healthy_when_reachable(self, sqlite_session_factory):
        """The postgres probe should report healthy when the DB answers SELECT 1.

        Regression test for issue #61: the probe used to pass a bare string
        to db.execute(), which SQLAlchemy 2.x rejects with an ArgumentError
        before it ever reaches the database. The overall response can still
        be a 503 here because of the unrelated redis probe (#62, out of
        scope for this fix) -- only the postgres dependency is asserted.
        """

        async def run():
            async with sqlite_session_factory() as session:
                try:
                    return await health_check(db=session)
                except HTTPException as exc:
                    return exc.detail

        body = asyncio.run(run())

        assert body["dependencies"]["postgres"] == "healthy"
