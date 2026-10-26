"""Shared test fixtures for PathReview."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest


@pytest.fixture
def sample_resume_text() -> str:
    """Return a sample resume text for testing."""
    return """
    Jane Doe
    Software Engineer
    jane.doe@example.com | github.com/janedoe

    Experience:
    - Software Engineer at TechCorp (2022-2024)
      Built REST APIs using Python and FastAPI.

    Education:
    - B.S. Computer Science, State University (2022)

    Skills: Python, JavaScript, React, PostgreSQL, Docker
    """


@pytest.fixture
def sample_readme_text() -> str:
    """Return a sample README text for testing."""
    return """
    # Weather App
    A weather forecasting application built with React and OpenWeatherMap API.

    ## Features
    - Current weather display
    - 5-day forecast
    - Location search

    ## Tech Stack
    - React 18
    - TypeScript
    - Tailwind CSS
    - OpenWeatherMap API
    """


class _StubResult:
    """Stands in for a SQLAlchemy result holding at most one row."""

    def __init__(self, value: Any) -> None:
        self._value = value

    def scalar_one_or_none(self) -> Any:
        """Return the stored row, or None if there is none."""
        return self._value

    def scalars(self) -> "_StubResult":
        """Return this result, so .scalars().first() reads the stored row."""
        return self

    def first(self) -> Any:
        """Return the stored row, or None if there is none."""
        return self._value


class StubSession:
    """Async session stub: each execute() returns (or raises) the next queued item."""

    def __init__(self) -> None:
        self.queue: list[Any] = []
        self.calls = 0

    async def execute(self, _stmt: Any) -> _StubResult:
        """Record the call and return the next queued item as a result.

        Args:
            _stmt: The SQLAlchemy statement. Ignored; the queue decides the result.

        Returns:
            A result wrapping the next queued item (None if the queue is empty).

        Raises:
            Exception: The next queued item, if it is an exception.
        """
        self.calls += 1
        item = self.queue.pop(0) if self.queue else None
        if isinstance(item, Exception):
            raise item
        return _StubResult(item)


@pytest.fixture
def stub_db() -> StubSession:
    """Return a fresh stub database session."""
    return StubSession()


@pytest.fixture
def client(stub_db: StubSession) -> Iterator[Any]:
    """Return a TestClient for the real app with get_db overridden by stub_db.

    The app is imported here rather than at module level so unit tests never
    load it. TestClient is not entered as a context manager, so the startup
    hook (which needs Postgres) does not run.
    """
    from fastapi.testclient import TestClient

    from api.main import app
    from core.database import get_db

    async def _override_get_db() -> Any:
        yield stub_db

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def make_token() -> Any:
    """Return a helper that signs a JWT like the app does, with overridable claims."""
    from jose import jwt

    from core.config import settings

    def _make(
        sub: str | None = "11111111-1111-1111-1111-111111111111",
        expires_in: timedelta = timedelta(minutes=5),
        secret: str | None = None,
    ) -> str:
        claims: dict[str, Any] = {"exp": datetime.now(UTC) + expires_in}
        if sub is not None:
            claims["sub"] = sub
        return jwt.encode(claims, secret or settings.secret_key, algorithm=settings.jwt_algorithm)

    return _make
