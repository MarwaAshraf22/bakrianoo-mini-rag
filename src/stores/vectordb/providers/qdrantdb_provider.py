import logging

from qdrant_client import QdrantClient, models

from ..vectordb_enum import DistanceMetricEnum
from ..vectordb_interface import VectorDBInterface


class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_metric: str):
        self.client = None
        self.db_path = db_path
        self.distance_metric = None

        if distance_metric.lower() == DistanceMetricEnum.COSINE.value:
            self.distance_metric = models.Distance.COSINE
        elif distance_metric.lower() == DistanceMetricEnum.DOT.value:
            self.distance_metric = models.Distance.DOT
        else:
            raise ValueError(f"Unsupported distance metric: {distance_metric}")
        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.client: QdrantClient = QdrantClient(path=self.db_path)

    def disconnect(self):
        self.client = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collections(self) -> list:
        return self.client.get_collections().collections

    def collection_info(self, collection_name: str) -> dict:
        # return self.client.get_collection(collection_name=collection_name)
        return self.client.get_collection(collection_name=collection_name).model_dump()

    def drop_collection(self, collection_name: str):
        if self.collection_exists(collection_name):
            return self.client.delete_collection(collection_name=collection_name)

    def create_collection(
        self, collection_name: str, embedding_size: int, do_reset: bool = False
    ):
        if do_reset and self.collection_exists(collection_name):
            self.drop_collection(collection_name)

        if not self.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size, distance=self.distance_metric
                ),
            )
            return True
        return False

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: list,
        metadata: dict | None = None,
        recordid: str | None = None,
    ) -> bool:
        if not self.collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return False

        try:
            # _ = self.client.upsert(
            #     collection_name=collection_name,
            #     points=[
            #         models.PointStruct(
            #             id=recordid,
            #             vector=vector,
            #             payload={"text": text, "metadata": metadata},
            #         )
            #     ],
            # )
            # _ = self.client.upload_points(
            #     collection_name=collection_name,
            #     points=[
            #         models.PointStruct(
            #             id=recordid,
            #             vector=vector,
            #             payload={"text": text, "metadata": metadata},
            #         )
            #     ],
            # )
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=recordid,
                        vector=vector,
                        payload={"text": text, "metadata": metadata},
                    )
                ],
            )
            return True
        except Exception as e:
            self.logger.error(f"Error inserting record: {e}")
            return False

    def insert_many(
        self,
        collection_name: str,
        texts: list[str],
        vectors: list[list],
        metadata: list[dict] | list[None] | None = None,
        recordids: list[str] | list[None] | None = None,
        batch_size: int = 50,
    ) -> bool:
        if not self.collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return []

        total_records = len(texts)
        metadata = metadata or [None] * total_records
        recordids = recordids or [None] * total_records
        # inserted_ids = []

        for start_idx in range(0, total_records, batch_size):
            end_idx = min(start_idx + batch_size, total_records)
            batch_texts = texts[start_idx:end_idx]
            batch_vectors = vectors[start_idx:end_idx]
            batch_metadata = metadata[start_idx:end_idx]

            batch_records = [
                models.Record(
                    id=recordids[i] if recordids and i < len(recordids) else None,
                    vector=batch_vectors[i],
                    payload={
                        "text": batch_texts[i],
                        "metadata": batch_metadata[i]
                        if batch_metadata and i < len(batch_metadata)
                        else None,
                    },
                )
                for i in range(start_idx, end_idx)
            ]
            try:
                _ = self.client.upload_records(
                    collection_name=collection_name, records=batch_records
                )
            except Exception as e:
                self.logger.error(
                    f"Error inserting batch starting at index {start_idx}: {e}"
                )
                return False
        return True

    def query_by_vector(
        self, collection_name: str, vector: list, limit: int = 5
    ) -> list:
        if not self.collection_exists(collection_name):
            self.logger.error(f"Collection {collection_name} does not exist.")
            return []

        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit,
            )
            return results
        except Exception as e:
            self.logger.error(f"Error querying by vector: {e}")
            return []
