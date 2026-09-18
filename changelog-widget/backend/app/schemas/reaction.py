"""
schemas/reaction.py
-------------------
Pydantic schemas for Reaction request validation and responses.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

ALLOWED_REACTIONS = ["❤️", "🎉", "🚀"]


class ReactionCreate(BaseModel):
    changelog_id: str = Field(..., description="ID of the changelog to react to")
    reaction: str = Field(..., description="Reaction emoji: ❤️, 🎉, or 🚀")


class ReactionResponse(BaseModel):
    id: str
    user_id: str
    changelog_id: str
    reaction: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReactionItemSummary(BaseModel):
    reaction: str
    count: int
    user_reacted: bool = False
    user_reaction_id: str | None = None


class ChangelogReactionsSummary(BaseModel):
    changelog_id: str
    reactions: list[ReactionItemSummary]


ReactionSummary = ReactionItemSummary

