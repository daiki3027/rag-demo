from datetime import datetime
import json
from pathlib import Path
from typing import List

from ..core.settings import Settings
from .embeddings import provider_from_settings
from .store import read_documents, write_vectors
from .types import VectorRecord


def reindex(settings: Settings) -> dict:
    documents_path: Path = settings.seed_dir / "documents.jsonl"
    documents = read_documents(documents_path)
    provider = provider_from_settings(settings)
    texts = [doc.text for doc in documents]
    vectors = provider.embed_texts(texts)
    records: List[VectorRecord] = []
    for doc, vector in zip(documents, vectors):
        records.append(
            VectorRecord(doc_id=doc.doc_id, title=doc.title, text=doc.text, vector=vector)
        )
    index_path = settings.index_dir / "vectors.jsonl"
    write_vectors(index_path, records)
    vector_dim = len(records[0].vector) if records else settings.embedding_dim
    meta = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "embedding_provider": settings.embedding_provider,
        "embedding_dim": vector_dim,
        "vector_count": len(records),
    }
    meta_path = settings.index_dir / "meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return meta
