"""
models/changelog.py
-------------------
Changelog document model for MongoDB.
"""

from datetime import datetime
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId, utc_now
from app.models.enums import ChangelogCategory, ChangelogStatus


class ChangelogModel(MongoBaseModel):
    """
    MongoDB representation of a Changelog in the 'changelogs' collection.
    """
    title: str = Field(..., min_length=3, max_length=200, description="Changelog post title")
    slug: str = Field(..., min_length=3, max_length=200, description="URL-friendly unique slug")
    content_markdown: str = Field(..., description="Markdown content of the release notes")
    category: ChangelogCategory = Field(..., description="Category: NEW, IMPROVED, or FIXED")
    cover_image: str | None = Field(default=None, description="Optional URL or path to cover image")
    published_at: datetime | None = Field(default=None, description="Release publication timestamp")
    status: ChangelogStatus = Field(default=ChangelogStatus.DRAFT, description="Status: DRAFT or PUBLISHED")
    created_by: PyObjectId = Field(..., description="User ID of the admin author")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
