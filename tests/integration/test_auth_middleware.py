"""Integration tests for the authentication middleware (issue #38).

Each test calls a real protected route on the real app with a missing or
bad token and checks that ``get_current_user`` in
``api/middleware/auth.py`` rejects it with a 401 and a
``WWW-Authenticate: Bearer`` header. None of these cases reach the
database: every bad token is rejected before the user lookup. The app's
startup hook does need Postgres, so the client fixture skips it (see
``client`` below), and the tests run with no services up.
"""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from api.main import app
from core.config import settings

PROTECTED_URL = "/profiles/00000000-0000-0000-0000-000000000000"
FAKE_USER_ID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture(scope="module")
def client():
    """Return a test client for the real app without running its startup hook.

    Using ``TestClient`` outside a ``with`` block skips the app's startup
    event, which calls ``init_db()`` and fails when Postgres is not
    running. The middleware under test does not need the database, so
    skipping startup keeps these tests runnable with no services up.
    """
    return TestClient(app)


def _make_token(secret: str, expires_in: timedelta) -> str:
    """Build a JWT for FAKE_USER_ID signed with ``secret``, using the app's algorithm."""
    return jwt.encode(
        {"sub": FAKE_USER_ID, "exp": datetime.now(UTC) + expires_in},
        secret,
        algorithm=settings.jwt_algorithm,
    )


def _assert_unauthorized(response) -> None:
    """Check that a response is a 401 carrying the Bearer challenge header."""
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.integration
class TestAuthMiddlewareEdgeCases:
    """A protected route rejects missing or bad tokens with 401."""

    def test_missing_authorization_header(self, client):
        """A request with no Authorization header is rejected."""
        response = client.get(PROTECTED_URL)
        _assert_unauthorized(response)

    def test_malformed_token(self, client):
        """A bearer value that is not a JWT at all is rejected."""
        response = client.get(PROTECTED_URL, headers={"Authorization": "Bearer not.a.real.token"})
        _assert_unauthorized(response)

    def test_expired_token(self, client):
        """A token signed with the real secret but already expired is rejected."""
        token = _make_token(settings.secret_key, timedelta(minutes=-5))
        response = client.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})
        _assert_unauthorized(response)

    def test_wrong_signing_secret(self, client):
        """A valid-looking token signed with a different secret is rejected."""
        token = _make_token("a-totally-different-secret", timedelta(minutes=30))
        response = client.get(PROTECTED_URL, headers={"Authorization": f"Bearer {token}"})
        _assert_unauthorized(response)
