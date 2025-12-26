import json

from models.db_schemas import DataChunk, Project
from stores.llm.llm_enum import DocumentTypeEnum
from stores.llm.llm_interface import LLMInterface
from stores.llm.templates.template_parser import TemplateParser
from stores.vectordb.vectordb_interface import VectorDBInterface

from .base import BaseController


class NLPController(BaseController):
    def __init__(
        self,
        client_vectordb: VectorDBInterface,
        client_generation: LLMInterface,
        client_embedding: LLMInterface,
        template_parser: TemplateParser,
    ):
        super().__init__()
        self.client_vectordb = client_vectordb
        self.client_generation = client_generation
        self.client_embedding = client_embedding
        self.template_parser = template_parser

    def create_collection_name(self, projectid: str) -> str:
        return f"collection_{projectid}".strip().lower()

    def reset_vectordb_collection(self, project: Project):
        collection_name = self.create_collection_name(str(project.projectid))
        self.client_vectordb.drop_collection(collection_name)

    def get_vectordb_collection_info(self, project: Project):
        collection_name = self.create_collection_name(str(project.projectid))
        info = self.client_vectordb.collection_info(collection_name)
        return json.loads(json.dumps(info, default=lambda x: x.__dict__))

    def index_into_vectordb(
        self,
        project: Project,
        chunks: list[DataChunk],
        chunkids: list[int],
        do_reset: bool = False,
    ) -> bool:
        # get collection name
        collection_name = self.create_collection_name(str(project.projectid))
        # manage items
        texts, metadata = list(
            zip(*[(chunk.chunk_text, chunk.chunk_metadata) for chunk in chunks])
        )
        vectors = [
            self.client_embedding.embed_text(
                text=text, document_type=DocumentTypeEnum.DOCUMENT.value
            )
            for text in texts
        ]

        # upsert collection
        self.client_vectordb.create_collection(
            collection_name=collection_name,
            embedding_size=self.client_embedding.embedding_size,
            do_reset=do_reset,
        )
        # insert into db
        self.client_vectordb.insert_many(
            collection_name=collection_name,
            vectors=vectors,
            metadata=metadata,
            texts=texts,
            recordids=chunkids,
        )
        return True

    def search_vectordb_collection(self, project: Project, text: str, limit: int = 10):
        collection_name = self.create_collection_name(str(project.projectid))
        query_vector = self.client_embedding.embed_text(
            text=text, document_type=DocumentTypeEnum.QUERY.value
        )
        if not (query_vector and len(query_vector)):
            return []

        results = self.client_vectordb.query_by_vector(
            collection_name=collection_name,
            vector=query_vector,
            limit=limit,
        )
        if not results:
            return []

        # return json.loads(json.dumps(results, default=lambda x: x.__dict__))
        return results

    def answer_rag_query(
        self, project: Project, query: str, limit: int = 10
    ) -> tuple[str, str, list[dict]]:
        retrieved_docs = self.search_vectordb_collection(
            project=project,
            text=query,
            limit=limit,
        )
        if not (retrieved_docs and len(retrieved_docs)):
            return "", "", []

        # construct sys prompt
        sys_prompt = self.template_parser.get("rag", "system_prompt")
        # construct doc prompt
        docs_prompt = "\n".join(
            [
                self.template_parser.get(
                    "rag",
                    "document_prompt",
                    _vars={
                        "doc_num": i,
                        "chunk_text": self.client_generation.process_text(doc.text),
                    },
                )
                for i, doc in enumerate(retrieved_docs)
            ]
        )
        # construct footer prompt
        footer_prompt = self.template_parser.get(
            "rag", "footer_prompt", _vars={"user_query": query}
        )

        chat_history = [
            self.client_generation.construct_prompt(
                sys_prompt, self.client_generation.enums.SYSTEM.value
            )
        ]

        full_prompt = "\n\n".join([docs_prompt, footer_prompt])

        print(
            f"[RAG] full prompt constructed:\n{full_prompt}\n{'-' * 50}\n", chat_history
        )

        answer = self.client_generation.generate_text(
            prompt=full_prompt, chat_history=chat_history
        )

        return answer, full_prompt, chat_history
