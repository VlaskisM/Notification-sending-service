import logging
from abc import ABC, abstractmethod

from app.schemas import NotificationResponse
from app.tasks import send_notification

log = logging.getLogger(__name__)


class MessageBrokerInterface(ABC):

    @abstractmethod
    async def publish(self, notification: NotificationResponse):
        pass


class CeleryMessageBroker(MessageBrokerInterface):

    async def publish(self, notification: NotificationResponse):
        log.info(f"queued notification {notification.id}", )
        send_notification.delay(str(notification.id))