from controllers.base import BaseController
from helpers.config import Settings

from .providers import QdrantDBProvider
from .vectordb_enum import VectorDBEnum


class VectorDBProviderFactory:
    def __init__(self, config: Settings):
        self.config = config
        self.base_controller = BaseController()

    def create(self, provider: str):
        if provider.upper() == VectorDBEnum.QDRANT.value:
            db_path = self.base_controller.get_database_path(self.config.VECTOR_DB_PATH)
            return QdrantDBProvider(
                db_path=str(db_path),
                distance_metric=self.config.VECTOR_DB_DISTANCE_METRIC,
            )
        return None
