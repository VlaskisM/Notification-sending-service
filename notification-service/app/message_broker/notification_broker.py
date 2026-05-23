from abc import ABC, abstractmethod

from app.schemas import NotificationResponse
from app.tasks import send_notification

class MessageBrokerInterface(ABC):

    @abstractmethod
    async def publish(self, notification: NotificationResponse):
        pass


class CeleryMessageBroker(MessageBrokerInterface):

    async def publish(self, notification: NotificationResponse):
        send_notification.delay(str(notification.id))