"use client";

import { useState } from "react";
import { runReindex, ReindexResult } from "@/lib/api";

export default function ReindexPanel() {
  const [result, setResult] = useState<ReindexResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleReindex = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await runReindex();
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
        <span className="badge">Admin</span>
        <h2 style={{ margin: 0 }}>Reindex</h2>
      </div>
      <p style={{ color: "var(--muted)", marginTop: 0 }}>
        seed データからベクトルインデックスを再生成します。
      </p>
      <button className="button" onClick={handleReindex} disabled={loading}>
        {loading ? "実行中..." : "Reindex 実行"}
      </button>
      {error && <p style={{ color: "#b91c1c" }}>{error}</p>}
      {result && (
        <div style={{ marginTop: 12, fontSize: 14 }}>
          <div>status: {result.status}</div>
          <div>updated_at: {result.meta.updated_at}</div>
          <div>provider: {result.meta.embedding_provider}</div>
          <div>dim: {result.meta.embedding_dim}</div>
          <div>vectors: {result.meta.vector_count}</div>
          {result.meta.usage && (
            <div style={{ marginTop: 6, color: "var(--muted)" }}>
              <span style={{ display: "inline-block", marginRight: 10 }}>
                model: {result.meta.usage.model ?? "-"}
              </span>
              <span style={{ display: "inline-block", marginRight: 10 }}>
                tokens: {result.meta.usage.total_tokens}
              </span>
              <span style={{ display: "inline-block", marginRight: 10 }}>
                {(() => {
                  const yen = result.meta.usage!.cost_usd * 155;
                  return `cost: $${result.meta.usage!.cost_usd.toFixed(8)} (¥${yen.toFixed(8)})`;
                })()}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
