"""
models/base.py
--------------
Pydantic V2 base model and MongoDB ObjectId helpers.
"""

from datetime import datetime, timezone
from typing import Annotated, Any
from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, BeforeValidator


def validate_object_id(v: Any) -> str:
    """Validate and convert BSON ObjectId or string representation to string."""
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str) and ObjectId.is_valid(v):
        return v
    raise ValueError(f"Invalid ObjectId: {v}")


# Custom type for ObjectId fields that accepts ObjectId/str and exposes a str
PyObjectId = Annotated[
    str,
    BeforeValidator(validate_object_id),
    PlainSerializer(lambda x: str(x), return_type=str),
]


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


class MongoBaseModel(BaseModel):
    """
    Base model for MongoDB documents.
    Maps '_id' from MongoDB to 'id' in Python/JSON and vice versa.
    """
    id: PyObjectId | None = Field(default=None, alias="_id")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    def to_mongo(self) -> dict[str, Any]:
        """
        Convert model to dict suitable for MongoDB insert/update.
        Converts string ObjectIds back to BSON ObjectId for proper indexing.
        """
        data = self.model_dump(by_alias=True, exclude_none=True)
        if "_id" in data and data["_id"] is None:
            del data["_id"]
        for k, v in list(data.items()):
            if isinstance(v, str) and ObjectId.is_valid(v) and (k == "_id" or k.endswith("_id") or k == "created_by"):
                data[k] = ObjectId(v)
        return data
