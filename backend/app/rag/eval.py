import json
from pathlib import Path
from typing import Dict, List, Optional

from .retrieve import SearchEngine
from .types import EvaluationItem, SearchResult


def read_qa(path: Path) -> List[EvaluationItem]:
    items: List[EvaluationItem] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            payload = json.loads(line)
            items.append(
                EvaluationItem(
                    question=payload["question"],
                    gold_doc_id=payload.get("gold_doc_id"),
                    subtype=payload.get("subtype"),
                )
            )
    return items


def summarize_top(results: List[SearchResult]) -> List[Dict[str, object]]:
    return [
        {"doc_id": r.doc_id, "score": r.score, "text": r.text}
        for r in results
    ]


def evaluate(search_engine: SearchEngine, qa_items: List[EvaluationItem], threshold: float) -> Dict[str, object]:
    pos_total = 0
    neg_total = 0
    hit = 0
    neg_success = 0
    failures: List[Dict[str, object]] = []

    for item in qa_items:
        results = search_engine.search(item.question)
        if item.gold_doc_id:
            pos_total += 1
            matched = any(r.doc_id == item.gold_doc_id for r in results)
            if matched:
                hit += 1
            else:
                failures.append(
                    {
                        "question": item.question,
                        "expected": item.gold_doc_id,
                        "got": summarize_top(results),
                        "subtype": item.subtype,
                        "type": "positive",
                    }
                )
        else:
            neg_total += 1
            max_score = results[0].score if results else 0.0
            if max_score < threshold:
                neg_success += 1
            else:
                failures.append(
                    {
                        "question": item.question,
                        "max_score": max_score,
                        "top": summarize_top(results),
                        "subtype": item.subtype,
                        "type": "negative",
                    }
                )

    total = pos_total + neg_total
    return {
        "total": total,
        "positive_total": pos_total,
        "negative_total": neg_total,
        "hit_at_5": hit / pos_total if pos_total else 0.0,
        "no_answer_accuracy": neg_success / neg_total if neg_total else 0.0,
        "failures": failures,
    }
