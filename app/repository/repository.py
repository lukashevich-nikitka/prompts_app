from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union

from sqlalchemy import ColumnElement, Select, Update, delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import sessionmanager
from app.models.base import Base

T = TypeVar("T", bound=Base)


class AppRepoInterface(ABC):
    @abstractmethod
    async def create(self, instance: T, dbsession: AsyncSession) -> T:
        pass

    @abstractmethod
    async def get(
        self,
        dbsession: AsyncSession,
        model: T,
        which: Optional[list] = None,
        many: bool = False,
        order_by: Optional[list[ColumnElement]] = None,
    ) -> Union[T, list[T]]:
        pass

    @abstractmethod
    async def update(
        self,
        dbsession: AsyncSession,
        model: T,
        change: Optional[dict[str, Any]] = None,
        which: Optional[list] = None,
    ) -> bool:
        pass

    @abstractmethod
    async def delete(
        self, dbsession: AsyncSession, model: T, which: Optional[list]
    ) -> bool:
        pass


def db_session(f: Callable):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        async with sessionmanager.session() as dbsession:
            return await f(dbsession=dbsession, *args, **kwargs)

    return wrapper


class PromptsAppRepository(AppRepoInterface):
    @db_session
    async def create(self, instance: T, dbsession: AsyncSession) -> Optional[T]:
        try:
            dbsession.add(instance)
            await dbsession.commit()
            return instance

        except SQLAlchemyError:
            await dbsession.rollback()
            raise

    @db_session
    async def get(
        self,
        model: T,
        dbsession: AsyncSession,
        which: Optional[list] = None,
        many: bool = False,
        order_by: Optional[list[ColumnElement]] = None,
    ) -> Union[T, list[T]]:
        try:
            stmt: Select[T] = select(model)

            if which:
                stmt = stmt.where(*which)

            if order_by:
                stmt = stmt.order_by(*order_by)

            result = await dbsession.execute(stmt)
            return result.scalars().all() if many else result.scalars().first()

        except SQLAlchemyError:
            return None

    @db_session
    async def update(
        self,
        dbsession: AsyncSession,
        model: T,
        change: Optional[dict[str, Any]] = None,
        which: Optional[list] = None,
    ) -> Optional[T]:
        try:
            stmt: Update = update(model)
            if which:
                stmt = stmt.where(*which).values(**change)

            await dbsession.execute(stmt)
            await dbsession.commit()
            return await self.get(dbsession, model, which)

        except SQLAlchemyError:
            await dbsession.rollback()
            return None

    @db_session
    async def delete(
        self, model: T, dbsession: AsyncSession, which: Optional[list] = None
    ) -> bool:
        try:
            stmt = delete(model)
            if which:
                stmt = stmt.where(*which)

            await dbsession.execute(stmt)
            await dbsession.commit()
            return True

        except SQLAlchemyError:
            await dbsession.rollback()
            return False
