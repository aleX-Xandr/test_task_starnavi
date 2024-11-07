import pytest
import pytest_asyncio

from alembic import command
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncIterator, Generator

from app.containers import container
from app.tests.fixtures import event_loop


@pytest_asyncio.fixture
async def f_engine() -> AsyncIterator[AsyncEngine]:
    test_engine = create_async_engine(
        container.config().db.master, echo=True, future=True
    )
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def f_session(f_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    async_session = sessionmaker(bind=f_engine, class_=AsyncSession)
    async with async_session() as session:
        yield session
        await session.rollback()
        await session.close()
