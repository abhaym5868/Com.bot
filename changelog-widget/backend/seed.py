"""
seed.py
-------
Populates the database with realistic sample data so the app is demo-ready.

Usage:
    cd backend
    source venv/bin/activate
    python seed.py

This script is idempotent: it checks if data already exists before inserting.
"""

import asyncio
from bson import ObjectId
from datetime import datetime, timedelta, timezone

from motor.motor_asyncio import AsyncIOMotorClient

# ── Load settings ─────────────────────────────────────────────────────────────
from app.config.settings import settings

# Fake admin ObjectId used as created_by for seeded entries
SEED_ADMIN_ID = ObjectId("000000000000000000000001")

# ── Sample data ───────────────────────────────────────────────────────────────
# IMPORTANT: use uppercase enum values (PUBLISHED/DRAFT/NEW/IMPROVED/FIXED)
# and the field name `content_markdown` to match the ChangelogModel.

CHANGELOGS = [
    {
        "title": "Introducing the Changelog Widget v1.0",
        "slug": "introducing-changelog-widget-v1-0",
        "content_markdown": """# 🎉 Welcome to the Changelog Widget!

We're thrilled to announce the **official launch** of the Changelog & Product Updates Widget — a self-hosted, embeddable solution for keeping your users informed about every improvement to your product.

## What's included?

- **Live timeline** of product updates, always in sync with your backend
- **Reaction system** — users can express ❤️ Love, 🎉 Celebrate, or 🚀 Rocket on any update
- **Notification center** — a bell icon shows unread counts and marks items read
- **Admin dashboard** — create, edit, draft, and publish updates with a rich Markdown editor
- **Public JSON feed** — machine-readable feed at `/api/v1/changelog/feed` for integrations
- **Category badges** — NEW · IMPROVED · FIXED

## How to get started

1. Sign up for an account
2. If you're an admin, log in and head to the **Dashboard**
3. Create your first changelog entry using the **Markdown Studio**
4. Hit **Publish** — it appears on the timeline instantly

We hope this makes it easier than ever to keep your community in the loop!
""",
        "category": "NEW",
        "status": "PUBLISHED",
        "published_at": datetime.now(timezone.utc) - timedelta(days=10),
        "cover_image": None,
    },
    {
        "title": "Improved Search — Now With Full-Text Debouncing",
        "slug": "improved-search-full-text-debouncing",
        "content_markdown": """# 🔍 Search is Smarter Now

We've upgraded the search experience on the public timeline with **server-side full-text matching** and a **300 ms debounce** so your results update smoothly as you type — without hammering the server.

## What changed?

| Before | After |
|--------|-------|
| Simple `contains` match on title only | Full-text search across title **and** content |
| Fires on every keystroke | Debounced to 300 ms |
| No URL persistence | Search query synced to URL params |

## Technical details

- The backend uses a MongoDB text index on `title` + `content` fields
- The frontend React hook uses `setTimeout` / `clearTimeout` for clean teardown
- Query parameter `?search=...` is preserved on page refresh

This means you can share a link directly to a filtered view — try it!
""",
        "category": "IMPROVED",
        "status": "PUBLISHED",
        "published_at": datetime.now(timezone.utc) - timedelta(days=7),
        "cover_image": None,
    },
    {
        "title": "Fixed: Notification Badge Count After Mark-All-Read",
        "slug": "fixed-notification-badge-count-mark-all-read",
        "content_markdown": """# 🐛 Bug Fix: Notification Count

We squashed a subtle bug where the red unread badge on the 🔔 bell icon **did not reset to zero** after clicking "Mark all as read" — it would stay at the old number until a page reload.

## Root cause

The `NotificationCenter` component was reading the count from a stale closure in the polling interval. After marking all read, the server returned 0 unread notifications, but the interval was referencing the cached value.

## Fix applied

- Replaced the stale closure with a `useCallback` + `useRef` pattern
- The count now updates **immediately** in the UI on successful mark-read response
- Added an optimistic UI update so there's no flicker

**No action needed** — the fix is live.
""",
        "category": "FIXED",
        "status": "PUBLISHED",
        "published_at": datetime.now(timezone.utc) - timedelta(days=5),
        "cover_image": None,
    },
    {
        "title": "New: Image Attachment Support in Changelog Posts",
        "slug": "new-image-attachment-support",
        "content_markdown": """# 🖼️ Cover Images Are Here

Admins can now upload a **cover image** to any changelog post. Images appear at the top of the detail page and as a thumbnail preview on the timeline card.

## Supported formats

- JPEG / PNG / WEBP / GIF
- Maximum file size: **5 MB**
- Images are stored under `backend/uploads/` and served at `/static/uploads/<filename>`

## How to add an image

1. Open the **Admin Dashboard**
2. Click **Create** or **Edit** on an existing post
3. In the Markdown Studio, click the 📎 image upload area
4. Select your file — the URL is inserted into your Markdown automatically

The Markdown preview renders the image in real time so you can see exactly how it will look before publishing.
""",
        "category": "NEW",
        "status": "PUBLISHED",
        "published_at": datetime.now(timezone.utc) - timedelta(days=3),
        "cover_image": None,
    },
    {
        "title": "Performance: MongoDB Indexes Added for Faster Queries",
        "slug": "performance-mongodb-indexes-faster-queries",
        "content_markdown": """# ⚡ Database Performance Upgrade

We've added strategic **MongoDB indexes** that significantly reduce query time for high-traffic scenarios.

## Indexes added

| Collection | Index | Purpose |
|------------|-------|---------|
| `changelogs` | `{ status: 1, published_at: -1 }` | Timeline listing |
| `changelogs` | `{ slug: 1 }` (unique) | Slug lookups |
| `changelogs` | Text index on `title + content` | Full-text search |
| `reactions` | `{ changelog_id: 1, user_id: 1, emoji: 1 }` (unique) | Prevent duplicate reactions |
| `notifications` | `{ user_id: 1, read: 1 }` | Unread count queries |
| `refresh_tokens` | `{ token: 1 }` (unique) + TTL | Token rotation |

## Impact

In local testing with 10,000 changelog documents, the timeline query went from **~120 ms → ~4 ms**.

No migration needed — indexes are created automatically at startup.
""",
        "category": "IMPROVED",
        "status": "PUBLISHED",
        "published_at": datetime.now(timezone.utc) - timedelta(days=1),
        "cover_image": None,
    },
    {
        "title": "Draft: Upcoming — Webhook Notifications (Coming Soon)",
        "slug": "upcoming-webhook-notifications",
        "content_markdown": """# 🔔 Webhooks — Work in Progress

We're building **outbound webhook support** so you can trigger external services whenever a changelog post is published.

## Planned features

- POST to a configurable webhook URL on publish
- Signed payloads with HMAC-SHA256 for verification
- Retry logic with exponential back-off

Stay tuned — this will ship in the next major release!
""",
        "category": "NEW",
        "status": "DRAFT",
        "published_at": None,
        "cover_image": None,
    },
]


async def seed():
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.database_name]

    existing = await db.changelogs.count_documents({})
    if existing > 0:
        print(f"⚠️  Database already has {existing} changelog(s). Skipping seed to avoid duplicates.")
        print("   To re-seed, drop the changelogs collection first:")
        print("   python -c \"import asyncio; from motor.motor_asyncio import AsyncIOMotorClient; from app.config.settings import settings; c=AsyncIOMotorClient(settings.mongo_uri); asyncio.run(c[settings.database_name].changelogs.drop())\"")
        client.close()
        return

    now = datetime.now(timezone.utc)
    docs = []
    for entry in CHANGELOGS:
        doc = {
            **entry,
            "created_by": SEED_ADMIN_ID,
            "created_at": entry.get("published_at") or now,
            "updated_at": entry.get("published_at") or now,
        }
        docs.append(doc)

    result = await db.changelogs.insert_many(docs)
    published = sum(1 for d in docs if d["status"] == "PUBLISHED")
    print(f"✅ Seeded {len(result.inserted_ids)} changelogs ({published} published, {len(docs)-published} draft).")
    print()
    print("   You can now open:")
    print("   • Timeline:  http://localhost:5173/")
    print("   • JSON Feed: http://localhost:5173/api/v1/changelog/feed")
    print("   • Backend:   http://127.0.0.1:8000/api/v1/changelog/feed")

    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
