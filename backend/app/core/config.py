from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and the project .env file."""

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ApexFlow AI"
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://apexflow:apexflow@localhost:5432/apexflow"


@lru_cache
def get_settings() -> Settings:
    return Settings()
