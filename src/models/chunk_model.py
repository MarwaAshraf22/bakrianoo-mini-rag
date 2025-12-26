from bson import ObjectId
from pymongo import InsertOne
from sqlalchemy import delete, func, select

# from sqlalchemy.future import select
from .base_data_model import BaseDataModel
from .db_schemas import DataChunk
from .enums.db_enum import DataBaseEnum

# class ChunkModel(BaseDataModel):
#     def __init__(self, db_client):
#         super().__init__(db_client)
#         self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

#     @classmethod
#     async def create_instance(cls, db_client):
#         instance = cls(db_client)
#         await instance.init_connection()
#         return instance

#     async def init_connection(self):
#         all_collections = await self.db_client.list_collection_names()
#         if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collections:
#             indexes = DataChunk.get_indexes()
#             for index in indexes:
#                 await self.collection.create_index(
#                     index["key"],
#                     unique=index.get("unique", False),
#                     name=index.get("name"),
#                 )

#     async def insert_chunk(self, chunk: DataChunk) -> DataChunk:
#         result = await self.collection.insert_one(
#             chunk.model_dump(by_alias=True, exclude_unset=True)
#         )
#         chunk.chunkid = result.inserted_id
#         return chunk

#     async def get_chunk(self, chunk_id: str) -> DataChunk | None:
#         chunk_data = await self.collection.find_one({"_id": chunk_id})
#         if chunk_data:
#             return DataChunk.model_validate(chunk_data)
#         return None

#     async def bulk_create_chunks(
#         self, chunks: list[DataChunk], batch_size: int = 100
#     ) -> int:
#         operations = []
#         for chunk in chunks:
#             operations.append(
#                 InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
#             )
#             if len(operations) == batch_size:
#                 await self.collection.bulk_write(operations)
#                 operations = []
#         if operations:
#             await self.collection.bulk_write(operations)
#         return len(chunks)

#     async def delete_chunks_by_projectid(self, projectid: str) -> int:
#         result = await self.collection.delete_many({"chunk_projectid": projectid})
#         return result.deleted_count

#     async def get_chunks_by_projectid(
#         self, projectid: str, page: int = 1, page_size: int = 100
#     ) -> list[DataChunk]:
#         skip = (page - 1) * page_size
#         cursor = (
#             self.collection.find({"chunk_projectid": ObjectId(projectid)})
#             .skip(skip)
#             .limit(page_size)
#         )
#         chunks = [DataChunk.model_validate(document) async for document in cursor]
#         return chunks


class ChunkModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client):
        instance = cls(db_client)
        return instance

    async def insert_chunk(self, chunk: DataChunk) -> DataChunk:
        async with self.db_client as session:
            async with session.begin():
                session.add(chunk)
            await session.commit()
            await session.refresh(chunk)
        return chunk

    async def get_chunk(self, chunk_id: str) -> DataChunk | None:
        async with self.db_client as session:
            result = await session.execute(
                select(DataChunk).where(DataChunk.chunkid == chunk_id)
            )
            chunk = result.scalar_one_or_none()
        return chunk

    async def bulk_create_chunks(
        self, chunks: list[DataChunk], batch_size: int = 100
    ) -> int:
        async with self.db_client() as session:
            async with session.begin():
                for i in range(0, len(chunks), batch_size):
                    batch = chunks[i : i + batch_size]
                    session.add_all(batch)
            await session.commit()
        return len(chunks)

    async def delete_chunks_by_projectid(self, projectid: int) -> int:
        async with self.db_client() as session:
            statement = delete(DataChunk).where(DataChunk.chunk_projectid == projectid)
            result = await session.execute(statement)
            await session.commit()
        return result.rowcount

    async def get_chunks_by_projectid(
        self, projectid: int, page: int = 1, page_size: int = 100
    ) -> list[DataChunk]:
        async with self.db_client() as session:
            statement = (
                select(DataChunk)
                .where(DataChunk.chunk_projectid == projectid)
                .offset(page_size * (page - 1))
                .limit(page_size)
            )
            result = await session.execute(statement)
            records = result.scalars().all()
        return records
