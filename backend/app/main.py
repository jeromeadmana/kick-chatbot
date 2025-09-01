# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings, CORS_ORIGIN_LIST
from app.core.db import create_db_tables
from app.routers import chat  # ensure routers imported via package
from app.core.rate_limiter import limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from fastapi import FastAPI
from app.api.routes import admin

app = FastAPI(title="Kick Chatbot - Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGIN_LIST or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter middleware
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# include routers
from app.routers import chat as chat_router
app.include_router(chat_router.router)
app.include_router(admin.router)

@app.on_event("startup")
async def startup():
    # Create DB tables for demo (use Alembic in production)
    await create_db_tables()
