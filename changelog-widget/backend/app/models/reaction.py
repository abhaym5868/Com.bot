"""
models/reaction.py
------------------
Reaction document model for MongoDB.
"""

from datetime import datetime
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId, utc_now


class ReactionModel(MongoBaseModel):
    """
    MongoDB representation of a user Reaction in the 'reactions' collection.
    Enforces that a user cannot react with the same reaction type multiple times
    on the same changelog via unique compound indexing.
    """
    user_id: PyObjectId = Field(..., description="ID of the reacting user")
    changelog_id: PyObjectId = Field(..., description="ID of the changelog post")
    reaction: str = Field(..., min_length=1, max_length=50, description="Reaction type identifier or emoji")
    created_at: datetime = Field(default_factory=utc_now)
