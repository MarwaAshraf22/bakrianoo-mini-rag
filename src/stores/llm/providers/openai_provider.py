import logging

from openai import OpenAI

from ..llm_enum import OpenAIEnum
from ..llm_interface import LLMInterface


class OpenAIProvider(LLMInterface):
    def __init__(
        self,
        api_key: str,
        api_url: str | None = None,
        default_in_max_chars: int = 1000,
        default_out_max_tokens: int = 1000,
        default_temperature: float = 0.1,
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.client = OpenAI(api_key=api_key, base_url=api_url)

        self.default_in_max_chars = default_in_max_chars
        self.default_out_max_tokens = default_out_max_tokens
        self.default_temperature = default_temperature

        self.generation_modelid = None
        self.embedding_modelid = None
        self.embedding_size = None

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
            self.logger.error("OpenAI client is not initialised.")
            return ""

        if not self.generation_modelid:
            self.logger.error("Generation model ID is not set.")
            return ""

        max_out_tokens = max_out_tokens or self.default_out_max_tokens
        temperature = temperature or self.default_temperature

        chat_history.append(self.construct_prompt(prompt, OpenAIEnum.USER.value))

        response = self.client.chat.completions.create(
            model=self.generation_modelid,
            messages=chat_history,
            max_tokens=max_out_tokens,
            temperature=temperature,
        )

        if not (
            response
            and response.choices
            and len(response.choices)
            and response.choices[0].message
            and response.choices[0].message.content
        ):
            self.logger.error("Invalid response from OpenAI chat completions API.")
            return ""

        return response.choices[0].message.content

    def process_text(self, text: str) -> str:
        return text[: self.default_in_max_chars].strip()

    def embed_text(self, text: str, document_type: str | None = None):
        if not self.client:
            self.logger.error("OpenAI client is not initialised.")
            return None

        if not self.embedding_modelid:
            self.logger.error("Embedding model ID is not set.")
            return None

        response = self.client.embeddings.create(
            model=self.embedding_modelid, input=text
        )

        if not (
            response
            and response.data
            and len(response.data)
            and response.data[0].embedding
        ):
            self.logger.error("Invalid response from OpenAI embeddings API.")
            return None
        
        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str) -> dict:
        return {
            "role": role,
            "content": self.process_text(prompt),
        }
