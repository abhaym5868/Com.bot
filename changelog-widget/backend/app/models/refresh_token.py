"""
models/refresh_token.py
-----------------------
MongoDB model for storing and tracking refresh token sessions for rotation.
"""

from datetime import datetime
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId, utc_now


class RefreshTokenModel(MongoBaseModel):
    """
    Tracks active refresh tokens to enforce rotation and token revocation.
    """
    user_id: PyObjectId = Field(..., description="User who owns this session")
    jti: str = Field(..., description="Unique JWT ID claim")
    expires_at: datetime = Field(..., description="Token expiry timestamp")
    revoked: bool = Field(default=False, description="Whether this session has been revoked")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
