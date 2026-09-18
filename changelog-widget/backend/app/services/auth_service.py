"""
services/auth_service.py
------------------------
Business logic for authentication: signup, login, JWT token rotation,
email verification simulation, and password reset.
"""

import logging
from bson import ObjectId
from fastapi import HTTPException, status
from jose import JWTError
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.settings import settings
from app.models.enums import UserRole
from app.models.user import UserModel
from app.models.refresh_token import RefreshTokenModel
from app.models.base import utc_now
from app.schemas.auth import SignupRequest, LoginRequest
from app.utils.password import hash_password, verify_password
from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    create_email_verification_token,
    create_password_reset_token,
    decode_token,
)

logger = logging.getLogger(__name__)


async def signup_user(
    db: AsyncIOMotorDatabase,
    data: SignupRequest,
) -> tuple[UserModel, str]:
    """
    Register a new user.
    Simulates email verification and securely assigns ADMIN role.
    """
    email_clean = data.email.strip().lower()

    # Check for existing email
    existing = await db["users"].find_one({"email": email_clean})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Secure role assignment:
    # 1. Very first user registered in system bootstraps as ADMIN
    # 2. Configured admin email whitelist from settings.admin_emails
    # 3. In development mode only, admin@ / @admin.com pattern allows easy test setups
    # 4. In production, arbitrary users CANNOT escalate privileges by picking an email pattern!
    user_count = await db["users"].count_documents({})
    admin_emails = settings.get_admin_emails()

    if user_count == 0:
        role = UserRole.ADMIN
    elif email_clean in admin_emails:
        role = UserRole.ADMIN
    elif settings.environment.lower() == "development" and (
        email_clean.startswith("admin@") or email_clean.endswith("@admin.com")
    ):
        role = UserRole.ADMIN
    else:
        role = UserRole.USER

    hashed_pw = hash_password(data.password)

    user = UserModel(
        name=data.name.strip(),
        email=email_clean,
        password_hash=hashed_pw,
        role=role,
        email_verified=False,
    )

    mongo_doc = user.to_mongo()
    insert_result = await db["users"].insert_one(mongo_doc)
    user.id = str(insert_result.inserted_id)

    # Generate email verification token (simulation)
    verification_token = create_email_verification_token(user.id, user.email)
    logger.info(
        "📧 [SIMULATION] Email verification sent to %s | Token: %s",
        user.email,
        verification_token,
    )

    return user, verification_token


async def verify_email_token(
    db: AsyncIOMotorDatabase,
    token: str,
) -> UserModel:
    """Verify user's email using verification token."""
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired email verification token.",
        )

    if payload.get("type") != "email_verification":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type.",
        )

    user_id = payload.get("sub")
    if not user_id or not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed token payload.",
        )

    doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if not doc.get("email_verified", False):
        await db["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"email_verified": True, "updated_at": utc_now()}},
        )
        doc["email_verified"] = True

    return UserModel(**doc)


async def login_user(
    db: AsyncIOMotorDatabase,
    data: LoginRequest,
) -> tuple[UserModel, str, str]:
    """
    Authenticate user credentials and issue access + refresh tokens.
    Saves session in refresh_tokens collection for rotation.
    """
    email_clean = data.email.strip().lower()
    doc = await db["users"].find_one({"email": email_clean})

    if not doc or not verify_password(data.password, doc.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserModel(**doc)

    # Generate tokens
    access_token = create_access_token(user.id, user.email, user.role.value)
    refresh_token, jti, expire = create_refresh_token(user.id)

    # Save session for token rotation tracking
    session = RefreshTokenModel(
        user_id=user.id,
        jti=jti,
        expires_at=expire,
        revoked=False,
    )
    await db["refresh_tokens"].insert_one(session.to_mongo())

    return user, access_token, refresh_token


async def refresh_tokens(
    db: AsyncIOMotorDatabase,
    token_str: str,
) -> tuple[UserModel, str, str]:
    """
    Perform Refresh Token Rotation:
    1. Validate refresh token & ensure JTI exists and is not revoked.
    2. Invalidate previous refresh token.
    3. Issue new access token + new refresh token pair.
    """
    try:
        payload = decode_token(token_str)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    jti = payload.get("jti")

    if not user_id or not jti or not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Find the session in DB
    session = await db["refresh_tokens"].find_one({"user_id": ObjectId(user_id), "jti": jti})

    if not session or session.get("revoked", False):
        # Possible token reuse attack — revoke all user sessions as a precaution
        await db["refresh_tokens"].update_many(
            {"user_id": ObjectId(user_id)},
            {"$set": {"revoked": True, "updated_at": utc_now()}},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Revoked or invalid refresh token. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Invalidate (revoke) old token
    await db["refresh_tokens"].update_one(
        {"_id": session["_id"]},
        {"$set": {"revoked": True, "updated_at": utc_now()}},
    )

    # Fetch user
    user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
        )

    user = UserModel(**user_doc)

    # Generate fresh token pair
    new_access_token = create_access_token(user.id, user.email, user.role.value)
    new_refresh_token, new_jti, new_expire = create_refresh_token(user.id)

    # Record new session
    new_session = RefreshTokenModel(
        user_id=user.id,
        jti=new_jti,
        expires_at=new_expire,
        revoked=False,
    )
    await db["refresh_tokens"].insert_one(new_session.to_mongo())

    return user, new_access_token, new_refresh_token


async def logout_user(
    db: AsyncIOMotorDatabase,
    token_str: str | None,
) -> None:
    """Revoke refresh session in database."""
    if not token_str:
        return

    try:
        payload = decode_token(token_str)
        jti = payload.get("jti")
        user_id = payload.get("sub")
        if jti and user_id and ObjectId.is_valid(user_id):
            await db["refresh_tokens"].update_one(
                {"user_id": ObjectId(user_id), "jti": jti},
                {"$set": {"revoked": True, "updated_at": utc_now()}},
            )
    except Exception:
        # Logout should not fail if token is expired or malformed
        pass


async def request_password_reset(
    db: AsyncIOMotorDatabase,
    email: str,
) -> str | None:
    """
    Generate password reset token and simulate sending an email.
    Returns token in dev mode for testing.
    """
    email_clean = email.strip().lower()
    doc = await db["users"].find_one({"email": email_clean})
    if not doc:
        # Don't leak whether email exists
        return None

    user = UserModel(**doc)
    reset_token = create_password_reset_token(user.id, user.email)
    logger.info(
        "🔑 [SIMULATION] Password reset requested for %s | Reset Token: %s",
        user.email,
        reset_token,
    )
    return reset_token


async def reset_password(
    db: AsyncIOMotorDatabase,
    token: str,
    new_password: str,
) -> None:
    """Reset user password and invalidate all existing refresh sessions."""
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    if payload.get("type") != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type.",
        )

    user_id = payload.get("sub")
    if not user_id or not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed token payload.",
        )

    user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    new_hash = hash_password(new_password)

    # Update password
    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password_hash": new_hash, "updated_at": utc_now()}},
    )

    # Invalidate all existing sessions for security
    await db["refresh_tokens"].update_many(
        {"user_id": ObjectId(user_id)},
        {"$set": {"revoked": True, "updated_at": utc_now()}},
    )
    logger.info("Password successfully reset for user %s. Sessions revoked.", user_id)
