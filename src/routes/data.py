import logging
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse

from controllers import DataController, ProjectController
from helpers.config import Settings, get_settings
from models import ResponseSignal

logger = logging.getLogger("uvicorn.error")

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{projectid}")
async def upload_data(
    projectid: str, file: UploadFile, app_settings: Settings = Depends(get_settings)
):
    data_controller = DataController()
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
            return JSONResponse(
                content={
                    "status": "success",
                    "message": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                    "file_id": Path(unique_filename).stem,
                },
            )
        except Exception as e:
            logger.error(f"Failed to save the file: {repr(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "status": "error",
                    "message": ResponseSignal.FILE_UPLOAD_FAILURE.value,
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
