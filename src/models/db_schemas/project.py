from bson import ObjectId
from pydantic import BaseModel, Field, field_validator


class Project(BaseModel):
    id: ObjectId | None = Field(None, alias="_id")
    projectid: str = Field(..., min_length=1)

    @field_validator("projectid")
    def validate_projectid(cls, v):
        if not v.isalnum():
            raise ValueError("projectid must be alphanumeric")
        return v

    class Config:
        arbitrary_types_allowed = True
