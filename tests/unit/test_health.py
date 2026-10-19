"""Tests for the dependency health endpoint."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.sql.elements import TextClause

from api.routes.health import health_check


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health_check_uses_text_clause_for_postgres_probe() -> None:
    """The PostgreSQL probe declares its textual SQL for SQLAlchemy 2.x."""
    db = AsyncMock()
    test_settings = SimpleNamespace(
        redis_host="localhost",
        redis_port=6379,
        vector_db_url="http://localhost:8001",
    )

    with (
        patch("core.config.settings", test_settings),
        patch("redis.Redis") as redis_client,
    ):
        redis_client.return_value.ping.return_value = True
        response = await health_check(db=db)

    db.execute.assert_awaited_once()
    statement = db.execute.await_args.args[0]
    assert isinstance(statement, TextClause)
    assert str(statement) == "SELECT 1"
    assert response["status"] == "healthy"
    assert response["dependencies"]["postgres"] == "healthy"
