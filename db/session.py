from typing import AsyncGenerator
import redis.asyncio
import redis
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from db.models import User
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME, REDIS_HOST, REDIS_PASS, REDIS_PORT

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

redis_session = redis.asyncio.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS, decode_responses=True)

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_redis_async_session() -> AsyncGenerator[redis.Redis, None]:
    async with redis.asyncio.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASS,
                                         decode_responses=True) as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
