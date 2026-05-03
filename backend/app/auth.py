import os
import logging
from typing import Optional
from dataclasses import dataclass
from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db

logger = logging.getLogger(__name__)

AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"

@dataclass
class CurrentUser:
    id: str
    email: str
    display_name: str
    auth_provider: str

# Dev-mode default user
_DEV_USER = CurrentUser(
    id="dev-user-00000000",
    email="dev@networksim.local",
    display_name="Developer",
    auth_provider="local"
)

async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> CurrentUser:
    """FastAPI dependency: extract current user from JWT or return dev user."""
    if not AUTH_ENABLED:
        return _DEV_USER
    
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = auth_header[7:]  # Strip "Bearer "
    try:
        payload = _verify_jwt(token)
    except Exception as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return CurrentUser(
        id=payload.get("sub", ""),
        email=payload.get("email", ""),
        display_name=payload.get("name", "Unknown"),
        auth_provider=payload.get("iss", "unknown")
    )

def _verify_jwt(token: str) -> dict:
    """Decode and verify a JWT token."""
    try:
        from jose import jwt as jose_jwt
        JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
        JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        return jose_jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except ImportError:
        raise HTTPException(status_code=500, detail="Authentication subsystem unavailable: python-jose not installed")

def get_optional_user(
    request: Request,
) -> Optional[CurrentUser]:
    """FastAPI dependency: returns user if auth header present, None otherwise."""
    if not AUTH_ENABLED:
        return _DEV_USER
    
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    
    try:
        payload = _verify_jwt(auth_header[7:])
        return CurrentUser(
            id=payload.get("sub", ""),
            email=payload.get("email", ""),
            display_name=payload.get("name", "Unknown"),
            auth_provider=payload.get("iss", "unknown")
        )
    except Exception:
        return None
