"""
tests/test_feed_api.py
----------------------
Integration tests for GET /api/v1/changelog/feed.

Tests verified:
    1. Feed is public — no auth required (HTTP 200).
    2. Returns ONLY published updates (drafts excluded).
    3. Items sorted newest-first (reverse-chronological).
    4. Pagination (page / limit) works correctly — no slug overlap.
    5. FeedItem shape: title, slug, category, published_at, cover_image.
    6. Internal fields (content_markdown, created_by) do NOT leak.
    7. Cache-Control: public, max-age=300 header is set.
    8. Empty feed returns [] with total=0 (not 404/500).
"""

import asyncio
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.config.database import get_database
from app.models.indexes import create_database_indexes


async def run_tests():
    print("🚀 Starting Public JSON Feed Integration Tests...\n")

    # ── Setup mock MongoDB ───────────────────────────────────────────────────
    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["test_feed_db"]
    await create_database_indexes(mock_db)
    app.dependency_overrides[get_database] = lambda: mock_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:

        # ── Shared setup: admin account ──────────────────────────────────────
        res = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Feed Admin", "email": "feedadmin@example.com", "password": "AdminPass123!"},
        )
        assert res.status_code == 201, f"Signup failed: {res.text}"
        admin_token = res.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # ── Helper: create a changelog entry ─────────────────────────────────
        async def create_cl(title, category="NEW", cover_image=None):
            payload = {
                "title": title,
                "content_markdown": f"Content for **{title}**",
                "category": category,
                "status": "DRAFT",
            }
            if cover_image:
                payload["cover_image"] = cover_image
            r = await client.post("/api/v1/changelog", json=payload, headers=admin_headers)
            assert r.status_code == 201, f"Create failed: {r.text}"
            return r.json()

        async def publish_cl(cl_id):
            r = await client.post(f"/api/v1/changelog/{cl_id}/publish", headers=admin_headers)
            assert r.status_code == 200, f"Publish failed: {r.text}"
            return r.json()

        async def get_feed(page=1, limit=20, headers=None):
            return await client.get(
                "/api/v1/changelog/feed",
                params={"page": page, "limit": limit},
                headers=headers or {},
            )

        # ─────────────────────────────────────────────────────────────────────
        # Test 1 — Feed is public (no auth needed)
        # ─────────────────────────────────────────────────────────────────────
        print("1️⃣  Feed is public (no Authorization header)...")
        resp = await get_feed()
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        print("   ✅ GET /api/v1/changelog/feed returned 200 without auth.\n")

        # ─────────────────────────────────────────────────────────────────────
        # Test 2 — Empty feed
        # ─────────────────────────────────────────────────────────────────────
        print("2️⃣  Empty feed (no published updates)...")
        data = resp.json()
        assert data["updates"] == [], f"Expected empty list, got {data['updates']}"
        assert data["total"] == 0
        assert data["pages"] == 0 or data["pages"] == 1  # either is acceptable
        print("   ✅ Empty feed returns [] with total=0.\n")

        # ─────────────────────────────────────────────────────────────────────
        # Test 3 — Drafts excluded, only published items appear
        # ─────────────────────────────────────────────────────────────────────
        print("3️⃣  Only published updates appear in feed (drafts excluded)...")
        await create_cl("Draft Only Post", category="NEW")        # stays draft
        pub_cl = await create_cl("Published Post", category="IMPROVED")
        await publish_cl(pub_cl["id"])

        resp = await get_feed()
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1, f"Expected 1 published, got {data['total']}"
        titles = [u["title"] for u in data["updates"]]
        assert "Published Post" in titles
        assert "Draft Only Post" not in titles
        print("   ✅ Draft excluded; only published post visible.\n")

        # ─────────────────────────────────────────────────────────────────────
        # Test 4 — FeedItem shape (required + optional fields)
        # ─────────────────────────────────────────────────────────────────────
        print("4️⃣  FeedItem shape — correct fields present, internals excluded...")
        img_cl = await create_cl("Field Check Post", category="NEW", cover_image="https://cdn.example.com/img.png")
        await publish_cl(img_cl["id"])

        resp = await get_feed()
        data = resp.json()
        item = next(u for u in data["updates"] if u["title"] == "Field Check Post")

        required_fields = {"title", "slug", "category", "published_at"}
        for field in required_fields:
            assert field in item, f"Missing required field: {field}"
        assert item["cover_image"] == "https://cdn.example.com/img.png"
        # Internal fields must not leak
        assert "content_markdown" not in item, "content_markdown leaked into feed!"
        assert "created_by" not in item, "created_by leaked into feed!"
        print("   ✅ FeedItem has correct fields; internals not exposed.\n")

        # ─────────────────────────────────────────────────────────────────────
        # Test 5 — Newest first (reverse-chronological order)
        # ─────────────────────────────────────────────────────────────────────
        print("5️⃣  Feed sorted newest-first...")
        for title in ["Alpha Update", "Beta Update", "Gamma Update"]:
            cl = await create_cl(title, category="FIXED")
            await publish_cl(cl["id"])

        resp = await get_feed()
        data = resp.json()
        # Only get our three new ones by filtering
        three = [u for u in data["updates"] if u["title"] in ("Alpha Update", "Beta Update", "Gamma Update")]
        assert len(three) == 3
        order = [u["title"] for u in three]
        assert order[0] == "Gamma Update", f"Expected Gamma first, got {order}"
        assert order[-1] == "Alpha Update", f"Expected Alpha last, got {order}"
        print("   ✅ Items returned in reverse-chronological order.\n")

        # ─────────────────────────────────────────────────────────────────────
        # Test 6 — Pagination
        # ─────────────────────────────────────────────────────────────────────
        print("6️⃣  Pagination (page/limit)...")
        # At this point we have: Published Post, Field Check Post, Alpha, Beta, Gamma = 5 published
        total_published = data["total"]
        print(f"   Total published so far: {total_published}")

        page1 = await get_feed(page=1, limit=2)
        page2 = await get_feed(page=2, limit=2)
        assert page1.status_code == 200
        assert page2.status_code == 200

        p1 = page1.json()
        p2 = page2.json()

        assert p1["total"] == total_published
        assert len(p1["updates"]) == 2, f"Expected 2 on page1, got {len(p1['updates'])}"
        # Page 2 must not overlap with page 1
        slugs_p1 = {u["slug"] for u in p1["updates"]}
        slugs_p2 = {u["slug"] for u in p2["updates"]}
        assert slugs_p1.isdisjoint(slugs_p2), f"Overlap found: {slugs_p1 & slugs_p2}"
        expected_pages = (total_published + 1) // 2  # ceil(total / limit)
        assert p1["pages"] == expected_pages
        print(f"   ✅ Pagination correct — {total_published} items across {expected_pages} pages of 2.\n")

        # ─────────────────────────────────────────────────────────────────────
        # Test 7 — Cache-Control header
        # ─────────────────────────────────────────────────────────────────────
        print("7️⃣  Cache-Control header...")
        resp = await get_feed()
        cc = resp.headers.get("cache-control", "")
        assert "public" in cc, f"'public' missing from Cache-Control: {cc}"
        assert "max-age=300" in cc, f"'max-age=300' missing from Cache-Control: {cc}"
        print(f"   ✅ Cache-Control: {cc}\n")

    app.dependency_overrides.clear()
    print("🎉 All Public JSON Feed tests passed!\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
