import ChatBox from "./components/ChatBox";
import ReindexPanel from "./components/ReindexPanel";

export default function HomePage() {
  return (
    <div className="grid" style={{ gap: 20 }}>
      <header className="panel" style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: 28, marginBottom: 4 }}>RAG v0</h1>
          <p style={{ color: "var(--muted)", margin: 0 }}>
            ベクトル検索 + cosine 全件走査。top_k=5 / threshold=0.25（envで変更可）。
          </p>
        </div>
        <a className="button" href="/eval" style={{ textDecoration: "none" }}>
          評価ページへ
        </a>
      </header>
      <div className="grid" style={{ gap: 20 }}>
        <ChatBox />
        <ReindexPanel />
      </div>
    </div>
  );
}
