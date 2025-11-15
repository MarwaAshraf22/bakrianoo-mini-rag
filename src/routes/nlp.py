import logging

from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse

from controllers import NLPController
from models import ResponseSignal
from models.chunk_model import ChunkModel
from models.project_model import ProjectModel
from routes.schemas.nlp import PushRequest, SearchRequest

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)


@nlp_router.post("/index/push/{projectid}")
async def push_index(request: Request, projectid: str, push_request: PushRequest):
    project_model = await ProjectModel.create_instance(db_client=request.app.database)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.database)

    project = await project_model.get_or_create_project(projectid=projectid)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
        )

    nlp_controller = NLPController(
        client_vectordb=request.app.vectordb_client,
        client_generation=request.app.generation_client,
        client_embedding=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    page_no = 1
    inserted_count = 0
    idx = 0
    while True:
        page_chunks = await chunk_model.get_chunks_by_projectid(
            projectid=str(project.id), page=page_no
        )
        if not (page_chunks and len(page_chunks)):
            break
        page_no += 1
        print(page_no)
        chunk_ids = list(range(idx, idx + len(page_chunks)))
        inserted = nlp_controller.index_into_vectordb(
            project=project,
            chunks=page_chunks,
            chunkids=chunk_ids,
            do_reset=push_request.do_reset,
        )

        idx += len(page_chunks)
        if not inserted:
            logger.error(
                f"Failed to index chunks into vectordb for projectid: {projectid}"
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "signal": ResponseSignal.INSERT_INTO_VECTORDB_FAILURE.value,
                },
            )
        inserted_count += len(page_chunks)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
            "inserted_count": inserted_count,
        },
    )


@nlp_router.get("/index/info/{projectid}")
async def get_project_index_info(request: Request, projectid: str):
    project_model = await ProjectModel.create_instance(db_client=request.app.database)
    project = await project_model.get_or_create_project(projectid=projectid)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
        )

    nlp_controller = NLPController(
        client_vectordb=request.app.vectordb_client,
        client_generation=request.app.generation_client,
        client_embedding=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    collection_info = nlp_controller.get_vectordb_collection_info(project=project)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info,
        },
    )


@nlp_router.post("/index/search/{projectid}")
async def search_index(request: Request, projectid: str, search_request: SearchRequest):
    project_model = await ProjectModel.create_instance(db_client=request.app.database)
    project = await project_model.get_or_create_project(projectid=projectid)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
        )

    nlp_controller = NLPController(
        client_vectordb=request.app.vectordb_client,
        client_generation=request.app.generation_client,
        client_embedding=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    results = nlp_controller.search_vectordb_collection(
        project=project,
        text=search_request.text,
        limit=search_request.limit or 10,
    )
    if not results:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value,
                "results": [],
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
            "results": [res.dict() for res in results],
        },
    )


@nlp_router.post("/index/answer/{projectid}")
async def answer_index(request: Request, projectid: str, search_request: SearchRequest):
    project_model = await ProjectModel.create_instance(db_client=request.app.database)
    project = await project_model.get_or_create_project(projectid=projectid)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.PROJECT_NOT_FOUND.value},
        )

    nlp_controller = NLPController(
        client_vectordb=request.app.vectordb_client,
        client_generation=request.app.generation_client,
        client_embedding=request.app.embedding_client,
        template_parser=request.app.template_parser,
    )
    answer, full_prompt, chat_history = nlp_controller.answer_rag_query(
        project=project,
        query=search_request.text,
        limit=search_request.limit or 10,
    )
    if not answer:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.RAG_ANSWER_ERROR.value,
                "answer": "",
            },
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history,
        },
    )
