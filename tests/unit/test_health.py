"""Tests for api/routes/health.py"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.sql.elements import TextClause

from api.routes.health import health_check


@pytest.mark.unit
class TestHealthCheck:
    """Test suite for the health_check route."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock async database session."""
        session = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_postgres_healthy_and_probe_uses_text_clause(self, mock_db_session):
        """Test postgres is healthy and db.execute receives a text() clause, not a raw string."""
        with patch("redis.Redis") as MockRedis, patch("core.config.settings") as mock_settings:
            MockRedis.return_value.ping = Mock(return_value=True)
            mock_settings.vector_db_url = "http://localhost:8000"

            result = await health_check(db=mock_db_session)

        assert result["dependencies"]["postgres"] == "healthy"
        mock_db_session.execute.assert_called_once()
        statement = mock_db_session.execute.call_args[0][0]
        assert isinstance(statement, TextClause)
        assert str(statement) == "SELECT 1"
