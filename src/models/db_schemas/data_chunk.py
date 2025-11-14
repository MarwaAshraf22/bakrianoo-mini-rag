from bson import ObjectId
from pydantic import BaseModel, Field, field_validator


class DataChunk(BaseModel):
    _id: ObjectId | None
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_projectid: ObjectId

    class Config:
        arbitrary_types_allowed = True
