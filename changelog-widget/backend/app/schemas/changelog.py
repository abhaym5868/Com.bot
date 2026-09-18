"""
schemas/changelog.py
--------------------
Pydantic schemas for Changelog request validation, responses, and pagination.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.enums import ChangelogCategory, ChangelogStatus


class ChangelogBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="Changelog post title")
    content_markdown: str = Field(..., min_length=1, description="Markdown content body")
    category: ChangelogCategory = Field(..., description="NEW, IMPROVED, or FIXED")
    cover_image: str | None = Field(default=None, description="Optional cover image URL")
    status: ChangelogStatus = Field(default=ChangelogStatus.DRAFT, description="DRAFT or PUBLISHED")
    published_at: datetime | None = Field(default=None, description="Publication timestamp")

    @field_validator("cover_image")
    @classmethod
    def validate_cover_image(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        clean = v.strip()
        if not (clean.startswith("http://") or clean.startswith("https://") or clean.startswith("/")):
            raise ValueError("cover_image must be a valid HTTP/HTTPS URL or relative path starting with '/'")
        return clean


class ChangelogCreate(ChangelogBase):
    slug: str | None = Field(
        default=None,
        min_length=3,
        max_length=200,
        description="Optional custom slug. If omitted, will be auto-generated from title.",
    )


class ChangelogUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    slug: str | None = Field(default=None, min_length=3, max_length=200)
    content_markdown: str | None = None
    category: ChangelogCategory | None = None
    cover_image: str | None = None
    status: ChangelogStatus | None = None
    published_at: datetime | None = None

    @field_validator("cover_image")
    @classmethod
    def validate_cover_image(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        clean = v.strip()
        if not (clean.startswith("http://") or clean.startswith("https://") or clean.startswith("/")):
            raise ValueError("cover_image must be a valid HTTP/HTTPS URL or relative path starting with '/'")
        return clean


class ChangelogResponse(ChangelogBase):
    id: str
    slug: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedChangelogResponse(BaseModel):
    items: list[ChangelogResponse]
    total: int
    page: int
    limit: int
    pages: int


class FeedItem(BaseModel):
    """Slim read model used by the public JSON feed."""

    title: str
    slug: str
    category: ChangelogCategory
    published_at: datetime
    cover_image: str | None = None

    model_config = ConfigDict(from_attributes=True)


class FeedResponse(BaseModel):
    """Paginated wrapper returned by GET /changelog/feed."""

    updates: list[FeedItem]
    total: int
    page: int
    limit: int
    pages: int
