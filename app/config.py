"""App settings, loaded from environment variables / the .env file."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "dev-only-change-me"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./slyce.db"

    anthropic_api_key: str = ""
    llm_model: str = "claude-haiku-5-5"

    trading212_api_key: str = ""
    trading212_api_secret: str = ""
    trading212_base_url: str = "https://demo.trading212.com/api/v0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
