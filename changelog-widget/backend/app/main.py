"""
main.py
-------
FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload
"""

import asyncio
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.settings import settings
from app.config.database import connect_db, close_db, get_database
from app.routes import health as health_router
from app.routes import auth as auth_router
from app.routes import changelog as changelog_router
from app.routes import reaction as reaction_router
from app.routes import notification as notification_router
from app.routes import upload as upload_router
from app.routes import analytics as analytics_router
from app.routes import audit as audit_router
from app.routes import rss as rss_router
from app.routes import widget_config as widget_config_router
from app.services.scheduler import scheduled_publisher_task

logger = logging.getLogger(__name__)

# ─── Lifespan (startup + shutdown) ────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    await connect_db()

    # Get the db handle for the background scheduler
    db = get_database()

    # Start background scheduler for auto-publishing SCHEDULED changelogs
    scheduler_task = asyncio.create_task(scheduled_publisher_task(db))
    logger.info("Background scheduler started.")

    yield

    # --- shutdown ---
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass
    await close_db()


# ─── App Instance ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Changelog Widget API",
    version="2.0.0",
    description="REST API for the Changelog & Product Updates Widget — SaaS production platform.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,   # needed for httpOnly cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Global Exception Handler ─────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server error processing %s: %s", request.url.path, exc)
    detail = (
        str(exc)
        if settings.environment.lower() == "development"
        else "An internal server error occurred."
    )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": detail},
    )

# ─── Root ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    """Quick sanity check — confirms the server is reachable."""
    return {"message": "Changelog Widget API is running", "version": "2.0.0"}

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(health_router.router)
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(rss_router.router, prefix="/api/v1/changelog", tags=["Feed"])
app.include_router(changelog_router.router, prefix="/api/v1/changelog", tags=["Changelog"])
app.include_router(reaction_router.router, prefix="/api/v1/reactions", tags=["Reactions"])
app.include_router(notification_router.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(upload_router.router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(analytics_router.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(audit_router.router, prefix="/api/v1/audit", tags=["Audit"])
app.include_router(widget_config_router.router, prefix="/api/v1/widget", tags=["Widget"])

# ─── Static Files (Uploads + Widget) ──────────────────────────────────────────
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Serve the embeddable widget JS from the static/widget directory
widget_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "widget")
os.makedirs(widget_dir, exist_ok=True)
app.mount("/static/widget", StaticFiles(directory=widget_dir), name="widget")
