import math
from pathlib import Path
from typing import List

from ..core.settings import Settings
from .embeddings import EmbeddingProvider, provider_from_settings
from .store import read_vectors
from .types import SearchResult, VectorRecord


def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def rank(query_vec: List[float], records: List[VectorRecord], top_k: int) -> List[SearchResult]:
    scored = []
    for record in records:
        if len(record.vector) != len(query_vec):
            raise ValueError(
                f"Vector dimension mismatch: index={len(record.vector)}, query={len(query_vec)}. Re-run /api/reindex."
            )
        scored.append(
            SearchResult(
                doc_id=record.doc_id,
                title=record.title,
                text=record.text,
                score=cosine_similarity(query_vec, record.vector),
            )
        )
    scored.sort(key=lambda x: x.score, reverse=True)
    return scored[:top_k]


class SearchEngine:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.index_path: Path = settings.index_dir / "vectors.jsonl"
        self.embedding_provider = provider_from_settings(settings)
        self.last_usage = None

    def _load_index(self) -> List[VectorRecord]:
        if not self.index_path.exists():
            raise FileNotFoundError("Index not found. Run /api/reindex first.")
        return read_vectors(self.index_path)

    def search(self, query: str) -> List[SearchResult]:
        vectors = self._load_index()
        query_vec = self.embedding_provider.embed_text(query)
        self.last_usage = getattr(self.embedding_provider, "last_usage", None)
        return rank(query_vec, vectors, self.settings.retriever_top_k)
