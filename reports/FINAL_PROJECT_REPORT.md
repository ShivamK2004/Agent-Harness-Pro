# Agent Harness Pro — Final Project Report

**Project domain:** Agentic AI, LLM evaluation, backend engineering, and reliability analysis  
**Author:** Shivam Kumar  
**Institution:** Indian Institute of Information Technology Vadodara  
**Project type:** Portfolio / engineering prototype  
**Version:** 1.3.0  
**Date:** November 2026

---

## Abstract

Agent Harness Pro is a modular application for executing and evaluating tool-using LLM workflows. It extends a simple agent demonstration into an end-to-end system with interchangeable model providers, a staged multi-agent workflow, a restricted tool registry, local document retrieval with source identifiers, repeatable benchmark tasks, a transparent heuristic evaluator, persistent run history, a REST API, a Next.js dashboard, a retained Streamlit fallback, and a CLI. The system supports Google Gemini, a local Ollama model, and an offline Mock provider. Its main engineering objective is to make an agent workflow inspectable and testable rather than treating a generated response as a black box.

## 1. Problem Statement

LLM-based agents can produce plausible but unsupported answers, invoke tools incorrectly, or fail in ways that are difficult to reproduce. A basic chatbot interface does not provide enough visibility into planning, evidence retrieval, tool execution, response generation, or verification. Developers need a repeatable harness to compare providers, inspect intermediate stages, validate tool boundaries, measure basic response signals, and review historical runs.

## 2. Objectives

1. Provide a provider-independent interface for Gemini, Ollama, and Mock mode.
2. Implement a staged workflow with Planner, Researcher, Executor, and Verifier agents.
3. Restrict tools to an explicit allowlist and constrain file operations to a workspace directory.
4. Retrieve local knowledge snippets and preserve line-aware source identifiers.
5. Run a repeatable benchmark dataset and produce interpretable heuristic scores.
6. Persist responses, metadata, and traces for later inspection.
7. Expose the system through a Next.js + React dashboard, FastAPI, a retained Streamlit fallback, and a CLI.
8. Document setup, architecture, evaluation limitations, and security boundaries.

## 3. Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Cloud LLM | Google Gemini API via `google-genai` |
| Local LLM | Ollama HTTP API |
| Offline mode | Deterministic Python Mock provider |
| Agent orchestration | Modular Python agent classes |
| Retrieval | Local Markdown/text chunking and lexical ranking |
| Backend | FastAPI, Pydantic, Uvicorn |
| Primary dashboard | Next.js, React, TypeScript, CSS |
| Legacy dashboard | Streamlit |
| Persistence | SQLite and JSONL |
| Testing | pytest |
| Packaging | pip, Docker, Docker Compose |

## 4. System Architecture

The application follows a layered architecture:

- **Interface layer:** Next.js + React dashboard (primary), Streamlit dashboard (legacy fallback), and FastAPI endpoints.
- **Orchestration layer:** coordinates the four agent stages and records trace events.
- **Agent layer:** planning, research, answer execution, and verification.
- **Provider layer:** normalizes generation calls across Gemini, Ollama, and Mock.
- **Tool layer:** exposes calculator, local knowledge search, and workspace file operations.
- **Retrieval layer:** indexes local documents and returns ranked chunks with line information.
- **Evaluation layer:** computes benchmark metrics.
- **Storage layer:** saves runs and traces to SQLite and JSONL.

### 4.1 Workflow

1. A task enters the orchestrator.
2. The Planner produces a bounded JSON plan.
3. The Researcher routes the task to a small set of registered tools. Knowledge search is read-only. Arithmetic requests may invoke the calculator.
4. The Executor generates a response using the supplied tool outputs and retrieved source snippets.
5. The Verifier checks citation identifiers and requests an advisory model review.
6. The evaluator computes heuristic metrics.
7. The system persists the result and ordered trace events.

## 5. Core Modules

### 5.1 Multi-provider layer

The common `BaseProvider` interface defines a `generate(system_prompt, user_prompt)` method. The Gemini implementation uses the Google Gen AI SDK, Ollama uses its local chat endpoint with a generate-endpoint fallback for compatibility, and Mock mode provides deterministic outputs for offline tests. This separation allows provider comparison without changing agent code.

### 5.2 Multi-agent workflow

- **Planner:** creates a short, bounded plan and filters the proposed tool list against registered tool names.
- **Researcher:** retrieves local evidence and calls approved tools.
- **Executor:** prepares an answer that should use supplied evidence and source markers.
- **Verifier:** checks whether cited IDs exist, flags missing citations when evidence exists, and requests an advisory review.

### 5.3 Tool registry and workspace

Tools are explicitly registered. The calculator uses restricted AST parsing rather than executing arbitrary Python. Workspace operations resolve paths and reject files outside the workspace root. The application intentionally does not expose shell execution.

### 5.4 Retrieval

The local knowledge base indexes `.md` and `.txt` files. Documents are split into line-aware chunks and ranked with token-frequency overlap plus an exact phrase bonus. Each result has a stable source ID for the current index, path, title, and line range. This is lexical retrieval, not embedding-based vector search.

### 5.5 Evaluation and benchmarking

Each benchmark case can define expected keywords, a reference answer, and expected tool names. The evaluator records keyword coverage, token Jaccard overlap, citation marker score, tool-use score, latency, and a weighted aggregate. The composite score is an engineering heuristic. It must not be interpreted as the probability that an answer is correct.

### 5.6 Persistence and observability

SQLite stores run-level data and ordered trace events. JSONL captures a second append-only record. The Next.js dashboard displays run aggregates, task execution results, traces, benchmarks, sources, and system health through FastAPI. The original Streamlit dashboard remains as a fallback.

## 6. Project Structure

```text
agent-harness-advanced/
├── app/                  # Legacy Streamlit interface
├── frontend/             # Next.js + React web dashboard
├── benchmarks/           # Benchmark task JSON
├── data/                 # Runtime SQLite database
├── docs/                 # Architecture, API, security, setup, roadmap
├── harness/              # Main Python package
│   ├── agents/            # Planner, researcher, executor, verifier
│   ├── api/               # FastAPI service
│   ├── evaluation/        # Metrics and benchmark runner
│   ├── providers/         # Gemini, Ollama, Mock adapters
│   ├── retrieval/         # Local knowledge base
│   ├── storage/           # SQLite persistence
│   └── tools/             # Calculator, workspace, registry
├── knowledge_base/       # Synthetic sample documents
├── logs/                 # Runtime JSONL logs
├── reports/              # This report
├── tests/                # Offline tests
└── workspace/            # Restricted file area
```

## 7. Installation and Execution

The project is designed to run in Mock mode before any external model is configured. Install the Python dependencies from `requirements.txt`, copy `.env.example` to `.env`, and start FastAPI with `uvicorn harness.api.main:app --reload --host 127.0.0.1 --port 8000`. In a second terminal, install the frontend dependencies from `frontend/` and run `npm run dev`. The Next.js application is served at `http://localhost:3000`. Gemini requires a key in the root `.env`; Ollama requires a locally running Ollama server and a model name matching `ollama list`. The original Streamlit UI remains optional. Automated tests run with `python -m pytest -q` and use Mock mode.

## 8. Testing Strategy

The included tests cover restricted arithmetic, rejection of disallowed AST syntax, workspace path traversal protection, extension restrictions, knowledge retrieval, deterministic Mock provider execution, SQLite history persistence, calculator tool routing, benchmark schema, scoring output, and the Ollama `/api/generate` compatibility fallback. A GitHub Actions workflow runs the offline suite on Python 3.10, 3.11, and 3.12 for pushes and pull requests. These tests validate the local software boundaries and plumbing; they do not evaluate the factual accuracy of remote model responses.

## 9. Evaluation Method and Interpretation

The weighted composite is:

`overall_score = 0.50 × keyword_coverage + 0.20 × token_overlap + 0.15 × citation_score + 0.15 × tool_use_score`.

This score is deterministic given an answer and benchmark metadata, but it has known weaknesses. Keyword coverage can reward keyword stuffing, Jaccard overlap penalizes paraphrases, citation presence does not establish entailment, and model-based verification can be incorrect. Meaningful evaluation should use reviewed golden data, claim-level evidence checks, adversarial tests, repeated runs, and separate cost/latency records.

## 10. Security and Privacy Considerations

The project keeps provider keys outside source code, restricts tools to an allowlist, applies path checks to workspace files, and avoids arbitrary shell execution. However, it is a local prototype. It does not include authentication, authorization, tenant isolation, public deployment hardening, or an OS-level sandbox. Free-tier cloud model use may have different data handling and reviewer terms than paid tiers. Never submit confidential data without checking the provider's terms and organizational policies.

## 11. Limitations

- The retrieval engine is lexical, not vector-based.
- The verifier is advisory and cannot guarantee that an answer is grounded.
- The sample dataset and knowledge documents are synthetic.
- No true human-in-the-loop approval screen is implemented. The web dashboard displays traces after a synchronous run; it does not yet stream intermediate events over WebSockets.
- Cost and token usage are not captured consistently across providers.
- No production deployment pipeline, distributed tracing, authentication, or monitoring stack is included. A GitHub Actions continuous-integration workflow runs automated tests.
- Tool routing is intentionally conservative and mostly deterministic rather than open-ended autonomous function calling.

## 12. Future Enhancements

1. Add embedding-based retrieval, reranking, and retrieval precision/recall.
2. Add structured output schemas and provider-native function calling.
3. Add human approval for write-capable tools.
4. Add claim-level groundedness evaluation with human-reviewed data.
5. Add token/cost tracking and model/prompt/dataset experiment manifests.
6. Add GitHub Actions for linting and test gates.
7. Add OpenTelemetry tracing and metrics.
8. Add authentication, RBAC, rate limits, tenant isolation, and hardened sandboxing.

## 13. Conclusion

Agent Harness Pro demonstrates a practical engineering approach to LLM agent reliability. Instead of only exposing a chat interface, it separates providers, agent stages, tools, retrieval, evaluation, storage, and interfaces. Its traceable workflow and offline test mode make it a useful base for further experimentation and a credible portfolio project when demonstrated honestly. Its heuristics should be treated as development signals, not guarantees of factuality or production readiness.

---

## Appendix A — Suggested Portfolio Summary

**Agent Harness Pro — Multi-Provider Agent Workflow & Reliability Lab**  
Built a modular Python framework for multi-agent LLM execution and evaluation with Gemini, Ollama, and offline Mock providers. Implemented Planner–Researcher–Executor–Verifier orchestration, allowlisted calculator and sandboxed workspace tools, local knowledge retrieval with citations, benchmark-based heuristic scoring, SQLite trace history, a Next.js + React dashboard, a FastAPI backend, and a retained Streamlit fallback. Added offline tests, a GitHub Actions test workflow, and documentation for setup, architecture, limitations, and security.

## Appendix B — Evidence to Capture Before Publishing

- Screenshot of Agent Playground with a Gemini or Ollama run.
- Screenshot of a benchmark result with provider/model name visible.
- Screenshot of run history and trace inspection.
- Terminal output of `python -m pytest -q`.
- A short architecture diagram or recorded demo.
- GitHub repository link and a versioned release.

Do not insert fabricated benchmark scores or claim a production deployment without having performed it.


## v1.3.0 reliability and benchmark corrections

- Benchmark metadata now controls expected-tool routing for evaluation cases, so knowledge questions reliably invoke local retrieval and arithmetic cases invoke the calculator.
- The benchmark runner isolates task failures, always returns a complete row for each dataset entry, and assigns zero overall score to failed executions.
- The dashboard renders missing metrics safely and exposes answer/error details for every task result.
- File-creation requests use the allowlisted workspace writer; `.text` files are permitted and verified inside `workspace/`.
- Planner templates, deterministic research summaries, and deterministic verification are used by default for lower latency. An optional model-based verifier can be enabled with `MODEL_VERIFIER_ENABLED=true`.
