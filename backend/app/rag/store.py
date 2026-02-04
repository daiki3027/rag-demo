import json
from pathlib import Path
from typing import Iterable, List

from .types import Document, VectorRecord


def read_documents(path: Path) -> List[Document]:
    documents: List[Document] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            payload = json.loads(line)
            documents.append(
                Document(
                    doc_id=payload["doc_id"],
                    title=payload.get("title", ""),
                    text=payload["text"],
                )
            )
    return documents


def write_vectors(path: Path, vectors: Iterable[VectorRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for record in vectors:
            f.write(
                json.dumps(
                    {
                        "doc_id": record.doc_id,
                        "title": record.title,
                        "text": record.text,
                        "vector": record.vector,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )


def read_vectors(path: Path) -> List[VectorRecord]:
    records: List[VectorRecord] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            payload = json.loads(line)
            records.append(
                VectorRecord(
                    doc_id=payload["doc_id"],
                    title=payload.get("title", ""),
                    text=payload["text"],
                    vector=list(payload["vector"]),
                )
            )
    return records
