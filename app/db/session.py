"""
Manages asynchronous database sessions and connections with SQLAlchemy,
providing context managers for proper resource handling.

The `get_db_session` function retrieves a database session in an async context.
"""

import contextlib
from typing import Any, AsyncIterator, Dict, Optional

from sqlalchemy.ext.asyncio import (AsyncConnection, AsyncEngine, AsyncSession,
                                    async_sessionmaker)
from sqlalchemy.ext.asyncio.engine import create_async_engine

from app.config import settings


class DBSessionException(Exception):
    """
    Custom exception for database session errors.
    """

    def __init__(self, message: str):
        super().__init__(message)


class DatabaseSessionManager:
    """
    Manages asynchronous database connections and sessions using SQLAlchemy,
    ensuring proper resource management and rollback on errors.
    """

    def __init__(self, host: str, engine_kwargs: Optional[Dict[str, Any]] = None):
        """
        Initializes the database session manager with an engine and sessionmaker.
        """
        if engine_kwargs is None:
            engine_kwargs = {}

        self.engine: AsyncEngine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, bind=self.engine, expire_on_commit=False
        )

    async def close(self):
        """
        Closes the engine and sessionmaker, cleaning up resources.
        """
        if self.engine is None:
            raise DBSessionException("DatabaseSessionManager is not initialized")
        await self.engine.dispose()

        self.engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """
        Provides an asynchronous connection to the database.
        Rolls back the connection in case of an error.
        """
        if self.engine is None:
            raise DBSessionException("DatabaseSessionManager is not initialized")

        async with self.engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Provides an asynchronous database session.
        Rolls back the session in case of an error.
        """
        if self._sessionmaker is None:
            raise DBSessionException("DatabaseSessionManager is not initialized")

        session: AsyncSession = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL, {"echo": False})


async def get_db_session():
    """
    Utility function to retrieve a database session within an asynchronous context.
    """
    async with sessionmanager.session() as session:
        yield session
