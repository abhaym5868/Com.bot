"""
schemas/auth.py
---------------
Pydantic schemas for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from app.schemas.user import UserResponse
from app.utils.password import validate_password_complexity


class SignupRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Unique email address")
    password: str = Field(..., min_length=8, max_length=100, description="Password (at least 8 chars, mixed case, number, special char)")

    @field_validator("password")
    @classmethod
    def check_password_complexity(cls, v: str) -> str:
        validate_password_complexity(v)
        return v


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., description="Account password")


class RefreshTokenRequest(BaseModel):
    refresh_token: str | None = Field(
        default=None,
        description="Optional refresh token string if not sending via httpOnly cookie",
    )


class AuthResponse(BaseModel):
    user: UserResponse


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email associated with the account")


class ForgotPasswordResponse(BaseModel):
    message: str
    simulation_token: str | None = Field(
        default=None,
        description="Provided in development mode to test reset password without an actual email inbox",
    )


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Password reset token received via email simulation")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password (at least 8 chars)")

    @field_validator("new_password")
    @classmethod
    def check_password_complexity(cls, v: str) -> str:
        validate_password_complexity(v)
        return v


class VerifyEmailRequest(BaseModel):
    token: str = Field(..., description="Verification token received via email simulation")


class MessageResponse(BaseModel):
    message: str


class CsrfResponse(BaseModel):
    csrf_token: str
