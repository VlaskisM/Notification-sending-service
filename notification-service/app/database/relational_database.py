from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import settings


class Base(DeclarativeBase):
    pass

engine = create_async_engine(settings.db_url, echo=True)

_async_session = async_sessionmaker(engine, expire_on_commit=False)