import functools
from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session

from whats_app_utils.custem_logger import logger
from whats_app_utils.settings import get_postgres_config

POSTGRES_DB = get_postgres_config()

# Create a global engine – used in both get_db and get_async_session
engine = create_async_engine(
    POSTGRES_DB.connection_string,
    future=True,
    echo=True,
)

# Create a global async_session
async_session = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False,
)

# engine סינכרוני – עבור סלרי/קוד סינכרוני
sync_engine = create_engine(
    POSTGRES_DB.sync_connection_string,  # שימי לב!
    future=True,
    echo=False,
)

# Session רגיל
SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

def get_sync_session() -> Session:
    """
    Get a new SQLAlchemy session for use in synchronous code.
    Use inside a `with` statement.
    """
    return SyncSessionLocal()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    logger.debug("Connecting to the DB")
    async with async_session() as session:
        yield session


def get_async_session() -> AsyncSession:
    """
    Returns a session for use inside regular functions (e.g. Celery)
    Used outside of Depends
    """
    return async_session()

