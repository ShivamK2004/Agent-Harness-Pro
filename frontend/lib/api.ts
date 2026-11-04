export type TraceEvent = {
  stage: string;
  status: string;
  message: string;
  timestamp?: string;
  details?: Record<string, unknown>;
};

export type Source = {
  source_id: string;
  path: string;
  title: string;
  start_line: number;
  end_line: number;
  text: string;
  score?: number;
};

export type AgentRun = {
  run_id: string;
  task: string;
  provider: string;
  model: string;
  answer: string;
  status: string;
  latency_ms: number;
  trace?: TraceEvent[];
  sources?: Source[];
  tools_used?: string[];
  evaluation?: Record<string, number | string | string[] | boolean | null>;
  created_at?: string;
  verifier_notes?: string;
};

export type BenchmarkMetrics = {
  overall_score?: number;
  keyword_coverage?: number;
  token_overlap?: number;
  citation_score?: number;
  tool_use_score?: number;
  latency_ms?: number;
  [key: string]: number | string | string[] | boolean | null | undefined;
};

export type BenchmarkResult = {
  task_id: string;
  task: string;
  run_id?: string | null;
  answer?: string;
  status?: string;
  error?: string | null;
  task_type?: string | null;
  metrics?: BenchmarkMetrics | null;
};

export type BenchmarkResponse = {
  dataset: string;
  total_tasks: number;
  successful_tasks?: number;
  failed_tasks?: number;
  aggregate: Record<string, number>;
  results: BenchmarkResult[];
};

export type HealthResponse = {
  status: string;
  app: string;
  configured_provider: string;
  provider: Record<string, unknown>;
};

export type DashboardStats = {
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  success_rate: number;
  average_latency_ms: number;
  average_score: number;
  recent_runs: AgentRun[];
};

const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
      cache: "no-store",
    });
  } catch {
    throw new Error(`Cannot reach the FastAPI backend at ${API_BASE}. Start the backend and try again.`);
  }

  const raw = await response.text();
  let payload: unknown = null;
  try {
    payload = raw ? JSON.parse(raw) : null;
  } catch {
    payload = raw;
  }
  if (!response.ok) {
    const detail = typeof payload === "object" && payload !== null && "detail" in payload
      ? String((payload as { detail: unknown }).detail)
      : typeof payload === "string" ? payload : `Request failed (${response.status})`;
    throw new Error(detail);
  }
  return payload as T;
}

export const api = {
  health: () => request<HealthResponse>("/health"),
  stats: () => request<DashboardStats>("/stats"),
  tools: () => request<{ tools: Array<Record<string, unknown>> }>("/tools"),
  runs: (limit = 100) => request<{ runs: AgentRun[] }>(`/runs?limit=${limit}`),
  run: (id: string) => request<AgentRun>(`/runs/${encodeURIComponent(id)}`),
  chat: (task: string, provider: string) => request<AgentRun>("/chat", {
    method: "POST", body: JSON.stringify({ task, provider }),
  }),
  benchmark: (provider: string) => request<BenchmarkResponse>("/benchmark/run", {
    method: "POST", body: JSON.stringify({ provider }),
  }),
};
