export type Source = {
  doc_id: string;
  score: number;
  text: string;
};

export type Usage = {
  model: string | null;
  prompt_tokens: number;
  total_tokens: number;
  cost_usd: number;
};

export type QueryResult = {
  answer: string;
  sources: Source[];
  usage?: Usage | null;
};

export type EvalResult = {
  total: number;
  positive_total: number;
  negative_total: number;
  hit_at_5: number;
  no_answer_accuracy: number;
  failures: any[];
  usage?: Usage | null;
};

// Choose API base URL depending on runtime:
// - Browser should call the host-exposed port (localhost:8000).
// - Server-side (Next dev server inside Docker) can reach the backend service name.
const BASE_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  (typeof window === "undefined" ? "http://backend:8000" : "http://localhost:8000");

async function postJson<T>(path: string, body?: any): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export async function runQuery(question: string): Promise<QueryResult> {
  return postJson<QueryResult>("/api/query", { question });
}

export async function runEval(): Promise<EvalResult> {
  return postJson<EvalResult>("/api/eval");
}

export type ReindexResult = {
  status: string;
  meta: {
    updated_at: string;
    embedding_provider: string;
    embedding_dim: number;
    vector_count: number;
    usage?: Usage | null;
  };
};

export async function runReindex(): Promise<ReindexResult> {
  return postJson<ReindexResult>("/api/reindex");
}
