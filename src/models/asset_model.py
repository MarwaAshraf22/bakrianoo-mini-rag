from bson import ObjectId
from sqlalchemy import delete, func, select

from .base_data_model import BaseDataModel
from .db_schemas import Asset
from .enums.db_enum import DataBaseEnum

# class AssetModel(BaseDataModel):
#     def __init__(self, db_client) -> None:
#         super().__init__(db_client)
#         self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]

#     @classmethod
#     async def create_instance(cls, db_client) -> "AssetModel":
#         instance = cls(db_client)
#         await instance.init_collection()
#         return instance

#     async def init_collection(self) -> None:
#         all_collections = await self.db_client.list_collection_names()
#         if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collections:
#             self.collection = await self.db_client.create_collection(
#                 DataBaseEnum.COLLECTION_ASSET_NAME.value
#             )
#             indexes = Asset.get_indexes()
#             for index in indexes:
#                 await self.collection.create_index(
#                     index["key"],
#                     name=index["name"],
#                     unique=index["unique"],
#                 )

#     async def insert_asset(self, asset: Asset) -> Asset:
#         result = await self.collection.insert_one(
#             asset.model_dump(by_alias=True, exclude_unset=True)
#         )
#         asset.id = result.inserted_id
#         return asset

#     async def get_asset_by_name(
#         self, asset_projectid: str | ObjectId, asset_name: str
#     ) -> Asset | None:
#         asset_projectid = (
#             ObjectId(asset_projectid)
#             if isinstance(asset_projectid, str)
#             else asset_projectid
#         )
#         document = await self.collection.find_one(
#             {"asset_projectid": asset_projectid, "asset_name": asset_name}
#         )
#         if document:
#             return Asset.model_validate(document)
#         return None

#     async def get_project_assets(
#         self, asset_projectid: str | ObjectId, asset_type: str
#     ) -> list[Asset]:
#         asset_projectid = (
#             ObjectId(asset_projectid)
#             if isinstance(asset_projectid, str)
#             else asset_projectid
#         )
#         cursor = self.collection.find(
#             {"asset_projectid": asset_projectid, "asset_type": asset_type}
#         )
#         assets = [Asset.model_validate(doc) async for doc in cursor]
#         return assets


class AssetModel(BaseDataModel):
    def __init__(self, db_client) -> None:
        super().__init__(db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client) -> "AssetModel":
        instance = cls(db_client)
        return instance

    async def insert_asset(self, asset: Asset) -> Asset:
        async with self.db_client() as session:
            async with session.begin():
                session.add(asset)
                await session.commit()
            await session.refresh(asset)
        return asset

    async def get_asset_by_name(
        self, asset_projectid: str | ObjectId, asset_name: str
    ) -> Asset | None:
        async with self.db_client() as session:
            statement = select(Asset).where(
                Asset.asset_projectid == asset_projectid, Asset.asset_name == asset_name
            )
            result = await session.execute(statement)
            record = result.scalar_one_or_none()
        return record

    async def get_project_assets(
        # self, asset_projectid: str | ObjectId, asset_type: str
        self, asset_projectid: int | ObjectId, asset_type: str
    ) -> list[Asset]:
        async with self.db_client() as session:
            statement = select(Asset).where(
                Asset.asset_projectid == asset_projectid,
                Asset.asset_type == asset_type,
            )
            result = await session.execute(statement)
            records = result.scalars().all()
        return records
