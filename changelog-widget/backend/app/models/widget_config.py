"""
models/widget_config.py
-----------------------
MongoDB model for Widget Studio customization settings.
"""

from typing import Any
from pydantic import Field
from app.models.base import MongoBaseModel, utc_now
from datetime import datetime


class WidgetConfigModel(MongoBaseModel):
    """
    Stored configuration for the embeddable Changelog widget.
    Single-tenant/project settings.
    """
    widget_name: str = Field(default="What's New")
    launcher_text: str = Field(default="What's New")
    launcher_style: str = Field(default="pill")      # 'pill', 'rounded', 'circle', 'minimal'
    launcher_size: str = Field(default="md")          # 'sm', 'md', 'lg'
    icon: str = Field(default="sparkle")              # 'bell', 'sparkle', 'megaphone', 'custom'
    position: str = Field(default="bottom-right")    # 'bottom-right', 'bottom-left', 'top-right', 'top-left'
    offset_x: int = Field(default=24)
    offset_y: int = Field(default=24)
    theme: str = Field(default="auto")               # 'auto', 'light', 'dark', 'custom'
    accent_color: str = Field(default="#6366F1")
    border_radius: int = Field(default=12)
    shadow: str = Field(default="medium")            # 'none', 'soft', 'medium', 'strong'
    animation: str = Field(default="subtle")         # 'none', 'subtle', 'bounce'

    # Content & Badges
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

    # Behavior
    open_behavior: str = Field(default="drawer")     # 'drawer', 'popover', 'modal'
    close_on_outside_click: bool = Field(default=True)
    close_on_esc: bool = Field(default=True)
    mark_read_on_open: bool = Field(default=True)
    auto_open: bool = Field(default=False)
    auto_open_delay: int = Field(default=5)

    # Advanced Custom CSS
    custom_css: str = Field(default="")
    updated_at: datetime = Field(default_factory=utc_now)
