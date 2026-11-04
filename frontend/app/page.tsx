"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { BrandMark } from "@/components/BrandMark";
import { AgentRun, BenchmarkResponse, DashboardStats, HealthResponse, api } from "@/lib/api";

type View = "overview" | "playground" | "benchmarks" | "runs" | "health";
type ToolInfo = Record<string, unknown>;

const NAV: { id: View; icon: string; label: string; group: string }[] = [
  { id: "overview", icon: "◫", label: "Overview", group: "Workspace" },
  { id: "playground", icon: "✳", label: "Agent Playground", group: "Workspace" },
  { id: "benchmarks", icon: "▤", label: "Benchmark Lab", group: "Evaluation" },
  { id: "runs", icon: "◷", label: "Run History", group: "Evaluation" },
  { id: "health", icon: "⌁", label: "System Health", group: "System" },
];

const TITLES: Record<View, { title: string; subtitle: string }> = {
  overview: { title: "Overview", subtitle: "Your agent operations at a glance." },
  playground: { title: "Agent Playground", subtitle: "Submit a task and inspect the multi-agent execution." },
  benchmarks: { title: "Benchmark Lab", subtitle: "Run the local evaluation dataset against a selected model provider." },
  runs: { title: "Run History", subtitle: "Inspect persisted agent executions, traces, and evaluation scores." },
  health: { title: "System Health", subtitle: "Check API connectivity, model configuration, and available tools." },
};

function formatMs(value?: number | null) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "—";
  return value >= 1000 ? `${(value / 1000).toFixed(1)} s` : `${Math.round(value)} ms`;
}

function formatDate(value?: string) {
  if (!value) return "Date unavailable";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function scoreLabel(value: unknown) {
  if (value === undefined || value === null || value === "") return "—";
  const number = typeof value === "number" ? value : Number(value);
  if (!Number.isFinite(number)) return "—";
  return `${Math.round(number * 100)}%`;
}

function Status({ value }: { value: string }) {
  const kind = value === "completed" || value === "ok" || value === "reachable" ? "completed" : value === "failed" || value === "error" || value === "unreachable" ? "failed" : "other";
  return <span className={`status ${kind}`}><span className="dot" />{value || "unknown"}</span>;
}

function StatCard({ icon, label, value, foot }: { icon: string; label: string; value: string; foot: string }) {
  return <div className="card stat-card"><div className="stat-head"><span>{label}</span><span className="stat-icon">{icon}</span></div><div className="stat-value">{value}</div><div className="stat-foot">{foot}</div></div>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div className="mini-metric"><div className="mini-metric-label">{label}</div><div className="mini-metric-value">{value}</div></div>;
}

function RunDetails({ run }: { run: AgentRun }) {
  const evaluation = run.evaluation || {};
  const evalEntries = Object.entries(evaluation).filter(([, value]) => typeof value === "number");
  return <div className="card" style={{ marginTop: 16 }}>
    <div className="section-heading"><div><h3 className="section-title">Execution result</h3><p className="section-description">{run.provider} · {run.model} · {formatDate(run.created_at)}</p></div><Status value={run.status} /></div>
    <div className="response-box">{run.answer || "No answer was returned."}</div>
    <div className="metric-grid">
      <Metric label="Latency" value={formatMs(run.latency_ms)} />
      <Metric label="Tools used" value={String(run.tools_used?.length ?? 0)} />
      <Metric label="Sources" value={String(run.sources?.length ?? 0)} />
      <Metric label="Overall score" value={scoreLabel(evaluation.overall_score)} />
    </div>
    {evalEntries.length > 0 && <div style={{ marginTop: 18 }}><h4 className="section-title">Evaluation metrics</h4><div className="metric-grid">{evalEntries.map(([key, value]) => <Metric key={key} label={key.replaceAll("_", " ")} value={key.includes("latency") ? formatMs(Number(value)) : Number(value) <= 1 ? scoreLabel(value) : String(value)} />)}</div></div>}
    {!!run.verifier_notes && <div style={{ marginTop: 16 }}><h4 className="section-title">Verifier notes</h4><p className="section-description" style={{ lineHeight: 1.7 }}>{run.verifier_notes}</p></div>}
    <div style={{ marginTop: 20 }}><h4 className="section-title">Agent execution trace</h4><div className="trace-list">{(run.trace || []).length ? run.trace?.map((event, index) => <div className="trace-event" key={`${event.stage}-${index}`}><div className="trace-number">{index + 1}</div><div><div className="trace-title">{event.stage} <span style={{ color: "#7f93ac", fontWeight: 400 }}>· {event.status}</span></div><div className="trace-message">{event.message}</div>{event.details && Object.keys(event.details).length > 0 && <div className="trace-details">{JSON.stringify(event.details, null, 2)}</div>}</div></div>) : <div className="empty-state">No trace events are available for this run.</div>}</div></div>
    {!!run.tools_used?.length && <div style={{ marginTop: 18 }}><h4 className="section-title">Tools used</h4><div style={{ display: "flex", flexWrap: "wrap", gap: 7, marginTop: 10 }}>{run.tools_used.map((tool) => <span className="status other" key={tool}>{tool}</span>)}</div></div>}
    {!!run.sources?.length && <div style={{ marginTop: 18 }}><h4 className="section-title">Retrieved sources</h4>{run.sources.map((source) => <div className="source-card" key={source.source_id}><div className="source-title">{source.title || source.path}</div><div className="source-path">{source.path} · lines {source.start_line}–{source.end_line}</div><div className="source-text">{source.text}</div></div>)}</div>}
  </div>;
}

export default function Home() {
  const [view, setView] = useState<View>("overview");
  const [provider, setProvider] = useState("ollama");
  const [task, setTask] = useState("Summarize the security principles in the knowledge base and list the main safeguards.");
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [tools, setTools] = useState<ToolInfo[]>([]);
  const [selectedRun, setSelectedRun] = useState<AgentRun | null>(null);
  const [benchmark, setBenchmark] = useState<BenchmarkResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const refresh = useCallback(async () => {
    setRefreshing(true);
    try {
      const [healthResult, statsResult, runsResult, toolsResult] = await Promise.allSettled([
        api.health(), api.stats(), api.runs(100), api.tools(),
      ]);
      if (healthResult.status === "fulfilled") setHealth(healthResult.value);
      if (statsResult.status === "fulfilled") setStats(statsResult.value);
      if (runsResult.status === "fulfilled") setRuns(runsResult.value.runs || []);
      if (toolsResult.status === "fulfilled") setTools(toolsResult.value.tools || []);
      const failures = [healthResult, statsResult, runsResult, toolsResult].filter((item) => item.status === "rejected");
      if (failures.length) setError((failures[0] as PromiseRejectedResult).reason?.message || "One or more backend endpoints are unavailable.");
      else setError("");
    } finally {
      setRefreshing(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  const successRate = stats?.success_rate ?? 0;
  const averageScore = stats?.average_score ?? 0;
  const providerInfo = health?.provider || {};
  const backendOnline = health?.status === "ok";
  const page = TITLES[view];

  const providerHealth = useMemo(() => {
    const reachable = providerInfo.reachable;
    if (providerInfo.configured === false) return "not configured";
    if (reachable === false) return "unreachable";
    if (reachable === true) return "reachable";
    return health?.configured_provider === "mock" ? "ready" : "configured";
  }, [health, providerInfo]);

  async function handleChat(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!task.trim()) return;
    setLoading(true); setError(""); setNotice(""); setSelectedRun(null);
    try {
      const result = await api.chat(task.trim(), provider);
      setSelectedRun(result);
      setNotice(result.status === "completed" ? "Agent workflow completed and the run was saved." : "The workflow returned a failed run. Inspect the trace below.");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Agent execution failed.");
    } finally { setLoading(false); }
  }

  async function handleBenchmark() {
    setLoading(true); setError(""); setNotice("");
    try {
      const result = await api.benchmark(provider);
      setBenchmark(result);
      const failed = result.failed_tasks ?? result.results.filter((row) => row.status !== "completed").length;
      setNotice(`Benchmark finished: ${result.total_tasks} tasks processed · ${result.successful_tasks ?? (result.total_tasks - failed)} successful · ${failed} failed.`);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Benchmark execution failed.");
    } finally { setLoading(false); }
  }

  async function openRun(runId: string) {
    setError("");
    try {
      const result = await api.run(runId);
      setSelectedRun(result);
      setView("runs");
    } catch (err) { setError(err instanceof Error ? err.message : "Could not load run details."); }
  }

  const renderRecentRows = (items: AgentRun[]) => items.length ? <div className="table-wrap"><table className="data-table"><thead><tr><th>Task</th><th>Provider</th><th>Status</th><th>Latency</th><th>Score</th></tr></thead><tbody>{items.map((run) => <tr key={run.run_id}><td><button className="table-link" onClick={() => void openRun(run.run_id)}>{run.task}</button><div className="small-text muted mono" style={{ marginTop: 4 }}>{run.run_id.slice(0, 8)}…</div></td><td>{run.provider}</td><td><Status value={run.status} /></td><td>{formatMs(run.latency_ms)}</td><td>{scoreLabel(run.evaluation?.overall_score)}</td></tr>)}</tbody></table></div> : <div className="empty-state"><div className="empty-icon">◷</div>No saved runs yet. Execute a task in the Agent Playground to create your first run.</div>;

  return <main className="app-shell">
    <aside className="sidebar">
      <div className="brand-row"><BrandMark /><div className="brand-copy"><div className="brand-name">Agent Harness Pro</div><div className="brand-sub">AI RELIABILITY LAB</div></div></div>
      {(["Workspace", "Evaluation", "System"] as const).map((group) => <div key={group}><div className="nav-label">{group}</div><div className="nav-list">{NAV.filter((item) => item.group === group).map((item) => <button key={item.id} className={`nav-button ${view === item.id ? "active" : ""}`} onClick={() => { setView(item.id); setError(""); }}><span className="nav-icon">{item.icon}</span><span className="nav-text">{item.label}</span></button>)}</div></div>)}
      <div className="sidebar-spacer" />
      <div className="provider-box"><label htmlFor="provider-select">MODEL PROVIDER</label><select id="provider-select" className="provider-select" value={provider} onChange={(event) => setProvider(event.target.value)}><option value="ollama">Ollama · Local</option><option value="gemini">Gemini · API</option><option value="mock">Mock · Offline</option></select><div className="small-text muted" style={{ marginTop: 8 }}>Provider is selected per request. API credentials remain on the backend.</div></div>
      <div className="sidebar-footer">Version 1.3.0<br/>Local-first development workspace</div>
    </aside>

    <section className="main-area">
      <header className="topbar">
        <div><div className="eyebrow">AGENT OPERATIONS / {view.toUpperCase()}</div><h1 className="page-title">{page.title}</h1><p className="page-subtitle">{page.subtitle}</p></div>
        <div className="top-actions"><div className="api-pill"><span className={`dot ${backendOnline ? "ok" : health ? "bad" : ""}`} />API {backendOnline ? "ONLINE" : health ? "ERROR" : "CHECKING"}</div><button className="secondary-button" onClick={() => void refresh()} disabled={refreshing}>{refreshing ? "Refreshing…" : "↻ Refresh"}</button></div>
      </header>

      {error && <div className="error-banner"><strong>Something needs attention:</strong> {error}</div>}
      {notice && <div className="success-banner">{notice}</div>}

      {view === "overview" && <>
        <div className="grid stats-grid">
          <StatCard icon="▶" label="Total runs" value={String(stats?.total_runs ?? 0)} foot="Persisted executions" />
          <StatCard icon="✓" label="Success rate" value={`${successRate.toFixed(1)}%`} foot={`${stats?.completed_runs ?? 0} completed runs`} />
          <StatCard icon="◷" label="Average latency" value={formatMs(stats?.average_latency_ms)} foot="Across saved runs" />
          <StatCard icon="◎" label="Average score" value={scoreLabel(averageScore)} foot="Heuristic evaluation score" />
        </div>
        <div className="grid content-grid">
          <div className="card"><div className="section-heading"><div><h2 className="section-title">Recent executions</h2><p className="section-description">Latest tasks recorded in SQLite.</p></div><button className="secondary-button small" onClick={() => setView("runs")}>View history →</button></div>{renderRecentRows(runs.slice(0, 7))}</div>
          <div className="card"><div className="section-heading"><div><h2 className="section-title">System snapshot</h2><p className="section-description">Current backend configuration.</p></div><span className={`dot ${backendOnline ? "ok" : "bad"}`} /></div><div className="health-row"><span className="muted">Backend</span><Status value={backendOnline ? "ok" : "unreachable"} /></div><div className="health-row"><span className="muted">Configured provider</span><strong>{health?.configured_provider || "—"}</strong></div><div className="health-row"><span className="muted">Provider health</span><Status value={providerHealth} /></div><div className="health-row"><span className="muted">Registered tools</span><strong>{tools.length}</strong></div><div style={{ marginTop: 17 }}><button className="secondary-button small" onClick={() => setView("health")}>Open system health →</button></div></div>
        </div>
        <div className="card" style={{ marginTop: 16 }}><div className="section-heading"><div><h2 className="section-title">Quick start</h2><p className="section-description">Run your first multi-agent task or benchmark.</p></div></div><div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}><button className="primary-button" onClick={() => setView("playground")}>✳ Open agent playground</button><button className="secondary-button" onClick={() => setView("benchmarks")}>▤ Open benchmark lab</button></div></div>
      </>}

      {view === "playground" && <div className="grid panel-grid">
        <div className="card"><div className="section-heading"><div><h2 className="section-title">Task input</h2><p className="section-description">The backend runs Planner → Researcher → Executor → Verifier.</p></div><span className="status other">{provider}</span></div><form onSubmit={handleChat}><textarea className="textarea" value={task} onChange={(event) => setTask(event.target.value)} maxLength={5000} placeholder="Describe a task for your agent team…"/><div className="form-row"><span className="hint">{task.length}/5000 characters · Provider: {provider}</span><button className="primary-button" type="submit" disabled={loading || !task.trim()}>{loading ? "Running agents…" : "▶ Run workflow"}</button></div></form><div className="hint">Tip: try “Find the refund window in the local policy and explain the evidence.” to test knowledge retrieval.</div></div>
        <div className="card"><h2 className="section-title">Workflow stages</h2><p className="section-description">The stages execute sequentially in the current backend.</p><div className="trace-list" style={{ marginTop: 18 }}>{[{name:"Planner",desc:"Creates bounded execution steps"},{name:"Researcher",desc:"Routes to relevant tools or skips retrieval"},{name:"Executor",desc:"Drafts an evidence-aware answer"},{name:"Verifier",desc:"Runs advisory checks and risk flags"}].map((stage,index)=><div className="trace-event" key={stage.name}><div className="trace-number">{index+1}</div><div><div className="trace-title">{stage.name}</div><div className="trace-message">{stage.desc}</div></div></div>)}</div></div>
        {selectedRun && <div style={{ gridColumn: "1 / -1" }}><RunDetails run={selectedRun}/></div>}
      </div>}

      {view === "benchmarks" && <div className="card"><div className="section-heading"><div><h2 className="section-title">Benchmark execution</h2><p className="section-description">Dataset: benchmarks/tasks.json · Provider: {provider}</p></div><button className="primary-button" onClick={() => void handleBenchmark()} disabled={loading}>{loading ? "Running benchmark…" : "▶ Run benchmark"}</button></div><p className="hint">Benchmark requests are synchronous. Larger datasets or slow local models may take several minutes.</p>{benchmark && <><div className="grid benchmark-grid" style={{ marginTop: 18 }}>{Object.entries(benchmark.aggregate || {}).map(([key,value])=><div className="benchmark-result" key={key}><div className="mini-metric-label">{key.replaceAll("_"," ")}</div><div className="mini-metric-value">{key.includes("latency") ? formatMs(value) : key === "overall_score" || key.endsWith("coverage") || key.endsWith("score") || key === "token_overlap" ? scoreLabel(value) : String(value)}</div>{(key.includes("score") || key.includes("coverage") || key === "token_overlap") && <div className="bar-track"><div className="bar-fill" style={{ width: `${Math.min(100,Math.max(0,value*100))}%` }} /></div>}</div>)}</div><div style={{ marginTop: 22 }}><div className="section-heading"><div><h3 className="section-title">Task results</h3><p className="section-description">{benchmark.total_tasks} benchmark cases processed · {benchmark.successful_tasks ?? "—"} successful · {benchmark.failed_tasks ?? "—"} failed.</p></div></div><div className="table-wrap"><table className="data-table"><thead><tr><th>Task</th><th>Status</th><th>Overall</th><th>Keyword coverage</th><th>Latency</th><th>Details</th></tr></thead><tbody>{(benchmark.results || []).map((row, index) => { const metrics = row.metrics ?? { overall_score: undefined, keyword_coverage: undefined, latency_ms: undefined }; return <tr key={row.task_id || `task-${index}`}><td>{row.task || "Unnamed benchmark task"}</td><td><Status value={row.status || "unknown"}/></td><td>{scoreLabel(metrics.overall_score)}</td><td>{scoreLabel(metrics.keyword_coverage)}</td><td>{formatMs(metrics.latency_ms)}</td><td><details className="benchmark-details"><summary>Inspect</summary>{row.error && <p className="benchmark-error">{row.error}</p>}<p>{row.answer || (row.error ? "The task did not return an answer." : "No answer was returned by the backend.")}</p>{row.run_id && <code>Run: {row.run_id}</code>}</details></td></tr>; })}</tbody></table></div></div></>}{!benchmark && <div className="empty-state" style={{ marginTop: 20 }}><div className="empty-icon">▤</div>No benchmark has been executed in this session. Run the dataset to see aggregate scores and task-level results.</div>}</div>}

      {view === "runs" && <>
        <div className="card"><div className="section-heading"><div><h2 className="section-title">Saved runs</h2><p className="section-description">Select a task to retrieve its stored trace and source details.</p></div><button className="secondary-button small" onClick={() => void refresh()}>↻ Reload</button></div>{renderRecentRows(runs)}</div>
        {selectedRun && <RunDetails run={selectedRun}/>}
      </>}

      {view === "health" && <div className="grid health-grid">
        <div className="card"><div className="section-heading"><div><h2 className="section-title">Backend status</h2><p className="section-description">FastAPI service response.</p></div><Status value={backendOnline ? "ok" : "unreachable"}/></div><div className="health-row"><span className="muted">Application</span><strong>{health?.app || "—"}</strong></div><div className="health-row"><span className="muted">API status</span><strong>{health?.status || "Not checked"}</strong></div><div className="health-row"><span className="muted">Configured provider</span><strong>{health?.configured_provider || "—"}</strong></div><div className="health-row"><span className="muted">Provider connectivity</span><Status value={providerHealth}/></div><div className="health-row"><span className="muted">Available tools</span><strong>{tools.length}</strong></div><button className="secondary-button small" style={{ marginTop: 15 }} onClick={() => void refresh()} disabled={refreshing}>{refreshing ? "Checking…" : "Run health check"}</button></div>
        <div className="card"><h2 className="section-title">Provider details</h2><p className="section-description">Returned by the backend health endpoint. API keys are never sent to this page.</p><pre className="provider-info" style={{ marginTop: 16 }}>{JSON.stringify(providerInfo,null,2)}</pre></div>
        <div className="card" style={{ gridColumn: "1 / -1" }}><h2 className="section-title">Registered tools</h2><p className="section-description">Tools exposed by the backend allowlist.</p>{tools.length ? tools.map((tool,index)=><div className="health-row" key={String(tool.name || tool.tool || index)}><strong>{String(tool.name || tool.tool || `Tool ${index+1}`)}</strong><span className="muted">{String(tool.description || tool.summary || "Registered")}</span></div>) : <div className="empty-state" style={{ marginTop: 14 }}>No tool metadata returned. Check that the backend is running.</div>}</div>
      </div>}

      <div className="footer-note">AGENT HARNESS PRO · HEURISTIC SCORES ARE SIGNALS, NOT PROOF OF FACTUAL CORRECTNESS</div>
    </section>
  </main>;
}
