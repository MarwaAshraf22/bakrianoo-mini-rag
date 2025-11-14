from .base_data_model import BaseDataModel
from .db_schemas import Project
from .enums.db_enum import DataBaseEnum


class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_connection()
        return instance

    async def init_connection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    unique=index.get("unique", False),
                    name=index.get("name"),
                )

    async def create_project(self, project: Project) -> Project:
        result = await self.collection.insert_one(
            project.model_dump(by_alias=True, exclude_unset=True)
        )
        project.id = result.inserted_id
        return project

    async def get_or_create_project(self, projectid: str) -> Project:
        project_data = await self.collection.find_one({"projectid": projectid})
        if project_data:
            return Project.model_validate(project_data)
        new_project = Project(projectid=projectid)
        return await self.create_project(new_project)

    async def get_all_projects(
        self, page: int = 1, page_size: int = 10
    ) -> tuple[list[Project], int]:
        total_docs = await self.collection.count_documents({})
        total_pages = (total_docs + page_size - 1) // page_size
        skip = (page - 1) * page_size
        cursor = self.collection.find().skip(skip).limit(page_size)
        projects = [Project.model_validate(doc) async for doc in cursor]
        return projects, total_pages
