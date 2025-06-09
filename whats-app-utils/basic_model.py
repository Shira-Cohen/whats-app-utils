from sqlalchemy import Integer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from asyncpg import UniqueViolationError
from sqlalchemy.orm import mapped_column, Mapped

import uuid
from sqlalchemy.dialects.postgresql import UUID

from utils.custem_logger import logger


class BasicModel(DeclarativeBase):
    __abstract__ = True
    # id: Mapped[uuid.UUID] = mapped_column(
    #     UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # TODO: check if we need to change the datatype of the ID in the postgres to string

    async def save(self, db_session: AsyncSession):
        """

        :param db_session:
        :return:
        """
        try:
            db_session.add(self)
            return await db_session.commit()
        except (SQLAlchemyError, UniqueViolationError) as e:
            logger.exception(f"Failed to save in DB, ERROR={e}")
            return None

    async def delete(self, db_session: AsyncSession):
        """

        :param db_session:
        :return:
        """
        try:
            await db_session.delete(self)
            await db_session.commit()
            return True
        except SQLAlchemyError as e:
            logger.exception(f"Failed to delete from DB, ERROR={e}")
            return False

    async def update(self, db: AsyncSession, **kwargs):
        """

        :param db:
        :param kwargs
        :return:
        """
        try:
            for k, v in kwargs.items():
                setattr(self, k, v)
            return await db.commit()
        except SQLAlchemyError as e:
            logger.exception(f"Failed to update in DB, ERROR={e}")
            return None

    async def save_or_update(self, db: AsyncSession):
        try:
            return await db.merge(self)
        except SQLAlchemyError as e:
            logger.exception(f"Failed to update or save in DB, ERROR={e}")
            return None

    @staticmethod
    async def exec_stmt(_stmt, db: AsyncSession):
        _result = await db.execute(_stmt)
        return _result.scalars().first()
