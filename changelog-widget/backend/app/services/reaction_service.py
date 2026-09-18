"""
services/reaction_service.py
----------------------------
Business logic for adding, removing, and summarizing changelog reactions.
Enforces unique constraints and authenticated ownership.
"""

import logging
from bson import ObjectId
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.models.base import utc_now
from app.models.enums import ChangelogStatus
from app.schemas.reaction import (
    ALLOWED_REACTIONS,
    ReactionCreate,
    ReactionResponse,
    ReactionItemSummary,
    ChangelogReactionsSummary,
)

logger = logging.getLogger(__name__)


async def add_reaction(
    db: AsyncIOMotorDatabase,
    user_id: str,
    data: ReactionCreate,
) -> ReactionResponse:
    """
    Adds a user reaction (❤️, 🎉, 🚀) to a published changelog post.
    Enforces unique constraint so a user cannot duplicate the same reaction on the same changelog.
    """
    if data.reaction not in ALLOWED_REACTIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT") else 422,
            detail=f"Invalid reaction. Allowed reactions are: {', '.join(ALLOWED_REACTIONS)}",
        )

    if not ObjectId.is_valid(data.changelog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid changelog ID format.",
        )

    # Verify changelog exists and is published (or exists)
    changelog = await db["changelogs"].find_one({"_id": ObjectId(data.changelog_id)})
    if not changelog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Changelog not found.",
        )

    doc = {
        "user_id": ObjectId(user_id),
        "changelog_id": ObjectId(data.changelog_id),
        "reaction": data.reaction,
        "created_at": utc_now(),
    }

    try:
        result = await db["reactions"].insert_one(doc)
        doc["_id"] = result.inserted_id
        return ReactionResponse(
            id=str(doc["_id"]),
            user_id=str(doc["user_id"]),
            changelog_id=str(doc["changelog_id"]),
            reaction=doc["reaction"],
            created_at=doc["created_at"],
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reacted with this emoji to this changelog.",
        )


async def remove_reaction(
    db: AsyncIOMotorDatabase,
    user_id: str,
    reaction_id: str,
    is_admin: bool = False,
) -> dict:
    """
    Removes a reaction. Only the reacting user (or an admin) can delete it.
    """
    if not ObjectId.is_valid(reaction_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reaction ID format.",
        )

    doc = await db["reactions"].find_one({"_id": ObjectId(reaction_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found.",
        )

    # Verify ownership
    if str(doc["user_id"]) != user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to remove this reaction.",
        )

    await db["reactions"].delete_one({"_id": ObjectId(reaction_id)})
    return {"message": "Reaction removed successfully."}


async def get_reactions_for_changelog(
    db: AsyncIOMotorDatabase,
    changelog_id: str,
    user_id: str | None = None,
) -> ChangelogReactionsSummary:
    """
    Retrieves reaction counts for ❤️, 🎉, 🚀 and indicates whether the
    current user has reacted, along with their reaction ID for easy deletion.
    """
    if not ObjectId.is_valid(changelog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid changelog ID format.",
        )

    target_oid = ObjectId(changelog_id)

    # Count for each allowed reaction
    reactions_list: list[ReactionItemSummary] = []

    # Find user's reactions if authenticated
    user_reactions_map: dict[str, str] = {}
    if user_id and ObjectId.is_valid(user_id):
        user_docs = db["reactions"].find(
            {"changelog_id": target_oid, "user_id": ObjectId(user_id)}
        )
        async for rdoc in user_docs:
            user_reactions_map[rdoc["reaction"]] = str(rdoc["_id"])

    # Aggregate total counts per reaction
    pipeline = [
        {"$match": {"changelog_id": target_oid, "reaction": {"$in": ALLOWED_REACTIONS}}},
        {"$group": {"_id": "$reaction", "count": {"$sum": 1}}},
    ]
    counts_map: dict[str, int] = {}
    cursor = db["reactions"].aggregate(pipeline)
    async for group in cursor:
        counts_map[group["_id"]] = group["count"]

    for emoji in ALLOWED_REACTIONS:
        user_reacted = emoji in user_reactions_map
        user_reaction_id = user_reactions_map.get(emoji)
        reactions_list.append(
            ReactionItemSummary(
                reaction=emoji,
                count=counts_map.get(emoji, 0),
                user_reacted=user_reacted,
                user_reaction_id=user_reaction_id,
            )
        )

    return ChangelogReactionsSummary(
        changelog_id=changelog_id,
        reactions=reactions_list,
    )
