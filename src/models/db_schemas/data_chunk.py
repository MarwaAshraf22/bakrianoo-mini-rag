from bson import ObjectId
from pydantic import BaseModel, Field


class DataChunk(BaseModel):
    id: ObjectId | None = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_projectid: ObjectId
    chunk_assetid: ObjectId

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("chunk_projectid", 1)],
                "unique": False,
                "name": "chunk_projectid_idx",
            },
        ]


class RetrievedDocument(BaseModel):
    text: str
    score: float
