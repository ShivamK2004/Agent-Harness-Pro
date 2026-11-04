# Next.js Frontend Guide

The primary web interface is a Next.js App Router application in `frontend/`. It communicates with the existing Python backend; it does not call Gemini or Ollama directly.

## Start locally (Windows PowerShell)

Terminal 1, from the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn harness.api.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2:

```powershell
cd frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## Configuration

`frontend/.env.local` contains only the backend base URL:

```dotenv
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Do not place `GEMINI_API_KEY` or other model secrets in `frontend/.env.local`. The browser must communicate with FastAPI; provider credentials remain in the root `.env` file read by Python.

## Pages / views

The initial dashboard is a client-side single-page workspace with these views:

- Overview: persisted run aggregates and recent activity.
- Agent Playground: provider selection, task submission, answer, metrics, trace, tools, and retrieval sources.
- Benchmark Lab: run `benchmarks/tasks.json` and inspect aggregate/task-level metrics.
- Run History: list runs and load a selected run's full trace.
- System Health: inspect FastAPI/provider health and tool metadata.

## Backend contract

The UI uses these routes:

| Method | Route | Use |
|---|---|---|
| GET | `/health` | API and configured provider status |
| GET | `/stats` | Dashboard aggregates derived from saved runs |
| GET | `/tools` | Registered tool descriptions |
| POST | `/chat` | Execute a task with `task` and `provider` |
| POST | `/benchmark/run` | Run the benchmark dataset with `provider` |
| GET | `/runs?limit=100` | Run history |
| GET | `/runs/{run_id}` | Full run, trace, and sources |

FastAPI allows local development origins `http://localhost:3000` and `http://127.0.0.1:3000`. Add an exact production frontend origin to `allow_origins` before deployment. Do not use wildcard origins with credentials in production.

## Build the frontend

```powershell
cd frontend
npm install
npm run build
npm run start
```

## Troubleshooting

- **Frontend says backend unreachable:** start the FastAPI terminal and verify `http://127.0.0.1:8000/health`.
- **CORS error:** verify that you opened the UI at `http://localhost:3000` or `http://127.0.0.1:3000` and that the latest `harness/api/main.py` is running.
- **Wrong API URL:** update `NEXT_PUBLIC_API_URL` in `frontend/.env.local`, then restart `npm run dev`.
- **Provider error:** configure `LLM_PROVIDER`, `GEMINI_API_KEY`, or `OLLAMA_MODEL` in the root `.env`; restart FastAPI after changing it.
- **Next.js install fails:** check `node --version` (Node.js 20.9 or later is required by the configured Next.js major release) and retry `npm install`.

## Current limitations

The dashboard submits regular HTTP requests and displays the trace after a run completes. It does not stream intermediate agent events yet. Authentication, multi-tenant isolation, rate limiting, and production deployment hardening are not included.
