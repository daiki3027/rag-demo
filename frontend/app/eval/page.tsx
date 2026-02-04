import EvalPanel from "../components/EvalPanel";

export default function EvalPage() {
  return (
    <div className="grid" style={{ gap: 20 }}>
      <header className="panel">
        <h1 style={{ fontSize: 26, marginBottom: 6 }}>評価</h1>
        <p style={{ color: "var(--muted)", margin: 0 }}>
          60問（ポジ30/ネガ30）のセットでHit@5とNo-answer accuracyを計算します。
        </p>
      </header>
      <EvalPanel />
    </div>
  );
}
