from dataclasses import dataclass, asdict
from typing import List, Optional

Vector = List[float]


@dataclass
class Document:
    doc_id: str
    title: str
    text: str


@dataclass
class VectorRecord:
    doc_id: str
    title: str
    text: str
    vector: Vector


@dataclass
class SearchResult:
    doc_id: str
    title: str
    text: str
    score: float


@dataclass
class Usage:
    model: str
    prompt_tokens: int
    total_tokens: int
    cost_usd: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvaluationItem:
    question: str
    gold_doc_id: Optional[str]
    subtype: Optional[str] = None
