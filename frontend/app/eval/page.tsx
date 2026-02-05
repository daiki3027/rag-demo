import EvalPanel from "../components/EvalPanel";

export default function EvalPage() {
  return (
    <div className="grid" style={{ gap: 20 }}>
      <header className="panel" style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 26, marginBottom: 6 }}>評価</h1>
          <p style={{ color: "var(--muted)", margin: 0 }}>
            60問（ポジ30/ネガ30）のセットでHit@5とNo-answer accuracyを計算します。
          </p>
        </div>
        <a className="button" href="/" style={{ textDecoration: "none" }}>
          トップへ戻る
        </a>
      </header>
      <EvalPanel />
    </div>
  );
}
