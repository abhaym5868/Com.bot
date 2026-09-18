"""
models/user.py
--------------
User document model for MongoDB.
"""

from datetime import datetime
from pydantic import EmailStr, Field
from app.models.base import MongoBaseModel, PyObjectId, utc_now
from app.models.enums import UserRole


class UserModel(MongoBaseModel):
    """
    MongoDB representation of a User in the 'users' collection.
    """
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    email: EmailStr = Field(..., description="Unique email address")
    password_hash: str = Field(..., description="Bcrypt hashed password")
    role: UserRole = Field(default=UserRole.USER, description="User role (user or admin)")
    email_verified: bool = Field(default=False, description="Email verification status")
    last_viewed_changelog_date: datetime | None = Field(
        default=None,
        description="Timestamp when user last checked changelogs (used for unread badges)"
    )
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
