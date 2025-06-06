import os

from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine
)

from dotenv import load_dotenv

load_dotenv()

from database.models import Base


db_url = os.getenv('DATABASE_URL')
if not db_url:
    raise RuntimeError('DATABASE_URL is missing in .env file')

engine = create_async_engine(db_url, echo=True)

session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_dp():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
