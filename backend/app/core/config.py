# app/core/config.py
from pydantic import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    SECRET_KEY: str
    ADMIN_MASTER_KEY: str
    CORS_ORIGINS: str = "http://localhost:3000"
    REDIS_URL: Optional[str] = None
    DEMO_SESSION_TTL: int = 600  # seconds

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
# convenience: list of origins
CORS_ORIGIN_LIST = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
if settings.DATABASE_URL.startswith("postgres://"):
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif settings.DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in settings.DATABASE_URL:
    settings.DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
