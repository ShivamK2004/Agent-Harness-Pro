# Agent Harness Pro FAQ

## What is the workflow?

The application uses a planner, researcher, executor, and verifier sequence. Each stage emits a trace event that can be inspected later.

## Which providers are supported?

Gemini uses the Google Gen AI Python SDK, Ollama uses its local HTTP API, and Mock mode provides deterministic responses for tests and offline demos.

## What does the evaluator measure?

It measures expected-keyword coverage, lexical token overlap against an optional reference answer, source citation markers, expected tool use, and latency. These are heuristic engineering signals, not factual accuracy measurements.
