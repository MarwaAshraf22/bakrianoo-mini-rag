import logging
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from controllers.base import BaseController
from controllers.project import ProjectController
from models import ProcessingEnums

logger = logging.getLogger("uvicorn.error")  # Use the same logger as in routes


class ProcessController(BaseController):
    def __init__(self, projectid: str):
        super().__init__()
        self.projectid = projectid
        self.path_project = ProjectController().get_dir_project(projectid=projectid)

    def get_file_extension(self, fileid: str) -> str:
        return Path(fileid).suffix

    def get_file_loader(self, fileid: str):
        extension = self.get_file_extension(fileid=fileid).lower()
        filepath = self.path_project / fileid
        if not filepath.exists():
            raise FileNotFoundError(str(filepath))
        if extension == ProcessingEnums.TXT.value:
            return TextLoader(filepath, encoding="utf-8")
        elif extension == ProcessingEnums.PDF.value:
            return PyMuPDFLoader(filepath)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")

    def load_file_content(self, fileid: str) -> list:
        try:
            loader = self.get_file_loader(fileid=fileid)
            return loader.load()
        except FileNotFoundError as fnfe:
            logger.error(f"File not found: {repr(fnfe)}")
            return []
        except ValueError as ve:
            logger.error(f"File loading error: {repr(ve)}")
            return []

    def process_file_content(
        self,
        file_content: list,
        fileid: str,
        chunk_size: int = 100,
        overlap_size: int = 20,
    ):
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=overlap_size,
                length_function=len,
            )
            file_content_text, file_content_meta = (
                [doc.page_content for doc in file_content],
                [doc.metadata for doc in file_content],
            )
            chunks = text_splitter.create_documents(
                file_content_text, metadatas=file_content_meta
            )
            return chunks
        except Exception as e:
            logger.error(f"Error processing file {fileid}: {repr(e)}")
            return None
