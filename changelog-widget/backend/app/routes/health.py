"""
routes/health.py
----------------
GET /health — verifies both FastAPI and MongoDB are operational.

Why check MongoDB here?
────────────────────────
A process can be running perfectly but the database can be unreachable
(wrong URI, expired Atlas free-tier pause, firewall, etc.).
A health endpoint that only says "I'm alive" misses half the picture.
This endpoint gives a real end-to-end signal for both layers.

Response shape:
    {
        "status": "healthy" | "degraded",
        "api":    "ok",
        "database": {
            "status":   "connected" | "unavailable",
            "database": "<db name>"          ← on success
            "error":    "<reason>"           ← on failure
        }
    }

HTTP status:
    200  when both API + DB are healthy
    503  when DB is unreachable (API is still running, but service is degraded)
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import ping_database, get_database

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check(db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Returns the health of the API and its MongoDB connection.
    HTTP 200 = fully healthy.
    HTTP 503 = API running but database unreachable.
    """
    db_status = await ping_database(db)
    is_healthy = db_status["status"] == "connected"

    body = {
        "status":   "healthy" if is_healthy else "degraded",
        "api":      "ok",
        "database": db_status,
    }

    # 503 Service Unavailable signals to load balancers / uptime monitors
    # that this instance should not receive traffic.
    status_code = 200 if is_healthy else 503
    return JSONResponse(content=body, status_code=status_code)
