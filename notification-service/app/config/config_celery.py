from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class CelerySettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    CELERY_BROKER_DB: int

    @property
    def broker_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.CELERY_BROKER_DB}"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent / ".env")
    )
settings = CelerySettings()
