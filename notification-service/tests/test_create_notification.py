import pytest
from uuid import UUID
from typing import Any, Callable

from app.services.service_notification import NotificationService
from app.uow import UnitOfWorkInterface
from app.repositories.notification_repository import NotificationRepositoryInterface
from app.schemas import NotificationCreate, NotificationResponse
from app.message_broker.notification_broker import MessageBrokerInterface
from app.validators.notification_validator import validate


@pytest.fixture
def valid_email():
    return NotificationCreate(
        type="email",
        recipient="test@example.com",
        message="Hello, this is a test email notification.",
    )

class FakeUnitOfWork(UnitOfWorkInterface):

    def __init__(self, repository: NotificationRepositoryInterface):
        self.repository = repository

    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc_val, exc_tb): pass
    async def commit(self): pass
    async def rollback(self): pass

class FakeNotificationRepository(NotificationRepositoryInterface):

    def __init__(self):
        self.saved_notifications = []

    async def save_to_db(self, notification_data: NotificationCreate) -> NotificationResponse:
        response = NotificationResponse(
            id="123e4567-e89b-12d3-a456-426614174000",
            type=notification_data.type,
            recipient=notification_data.recipient,
            subject=notification_data.subject,
            message=notification_data.message,
            status="pending",
            error_text=None,
        )

        self.saved_notifications.append(response)
        return response
    
    async def update_status(self, notification_id: str, status: str, error: str | None = None) -> None: pass
    async def get_by_id(self, notification_id: str) -> NotificationResponse | None: pass
    async def list(self,status: str | None = None,limit: int = 50,offset: int = 0) -> list[NotificationResponse]:pass

class FakeMessageBroker(MessageBrokerInterface):

    def __init__(self):
        self.published_messages = []

    async def publish(self, message: NotificationResponse) -> None:
        self.published_messages.append(message)

@pytest.mark.asyncio
async def test_create_notification(valid_email):

    notification_service = NotificationService(
    uow_factory=lambda: FakeUnitOfWork(
        repository=FakeNotificationRepository()
    ),
    message_broker=FakeMessageBroker()
)

    result = await notification_service.create_notification(valid_email)
    assert result["id"] == "123e4567-e89b-12d3-a456-426614174000"
    assert result["status"] == "queued"



    
    
    

    
    