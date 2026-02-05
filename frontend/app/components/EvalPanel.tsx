"use client";

import { useState } from "react";
import { runEval, EvalResult } from "@/lib/api";

function formatPercent(value: number) {
  return `${(value * 100).toFixed(1)}%`;
}

export default function EvalPanel() {
  const [result, setResult] = useState<EvalResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRun = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await runEval();
      setResult(res);
    } catch (err: any) {
      setError(err.message || "エラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <div className="section-title">
        <span className="badge">Eval</span>
        <h2 style={{ margin: 0 }}>評価を実行</h2>
      </div>
      <p style={{ color: "var(--muted)", marginTop: 0 }}>Hit@5（ポジ）、No-answer accuracy（ネガ）を返します。</p>
      <button className="button" onClick={handleRun} disabled={loading}>
        {loading ? "実行中..." : "Run eval"}
      </button>
      {error && <p style={{ color: "#b91c1c" }}>{error}</p>}
      {result && (
        <div style={{ marginTop: 16 }}>
          <div className="panel" style={{ padding: "12px 14px", marginBottom: 12 }}>
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
              <div>
                <div style={{ fontSize: 13, color: "var(--muted)" }}>Hit@5</div>
                <div style={{ fontSize: 22, fontWeight: 700 }}>{formatPercent(result.hit_at_5)}</div>
              </div>
              <div>
                <div style={{ fontSize: 13, color: "var(--muted)" }}>No-answer accuracy</div>
                <div style={{ fontSize: 22, fontWeight: 700 }}>{formatPercent(result.no_answer_accuracy)}</div>
              </div>
              <div>
                <div style={{ fontSize: 13, color: "var(--muted)" }}>Total</div>
                <div style={{ fontSize: 22, fontWeight: 700 }}>{result.total}</div>
              </div>
            </div>
            {result.usage && (
              <div style={{ marginTop: 8, fontSize: 13, color: "var(--muted)" }}>
                <span style={{ display: "inline-block", marginRight: 10 }}>
                  model: {result.usage.model ?? "-"}
                </span>
                <span style={{ display: "inline-block", marginRight: 10 }}>
                  tokens: {result.usage.total_tokens}
                </span>
                <span style={{ display: "inline-block", marginRight: 10 }}>
                  {(() => {
                    const yen = result.usage!.cost_usd * 155;
                    return `cost: $${result.usage!.cost_usd.toFixed(8)} (¥${yen.toFixed(8)})`;
                  })()}
                </span>
              </div>
            )}
          </div>
          <h3 style={{ marginBottom: 8 }}>Failures ({result.failures.length})</h3>
          {result.failures.length === 0 ? (
            <p style={{ color: "var(--muted)" }}>すべて成功しました。</p>
          ) : (
            <div className="grid" style={{ gap: 10 }}>
              {result.failures.map((f, idx) => (
                <div key={idx} className="panel" style={{ padding: "12px 14px" }}>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <span className="badge">{f.type}</span>
                    {f.subtype && <span style={{ fontSize: 12, color: "var(--muted)" }}>{f.subtype}</span>}
                  </div>
                  <p style={{ margin: "6px 0", fontWeight: 600 }}>{f.question}</p>
                  {f.expected && <p style={{ margin: "2px 0", color: "var(--muted)" }}>期待: {f.expected}</p>}
                  {f.got && (
                    <div className="code-block">
                      {JSON.stringify(f.got, null, 2)}
                    </div>
                  )}
                  {f.top && (
                    <div className="code-block">
                      {JSON.stringify(f.top, null, 2)}
                    </div>
                  )}
                  {typeof f.max_score === "number" && (
                    <p style={{ margin: "4px 0", color: "var(--muted)" }}>max_score: {f.max_score.toFixed(3)}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
