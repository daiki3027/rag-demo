# RAG v0

最小構成の RAG (ベクトル検索 + cosine 全件走査) デモです。バックエンドは FastAPI、フロントエンドは Next.js(App Router)で実装しています。

## ディレクトリ
- `backend/` FastAPI + インデクサ
- `frontend/` Next.js UI
- `backend/data/seed/` テスト用ドキュメント50件(`documents.jsonl`)とQA60問(`qa.jsonl`)
- `backend/data/index/` ベクトルインデックス出力先(`vectors.jsonl`, `meta.json`)

## Docker でまとめて起動する
- ビルド & 起動: `docker compose up --build`
- バックエンド: http://localhost:8000
- フロントエンド: http://localhost:3000 (バックエンドへの接続先は `NEXT_PUBLIC_BACKEND_URL` で変更可)
- 生成されたインデックスはホストの `backend/data` と共有されるため、コンテナ再作成後も維持されます。

## 1. バックエンド起動
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # EMBEDDING_PROVIDER=dummy などを設定
uvicorn app.main:app --reload
```

### インデックス作成
初回はインデックスが無いので再構築してください。
```bash
curl -X POST http://localhost:8000/api/reindex
```
`backend/data/index/` に `vectors.jsonl` が出力されます。

## 2. フロントエンド起動
```bash
cd frontend
npm install
cp .env.local.example .env.local  # NEXT_PUBLIC_BACKEND_URL を必要に応じ変更
npm run dev
```
- `http://localhost:3000/` : Chat 画面（質問フォーム + sources表示）
- `http://localhost:3000/eval` : 評価画面（Hit@5 / No-answer accuracy, failures）

## 3. API
- `POST /api/query` {"question": "..."} → answer + sources(top5)。`max_score < threshold` なら sources 空＋拒否文。
- `POST /api/reindex` → seed から再インデックス。
- `POST /api/eval` → 60問評価結果を返却。

## 4. パラメータ調整
- `RETRIEVER_THRESHOLD` (デフォルト 0.25)
- `EMBEDDING_PROVIDER` (`dummy` または `openai`)
- `EMBEDDING_DIM` (dummy用ベクトル次元)

環境変数は `backend/.env` で設定できます。
