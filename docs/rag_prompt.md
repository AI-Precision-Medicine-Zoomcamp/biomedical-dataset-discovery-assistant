# RAG Prompt Contract

The current prompt is designed for a grounded RAG assistant, not a full
tool-using agent.

## Current Role

The LLM receives:

```text
user question
retrieved DatasetRecord context
evidence items
limitations
source URLs
match levels
```

It should produce a dataset-discovery answer grounded only in that context.

## What The Prompt Must Do

The prompt must force the model to:

- answer dataset-discovery questions, not medical questions
- use only the retrieved catalog context
- cite catalog entries by bracket number, such as `[1]`
- distinguish candidate relevance from confirmed evidence
- avoid claiming confirmed gene, mutation, or KRAS G12C-positive cases unless
  the catalog explicitly verifies them
- mention limitations when metadata is incomplete
- prefer dataset IDs, sources, evidence, and source URLs over general biomedical
  background
- directly answer scoped questions such as whether `TCGA-BRCA` can answer an
  `NSCLC` mutation research question

## What It Is Not Yet

This is not a full LLM agent yet.

A full agent would be able to:

- decide whether it needs to call retrieval
- call tools or APIs
- inspect tool results
- revise its plan
- produce a final answer after tool observations

Our current flow is simpler and safer:

```text
retrieve records
-> build grounded context
-> build prompt
-> call LLM or dry-run
-> evaluate answer
```

This is the right intermediate step before agentic tool use.

The repository now includes a local tool-using scaffold in `src/agent.py`. It
calls tools, returns a trace, and passes `get_dataset_details` output into the
final grounded answer. The LLM does not yet autonomously choose tools.

Current local tool flow:

```text
search_catalog
-> get_dataset_details
-> generate_grounded_answer from those details
```

## Reliability Checks

The prompt is checked in tests and evaluation:

- `tests/test_rag.py` checks prompt guardrails and context inclusion
- `evaluation/answer_eval.py` checks answer-level behavior
- `make answer-eval` verifies answers mention evidence, limitations,
  uncertainty, expected dataset IDs, and avoid medical-advice language

## Live Mode

Dry-run mode is the default and does not call an LLM:

```bash
make rag
```

Live mode calls the OpenAI Responses API and requires `OPENAI_API_KEY`:

```bash
uv run python -m src.rag "What datasets are available for KRAS G12C research in NSCLC?" --live
```

The implementation uses the Responses API shape documented by OpenAI: a model
and input are sent to create a model response.
