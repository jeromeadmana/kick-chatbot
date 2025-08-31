# app/core/db.py
import sqlalchemy.ext.asyncio as async_sa
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

DATABASE_URL = settings.DATABASE_URL

engine = async_sa.create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=async_sa.AsyncSession
)

Base = declarative_base()

# utility to create tables at startup (demo-only; use alembic for prod)
async def create_db_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
