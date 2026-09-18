"""
schemas/user.py
---------------
Pydantic schemas for User request validation and responses.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.enums import UserRole


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, description="Plaintext password for registration")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    last_viewed_changelog_date: datetime | None = None


class UserResponse(UserBase):
    id: str
    role: UserRole
    email_verified: bool
    last_viewed_changelog_date: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
