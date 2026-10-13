"""Unit tests for the /health route."""

import asyncio
import contextlib
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.sql.elements import TextClause

from api.routes.health import health_check


@pytest.mark.unit
def test_postgres_probe_uses_text_clause():
    """SQLAlchemy 2.x rejects a bare string; the probe must pass text()."""
    db = AsyncMock()

    async def execute(statement):
        if isinstance(statement, str):
            raise TypeError("Textual SQL expression should be explicitly declared as text()")

    db.execute.side_effect = execute

    # redis/vector probes may raise HTTPException; only the postgres call matters here
    with contextlib.suppress(Exception):
        asyncio.run(health_check(db=db))

    statement = db.execute.call_args.args[0]
    assert isinstance(statement, TextClause)
