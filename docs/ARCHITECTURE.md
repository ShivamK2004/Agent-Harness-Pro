# Architecture and Design

## 1. Goals

Agent Harness Pro is designed as a small but complete engineering system for experimentation with LLM-powered workflows. Its goals are modular provider integration, observable multi-agent execution, restricted tools, document-grounded responses, repeatable benchmark runs, and inspectable history.

## 2. Component responsibilities

| Component | Responsibility |
|---|---|
| Provider adapter | Normalizes generation calls for Gemini, Ollama, and Mock |
| Planner | Creates a bounded plan in JSON form; cannot execute code |
| Researcher | Invokes only registered local tools and retrieves relevant evidence |
| Executor | Generates an answer using supplied evidence and tool outputs |
| Verifier | Checks citation IDs and requests an advisory model review |
| Tool registry | Enforces a finite allowlist and dispatches validated tool actions |
| Knowledge base | Reads `.md`/`.txt`, chunks documents, performs lexical ranking |
| Evaluator | Calculates transparent benchmark heuristics |
| Run store | Persists run metadata and stage traces to SQLite |
| Next.js UI | Primary web dashboard: overview, playground, benchmarks, run history, and health |
| Streamlit UI | Legacy Python dashboard retained as a fallback |
| FastAPI | Programmatic endpoints for chat, benchmarks, runs, and tools |

## 3. Request lifecycle

1. Validate the task is non-empty.
2. Generate a run ID and record an orchestrator trace event.
3. Classify the request and use a bounded static plan for supported task types; model planning remains a fallback for unknown routes.
4. The researcher uses deterministic routing to call knowledge search and, for explicit arithmetic requests, the calculator. The model does not get arbitrary tool execution privileges.
5. The executor receives the user task, retrieved chunks, and tool outputs. It must preserve `[KBnnn]` source identifiers and state when evidence is absent.
6. The verifier checks whether cited IDs exist and whether sources were cited when available. It also requests an advisory review from the configured model.
7. The evaluator records heuristic quality metrics and latency.
8. The run and trace are saved to SQLite and JSONL.

## 4. Provider design

All providers implement `BaseProvider.generate(system_prompt, user_prompt)`. This keeps agent logic independent from vendor-specific client code. Gemini is accessed via `google-genai`; Ollama uses `/api/chat` with `/api/generate` fallback when the chat route returns 404/405; Mock is deterministic and intended for tests.

## 5. Retrieval design

The local knowledge engine indexes Markdown and plain-text files. It creates line-aware chunks and ranks them using token-frequency overlap plus an exact phrase bonus. This choice avoids requiring a vector database or embedding model for the starter project. It is a lexical retriever, not semantic vector search.

## 6. Tool safety

- No shell tool exists.
- The calculator parses Python AST but evaluates only numeric constants, approved binary operators, and approved unary operators.
- Workspace read/write resolves paths and rejects paths outside the workspace root.
- Only `.txt`, `.md`, `.json`, `.csv`, and `.py` are accepted for workspace operations.
- Tool outputs and file sizes have limits.
- Retrieved content is treated as untrusted data in the executor instructions.

## 7. Persistence

SQLite contains `runs` and `trace_events`. Each run stores provider/model, task, answer, latency, heuristic evaluation, source metadata, tool names, and verifier notes. Trace events are stored separately for ordered inspection. JSONL is an append-only secondary record for local analysis.

## 8. Extension points

- Replace lexical retrieval with embeddings and a vector index.
- Add a human approval queue between researcher and executor for write operations.
- Add provider-specific structured output/function calling.
- Add token/cost usage tracking where provider response metadata is available.
- Add authentication, RBAC, rate limiting, tenant isolation, and OpenTelemetry before deployment.

## 9. CI workflow

The `.github/workflows/tests.yml` workflow runs the offline pytest suite on pushes and pull requests against Python 3.10, 3.11, and 3.12. The workflow uses Mock mode and requires no model API keys. It is a continuous-integration test workflow, not a production deployment pipeline.


## Web frontend integration

The primary interface is the Next.js application in `frontend/`. It calls the FastAPI backend over HTTP. FastAPI exposes local CORS origins for the Next.js development server; provider credentials remain in the root Python `.env` file. See [NEXTJS_FRONTEND.md](NEXTJS_FRONTEND.md).


## Latency and verification

Known task routes use deterministic planning. Research summaries are generated from tool outputs without an extra model call. Deterministic verification runs by default; set `MODEL_VERIFIER_ENABLED=true` to add an optional model review call. This reduces latency for calculations and sandbox file creation while keeping the verification checks explicit.
