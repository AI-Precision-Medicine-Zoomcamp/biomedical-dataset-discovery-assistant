# Course Requirements Checklist

This checklist maps the project to the LLM Zoomcamp project requirements and
review rubric.

## Summary

Current readiness:

```text
Core RAG project: mostly complete
Reliability evaluation: strong for the current catalog scope
Reviewer experience: documented with runnable walkthrough and screenshots
Monitoring: basic feedback capture and summary page added
Deployment: optional bonus; local Docker Compose is implemented
```

## Requirement Mapping

| Requirement | Current Evidence | Status |
|---|---|---|
| Problem description | `README.md`, `docs/project_status.md`, `docs/domain_background.md` explain biomedical dataset discovery and target users | Complete |
| Knowledge base / data source | GDC and cBioPortal metadata, seed and live/broad catalogs | Complete |
| Ingestion path | `scripts/ingest_gdc.py`, `scripts/ingest_cbioportal.py`, `scripts/build_catalog.py`, `make pipeline`, live catalog targets | Complete |
| Retrieval system | keyword, TF-IDF, constrained hybrid retrieval in `src/retriever.py` | Complete |
| Retrieval evaluation | `evaluation/retrieval_eval.py`, `evaluation/retrieval_compare.py`, seed/live/reliability question sets | Complete |
| LLM-powered answer flow | `src/rag.py` supports live OpenAI calls over retrieved context | Complete |
| End-to-end evaluation | `answer_eval`, `claim_eval`, `rag_live_eval`, live answer and live judge records | Complete |
| Interface | Browser UI at `/`, CLI commands, and HTTP API with `/health`, `/search`, `/ask`, `/feedback`, `/monitoring` | Complete |
| Monitoring / feedback | `POST /feedback` appends JSONL feedback events; `/feedback/summary` and `/monitoring` expose summary metrics | Mostly complete |
| Containerization | `Dockerfile` and `docker-compose.yml` can run the local browser UI/API; local compose healthcheck verified | Mostly complete |
| Reproducibility | `pyproject.toml`, `uv.lock`, Makefile, docs, local seed data | Mostly complete |
| Documentation | README plus project map, status, schema, pipeline, evaluation, live eval, transparent evaluation report | Strong |

## Current Scores Against The Public Rubric

Estimated status using the public LLM Zoomcamp project rubric:

| Rubric Area | Expected Max | Current Estimate | Why |
|---|---:|---:|---|
| Problem description | 2 | 2 | Problem, target user, and scope are clear |
| Retrieval flow | 2 | 2 | Catalog retrieval plus LLM answer flow exists |
| Retrieval evaluation | 2 | 2 | Multiple retrieval methods are evaluated; hybrid is selected |
| LLM evaluation | 2 | 2 | Rule checks, claim verification, live answer eval, sampled live judge |
| Interface | 2 | 2 | Browser UI and HTTP API are available |
| Ingestion pipeline | 2 | 2 | Automated Python ingestion and catalog build |
| Monitoring | 2 | 1-2 | Feedback is collected and summarized; still basic compared with production monitoring |
| Containerization | 2 | 1-2 | Dockerfile and Docker Compose exist; local healthcheck path verified |
| Reproducibility | 2 | 1-2 | Dependencies are pinned and seed mode exists; needs a clean reviewer run |
| Best practices | 3 | 1-2 | Hybrid search exists; reranking/query rewriting are limited |

Estimated readiness:

```text
Passing submission: close
High-scoring submission: needs clean clone-style reviewer verification; video and cloud deployment are optional
```

## Commands Reviewers Can Run

Run tests:

```bash
make test
```

Run the clean local reviewer check:

```bash
make reviewer-check
```

Run the local seed pipeline:

```bash
make pipeline
```

Compare retrieval methods:

```bash
make retrieval-compare CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_reliability.json
```

Evaluate answer guardrails:

```bash
make answer-eval CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_reliability.json
```

Verify answer claims:

```bash
make claim-eval CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_reliability.json
```

Generate the transparent evaluation report:

```bash
make eval-report CATALOG=data/processed/catalog_broad_live.json QUESTIONS=eval/questions_reliability.json
```

Run the API:

```bash
make api
```

Open the browser UI:

```text
http://127.0.0.1:8000/
```

Open the monitoring summary:

```text
http://127.0.0.1:8000/monitoring
```

Run with Docker Compose:

```bash
docker compose up --build
```

Example feedback event:

```bash
curl -s -X POST http://127.0.0.1:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"question": "Which datasets exist for NSCLC?", "rating": 5, "comment": "Useful answer."}'
```

## Remaining Work

Highest priority before final submission:

1. Do a clean clone-style run through the README commands.
2. Repeat the Docker Compose path on a clean checkout.
3. Review `docs/evaluation_report_reliability.md` for weak-but-passing examples.
4. Polish the monitoring page if time allows.

Deferred product depth:

- deeper GDC file metadata
- richer cBioPortal clinical/sample-list metadata
- patient-level mutation or sample-count verification
- GEO/SRA ingestion
