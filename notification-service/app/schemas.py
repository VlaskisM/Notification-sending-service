from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationCreate(BaseModel):
    type: str
    recipient: str
    message: str
    subject: str | None = None
    #channel_data: dict | None = None


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    error: str | None = None