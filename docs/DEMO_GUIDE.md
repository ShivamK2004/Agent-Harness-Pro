# Demo and Portfolio Walkthrough

## Suggested 5–7 minute demo

1. Start Streamlit with `LLM_PROVIDER=mock` and show that the app works offline.
2. Open Agent Playground and ask: `What is the sample support response time?`
3. Show the cited local source, tool output, evaluation object, and stage trace.
4. Ask an arithmetic task such as `Calculate 125 * 8 + 40` and show the calculator tool result.
5. Open Benchmark Lab and run all bundled cases.
6. Open Run History to demonstrate SQLite persistence.
7. Switch to Gemini or Ollama only after setting up credentials/model locally; compare the same tasks with the same benchmark dataset.

## Suggested interview explanation

"I built a provider-agnostic agent harness with planner, researcher, executor, and verifier stages. The workflow is observable through trace events, and tools are allowlisted rather than executing arbitrary model-generated code. It retrieves local Markdown evidence with line-aware source identifiers, runs benchmark tasks, computes transparent heuristic metrics, and stores results in SQLite. Gemini and Ollama are adapters behind one provider interface, while Mock mode supports offline tests."

## Be accurate when presenting it

- Say "lexical retrieval" rather than vector RAG; the included index uses token overlap.
- Say "heuristic hallucination/citation checks" rather than guaranteed hallucination detection.
- Say "multi-agent workflow prototype" rather than production autonomous agents.
- Do not claim CI/CD, cloud deployment, observability stack, or human approval workflow unless you add and test them.
- Replace the sample synthetic support documents with your own non-sensitive demo corpus before showcasing it.


Try these deterministic tool examples in the Playground:

- `What is 25 multiplied by 4?` — uses the restricted calculator.
- `Can you create a shivam.text file?` — creates an empty file at `workspace/shivam.text` and verifies it.
- `What is the sample support response time?` — local knowledge retrieval when routed as a knowledge task.
