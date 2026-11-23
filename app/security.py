from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Header, HTTPException, status

from app.config import get_settings


def _secret() -> str:
    secret = get_settings().jwt_secret
    if len(secret) < 32:
        raise RuntimeError("JWT_SECRET must contain at least 32 characters")
    return secret


def create_access_token(user_id: str, expires_minutes: int = 60) -> str:
    """Create a short-lived HS256 user token for trusted provisioning workflows."""
    if not user_id or len(user_id) > 128:
        raise ValueError("Invalid user_id")
    if not 1 <= expires_minutes <= 1440:
        raise ValueError("expires_minutes must be between 1 and 1440")
    now = datetime.now(timezone.utc)
    payload = {"sub": user_id, "iat": now, "exp": now + timedelta(minutes=expires_minutes)}
    return jwt.encode(payload, _secret(), algorithm="HS256")


def authenticated_user(authorization: str | None = Header(default=None)) -> str:
    try:
        secret = _secret()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Authentication is not configured") from exc
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    token = authorization[7:].strip()
    try:
        payload: dict[str, Any] = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not isinstance(user_id, str) or not user_id or len(user_id) > 128:
            raise jwt.InvalidTokenError("Invalid subject")
        return user_id
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc
