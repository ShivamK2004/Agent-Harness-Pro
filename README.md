# Agent Harness Pro — Multi-Provider Agent Workflow & Reliability Lab

**An end-to-end, portfolio-ready Python project for building, running, tracing, and evaluating tool-using LLM workflows.**

Agent Harness Pro extends a basic LLM-agent demo into a modular application with a multi-agent pipeline, a model-provider abstraction, controlled tools, local knowledge retrieval, benchmark evaluation, SQLite run history, a FastAPI service, a Next.js + React dashboard, a legacy Streamlit dashboard, and a CLI.

> **Important:** This is an advanced portfolio prototype, not a certified safety system or a production deployment. The verifier uses transparent heuristics and optional model review; neither guarantees factual correctness. Review tool permissions and security documentation before exposing it to untrusted users.

## Highlights

- **Three providers:** Google Gemini API, local Ollama, and deterministic Mock mode.
- **Multi-agent workflow:** Planner → Researcher → Executor → Verifier, with trace events at every stage.
- **Controlled tools:** calculator, local knowledge search, and workspace file read/write. Tools are allowlisted; workspace paths are constrained.
- **Local RAG:** chunking and lexical ranking over Markdown/text files, with source IDs and line references in context.
- **Evaluation:** benchmark tasks, expected-keyword coverage, token-overlap proxy, citation checks, tool-use signals, latency, and an overall heuristic score.
- **Persistence:** SQLite stores runs, evaluations, and trace events; JSONL logs are also available.
- **Interfaces:** Next.js + React dashboard, FastAPI REST API, legacy Streamlit dashboard, and CLI.
- **Developer workflow:** unit tests, GitHub Actions test workflow, Docker, `.env` configuration, setup scripts, sample knowledge documents, and project report.

## Architecture at a glance

```text
User / Benchmark Task
        |
        v
  Orchestrator
        |
        +--> Planner Agent --------- creates a bounded plan
        |
        +--> Researcher Agent ------ searches local knowledge base
        |          |
        |          +--> Allowlisted tools: knowledge_search / calculator / workspace
        |
        +--> Executor Agent -------- creates an answer grounded in tool evidence
        |
        +--> Verifier Agent -------- checks citations, evidence coverage, and risk flags
        |
        v
 Evaluation + Trace + SQLite + JSONL
        |
        +--> Next.js Dashboard (primary UI)
        +--> Streamlit Dashboard (legacy fallback)
        +--> FastAPI REST API
        +--> CLI / Benchmark Runner

Provider adapter: Gemini | Ollama | Mock
```

## Quick start (Windows PowerShell)

### Prerequisites

- Python 3.10+ (Python 3.13 is suitable for this project).
- Node.js 20.9+ and npm for the Next.js UI.
- Ollama only if you want to run a local model.

### 1. Install the Python backend

From the project root in PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If Python 3.13 is not installed, use another installed version such as `py -3.10 -m venv .venv`.

### 2. Configure a provider

For a first offline check, leave `LLM_PROVIDER=mock` in `.env`. To use the Llama 3 model that was present on the development computer, set:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:latest
OLLAMA_TIMEOUT_SECONDS=180
```

For Gemini, use a key created in [Google AI Studio](https://aistudio.google.com/apikey):

```dotenv
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Never commit `.env` or expose an API key in frontend code. Provider secrets are read by the Python backend only.

### 3. Start the FastAPI backend

In the first terminal, from the project root:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn harness.api.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/health` to confirm the backend is responding and `http://127.0.0.1:8000/docs` to inspect the API. Keep this terminal running.

### 4. Install and start the Next.js frontend

Open a second PowerShell terminal in the project root:

```powershell
cd frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`. The frontend calls the Python API at `http://127.0.0.1:8000`. The API base URL can be changed in `frontend/.env.local`.

### 5. Run tests

From the repository root, in a terminal with `.venv` activated:

```powershell
python -m pytest -q
```

### Optional: legacy Streamlit UI

The original Streamlit UI is retained as a fallback:

```powershell
streamlit run app/streamlit_app.py
```

Open `http://localhost:8501`.

### Use Gemini

1. Create an API key in [Google AI Studio](https://aistudio.google.com/).
2. Add it to `.env` (never commit the real key):

   ```dotenv
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_key_here
   GEMINI_MODEL=gemini-3.8-flash
   ```

3. Install dependencies and start the app again. The model name is configurable; check your AI Studio account for currently enabled models and quotas.

The free tier is subject to model-specific rate limits and account availability. Do not send confidential or personal data through a free-tier API. Review Google's current terms and data-use settings before using it.

### Use Ollama locally

1. Install Ollama from [ollama.com](https://ollama.com/).
2. Pull a model, for example:

   ```powershell
   ollama pull llama3:latest
   ```

3. Configure `.env`:

   ```dotenv
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=llama3:latest
   OLLAMA_BASE_URL=http://localhost:11434
   ```

4. Make sure Ollama is running, then start the FastAPI backend and Next.js frontend using the two-terminal instructions above.

### Run from CLI

```powershell
python -m harness.cli ask "Summarize the access policy in the local knowledge base"
python -m harness.cli benchmark
python -m harness.cli history --limit 10
```

Tests use Mock mode and do not require a Gemini key or a running Ollama service.

## Project structure

```text
agent-harness-advanced/
├── .github/workflows/      # Automated test workflow
├── app/                    # Legacy Streamlit dashboard
├── frontend/               # Next.js + React dashboard
├── benchmarks/             # Sample benchmark dataset
├── data/                   # SQLite database created at runtime
├── docs/                   # Architecture, API, setup, security, demo guides
├── harness/
│   ├── agents/              # Planner, researcher, executor, verifier, orchestrator
│   ├── api/                 # FastAPI endpoints
│   ├── evaluation/          # Metrics and benchmark runner
│   ├── providers/           # Gemini, Ollama, Mock adapters
│   ├── retrieval/           # Local document indexing and retrieval
│   ├── storage/             # SQLite persistence
│   └── tools/               # Allowlisted tools and sandboxed workspace
├── knowledge_base/          # Sample local knowledge documents
├── logs/                    # JSONL run logs created at runtime
├── reports/                 # Complete project report
├── tests/                   # Offline unit and integration tests
├── workspace/               # Sandboxed file workspace
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── requirements.txt
```

## Main screens

The primary web UI is the Next.js application in `frontend/`. Start it with `cd frontend`, `npm install`, and `npm run dev` after the FastAPI backend is running. The Streamlit interface remains available as a fallback.

- **Overview:** persisted run totals, success rate, average latency, and recent activity.
- **Agent Playground:** select a provider and run a user task; inspect answer, citations, trace, and evaluation.
- **Benchmark Lab:** execute bundled benchmark cases and compare aggregate scores.
- **Run History:** inspect persisted runs and their stage traces.
- **System Health:** check API/provider response and inspect registered tools.

## Evaluation interpretation

The default evaluation is deliberately explainable and lightweight:

- `keyword_coverage`: fraction of benchmark expected keywords present in the answer.
- `token_overlap`: Jaccard overlap against the reference answer (a lexical proxy, **not** embedding-based semantic similarity).
- `citation_score`: presence and count of source markers when retrieved sources exist.
- `tool_use_score`: whether a relevant registered tool was used for a tool-oriented benchmark.
- `overall_score`: weighted heuristic aggregate.

These metrics are useful for regression comparisons, not proof of correctness. The verifier may add a model-based review note, but the model review is not treated as ground truth.

## API endpoints

- `GET /health` — configured provider health.
- `GET /stats` — run-history aggregates for the dashboard.
- `GET /tools` — registered tool descriptions.
- `POST /chat` — run an agent workflow.
- `POST /benchmark/run` — execute the benchmark dataset.
- `GET /runs` and `GET /runs/{run_id}` — persisted run history and details.

## Useful commands

```bash
python -m harness.cli ask "What is the refund window?"
python -m harness.cli benchmark --dataset benchmarks/tasks.json
python -m harness.cli history --limit 20
python -m harness.cli health
```

## Configuration

See `.env.example`, [docs/SETUP_WINDOWS.md](docs/SETUP_WINDOWS.md), and [docs/INTERVIEW_GUIDE.md](docs/INTERVIEW_GUIDE.md). Common variables:

| Variable | Purpose | Default |
|---|---|---|
| `LLM_PROVIDER` | `gemini`, `ollama`, or `mock` | `mock` |
| `GEMINI_API_KEY` | Gemini API key | empty |
| `GEMINI_MODEL` | Gemini model ID | `gemini-3.8-flash` |
| `OLLAMA_MODEL` | Local Ollama model | `llama3:latest` |
| `OLLAMA_BASE_URL` | Ollama server | `http://localhost:11434` |
| `DATABASE_URL` | SQLite file path (SQLite only) | `sqlite:///data/agent_harness.db` |
| `WORKSPACE_DIR` | Sandboxed workspace | `workspace` |
| `KNOWLEDGE_BASE_DIR` | Local document directory | `knowledge_base` |
| `MAX_TOOL_OUTPUT_CHARS` | Maximum tool output size | `8000` |

## Security and limitations

- API keys belong in `.env` or a secret manager; do not hard-code or commit them.
- The workspace tool blocks path traversal and only accepts a small set of text extensions.
- The calculator uses a restricted AST evaluator; it does not call `eval()`.
- This demo has no user authentication, tenant isolation, rate limiting, or hardened process sandbox. Do not expose it publicly without adding these controls.
- The agent may produce incorrect output. Verify important claims against original sources.
- The local RAG index is rebuilt from files on disk and is lexical rather than vector-embedding based.

## Author / portfolio customization

Update the author line in `reports/FINAL_PROJECT_REPORT.md`, add your GitHub URL after you create a repository, and include screenshots of your own successful runs. Do not claim performance numbers that you have not measured.

## License

MIT. See [LICENSE](LICENSE).

## Intent-based task routing (v1.3.0)

The workflow distinguishes calculation, knowledge-retrieval, sandbox file creation, and general questions. Benchmark metadata can require the intended registered tool so a support FAQ test cannot accidentally skip knowledge retrieval. Benchmark output always includes one result row per dataset case, including explicit failure rows and error details. The dashboard safely displays missing metrics and provides an Inspect panel for each result. Calculations and file creation avoid unnecessary model calls. See [Task Routing](docs/TASK_ROUTING.md). For example, `What is 25 multiplied by 4?` is routed to the calculator and returns `100`; `create shivam.text file` creates an empty file in `workspace/shivam.text`.
