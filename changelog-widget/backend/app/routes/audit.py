"""
routes/audit.py
---------------
Admin audit log endpoint:
- GET /api/v1/audit  — paginated activity log (Admin only)
"""

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.middleware.auth import get_current_admin_user
from app.models.user import UserModel

router = APIRouter()


@router.get(
    "",
    summary="Admin activity log (Admin only)",
    description="Returns paginated audit log entries of admin actions: creates, edits, publishes, deletes, pins, etc.",
)
async def list_audit_logs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    admin_user: UserModel = Depends(get_current_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    import math
    skip = (page - 1) * limit
    total = await db["audit_logs"].count_documents({})
    total_pages = max(1, math.ceil(total / limit)) if total > 0 else 1

    cursor = (
        db["audit_logs"]
        .find({}, {"_id": 1, "user_id": 1, "user_name": 1, "action": 1, "resource_type": 1,
                   "resource_id": 1, "resource_title": 1, "metadata": 1, "timestamp": 1})
        .sort("timestamp", -1)
        .skip(skip)
        .limit(limit)
    )

    items = []
    async for doc in cursor:
        res_id = doc.get("resource_id")
        items.append({
            "id": str(doc["_id"]),
            "user_id": str(doc.get("user_id", "")),
            "user_name": doc.get("user_name", ""),
            "action": doc.get("action", ""),
            "resource_type": doc.get("resource_type", ""),
            "resource_id": str(res_id) if res_id is not None else None,
            "resource_title": doc.get("resource_title"),
            "metadata": {k: str(v) if isinstance(v, (int, float, str, bool, list, dict)) else str(v) for k, v in doc.get("metadata", {}).items()},
            "timestamp": doc.get("timestamp"),
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": total_pages,
    }
