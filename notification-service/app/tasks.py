import logging
from uuid import UUID

from sqlalchemy import update

from app.celery_app import celery_app
from app.database.relational_database import sync_session
from app.models import Notification


log = logging.getLogger(__name__)


@celery_app.task(
    name="send_notification",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def send_notification(self, notification_id: str):
    nid = UUID(notification_id)
    log.info("processing notification id=%s", nid)
    try:
        _update_status(nid, status="sent")
        log.info("notification sent id=%s", nid)
    except Exception as e:
        log.error("notification failed id=%s error=%s", nid, e)
        _update_status(nid, status="failed", error=str(e))
        raise self.retry(exc=e)


def _update_status(
    notification_id: UUID,
    status: str,
    error: str | None = None,
) -> None:
    with sync_session() as session:
        session.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(status=status, error_text=error)
        )
        session.commit()
