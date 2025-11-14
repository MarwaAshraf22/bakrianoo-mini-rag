from bson import ObjectId

from .base_data_model import BaseDataModel
from .db_schemas.asset import Asset
from .enums.db_enum import DataBaseEnum


class AssetModel(BaseDataModel):
    def __init__(self, db_client) -> None:
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client) -> "AssetModel":
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self) -> None:
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collections:
            self.collection = await self.db_client.create_collection(
                DataBaseEnum.COLLECTION_ASSET_NAME.value
            )
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"],
                )

    async def insert_asset(self, asset: Asset) -> Asset:
        result = await self.collection.insert_one(
            asset.model_dump(by_alias=True, exclude_unset=True)
        )
        asset.id = result.inserted_id
        return asset

    async def get_project_assets(self, asset_projectid: str | ObjectId) -> list[Asset]:
        asset_projectid = (
            ObjectId(asset_projectid)
            if isinstance(asset_projectid, str)
            else asset_projectid
        )
        cursor = self.collection.find({"asset_projectid": asset_projectid})
        assets = [Asset.model_validate(doc) async for doc in cursor]
        return assets
