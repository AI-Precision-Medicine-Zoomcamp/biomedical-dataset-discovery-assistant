# Project Map

This is the navigation map for the Biomedical Dataset Discovery Assistant.
Use this file when the repository feels large.

## Product In One Sentence

The project helps research users discover public biomedical cancer datasets by
searching normalized metadata from GDC and cBioPortal, then explaining candidate
datasets with evidence and limitations.

It is not a medical diagnosis, treatment, or biological interpretation system.

## Main Story

The whole project follows one pipeline:

```text
public metadata sources
-> raw source extracts
-> normalized DatasetRecord catalog
-> retrieval
-> grounded answer
-> tool trace / API
-> evaluation
```

The point is not to build a general medical chatbot. The point is to make public
dataset discovery faster, more transparent, and safer.

## Current Course Position

```text
Problem description                done
Ingestion pipeline                 done for project/study metadata
Knowledge base / catalog           done
Retrieval flow                     done
Multiple retrieval methods         done: keyword, TF-IDF, constrained hybrid
RAG / answer generation            done as deterministic + optional live LLM flow
Tool-using agent scaffold          done as transparent local tool workflow
Reviewer interface                 done as browser UI plus HTTP API
Retrieval evaluation               done
Answer guardrail evaluation        done as rule-based checks
LLM-as-judge evaluation            workflow done; live judge smoke test passed
Monitoring / feedback              done: feedback capture plus summary page
Full docker-compose app stack       done for local UI/API
```

## Directory Roles

### `data/`

Stores source extracts and processed catalogs.

```text
data/raw/
  gdc/
  cbioportal/

data/processed/
  seed_catalog.json
  catalog.json
```

Important generated catalogs:

```text
data/processed/catalog.json
  default reproducible local catalog
  6 records from seed GDC + seed cBioPortal extracts

data/processed/catalog_expanded_live.json
  all discovered GDC TCGA projects + cBioPortal TCGA PanCancer Atlas studies
  65 records in the latest successful run

data/processed/catalog_broad_live.json
  broad GDC project metadata + cBioPortal TCGA PanCancer Atlas studies
  123 records in the latest successful run
```

Most live/broad generated files are ignored by git because they can be
regenerated.

### `docs/reviewer_walkthrough.md`

The shortest reviewer path for running the UI, feedback summary, Docker Compose
app, and reliability evaluation commands.

### `scripts/`

Data pipeline code.

```text
scripts/ingest_gdc.py
  extract GDC seed or live project metadata

scripts/ingest_cbioportal.py
  extract cBioPortal seed or live study/molecular-profile metadata

scripts/build_catalog.py
  transform raw source metadata into DatasetRecord JSON

scripts/validate_catalog.py
  check catalog quality and required fields
```

This layer answers:

```text
Where did the data come from?
Can we rebuild the catalog?
Is the normalized schema valid?
```

### `src/`

Application logic.

```text
src/models.py
  DatasetRecord and EvidenceItem schema

src/catalog.py
  load catalogs and group source views by canonical dataset ID

src/retriever.py
  keyword, TF-IDF, and constrained hybrid retrieval

src/answer.py
  deterministic evidence-aware answer generation

src/rag.py
  prompt/context builder and optional live LLM call

src/tools.py
  local tools: search, dataset details, grounded answer

src/agent.py
  transparent tool-using workflow with trace

src/api.py
  dependency-free browser UI plus HTTP API for reviewer interaction and feedback capture
```

This layer answers:

```text
Can the assistant find relevant datasets?
Can it explain why they match?
Can it avoid overclaiming?
Can a reviewer interact with it?
Can a reviewer leave feedback?
```

### `evaluation/` And `eval/`

Evaluation code and question sets.

```text
eval/questions_seed.json
  smaller seed-catalog evaluation set

eval/questions_live.json
  broader multi-cancer live/broad catalog evaluation set

eval/questions_reliability.json
  realistic mixed queries for biomarker, modality, source, and exclusion reliability

evaluation/retrieval_eval.py
  evaluate one retrieval method

evaluation/retrieval_compare.py
  compare keyword, TF-IDF, and hybrid retrieval

evaluation/answer_eval.py
  rule-based groundedness and safety checks for answers

evaluation/llm_judge_eval.py
  LLM-as-judge workflow with local fallback and optional live judge mode

evaluation/rag_live_eval.py
  live RAG answer evaluation with optional live judge mode

evaluation/claim_eval.py
  reverse-check answer claims against catalog evidence and absent records

evaluation/evaluation_report.py
  generate a per-question report explaining retrieval, answer, and claim checks
```

This layer answers:

```text
Which retrieval method works best?
Do out-of-scope records leak into top-k?
Does the answer mention evidence and limitations?
Does it avoid medical advice?
Does it avoid unsupported mutation-positive case-count claims?
Why did each evaluation case pass or fail?
```

### `docs/`

Project explanation and reviewer context.

```text
docs/project_map.md
  this navigation file

docs/project_status.md
  current implementation status and next steps

docs/data_pipeline.md
  ingestion and catalog-building details

docs/data_schema.md
  DatasetRecord schema explanation

docs/evaluation_plan.md
  retrieval and answer evaluation design

docs/live_llm_eval_results.md
  recorded live RAG and live judge smoke-test results

docs/rag_prompt.md
  answer contract and prompt behavior

docs/engineering_setup.md
  uv, Docker, Airflow, and local execution

docs/orchestration.md
  Kestra/Airflow mapping

docs/domain_background.md
  biomedical context for non-specialists

docs/data_sources.md
  source choices and deferred sources
```

This layer answers:

```text
Can someone understand the project without watching us build it?
Can a reviewer find the scoring evidence quickly?
```

### `tests/`

Regression tests.

```text
tests/test_pipeline.py
tests/test_retriever.py
tests/test_answer.py
tests/test_rag.py
tests/test_agent.py
tests/test_api.py
tests/test_answer_eval.py
tests/test_orchestration_files.py
```

This layer answers:

```text
Did we break the pipeline, retrieval, answer guardrails, API, or orchestration files?
```

### Root Files

```text
Makefile
  main command interface

pyproject.toml
  Python project metadata for uv

Dockerfile
  reproducible container execution

flows/catalog_pipeline.yml
  Kestra-style orchestration flow

dags/catalog_pipeline_dag.py
  optional Airflow DAG skeleton
```

## Main Commands

Default local pipeline:

```bash
make pipeline
make test
make eval
make answer-eval
```

Compare retrieval methods:

```bash
make retrieval-compare
make retrieval-compare CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_live.json
```

Build larger catalogs:

```bash
make expanded-live-catalog
make broad-live-catalog
```

Run the tool workflow:

```bash
make agent
```

Run the local HTTP API:

```bash
make api
```

Then call:

```bash
curl -s http://127.0.0.1:8000/health
curl -s "http://127.0.0.1:8000/search?question=Which%20datasets%20exist%20for%20NSCLC%3F"
```

## What Is Stable Now

- The local seed pipeline is reproducible.
- GDC and cBioPortal live metadata ingestion exists.
- Broad GDC metadata ingestion exists.
- The catalog schema is normalized and validated.
- Retrieval supports keyword, TF-IDF, and constrained hybrid methods.
- The current default retrieval method is constrained hybrid.
- Retrieval comparison shows plain TF-IDF can retrieve expected records but has
  weaker absent-hit behavior.
- Deterministic answers include evidence, limitations, and non-clinical guardrails.
- The local tool workflow returns a trace.
- The lightweight API works for reviewer interaction.

## Current Weak Spots

- GDC broad metadata is wide but not deep; it is project-level basic metadata.
- The system does not verify patient-level mutation counts such as KRAS
  G12C-positive cohorts.
- Live LLM answers have passed on the reliability question set, with sampled
  high-risk live judge checks recorded.
- The current agent has real tool usage, but tool order is still fixed rather
  than chosen autonomously by an LLM.
- Basic feedback capture is implemented through `POST /feedback`, and a simple
  monitoring summary is available at `/monitoring`.
- The browser UI and feedback/monitoring summary work locally.
- Docker Compose runs the complete local UI/API application with a healthcheck.

## How To Read The Repo

If you are a reviewer, start here:

```text
README.md
docs/project_map.md
docs/evaluation_plan.md
make test
make retrieval-compare
make api
```

If you are debugging data:

```text
docs/data_pipeline.md
scripts/
data/raw/
data/processed/
```

If you are debugging answer quality:

```text
src/retriever.py
src/answer.py
src/rag.py
evaluation/
eval/
```

If you are improving the project after the capstone:

```text
1. review weak-but-passing reliability cases
2. richer monitoring and operational metrics
3. deeper GDC/cBioPortal metadata
4. autonomous LLM tool selection
```
