import { Source } from "@/lib/api";

export default function Sources({ sources }: { sources: Source[] }) {
  if (!sources.length) {
    return <p style={{ color: "var(--muted)", fontSize: 14 }}>根拠となるソースはありません。</p>;
  }

  return (
    <div style={{ marginTop: 12 }}>
      <h3 style={{ fontSize: 16, marginBottom: 8 }}>Sources</h3>
      <div className="grid" style={{ gap: 10 }}>
        {sources.map((source) => (
          <div key={source.doc_id + source.score} className="panel" style={{ padding: "10px 12px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <strong>{source.doc_id}</strong>
              <span style={{ color: "var(--muted)", fontSize: 13 }}>score {source.score.toFixed(3)}</span>
            </div>
            <p style={{ margin: "6px 0 0", lineHeight: 1.4 }}>{source.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
