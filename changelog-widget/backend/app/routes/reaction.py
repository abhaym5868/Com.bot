"""
routes/reaction.py
------------------
API routes for reactions on changelog entries.
- POST /api/v1/reactions
- DELETE /api/v1/reactions/{id}
- GET /api/v1/reactions/changelog/{changelog_id}
"""

from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.middleware.auth import get_current_user, get_optional_current_user
from app.models.enums import UserRole
from app.models.user import UserModel
from app.schemas.auth import MessageResponse
from app.schemas.reaction import (
    ReactionCreate,
    ReactionResponse,
    ChangelogReactionsSummary,
)
from app.services import reaction_service

router = APIRouter()


@router.post(
    "",
    response_model=ReactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add reaction to changelog (Authenticated)",
    description="Allows authenticated users to react with ❤️, 🎉, or 🚀. Enforces uniqueness.",
)
async def create_reaction(
    data: ReactionCreate,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    return await reaction_service.add_reaction(db, current_user.id, data)


@router.delete(
    "/{id}",
    response_model=MessageResponse,
    summary="Remove reaction (Authenticated)",
    description="Allows a user to remove their previously placed reaction.",
)
async def delete_reaction(
    id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    is_admin = current_user.role == UserRole.ADMIN
    result = await reaction_service.remove_reaction(db, current_user.id, id, is_admin=is_admin)
    return MessageResponse(**result)


@router.get(
    "/changelog/{changelog_id}",
    response_model=ChangelogReactionsSummary,
    summary="Get reaction counts for a changelog",
    description="Returns counts for ❤️, 🎉, 🚀 and whether the current user reacted.",
)
async def get_reactions(
    changelog_id: str,
    current_user: UserModel | None = Depends(get_optional_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    user_id = current_user.id if current_user else None
    return await reaction_service.get_reactions_for_changelog(db, changelog_id, user_id)
