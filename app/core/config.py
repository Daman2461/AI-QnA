from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator
import secrets
from functools import lru_cache
import os


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "AI Document Q&A System"
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # Mistral (replacing OpenAI)
    MISTRAL_API_KEY: str = ""
    MISTRAL_MODEL_NAME: str = "mistral-tiny"

    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENV: str
    PINECONE_INDEX_NAME: str

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings() 