# Task routing (v1.3.0)

The harness uses bounded, deterministic routing for the supported task types:

- **Calculation**: extracts a basic arithmetic expression and runs the restricted AST calculator. It skips knowledge retrieval and model generation.
- **Knowledge**: searches local Markdown/text documents and passes retrieved source snippets to the Executor. Benchmark metadata can explicitly require `knowledge_search`, ensuring that a benchmark case tests the intended retrieval path even when its natural-language question does not mention a policy or document.
- **File creation**: recognizes supported filename requests (`.txt`, `.text`, `.md`, `.json`, `.csv`, `.py`) and creates the file inside the sandbox `workspace/` directory. Requests without a filename are not executed.
- **General**: skips retrieval and sends the question to the selected LLM provider.

The Planner uses bounded route templates for these known task types. Research summaries are assembled from the tool outputs instead of using a separate model call. The Verifier performs deterministic citation/tool checks by default. Set `MODEL_VERIFIER_ENABLED=true` in `.env` to enable an additional, advisory model-review call (which increases latency).

The benchmark runner processes each task independently. If one case fails, it still returns a result row with `status: failed`, an error description, latency, and zero overall score; other cases continue. Aggregate scores include failed cases as zero overall score so failures cannot disappear from the benchmark average. The frontend displays missing fields as `—` and provides an Inspect panel for each row.

These checks are engineering signals, not guarantees of factual correctness. The calculator is restricted to basic arithmetic and does not execute Python code. Files created through the agent are inside the project workspace, not arbitrary locations on the computer.
