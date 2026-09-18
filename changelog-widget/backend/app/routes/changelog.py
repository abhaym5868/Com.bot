"""
routes/changelog.py
-------------------
API endpoints for changelog management: CRUD, draft/publish actions,
filtering by category/status, pagination, and role-based visibility.
"""

from fastapi import APIRouter, Depends, Query, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.middleware.auth import get_current_admin_user, get_optional_current_user
from app.models.enums import ChangelogCategory, ChangelogStatus, UserRole
from app.models.user import UserModel
from app.schemas.auth import MessageResponse
from app.schemas.changelog import (
    ChangelogCreate,
    ChangelogResponse,
    ChangelogUpdate,
    FeedItem,
    FeedResponse,
    PaginatedChangelogResponse,
)
from app.services import changelog_service

router = APIRouter()


@router.post(
    "",
    response_model=ChangelogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create changelog update (Admin only)",
    description="Creates a new changelog update in DRAFT or PUBLISHED status. Auto-generates unique slug if not provided.",
)
async def create_changelog(
    data: ChangelogCreate,
    admin_user: UserModel = Depends(get_current_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    changelog = await changelog_service.create_changelog(db, admin_user.id, data)
    return ChangelogResponse.model_validate(changelog.model_dump())


@router.get(
    "",
    response_model=PaginatedChangelogResponse,
    summary="List changelog updates",
    description="Retrieves a paginated list of changelog updates sorted newest first. Public visitors strictly see PUBLISHED posts; admins can view drafts and filter by status.",
)
async def list_changelogs(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=10, ge=1, le=100, description="Items per page"),
    status: ChangelogStatus | None = Query(default=None, description="Filter by status (Admin only)"),
    category: ChangelogCategory | None = Query(default=None, description="Filter by category (NEW, IMPROVED, FIXED)"),
    search: str | None = Query(default=None, description="Search keyword in title or markdown"),
    current_user: UserModel | None = Depends(get_optional_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    is_admin = current_user is not None and current_user.role == UserRole.ADMIN
    return await changelog_service.list_changelogs(
        db=db,
        page=page,
        limit=limit,
        status_filter=status,
        category_filter=category,
        search=search,
        is_admin=is_admin,
    )


@router.get(
    "/feed",
    response_model=FeedResponse,
    summary="Public JSON feed of published changelog updates",
    description=(
        "Returns a reverse-chronological list of **published** changelog updates. "
        "No authentication required. Suitable for RSS-like integrations, embeds, or public SDKs. "
        "Responses are cached for 5 minutes via Cache-Control."
    ),
)
async def changelog_feed(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page (max 100)"),
    response: Response = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Public feed — no auth. Returns only PUBLISHED entries sorted newest-first.
    Sets Cache-Control: public, max-age=300 to let CDNs/browsers cache for 5 min.
    """
    result = await changelog_service.list_changelogs(
        db=db,
        page=page,
        limit=limit,
        status_filter=None,   # service auto-restricts to PUBLISHED for non-admins
        category_filter=None,
        search=None,
        is_admin=False,       # always treat as public visitor
    )

    # Set cache header so browsers/CDNs cache for 5 minutes
    response.headers["Cache-Control"] = "public, max-age=300"

    feed_items = [
        FeedItem(
            title=item.title,
            slug=item.slug,
            category=item.category,
            published_at=item.published_at,
            cover_image=item.cover_image,
        )
        for item in result.items
    ]

    return FeedResponse(
        updates=feed_items,
        total=result.total,
        page=result.page,
        limit=result.limit,
        pages=result.pages,
    )


@router.get(
    "/{slug}",
    response_model=ChangelogResponse,
    summary="Get single changelog update",
    description="Fetches a changelog update by unique slug or ObjectId. Public visitors cannot view drafts (returns 404).",
)
async def get_changelog(
    slug: str,
    current_user: UserModel | None = Depends(get_optional_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    is_admin = current_user is not None and current_user.role == UserRole.ADMIN
    changelog = await changelog_service.get_changelog_by_slug_or_id(db, slug, is_admin=is_admin)
    return ChangelogResponse.model_validate(changelog.model_dump())


@router.put(
    "/{id}",
    response_model=ChangelogResponse,
    summary="Update changelog post (Admin only)",
    description="Updates title, slug, content, category, cover image, status, or published_at for an existing changelog.",
)
async def update_changelog(
    id: str,
    data: ChangelogUpdate,
    admin_user: UserModel = Depends(get_current_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    updated = await changelog_service.update_changelog(db, id, data)
    return ChangelogResponse.model_validate(updated.model_dump())


@router.delete(
    "/{id}",
    response_model=MessageResponse,
    summary="Delete changelog post (Admin only)",
    description="Permanently deletes a changelog post and cleans up any reactions associated with it.",
)
async def delete_changelog(
    id: str,
    admin_user: UserModel = Depends(get_current_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    await changelog_service.delete_changelog(db, id)
    return MessageResponse(message="Changelog and associated reactions successfully deleted.")


@router.post(
    "/{id}/publish",
    response_model=ChangelogResponse,
    summary="Publish a draft changelog (Admin only)",
    description="Transitions a draft changelog post to PUBLISHED status and timestamps published_at.",
)
async def publish_changelog(
    id: str,
    admin_user: UserModel = Depends(get_current_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    published = await changelog_service.publish_changelog(db, id)
    return ChangelogResponse.model_validate(published.model_dump())
