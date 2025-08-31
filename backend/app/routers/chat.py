# app/routers/chat.py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException, status
from sqlalchemy import select
from app.core.db import AsyncSessionLocal
from app import models, schemas
from app.websocket_manager import ws_manager
from app.ai_client import AIClient
from app.core.config import settings
from app.core.rate_limiter import limiter
from slowapi.util import get_remote_address
from slowapi import _rate_limit_exceeded_handler
from fastapi import Request, BackgroundTasks
import uuid
import datetime
import asyncio

router = APIRouter(prefix="/api/chat", tags=["chat"])
ai = AIClient()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/session", response_model=schemas.SessionOut)
async def create_session(is_demo: bool = True, db=Depends(get_db)):
    """
    Creates a new session token. Demo sessions get a short TTL.
    """
    session_id = str(uuid.uuid4())
    expires_at = None
    if is_demo:
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.DEMO_SESSION_TTL)
    db_obj = models.Session(id=session_id, expires_at=expires_at, is_demo=is_demo)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.post("/message", response_model=schemas.ChatResponse)
@limiter.limit("10/minute")  # simple rate limit per IP
async def send_message(payload: schemas.MessageCreate, request: Request, background: BackgroundTasks, db=Depends(get_db)):
    """
    Accepts a message, saves it, asks the AI client for a reply, saves the reply,
    and returns it. Also broadcasts via WebSocket manager if clients are connected.
    """
    # Basic session create-if-missing
    session_id = payload.session_id
    if not session_id:
        session_id = str(uuid.uuid4())
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.DEMO_SESSION_TTL)
        db.add(models.Session(id=session_id, expires_at=expires_at, is_demo=True))
        await db.commit()

    # save user message
    msg = models.Message(session_id=session_id, role="user", content=payload.content)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    # fetch previous messages if you want context (simple approach: last N messages)
    q = select(models.Message).where(models.Message.session_id == session_id).order_by(models.Message.created_at)
    res = await db.execute(q)
    messages = res.scalars().all()
    # Convert to simple list of dicts for AI client
    ai_messages = [{"role": m.role, "content": m.content} for m in messages]

    # call AI (in background to keep request snappy if needed)
    reply_text = await ai.generate(ai_messages)

    # save assistant message
    assist = models.Message(session_id=session_id, role="assistant", content=reply_text)
    db.add(assist)
    await db.commit()
    await db.refresh(assist)

    # broadcast via websocket (best-effort)
    await ws_manager.broadcast(session_id, reply_text)

    return schemas.ChatResponse(reply=reply_text, message=assist)

@router.websocket("/ws/{session_id}")
async def ws_chat(websocket: WebSocket, session_id: str):
    """
    Websocket endpoint for real-time chat updates.
    """
    await ws_manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Expect {"type":"user","content":"..."} from frontend
            if data.get("type") == "user" and "content" in data:
                # For safety, do a minimal check and then call AI
                user_text = data["content"]
                # We keep this simple: call AI inline and broadcast the reply.
                # For production: push to a queue / background worker.
                # Save to DB omitted here for brevity (but recommended).
                reply = await ai.generate([{"role":"user","content":user_text}])
                await ws_manager.broadcast(session_id, reply)
    except WebSocketDisconnect:
        await ws_manager.disconnect(session_id, websocket)
    except Exception:
        await ws_manager.disconnect(session_id, websocket)
        raise
