from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str
    FILE_ALLOWED_TYPES: list[str]
    FILE_MAX_SIZE_MB: int
    FILE_DEFAULT_CHUNK_SIZE: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        model_config = SettingsConfigDict(
            extra="ignore",
        )


def get_settings() -> Settings:
    """_summary_

    :return: _description_
    :rtype: Settings
    """
    return Settings()
