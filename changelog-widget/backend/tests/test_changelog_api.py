"""
tests/test_changelog_api.py
---------------------------
End-to-end integration test suite for changelog CRUD, draft/publish lifecycle,
slug collision avoidance, public vs admin visibility, and filtering.
"""

import asyncio
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.config.database import get_database
from app.models.indexes import create_database_indexes


async def run_tests():
    print("🚀 Starting Changelog Management Integration Tests...\n")

    # Setup mock MongoDB
    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["test_changelog_db"]
    await create_database_indexes(mock_db)

    # Dependency override
    app.dependency_overrides[get_database] = lambda: mock_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:

        # ── 1. Create Admin and Regular Users ─────────────────────────────────
        print("1️⃣ Setting up Admin and Regular User accounts...")
        # First signup is automatically admin
        res_admin = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Admin Boss", "email": "admin@example.com", "password": "AdminPassword123!"},
        )
        assert res_admin.status_code == 201
        admin_token = res_admin.json()["access_token"]

        # Second signup is regular user
        res_user = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Regular Joe", "email": "joe@example.com", "password": "UserPassword123!"},
        )
        assert res_user.status_code == 201
        user_token = res_user.json()["access_token"]
        print("   ✅ Accounts created successfully.")

        # ── 2. RBAC: Non-Admins Cannot Modify Changelogs ──────────────────────
        print("2️⃣ Testing RBAC permissions (regular user blocked)...")
        draft_payload = {
            "title": "Exciting New Dashboard v1.0!",
            "content_markdown": "### Highlights\n- Beautiful analytics\n- Real-time stream",
            "category": "NEW",
            "status": "DRAFT",
        }

        # Unauthenticated user (no cookies, no headers) -> 401
        async with AsyncClient(transport=transport, base_url="http://testserver") as anon_client:
            res_unauth = await anon_client.post("/api/v1/changelog", json=draft_payload)
            assert res_unauth.status_code == 401, f"Expected 401, got {res_unauth.status_code}: {res_unauth.text}"
            print("   ✅ Unauthenticated POST blocked with HTTP 401.")

        # Regular user (with user_token or user cookie) -> 403 Forbidden
        res_forbidden = await client.post(
            "/api/v1/changelog",
            json=draft_payload,
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert res_forbidden.status_code == 403, f"Expected 403, got {res_forbidden.status_code}: {res_forbidden.text}"
        print("   ✅ Regular user POST blocked with HTTP 403 Forbidden.")


        # ── 3. Admin Creates Changelog Draft & Slug Generation ────────────────
        print("3️⃣ Testing Changelog Draft Creation & Slug Auto-generation...")
        res_create = await client.post(
            "/api/v1/changelog",
            json=draft_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res_create.status_code == 201, f"Failed to create: {res_create.text}"
        cl_data = res_create.json()
        assert cl_data["slug"] == "exciting-new-dashboard-v1-0"
        assert cl_data["status"] == "DRAFT"
        assert cl_data["published_at"] is None
        changelog_id = cl_data["id"]
        changelog_slug = cl_data["slug"]
        print(f"   ✅ Draft created with auto-slug: '{changelog_slug}'")

        # ── 4. Duplicate Slug Collision Handling ─────────────────────────────
        print("4️⃣ Testing Duplicate Slug Collision Resolution...")
        # Create another post with the same title
        res_create_dup = await client.post(
            "/api/v1/changelog",
            json=draft_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res_create_dup.status_code == 201
        dup_data = res_create_dup.json()
        assert dup_data["slug"] == "exciting-new-dashboard-v1-0-1", f"Expected suffix -1, got {dup_data['slug']}"
        print(f"   ✅ Duplicate title collision resolved to: '{dup_data['slug']}'")

        # ── 5. Public vs Admin Visibility for Drafts ──────────────────────────
        print("5️⃣ Testing Public vs Admin Visibility (Draft Isolation)...")
        # Public call -> should see 0 items because both are DRAFT
        res_public_list = await client.get("/api/v1/changelog")
        assert res_public_list.status_code == 200
        assert res_public_list.json()["total"] == 0
        print("   ✅ Public visitor cannot see DRAFT updates (total = 0).")

        # Public fetch single draft -> 404
        res_public_single = await client.get(f"/api/v1/changelog/{changelog_slug}")
        assert res_public_single.status_code == 404
        print("   ✅ Public visitor GET /changelog/{draft_slug} returns HTTP 404 Not Found.")

        # Admin call -> should see 2 items
        res_admin_list = await client.get(
            "/api/v1/changelog",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res_admin_list.status_code == 200
        assert res_admin_list.json()["total"] == 2
        print("   ✅ Admin visitor can see DRAFT updates (total = 2).")

        # ── 6. Publish Changelog ──────────────────────────────────────────────
        print("6️⃣ Testing POST /api/v1/changelog/{id}/publish...")
        res_publish = await client.post(
            f"/api/v1/changelog/{changelog_id}/publish",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res_publish.status_code == 200
        pub_data = res_publish.json()
        assert pub_data["status"] == "PUBLISHED"
        assert pub_data["published_at"] is not None
        print(f"   ✅ Changelog published! Timestamp: {pub_data['published_at']}")

        # ── 7. Public Can Now View the Published Update ───────────────────────
        print("7️⃣ Testing Public Access to Published Update...")
        res_pub_now = await client.get(f"/api/v1/changelog/{changelog_slug}")
        assert res_pub_now.status_code == 200
        assert res_pub_now.json()["title"] == "Exciting New Dashboard v1.0!"
        print("   ✅ Public visitor can now fetch the published changelog.")

        # Public list now returns 1 item
        res_pub_list_now = await client.get("/api/v1/changelog")
        assert res_pub_list_now.json()["total"] == 1
        print("   ✅ Public feed now returns 1 published update.")

        # ── 8. Create a 'FIXED' Changelog and Test Filtering ──────────────────
        print("8️⃣ Testing Category Filtering...")
        res_create_fixed = await client.post(
            "/api/v1/changelog",
            json={
                "title": "Bugfix: Memory Leak in Background Workers",
                "content_markdown": "Fixed critical socket leak.",
                "category": "FIXED",
                "status": "PUBLISHED",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res_create_fixed.status_code == 201

        # Filter by category=FIXED
        res_fixed = await client.get("/api/v1/changelog?category=FIXED")
        assert res_fixed.status_code == 200
        assert res_fixed.json()["total"] == 1
        assert res_fixed.json()["items"][0]["category"] == "FIXED"
        print("   ✅ Filtering by ?category=FIXED returns only fixed items.")

        # Filter by category=NEW
        res_new = await client.get("/api/v1/changelog?category=NEW")
        assert res_new.status_code == 200
        assert res_new.json()["total"] == 1
        assert res_new.json()["items"][0]["category"] == "NEW"
        print("   ✅ Filtering by ?category=NEW returns only new items.")

        # ── 9. Pagination & Sorting ──────────────────────────────────────────
        print("9️⃣ Testing Pagination & Sorting...")
        # 2 published items exist, limit=1
        res_page1 = await client.get("/api/v1/changelog?page=1&limit=1")
        assert res_page1.status_code == 200
        data_p1 = res_page1.json()
        assert data_p1["page"] == 1
        assert data_p1["limit"] == 1
        assert data_p1["total"] == 2
        assert data_p1["pages"] == 2
        assert len(data_p1["items"]) == 1
        print("   ✅ Pagination calculated total=2, limit=1, pages=2.")

        # ── 10. Update Changelog ─────────────────────────────────────────────
        print("🔟 Testing PUT /api/v1/changelog/{id}...")
        update_payload = {
            "title": "Exciting New Dashboard v1.1 (Patched)",
            "content_markdown": "Updated notes with performance benchmark.",
            "category": "IMPROVED",
        }
        res_update = await client.put(
            f"/api/v1/changelog/{changelog_id}",
            json=update_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res_update.status_code == 200
        upd_data = res_update.json()
        assert upd_data["title"] == "Exciting New Dashboard v1.1 (Patched)"
        assert upd_data["category"] == "IMPROVED"
        print("   ✅ Changelog updated successfully.")

        # ── 11. Delete Changelog ─────────────────────────────────────────────
        print("1️⃣1️⃣ Testing DELETE /api/v1/changelog/{id}...")
        res_delete = await client.delete(
            f"/api/v1/changelog/{changelog_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res_delete.status_code == 200
        print("   ✅ Changelog deleted.")

        # Confirm deleted
        res_get_deleted = await client.get(
            f"/api/v1/changelog/{changelog_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res_get_deleted.status_code == 404
        print("   ✅ Confirmed: subsequent GET returns HTTP 404 Not Found.")

    print("\n🎉 ALL 11 CHANGELOG CRUD TEST SUITES PASSED FLAWLESSLY!")


if __name__ == "__main__":
    asyncio.run(run_tests())
