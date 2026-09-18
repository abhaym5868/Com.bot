"""
main.py
-------
FastAPI application entry point — Step 2 (MongoDB connection added).

Run with:
    uvicorn app.main:app --reload
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.settings import settings
from app.config.database import connect_db, close_db
from app.routes import health as health_router
from app.routes import auth as auth_router
from app.routes import changelog as changelog_router
from app.routes import reaction as reaction_router
from app.routes import notification as notification_router
from app.routes import upload as upload_router



# ─── Lifespan (startup + shutdown) ────────────────────────────────────────────
# FastAPI's recommended way to run code on startup and shutdown.
# On startup  : verify MongoDB is reachable and log the result.
# On shutdown : cleanly close the Motor connection pool.

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    await connect_db()
    yield
    # --- shutdown ---
    await close_db()


# ─── App Instance ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Changelog Widget API",
    version="1.0.0",
    description="REST API for the Changelog & Product Updates Widget.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

import logging

logger = logging.getLogger(__name__)

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
    return {"message": "Changelog API is running"}

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(health_router.router)
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(changelog_router.router, prefix="/api/v1/changelog", tags=["Changelog"])
app.include_router(reaction_router.router, prefix="/api/v1/reactions", tags=["Reactions"])
app.include_router(notification_router.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(upload_router.router, prefix="/api/v1/upload", tags=["Upload"])

# ─── Static Files (Uploads) ───────────────────────────────────────────────────
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


