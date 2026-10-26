"""Tests for webhook_service.notify_review_finished"""

import json
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from structlog.testing import capture_logs

from core.services.webhook_service import notify_review_finished


def _review(status: str) -> SimpleNamespace:
    """A review with every field ReviewResponse reads."""
    now = datetime(2026, 10, 7, 12, 0, 0)
    return SimpleNamespace(
        id=uuid4(),
        profile_id=uuid4(),
        status=status,
        sections=None,
        overall_score=None,
        error_message=None,
        created_at=now,
        updated_at=now,
    )


def _result(*, first=None, all_=None) -> Mock:
    """A db.execute() result whose .scalars() yields first/all_."""
    result = Mock()
    result.scalars.return_value.first.return_value = first
    result.scalars.return_value.all.return_value = all_ or []
    return result


def _session(review, urls) -> AsyncMock:
    """A session that returns the review, then the owner's webhook URLs."""
    session = AsyncMock()
    session.execute = AsyncMock(side_effect=[_result(first=review), _result(all_=urls)])
    return session


@pytest.mark.unit
class TestNotifyReviewFinished:
    """Test suite for notify_review_finished."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status", ["complete", "failed"])
    async def test_finished_review_is_posted_once(self, httpserver, status):
        """A finished review sends one POST whose body matches the review."""
        review = _review(status)
        httpserver.expect_oneshot_request("/hook", method="POST").respond_with_data("ok")

        with capture_logs() as logs:
            await notify_review_finished(_session(review, [httpserver.url_for("/hook")]), review.id)

        httpserver.check_assertions()
        assert len(httpserver.log) == 1
        body = json.loads(httpserver.log[0][0].get_data())
        assert body["id"] == str(review.id)
        assert body["status"] == status
        delivered = [e for e in logs if e["event"] == "webhook_delivered"]
        assert len(delivered) == 1
        assert delivered[0]["status_code"] == 200

    @pytest.mark.asyncio
    async def test_review_is_reloaded_from_db(self):
        """The review query refreshes cached state so the payload matches GET."""
        review = _review("complete")
        session = _session(review, [])

        await notify_review_finished(session, review.id)

        review_stmt = session.execute.await_args_list[0].args[0]
        assert review_stmt.get_execution_options().get("populate_existing") is True

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status", ["pending", "processing"])
    async def test_unfinished_review_is_not_posted(self, httpserver, status):
        """A review that isn't finished sends nothing and skips the URL lookup."""
        review = _review(status)
        session = _session(review, [httpserver.url_for("/hook")])

        await notify_review_finished(session, review.id)

        assert len(httpserver.log) == 0
        assert session.execute.await_count == 1

    @pytest.mark.asyncio
    async def test_missing_review_is_not_posted(self, httpserver):
        """A review id that doesn't exist sends nothing."""
        session = _session(None, [httpserver.url_for("/hook")])

        await notify_review_finished(session, uuid4())

        assert len(httpserver.log) == 0

    @pytest.mark.asyncio
    async def test_owner_without_webhooks_is_not_posted(self, httpserver):
        """An owner with no registered URLs sends nothing."""
        review = _review("complete")

        with capture_logs() as logs:
            await notify_review_finished(_session(review, []), review.id)

        assert len(httpserver.log) == 0
        assert not [e for e in logs if e["event"].startswith("webhook_")]

    @pytest.mark.asyncio
    async def test_unreachable_url_is_logged_not_raised(self):
        """A refused connection is logged as a failed delivery."""
        review = _review("complete")
        session = _session(review, ["http://127.0.0.1:1/hook"])

        with capture_logs() as logs:
            await notify_review_finished(session, review.id)

        failed = [e for e in logs if e["event"] == "webhook_delivery_failed"]
        assert len(failed) == 1
        assert failed[0]["url"] == "http://127.0.0.1:1/hook"

    @pytest.mark.asyncio
    async def test_broken_session_is_logged_not_raised(self, httpserver):
        """A session whose execute raises is logged, and nothing is sent."""
        session = AsyncMock()
        session.execute = AsyncMock(side_effect=RuntimeError("connection closed"))

        with capture_logs() as logs:
            await notify_review_finished(session, uuid4())

        assert len(httpserver.log) == 0
        assert [e["event"] for e in logs] == ["webhook_lookup_failed"]
