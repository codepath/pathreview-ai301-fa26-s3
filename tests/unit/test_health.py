
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import TextClause
from sqlalchemy.ext.asyncio import AsyncSession

from api.routes.health import health_check


@pytest.mark.asyncio
@pytest.mark.unit
async def test_health_check_uses_text_for_database_probe():
    """The database health probe must use SQLAlchemy's text() construct."""
    session = AsyncSession()
    captured = {}

    async def execute(statement):
        captured["statement"] = statement
        return AsyncMock()

    session.execute = execute

    mock_settings = MagicMock()
    mock_settings.redis_host = "localhost"
    mock_settings.redis_port = 6379
    mock_settings.vector_db_url = "http://localhost:8000"

    mock_redis = MagicMock()
    mock_redis.return_value.ping.return_value = True

    with patch("core.config.settings", mock_settings), patch(
        "redis.Redis", mock_redis
    ):
        result = await health_check(session)

    assert isinstance(captured["statement"], TextClause)
    assert str(captured["statement"]) == "SELECT 1"
    assert result["dependencies"]["postgres"] == "healthy"

    await session.close()
