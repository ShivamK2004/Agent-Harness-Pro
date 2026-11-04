"""Streamlit dashboard for Agent Harness Pro."""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from harness.config import settings
from harness.agents.orchestrator import AgentOrchestrator
from harness.evaluation.benchmark import BenchmarkRunner
from harness.storage.database import RunStore
from harness.providers.factory import get_provider
from harness.retrieval.knowledge_base import LocalKnowledgeBase
from harness.tools.workspace import WorkspaceTool

st.set_page_config(page_title="Agent Harness Pro", page_icon="🧭", layout="wide")

@st.cache_resource
def get_store():
    return RunStore()

@st.cache_resource
def get_kb():
    return LocalKnowledgeBase(settings.knowledge_base_dir)


def provider_selector():
    default = settings.llm_provider if settings.llm_provider in {"gemini", "ollama", "mock"} else "mock"
    return st.sidebar.selectbox("Model provider", ["mock", "gemini", "ollama"],
                                 index=["mock", "gemini", "ollama"].index(default),
                                 help="Mock is offline and free; Gemini requires GEMINI_API_KEY; Ollama requires a running local server.")

st.sidebar.title("🧭 Agent Harness Pro")
page = st.sidebar.radio("Navigation", ["Agent Playground", "Benchmark Lab", "Run History", "Knowledge Base", "Sandbox Workspace", "System Health"])
provider = provider_selector()
st.sidebar.caption("Planner → Researcher → Executor → Verifier")
st.sidebar.caption("Tools are allowlisted; workspace paths are restricted.")

st.title("🧭 Agent Harness Pro")
st.caption("Multi-provider LLM agent workflows, evaluation, traceability, and reliability analysis")

if page == "Agent Playground":
    st.subheader("Run an agent task")
    st.write("Try asking about the sample knowledge base, requesting a calculation, or asking the agent to explain its evidence.")
    task = st.text_area("Your task", value="What is the sample support response time and how can a customer contact support?", height=110)
    if st.button("Run workflow", type="primary", disabled=not task.strip()):
        with st.spinner(f"Running with {provider}..."):
            run = AgentOrchestrator(provider).run(task)
        st.session_state["last_run"] = run.to_dict()
    run_data = st.session_state.get("last_run")
    if run_data:
        st.markdown("### Agent response")
        st.markdown(run_data["answer"])
        a, b, c, d = st.columns(4)
        a.metric("Status", run_data["status"])
        b.metric("Latency", f"{run_data['latency_ms']:.0f} ms")
        c.metric("Sources", len(run_data["sources"]))
        d.metric("Tools", len(run_data["tools_used"]))
        st.markdown("### Evaluation (heuristic, not factual accuracy)")
        st.json(run_data["evaluation"])
        with st.expander("Source evidence"):
            for source in run_data["sources"]:
                st.markdown(f"**[{source['source_id']}] {source['title']}** — `{source['path']}:{source['start_line']}-{source['end_line']}`")
                st.code(source["text"][:3000])
        with st.expander("Workflow trace"):
            st.dataframe(run_data["trace"], use_container_width=True)
        with st.expander("Verifier notes"):
            st.write(run_data.get("verifier_notes", "No notes"))

elif page == "Benchmark Lab":
    st.subheader("Benchmark suite")
    st.write("Runs the bundled tasks sequentially and computes a transparent heuristic score for each task.")
    st.warning("Benchmark scores are regression signals only. They are not proof of truth, safety, or model quality.")
    if st.button("Run all benchmark tasks", type="primary"):
        with st.spinner(f"Running benchmark with {provider}..."):
            result = BenchmarkRunner(AgentOrchestrator(provider)).run(settings.benchmark_dataset)
        st.session_state["benchmark_result"] = result
    result = st.session_state.get("benchmark_result")
    if result:
        st.markdown("### Aggregate results")
        cols = st.columns(5)
        for col, key, label in zip(cols, ["overall_score", "keyword_coverage", "token_overlap", "citation_score", "avg_latency_ms"],
                                   ["Overall", "Keyword coverage", "Token overlap", "Citation score", "Avg latency ms"]):
            value = result["aggregate"][key]
            col.metric(label, f"{value:.3f}" if key != "avg_latency_ms" else f"{value:.0f}")
        st.dataframe([{"Task": r["task_id"], "Status": r["status"], **r["metrics"]} for r in result["results"]], use_container_width=True)
        for item in result["results"]:
            with st.expander(f"{item['task_id']} — {item['task'][:90]}"):
                st.markdown(item["answer"])
                st.json(item["metrics"])

elif page == "Run History":
    st.subheader("Persisted run history")
    rows = get_store().list_runs(100)
    if not rows:
        st.info("No runs stored yet. Run a task in Agent Playground.")
    else:
        st.dataframe([{"Run ID": r["run_id"], "Created": r["created_at"], "Provider": r["provider"],
                       "Status": r["status"], "Latency ms": round(r["latency_ms"], 1),
                       "Overall": r["evaluation"].get("overall_score"), "Task": r["task"][:100]} for r in rows], use_container_width=True)
        selected = st.selectbox("Inspect run", [r["run_id"] for r in rows])
        detail = get_store().get_run(selected)
        if detail:
            st.markdown("#### Answer")
            st.markdown(detail["answer"])
            st.markdown("#### Trace")
            st.dataframe(detail.get("trace", []), use_container_width=True)
            st.json(detail["evaluation"])

elif page == "Knowledge Base":
    st.subheader("Local knowledge base")
    kb = get_kb()
    left, right = st.columns([1, 1])
    left.metric("Indexed chunks", len(kb.documents))
    right.metric("Documents", len(kb.list_documents()))
    if st.button("Reload knowledge files"):
        count = kb.reload()
        st.success(f"Reindexed {count} chunks.")
    st.dataframe(kb.list_documents(), use_container_width=True)
    query = st.text_input("Try a knowledge search")
    if query:
        for src in kb.search(query):
            st.markdown(f"**[{src.source_id}] {src.title}** — `{src.path}:{src.start_line}-{src.end_line}` (score {src.score:g})")
            st.code(src.text[:2000])
    st.caption("Supported extensions: .md and .txt. Lexical ranking is used; this is not vector search.")

elif page == "Sandbox Workspace":
    st.subheader("Restricted workspace tools")
    st.caption("Files are confined to the configured workspace directory. Only .txt, .md, .json, .csv, and .py are accepted. This is a path guard, not an OS-level sandbox.")
    workspace = WorkspaceTool(settings.workspace_dir, settings.max_workspace_file_bytes)
    tab_write, tab_read, tab_list = st.tabs(["Write file", "Read file", "List files"])
    with tab_write:
        with st.form("workspace_write_form"):
            rel_path = st.text_input("Relative path", value="notes/demo.md")
            content = st.text_area("File content", height=160)
            submitted = st.form_submit_button("Write into workspace")
        if submitted:
            try:
                st.success(workspace.write(rel_path, content))
            except Exception as exc:
                st.error(str(exc))
    with tab_read:
        available = workspace.list_files()
        if available:
            selected_file = st.selectbox("Choose file", available)
            if st.button("Read selected file"):
                try:
                    st.code(workspace.read(selected_file))
                except Exception as exc:
                    st.error(str(exc))
        else:
            st.info("No supported files yet. Create one in the Write file tab.")
    with tab_list:
        st.write(workspace.list_files())

elif page == "System Health":
    st.subheader("Configuration and health")
    try:
        provider_health = get_provider(provider).health()
    except Exception as exc:
        provider_health = {"error": str(exc)}
    st.write("Selected provider")
    st.json(provider_health)
    st.write("Local resources")
    st.json({"database": str(settings.sqlite_path), "database_exists": settings.sqlite_path.exists(),
             "workspace": str(settings.workspace_dir), "workspace_exists": settings.workspace_dir.exists(),
             "knowledge_base": str(settings.knowledge_base_dir), "indexed_chunks": len(get_kb().documents),
             "log_directory": str(settings.log_dir)})
    st.info("For Gemini, check the key and model in .env. For Ollama, verify that `ollama serve` is running and the configured model is pulled.")

st.divider()
st.caption("Agent Harness Pro • Local-first prototype • Verify important outputs before relying on them")
