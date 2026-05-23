import asyncio
import logging
from uuid import UUID

from app.celery_app import celery_app
from app.database.relational_database import _async_session
from app.repositories.notification_repository import NotificationRepository
from app.uow import NotificationUnitOfWork


log = logging.getLogger(__name__)

@celery_app.task(
    name="send_notification",
    bind=True,
    max_retries=3,
    default_retry_delay=5
)
def send_notification(self, notification_id: str):
    nid = UUID(notification_id)
    try:

        log.info("A message is being sent")

        asyncio.run(_update_status(nid, status="sent"))

    except Exception as e:
        log.info("failed to send message")

        asyncio.run(_update_status(nid, status="failed", error=str(e)))
        raise self.retry(exc=e)


async def _update_status(notification_id: UUID, status: str, error: str | None = None) -> None:

    async with NotificationUnitOfWork(session_factory = _async_session, repository_factory = NotificationRepository) as uow:

        await uow.repository.update_status(notification_id, status, error)




