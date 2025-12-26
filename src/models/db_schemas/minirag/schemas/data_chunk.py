import uuid

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import SQLAlchemyBase


class DataChunk(SQLAlchemyBase):
    __tablename__ = "chunks"

    chunkid = Column(Integer, primary_key=True, autoincrement=True)
    chunk_uuid = Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False
    )

    chunk_text = Column(String, nullable=False)
    chunk_order = Column(Integer, nullable=False)

    chunk_projectid = Column(Integer, ForeignKey("projects.projectid"), nullable=False)
    chunk_assetid = Column(Integer, ForeignKey("assets.assetid"), nullable=False)
    chunk_metadata = Column(JSONB, nullable=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    asset = relationship("Asset", back_populates="chunks")
    project = relationship("Project", back_populates="chunks")

    __table_args__ = (
        Index("idx_chunk_project_id", chunk_projectid),
        Index("idx_chunk_asset_id", chunk_assetid),
    )


class RetrievedDocument(BaseModel):
    text: str
    score: float
