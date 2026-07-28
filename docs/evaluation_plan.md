# Evaluation Plan

This document defines the initial evaluation approach for the Biomedical Dataset Discovery Assistant.

Evaluation should measure two separate parts of the system:

1. Retrieval: did the system find the right dataset records?
2. RAG answer quality: did the assistant explain the results correctly and safely?

Keeping these separate helps diagnose failures. A bad final answer may come from weak retrieval, incomplete metadata, or a poor prompt.

## Evaluation Scope

The first evaluation set should focus on dataset discovery, not general biomedical knowledge.

Initial scope:

- lung cancer
- NSCLC
- LUAD
- LUSC
- EGFR
- KRAS
- KRAS G12C
- RNA-seq
- mutation data
- clinical metadata

## Retrieval Evaluation

Retrieval evaluation checks whether expected dataset records appear in the top results.

Candidate metrics:

- `hit_rate_at_k`: whether at least one expected dataset appears in the top-k results
- `top_hit_rate`: whether the highest ranked result is one of the expected top records
- `recall_at_k`: how many expected datasets were retrieved in the top-k results
- `precision_at_k`: how many retrieved results are relevant
- `source_coverage`: whether expected source systems appear in the results
- `absent_hit_rate`: whether explicitly out-of-scope records are kept out of top-k

For the first prototype, `hit_rate_at_5` was enough. The current evaluation is
stricter: it also checks top result quality, source-specific retrieval, and
negative examples such as preventing BRCA from appearing in EGFR/KRAS NSCLC
queries.

Current implementation:

```bash
uv run python -m evaluation.retrieval_eval --catalog data/processed/catalog.json
```

Run the broader live-catalog evaluation:

```bash
uv run python -m evaluation.retrieval_eval --catalog data/processed/catalog_broad_live.json --questions eval/questions_live.json
```

Compare retrieval methods:

```bash
make retrieval-compare
make retrieval-compare CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_live.json
make retrieval-compare CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_reliability.json
```

Current methods:

- `keyword`: tuned lexical retrieval with synonym expansion, exact-ID boosts,
  source preferences, and disease-scope penalties
- `tfidf`: in-memory TF-IDF cosine baseline over normalized catalog text
- `hybrid`: keyword-gated candidate recall plus TF-IDF reranking signal

The current default is `hybrid`. In the broad live-catalog comparison, plain
TF-IDF reached the expected datasets but had weaker absent-hit behavior, which
means it allowed more explicitly out-of-scope records into top-k. The constrained
hybrid method kept the keyword guardrails while still evaluating a vector-style
signal.

## Answer Evaluation

Answer evaluation checks whether the final RAG answer is useful, grounded, and honest about uncertainty.

The answer should:

- name relevant dataset IDs
- name the source systems
- explain why each dataset matches the query
- mention important available data types
- distinguish explicit evidence from inferred relevance
- include limitations when evidence is weak
- avoid medical advice or treatment recommendations

Current implementation:

```bash
uv run python -m evaluation.answer_eval --catalog data/processed/catalog.json
```

This is currently a deterministic rule-based guardrail check over the local
answer generator. It is useful for catching obvious regressions, but it is not
yet live LLM output evaluation or LLM-as-judge.

## LLM-As-Judge Evaluation

The project also includes an LLM-as-judge workflow:

```bash
make llm-judge-eval
make llm-judge-eval CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_live.json
```

The judge scores each answer from 1 to 5 on:

- relevance
- groundedness
- uncertainty
- safety
- usefulness

By default, this command uses a local heuristic fallback so the repository stays
runnable without external credentials. This local fallback is useful for testing
the judge pipeline, prompt construction, and report shape, but it should not be
presented as a live LLM judgment.

To run a live LLM judge:

```bash
OPENAI_API_KEY=... make llm-judge-eval LIVE=--live
```

Live judge results should be reported separately from the local heuristic judge
because they involve an external model and may vary by model/version.

## Reverse Claim Verification

The project also uses a course-style "answer, then verify" loop:

```bash
make claim-eval
make claim-eval CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_live.json
```

This check treats the generated answer as a set of claims and verifies them
against the catalog and evaluation question metadata. It currently checks:

- expected datasets are mentioned by source-specific ID or canonical ID
- open-ended dataset-list questions can use `min_expected_dataset_hits` so the
  evaluator does not require every example dataset to appear in a short top-k
  answer
- explicitly absent datasets do not leak into answers
- mutation-positive case/sample/count claims are not made unless supported by
  explicit catalog evidence
- questions asking for confirmed variant counts clearly receive uncertainty
  language when the catalog lacks that evidence

Current status:

- seed catalog: `14/14`, claim pass rate `1.00`
- broad live catalog: `18/18`, claim pass rate `1.00`

The cBioPortal methylation-profile question uses `min_expected_dataset_hits`
because it is an open-ended discovery question with many valid matching studies;
the answer should return useful matching datasets, not necessarily every
handwritten example in the evaluation file.

## Failure Diagnosis

When an answer is weak, diagnose the failure source:

```text
Wrong or missing datasets
-> retrieval problem

Right datasets, but metadata lacks enough detail
-> catalog/schema problem

Enough context, but vague or unsupported answer
-> prompt/RAG generation problem

Question requires patient-level data not in metadata
-> scope limitation
```

## Initial Evaluation Questions

These questions are also stored in `eval/questions_seed.json`.

1. What public datasets exist for NSCLC?
2. Which public datasets are available for lung adenocarcinoma?
3. Which datasets are available for lung squamous cell carcinoma?
4. Compare TCGA-LUAD and TCGA-LUSC.
5. Which datasets contain RNA-seq data for lung cancer?
6. Which datasets can support EGFR mutation research?
7. Which datasets can support KRAS mutation research?
8. What datasets are available for KRAS G12C research in NSCLC?
9. Which datasets include both clinical metadata and molecular data?
10. Which cBioPortal studies are relevant to NSCLC?

The live evaluation file, `eval/questions_live.json`, expands the test set to
18 questions across colorectal, melanoma, prostate, kidney, brain/glioma,
ovarian, bladder, gastric, liver, thyroid, cervical, uterine/endometrial, head
and neck, source-specific GDC/cBioPortal, copy-number, methylation, mutation,
and clinical metadata scenarios.

The reliability evaluation file, `eval/questions_reliability.json`, adds 12
more realistic dataset-discovery questions that combine disease, source,
biomarker, modality, and exclusion constraints. Examples include EGFR-mutant
LUAD with clinical metadata, KRAS G12C NSCLC with RNA-seq, cBioPortal mutation
plus copy-number queries, GDC-specific glioma transcriptomics, and "melanoma but
not colorectal" exclusion wording.

Current reliability-set status on `data/processed/catalog_broad_live.json`:

- retrieval comparison: hybrid `dataset=1.00`, `top=1.00`, `source=1.00`, `absent=1.00`
- answer evaluation: `12/12`, pass rate `1.00`
- claim verification: `12/12`, pass rate `1.00`

## Match Strength Guidance

Match strength should be calculated at query time.

Example:

```text
Query: What datasets are available for KRAS G12C research in NSCLC?
```

Possible labels:

- `strong`: metadata explicitly mentions KRAS G12C
- `medium`: dataset has KRAS or mutation data, but KRAS G12C-positive cases are not explicitly verified
- `weak`: dataset is lung cancer-related and has mutation profiling, but gene or variant relevance is not verified

The assistant may return medium or weak candidate datasets, but it must label uncertainty and explain limitations.

## Initial Evaluation File Shape

Each evaluation question should eventually include:

```json
{
  "id": "q001",
  "question": "What public datasets exist for NSCLC?",
  "expected_dataset_ids": ["gdc:TCGA-LUAD", "gdc:TCGA-LUSC"],
  "expected_absent_dataset_ids": ["gdc:TCGA-BRCA"],
  "min_expected_dataset_hits": 2,
  "expected_sources": ["GDC"],
  "expected_keywords": ["NSCLC", "LUAD", "LUSC", "lung"],
  "answer_checks": [
    "mentions relevant dataset IDs",
    "explains why LUAD and LUSC are relevant to NSCLC",
    "does not provide medical advice"
  ]
}
```

This structure can be expanded after the seed catalog is created.
