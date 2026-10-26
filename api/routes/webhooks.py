import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from api.middleware.auth import get_current_user
from api.schemas.webhook import WebhookCreate, WebhookResponse
from core.database import get_db
from core.models.user import User
from core.services.webhook_service import register_webhook

log = structlog.get_logger()

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("", response_model=WebhookResponse)
async def register_webhook_endpoint(
    data: WebhookCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Register a callback URL for the current user.
    When any of the user's reviews reaches "complete" or "failed", the URL
    receives a POST whose JSON body matches GET /reviews/{review_id}.
    Registering the same URL again returns the existing webhook.
    """
    try:
        webhook = await register_webhook(db=db, user_id=current_user.id, url=str(data.url))

        log.info(
            "webhook_registered",
            webhook_id=str(webhook.id),
            user_id=str(current_user.id),
        )

        return WebhookResponse.model_validate(webhook)

    except HTTPException:
        raise
    except Exception as exc:
        log.error("webhook_registration_error", error=str(exc))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register webhook",
        )
