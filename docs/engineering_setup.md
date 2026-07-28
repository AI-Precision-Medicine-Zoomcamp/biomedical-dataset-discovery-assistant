# Engineering Setup

This project follows the LLM Zoomcamp style of keeping the application runnable
from a clean Python project, while also borrowing data engineering structure for
the metadata pipeline.

## Local Python Runtime

The project uses:

- `.python-version` for the preferred Python version
- `pyproject.toml` for project metadata and command entrypoints
- `uv` for local execution

This repo sets `UV_CACHE_DIR=.uv-cache` in the `Makefile` so local commands do
not depend on write access to the global `~/.cache/uv` directory.

Install/sync the environment:

```bash
uv sync
```

If your shell has the same cache permission issue, run:

```bash
UV_CACHE_DIR=.uv-cache uv sync
```

Run the full local catalog pipeline:

```bash
make pipeline
```

Equivalent explicit commands:

```bash
uv run python -m scripts.ingest_gdc
uv run python -m scripts.ingest_cbioportal
uv run python -m scripts.build_catalog
uv run python -m scripts.validate_catalog
uv run python -m evaluation.retrieval_eval --catalog data/processed/catalog.json
```

Run tests:

```bash
make test
```

Run an evidence-aware answer:

```bash
make answer
```

Or pass a custom question:

```bash
make answer QUESTION="Can TCGA-BRCA answer an NSCLC mutation research question?"
```

## Docker

Docker is useful for reproducibility: another reviewer can run the same pipeline
or evaluation without depending on the exact local Python setup.

The Compose stack exposes:

- Streamlit reviewer UI on `http://127.0.0.1:8501/`
- HTTP API and dependency-free fallback UI on `http://127.0.0.1:8000/`

Build the image:

```bash
make docker-build
```

Run the default retrieval evaluation inside the image:

```bash
make docker-run
```

The current Docker image is intentionally simple. It is not a production API
container yet.

## Airflow

Airflow is treated as an optional orchestration layer.

The DAG skeleton lives at:

```text
dags/catalog_pipeline_dag.py
```

It mirrors the local pipeline:

```text
ingest_gdc
ingest_cbioportal
-> build_catalog
-> validate_catalog
-> retrieval_eval
```

Airflow is not included in the default dependencies because it is heavy and not
needed to understand or validate the current project. When the pipeline becomes
larger or scheduled, this DAG can be moved into a real Airflow environment.

## Why This Setup

This setup separates concerns:

- `uv` manages the Python project and local commands.
- `scripts/` contains deterministic data pipeline steps.
- `Dockerfile` supports reproducible execution.
- `dags/` shows how the same pipeline maps to DE orchestration.
- `src/` keeps retrieval and answer logic separate from ingestion.

That means we can grow the project without mixing pipeline code, retrieval code,
and deployment code into one script.
