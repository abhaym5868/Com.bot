"""
models/audit_log.py
-------------------
Audit log document model for MongoDB.
Tracks admin actions for the activity log page.
"""

from datetime import datetime
from typing import Any
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId, utc_now


class AuditLogModel(MongoBaseModel):
    """
    MongoDB representation of an admin action in the 'audit_logs' collection.
    """
    user_id: PyObjectId = Field(..., description="ID of the admin who performed the action")
    user_name: str = Field(..., description="Name of the admin (denormalized for display)")
    action: str = Field(..., description="Action type, e.g. 'created', 'published', 'deleted'")
    resource_type: str = Field(..., description="Resource type, e.g. 'changelog'")
    resource_id: str | None = Field(default=None, description="ID of the affected resource")
    resource_title: str | None = Field(default=None, description="Title/name of the resource for display")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Optional contextual metadata")
    timestamp: datetime = Field(default_factory=utc_now)
