import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.rag.embeddings import DummyEmbeddingProvider  # noqa: E402
from app.rag.eval import sweep_thresholds  # noqa: E402
from app.rag.retrieve import cosine_similarity, rank  # noqa: E402
from app.rag.types import EvaluationItem, SearchResult, VectorRecord  # noqa: E402


def result(doc_id: str, score: float) -> SearchResult:
    return SearchResult(doc_id=doc_id, title="", text="", score=score)


class TestRetrieve(unittest.TestCase):
    def test_cosine_similarity(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [1, 0]), 1.0)
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)
        self.assertEqual(cosine_similarity([0, 0], [1, 0]), 0.0)

    def test_rank_orders_by_score_and_truncates(self):
        records = [
            VectorRecord("a", "", "", [1.0, 0.0]),
            VectorRecord("b", "", "", [0.0, 1.0]),
            VectorRecord("c", "", "", [0.7, 0.7]),
        ]
        top = rank([1.0, 0.0], records, top_k=2)
        self.assertEqual([r.doc_id for r in top], ["a", "c"])

    def test_rank_rejects_dimension_mismatch(self):
        with self.assertRaises(ValueError):
            rank([1.0, 0.0, 0.0], [VectorRecord("a", "", "", [1.0, 0.0])], top_k=1)


class TestDummyEmbedding(unittest.TestCase):
    def test_deterministic_and_normalized(self):
        provider = DummyEmbeddingProvider(dimension=32)
        a, b = provider.embed_texts(["ログイン", "ログイン"])
        self.assertEqual(a, b)
        self.assertAlmostEqual(sum(x * x for x in a), 1.0)


class TestSweepThresholds(unittest.TestCase):
    def setUp(self):
        self.items = [
            EvaluationItem("q1", "d1"),
            EvaluationItem("q2", "d2"),
            EvaluationItem("q3", None, "noise"),
            EvaluationItem("q4", None, "boundary"),
        ]
        self.ranked = [
            [result("d1", 0.9)],               # answerable, correct
            [result("x", 0.4), result("d2", 0.3)],  # answerable, gold ranked 2nd
            [result("y", 0.2)],                # unanswerable, low score
            [result("z", 0.6)],                # unanswerable, high score
        ]

    def test_low_threshold_answers_everything(self):
        row = sweep_thresholds(self.items, self.ranked, [0.1])[0]
        self.assertEqual(row["hit_at_k"], 1.0)
        self.assertEqual(row["hit_at_1"], 0.5)  # q2's gold is ranked second
        self.assertEqual(row["answered_correctly"], 0.5)
        self.assertEqual(row["no_answer_accuracy"], 0.0)

    def test_threshold_trades_refusals_for_misses(self):
        row = sweep_thresholds(self.items, self.ranked, [0.5])[0]
        self.assertEqual(row["answered_correctly"], 0.5)
        self.assertEqual(row["false_refusal"], 0.5)
        self.assertEqual(row["no_answer_by_subtype"], {"boundary": 0.0, "noise": 1.0})
        self.assertEqual(row["overall_accuracy"], 0.5)  # q1 answered + q3 refused, out of 4

    def test_hit_at_k_does_not_depend_on_threshold(self):
        rows = sweep_thresholds(self.items, self.ranked, [0.1, 0.5, 0.95])
        self.assertEqual({r["hit_at_k"] for r in rows}, {1.0})

    def test_length_mismatch(self):
        with self.assertRaises(ValueError):
            sweep_thresholds(self.items, self.ranked[:1], [0.1])


class TestRunEvalScript(unittest.TestCase):
    def test_dummy_run_writes_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(
                [sys.executable, str(BACKEND_DIR / "scripts" / "run_eval.py"),
                 "--provider", "dummy", "--out-dir", tmp],
                check=True, capture_output=True, cwd=BACKEND_DIR,
            )
            payload = json.loads((Path(tmp) / "dummy.json").read_text(encoding="utf-8"))
            self.assertEqual(len(payload["top_scores"]), 60)
            self.assertTrue((Path(tmp) / "dummy.md").exists())


if __name__ == "__main__":
    unittest.main()
