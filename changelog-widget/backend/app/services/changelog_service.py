"""
services/changelog_service.py
------------------------------
Business logic for changelog CRUD, draft/scheduled publishing, pagination,
filtering, pinning, and duplicate slug handling.
"""

import re
import math
import logging
from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.base import utc_now
from app.models.changelog import ChangelogModel
from app.models.enums import ChangelogCategory, ChangelogStatus
from app.schemas.changelog import (
    ChangelogCreate,
    ChangelogResponse,
    ChangelogUpdate,
    PaginatedChangelogResponse,
)
from app.utils.slug import generate_unique_slug

logger = logging.getLogger(__name__)


async def create_changelog(
    db: AsyncIOMotorDatabase,
    admin_id: str,
    data: ChangelogCreate,
) -> ChangelogModel:
    """Create a new changelog post (draft, scheduled, or published)."""
    # Generate unique slug
    raw_slug = data.slug.strip() if data.slug else data.title
    unique_slug = await generate_unique_slug(db, raw_slug)

    # Set publication timestamp if published
    published_at = data.published_at
    if data.status == ChangelogStatus.PUBLISHED and not published_at:
        published_at = utc_now()

    changelog = ChangelogModel(
        title=data.title.strip(),
        slug=unique_slug,
        content_markdown=data.content_markdown,
        category=data.category,
        cover_image=data.cover_image,
        status=data.status,
        published_at=published_at,
        version=data.version,
        is_pinned=data.is_pinned,
        scheduled_for=data.scheduled_for,
        created_by=admin_id,
        created_at=utc_now(),
        updated_at=utc_now(),
    )

    mongo_doc = changelog.to_mongo()
    result = await db["changelogs"].insert_one(mongo_doc)
    changelog.id = str(result.inserted_id)
    logger.info(
        "Changelog created: %s (id: %s, status: %s)",
        changelog.slug, changelog.id, changelog.status,
    )
    return changelog


async def get_changelog_by_slug_or_id(
    db: AsyncIOMotorDatabase,
    identifier: str,
    is_admin: bool = False,
) -> ChangelogModel:
    """
    Fetch a single changelog by slug or ObjectId.
    Public/regular users can only view PUBLISHED posts (returns 404 for drafts/scheduled).
    """
    query: dict = {"$or": [{"slug": identifier}]}
    if ObjectId.is_valid(identifier):
        query["$or"].append({"_id": ObjectId(identifier)})

    doc = await db["changelogs"].find_one(query)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Changelog not found.",
        )

    # Enforce draft/scheduled visibility — only admins see non-published
    if doc.get("status") != ChangelogStatus.PUBLISHED.value and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Changelog not found.",
        )

    return ChangelogModel(**doc)


async def list_changelogs(
    db: AsyncIOMotorDatabase,
    page: int = 1,
    limit: int = 10,
    status_filter: ChangelogStatus | None = None,
    category_filter: ChangelogCategory | None = None,
    search: str | None = None,
    is_admin: bool = False,
) -> PaginatedChangelogResponse:
    """
    List changelog updates with pagination, filtering, and sorting.
    Public users ONLY see PUBLISHED updates.
    Pinned published updates float to the top.
    """
    query: dict = {}

    # Visibility rules
    if not is_admin:
        # Public users see only published posts
        query["status"] = ChangelogStatus.PUBLISHED.value
    elif status_filter:
        query["status"] = status_filter.value

    if category_filter:
        query["category"] = category_filter.value

    if search and search.strip():
        search_regex = {"$regex": re.escape(search.strip()), "$options": "i"}
        query["$or"] = [
            {"title": search_regex},
            {"content_markdown": search_regex},
            {"slug": search_regex},
            {"version": search_regex},
        ]

    total = await db["changelogs"].count_documents(query)
    skip = (page - 1) * limit
    total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1

    # Sort: pinned first (desc), then published_at DESC, then created_at DESC
    cursor = (
        db["changelogs"]
        .find(query)
        .sort([("is_pinned", -1), ("published_at", -1), ("created_at", -1)])
        .skip(skip)
        .limit(limit)
    )

    items: list[ChangelogResponse] = []
    async for doc in cursor:
        model = ChangelogModel(**doc)
        items.append(ChangelogResponse.model_validate(model.model_dump()))

    return PaginatedChangelogResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=total_pages,
    )


async def update_changelog(
    db: AsyncIOMotorDatabase,
    changelog_id: str,
    data: ChangelogUpdate,
) -> ChangelogModel:
    """Update an existing changelog post (Admin only)."""
    if not ObjectId.is_valid(changelog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid changelog ID.",
        )

    existing = await db["changelogs"].find_one({"_id": ObjectId(changelog_id)})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Changelog not found.",
        )

    updates: dict = {"updated_at": utc_now()}

    if data.title is not None:
        updates["title"] = data.title.strip()

    if data.slug is not None and data.slug.strip():
        unique_slug = await generate_unique_slug(db, data.slug.strip(), exclude_id=changelog_id)
        updates["slug"] = unique_slug
    elif data.title is not None and not existing.get("slug"):
        updates["slug"] = await generate_unique_slug(db, data.title, exclude_id=changelog_id)

    if data.content_markdown is not None:
        updates["content_markdown"] = data.content_markdown

    if data.category is not None:
        updates["category"] = data.category.value

    if data.cover_image is not None:
        updates["cover_image"] = data.cover_image

    if data.published_at is not None:
        updates["published_at"] = data.published_at

    if data.version is not None:
        updates["version"] = data.version if data.version.strip() else None

    if data.is_pinned is not None:
        updates["is_pinned"] = data.is_pinned

    if data.scheduled_for is not None:
        updates["scheduled_for"] = data.scheduled_for

    if data.status is not None:
        updates["status"] = data.status.value
        # If changing to PUBLISHED and no published_at timestamp exists, assign now
        if (
            data.status == ChangelogStatus.PUBLISHED
            and not existing.get("published_at")
            and not data.published_at
        ):
            updates["published_at"] = utc_now()
        # If changing to SCHEDULED, clear published_at unless explicitly set
        elif data.status == ChangelogStatus.SCHEDULED and not data.published_at:
            updates["published_at"] = None

    await db["changelogs"].update_one(
        {"_id": ObjectId(changelog_id)},
        {"$set": updates},
    )

    updated_doc = await db["changelogs"].find_one({"_id": ObjectId(changelog_id)})
    return ChangelogModel(**updated_doc)


async def delete_changelog(
    db: AsyncIOMotorDatabase,
    changelog_id: str,
) -> None:
    """Delete changelog post and cleanup associated reactions/views (Admin only)."""
    if not ObjectId.is_valid(changelog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid changelog ID.",
        )

    result = await db["changelogs"].delete_one({"_id": ObjectId(changelog_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Changelog not found.",
        )

    # Cleanup associated reactions and views
    await db["reactions"].delete_many({"changelog_id": ObjectId(changelog_id)})
    await db["views"].delete_many({"changelog_id": ObjectId(changelog_id)})
    logger.info("Changelog %s deleted along with associated reactions/views.", changelog_id)


async def publish_changelog(
    db: AsyncIOMotorDatabase,
    changelog_id: str,
) -> ChangelogModel:
    """Publish a draft/scheduled changelog and assign published_at timestamp."""
    if not ObjectId.is_valid(changelog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid changelog ID.",
        )

    existing = await db["changelogs"].find_one({"_id": ObjectId(changelog_id)})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Changelog not found.",
        )

    published_at = existing.get("published_at") or utc_now()

    await db["changelogs"].update_one(
        {"_id": ObjectId(changelog_id)},
        {
            "$set": {
                "status": ChangelogStatus.PUBLISHED.value,
                "published_at": published_at,
                "updated_at": utc_now(),
            }
        },
    )

    updated_doc = await db["changelogs"].find_one({"_id": ObjectId(changelog_id)})
    return ChangelogModel(**updated_doc)


async def pin_changelog(
    db: AsyncIOMotorDatabase,
    changelog_id: str,
) -> ChangelogModel:
    """Pin a published changelog update."""
    if not ObjectId.is_valid(changelog_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid changelog ID.")

    existing = await db["changelogs"].find_one({"_id": ObjectId(changelog_id)})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Changelog not found.")

    if existing.get("status") != ChangelogStatus.PUBLISHED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only published updates can be pinned.",
        )

    await db["changelogs"].update_one(
        {"_id": ObjectId(changelog_id)},
        {"$set": {"is_pinned": True, "updated_at": utc_now()}},
    )
    updated_doc = await db["changelogs"].find_one({"_id": ObjectId(changelog_id)})
    return ChangelogModel(**updated_doc)


async def unpin_changelog(
    db: AsyncIOMotorDatabase,
    changelog_id: str,
) -> ChangelogModel:
    """Unpin a changelog update."""
    if not ObjectId.is_valid(changelog_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid changelog ID.")

    existing = await db["changelogs"].find_one({"_id": ObjectId(changelog_id)})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Changelog not found.")

    await db["changelogs"].update_one(
        {"_id": ObjectId(changelog_id)},
        {"$set": {"is_pinned": False, "updated_at": utc_now()}},
    )
    updated_doc = await db["changelogs"].find_one({"_id": ObjectId(changelog_id)})
    return ChangelogModel(**updated_doc)


async def auto_publish_scheduled(db: AsyncIOMotorDatabase) -> int:
    """
    Called by the background scheduler.
    Finds all SCHEDULED changelogs whose scheduled_for <= now and publishes them.
    Returns the count of items published.
    """
    now = utc_now()
    result = await db["changelogs"].update_many(
        {
            "status": ChangelogStatus.SCHEDULED.value,
            "scheduled_for": {"$lte": now},
        },
        {
            "$set": {
                "status": ChangelogStatus.PUBLISHED.value,
                "published_at": now,
                "updated_at": now,
            }
        },
    )
    if result.modified_count > 0:
        logger.info("Auto-published %d scheduled changelog(s).", result.modified_count)
    return result.modified_count
