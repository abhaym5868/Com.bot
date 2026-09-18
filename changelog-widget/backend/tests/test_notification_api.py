"""
tests/test_notification_api.py
------------------------------
End-to-end integration test for What's New Notification Center:
1. Admin creates and publishes updates.
2. User signs up / logs in and queries notification center -> unread_count is verified.
3. User opens notification drawer (calls POST /api/v1/notifications/mark-read).
4. Verify unread_count becomes 0.
5. Admin publishes another update.
6. Verify user's unread_count increases to 1.
"""

import asyncio
from datetime import timedelta
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.config.database import get_database
from app.models.indexes import create_database_indexes
from app.models.base import utc_now


async def run_tests():
    print("🚀 Starting What's New Notification Center Tests...\n")

    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["test_notification_db"]
    await create_database_indexes(mock_db)

    app.dependency_overrides[get_database] = lambda: mock_db

    transport = ASGITransport(app=app)

    # 1. Setup Admin & User Accounts
    print("1️⃣ Setting up Admin & Regular User...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_admin = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Admin Boss", "email": "admin@notif.com", "password": "AdminPassword123!"},
        )
        assert res_admin.status_code == 201
        admin_token = res_admin.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_user = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Sarah Consumer", "email": "sarah@notif.com", "password": "SarahPassword123!"},
        )
        assert res_user.status_code == 201
        user_token = res_user.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}

    print("   ✅ Admin and Sarah created successfully.")

    # 2. Admin creates and publishes 2 updates
    print("2️⃣ Admin publishes 2 initial updates...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res1 = await client.post(
            "/api/v1/changelog",
            json={
                "title": "Release 1.0: Realtime Collaboration",
                "content_markdown": "Now you can work simultaneously with teammates.",
                "category": "NEW",
                "status": "PUBLISHED",
            },
            headers=admin_headers,
        )
        assert res1.status_code == 201

        res2 = await client.post(
            "/api/v1/changelog",
            json={
                "title": "Release 1.1: Turbo Search",
                "content_markdown": "Instant full-text indexing engine.",
                "category": "IMPROVED",
                "status": "PUBLISHED",
            },
            headers=admin_headers,
        )
        assert res2.status_code == 201

        # Also create 1 DRAFT (must NOT count towards unread)
        res_draft = await client.post(
            "/api/v1/changelog",
            json={
                "title": "Secret Internal Draft",
                "content_markdown": "Not ready for public eyes.",
                "category": "NEW",
                "status": "DRAFT",
            },
            headers=admin_headers,
        )
        assert res_draft.status_code == 201

    print("   ✅ 2 published updates and 1 draft created.")

    # 3. User checks notifications -> unread_count must be 2
    print("3️⃣ User checks notifications (verifying unread count = 2)...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_notif = await client.get("/api/v1/notifications", headers=user_headers)
        assert res_notif.status_code == 200
        data = res_notif.json()
        assert data["unread_count"] == 2, f"Expected 2 unread, got {data['unread_count']}"
        assert len(data["recent_updates"]) == 2
        print(f"   ✅ Unread count accurately calculated: {data['unread_count']}.")

    # 4. User opens drawer -> calls POST /api/v1/notifications/mark-read
    print("4️⃣ User opens drawer (marking notifications as read)...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_read = await client.post("/api/v1/notifications/mark-read", headers=user_headers)
        assert res_read.status_code == 200
        assert res_read.json()["unread_count"] == 0
        print("   ✅ Mark-read API returned unread_count = 0.")

    # 5. User checks notifications again -> unread_count must be 0
    print("5️⃣ Verifying unread count is now 0...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_notif2 = await client.get("/api/v1/notifications", headers=user_headers)
        assert res_notif2.status_code == 200
        data2 = res_notif2.json()
        assert data2["unread_count"] == 0, f"Expected 0 unread, got {data2['unread_count']}"
        assert len(data2["recent_updates"]) == 2  # Recent updates are still visible!
        print("   ✅ Unread count is verified to be 0 while recent updates remain visible.")

    # 6. Admin publishes another update with a future/fresh timestamp
    print("6️⃣ Admin publishes another update (Release 2.0)...")
    await asyncio.sleep(0.01)  # small tick to ensure published_at > user last_viewed_changelog_date
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res3 = await client.post(
            "/api/v1/changelog",
            json={
                "title": "Release 2.0: AI Copilot",
                "content_markdown": "Full AI copilot integrated into product workflows.",
                "category": "NEW",
                "status": "PUBLISHED",
            },
            headers=admin_headers,
        )
        assert res3.status_code == 201

    # 7. User checks notifications again -> unread_count must now be 1
    print("7️⃣ Verifying user's unread count increases back to 1...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_notif3 = await client.get("/api/v1/notifications", headers=user_headers)
        assert res_notif3.status_code == 200
        data3 = res_notif3.json()
        assert data3["unread_count"] == 1, f"Expected 1 unread, got {data3['unread_count']}"
        assert data3["recent_updates"][0]["title"] == "Release 2.0: AI Copilot"
        print(f"   ✅ Unread count successfully incremented back to {data3['unread_count']}!")

    print("\n🎉 ALL NOTIFICATION CENTER TESTS PASSED FLAWLESSLY!\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
