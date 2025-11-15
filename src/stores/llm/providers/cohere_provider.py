import logging

import cohere

from ..llm_enum import CohereEnum
from ..llm_interface import LLMInterface


class CohereProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        # api_url: str | None = None,
        default_in_max_chars: int = 1000,
        default_out_max_tokens: int = 1000,
        default_temperature: float = 0.1,
    ):
        self.api_key = api_key
        # self.api_url = api_url

        self.default_in_max_chars = default_in_max_chars
        self.default_out_max_tokens = default_out_max_tokens
        self.default_temperature = default_temperature

        self.generation_modelid = None
        self.embedding_modelid = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=api_key)
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, modelid: str):
        self.generation_modelid = modelid

    def set_embedding_model(self, modelid: str, embedding_size: int):
        self.embedding_modelid = modelid
        self.embedding_size = embedding_size

    def generate_text(
        self,
        prompt: str,
        chat_history: list[dict] = [],
        max_out_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        if not self.client:
            self.logger.error("Cohere client is not initialised.")
            return ""
        if not self.generation_modelid:
            self.logger.error("Generation model ID is not set.")
            return ""

        max_out_tokens = max_out_tokens or self.default_out_max_tokens
        temperature = temperature or self.default_temperature
        response = self.client.chat(
            model=self.generation_modelid,
            chat_history=chat_history,
            message=self.process_text(prompt),
            max_tokens=max_out_tokens,
            temperature=temperature,
        )
        if not response or not response.text:
            self.logger.error("Invalid response from Cohere chat API.")
            return ""

    def embed_text(self, text: str, document_type: str | None = None):
        if not self.client:
            self.logger.error("Cohere client is not initialised.")
            return None
        if not self.embedding_modelid:
            self.logger.error("Embedding model ID is not set.")
            return None

        input_type = CohereEnum.DOCUMENT.value
        if document_type == CohereEnum.QUERY.value:
            input_type = CohereEnum.QUERY.value

        response = self.client.embed(
            model=self.embedding_modelid,
            texts=[self.process_text(text)],
            input_type=input_type,
            embedding_types=["float"],
        )
        if not (response and response.embeddings and response.embeddings.float):
            self.logger.error("Invalid response from Cohere embeddings API.")
            return None
        
        return response.embeddings.float[0]

    def construct_prompt(self, prompt: str, role: str) -> dict:
        return {
            "role": role,
            "text": self.process_text(prompt),
        }

    def process_text(self, text: str) -> str:
        return text[: self.default_in_max_chars].strip()
