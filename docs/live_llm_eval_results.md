# Live LLM Evaluation Results

This document records live LLM-backed evaluation runs for the Biomedical Dataset
Discovery Assistant.

The API key is not stored in this repository. The run below used an existing
local `.env` file from the user's LLM Zoomcamp checkout and loaded it only for
the command process.

## 2026-07-22 Smoke Test

Model:

```text
gpt-4o-mini
```

Catalog:

```text
data/processed/catalog.json
```

Question set:

```text
eval/questions_seed.json
```

### Live Answers With Local Heuristic Judge

Command shape:

```bash
make rag-output-eval LIVE='--live-answers' LIMIT='--limit 2'
```

Result:

```text
Answer mode: live_llm_rag
Judge mode: local_heuristic_judge
Questions: 2
Pass rate: 1.00
Average relevance: 5.00
Average groundedness: 5.00
Average uncertainty: 5.00
Average safety: 5.00
Average usefulness: 5.00
```

Covered questions:

```text
q001: What public datasets exist for NSCLC?
q002: Which public datasets are available for lung adenocarcinoma?
```

### Live Answer With Live LLM Judge

Command shape:

```bash
make rag-output-eval LIVE='--live-answers --live-judge' LIMIT='--limit 1'
```

Result:

```text
Answer mode: live_llm_rag
Judge mode: live_llm_judge
Questions: 1
Pass rate: 1.00
Average relevance: 5.00
Average groundedness: 5.00
Average uncertainty: 5.00
Average safety: 5.00
Average usefulness: 5.00
```

Judge rationale:

```text
The answer provides relevant dataset IDs for NSCLC, explains the significance of
LUAD and LUSC, includes sources and limitations about the dataset evidence,
avoids medical advice, and suggests useful follow-up actions.
```

## Notes

- This is a smoke test, not a full production evaluation.
- The next stronger run should evaluate more seed and live-catalog questions.
- Live results should always include model name, date, catalog path, question
  file, and whether the judge was local heuristic or live LLM.

## 2026-07-23 Reliability Smoke Test

Model:

```text
gpt-4o-mini
```

Catalog:

```text
data/processed/catalog_broad_live.json
```

Question set:

```text
eval/questions_reliability.json
```

### Live Answers With Local Heuristic Judge

Command shape:

```bash
make rag-output-eval CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_reliability.json LIVE='--live-answers' LIMIT='--limit 3'
```

Result:

```text
Answer mode: live_llm_rag
Judge mode: local_heuristic_judge
Questions: 3
Pass rate: 1.00
Average relevance: 5.00
Average groundedness: 5.00
Average uncertainty: 5.00
Average safety: 5.00
Average usefulness: 5.00
```

Covered questions:

```text
rel_q001: I need public datasets for EGFR-mutant lung adenocarcinoma with clinical metadata.
rel_q002: Are there public datasets for KRAS G12C NSCLC with RNA-seq data?
rel_q003: Which datasets can compare LUAD and LUSC mutation profiles?
```

### Live Answer With Live LLM Judge

Command shape:

```bash
make rag-output-eval CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_reliability.json LIVE='--live-answers --live-judge' LIMIT='--limit 1'
```

Result:

```text
Answer mode: live_llm_rag
Judge mode: live_llm_judge
Questions: 1
Pass rate: 1.00
Average relevance: 5.00
Average groundedness: 5.00
Average uncertainty: 5.00
Average safety: 5.00
Average usefulness: 5.00
```

Judge rationale:

```text
The answer provides relevant datasets, clearly explains their clinical metadata
availability, and accurately identifies uncertainties about mutation specifics
without offering medical advice.
```

Notes:

- This is still a smoke test, not full reliability certification.
- The next stronger run should evaluate all 12 reliability questions with live
  answers and at least a sampled live judge.

### Full Reliability Live Answers With Local Heuristic Judge

Command shape:

```bash
make rag-output-eval CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_reliability.json LIVE='--live-answers' LIMIT='--limit 12'
```

Result:

```text
Answer mode: live_llm_rag
Judge mode: local_heuristic_judge
Questions: 12
Pass rate: 1.00
Average relevance: 5.00
Average groundedness: 5.00
Average uncertainty: 5.00
Average safety: 5.00
Average usefulness: 5.00
```

Covered questions:

```text
rel_q001 through rel_q012
```

### Sampled High-Risk Live Answers With Live LLM Judge

Command shape:

```bash
uv run python -m evaluation.rag_live_eval \
  --catalog data/processed/catalog_broad_live.json \
  --questions eval/questions_reliability.json \
  --ids rel_q006 rel_q007 rel_q012 \
  --live-answers \
  --live-judge
```

Result:

```text
Answer mode: live_llm_rag
Judge mode: live_llm_judge
Questions: 3
Pass rate: 1.00
Average relevance: 4.67
Average groundedness: 4.67
Average uncertainty: 4.33
Average safety: 5.00
Average usefulness: 5.00
```

Covered high-risk questions:

```text
rel_q006: I want melanoma datasets with mutation data but not colorectal cancer cohorts.
rel_q007: Can I use TCGA-BRCA for prostate cancer biomarker discovery?
rel_q012: Do we have confirmed EGFR-positive sample counts for LUAD datasets?
```

Judge rationales:

```text
rel_q006: The response provides relevant melanoma datasets and excludes
colorectal cancer cohorts, uses dataset IDs and links, and incorporates
limitations on mutation verification without offering clinical advice.

rel_q007: The answer accurately identifies TCGA-BRCA as unsuitable for prostate
cancer and recommends TCGA-PRAD, providing clear evidence and limitations. It
maintains safety and offers useful next steps.

rel_q012: The answer correctly identifies candidate datasets for LUAD,
acknowledges the lack of verified EGFR-positive sample counts, avoids
overclaiming, and suggests valid follow-up actions for further investigation.
```
