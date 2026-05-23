from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
    error: str | None = Field(default=None, validation_alias="error_text")