"""
tests/test_upload_api.py
------------------------
Integration test suite for the image upload endpoint (POST /api/v1/upload/image)
and static file serving (/static/uploads/{filename}).
"""

import io
import os
import shutil
import pytest
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.config.database import get_database
from app.config.settings import settings
from app.models.indexes import create_database_indexes


@pytest.mark.asyncio
async def test_upload_suite():
    print("🚀 Starting Image Upload Integration Tests...\n")

    # 1. Setup mock MongoDB
    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["test_upload_db"]
    await create_database_indexes(mock_db)
    app.dependency_overrides[get_database] = lambda: mock_db

    # Setup upload directory
    os.makedirs(settings.upload_dir, exist_ok=True)
    created_files = []

    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            # 1. Setup Admin and Regular User
            print("1️⃣ Creating Admin and Regular User...")
            res_admin = await client.post(
                "/api/v1/auth/signup",
                json={"name": "Admin", "email": "admin@upload.com", "password": "Password123!"},
            )
            assert res_admin.status_code == 201
            admin_token = res_admin.cookies.get("access_token")
            assert admin_token is not None
            admin_headers = {"Authorization": f"Bearer {admin_token}"}

            res_user = await client.post(
                "/api/v1/auth/signup",
                json={"name": "User", "email": "user@upload.com", "password": "Password123!"},
            )
            assert res_user.status_code == 201
            user_token = res_user.cookies.get("access_token")
            assert user_token is not None
            user_headers = {"Authorization": f"Bearer {user_token}"}
            print("   ✅ Users created.")

            # 2. Upload valid PNG image as Admin
            print("2️⃣ Testing valid PNG upload (Admin)...")
            png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
            files = {"file": ("test_image.png", io.BytesIO(png_bytes), "image/png")}
            res_upload = await client.post("/api/v1/upload/image", files=files, headers=admin_headers)
            assert res_upload.status_code == 201, f"Upload failed: {res_upload.text}"
            data = res_upload.json()
            assert "url" in data
            assert data["url"].startswith("/static/uploads/")
            assert data["content_type"] == "image/png"
            assert data["size_bytes"] == len(png_bytes)
            uploaded_url = data["url"]
            created_files.append(os.path.join(settings.upload_dir, data["filename"]))
            print(f"   ✅ Image uploaded successfully. URL: {uploaded_url}")

            # 3. Verify static file retrieval
            print("3️⃣ Testing static file retrieval via GET...")
            res_static = await client.get(uploaded_url)
            assert res_static.status_code == 200
            assert res_static.content == png_bytes
            print("   ✅ Static file served correctly.")

            # 4. Upload unauthenticated -> 401
            print("4️⃣ Testing unauthenticated upload attempt...")
            client.cookies.clear()
            files = {"file": ("unauth.png", io.BytesIO(png_bytes), "image/png")}
            res_unauth = await client.post("/api/v1/upload/image", files=files)
            assert res_unauth.status_code == 401
            print("   ✅ Unauthenticated upload rejected with HTTP 401.")

            # 5. Upload as regular user (non-admin) -> 403 Forbidden
            print("5️⃣ Testing non-admin upload attempt...")
            files = {"file": ("user.png", io.BytesIO(png_bytes), "image/png")}
            res_forbid = await client.post("/api/v1/upload/image", files=files, headers=user_headers)
            assert res_forbid.status_code == 403
            print("   ✅ Non-admin upload rejected with HTTP 403 Forbidden.")

            # 6. Invalid MIME type -> 415 Unsupported Media Type
            print("6️⃣ Testing invalid file type upload (text/plain)...")
            text_files = {"file": ("malicious.txt", io.BytesIO(b"Hello world"), "text/plain")}
            res_bad_type = await client.post("/api/v1/upload/image", files=text_files, headers=admin_headers)
            assert res_bad_type.status_code == 415
            print("   ✅ Invalid file type rejected with HTTP 415 Unsupported Media Type.")

            # 7. Empty file -> 400 Bad Request
            print("7️⃣ Testing empty file upload (0 bytes)...")
            empty_files = {"file": ("empty.png", io.BytesIO(b""), "image/png")}
            res_empty = await client.post("/api/v1/upload/image", files=empty_files, headers=admin_headers)
            assert res_empty.status_code == 400
            print("   ✅ Empty file rejected with HTTP 400 Bad Request.")

            # 8. Oversized file (> 5MB) -> 413 Payload Too Large
            print("8️⃣ Testing oversized file upload (> 5MB)...")
            large_bytes = b"x" * (6 * 1024 * 1024)  # 6MB
            large_files = {"file": ("large.png", io.BytesIO(large_bytes), "image/png")}
            res_large = await client.post("/api/v1/upload/image", files=large_files, headers=admin_headers)
            assert res_large.status_code == 413
            print("   ✅ Oversized file rejected with HTTP 413 Request Entity Too Large.")

        print("\n🎉 ALL IMAGE UPLOAD TESTS PASSED FLAWLESSLY!\n")
    finally:
        for fpath in created_files:
            if os.path.exists(fpath):
                os.remove(fpath)
        app.dependency_overrides.clear()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_tests())
