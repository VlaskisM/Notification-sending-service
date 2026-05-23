from abc import ABC, abstractmethod
from uuid import UUID
from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import NotificationCreate, NotificationResponse
from app.models import Notification


class NotificationRepositoryInterface(ABC):

    @abstractmethod
    async def save_to_db(self, notification_data: NotificationCreate) -> NotificationResponse:
        pass

    @abstractmethod
    async def update_status(self, notification_id: UUID, status: str, error: str | None = None) -> None:
        pass

    @abstractmethod
    async def get_by_id(self, notification_id: UUID) -> NotificationResponse | None:
        pass

    @abstractmethod
    async def list(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[NotificationResponse]:
        pass


class NotificationRepository(NotificationRepositoryInterface):

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save_to_db(self, notification_data: NotificationCreate) -> NotificationResponse:
        add_data = insert(Notification).values(
            type = notification_data.type,
            recipient = notification_data.recipient,
            subject = notification_data.subject,
            message = notification_data.message
        ).returning(Notification)

        result = await self._session.execute(add_data)
        response = result.scalars().one()
        return NotificationResponse.model_validate(response)

    async def update_status(
            self,
            notification_id: UUID,
            status: str,
            error: str | None = None,
    ) -> None:
        await self._session.execute(
            update(Notification)
            .where(Notification.id == notification_id)
            .values(status=status, error_text=error)
        )

    async def get_by_id(self, notification_id: UUID) -> NotificationResponse | None:
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self._session.execute(stmt)
        obj = result.scalars().one_or_none()
        if obj is None:
            return None
        return NotificationResponse.model_validate(obj)

    async def list(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[NotificationResponse]:
        stmt = select(Notification)
        if status is not None:
            stmt = stmt.where(Notification.status == status)
        stmt = (
            stmt.order_by(Notification.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        return [NotificationResponse.model_validate(o) for o in result.scalars().all()]
