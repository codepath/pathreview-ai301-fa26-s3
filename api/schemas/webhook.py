from datetime import datetime
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel


class WebhookCreate(BaseModel):
    url: AnyHttpUrl


class WebhookResponse(BaseModel):
    id: UUID
    url: str
    created_at: datetime

    model_config = {"from_attributes": True}
