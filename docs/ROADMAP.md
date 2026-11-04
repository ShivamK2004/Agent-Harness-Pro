# Roadmap

## Implemented in this version

- Gemini, Ollama, and Mock provider adapters
- Planner, researcher, executor, verifier workflow
- Allowlisted calculator, knowledge search, and workspace tools
- Local line-aware Markdown/text retrieval
- SQLite run and trace persistence; JSONL logs
- Benchmark dataset and heuristic evaluator
- Next.js + React dashboard, FastAPI endpoints, and retained Streamlit fallback
- Unit tests, Docker setup, and documentation

## Next engineering milestones

1. Add a vector retrieval adapter with embeddings and reranking.
2. Add structured-output schema validation and provider-native function calling.
3. Add explicit human approval before any write-capable tool action.
4. Add prompt-injection benchmark cases and claim-level source entailment checks.
5. Add token usage and cost capture when provider metadata exposes it.
6. Add CI workflow for linting and tests (GitHub Actions).
7. Add OpenTelemetry tracing and metrics export.
8. Add auth, RBAC, tenant isolation, and rate limiting before deployment.
9. Add experiment manifests to track provider/model/prompt/dataset versions.
