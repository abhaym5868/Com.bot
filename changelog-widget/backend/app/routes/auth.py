"""
routes/auth.py
--------------
Authentication API endpoints: signup, login, token refresh, logout,
email verification simulation, forgot password, reset password, and user profile.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.settings import settings
from app.config.database import get_database
from app.middleware.auth import (
    clear_auth_cookies,
    get_current_admin_user,
    get_current_user,
    set_auth_cookies,
)
from app.models.user import UserModel
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    MessageResponse,
    RefreshTokenRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.schemas.user import UserResponse
from app.services import auth_service

router = APIRouter()


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Registers a new user, hashes password, generates email verification simulation token, and sets httpOnly auth cookies.",
)
async def signup(
    data: SignupRequest,
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user, verification_token = await auth_service.signup_user(db, data)

    # Automatically issue login tokens upon signup
    user, access_token, refresh_token = await auth_service.login_user(
        db, LoginRequest(email=data.email, password=data.password)
    )

    # Set httpOnly cookies
    set_auth_cookies(response, access_token, refresh_token)

    # Include verification token in header ONLY in development for simulation / testing
    if settings.environment.lower() == "development":
        response.headers["X-Email-Verification-Token"] = verification_token

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user.model_dump()),
    )


@router.post(
    "/verify-email",
    response_model=UserResponse,
    summary="Verify user email (simulation)",
    description="Validates the simulated verification token and marks user's email as verified.",
)
async def verify_email(
    data: VerifyEmailRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    verified_user = await auth_service.verify_email_token(db, data.token)
    return UserResponse.model_validate(verified_user.model_dump())


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive access + refresh tokens",
    description="Authenticates credentials, sets httpOnly cookies (15m access, 7d refresh), and returns user profile.",
)
async def login(
    data: LoginRequest,
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user, access_token, refresh_token = await auth_service.login_user(db, data)
    set_auth_cookies(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.model_validate(user.model_dump()),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token with token rotation",
    description="Reads refresh token from httpOnly cookie (or request body), revokes it, and issues a fresh token pair.",
)
async def refresh_token_endpoint(
    request: Request,
    response: Response,
    body: RefreshTokenRequest | None = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    # Check cookie first, then fallback to JSON body
    token_str = (body.refresh_token if body and body.refresh_token else None) or request.cookies.get("refresh_token")

    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing from cookie or request body.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user, new_access, new_refresh = await auth_service.refresh_tokens(db, token_str)
    set_auth_cookies(response, new_access, new_refresh)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        user=UserResponse.model_validate(user.model_dump()),
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Log out user",
    description="Revokes refresh token in database and clears httpOnly auth cookies.",
)
async def logout(
    request: Request,
    response: Response,
    body: RefreshTokenRequest | None = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    token_str = (body.refresh_token if body and body.refresh_token else None) or request.cookies.get("refresh_token")

    await auth_service.logout_user(db, token_str)
    clear_auth_cookies(response)

    return MessageResponse(message="Successfully logged out.")


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Request password reset (simulation)",
    description="Generates password reset token and logs simulated email. Returns simulation token for testing in dev.",
)
async def forgot_password(
    data: ForgotPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    token = await auth_service.request_password_reset(db, data.email)
    simulation_token = token if settings.environment.lower() == "development" else None
    return ForgotPasswordResponse(
        message="If this email is registered, password reset instructions have been dispatched.",
        simulation_token=simulation_token,
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password with token",
    description="Validates the reset token, updates password, and revokes all active user sessions.",
)
async def reset_password(
    data: ResetPasswordRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    await auth_service.reset_password(db, data.token, data.new_password)
    return MessageResponse(message="Password has been successfully reset. Please log in with your new password.")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
    description="Returns the profile of the authenticated user from access token in httpOnly cookie or Authorization header.",
)
async def get_me(
    current_user: UserModel = Depends(get_current_user),
):
    return UserResponse.model_validate(current_user.model_dump())


@router.get(
    "/admin-check",
    response_model=MessageResponse,
    summary="Verify admin authorization",
    description="Protected route that validates admin RBAC permission. Returns 403 Forbidden for non-admins.",
)
async def admin_check(
    admin_user: UserModel = Depends(get_current_admin_user),
):
    return MessageResponse(message=f"Welcome Admin {admin_user.name}! Authorization verified.")
