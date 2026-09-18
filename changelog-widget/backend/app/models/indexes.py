"""
models/indexes.py
-----------------
MongoDB index creation logic for collections: users, changelogs, reactions.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING, IndexModel

logger = logging.getLogger(__name__)


async def create_database_indexes(db: AsyncIOMotorDatabase) -> dict[str, list[str]]:
    """
    Ensure all necessary indexes and unique constraints exist in MongoDB.
    Safe to call multiple times (idempotent).
    """
    results: dict[str, list[str]] = {}

    # ── 1. Users collection indexes ──────────────────────────────────────────
    user_indexes = [
        IndexModel(
            [("email", ASCENDING)],
            unique=True,
            name="idx_users_email_unique",
        ),
        IndexModel(
            [("role", ASCENDING)],
            name="idx_users_role",
        ),
    ]
    created_user_indexes = await db["users"].create_indexes(user_indexes)
    results["users"] = created_user_indexes
    logger.info("Ensured users indexes: %s", created_user_indexes)

    # ── 2. Changelogs collection indexes ─────────────────────────────────────
    changelog_indexes = [
        IndexModel(
            [("slug", ASCENDING)],
            unique=True,
            name="idx_changelogs_slug_unique",
        ),
        IndexModel(
            [("status", ASCENDING), ("published_at", DESCENDING)],
            name="idx_changelogs_status_published_at",
        ),
        IndexModel(
            [("category", ASCENDING)],
            name="idx_changelogs_category",
        ),
        IndexModel(
            [("created_by", ASCENDING)],
            name="idx_changelogs_created_by",
        ),
    ]
    created_changelog_indexes = await db["changelogs"].create_indexes(changelog_indexes)
    results["changelogs"] = created_changelog_indexes
    logger.info("Ensured changelogs indexes: %s", created_changelog_indexes)

    # ── 3. Reactions collection indexes ──────────────────────────────────────
    # Important:
    # A user must not be able to create the same reaction multiple times for the same changelog.
    # Enforced by unique compound index on (user_id, changelog_id, reaction).
    reaction_indexes = [
        IndexModel(
            [
                ("user_id", ASCENDING),
                ("changelog_id", ASCENDING),
                ("reaction", ASCENDING),
            ],
            unique=True,
            name="idx_reactions_user_changelog_reaction_unique",
        ),
        IndexModel(
            [("changelog_id", ASCENDING), ("reaction", ASCENDING)],
            name="idx_reactions_changelog_reaction_count",
        ),
        IndexModel(
            [("user_id", ASCENDING)],
            name="idx_reactions_user_id",
        ),
    ]
    created_reaction_indexes = await db["reactions"].create_indexes(reaction_indexes)
    results["reactions"] = created_reaction_indexes
    logger.info("Ensured reactions indexes: %s", created_reaction_indexes)

    # ── 4. Refresh Tokens collection indexes ─────────────────────────────────
    refresh_token_indexes = [
        IndexModel(
            [("user_id", ASCENDING), ("jti", ASCENDING)],
            unique=True,
            name="idx_refresh_tokens_user_jti_unique",
        ),
        IndexModel(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0,
            name="idx_refresh_tokens_ttl",
        ),
    ]
    created_refresh_token_indexes = await db["refresh_tokens"].create_indexes(refresh_token_indexes)
    results["refresh_tokens"] = created_refresh_token_indexes
    logger.info("Ensured refresh_tokens indexes: %s", created_refresh_token_indexes)

    return results

