export type Source = {
  doc_id: string;
  score: number;
  text: string;
};

export type QueryResult = {
  answer: string;
  sources: Source[];
};

export type EvalResult = {
  total: number;
  positive_total: number;
  negative_total: number;
  hit_at_5: number;
  no_answer_accuracy: number;
  failures: any[];
};

const BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

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
