from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from floranova.config import settings

# Engine configuration
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    # SQLite performance tuning
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    # Set WAL mode and foreign keys for SQLite
    if "sqlite" in settings.DATABASE_URL:
        async with engine.begin() as conn:
            await conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
            await conn.exec_driver_sql("PRAGMA foreign_keys=ON;")
            await conn.run_sync(Base.metadata.create_all)
    else:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
