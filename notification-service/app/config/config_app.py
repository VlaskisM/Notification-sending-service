from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    PAGINATION_DEFAULT_LIMIT: int = 5
    PAGINATION_MAX_LIMIT: int = 10

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        extra="ignore"
    )


settings = AppSettings()
