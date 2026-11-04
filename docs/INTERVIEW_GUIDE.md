# Interview Preparation — Agent Harness Pro

## 60-second project explanation

I built Agent Harness Pro, a modular Python framework for executing and evaluating LLM workflows. It supports Gemini, local Ollama, and Mock mode through a common provider interface. A task moves through Planner, Researcher, Executor, and Verifier stages. The researcher can search a local knowledge base or use a restricted calculator; file operations are confined to a workspace. Each run records sources, tools, latency, evaluation signals, and stage traces in SQLite. I also built a Next.js + React dashboard connected to FastAPI and kept the original Streamlit interface as an optional fallback. The project includes a benchmark runner, offline tests, and a GitHub Actions test workflow.

## Architecture questions to prepare

### Why did you separate model providers?

The agent logic should not depend on one vendor SDK. A common `BaseProvider` interface makes it easier to compare cloud and local models, test offline, and replace a provider without rewriting orchestration.

### Why use a Planner–Researcher–Executor–Verifier workflow?

Separate stages make intermediate behavior observable. Planning creates a bounded sequence, research retrieves evidence and tool outputs, execution drafts the answer, and verification checks source identifiers and requests a second-pass review.

### How do you prevent arbitrary tool execution?

The model does not directly execute generated Python or shell commands. A deterministic router selects from a fixed registry. The calculator accepts only a restricted AST grammar, and workspace paths are resolved and checked against the workspace root.

### Is the verifier guaranteed to catch hallucinations?

No. The verifier is advisory. The deterministic component checks whether citation identifiers exist and whether retrieved sources were cited. The LLM review may be wrong. A stronger system would need claim-level entailment tests and human-reviewed golden data.

### Is this vector RAG?

No. The current retrieval layer uses line-aware chunking and lexical token-frequency ranking. Embedding-based retrieval and reranking are listed as future work.

### How do you compare providers?

Run the same benchmark dataset against each provider and compare latency, expected-keyword coverage, token overlap, citation-marker score, and tool-use score. The current composite is a heuristic and should not be presented as factual accuracy.

## Demo checklist

- [ ] Run the test suite and show all tests passing.
- [ ] Start in Mock mode to demonstrate offline determinism.
- [ ] Run a knowledge-base question and inspect citations.
- [ ] Run a calculator task and show the restricted tool result.
- [ ] Run the benchmark suite.
- [ ] Inspect stored run history and trace events.
- [ ] Configure Gemini or Ollama and repeat one task.
- [ ] Explain the known limitations and security boundaries.

## Do not overclaim

Do not state that this is production-grade, fully autonomous, vector RAG, a guaranteed hallucination detector, or a human-in-the-loop system. Do not claim deployment to AWS/Azure/GCP or financial-grade compliance. The project is a local portfolio prototype with CI test automation.
