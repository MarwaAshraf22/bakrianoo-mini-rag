from datetime import datetime, timezone

from bson import ObjectId
from pydantic import BaseModel, Field


class Asset(BaseModel):
    id: ObjectId | None = Field(None, alias="_id")
    asset_projectid: ObjectId
    asset_name: str = Field(..., min_length=1)
    asset_type: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None)
    asset_pushed_at: datetime = Field(default=datetime.now(timezone.utc))

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("asset_projectid", 1)],
                "name": "asset_projectid_index",
                "unique": False,
            },
            {
                "key": [("asset_projectid", 1), ("asset_name", 1)],
                "name": "asset_projectid_name_index",
                "unique": True,
            },
        ]
