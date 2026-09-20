"""
routes/rss.py
--------------
RSS 2.0 feed endpoint:
- GET /api/v1/changelog/rss  — public RSS XML feed of published changelogs
"""

from datetime import timezone
from fastapi import APIRouter, Depends, Query, Response
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.config.settings import settings
from app.models.enums import ChangelogStatus

router = APIRouter()

RSS_CONTENT_TYPE = "application/rss+xml; charset=utf-8"


@router.get(
    "/rss",
    summary="Public RSS feed of published changelogs",
    description="Returns a valid RSS 2.0 XML feed of published changelog updates in reverse chronological order.",
    response_class=Response,
    tags=["Feed"],
)
async def changelog_rss(
    limit: int = Query(default=20, ge=1, le=100, description="Number of items (max 100)"),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    cursor = (
        db["changelogs"]
        .find({"status": ChangelogStatus.PUBLISHED.value})
        .sort([("is_pinned", -1), ("published_at", -1)])
        .limit(limit)
    )

    items_xml = []
    async for doc in cursor:
        title = _escape_xml(doc.get("title", ""))
        slug = doc.get("slug", "")
        category = doc.get("category", "")
        version = doc.get("version", "")
        published_at = doc.get("published_at")

        # Format date as RFC 822 (required by RSS)
        pub_date = ""
        if published_at:
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            pub_date = published_at.strftime("%a, %d %b %Y %H:%M:%S +0000")

        # Build content snippet from markdown (strip markup)
        raw_content = doc.get("content_markdown", "")
        description = _escape_xml(raw_content[:500] + ("…" if len(raw_content) > 500 else ""))

        link = f"{settings.frontend_url}/updates/{slug}"

        version_part = f"[{version}] " if version else ""
        full_title = f"{version_part}{title} #{category}"

        items_xml.append(f"""    <item>
      <title>{_escape_xml(full_title)}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <description>{description}</description>
      <pubDate>{pub_date}</pubDate>
      <category>{_escape_xml(category)}</category>
    </item>""")

    items_str = "\n".join(items_xml)

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{_escape_xml(settings.app_name)} Product Updates</title>
    <link>{settings.frontend_url}</link>
    <description>Latest product updates, features, and bug fixes from {_escape_xml(settings.app_name)}.</description>
    <language>en-us</language>
    <atom:link href="{settings.frontend_url}/api/v1/changelog/rss" rel="self" type="application/rss+xml"/>
{items_str}
  </channel>
</rss>"""

    return Response(
        content=rss_xml,
        media_type=RSS_CONTENT_TYPE,
        headers={"Cache-Control": "public, max-age=300"},
    )


def _escape_xml(text: str) -> str:
    """Escape characters that would break XML."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )
