from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from settings import Settings

# dialect+driver://username:password@host:port/database
DATABASE_URL = f'postgresql+asyncpg://{Settings.DATABASE_USER}:{Settings.DATABASE_PASSWORD}@' \
               f'{Settings.DATABASE_HOST}:{Settings.DATABASE_PORT}/{Settings.DATABASE_NAME}'

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
