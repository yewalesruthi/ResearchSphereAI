from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    groq_api_key: str = ""
    secret_key: str = "change-me-in-production"
    database_url: str = "sqlite:///./researchsphere.db"
    chroma_persist_dir: str = "./chroma_db"
    upload_dir: str = "./uploads"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    llm_model: str = "llama-3.3-70b-versatile"
    vision_model: str = "llava-v1.5-7b-4096-preview"
    whisper_model: str = "base"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    environment: str = "development"
    chunk_size: int = 512
    chunk_overlap: int = 50
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
