# Evaluation Methodology

## Purpose

The benchmark subsystem is intended to make workflow behavior repeatable and comparable across providers. It is not a scientific benchmark suite and does not establish factual accuracy.

## Included signals

### Expected-keyword coverage

The fraction of task-specific expected keyword strings that appear in the generated answer. Each phrase is checked case-insensitively.

### Token overlap

Jaccard similarity over non-stopword tokens between the answer and a reference answer. This is a lexical proxy. It does not understand paraphrases, entailment, or context.

### Citation score

When sources are retrieved, counts unique `[KBnnn]` markers in the answer relative to the number of retrieved sources. It only checks marker presence and IDs; it does not prove a cited chunk supports the statement.

### Tool-use score

Compares the expected tool names for a benchmark case with tools actually invoked.

### Latency

Wall-clock elapsed time for the workflow; it includes model-provider round trips and all agent stages.

## Composite score

`overall_score = 0.50 * keyword_coverage + 0.20 * token_overlap + 0.15 * citation_score + 0.15 * tool_use_score`

Scores are between 0 and 1. The weights are configurable by editing `harness/evaluation/scoring.py`.

## Limitations

- Expected keywords can reward superficial keyword stuffing.
- Jaccard token overlap penalizes valid paraphrases.
- Citation presence does not prove entailment or source faithfulness.
- The model-based verifier may itself be wrong or inconsistent.
- Scores can vary by model, prompt, temperature, quota, and backend version.
- Synthetic benchmark documents are only examples.

## Recommended future evaluation

Use a manually reviewed golden dataset, human-rated faithfulness, retrieval precision/recall, claim-level evidence entailment, adversarial prompt-injection tests, repeated runs with confidence intervals, and a separate cost/latency report. Store dataset version and model configuration with every experiment.
