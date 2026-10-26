from uuid import UUID

import httpx
import structlog
from sqlalchemy import and_, select

from api.schemas.review import ReviewResponse
from core.models.profile import Profile
from core.models.review import Review
from core.models.webhook import Webhook

log = structlog.get_logger()

FINISHED_STATUSES = ("complete", "failed")
DELIVERY_TIMEOUT_SECONDS = 5.0


async def register_webhook(
    db,
    user_id: str,
    url: str,
) -> Webhook:
    """
    Register a callback URL for the user.
    Returns the existing record if the user already registered this URL.
    """
    stmt = select(Webhook).where(and_(Webhook.user_id == user_id, Webhook.url == url))
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing:
        return existing

    webhook = Webhook(user_id=user_id, url=url)
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)
    return webhook


async def notify_review_finished(db, review_id: UUID) -> None:
    """
    POST the review payload to every webhook the review's owner registered.
    Only fires once the review is "complete" or "failed". Each URL gets one
    attempt; failures are logged and never raised, so delivery can't change
    the review's outcome.
    """
    try:
        # Reload from the DB: process_review's session doesn't expire on commit,
        # so the cached object can hold values that differ from GET /reviews/{id}.
        review_stmt = (
            select(Review).where(Review.id == review_id).execution_options(populate_existing=True)
        )
        result = await db.execute(review_stmt)
        review = result.scalars().first()
        if not review or review.status not in FINISHED_STATUSES:
            return

        url_stmt = (
            select(Webhook.url)
            .join(Profile, Profile.user_id == Webhook.user_id)
            .where(Profile.id == review.profile_id)
        )
        result = await db.execute(url_stmt)
        urls = result.scalars().all()
        if not urls:
            return

        payload = ReviewResponse.model_validate(review).model_dump(mode="json")
    except Exception as exc:
        log.error("webhook_lookup_failed", review_id=str(review_id), error=str(exc))
        return

    try:
        async with httpx.AsyncClient(timeout=DELIVERY_TIMEOUT_SECONDS) as client:
            for url in urls:
                try:
                    response = await client.post(url, json=payload)
                    log.info(
                        "webhook_delivered",
                        review_id=str(review_id),
                        url=url,
                        status_code=response.status_code,
                    )
                except Exception as exc:
                    log.warning(
                        "webhook_delivery_failed",
                        review_id=str(review_id),
                        url=url,
                        error=str(exc),
                    )
    except Exception as exc:
        log.error("webhook_client_failed", review_id=str(review_id), error=str(exc))
