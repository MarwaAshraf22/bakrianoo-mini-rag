from helpers.config import Settings

from .llm_enum import LLMEnum
from .providers import CohereProvider, OpenAIProvider


class LLMProviderFactory:
    def __init__(self, config: Settings):
        self.config = config

    def create(self, provider: str):
        provider = provider.upper()
        if provider == LLMEnum.OPENAI.value:
            return OpenAIProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_in_max_chars=self.config.INPUT_DEFAULT_MAX_TOKENS,
                default_out_max_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
            )
        elif provider == LLMEnum.COHERE.value:
            return CohereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_in_max_chars=self.config.INPUT_DEFAULT_MAX_TOKENS,
                default_out_max_tokens=self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_temperature=self.config.GENERATION_DEFAULT_TEMPERATURE,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
