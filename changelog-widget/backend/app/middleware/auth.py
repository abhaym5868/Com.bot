"""
middleware/auth.py
------------------
Authentication dependencies, JWT token extraction, cookie helpers,
CSRF double-submit protection, and Role-Based Access Control (RBAC) guards.
"""

import secrets
from bson import ObjectId
from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.settings import settings
from app.config.database import get_database
from app.models.enums import UserRole
from app.models.user import UserModel
from app.utils.jwt import decode_token

# Optional bearer schema so Swagger UI displays the "Authorize" button nicely
security_bearer = HTTPBearer(auto_error=False)


def generate_csrf_token() -> str:
    """Generate a cryptographically secure random token for CSRF protection."""
    return secrets.token_urlsafe(32)


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    csrf_token: str | None = None,
) -> str:
    """
    Set access_token and refresh_token as secure, httpOnly cookies,
    and csrf_token as a readable cookie for CSRF double-submit validation.
    """
    # Access token cookie (15 minutes)
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.access_token_expire_minutes * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )

    # Refresh token cookie (7 days)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )

    # CSRF cookie (readable by JavaScript to send via X-CSRF-Token header)
    token = csrf_token or generate_csrf_token()
    response.set_cookie(
        key="csrf_token",
        value=token,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        path="/",
    )
    return token


def clear_auth_cookies(response: Response) -> None:
    """Clear access, refresh, and csrf cookies upon logout."""
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )
    response.delete_cookie(
        key="csrf_token",
        path="/",
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
    )


def verify_csrf(request: Request) -> None:
    """
    Validate double-submit CSRF token for state-changing requests when
    authenticated via browser cookies.
    Exemptions:
    - Safe methods: GET, HEAD, OPTIONS
    - Direct API clients using Authorization: Bearer header
    - Unauthenticated requests where no access_token cookie is present
    """
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return

    # Direct Bearer tokens are exempt from CSRF (they cannot be forged via ambient browser cookies)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return

    # Public unauthenticated routes are exempt from CSRF
    public_paths = (
        "/api/v1/auth/login",
        "/api/v1/auth/signup",
        "/api/v1/auth/refresh",
        "/api/v1/auth/forgot-password",
        "/api/v1/auth/reset-password",
        "/api/v1/auth/verify-email",
        "/api/v1/analytics/view",
    )
    if any(request.url.path.startswith(p) for p in public_paths):
        return

    # Check if request has an authenticated session cookie
    if request.cookies.get("access_token"):
        csrf_cookie = request.cookies.get("csrf_token")
        csrf_header = request.headers.get("X-CSRF-Token") or request.headers.get("x-csrf-token")

        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token validation failed. Missing or mismatched X-CSRF-Token header.",
            )


def get_token_from_request(
    request: Request,
    bearer_creds: HTTPAuthorizationCredentials | None = None,
) -> str | None:
    """
    Extract access token:
    1. Checks Authorization: Bearer header (Swagger / Postman / Mobile)
    2. Falls back to httpOnly cookie `access_token` (Web Browser)
    """
    if bearer_creds and bearer_creds.credentials:
        return bearer_creds.credentials

    # Check Authorization header manually if not captured by HTTPBearer
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:].strip()

    # Check cookie
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    return None


async def get_current_user(
    request: Request,
    bearer_creds: HTTPAuthorizationCredentials | None = Depends(security_bearer),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> UserModel:
    """
    Dependency that authenticates the current user from cookie or bearer token.
    Raises HTTP 401 if unauthenticated or token is expired/invalid.
    """
    token = get_token_from_request(request, bearer_creds)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Missing token in cookie or Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: access token expected.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id or not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserModel(**doc)


async def get_current_admin_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """
    Dependency that enforces ADMIN role.
    Raises HTTP 403 Forbidden if current user is not an administrator.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin authorization required to perform this action.",
        )
    return current_user


async def get_optional_current_user(
    request: Request,
    bearer_creds: HTTPAuthorizationCredentials | None = Depends(security_bearer),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> UserModel | None:
    """
    Optional authentication: returns UserModel if a valid access token is provided,
    or None for public / unauthenticated visitors.
    """
    token = get_token_from_request(request, bearer_creds)
    if not token:
        return None

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        user_id = payload.get("sub")
        if not user_id or not ObjectId.is_valid(user_id):
            return None
        doc = await db["users"].find_one({"_id": ObjectId(user_id)})
        if not doc:
            return None
        return UserModel(**doc)
    except Exception:
        return None
