"""
tests/test_complete_suite.py
----------------------------
STEP 17: Master End-to-End Test Suite covering all features and edge cases:
- AUTH (Signup, Login, Logout, Refresh, Forgot/Reset Password, Admin Protection)
- CHANGELOG (Create, Read, Update, Delete, Draft, Publish)
- PUBLIC (Timeline, Category Filters, Search, Details)
- REACTIONS (❤️, 🎉, 🚀, Duplicate Prevention, Remove, Aggregation)
- NOTIFICATIONS (Unread Count, Mark as Read, New Update Increment)
- FEED (Public JSON Feed, Cache-Control, Reverse-Chronological, Pagination)
- NEGATIVE & EDGE CASES:
  * Invalid Input (Malformed schemas, bad email, bad category, invalid emoji, unsafe cover URL)
  * Unauthorized Requests (Missing tokens, forged tokens)
  * Expired Tokens (Tokens past expiration date)
  * Nonexistent IDs (Changelogs, Reactions)
  * Duplicate Data (Duplicate emails, duplicate reactions, slug auto-increments)
  * Empty Database (Timeline, Feed, Notifications, Search)
  * Invalid Image Upload (MIME types, empty files, oversized files, permission checks)
  * Database & Server Health Checks (/health, error handling)
"""

import asyncio
from datetime import datetime, timedelta, timezone
import io
import os
import shutil
from bson import ObjectId
from httpx import ASGITransport, AsyncClient
from jose import jwt
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.config.database import get_database
from app.config.settings import settings
from app.models.indexes import create_database_indexes


async def run_master_suite():
    print("=" * 70)
    print("🚀 STEP 17 — COMPREHENSIVE END-TO-END MASTER TEST SUITE")
    print("=" * 70 + "\n")

    # 1. Setup mock MongoDB
    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["test_master_changelog_db"]
    await create_database_indexes(mock_db)
    app.dependency_overrides[get_database] = lambda: mock_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:

        # ──────────────────────────────────────────────────────────────────────
        # SECTION 1: EMPTY DATABASE BEHAVIOR
        # ──────────────────────────────────────────────────────────────────────
        print("📁 [SECTION 1] Testing Empty Database Behavior...")
        
        # 1.1 Empty Timeline
        res = await client.get("/api/v1/changelog")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["items"] == []
        print("   ✅ Empty timeline returns total=0, items=[]")

        # 1.2 Empty Public Feed
        res = await client.get("/api/v1/changelog/feed")
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["updates"] == []
        print("   ✅ Empty public feed returns total=0, updates=[]")

        # 1.3 Empty Notifications
        res = await client.get("/api/v1/notifications")
        assert res.status_code == 200
        data = res.json()
        assert data["unread_count"] == 0
        assert data["recent_updates"] == []
        print("   ✅ Empty notifications returns unread_count=0, recent_updates=[]")

        # 1.4 Search on empty DB
        res = await client.get("/api/v1/changelog?search=anything")
        assert res.status_code == 200
        assert res.json()["total"] == 0
        print("   ✅ Search on empty DB returns total=0 gracefully")

        # ──────────────────────────────────────────────────────────────────────
        # SECTION 2: AUTHENTICATION & AUTHORIZATION
        # ──────────────────────────────────────────────────────────────────────
        print("\n🔐 [SECTION 2] Testing Authentication & Authorization...")

        # 2.1 First user signup -> Admin
        client.cookies.clear()
        admin_payload = {
            "name": "Super Admin",
            "email": "admin@mastertest.com",
            "password": "MasterAdmin123!",
        }
        res_admin = await client.post("/api/v1/auth/signup", json=admin_payload)
        assert res_admin.status_code == 201
        admin_data = res_admin.json()
        assert admin_data["user"]["role"] == "admin"
        admin_token = admin_data["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("   ✅ Admin registered successfully (role=admin)")

        # 2.2 Second user signup -> Regular User
        client.cookies.clear()
        user_payload = {
            "name": "Jane User",
            "email": "jane@mastertest.com",
            "password": "JanePassword123!",
        }
        res_user = await client.post("/api/v1/auth/signup", json=user_payload)
        assert res_user.status_code == 201
        user_data = res_user.json()
        assert user_data["user"]["role"] == "user"
        user_token = user_data["access_token"]
        user_refresh_token = user_data["refresh_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        print("   ✅ Regular user registered successfully (role=user)")

        # 2.3 Duplicate email signup conflict (409)
        res_dup = await client.post("/api/v1/auth/signup", json=user_payload)
        assert res_dup.status_code == 409
        print("   ✅ Duplicate email rejected with HTTP 409 Conflict")

        # 2.4 Login with invalid password (401)
        res_bad_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "jane@mastertest.com", "password": "WrongPassword!"},
        )
        assert res_bad_login.status_code == 401
        print("   ✅ Invalid credentials rejected with HTTP 401")

        # 2.5 Login with valid credentials (200)
        client.cookies.clear()
        res_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "jane@mastertest.com", "password": "JanePassword123!"},
        )
        assert res_login.status_code == 200
        assert "access_token" in res_login.json()
        print("   ✅ Valid login returned access token & cookies")

        # 2.6 GET /api/v1/auth/me
        res_me = await client.get("/api/v1/auth/me", headers=user_headers)
        assert res_me.status_code == 200
        assert res_me.json()["email"] == "jane@mastertest.com"
        print("   ✅ GET /api/v1/auth/me succeeded")

        # 2.7 Token Refresh & Token Rotation
        res_refresh = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": user_refresh_token},
        )
        assert res_refresh.status_code == 200
        new_tokens = res_refresh.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        print("   ✅ Refresh token rotated successfully")

        # 2.8 Reusing old refresh token -> 401
        res_reuse = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": user_refresh_token},
        )
        assert res_reuse.status_code == 401
        print("   ✅ Revoked refresh token reuse blocked with HTTP 401")

        # 2.9 Forgot Password & Reset Password
        res_forgot = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "jane@mastertest.com"},
        )
        assert res_forgot.status_code == 200
        sim_token = res_forgot.json().get("reset_token")
        if sim_token:
            res_reset = await client.post(
                "/api/v1/auth/reset-password",
                json={"token": sim_token, "new_password": "NewJanePassword123!"},
            )
            assert res_reset.status_code == 200
            print("   ✅ Forgot & reset password flow succeeded")

        # 2.10 Admin Protection Guard (RBAC)
        # Regular user trying admin endpoint -> 403
        res_forbidden = await client.post(
            "/api/v1/changelog",
            json={"title": "Hacked", "category": "NEW", "content_markdown": "test"},
            headers=user_headers,
        )
        assert res_forbidden.status_code == 403
        print("   ✅ Non-admin user blocked from admin action with HTTP 403 Forbidden")

        # 2.11 Logout
        res_logout = await client.post("/api/v1/auth/logout", headers=user_headers)
        assert res_logout.status_code == 200
        print("   ✅ Logout succeeded")

        # ──────────────────────────────────────────────────────────────────────
        # SECTION 3: CHANGELOG CRUD, DRAFTS & PUBLISHING
        # ──────────────────────────────────────────────────────────────────────
        print("\n📝 [SECTION 3] Testing Changelog CRUD, Drafts & Publishing...")

        # 3.1 Create Draft Changelog
        draft_payload = {
            "title": "Quantum Speed AI v1.0",
            "content_markdown": "## Major Speed Boost\n\nExperience **instant** answers.",
            "category": "NEW",
            "cover_image": "https://images.unsplash.com/photo-1550745165-9bc0b252726f",
            "status": "DRAFT",
        }
        res_create = await client.post("/api/v1/changelog", json=draft_payload, headers=admin_headers)
        assert res_create.status_code == 201
        draft_cl = res_create.json()
        assert draft_cl["status"] == "DRAFT"
        assert draft_cl["slug"] == "quantum-speed-ai-v1-0"
        draft_id = draft_cl["id"]
        draft_slug = draft_cl["slug"]
        print(f"   ✅ Draft created with slug: {draft_slug}")

        # 3.2 Duplicate Title -> Unique Slug Auto-increment
        res_dup_title = await client.post("/api/v1/changelog", json=draft_payload, headers=admin_headers)
        assert res_dup_title.status_code == 201
        assert res_dup_title.json()["slug"] == "quantum-speed-ai-v1-0-1"
        print("   ✅ Duplicate title resolved to auto-incremented slug: quantum-speed-ai-v1-0-1")

        # Clean up duplicate draft
        await client.delete(f"/api/v1/changelog/{res_dup_title.json()['id']}", headers=admin_headers)

        # 3.3 Draft Isolation: Public cannot view draft
        client.cookies.clear()
        res_public_list = await client.get("/api/v1/changelog")
        assert res_public_list.json()["total"] == 0

        res_public_slug = await client.get(f"/api/v1/changelog/{draft_slug}")
        assert res_public_slug.status_code == 404
        print("   ✅ Drafts strictly invisible to public visitors (returns 404)")

        # 3.4 Admin can view draft
        res_admin_slug = await client.get(f"/api/v1/changelog/{draft_slug}", headers=admin_headers)
        assert res_admin_slug.status_code == 200
        print("   ✅ Admin can view draft post")

        # 3.5 Update Changelog
        update_payload = {
            "title": "Quantum Speed AI v1.1 Updated",
            "content_markdown": "## Updated speed improvements\nNow with 15x faster retrieval!",
            "category": "IMPROVED",
        }
        res_update = await client.put(f"/api/v1/changelog/{draft_id}", json=update_payload, headers=admin_headers)
        assert res_update.status_code == 200
        assert res_update.json()["title"] == "Quantum Speed AI v1.1 Updated"
        assert res_update.json()["category"] == "IMPROVED"
        print("   ✅ Changelog updated successfully")

        # 3.6 Publish Changelog
        res_pub = await client.post(f"/api/v1/changelog/{draft_id}/publish", headers=admin_headers)
        assert res_pub.status_code == 200
        published_cl = res_pub.json()
        assert published_cl["status"] == "PUBLISHED"
        assert published_cl["published_at"] is not None
        pub_slug = published_cl["slug"]
        print("   ✅ Changelog published! Timestamp assigned.")

        # 3.7 Public access after publish
        res_pub_view = await client.get(f"/api/v1/changelog/{pub_slug}")
        assert res_pub_view.status_code == 200
        assert res_pub_view.json()["id"] == draft_id
        print("   ✅ Public visitor can view published changelog by slug")

        # Create a second published post (FIXED category) for filtering/reactions
        res_fix = await client.post(
            "/api/v1/changelog",
            json={
                "title": "Critical Security Patch",
                "content_markdown": "Resolved token replay edge case in authentication.",
                "category": "FIXED",
                "status": "PUBLISHED",
            },
            headers=admin_headers,
        )
        assert res_fix.status_code == 201
        fix_id = res_fix.json()["id"]
        print("   ✅ Second post created (category=FIXED, status=PUBLISHED)")

        # ──────────────────────────────────────────────────────────────────────
        # SECTION 4: PUBLIC TIMELINE, FILTERS & SEARCH
        # ──────────────────────────────────────────────────────────────────────
        print("\n🔍 [SECTION 4] Testing Public Timeline, Filters & Search...")

        # 4.1 Timeline list (both published posts visible)
        res_tl = await client.get("/api/v1/changelog")
        assert res_tl.status_code == 200
        assert res_tl.json()["total"] == 2
        print("   ✅ Public timeline returns all published posts (total=2)")

        # 4.2 Category Filter (?category=FIXED)
        res_fixed = await client.get("/api/v1/changelog?category=FIXED")
        assert res_fixed.status_code == 200
        assert res_fixed.json()["total"] == 1
        assert res_fixed.json()["items"][0]["category"] == "FIXED"
        print("   ✅ Filtering by category=FIXED returns only fixed items")

        # 4.3 Category Filter (?category=IMPROVED)
        res_imp = await client.get("/api/v1/changelog?category=IMPROVED")
        assert res_imp.status_code == 200
        assert res_imp.json()["total"] == 1
        assert res_imp.json()["items"][0]["category"] == "IMPROVED"
        print("   ✅ Filtering by category=IMPROVED returns only improved items")

        # 4.4 Search by Title
        res_search_title = await client.get("/api/v1/changelog?search=Quantum")
        assert res_search_title.status_code == 200
        assert res_search_title.json()["total"] == 1
        print("   ✅ Search in title returns matching result")

        # 4.5 Search in Markdown Content
        res_search_content = await client.get("/api/v1/changelog?search=replay")
        assert res_search_content.status_code == 200
        assert res_search_content.json()["total"] == 1
        print("   ✅ Search in content_markdown returns matching result")

        # 4.6 Case-Insensitive Search
        res_search_lower = await client.get("/api/v1/changelog?search=quantum")
        assert res_search_lower.status_code == 200
        assert res_search_lower.json()["total"] == 1
        print("   ✅ Case-insensitive search verified")

        # 4.7 Search with Regex Special Characters
        res_regex = await client.get("/api/v1/changelog?search=[a-z]*")
        assert res_regex.status_code == 200
        print("   ✅ Regex special characters handled safely without ReDoS crashes")

        # ──────────────────────────────────────────────────────────────────────
        # SECTION 5: REACTIONS (❤️, 🎉, 🚀)
        # ──────────────────────────────────────────────────────────────────────
        print("\n💖 [SECTION 5] Testing Emoji Reactions (❤️, 🎉, 🚀)...")

        # 5.1 Unauthenticated reaction -> 401
        client.cookies.clear()
        res_unauth_react = await client.post(
            "/api/v1/reactions",
            json={"changelog_id": draft_id, "reaction": "❤️"},
        )
        assert res_unauth_react.status_code == 401
        print("   ✅ Unauthenticated reaction rejected with HTTP 401")

        # 5.2 Regular User adds reaction ❤️
        res_react_1 = await client.post(
            "/api/v1/reactions",
            json={"changelog_id": draft_id, "reaction": "❤️"},
            headers=user_headers,
        )
        assert res_react_1.status_code == 201
        reaction_1_id = res_react_1.json()["id"]
        print("   ✅ User 1 added reaction ❤️")

        # 5.3 Duplicate reaction prevention (409)
        res_dup_react = await client.post(
            "/api/v1/reactions",
            json={"changelog_id": draft_id, "reaction": "❤️"},
            headers=user_headers,
        )
        assert res_dup_react.status_code == 409
        print("   ✅ Duplicate reaction blocked with HTTP 409 Conflict")

        # 5.4 User adds different reaction 🎉 to same post
        res_react_2 = await client.post(
            "/api/v1/reactions",
            json={"changelog_id": draft_id, "reaction": "🎉"},
            headers=user_headers,
        )
        assert res_react_2.status_code == 201
        print("   ✅ User added different reaction 🎉 to same post")

        # 5.5 Admin user reacts with 🚀
        res_admin_react = await client.post(
            "/api/v1/reactions",
            json={"changelog_id": draft_id, "reaction": "🚀"},
            headers=admin_headers,
        )
        assert res_admin_react.status_code == 201
        print("   ✅ User 2 (Admin) added reaction 🚀")

        # 5.6 Verify Reaction Summary
        res_summary = await client.get(f"/api/v1/reactions/changelog/{draft_id}", headers=user_headers)
        assert res_summary.status_code == 200
        summary_data = res_summary.json()
        counts = {r["reaction"]: r["count"] for r in summary_data["reactions"]}
        assert sum(counts.values()) == 3
        assert counts["❤️"] == 1
        assert counts["🎉"] == 1
        assert counts["🚀"] == 1
        # Check user_reacted flags for User 1
        user_flags = {r["reaction"]: r["user_reacted"] for r in summary_data["reactions"]}
        assert user_flags["❤️"] is True
        assert user_flags["🎉"] is True
        assert user_flags["🚀"] is False  # Added by Admin, not User 1
        print("   ✅ Reaction aggregation and user_reacted states accurately verified")

        # 5.7 Ownership Protection: User cannot delete Admin's reaction
        res_unauth_del = await client.delete(
            f"/api/v1/reactions/{res_admin_react.json()['id']}",
            headers=user_headers,
        )
        assert res_unauth_del.status_code == 403
        print("   ✅ Unauthorized reaction deletion rejected with HTTP 403")

        # 5.8 Remove Reaction
        res_del_react = await client.delete(f"/api/v1/reactions/{reaction_1_id}", headers=user_headers)
        assert res_del_react.status_code == 200
        # Verify count decreased
        res_summary_after = await client.get(f"/api/v1/reactions/changelog/{draft_id}", headers=user_headers)
        after_counts = {r["reaction"]: r["count"] for r in res_summary_after.json()["reactions"]}
        assert sum(after_counts.values()) == 2
        print("   ✅ User successfully removed reaction; summary updated")

        # ──────────────────────────────────────────────────────────────────────
        # SECTION 6: WHAT'S NEW NOTIFICATION CENTER
        # ──────────────────────────────────────────────────────────────────────
        print("\n🔔 [SECTION 6] Testing Notifications & Unread Counts...")

        # 6.1 Check unread notifications as regular user
        res_notif = await client.get("/api/v1/notifications", headers=user_headers)
        assert res_notif.status_code == 200
        notif_data = res_notif.json()
        assert notif_data["unread_count"] == 2
        assert len(notif_data["recent_updates"]) == 2
        print(f"   ✅ Initial unread count verified: {notif_data['unread_count']}")

        # 6.2 Mark notifications as read (drawer opened)
        res_read = await client.post("/api/v1/notifications/mark-read", headers=user_headers)
        assert res_read.status_code == 200
        assert res_read.json()["unread_count"] == 0
        print("   ✅ Mark-read reset unread count to 0")

        # 6.3 Subsequent fetch shows 0 unread
        res_notif_0 = await client.get("/api/v1/notifications", headers=user_headers)
        assert res_notif_0.json()["unread_count"] == 0
        print("   ✅ Subsequent check confirms unread count is 0")

        # 6.4 Admin publishes another update
        await client.post(
            "/api/v1/changelog",
            json={
                "title": "Brand New Notification Feature",
                "content_markdown": "Now get notified about product releases in real-time.",
                "category": "NEW",
                "status": "PUBLISHED",
            },
            headers=admin_headers,
        )

        # 6.5 User unread count increments back to 1
        res_notif_inc = await client.get("/api/v1/notifications", headers=user_headers)
        assert res_notif_inc.json()["unread_count"] == 1
        print("   ✅ Unread count automatically incremented to 1 on new publish")

        # ──────────────────────────────────────────────────────────────────────
        # SECTION 7: PUBLIC JSON FEED
        # ──────────────────────────────────────────────────────────────────────
        print("\n📡 [SECTION 7] Testing Public JSON Feed (GET /api/v1/changelog/feed)...")

        client.cookies.clear()
        res_feed = await client.get("/api/v1/changelog/feed")
        assert res_feed.status_code == 200
        feed_data = res_feed.json()
        assert "updates" in feed_data
        assert feed_data["total"] == 3
        # Verify reverse-chronological order
        pub_dates = [item["published_at"] for item in feed_data["updates"]]
        assert pub_dates == sorted(pub_dates, reverse=True)
        # Verify Cache-Control header
        assert "public" in res_feed.headers.get("cache-control", "")
        print("   ✅ Public feed returned 200 without auth, properly sorted with Cache-Control")

        # ──────────────────────────────────────────────────────────────────────
        # SECTION 8: NEGATIVE TESTING & EDGE CASES
        # ──────────────────────────────────────────────────────────────────────
        print("\n⚠️ [SECTION 8] Testing Negative Cases & Robustness...")

        # 8.1 Invalid Input: Invalid Email Format
        res_bad_email = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Bad", "email": "not-a-valid-email", "password": "Password123!"},
        )
        assert res_bad_email.status_code == 422
        print("   ✅ Invalid email format rejected with HTTP 422")

        # 8.2 Invalid Input: Weak/Short Password (<8 chars)
        res_short_pwd = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Bad", "email": "shortpwd@example.com", "password": "short"},
        )
        assert res_short_pwd.status_code == 422
        print("   ✅ Short password rejected with HTTP 422")

        # 8.3 Invalid Input: Bad Changelog Category
        res_bad_cat = await client.post(
            "/api/v1/changelog",
            json={"title": "Valid Title", "category": "INVALID_CATEGORY", "content_markdown": "test"},
            headers=admin_headers,
        )
        assert res_bad_cat.status_code == 422
        print("   ✅ Bad changelog category rejected with HTTP 422")

        # 8.4 Invalid Input: Malicious javascript: URL in cover_image
        res_xss_url = await client.post(
            "/api/v1/changelog",
            json={
                "title": "XSS Attempt",
                "category": "NEW",
                "content_markdown": "test",
                "cover_image": "javascript:alert(document.cookie)",
            },
            headers=admin_headers,
        )
        assert res_xss_url.status_code == 422
        print("   ✅ Malicious javascript: scheme rejected with HTTP 422")

        # 8.5 Invalid Input: Invalid Reaction Emoji
        res_bad_emoji = await client.post(
            "/api/v1/reactions",
            json={"changelog_id": draft_id, "reaction": "💀"},
            headers=user_headers,
        )
        assert res_bad_emoji.status_code == 422
        print("   ✅ Invalid reaction emoji rejected with HTTP 422")

        # 8.6 Invalid Input: Negative Page Number
        res_neg_page = await client.get("/api/v1/changelog?page=-1")
        assert res_neg_page.status_code == 422
        print("   ✅ Negative page number (?page=-1) rejected with HTTP 422")

        # 8.7 Unauthorized Requests: Access /me with invalid token signature
        bad_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.tampered_signature"
        res_tampered = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {bad_token}"})
        assert res_tampered.status_code == 401
        print("   ✅ Tampered JWT signature rejected with HTTP 401")

        # 8.8 Expired Tokens: Token with exp timestamp in past
        expired_payload = {
            "sub": str(ObjectId()),
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        expired_token = jwt.encode(expired_payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        res_expired = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
        assert res_expired.status_code == 401
        print("   ✅ Expired access token rejected with HTTP 401")

        # 8.9 Nonexistent IDs: GET non-existent changelog ID
        nonexistent_id = str(ObjectId())
        res_404_get = await client.get(f"/api/v1/changelog/{nonexistent_id}")
        assert res_404_get.status_code == 404
        print("   ✅ Nonexistent changelog GET returns HTTP 404")

        # 8.10 Nonexistent IDs: PUT non-existent changelog ID
        res_404_put = await client.put(
            f"/api/v1/changelog/{nonexistent_id}",
            json={"title": "Does Not Exist"},
            headers=admin_headers,
        )
        assert res_404_put.status_code == 404
        print("   ✅ Nonexistent changelog PUT returns HTTP 404")

        # 8.11 Nonexistent IDs: DELETE non-existent changelog ID
        res_404_del = await client.delete(f"/api/v1/changelog/{nonexistent_id}", headers=admin_headers)
        assert res_404_del.status_code == 404
        print("   ✅ Nonexistent changelog DELETE returns HTTP 404")

        # 8.12 Nonexistent IDs: React to non-existent changelog ID
        res_404_react = await client.post(
            "/api/v1/reactions",
            json={"changelog_id": nonexistent_id, "reaction": "❤️"},
            headers=user_headers,
        )
        assert res_404_react.status_code == 404
        print("   ✅ Reaction on nonexistent changelog returns HTTP 404")

        # 8.13 Nonexistent IDs: Delete non-existent reaction ID
        res_404_del_react = await client.delete(f"/api/v1/reactions/{nonexistent_id}", headers=user_headers)
        assert res_404_del_react.status_code == 404
        print("   ✅ Nonexistent reaction DELETE returns HTTP 404")

        # 8.14 Invalid ObjectId Format Handling
        res_bad_oid = await client.put(
            "/api/v1/changelog/not-a-valid-object-id",
            json={"title": "Bad ID"},
            headers=admin_headers,
        )
        assert res_bad_oid.status_code == 400
        print("   ✅ Malformed changelog ID returns HTTP 400")

        # ──────────────────────────────────────────────────────────────────────
        # SECTION 9: IMAGE ATTACHMENTS & UPLOAD VALIDATION
        # ──────────────────────────────────────────────────────────────────────
        print("\n🖼️ [SECTION 9] Testing Image Upload & Validation...")
        png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"

        # 9.1 Valid PNG upload as admin
        files = {"file": ("cover.png", io.BytesIO(png_bytes), "image/png")}
        res_up = await client.post("/api/v1/upload/image", files=files, headers=admin_headers)
        assert res_up.status_code == 201
        upload_data = res_up.json()
        assert "url" in upload_data
        image_url = upload_data["url"]
        uploaded_filename = upload_data["filename"]
        print(f"   ✅ Admin uploaded image successfully. URL: {image_url}")

        # 9.2 Retrieve uploaded image from static URL
        res_img_get = await client.get(image_url)
        assert res_img_get.status_code == 200
        assert res_img_get.content == png_bytes
        print("   ✅ Uploaded static image fetched and matches original content")

        # Clean up disk file
        disk_file = os.path.join(settings.upload_dir, uploaded_filename)
        if os.path.exists(disk_file):
            os.remove(disk_file)

        # 9.3 Invalid image type (text/plain)
        files_bad = {"file": ("malicious.txt", io.BytesIO(b"malicious script"), "text/plain")}
        res_bad_img = await client.post("/api/v1/upload/image", files=files_bad, headers=admin_headers)
        assert res_bad_img.status_code == 415
        print("   ✅ Invalid file type rejected with HTTP 415 Unsupported Media Type")

        # 9.4 Empty file (0 bytes)
        files_empty = {"file": ("empty.jpg", io.BytesIO(b""), "image/jpeg")}
        res_empty_img = await client.post("/api/v1/upload/image", files=files_empty, headers=admin_headers)
        assert res_empty_img.status_code == 400
        print("   ✅ Empty file upload rejected with HTTP 400 Bad Request")

        # 9.5 Oversized file (> 5MB)
        huge_bytes = b"0" * (6 * 1024 * 1024)
        files_huge = {"file": ("huge.png", io.BytesIO(huge_bytes), "image/png")}
        res_huge_img = await client.post("/api/v1/upload/image", files=files_huge, headers=admin_headers)
        assert res_huge_img.status_code == 413
        print("   ✅ Oversized file rejected with HTTP 413 Payload Too Large")

        # 9.6 Unauthenticated upload
        client.cookies.clear()
        res_unauth_img = await client.post(
            "/api/v1/upload/image",
            files={"file": ("unauth.png", io.BytesIO(png_bytes), "image/png")},
        )
        assert res_unauth_img.status_code == 401
        print("   ✅ Unauthenticated upload rejected with HTTP 401")

        # 9.7 Non-admin upload
        res_nonadmin_img = await client.post(
            "/api/v1/upload/image",
            files={"file": ("user.png", io.BytesIO(png_bytes), "image/png")},
            headers=user_headers,
        )
        assert res_nonadmin_img.status_code == 403
        print("   ✅ Non-admin user upload rejected with HTTP 403 Forbidden")

        # ──────────────────────────────────────────────────────────────────────
        # SECTION 10: SERVER HEALTH & ERROR RESILIENCE
        # ──────────────────────────────────────────────────────────────────────
        print("\n🏥 [SECTION 10] Testing Server Health & Error Resilience...")

        # 10.1 Root endpoint
        res_root = await client.get("/")
        assert res_root.status_code == 200
        assert res_root.json()["message"] == "Changelog API is running"
        print("   ✅ Root / endpoint is healthy")

        # 10.2 /health endpoint
        res_health = await client.get("/health")
        assert res_health.status_code == 200
        health_data = res_health.json()
        assert health_data["status"] == "healthy"
        assert health_data["database"]["status"] == "connected"
        print("   ✅ Health endpoint reports healthy status & database connected")

        # 10.3 Delete Changelog with associated reactions cleanup
        res_del_final = await client.delete(f"/api/v1/changelog/{draft_id}", headers=admin_headers)
        assert res_del_final.status_code == 200
        # Verify subsequent GET returns 404
        assert (await client.get(f"/api/v1/changelog/{draft_id}")).status_code == 404
        # Verify associated reactions were cleaned up
        res_reactions_gone = await client.get(f"/api/v1/reactions/changelog/{draft_id}")
        assert sum(r["count"] for r in res_reactions_gone.json()["reactions"]) == 0
        print("   ✅ Changelog deleted and cascading reaction cleanup confirmed")

    app.dependency_overrides.clear()
    print("\n" + "=" * 70)
    print("🏆 ALL 45+ STEP 17 E2E INTEGRATION & EDGE CASE TESTS PASSED!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(run_master_suite())
