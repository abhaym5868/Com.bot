"""
tests/test_v2_features.py
-------------------------
Integration tests for v2 features:
1. Pin/unpin changelogs
2. Scheduled changelog status and auto-publishing logic
3. RSS 2.0 XML feed endpoint
4. Anonymous view tracking and analytics dashboard
5. Admin audit log recording
"""

import asyncio
import pytest
from datetime import datetime, timezone, timedelta
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.config.database import get_database
from app.models.indexes import create_database_indexes
from app.services.changelog_service import auto_publish_scheduled


@pytest.mark.asyncio
async def test_v2_features():
    print("🚀 Starting Changelog v2 Feature Integration Tests...\n")

    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["test_v2_changelog_db"]
    await create_database_indexes(mock_db)

    app.dependency_overrides[get_database] = lambda: mock_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Setup Admin
        print("1️⃣ Setting up Admin user...")
        res_admin = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Admin Boss", "email": "admin@v2.com", "password": "AdminPassword123!"},
        )
        assert res_admin.status_code == 201
        admin_token = res_admin.cookies.get("access_token")
        assert admin_token is not None
        headers = {"Authorization": f"Bearer {admin_token}"}
        print("   ✅ Admin created successfully.")

        # 2. Test Changelog creation with Version and Scheduled status
        print("2️⃣ Testing Changelog creation with version & SCHEDULED status...")
        future_time = datetime.now(timezone.utc) + timedelta(days=2)
        sched_res = await client.post(
            "/api/v1/changelog",
            headers=headers,
            json={
                "title": "Scheduled Release v2.1",
                "content_markdown": "## Coming Soon\nBig improvements coming!",
                "category": "NEW",
                "status": "SCHEDULED",
                "version": "v2.1.0",
                "scheduled_for": future_time.isoformat(),
            },
        )
        assert sched_res.status_code == 201
        sched_data = sched_res.json()
        sched_id = sched_data["id"]
        assert sched_data["status"] == "SCHEDULED"
        assert sched_data["version"] == "v2.1.0"
        print("   ✅ Scheduled changelog created.")

        # Public user should NOT see SCHEDULED changelog
        anon_feed = await client.get("/api/v1/changelog/feed")
        assert anon_feed.status_code == 200
        assert anon_feed.json()["total"] == 0
        print("   ✅ Public feed correctly excludes SCHEDULED posts.")

        # 3. Test Pin / Unpin
        print("3️⃣ Testing Pin & Unpin endpoints...")
        # Create published post
        pub_res = await client.post(
            "/api/v1/changelog",
            headers=headers,
            json={
                "title": "Published Release v2.0",
                "content_markdown": "## Version 2.0 is live!\nFeaturing RSS and Dark Mode.",
                "category": "NEW",
                "status": "PUBLISHED",
                "version": "v2.0.0",
            },
        )
        assert pub_res.status_code == 201
        pub_id = pub_res.json()["id"]

        # Pin it
        pin_res = await client.post(f"/api/v1/changelog/{pub_id}/pin", headers=headers)
        assert pin_res.status_code == 200
        assert pin_res.json()["is_pinned"] is True
        print("   ✅ Changelog pinned successfully.")

        # Unpin it
        unpin_res = await client.post(f"/api/v1/changelog/{pub_id}/unpin", headers=headers)
        assert unpin_res.status_code == 200
        assert unpin_res.json()["is_pinned"] is False
        print("   ✅ Changelog unpinned successfully.")

        # Re-pin for RSS test
        await client.post(f"/api/v1/changelog/{pub_id}/pin", headers=headers)

        # 4. Test RSS 2.0 XML Feed
        print("4️⃣ Testing GET /api/v1/changelog/rss...")
        rss_res = await client.get("/api/v1/changelog/rss")
        assert rss_res.status_code == 200
        assert "application/rss+xml" in rss_res.headers["content-type"]
        rss_text = rss_res.text
        assert "<rss version=\"2.0\"" in rss_text
        assert "Published Release v2.0" in rss_text
        assert "[v2.0.0]" in rss_text
        print("   ✅ RSS feed generated valid XML with version tag.")

        # 5. Test Anonymous View Recording & Analytics
        print("5️⃣ Testing View recording and Analytics Dashboard...")
        view_res = await client.post(
            f"/api/v1/analytics/view/{pub_id}",
            headers={"User-Agent": "TestBrowser/1.0", "X-Forwarded-For": "192.168.1.50"}
        )
        assert view_res.status_code == 200
        assert view_res.json()["recorded"] is True
        print("   ✅ View recorded successfully.")

        # Duplicate view from same IP & UA within cooldown window
        view_res2 = await client.post(
            f"/api/v1/analytics/view/{pub_id}",
            headers={"User-Agent": "TestBrowser/1.0", "X-Forwarded-For": "192.168.1.50"}
        )
        assert view_res2.status_code == 200
        assert view_res2.json()["recorded"] is False
        print("   ✅ Duplicate view deduplicated accurately.")

        # Analytics Dashboard
        dash_res = await client.get("/api/v1/analytics/dashboard", headers=headers)
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert dash_data["total_views"] >= 1
        assert dash_data["total_changelogs"] >= 1
        print("   ✅ Analytics dashboard returned accurate aggregate stats.")

        # 6. Test Admin Audit Log
        print("6️⃣ Testing GET /api/v1/audit...")
        audit_res = await client.get("/api/v1/audit", headers=headers)
        assert audit_res.status_code == 200
        audit_data = audit_res.json()
        assert audit_data["total"] >= 1
        print("   ✅ Audit log recorded admin activity.")

        # 7. Test Auto-publishing logic for past scheduled dates
        print("7️⃣ Testing auto-publishing scheduled changelogs...")
        # Update scheduled post to past time
        past_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        await mock_db["changelogs"].update_one(
            {"status": "SCHEDULED"},
            {"$set": {"scheduled_for": past_time}}
        )
        published_count = await auto_publish_scheduled(mock_db)
        assert published_count == 1
        print("   ✅ Auto-publish worker published 1 scheduled post whose time passed.")

    print("\n🎉 ALL v2 FEATURE TESTS PASSED FLAWLESSLY!")


if __name__ == "__main__":
    asyncio.run(run_v2_tests())
