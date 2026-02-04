"use client";

import { FormEvent, useMemo, useState } from "react";
import { runQuery, Source } from "@/lib/api";
import Sources from "./Sources";

export default function ChatBox() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const topScore = useMemo(() => (sources[0] ? sources[0].score : null), [sources]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await runQuery(question.trim());
      setAnswer(res.answer);
      setSources(res.sources || []);
    } catch (err: any) {
      setError(err.message || "エラーが発生しました");
      setAnswer(null);
      setSources([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-2" style={{ gap: "20px" }}>
      <div className="panel">
        <div className="section-title">
          <span className="badge">Chat</span>
          <h2 style={{ margin: 0 }}>質問する</h2>
        </div>
        <form onSubmit={handleSubmit} className="grid" style={{ gap: "12px" }}>
          <textarea
            rows={3}
            placeholder="例: ログインには何が必要ですか？"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
            <button className="button" type="submit" disabled={loading}>
              {loading ? "送信中..." : "送信"}
            </button>
            <span style={{ color: "var(--muted)", fontSize: 14 }}>
              top_k=5 / thresholdはバックエンドの環境変数で変更可能
            </span>
          </div>
        </form>
        {error && <p style={{ color: "#b91c1c" }}>{error}</p>}
      </div>
      <div className="panel">
        <div className="section-title">
          <span className="badge">Answer</span>
          <h2 style={{ margin: 0 }}>回答</h2>
        </div>
        {answer ? (
          <>
            <p style={{ lineHeight: 1.6 }}>{answer}</p>
            <Sources sources={sources} />
            {topScore !== null && (
              <p style={{ color: "var(--muted)", fontSize: 13, marginTop: 8 }}>
                debug: max_score = {topScore.toFixed(3)}
              </p>
            )}
          </>
        ) : (
          <p style={{ color: "var(--muted)" }}>まだ回答はありません。質問を入力してください。</p>
        )}
      </div>
    </div>
  );
}
