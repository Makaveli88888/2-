from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Header, HTTPException, status

from app.config import get_settings


def create_access_token(user_id: str, expires_minutes: int = 60) -> str:
    """Create a short-lived HS256 user token for trusted provisioning workflows."""
    settings = get_settings()
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET is required")
    if not user_id or len(user_id) > 128:
        raise ValueError("Invalid user_id")
    now = datetime.now(timezone.utc)
    payload = {"sub": user_id, "iat": now, "exp": now + timedelta(minutes=expires_minutes)}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def authenticated_user(authorization: str | None = Header(default=None)) -> str:
    settings = get_settings()
    if not settings.jwt_secret:
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    token = authorization[7:].strip()
    try:
        payload: dict[str, Any] = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not isinstance(user_id, str) or not user_id or len(user_id) > 128:
            raise jwt.InvalidTokenError("Invalid subject")
        return user_id
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc
