"""Regression test for #61 — health check must wrap raw SQL in text()."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_reports_postgres_healthy():
    """
    The health check's DB probe must not fail with a SQLAlchemy ArgumentError.
    Before the fix, the raw string db.execute("SELECT 1") raised:
        Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')
    After the fix, the postgres dependency reports healthy.

    Note: the overall status may still be 503 if the Redis check fails (#62).
    This test asserts on dependencies.postgres specifically, isolating this fix.
    """
    response = client.get("/health")
    body = response.json()

    # The endpoint may 503 due to Redis (#62); we only care about postgres here.
    detail = body.get("detail", body)
    assert detail["dependencies"]["postgres"] == "healthy"
