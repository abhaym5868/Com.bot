"""
utils/slug.py
-------------
Slug generation from titles and collision avoidance with MongoDB.
"""

import re
import unicodedata
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


def slugify(text: str) -> str:
    """
    Transform arbitrary text into an URL-friendly slug.
    Example: "New Feature: AI Assistant v2.0!" -> "new-feature-ai-assistant-v2-0"
    """
    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    # Convert to lowercase
    text = text.lower()
    # Replace non-alphanumeric characters with hyphens
    text = re.sub(r"[^\w\s-]", "-", text)
    # Replace multiple whitespace/hyphens with a single hyphen
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text or "changelog"


async def generate_unique_slug(
    db: AsyncIOMotorDatabase,
    title_or_slug: str,
    exclude_id: str | None = None,
) -> str:
    """
    Ensure the slug is unique in the changelogs collection.
    If a conflict exists, appends numerical suffixes: -1, -2, etc.
    """
    base_slug = slugify(title_or_slug)
    candidate = base_slug
    counter = 1

    while True:
        query: dict = {"slug": candidate}
        if exclude_id and ObjectId.is_valid(exclude_id):
            query["_id"] = {"$ne": ObjectId(exclude_id)}

        existing = await db["changelogs"].find_one(query, {"_id": 1})
        if not existing:
            return candidate

        candidate = f"{base_slug}-{counter}"
        counter += 1
