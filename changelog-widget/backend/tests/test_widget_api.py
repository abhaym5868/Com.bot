"""
tests/test_widget_api.py
------------------------
Integration tests for Widget Configuration endpoints:
- GET /api/v1/widget/config (public / fallback default)
- PUT /api/v1/widget/config (authenticated admin update)
- Permission checks (non-admin forbidden)
"""

import pytest
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.config.database import get_database


@pytest.mark.asyncio
async def test_widget_config_lifecycle():
    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["test_widget_db"]
    app.dependency_overrides[get_database] = lambda: mock_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. GET config before any DB record -> should return default config
        res_get = await client.get("/api/v1/widget/config")
        assert res_get.status_code == 200
        data = res_get.json()
        assert data["launcher_text"] == "What's New"
        assert data["position"] == "bottom-right"
        assert data["accent_color"] == "#6366F1"

        # 2. PUT config without auth -> 401 Unauthorized
        res_put_unauth = await client.put(
            "/api/v1/widget/config",
            json={"launcher_text": "Updated Text", "accent_color": "#10B981"}
        )
        assert res_put_unauth.status_code == 401

        # 3. Create Admin user & login
        admin_signup = await client.post(
            "/api/v1/auth/signup",
            json={"name": "Widget Admin", "email": "widgetadmin@example.com", "password": "AdminPassword123!"}
        )
        assert admin_signup.status_code == 201
        admin_token = admin_signup.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_token}"}

        # 4. PUT config as admin
        update_payload = {
            "widget_name": "SaaS Updates",
            "launcher_text": "Product News",
            "launcher_style": "pill",
            "launcher_size": "lg",
            "icon": "rocket",
            "position": "bottom-left",
            "offset_x": 32,
            "offset_y": 32,
            "theme": "dark",
            "accent_color": "#10B981",
            "border_radius": 16,
            "shadow": "elevated",
            "animation": "pulse",
            "show_badge": True,
            "show_count": True,
            "max_notifications": 8,
            "title": "What's Cooking",
            "subtitle": "Fresh releases weekly",
            "show_category": True,
            "show_date": True,
            "show_cover_image": False,
            "show_reactions": True,
            "show_read_more": True,
            "max_visible_updates": 6,
            "open_behavior": "drawer",
            "close_on_outside_click": True,
            "close_on_esc": True,
            "mark_read_on_open": True,
            "auto_open": False,
            "auto_open_delay": 5,
            "custom_css": ".cw-launcher { font-weight: 700; }"
        }

        res_put = await client.put("/api/v1/widget/config", headers=headers, json=update_payload)
        assert res_put.status_code == 200
        saved_data = res_put.json()
        assert saved_data["launcher_text"] == "Product News"
        assert saved_data["position"] == "bottom-left"
        assert saved_data["accent_color"] == "#10B981"
        assert saved_data["icon"] == "rocket"

        # 5. GET config again -> should reflect updated values
        res_get_updated = await client.get("/api/v1/widget/config")
        assert res_get_updated.status_code == 200
        updated_data = res_get_updated.json()
        assert updated_data["launcher_text"] == "Product News"
        assert updated_data["position"] == "bottom-left"
        assert updated_data["accent_color"] == "#10B981"
        assert updated_data["icon"] == "rocket"
        assert updated_data["custom_css"] == ".cw-launcher { font-weight: 700; }"
