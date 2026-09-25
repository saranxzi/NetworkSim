import os
import logging
from dataclasses import dataclass
from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)

AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"

@dataclass(slots=True)
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

def _payload_to_user(payload: dict) -> CurrentUser:
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
        jwt_secret = os.getenv("JWT_SECRET", "dev-secret-change-me")
        jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        return jose_jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
    except ImportError:
        raise HTTPException(status_code=500, detail="Authentication subsystem unavailable: python-jose not installed")

def get_current_user(request: Request) -> CurrentUser:
    """FastAPI dependency: extract current user from JWT or return dev user."""
    if not AUTH_ENABLED:
        return _DEV_USER
    
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    token = auth_header.removeprefix("Bearer ")
    try:
        payload = _verify_jwt(token)
    except Exception as e:
        logger.warning(f"JWT verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return _payload_to_user(payload)

def get_optional_user(request: Request) -> CurrentUser | None:
    """FastAPI dependency: returns user if auth header present, None otherwise."""
    if not AUTH_ENABLED:
        return _DEV_USER
    
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    
    try:
        payload = _verify_jwt(auth_header.removeprefix("Bearer "))
        return _payload_to_user(payload)
    except Exception:
        return None
