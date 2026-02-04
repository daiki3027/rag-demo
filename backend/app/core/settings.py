from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "rag-v0"
    embedding_provider: Literal["dummy", "openai"] = Field("dummy", env="EMBEDDING_PROVIDER")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    retriever_threshold: float = Field(0.25, env="RETRIEVER_THRESHOLD")
    retriever_top_k: int = 5
    embedding_dim: int = Field(128, env="EMBEDDING_DIM")

    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    seed_dir: Path = data_dir / "seed"
    index_dir: Path = data_dir / "index"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
