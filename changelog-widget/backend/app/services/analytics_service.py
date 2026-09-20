"""
services/analytics_service.py
-------------------------------
Aggregation queries for admin analytics dashboard.
All metrics come from real MongoDB data — no synthetic numbers.
"""

import hashlib
import logging
from bson import ObjectId
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.base import utc_now
from app.models.enums import ChangelogStatus
from app.models.view import ViewModel

logger = logging.getLogger(__name__)

# ── Cooldown window to prevent rapid re-counting (1 hour) ─────────────────────
VIEW_COOLDOWN_SECONDS = 3600


def _make_visitor_hash(request: Request) -> str:
    """
    Build an anonymous, non-reversible visitor fingerprint from IP + User-Agent.
    A static salt is mixed in so the raw hash can't be correlated across systems.
    """
    salt = "cw-view-v1"
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    raw = f"{salt}:{ip}:{ua}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def record_view(
    db: AsyncIOMotorDatabase,
    changelog_id: str,
    request: Request,
    user_id: str | None = None,
) -> bool:
    """
    Record a view for a changelog post.
    Returns True if the view was recorded, False if it was a duplicate within the cooldown window.
    """
    if not ObjectId.is_valid(changelog_id):
        return False

    visitor_hash = _make_visitor_hash(request)
    now = utc_now()

    from datetime import timedelta
    cooldown_since = now - timedelta(seconds=VIEW_COOLDOWN_SECONDS)

    # Check for recent view from same visitor on same changelog
    existing = await db["views"].find_one({
        "changelog_id": ObjectId(changelog_id),
        "visitor_hash": visitor_hash,
        "timestamp": {"$gte": cooldown_since},
    })

    if existing:
        return False  # Duplicate within cooldown

    view = ViewModel(
        changelog_id=changelog_id,
        visitor_hash=visitor_hash,
        user_id=user_id if user_id else None,
        timestamp=now,
    )
    await db["views"].insert_one(view.to_mongo())
    return True


async def get_dashboard_stats(db: AsyncIOMotorDatabase) -> dict:
    """
    Aggregate admin dashboard statistics from real data.
    Returns total views, total reactions, published count, draft count,
    scheduled count, and top performing updates.
    """
    # ── Published / Draft / Scheduled counts ──────────────────────────────────
    total_published = await db["changelogs"].count_documents(
        {"status": ChangelogStatus.PUBLISHED.value}
    )
    total_draft = await db["changelogs"].count_documents(
        {"status": ChangelogStatus.DRAFT.value}
    )
    total_scheduled = await db["changelogs"].count_documents(
        {"status": ChangelogStatus.SCHEDULED.value}
    )
    total_changelogs = total_published + total_draft + total_scheduled

    # ── Total views ──────────────────────────────────────────────────────────
    total_views = await db["views"].count_documents({})

    # ── Total reactions ───────────────────────────────────────────────────────
    total_reactions = await db["reactions"].count_documents({})

    # ── Reaction distribution ─────────────────────────────────────────────────
    reaction_pipeline = [
        {"$group": {"_id": "$reaction", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    reaction_dist: dict[str, int] = {}
    async for doc in db["reactions"].aggregate(reaction_pipeline):
        reaction_dist[doc["_id"]] = doc["count"]

    # ── Most viewed updates (top 5) ────────────────────────────────────────────
    view_pipeline = [
        {"$group": {"_id": "$changelog_id", "view_count": {"$sum": 1}}},
        {"$sort": {"view_count": -1}},
        {"$limit": 5},
    ]
    most_viewed = []
    async for doc in db["views"].aggregate(view_pipeline):
        cl_doc = await db["changelogs"].find_one({"_id": doc["_id"]})
        if cl_doc:
            most_viewed.append({
                "id": str(doc["_id"]),
                "title": cl_doc.get("title", ""),
                "slug": cl_doc.get("slug", ""),
                "view_count": doc["view_count"],
            })

    # ── Most reacted updates (top 5) ──────────────────────────────────────────
    react_pipeline = [
        {"$group": {"_id": "$changelog_id", "reaction_count": {"$sum": 1}}},
        {"$sort": {"reaction_count": -1}},
        {"$limit": 5},
    ]
    most_reacted = []
    async for doc in db["reactions"].aggregate(react_pipeline):
        cl_doc = await db["changelogs"].find_one({"_id": doc["_id"]})
        if cl_doc:
            most_reacted.append({
                "id": str(doc["_id"]),
                "title": cl_doc.get("title", ""),
                "slug": cl_doc.get("slug", ""),
                "reaction_count": doc["reaction_count"],
            })

    return {
        "total_changelogs": total_changelogs,
        "total_published": total_published,
        "total_draft": total_draft,
        "total_scheduled": total_scheduled,
        "total_views": total_views,
        "total_reactions": total_reactions,
        "reaction_distribution": reaction_dist,
        "most_viewed": most_viewed,
        "most_reacted": most_reacted,
    }


async def get_update_performance(db: AsyncIOMotorDatabase, limit: int = 20) -> list[dict]:
    """
    Per-update metrics: views + reactions for published changelogs.
    """
    cursor = (
        db["changelogs"]
        .find({"status": ChangelogStatus.PUBLISHED.value})
        .sort([("published_at", -1)])
        .limit(limit)
    )

    results = []
    async for cl_doc in cursor:
        cl_id = cl_doc["_id"]
        view_count = await db["views"].count_documents({"changelog_id": cl_id})
        reaction_count = await db["reactions"].count_documents({"changelog_id": cl_id})

        # Per-reaction breakdown
        reaction_pipeline = [
            {"$match": {"changelog_id": cl_id}},
            {"$group": {"_id": "$reaction", "count": {"$sum": 1}}},
        ]
        reaction_breakdown: dict[str, int] = {}
        async for rdoc in db["reactions"].aggregate(reaction_pipeline):
            reaction_breakdown[rdoc["_id"]] = rdoc["count"]

        results.append({
            "id": str(cl_id),
            "title": cl_doc.get("title", ""),
            "slug": cl_doc.get("slug", ""),
            "category": cl_doc.get("category", ""),
            "version": cl_doc.get("version"),
            "published_at": cl_doc.get("published_at"),
            "view_count": view_count,
            "reaction_count": reaction_count,
            "reaction_breakdown": reaction_breakdown,
        })

    return results


async def log_admin_action(
    db: AsyncIOMotorDatabase,
    user_id: str,
    user_name: str,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    resource_title: str | None = None,
    metadata: dict | None = None,
) -> None:
    """
    Insert an audit log entry. Fire-and-forget — errors are logged, not raised.
    """
    try:
        from app.models.audit_log import AuditLogModel
        log_entry = AuditLogModel(
            user_id=user_id,
            user_name=user_name,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_title=resource_title,
            metadata=metadata or {},
        )
        await db["audit_logs"].insert_one(log_entry.to_mongo())
    except Exception as exc:
        logger.warning("Failed to write audit log: %s", exc)
