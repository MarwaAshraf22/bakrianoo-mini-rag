from abc import ABC, abstractmethod


class LLMInterface(ABC):
    @abstractmethod
    def set_generation_model(self, modelid: str):
        pass

    @abstractmethod
    def set_embedding_model(self, modelid: str, embedding_size: int):
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        chat_history: list[dict] = [],
        max_out_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str | None = None):
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str) -> dict:
        pass
