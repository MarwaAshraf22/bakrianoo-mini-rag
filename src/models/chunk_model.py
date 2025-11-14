from httpx import delete
from pymongo import InsertOne

from .base_data_model import BaseDataModel
from .db_schemas import DataChunk
from .enums.db_enum import DataBaseEnum


class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_connection()
        return instance

    async def init_connection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections:
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    unique=index.get("unique", False),
                    name=index.get("name"),
                )

    async def create_chunk(self, chunk: DataChunk) -> DataChunk:
        result = await self.collection.insert_one(
            chunk.model_dump(by_alias=True, exclude_unset=True)
        )
        chunk.id = result.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: str) -> DataChunk | None:
        chunk_data = await self.collection.find_one({"_id": chunk_id})
        if chunk_data:
            return DataChunk.model_validate(chunk_data)
        return None

    async def bulk_create_chunks(
        self, chunks: list[DataChunk], batch_size: int = 100
    ) -> int:
        operations = []
        for chunk in chunks:
            operations.append(InsertOne(chunk.model_dump()))
            if len(operations) == batch_size:
                await self.collection.bulk_write(operations)
                operations = []
        if operations:
            await self.collection.bulk_write(operations)
        return len(chunks)

    async def delete_chunks_by_projectid(self, projectid: str) -> int:
        result = await self.collection.delete_many({"chunk_projectid": projectid})
        return result.deleted_count
