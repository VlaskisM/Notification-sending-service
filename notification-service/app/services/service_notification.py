from abc import ABC, abstractmethod
from typing import Any, Callable
from uuid import UUID

from app.uow import UnitOfWorkInterface
from app.message_broker.notification_broker import MessageBrokerInterface
from app.schemas import NotificationCreate
from app.validators.notification_validator import (
    NotificationValidationError,
    validate
)






class NotificationNotFoundError(Exception):
    pass


class NotificationServiceInterface(ABC):

    @abstractmethod
    async def create_notification(self, notification_data: NotificationCreate) -> dict[str, Any]:
        pass

    @abstractmethod
    async def get_notification(self, notification_id: UUID) -> dict[str, Any]:
        pass

    @abstractmethod
    async def list_notifications(
        self,
        status: str | None,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        pass


class NotificationService(NotificationServiceInterface):

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWorkInterface],
        message_broker: MessageBrokerInterface,
    ):
        self._uow_factory = uow_factory
        self._message_broker = message_broker


    async def create_notification(self, notification_data: NotificationCreate) -> dict[str, Any]:
        "План: Сначала валидация данных, "

        try:
            await self.valid(notification_data)
        except NotificationValidationError as e:
            raise NotificationValidationError(str(e))

        async with self._uow_factory() as uow:

            result_response = await uow.repository.save_to_db(notification_data)

        await self._message_broker.publish(result_response)
        return result_response.model_dump(mode="json")


    async def get_notification(self, notification_id: UUID) -> dict[str, Any]:
        async with self._uow_factory() as uow:
            result = await uow.repository.get_by_id(notification_id)
        if result is None:
            raise NotificationNotFoundError(f"Notification {notification_id} not found")
        return result.model_dump(mode="json")


    async def list_notifications(
        self,
        status: str | None,
        limit: int,
        offset: int,
    ) -> list[dict[str, Any]]:
        async with self._uow_factory() as uow:
            items = await uow.repository.list(status=status, limit=limit, offset=offset)
        return [item.model_dump(mode="json") for item in items]



