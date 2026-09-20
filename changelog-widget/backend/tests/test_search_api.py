"""
tests/test_search_api.py
------------------------
Integration test suite for search functionality across title and content_markdown:
- Case-insensitive search
- Search across title vs content_markdown
- Public vs Admin visibility in search results
- Safe handling of regex special characters
"""

import asyncio
import pytest
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.config.database import get_database
from app.models.indexes import create_database_indexes


@pytest.mark.asyncio
async def test_search_features():
    print("🚀 Starting Search Integration Tests...\n")

    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["test_search_db"]
    await create_database_indexes(mock_db)

    app.dependency_overrides[get_database] = lambda: mock_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Setup Admin Account
        print("1️⃣ Setting up Admin...")
        res_admin = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Admin Tester", "email": "search_admin@example.com", "password": "AdminPassword123!"},
        )
        assert res_admin.status_code == 201
        admin_token = res_admin.cookies.get("access_token")
        assert admin_token is not None
        headers = {"Authorization": f"Bearer {admin_token}"}
        print("   ✅ Admin created successfully.")

        # 2. Seed multiple changelog posts
        print("2️⃣ Seeding multiple changelog updates...")
        posts = [
            {
                "title": "Superfast AI Assistant",
                "content_markdown": "Natural language queries for analytics.",
                "category": "NEW",
                "status": "PUBLISHED",
            },
            {
                "title": "Postgres Database Tuning",
                "content_markdown": "Added caching layer with redis AI accelerator.",
                "category": "IMPROVED",
                "status": "PUBLISHED",
            },
            {
                "title": "Bugfix for Mobile Login",
                "content_markdown": "Resolved issue where virtual keyboard obscured submit button.",
                "category": "FIXED",
                "status": "PUBLISHED",
            },
            {
                "title": "Secret Internal AI Draft",
                "content_markdown": "Work in progress for Q4 AI roadmap.",
                "category": "NEW",
                "status": "DRAFT",
            },
        ]

        for p in posts:
            res = await client.post("/api/v1/changelog", json=p, headers=headers)
            assert res.status_code == 201

        print("   ✅ 4 updates seeded (3 PUBLISHED, 1 DRAFT).")

        # 3. Public search: Case-insensitive 'ai'
        print("3️⃣ Testing public case-insensitive search for 'ai'...")
        async with AsyncClient(transport=transport, base_url="http://testserver") as anon_client:
            res_ai = await anon_client.get("/api/v1/changelog?search=ai")
            assert res_ai.status_code == 200
            data_ai = res_ai.json()
            assert data_ai["total"] == 2, f"Expected 2 matches for 'ai', got {data_ai['total']}"
            titles = [item["title"] for item in data_ai["items"]]
            assert "Superfast AI Assistant" in titles
            assert "Postgres Database Tuning" in titles
            assert "Secret Internal AI Draft" not in titles  # Public visitor must not see drafts
            print(f"   ✅ Public search correctly returned 2 published matches: {titles}")

            # 4. Search in content_markdown: 'keyboard'
            print("4️⃣ Testing search in content_markdown for 'keyboard'...")
            res_kb = await anon_client.get("/api/v1/changelog?search=keyboard")
            assert res_kb.status_code == 200
            data_kb = res_kb.json()
            assert data_kb["total"] == 1
            assert data_kb["items"][0]["title"] == "Bugfix for Mobile Login"
            print("   ✅ Content markdown match succeeded.")

            # 5. Search with no matches
            print("5️⃣ Testing search for non-existent keyword...")
            res_empty = await anon_client.get("/api/v1/changelog?search=NonExistentTermXYZ")
            assert res_empty.status_code == 200
            assert res_empty.json()["total"] == 0
            print("   ✅ Returned empty list gracefully.")

        # 6. Admin search: Can see matching DRAFT
        print("6️⃣ Testing Admin search for 'ai'...")
        res_admin_ai = await client.get("/api/v1/changelog?search=ai", headers=headers)
        assert res_admin_ai.status_code == 200
        assert res_admin_ai.json()["total"] == 3  # 2 published + 1 draft
        print("   ✅ Admin search correctly includes drafts (3 total).")

        # 7. Safe regex search with special characters
        print("7️⃣ Testing search with regex special characters like '[', '(', '*'...")
        res_special = await client.get("/api/v1/changelog?search=[test]+(regex)*")
        assert res_special.status_code == 200
        assert res_special.json()["total"] == 0
        print("   ✅ Special characters handled safely without regex compilation crashes.")

    print("\n🎉 ALL SEARCH INTEGRATION TESTS PASSED FLAWLESSLY!\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
