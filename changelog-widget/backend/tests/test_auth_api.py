"""
tests/test_auth_api.py
----------------------
End-to-end integration test suite for authentication endpoints using mongomock-motor.
"""

import asyncio
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.config.database import get_database
from app.models.indexes import create_database_indexes


async def run_tests():
    print("🚀 Starting Authentication Integration Tests...\n")

    # 1. Setup mock MongoDB
    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["test_changelog_db"]

    # Ensure indexes
    await create_database_indexes(mock_db)

    # Dependency override for FastAPI get_database
    app.dependency_overrides[get_database] = lambda: mock_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:

        # ── Test 1: Signup User ──────────────────────────────────────────────
        print("1️⃣ Testing POST /api/v1/auth/signup (Regular User)...")
        signup_payload = {
            "name": "Bob User",
            "email": "bob@example.com",
            "password": "Password123!",
        }
        # First user is admin by design; let's create admin first then regular user
        admin_signup = {
            "name": "Admin Boss",
            "email": "admin@example.com",
            "password": "AdminPassword123!",
        }
        res_admin = await client.post("/api/v1/auth/signup", json=admin_signup)
        assert res_admin.status_code == 201, f"Admin signup failed: {res_admin.text}"
        admin_data = res_admin.json()
        assert admin_data["user"]["role"] == "admin"
        assert "access_token" in admin_data
        assert "refresh_token" in admin_data
        admin_token = admin_data["access_token"]
        print("   ✅ First user registered as ADMIN successfully.")

        res_user = await client.post("/api/v1/auth/signup", json=signup_payload)
        assert res_user.status_code == 201, f"User signup failed: {res_user.text}"
        user_data = res_user.json()
        assert user_data["user"]["role"] == "user"
        assert user_data["user"]["email"] == "bob@example.com"
        assert user_data["user"]["email_verified"] is False
        verification_token = res_user.headers.get("x-email-verification-token")
        assert verification_token is not None, "Verification token missing in headers"
        user_access_token = user_data["access_token"]
        user_refresh_token = user_data["refresh_token"]

        # Check cookies
        assert "access_token" in res_user.cookies
        assert "refresh_token" in res_user.cookies
        print("   ✅ Regular user registered successfully with httpOnly cookies.")

        # ── Test 2: Duplicate Signup (409 Conflict) ──────────────────────────
        print("2️⃣ Testing Duplicate Signup Conflict (409)...")
        res_dup = await client.post("/api/v1/auth/signup", json=signup_payload)
        assert res_dup.status_code == 409, f"Expected 409, got {res_dup.status_code}"
        print("   ✅ Duplicate email rejected with HTTP 409 Conflict.")

        # ── Test 3: Verify Email Simulation ──────────────────────────────────
        print("3️⃣ Testing POST /api/v1/auth/verify-email...")
        res_verif = await client.post("/api/v1/auth/verify-email", json={"token": verification_token})
        assert res_verif.status_code == 200, f"Email verification failed: {res_verif.text}"
        assert res_verif.json()["email_verified"] is True
        print("   ✅ Email successfully verified via simulation token.")

        # ── Test 4: Login ────────────────────────────────────────────────────
        print("4️⃣ Testing POST /api/v1/auth/login...")
        # 4a. Wrong password -> 401
        res_bad = await client.post(
            "/api/v1/auth/login",
            json={"email": "bob@example.com", "password": "WrongPassword!"},
        )
        assert res_bad.status_code == 401
        print("   ✅ Invalid password rejected with HTTP 401.")

        # 4b. Valid password -> 200
        res_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "bob@example.com", "password": "Password123!"},
        )
        assert res_login.status_code == 200
        login_data = res_login.json()
        user_access_token = login_data["access_token"]
        user_refresh_token = login_data["refresh_token"]
        assert "access_token" in res_login.cookies
        print("   ✅ Valid login succeeded; cookies and tokens returned.")

        # ── Test 5: GET /api/v1/auth/me ──────────────────────────────────────
        print("5️⃣ Testing GET /api/v1/auth/me...")
        # Via Bearer Header
        res_me_header = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {user_access_token}"},
        )
        assert res_me_header.status_code == 200
        assert res_me_header.json()["email"] == "bob@example.com"
        print("   ✅ /me retrieved using Authorization: Bearer header.")

        # Via Cookie
        client.cookies.set("access_token", user_access_token)
        res_me_cookie = await client.get("/api/v1/auth/me")
        assert res_me_cookie.status_code == 200
        assert res_me_cookie.json()["name"] == "Bob User"
        print("   ✅ /me retrieved using httpOnly cookie.")

        # ── Test 6: Refresh Token & Rotation ─────────────────────────────────
        print("6️⃣ Testing POST /api/v1/auth/refresh (Token Rotation)...")
        client.cookies.set("refresh_token", user_refresh_token)
        res_refresh = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": user_refresh_token},
        )
        assert res_refresh.status_code == 200
        refresh_data = res_refresh.json()
        new_access = refresh_data["access_token"]
        new_refresh = refresh_data["refresh_token"]
        assert new_refresh != user_refresh_token, "Refresh token was not rotated!"
        print("   ✅ Token rotated: new access + refresh token pair issued.")

        # Test reuse of old refresh token (should be rejected)
        res_reuse = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": user_refresh_token},
        )
        assert res_reuse.status_code == 401, "Old revoked refresh token was accepted!"
        print("   ✅ Reusing revoked refresh token rejected with HTTP 401.")

        # ── Test 7: Role-Based Access Control (Admin Check) ───────────────────
        print("7️⃣ Testing Admin Authorization (RBAC)...")
        # Regular user attempt -> 403 Forbidden
        res_forbidden = await client.get(
            "/api/v1/auth/admin-check",
            headers={"Authorization": f"Bearer {new_access}"},
        )
        assert res_forbidden.status_code == 403
        print("   ✅ Non-admin user blocked from admin endpoint with HTTP 403 Forbidden.")

        # Admin user attempt -> 200 OK
        res_admin_check = await client.get(
            "/api/v1/auth/admin-check",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert res_admin_check.status_code == 200
        print("   ✅ Admin user permitted with HTTP 200 OK.")

        # ── Test 8: Forgot Password & Reset Flow ─────────────────────────────
        print("8️⃣ Testing Forgot Password & Reset Flow...")
        res_forgot = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "bob@example.com"},
        )
        assert res_forgot.status_code == 200
        reset_token = res_forgot.json()["simulation_token"]
        assert reset_token is not None

        # Reset password
        res_reset = await client.post(
            "/api/v1/auth/reset-password",
            json={"token": reset_token, "new_password": "BrandNewPassword123!"},
        )
        assert res_reset.status_code == 200
        print("   ✅ Password successfully reset.")

        # Verify old password fails
        res_old_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "bob@example.com", "password": "Password123!"},
        )
        assert res_old_login.status_code == 401

        # Verify new password succeeds
        res_new_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "bob@example.com", "password": "BrandNewPassword123!"},
        )
        assert res_new_login.status_code == 200
        print("   ✅ Login with new password succeeded, old password rejected.")

        # ── Test 9: Logout ───────────────────────────────────────────────────
        print("9️⃣ Testing POST /api/v1/auth/logout...")
        active_refresh = res_new_login.json()["refresh_token"]
        res_logout = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": active_refresh},
        )
        assert res_logout.status_code == 200
        # Check deleted cookies
        assert res_logout.cookies.get("access_token") is None
        print("   ✅ Logout succeeded and cookies cleared.")

    print("\n🎉 ALL 9 TEST SUITES PASSED FLAWLESSLY!")


if __name__ == "__main__":
    asyncio.run(run_tests())
