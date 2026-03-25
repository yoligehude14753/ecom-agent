from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: Literal["development", "production", "test"] = "development"
    SECRET_KEY: str = "dev-secret-key"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://ecomagent:ecomagent@localhost:5432/ecomagent"

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # LLM
    LLM_PROVIDER: Literal["openai", "anthropic", "gemini", "ollama"] = "openai"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1"

    # Amazon SP-API
    AMAZON_CLIENT_ID: str = ""
    AMAZON_CLIENT_SECRET: str = ""
    AMAZON_REFRESH_TOKEN: str = ""
    AMAZON_MARKETPLACE_ID: str = "ATVPDKIKX0DER"
    AMAZON_REGION: str = "us-east-1"
    AMAZON_SP_API_ENDPOINT: str = "https://sellingpartnerapi-na.amazon.com"

    # Amazon Advertising API
    AMAZON_ADS_CLIENT_ID: str = ""
    AMAZON_ADS_CLIENT_SECRET: str = ""
    AMAZON_ADS_REFRESH_TOKEN: str = ""
    AMAZON_ADS_PROFILE_ID: str = ""

    # Scraping
    SCRAPER_PROXY_URL: str = ""
    SCRAPER_HEADLESS: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
