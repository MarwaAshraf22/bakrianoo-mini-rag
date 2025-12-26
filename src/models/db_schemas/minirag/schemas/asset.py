import uuid

from sqlalchemy import Column, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import SQLAlchemyBase


class Asset(SQLAlchemyBase):
    __tablename__ = "assets"

    assetid = Column(Integer, primary_key=True, autoincrement=True)
    asset_uuid = Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False
    )

    asset_type = Column(String, nullable=False)
    asset_name = Column(String, nullable=False)
    asset_size = Column(Integer, nullable=False)
    asset_config = Column(JSONB, nullable=True)

    asset_projectid = Column(
        Integer, ForeignKey("projects.projectid"), nullable=False
    )

    chunks = relationship("DataChunk", back_populates="asset")
    project = relationship("Project", back_populates="assets")

    __table_args__ = (
        Index("idx_asset_project_id", asset_projectid),
        Index("idx_asset_type", asset_type),
    )
