# Local Smoke-Test Record — Agent Harness Pro v1.3.0

**Recorded:** 2026-11-04  
**Mode:** deterministic Mock provider (offline)  
**Purpose:** validate application plumbing and integration contracts; not an LLM quality benchmark.

## Python automated tests

- Test command: `python -m pytest -q`
- Result: **23 passed**
- Coverage includes calculator allowlist, workspace path protection, `.text` file creation, local retrieval, benchmark task routing, benchmark per-case failure reporting, scoring, orchestrator behavior, SQLite persistence, Ollama chat-to-generate fallback, and FastAPI routes.

## FastAPI smoke checks

- `GET /`, `/health`, `/stats`, `/tools`, and `/runs` — HTTP 200.
- `POST /chat` with `What is 25 multiplied by 4?` and Mock provider — completed; answer `100`; `calculator` tool recorded.
- `POST /benchmark/run` with Mock provider — 4 tasks processed, 4 successful, 0 failed; every row included all expected metrics; expected-tool score was 100% for all four cases.

## Not tested

No live Gemini request or live Ollama generation was executed. Browser interactions and Docker builds were not manually exercised in this packaging environment. Run `npm install` and `npm run build` in `frontend/` on the target machine to verify the production frontend build.
