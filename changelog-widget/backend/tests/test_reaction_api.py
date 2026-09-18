"""
tests/test_reaction_api.py
--------------------------
Integration test suite for changelog reactions:
- Authenticated user adds new reaction
- Unique constraint blocks duplicate reaction (409 Conflict)
- Same user can add different reactions (❤️, 🎉, 🚀)
- Multiple users reacting to the same changelog
- User removes their reaction (DELETE /api/v1/reactions/{id})
- Authorization check: user cannot delete another user's reaction
- Anonymous user blocked with 401 Unauthorized
"""

import asyncio
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.config.database import get_database
from app.models.indexes import create_database_indexes


async def run_tests():
    print("🚀 Starting Reaction Integration Tests...\n")

    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["test_reaction_db"]
    await create_database_indexes(mock_db)

    app.dependency_overrides[get_database] = lambda: mock_db

    transport = ASGITransport(app=app)

    # 1. Setup Admin, User 1, User 2
    print("1️⃣ Setting up Users...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # First signup is admin
        res_admin = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Admin Owner", "email": "admin@reaction.com", "password": "AdminPassword123!"},
        )
        assert res_admin.status_code == 201
        admin_token = res_admin.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_u1 = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Alice User", "email": "alice@reaction.com", "password": "AlicePassword123!"},
        )
        assert res_u1.status_code == 201
        u1_token = res_u1.json()["access_token"]
        u1_headers = {"Authorization": f"Bearer {u1_token}"}

    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_u2 = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Bob User", "email": "bob@reaction.com", "password": "BobPassword123!"},
        )
        assert res_u2.status_code == 201
        u2_token = res_u2.json()["access_token"]
        u2_headers = {"Authorization": f"Bearer {u2_token}"}

    print("   ✅ Admin, Alice (User 1), and Bob (User 2) created.")

    # 2. Publish a changelog post
    print("2️⃣ Publishing a changelog post...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_ch = await client.post(
            "/api/v1/changelog",
            json={
                "title": "Exciting AI Workflow Release",
                "content_markdown": "Shipped new autonomous workflows.",
                "category": "NEW",
                "status": "PUBLISHED",
            },
            headers=admin_headers,
        )
        assert res_ch.status_code == 201
        changelog_id = res_ch.json()["id"]
        print(f"   ✅ Published changelog with ID: {changelog_id}")

    # 3. Test: Anonymous user blocked
    print("3️⃣ Testing unauthenticated reaction attempt...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as anon_client:
        res_anon = await anon_client.post(
            "/api/v1/reactions",
            json={"changelog_id": changelog_id, "reaction": "❤️"},
        )
        assert res_anon.status_code == 401
        print("   ✅ Unauthenticated POST blocked with HTTP 401 Unauthorized.")

    # 4. Test: User 1 adds new reaction ❤️
    print("4️⃣ Testing User 1 adding new reaction ❤️...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_r1 = await client.post(
            "/api/v1/reactions",
            json={"changelog_id": changelog_id, "reaction": "❤️"},
            headers=u1_headers,
        )
        assert res_r1.status_code == 201
        u1_heart_reaction_id = res_r1.json()["id"]
        assert res_r1.json()["reaction"] == "❤️"
        assert res_r1.json()["changelog_id"] == changelog_id
        print("   ✅ Reaction created successfully (HTTP 201).")

    # 5. Test: Duplicate reaction from User 1 is blocked (409 Conflict)
    print("5️⃣ Testing duplicate reaction constraint (same user + same changelog + same emoji)...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_dup = await client.post(
            "/api/v1/reactions",
            json={"changelog_id": changelog_id, "reaction": "❤️"},
            headers=u1_headers,
        )
        assert res_dup.status_code == 409
        print(f"   ✅ Duplicate blocked by unique index with HTTP 409: {res_dup.json()['detail']}")

    # 6. Test: Same User 1 adds a different reaction 🎉
    print("6️⃣ Testing User 1 adding different reaction 🎉...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_r2 = await client.post(
            "/api/v1/reactions",
            json={"changelog_id": changelog_id, "reaction": "🎉"},
            headers=u1_headers,
        )
        assert res_r2.status_code == 201
        u1_party_reaction_id = res_r2.json()["id"]
        print("   ✅ Different reaction allowed for same user.")

    # 7. Test: Multiple users (User 2 reacts with ❤️ and 🚀)
    print("7️⃣ Testing multiple users reacting...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_u2_heart = await client.post(
            "/api/v1/reactions",
            json={"changelog_id": changelog_id, "reaction": "❤️"},
            headers=u2_headers,
        )
        assert res_u2_heart.status_code == 201
        u2_heart_reaction_id = res_u2_heart.json()["id"]

        res_u2_rocket = await client.post(
            "/api/v1/reactions",
            json={"changelog_id": changelog_id, "reaction": "🚀"},
            headers=u2_headers,
        )
        assert res_u2_rocket.status_code == 201

    # Check counts & user_reacted for User 1 vs User 2 vs Public
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_summary_u1 = await client.get(
            f"/api/v1/reactions/changelog/{changelog_id}",
            headers=u1_headers,
        )
        assert res_summary_u1.status_code == 200
        summary_map_u1 = {r["reaction"]: r for r in res_summary_u1.json()["reactions"]}
        # ❤️: count=2, Alice reacted=True
        assert summary_map_u1["❤️"]["count"] == 2
        assert summary_map_u1["❤️"]["user_reacted"] is True
        assert summary_map_u1["❤️"]["user_reaction_id"] == u1_heart_reaction_id
        # 🎉: count=1, Alice reacted=True
        assert summary_map_u1["🎉"]["count"] == 1
        assert summary_map_u1["🎉"]["user_reacted"] is True
        # 🚀: count=1, Alice reacted=False
        assert summary_map_u1["🚀"]["count"] == 1
        assert summary_map_u1["🚀"]["user_reacted"] is False
        print("   ✅ Reaction counts and Alice's reacted state verified accurately.")

    # 8. Test: User 1 cannot delete User 2's reaction (403 Forbidden)
    print("8️⃣ Testing ownership check: User 1 cannot delete User 2's reaction...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_steal = await client.delete(
            f"/api/v1/reactions/{u2_heart_reaction_id}",
            headers=u1_headers,
        )
        assert res_steal.status_code == 403
        print("   ✅ Unauthorized deletion rejected with HTTP 403 Forbidden.")

    # 9. Test: User 1 removes their reaction ❤️
    print("9️⃣ Testing User 1 removing their reaction ❤️...")
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        res_del = await client.delete(
            f"/api/v1/reactions/{u1_heart_reaction_id}",
            headers=u1_headers,
        )
        assert res_del.status_code == 200
        print("   ✅ User 1 reaction removed successfully.")

        # Check updated counts: ❤️ count should now be 1 (User 2), and Alice user_reacted=False
        res_summary_after = await client.get(
            f"/api/v1/reactions/changelog/{changelog_id}",
            headers=u1_headers,
        )
        summary_after = {r["reaction"]: r for r in res_summary_after.json()["reactions"]}
        assert summary_after["❤️"]["count"] == 1
        assert summary_after["❤️"]["user_reacted"] is False
        assert summary_after["❤️"]["user_reaction_id"] is None
        print("   ✅ Summary updated immediately: count decremented to 1 and user_reacted is False.")

    print("\n🎉 ALL REACTION TEST SUITES PASSED FLAWLESSLY!\n")


if __name__ == "__main__":
    asyncio.run(run_tests())
