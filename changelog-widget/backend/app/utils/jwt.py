"""
utils/jwt.py
------------
JWT creation, encoding, and decoding using python-jose.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
import uuid
from jose import JWTError, jwt
from app.config.settings import settings


def generate_jti() -> str:
    """Generate a unique JWT ID for token tracking and rotation."""
    return str(uuid.uuid4())


def create_access_token(user_id: str, email: str, role: str) -> str:
    """Create a short-lived access token (default: 15 minutes)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str, jti: str | None = None) -> tuple[str, str, datetime]:
    """
    Create a long-lived refresh token (default: 7 days).
    Returns (token_string, jti, expires_at).
    """
    if not jti:
        jti = generate_jti()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": user_id,
        "jti": jti,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, jti, expire


def create_email_verification_token(user_id: str, email: str) -> str:
    """Create a token for email verification simulation (default: 24 hours)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=settings.email_verification_token_expire_hours)
    payload = {
        "sub": user_id,
        "email": email,
        "type": "email_verification",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_password_reset_token(user_id: str, email: str) -> str:
    """Create a short-lived token for password reset (default: 1 hour)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=settings.password_reset_token_expire_hours)
    payload = {
        "sub": user_id,
        "email": email,
        "type": "password_reset",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token against the app secret key.
    Raises JWTError if invalid or expired.
    """
    return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
