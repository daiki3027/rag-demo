"""Run the 60-question evaluation from the command line.

Usage (from backend/):
    python scripts/run_eval.py --provider dummy
    OPENAI_API_KEY=sk-... python scripts/run_eval.py --provider openai

OpenAI embeddings are cached under data/eval_cache/, so re-running costs
nothing and gives the same numbers (the dummy provider is deterministic and
is not cached). Results are written to
eval_results/<provider>.json and eval_results/<provider>.md.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.core.settings import Settings  # noqa: E402
from app.rag.embeddings import EmbeddingProvider, provider_from_settings  # noqa: E402
from app.rag.eval import read_qa, sweep_thresholds  # noqa: E402
from app.rag.retrieve import rank  # noqa: E402
from app.rag.store import read_documents  # noqa: E402
from app.rag.types import SearchResult, VectorRecord, Vector  # noqa: E402

DEFAULT_THRESHOLDS = [round(0.10 + 0.05 * i, 2) for i in range(15)]  # 0.10 .. 0.80


class CachedEmbedder:
    """Wraps a provider and stores vectors keyed by the text's hash.

    With cache_path=None nothing is stored (used for the deterministic dummy provider).
    """

    def __init__(self, provider: EmbeddingProvider, cache_path: Optional[Path]) -> None:
        self.provider = provider
        self.cache_path = cache_path
        self.cache: Dict[str, Vector] = {}
        self.api_calls = 0
        if cache_path is not None and cache_path.exists():
            for line in cache_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    self.cache[row["key"]] = row["vector"]

    @staticmethod
    def key(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def embed(self, texts: Sequence[str]) -> List[Vector]:
        missing = [t for t in dict.fromkeys(texts) if self.key(t) not in self.cache]
        if missing:
            self.api_calls += 1
            for text, vector in zip(missing, self.provider.embed_texts(missing)):
                self.cache[self.key(text)] = vector
            if self.cache_path is not None:
                self.cache_path.parent.mkdir(parents=True, exist_ok=True)
                with self.cache_path.open("w", encoding="utf-8") as f:
                    for k in sorted(self.cache):
                        f.write(json.dumps({"key": k, "vector": self.cache[k]}) + "\n")
        return [self.cache[self.key(t)] for t in texts]


def pct(x: float) -> str:
    return f"{x * 100:.0f}%"


def to_markdown(provider: str, model: str, rows: List[dict], failures: List[dict], default_threshold: float) -> str:
    lines = [
        f"# 評価結果: {provider}（{model}）",
        "",
        "| 閾値 | Hit@1 | Hit@5 | 正しく答えた | 誤って断った | 断れた（全体） | noise | hallucination | boundary | 全体の正解率 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        sub = r["no_answer_by_subtype"]
        lines.append(
            f"| {r['threshold']:.2f} | {pct(r['hit_at_1'])} | {pct(r['hit_at_k'])} | {pct(r['answered_correctly'])} | "
            f"{pct(r['false_refusal'])} | {pct(r['no_answer_accuracy'])} | {pct(sub.get('noise', 0))} | "
            f"{pct(sub.get('hallucination', 0))} | {pct(sub.get('boundary', 0))} | {pct(r['overall_accuracy'])} |"
        )
    lines += ["", f"## 閾値 {default_threshold:.2f} での失敗例", ""]
    lines += ["| 種類 | 質問 | 期待 | 1位の文書（スコア） |", "| --- | --- | --- | --- |"]
    for f in failures:
        lines.append(f"| {f['kind']} | {f['question']} | {f['expected']} | {f['top_doc']}（{f['top_score']:.3f}） |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--provider", choices=["dummy", "openai"], default="dummy")
    parser.add_argument("--thresholds", type=str, default=",".join(str(t) for t in DEFAULT_THRESHOLDS))
    parser.add_argument("--default-threshold", type=float, default=None,
                        help="threshold used for the failure list (default: RETRIEVER_THRESHOLD)")
    parser.add_argument("--out-dir", type=Path, default=BACKEND_DIR / "eval_results")
    args = parser.parse_args()

    settings = Settings(embedding_provider=args.provider)
    provider = provider_from_settings(settings)
    model = getattr(provider, "model", f"dummy-{settings.embedding_dim}d")
    cache_path = None if args.provider == "dummy" else settings.data_dir / "eval_cache" / f"{model}.jsonl"
    embedder = CachedEmbedder(provider, cache_path)

    documents = read_documents(settings.seed_dir / "documents.jsonl")
    qa_items = read_qa(settings.seed_dir / "qa.jsonl")
    doc_vectors = embedder.embed([d.text for d in documents])
    records = [VectorRecord(d.doc_id, d.title, d.text, v) for d, v in zip(documents, doc_vectors)]
    query_vectors = embedder.embed([q.question for q in qa_items])
    ranked: List[List[SearchResult]] = [rank(v, records, settings.retriever_top_k) for v in query_vectors]

    thresholds = [float(t) for t in args.thresholds.split(",")]
    rows = sweep_thresholds(qa_items, ranked, thresholds)

    default_threshold = args.default_threshold if args.default_threshold is not None else settings.retriever_threshold
    failures = []
    for item, results in zip(qa_items, ranked):
        top = results[0]
        answered = top.score >= default_threshold
        if item.gold_doc_id:
            if not (answered and top.doc_id == item.gold_doc_id):
                if not answered:
                    kind = "誤って断った"
                elif any(r.doc_id == item.gold_doc_id for r in results):
                    kind = "正解が2位以下（別の文書を回答）"
                else:
                    kind = "上位5件に正解なし"
                failures.append({"kind": kind, "question": item.question, "expected": item.gold_doc_id,
                                 "top_doc": top.doc_id, "top_score": top.score})
        elif answered:
            failures.append({"kind": f"断れなかった（{item.subtype}）", "question": item.question,
                             "expected": "（回答なし）", "top_doc": top.doc_id, "top_score": top.score})

    args.out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"provider": args.provider, "model": model, "top_k": settings.retriever_top_k,
               "default_threshold": default_threshold, "rows": rows, "failures": failures,
               "top_scores": [{"question": q.question, "gold": q.gold_doc_id, "subtype": q.subtype,
                               "top": [[r.doc_id, round(r.score, 4)] for r in res]}
                              for q, res in zip(qa_items, ranked)]}
    (args.out_dir / f"{args.provider}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md = to_markdown(args.provider, model, rows, failures, default_threshold)
    (args.out_dir / f"{args.provider}.md").write_text(md, encoding="utf-8")
    print(md)
    print(f"embedding API calls this run: {embedder.api_calls}", file=sys.stderr)


if __name__ == "__main__":
    main()
