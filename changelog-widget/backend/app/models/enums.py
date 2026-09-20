"""
models/enums.py
---------------
Enumerations for roles, changelog categories, and statuses.
"""

from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class ChangelogCategory(str, Enum):
    NEW = "NEW"
    IMPROVED = "IMPROVED"
    FIXED = "FIXED"


class ChangelogStatus(str, Enum):
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    PUBLISHED = "PUBLISHED"


class ReactionType(str, Enum):
    LIKE = "👍"
    LOVE = "❤️"
    CELEBRATE = "🎉"
    FIRE = "🔥"
    ROCKET = "🚀"
    EYES = "👀"
