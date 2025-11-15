from abc import ABC, abstractmethod

from models.db_schemas import RetrievedDocument


class VectorDBInterface(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def collection_exists(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def list_all_collections(self) -> list:
        pass

    @abstractmethod
    def collection_info(self, collection_name: str) -> dict:
        pass

    @abstractmethod
    def drop_collection(self, collection_name: str):
        pass

    @abstractmethod
    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        pass

    @abstractmethod
    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict | None = None,
        recordid: str | None = None,
    ) -> bool:
        pass

    @abstractmethod
    def insert_many(
        self,
        collection_name: str,
        texts: list[str],
        vectors: list[list],
        metadata: list[dict] | None = None,
        recordids: list[str] | None = None,
        batch_size: int = 50,
    ) -> bool:
        pass

    @abstractmethod
    def query_by_vector(
        self, collection_name: str, vector: list, limit: int = 5
    ) -> list[RetrievedDocument]:
        pass
