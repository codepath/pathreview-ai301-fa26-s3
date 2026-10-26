"""Integration tests for authentication edge cases in api/middleware/auth.py (#38)."""

from datetime import timedelta

import pytest

from core.models.user import User

PROFILE_URL = "/profiles/00000000-0000-0000-0000-000000000000"
USER_ID = "11111111-1111-1111-1111-111111111111"

pytestmark = pytest.mark.integration


def test_missing_authorization_header(client, stub_db):
    """Test a request with no Authorization header gets 401 before any DB lookup."""
    response = client.get(PROFILE_URL)

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert stub_db.calls == 0


def test_malformed_token(client, stub_db):
    """Test a token that is not a JWT gets 401 before any DB lookup."""
    response = client.get(PROFILE_URL, headers={"Authorization": "Bearer not.a.jwt"})

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert stub_db.calls == 0


def test_expired_token(client, stub_db, make_token):
    """Test a correctly signed but expired token gets 401 before any DB lookup."""
    token = make_token(expires_in=timedelta(minutes=-5))

    response = client.get(PROFILE_URL, headers={"Authorization": f"Bearer {token}"})

    # Detail text is deliberately not asserted: see the "Token has expired"
    # branch at api/middleware/auth.py:44-49, discussed on #38.
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert stub_db.calls == 0


def test_wrong_signing_secret(client, stub_db, make_token):
    """Test an unexpired token signed with a different secret gets 401."""
    token = make_token(secret="not-the-app-secret")

    response = client.get(PROFILE_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert stub_db.calls == 0


def test_valid_token_reaches_route(client, stub_db, make_token):
    """Test a valid token passes auth, so the 401s above come from the middleware."""
    stub_db.queue = [User(id=USER_ID, email="jane@example.com", hashed_password="x"), None]
    token = make_token(sub=USER_ID)

    response = client.get(PROFILE_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Profile not found"
    assert stub_db.calls == 2


def test_unknown_user(client, stub_db, make_token):
    """Test a valid token for a user that no longer exists gets 401."""
    stub_db.queue = [None]
    token = make_token(sub=USER_ID)

    response = client.get(PROFILE_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert stub_db.calls == 1


def test_user_lookup_error(client, stub_db, make_token):
    """Test a database failure during the user lookup gets 500 from the middleware."""
    stub_db.queue = [RuntimeError("connection lost")]
    token = make_token(sub=USER_ID)

    response = client.get(PROFILE_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 500
    assert response.json()["detail"] == "Database error"
    assert stub_db.calls == 1
