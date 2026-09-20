"""
schemas/widget_config.py
------------------------
Pydantic schemas for Widget configuration requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class WidgetConfigSchema(BaseModel):
    widget_name: str = Field(default="What's New")
    launcher_text: str = Field(default="What's New")
    launcher_style: str = Field(default="pill")
    launcher_size: str = Field(default="md")
    icon: str = Field(default="sparkle")
    position: str = Field(default="bottom-right")
    offset_x: int = Field(default=24)
    offset_y: int = Field(default=24)
    theme: str = Field(default="auto")
    accent_color: str = Field(default="#6366F1")
    border_radius: int = Field(default=12)
    shadow: str = Field(default="medium")
    animation: str = Field(default="subtle")

    show_badge: bool = Field(default=True)
    show_count: bool = Field(default=True)
    max_notifications: int = Field(default=5)
    title: str = Field(default="What's New")
    subtitle: str = Field(default="Latest product announcements")
    show_category: bool = Field(default=True)
    show_date: bool = Field(default=True)
    show_cover_image: bool = Field(default=True)
    show_reactions: bool = Field(default=True)
    show_read_more: bool = Field(default=True)
    max_visible_updates: int = Field(default=5)

    open_behavior: str = Field(default="drawer")
    close_on_outside_click: bool = Field(default=True)
    close_on_esc: bool = Field(default=True)
    mark_read_on_open: bool = Field(default=True)
    auto_open: bool = Field(default=False)
    auto_open_delay: int = Field(default=5)

    custom_css: str = Field(default="")
    updated_at: Optional[datetime] = None


class WidgetConfigResponse(WidgetConfigSchema):
    pass
