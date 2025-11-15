import logging

import aiofiles
from fastapi import APIRouter, Depends, Request, UploadFile, status
from fastapi.responses import JSONResponse

from controllers import DataController, ProcessController, ProjectController
from helpers.config import Settings, get_settings
from models import AssetTypeEnum, ResponseSignal
from models.asset_model import AssetModel
from models.chunk_model import ChunkModel
from models.db_schemas import Asset, DataChunk
from models.project_model import ProjectModel
from routes.schemas.data import ProcessRequest

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{projectid}")
async def upload_data(
    request: Request,
    projectid: str,
    file: UploadFile,
    app_settings: Settings = Depends(get_settings),
):
    data_controller = DataController()
    project_model = await ProjectModel.create_instance(db_client=request.app.database)
    project = await project_model.get_or_create_project(projectid=projectid)
    try:
        _ = data_controller.validate_uploaded_file(file=file)
        project_controller = ProjectController()
        dir_project = project_controller.get_dir_project(projectid=projectid)
        unique_filename = data_controller.generate_unique_filename(file.filename)
        path_file = dir_project / unique_filename
        try:
            async with aiofiles.open(path_file, "wb") as ptr_file:
                while content := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                    await ptr_file.write(content)
        except Exception as e:
            logger.error(f"Failed to save the file: {repr(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "signal": ResponseSignal.FILE_UPLOAD_FAILURE.value,
                },
            )
        asset_model = await AssetModel.create_instance(db_client=request.app.database)
        asset_resource = Asset(
            asset_projectid=project.id,
            asset_type=AssetTypeEnum.FILE.value,
            asset_name=unique_filename,
            asset_size=file.size,
        )
        asset_record = await asset_model.insert_asset(asset=asset_resource)
        return JSONResponse(
            content={
                "status": "success",
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(asset_record.id),
            },
        )
    except ValueError as ve:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": repr(ve),
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": f"An unexpected error occurred: {repr(e)}",
            },
        )


@data_router.post("/process/{projectid}")
async def process_endpoint(
    request: Request, projectid: str, process_request: ProcessRequest
):
    fileid = process_request.file_id
    chunk_size = process_request.chunk_size or 100
    overlap_size = process_request.overlap_size or 20
    do_reset = process_request.do_reset or 0

    chunk_model = await ChunkModel.create_instance(db_client=request.app.database)
    project_model = await ProjectModel.create_instance(db_client=request.app.database)
    asset_model = await AssetModel.create_instance(db_client=request.app.database)
    project = await project_model.get_or_create_project(projectid=projectid)
    process_controller = ProcessController(projectid=projectid)

    project_file_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_by_name(
            asset_projectid=project.id, asset_name=process_request.file_id
        )
        if not asset_record:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "status": "error",
                    "signal": ResponseSignal.FILE_MISSING_ID_ERROR.value,
                },
            )
        project_file_ids = {asset_record.id: asset_record.asset_name}
    else:
        project_files = await asset_model.get_project_assets(
            asset_projectid=str(project.id),
            asset_type=AssetTypeEnum.FILE.value,
        )
        project_file_ids = {asset.id: asset.asset_name for asset in project_files}
    if not project_file_ids or len(project_file_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "error",
                "signal": ResponseSignal.NO_FILES_ERROR.value,
            },
        )

    if do_reset:
        await chunk_model.delete_chunks_by_projectid(projectid=str(project.id))

    no_records, no_files = 0, 0
    for asset_id, fileid in project_file_ids.items():
        file_content = process_controller.load_file_content(fileid=fileid)
        if not file_content or len(file_content) == 0:
            logger.error(f"No content loaded for file ID: {fileid}")
            continue
        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            fileid=fileid,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )
        if not file_chunks or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "signal": ResponseSignal.FILE_PROCESSING_FAILURE.value,
                },
            )

        file_chunks_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i + 1,
                chunk_projectid=project.id,
                chunk_assetid=asset_id,
            )
            for i, chunk in enumerate(file_chunks)
        ]

        no_records += await chunk_model.bulk_create_chunks(chunks=file_chunks_records)
        no_files += 1

    # DEBUG:
    return JSONResponse(
        content={
            "status": "success",
            "signal": ResponseSignal.FILE_PROCESSING_SUCCESS.value,
            "total_chunks_created": no_records,
            "total_files_processed": no_files,
        },
    )
