"""
config/database.py
------------------
MongoDB connection using Motor — the async driver for Python.

Why Motor instead of plain PyMongo?
────────────────────────────────────
FastAPI is an async framework. PyMongo is synchronous — calling it inside an
async route would block the event loop, making the server unable to handle
other requests while waiting for MongoDB. Motor is PyMongo's async wrapper
that plays nicely with asyncio, so database calls are non-blocking.

How the connection works:
──────────────────────────
1. AsyncIOMotorClient is created once when this module is first imported.
   It manages an internal connection pool — typically 5–100 connections —
   so we don't open/close a connection on every request.

2. get_database() is a FastAPI dependency. Route functions declare it as a
   parameter and FastAPI injects the DB handle automatically:

       async def my_route(db = Depends(get_database)):
           doc = await db["users"].find_one({"email": "..."})

3. ping_database() is used by GET /health to check if MongoDB is reachable.
   It sends the lightest possible command ("ping") to the server.
"""

import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.config.settings import settings

logger = logging.getLogger(__name__)

# ─── Client (module-level singleton) ──────────────────────────────────────────
# serverSelectionTimeoutMS=5000 means: if MongoDB can't be reached within
# 5 seconds, raise an error instead of hanging indefinitely.

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    """Return the shared Motor client, creating it if needed."""
    global _client
    if _client is None:
        client_kwargs = {
            "serverSelectionTimeoutMS": 5000,  # fail fast if unreachable
        }
        if "mongodb+srv://" in settings.mongo_uri or "ssl=true" in settings.mongo_uri.lower() or "tls=true" in settings.mongo_uri.lower():
            try:
                import certifi
                client_kwargs["tlsCAFile"] = certifi.where()
            except Exception:
                pass

        _client = AsyncIOMotorClient(
            settings.mongo_uri,
            **client_kwargs,
        )
        logger.info("MongoDB client created.")
    return _client


def get_database() -> AsyncIOMotorDatabase:
    """
    FastAPI dependency — inject this to get the database handle.

    Usage in a route:
        async def create_user(db: AsyncIOMotorDatabase = Depends(get_database)):
            await db["users"].insert_one({...})
    """
    return get_client()[settings.database_name]


# ─── Health check helper ───────────────────────────────────────────────────────

async def ping_database(db: AsyncIOMotorDatabase | None = None) -> dict:
    """
    Send a lightweight 'ping' command to MongoDB.

    Returns a dict:
        {"status": "connected", "database": "<db name>"}   on success
        {"status": "unavailable", "error": "<reason>"}      on failure
    """
    try:
        database = db if db is not None else get_database()
        # db.command("ping") is the official lightest-weight MongoDB round-trip.
        # It doesn't read or write any data — just checks connectivity.
        await database.command("ping")
        db_name = getattr(database, "name", settings.database_name)
        return {"status": "connected", "database": db_name}

    except ServerSelectionTimeoutError:
        logger.warning("MongoDB ping timed out.")
        return {
            "status": "unavailable",
            "error": "Server selection timed out — check MONGO_URI and network access.",
        }
    except ConnectionFailure as exc:
        logger.warning("MongoDB connection failed: %s", exc)
        error_msg = str(exc) if settings.environment.lower() == "development" else "Database connection failed."
        return {"status": "unavailable", "error": error_msg}
    except Exception as exc:
        logger.error("Unexpected DB error: %s", exc)
        error_msg = str(exc) if settings.environment.lower() == "development" else "Database service unavailable."
        return {"status": "unavailable", "error": error_msg}


# ─── Lifecycle helpers (optional — called from main.py startup/shutdown) ───────

async def connect_db():
    """Call at app startup to eagerly create the client and log the result."""
    result = await ping_database()
    if result["status"] == "connected":
        logger.info("✅ MongoDB connected — database: %s", settings.database_name)
        try:
            from app.models.indexes import create_database_indexes
            db = get_database()
            await create_database_indexes(db)
        except Exception as exc:
            logger.warning("Failed to initialize database indexes: %s", exc)
    else:
        logger.error("❌ MongoDB unreachable at startup: %s", result["error"])


async def close_db():
    """Call at app shutdown to cleanly close the connection pool."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("MongoDB client closed.")
