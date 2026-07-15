from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and the project .env file."""

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "ApexFlow AI"
    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://apexflow:apexflow@localhost:5432/apexflow"
    jwt_secret_key: SecretStr = SecretStr("change-this-development-secret")
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    passwordless_token_minutes: int = 15
    google_client_id: str | None = None
    google_client_secret: SecretStr | None = None
    google_redirect_uri: str = "http://localhost:8000/api/v1/auth/google/callback"
    allowed_google_workspace_domains: str = ""
    cors_origins: str = "http://localhost:3000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
