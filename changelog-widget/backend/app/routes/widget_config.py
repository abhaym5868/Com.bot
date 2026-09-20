"""
routes/widget_config.py
-----------------------
API endpoints for Widget Configuration:
- GET /api/v1/widget/config  (Public/cached, returns saved or default widget settings)
- PUT /api/v1/widget/config  (Admin only, saves widget configuration to MongoDB)
"""

from fastapi import APIRouter, Depends, Response
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.middleware.auth import get_current_admin_user
from app.models.user import UserModel
from app.models.base import utc_now
from app.schemas.widget_config import WidgetConfigSchema, WidgetConfigResponse

router = APIRouter()

CONFIG_KEY = "primary_widget_config"


@router.get(
    "/config",
    response_model=WidgetConfigResponse,
    summary="Get widget configuration",
    description="Returns stored widget configuration settings or default fallback values.",
)
async def get_widget_config(
    response: Response,
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    # Set 60s cache header for public performance
    response.headers["Cache-Control"] = "public, max-age=60"

    doc = await db["widget_configs"].find_one({"key": CONFIG_KEY})
    if not doc:
        # Return default schema instance
        default_instance = WidgetConfigSchema()
        return WidgetConfigResponse.model_validate(default_instance.model_dump())

    return WidgetConfigResponse.model_validate(doc)


@router.put(
    "/config",
    response_model=WidgetConfigResponse,
    summary="Update widget configuration (Admin only)",
    description="Saves updated widget configuration settings to MongoDB.",
)
async def update_widget_config(
    payload: WidgetConfigSchema,
    admin_user: UserModel = Depends(get_current_admin_user),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    update_data = payload.model_dump()
    update_data["key"] = CONFIG_KEY
    update_data["updated_at"] = utc_now()
    update_data["updated_by"] = str(admin_user.id)

    await db["widget_configs"].update_one(
        {"key": CONFIG_KEY},
        {"$set": update_data},
        upsert=True,
    )

    doc = await db["widget_configs"].find_one({"key": CONFIG_KEY})
    return WidgetConfigResponse.model_validate(doc)
