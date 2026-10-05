import asyncio
import os

# core.database builds its engine at import time from DATABASE_URL; point it
# at SQLite so the test does not need asyncpg or a running Postgres.
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from api.routes.health import health_check


def _run_health_check():
    async def run():
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        try:
            async with AsyncSession(engine) as session:
                try:
                    return await health_check(db=session)
                except HTTPException as exc:
                    return exc.detail
        finally:
            await engine.dispose()

    return asyncio.run(run())


def test_postgres_probe_reports_healthy_when_database_answers():
    # Regression for #61: a bare "SELECT 1" string is rejected by SQLAlchemy 2.x
    # before it reaches the database, so the probe reported a live DB as down.
    body = _run_health_check()
    assert body["dependencies"]["postgres"] == "healthy"
