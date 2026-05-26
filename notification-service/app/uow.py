from abc import ABC, abstractmethod
from typing import Callable, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.notification_repository import NotificationRepositoryInterface
from app.message_broker.notification_broker import MessageBrokerInterface
from app.schemas import NotificationResponse, NotificationCreate


class UnitOfWorkInterface(ABC):

    repository: NotificationRepositoryInterface

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass


class NotificationUnitOfWork(UnitOfWorkInterface):

    def __init__(
            self,
            session_factory: Callable[[], AsyncSession],
            repository_factory: Callable[[AsyncSession], NotificationRepositoryInterface]
        ):
        self._session_factory = session_factory
        self._repository_factory = repository_factory

    async def __aenter__(self):
        self._session = self._session_factory()
        self.repository = self._repository_factory(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                await self.rollback()
            else:
                try:
                    await self.commit()
                except Exception:
                    await self.rollback()
                    raise
        finally:
            await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
