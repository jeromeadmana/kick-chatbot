from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.core.config import settings
from app.core.security import create_access_token, verify_access_token

router = APIRouter(prefix="/admin", tags=["admin"])
auth_scheme = HTTPBearer()

class AuthRequest(BaseModel):
    master_key: str

class AuthResponse(BaseModel):
    access_token: str

@router.post("/auth", response_model=AuthResponse)
async def admin_auth(request: AuthRequest):
    """Authenticate using master key and return JWT"""
    if request.master_key != settings.ADMIN_MASTER_KEY:
        raise HTTPException(status_code=401, detail="Invalid master key")
    token = create_access_token({"sub": "admin"})
    return AuthResponse(access_token=token)

@router.get("/protected")
async def protected_route(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """Example protected endpoint"""
    payload = verify_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"msg": "You are an admin", "payload": payload}
