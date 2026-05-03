"""Centralized FastAPI dependency injection."""
from app.db import get_db
from app.auth import get_current_user, get_optional_user, CurrentUser

__all__ = ["get_db", "get_current_user", "get_optional_user", "CurrentUser"]
