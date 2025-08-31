# app/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MessageCreate(BaseModel):
    session_id: Optional[str] = None
    content: str

class MessageOut(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

class SessionOut(BaseModel):
    id: str
    created_at: datetime
    expires_at: Optional[datetime]
    is_demo: bool

    class Config:
        orm_mode = True

class ChatResponse(BaseModel):
    reply: str
    message: MessageOut
