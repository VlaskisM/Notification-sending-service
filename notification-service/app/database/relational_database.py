from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from app.config.config_postgres import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.db_url, echo=True, poolclass=NullPool)

_async_session = async_sessionmaker(engine, expire_on_commit=False)

# Нужен для alembic и для Celery
sync_engine = create_engine(settings.sync_db_url, echo=True, pool_pre_ping=True)

sync_session = sessionmaker(sync_engine, expire_on_commit=False)