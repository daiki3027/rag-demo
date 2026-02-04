import hashlib
import math
from abc import ABC, abstractmethod
from typing import Iterable, List, Sequence

from ..core.settings import Settings
from .types import Vector


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: Sequence[str]) -> List[Vector]:
        raise NotImplementedError

    def embed_text(self, text: str) -> Vector:
        return self.embed_texts([text])[0]


class DummyEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int = 128) -> None:
        self.dimension = dimension

    def _tokenize(self, text: str) -> Iterable[str]:
        text = text.lower()
        for ch in text:
            if ch.isspace():
                continue
            yield ch

    def _vector_for_tokens(self, tokens: Iterable[str]) -> Vector:
        vec = [0.0 for _ in range(self.dimension)]
        for token in tokens:
            digest = hashlib.md5(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest, "big") % self.dimension
            vec[bucket] += 1.0
        norm = math.sqrt(sum(x * x for x in vec))
        if norm == 0:
            return vec
        return [x / norm for x in vec]

    def embed_texts(self, texts: Sequence[str]) -> List[Vector]:
        return [self._vector_for_tokens(self._tokenize(text)) for text in texts]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str, model: str = "text-embedding-3-small") -> None:
        try:
            from openai import OpenAI  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("openai package is required for OpenAI embeddings") from exc
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_texts(self, texts: Sequence[str]) -> List[Vector]:
        response = self.client.embeddings.create(model=self.model, input=list(texts))
        return [item.embedding for item in response.data]


def provider_from_settings(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for openai provider")
        return OpenAIEmbeddingProvider(api_key=settings.openai_api_key)
    return DummyEmbeddingProvider(dimension=settings.embedding_dim)
