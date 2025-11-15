from enum import Enum


class VectorDBEnum(Enum):
    QDRANT = "QDRANT"


class DistanceMetricEnum(Enum):
    COSINE = "cosine"
    DOT = "dot"


class LLMEnum(Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"


class OpenAIEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class CohereEnum(Enum):
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"

    DOCUMENT = "search_document"
    QUERY = "search_query"


class DocumentTypeEnum(Enum):
    DOCUMENT = "document"
    QUERY = "query"
