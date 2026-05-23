from abc import ABC, abstractmethod
from typing import Callable

from app.uow import UnitOfWorkInterface
from app.message_broker.notification_broker import MessageBrokerInterface
from app.schemas import NotificationCreate



class NotificationValidationError(Exception):
    pass


class NotificationServiceInterface(ABC):

    @abstractmethod
    async def create_notification(self, notification_data: NotificationCreate):
        pass


class NotificationService(NotificationServiceInterface):

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWorkInterface],
        message_broker: MessageBrokerInterface,
    ):
        self._uow_factory = uow_factory
        self._message_broker = message_broker


    async def create_notification(self, notification_data: NotificationCreate):
        "План: Сначала валидация данных, "


        data_valid = await self._data_validation(notification_data)

        if not data_valid:
            raise NotificationValidationError("Invalid notification data")

        async with self._uow_factory() as uow:

            result_response = await uow.repository.save_to_db(notification_data)
    
        await self._message_broker.publish(result_response)
        return result_response


    async def _data_validation(self, notification_data):
        pass


