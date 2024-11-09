from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import expression
from sqlmodel import Field

from app.configs import DbConfig
from app.exceptions import LogicError


class UTCNow(expression.FunctionElement):
    type = DateTime()

@compiles(UTCNow, "postgresql")
def pg_utcnow(_, __, **___):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class DB:
    def __init__(self, config: DbConfig, *, debug: bool = False):
        self._config = config
        self._debug = debug
        self._db_url = self._config.master
        self._engine: AsyncEngine | None = None
        self._async_session: AsyncSession | None = None

    async def init_db(self, db_url: str | None = None):
        if isinstance(db_url, str):
            self._db_url = db_url

        self._engine = create_async_engine(
            self._db_url,
            echo=self._debug,
            future=True,
            poolclass=NullPool,
        )

        self._async_session = sessionmaker( #type: ignore
            self._engine, class_=AsyncSession, expire_on_commit=False
        )

    @property
    def db_url(self):
        return self._db_url

    async def dispose(self):
        await self._engine.dispose()

    @asynccontextmanager
    async def get_session(self):
        await self.init_db()

        session: AsyncSession = self._async_session()
        async with session:
            try:
                yield session
            except LogicError as e:
                await session.rollback()
                raise e
            except Exception:
                await session.rollback()
                raise
            else:
                await session.commit()
            finally:
                await session.close()
