# REST API Guide

Start the service:

```bash
uvicorn harness.api.main:app --reload --host 127.0.0.1 --port 8000
```

Interactive OpenAPI docs: `http://127.0.0.1:8000/docs`. The local Next.js development origins `http://localhost:3000` and `http://127.0.0.1:3000` are enabled by CORS.

## `GET /health`

Returns application status and configured provider health. Ollama reachability is checked; Gemini credentials are checked for presence, but a live Gemini request is not made.

## `GET /stats`

Returns aggregates derived from the latest 500 persisted runs: counts, success rate, average latency, average heuristic score, and recent runs. These are dashboard summaries, not ground-truth quality metrics.

## `GET /tools`

Returns the registered allowlisted tools.

## `POST /chat`

Request:

```json
{
  "task": "What is the sample support response time?",
  "provider": "mock"
}
```

`provider` is optional and accepts `mock`, `gemini`, or `ollama`. Response includes the run ID, answer, sources, tools, trace, latency, and evaluation object.

## `POST /benchmark/run`

Runs the bundled dataset using the specified provider or the configured default. Request:

```json
{"provider":"mock"}
```

## `GET /runs?limit=20`

Lists recent runs. Limit is clamped between 1 and 500.

## `GET /runs/{run_id}`

Returns one persisted run with trace events. Returns 404 if it does not exist.

## Error behavior

Invalid requests return HTTP 4xx. Provider connectivity/configuration errors are surfaced as an API error. Do not expose the API on a public interface without authentication, authorization, rate limiting, and secure secret handling.
