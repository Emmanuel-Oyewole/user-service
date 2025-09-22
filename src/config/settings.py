from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    service_name: str = "User-service"
    service_mode: str = Literal["development", "production"]

    postgres_url: str = "postgres://username:password@host:port/database"
    redis_url:str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()