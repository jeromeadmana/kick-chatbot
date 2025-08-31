# tests/test_token.py
import jwt
from datetime import datetime, timedelta
from app.core.config import settings

def create_admin_token(secret: str, expires_seconds: int = 60):
    payload = {"exp": datetime.utcnow() + timedelta(seconds=expires_seconds), "role":"admin"}
    return jwt.encode(payload, secret, algorithm="HS256")

def test_admin_token_valid():
    tok = create_admin_token(settings.SECRET_KEY, expires_seconds=5)
    decoded = jwt.decode(tok, settings.SECRET_KEY, algorithms=["HS256"])
    assert decoded["role"] == "admin"
