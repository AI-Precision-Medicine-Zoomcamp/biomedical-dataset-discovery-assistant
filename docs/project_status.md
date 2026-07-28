# Project Status

This document summarizes the current planning state of the Biomedical Dataset Discovery Assistant.

## Current Stage

The project is in the first runnable prototype stage.

The work has moved beyond planning. The repository now contains a small normalized seed catalog, a local data pipeline, keyword/TF-IDF/hybrid retrieval, retrieval evaluation, unit tests, a deterministic evidence-aware answer layer, a RAG prompt/live-call hook, and a local tool-using agent scaffold. This is not yet a full autonomous LLM agent, but it is enough to test the core dataset-discovery loop:

```text
seed catalog
-> normalized DatasetRecord objects
-> constrained hybrid retrieval
-> evidence-aware answer text
-> retrieval and answer guardrail tests
```

The project also has a minimal HTTP API for reviewer interaction:

```text
HTTP request
-> search or ask endpoint
-> local tool workflow
-> grounded answer plus tool trace
```

The repository also now has a local data pipeline that turns raw seed metadata
extracts into a processed `DatasetRecord` catalog:

```text
source-specific raw metadata
-> data/raw/
-> scripts/build_catalog.py
-> data/processed/catalog.json
-> quality checks
-> retrieval evaluation
```

The GDC and cBioPortal ingestion steps now support optional live API modes while
keeping the default seed mode reproducible:

```bash
uv run python -m scripts.ingest_gdc --live
uv run python -m scripts.ingest_gdc --live --tcga-defaults
uv run python -m scripts.ingest_cbioportal --live --tcga-defaults
```

The broader GDC live mode writes to `data/raw/gdc/projects_live.json` by default
and can be built into `data/processed/catalog_live_gdc.json` with:

```bash
make live-gdc-catalog
```

The broader full live mode writes live GDC and cBioPortal extracts and can be
built into `data/processed/catalog_live.json` with:

```bash
make live-catalog
```

The expanded live mode discovers all current GDC TCGA projects and cBioPortal
TCGA PanCancer Atlas studies, then builds `data/processed/catalog_expanded_live.json`:

```bash
make expanded-live-catalog
```

The broad live mode fetches basic metadata for all public GDC projects returned
by the projects endpoint and combines it with cBioPortal TCGA PanCancer Atlas
metadata, then builds `data/processed/catalog_broad_live.json`:

```bash
make broad-live-catalog
```

This is the current reliability stress-test catalog. It is wider than the
all-TCGA catalog, but the GDC side is intentionally basic project-level
metadata.

## Project Direction

The assistant will help researchers discover public biomedical datasets relevant to diseases, genes, biomarkers, mutations, data types, and research questions.

The core problem:

```text
Public biomedical datasets are spread across different platforms.
Each platform has different metadata structures, terminology, and search workflows.
Researchers need a faster way to identify candidate datasets and understand why they are relevant.
```

The assistant should act as a research data navigation tool, not a medical diagnosis or treatment assistant.

## Target User

The target user is a professional or semi-professional research user, such as:

- biomedical researcher
- bioinformatics analyst
- data scientist working with biomedical datasets
- ML researcher looking for public biomedical datasets

The system should not assume the user is a patient or a general consumer.

## Initial Product Value

The assistant should provide value by:

- collecting metadata from multiple biomedical data sources
- normalizing source-specific metadata into one shared discovery schema
- allowing natural-language dataset discovery queries
- returning candidate datasets with evidence and limitations
- helping users judge which datasets are worth inspecting further

The first version should not claim to cover every public biomedical data source. It should demonstrate a reliable and extensible discovery workflow.

## Confirmed MVP Scope

### Included In First Version

- GDC/TCGA metadata, with optional live ingestion for a broader TCGA project panel
- cBioPortal metadata, with optional live ingestion for TCGA PanCancer study and molecular-profile metadata
- lung cancer focus
- NSCLC, LUAD, and LUSC examples
- RNA-seq, mutation, clinical metadata, and copy number as key data types
- keyword, TF-IDF, and constrained hybrid retrieval over normalized dataset metadata
- deterministic answers grounded in retrieved dataset records
- RAG prompt builder with optional live LLM call
- local tool workflow that searches the catalog, fetches dataset details, and generates a tool-grounded answer
- lightweight HTTP API for `/health`, `/search`, and `/ask`
- basic evaluation questions for dataset discovery

### Deferred Until Later

- GEO ingestion
- SRA ingestion
- Open Targets query expansion
- raw genomic file download
- patient-level mutation analysis
- expression matrix analysis
- treatment recommendation or clinical decision support

## Key Design Decisions

### Source-Specific Records

The first version treats records from different platforms as separate source-specific records.

Example:

```text
gdc:TCGA-LUAD
cbioportal:luad_tcga_pan_can_atlas_2018
```

These can share a `canonical_dataset_id`, such as `TCGA-LUAD`, so the system can show that they refer to related biological data without prematurely merging them.

### Global Dataset IDs

`dataset_id` should be globally unique.

Recommended format:

```text
gdc:TCGA-LUAD
cbioportal:luad_tcga_pan_can_atlas_2018
geo:GSEXXXXX
sra:SRPXXXXX
```

This avoids collisions when the same biological study appears in multiple sources.

### Evidence-Aware Answers

The assistant should not simply return dataset names. It should explain:

- why a dataset matches the query
- which source the information came from
- what data types appear to be available
- whether the match is explicit or inferred
- what limitations remain

If evidence is weak, the assistant should still be helpful, but it must label uncertainty.

### Query-Time Match Level

Match strength should be calculated at query time, not stored permanently in the dataset record.

Reason:

```text
TCGA-LUAD may be a strong match for "NSCLC mutation datasets"
but only a medium match for "KRAS G12C-positive NSCLC cohorts"
if KRAS G12C-positive cases are not explicitly verified.
```

The dataset record should store evidence and limitations. The retrieval/RAG layer should use that evidence to calculate query-specific match levels.

## Current Documents

- `README.md`: project overview and links
- `docs/project_investigation.md`: initial project investigation
- `docs/domain_background.md`: minimum biomedical/domain background
- `docs/data_sources.md`: selected and deferred data sources
- `docs/data_schema.md`: normalized `DatasetRecord` schema
- `docs/project_status.md`: current progress and decisions
- `docs/course_requirements_checklist.md`: mapping from project work to course rubric
- `docs/reviewer_walkthrough.md`: shortest reviewer path for UI, monitoring, Docker, and evaluation
- `docs/evaluation_plan.md`: retrieval and answer evaluation plan
- `docs/evaluation_report_seed.md`: generated by `make reviewer-check` for the default seed catalog
- `docs/evaluation_report_reliability.md`: transparent per-question reliability report
- `docs/live_llm_eval_results.md`: recorded live RAG and live judge smoke-test results
- `eval/questions_seed.json`: initial dataset discovery evaluation questions
- `eval/questions_live.json`: expanded live-catalog evaluation questions
- `eval/questions_reliability.json`: realistic mixed dataset-discovery reliability questions

## Current Implementation

Implemented files:

- `src/models.py`: `DatasetRecord` and `EvidenceItem`
- `src/catalog.py`: seed catalog loading and canonical dataset grouping
- `src/retriever.py`: keyword, TF-IDF, and constrained hybrid retrieval with synonym expansion, exact-ID boost, source preferences, and scope penalties
- `src/answer.py`: deterministic evidence-aware answer generation from retrieved records
- `src/rag.py`: RAG context and prompt builder with optional live LLM call
- `src/tools.py`: local catalog search, detail, and grounded-answer tools
- `src/agent.py`: local tool-using agent scaffold whose final answer uses dataset detail tool output
- `src/api.py`: dependency-free browser UI and HTTP API wrapping search, agent answer, and feedback flows
- `scripts/ingest_gdc.py`: local raw GDC seed extract
- `scripts/ingest_cbioportal.py`: local raw cBioPortal seed extract
- `scripts/build_catalog.py`: raw-to-`DatasetRecord` transform
- `scripts/validate_catalog.py`: processed catalog quality checks
- `pyproject.toml`: `uv` project config and CLI entrypoints
- `Dockerfile`: reproducible container execution
- `docker-compose.yml`: local browser UI/API service with healthcheck; local
  build and `/health` smoke test verified
- `flows/catalog_pipeline.yml`: Kestra flow aligned with the LLM Zoomcamp orchestration module
- `dags/catalog_pipeline_dag.py`: optional Airflow orchestration skeleton
- `evaluation/retrieval_eval.py`: retrieval evaluation with expected-present and expected-absent checks
- `evaluation/retrieval_compare.py`: keyword, TF-IDF, and hybrid retrieval comparison
- `evaluation/answer_eval.py`: rule-based deterministic answer evaluation for groundedness and safety
- `evaluation/llm_judge_eval.py`: LLM-as-judge workflow with local fallback and optional live judge mode
- `evaluation/rag_live_eval.py`: live RAG answer evaluation with optional live judge mode
- `evaluation/claim_eval.py`: reverse claim verification against catalog evidence and expected absent records
- `evaluation/evaluation_report.py`: transparent combined report for retrieval, answer, and claim checks
- `tests/test_retriever.py`: retrieval and grouping tests
- `tests/test_answer.py`: answer guardrail and query-time match-level tests

Current validation commands:

```bash
PYTHONPATH=. python3 -m evaluation.retrieval_eval
PYTHONPATH=. python3 -m evaluation.retrieval_compare
PYTHONPATH=. python3 -m unittest discover -s tests
PYTHONPATH=. python3 -m src.answer "What datasets are available for KRAS G12C research in NSCLC?"
make pipeline
make test
uv run python -m scripts.ingest_gdc --live
make rag
make agent
make api
make answer-eval
make answer-eval CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_reliability.json
make llm-judge-eval
make rag-output-eval LIVE='--live-answers' LIMIT='--limit 2'
make claim-eval
make expanded-live-catalog
make expanded-answer-eval
make retrieval-compare CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_live.json
make claim-eval CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_live.json
make retrieval-compare CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_reliability.json
make claim-eval CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_reliability.json
make eval-report CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_reliability.json
make reviewer-check
```

Current evaluation shape:

- positive questions check whether expected records and sources appear
- negative checks ensure out-of-scope records such as BRCA do not appear for explicit NSCLC queries
- retrieval comparison evaluates keyword, TF-IDF, and hybrid methods on the same question set
- answer checks verify that KRAS G12C answers label uncertainty instead of claiming confirmed variant-positive cohorts
- LLM-as-judge workflow scores relevance, groundedness, uncertainty, safety,
  and usefulness; default mode is a local fallback, while live judging is
  available with `LIVE=--live`
- reverse claim verification checks generated answers against expected,
  explicitly absent, and unsupported variant-count claims
- live LLM smoke testing has passed on a small seed-question sample and is
  recorded in `docs/live_llm_eval_results.md`
- live-catalog questions check additional cancer types such as colorectal cancer, melanoma, prostate cancer, kidney cancer, brain/glioma, and methylation profile availability
- broad-catalog questions now cover 18 multi-cancer and source-specific scenarios
  across GDC and cBioPortal, with negative checks for out-of-scope records
- current claim verification results are `14/14` on the seed catalog and `18/18`
  on the broad live catalog
- reliability questions now cover 12 mixed real-user scenarios combining
  biomarker, disease, source, modality, and exclusion constraints; current broad
  live catalog results are retrieval `1.00/1.00/1.00/1.00`, answer pass rate
  `1.00`, and claim pass rate `1.00`
- retrieval now handles simple exclusion wording such as "not colorectal" so
  irrelevant cohorts are not pulled into answers for negated user constraints
- reliability live RAG evaluation has passed on all 12 reliability questions
  with the local heuristic judge
- sampled high-risk live LLM judge checks pass on exclusion, out-of-scope, and
  confirmed-count reliability questions
- a transparent reliability report now explains each pass/fail decision by
  showing expected datasets, retrieved datasets, answer checks, claim checks,
  and answer excerpts
- basic feedback capture is available through `POST /feedback`, writing JSONL
  events under `data/feedback/`
- feedback metrics are visible through `GET /feedback/summary` and the
  browser monitoring page at `/monitoring`

## Next Implementation Steps

1. Review the transparent evaluation report for weak-but-passing cases.
2. Add sampled live LLM judge coverage across more reliability question types.
3. Extend live GDC extraction from project metadata to file metadata.
4. Add richer cBioPortal clinical/sample-list extraction.
5. Tune the LLM-backed RAG prompt using live model outputs.
6. Upgrade the fixed local tool workflow into autonomous LLM tool selection, or explicitly keep it as a transparent pipeline-style agent.
7. Repeat the Docker Compose reviewer check from a clean checkout.

## Current Risks

- Metadata may not be detailed enough to confirm specific mutations such as KRAS G12C.
- GDC and cBioPortal may contain overlapping biological studies with different metadata structures.
- The catalog is still tiny and too small to prove broad source coverage.
- The pipeline defaults to curated seed extracts; GDC and cBioPortal both have optional live API modes.
- Plain lexical or TF-IDF retrieval can over-match terms that appear in
  limitations or negated statements; the default constrained hybrid method keeps
  scope guardrails in front of TF-IDF reranking.
- The local agent has real tool usage, but its tool order is still fixed rather than chosen autonomously by an LLM.
- If retrieval/detail records are too shallow, the LLM answer will be vague.
- If uncertainty is not labeled, the assistant may sound more confident than the evidence supports.
- The project has a live LLM evaluation smoke test, but the sample is still
  small and needs broader coverage before final submission.
- The project still needs monitoring dashboard polish and a clean clone-style
  reviewer run to score well as a final capstone. A walkthrough video remains
  optional because the README now includes UI and monitoring screenshots.

## Working Principle

Build the project in small layers:

```text
domain understanding
-> source selection
-> normalized schema
-> seed catalog
-> retrieval
-> RAG
-> evaluation
-> UI
```

This keeps the project professional without making the first version too large to finish.
