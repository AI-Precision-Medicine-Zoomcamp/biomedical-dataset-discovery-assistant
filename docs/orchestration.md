# Orchestration

The project now includes two orchestration references:

- Kestra flow: `flows/catalog_pipeline.yml`
- Airflow DAG skeleton: `dags/catalog_pipeline_dag.py`

## Recommended Path

For LLM Zoomcamp alignment, use the Kestra flow as the main orchestration
reference.

The course Module 3 focuses on AI orchestration with Kestra, including RAG
workflows, agents, tools, and observability. Our flow mirrors the local pipeline:

```text
ingest_gdc
ingest_cbioportal
-> build_catalog
-> validate_catalog
-> retrieval_eval
-> answer_eval
```

This maps directly to the project requirement for an ingestion pipeline and
keeps the pipeline visible as a sequence of tasks.

## Current Runtime Assumption

The Kestra flow is a course-aligned orchestration scaffold. The current tasks
run commands such as:

```bash
uv run python -m scripts.build_catalog
```

That means a Kestra worker must have this repository mounted or checked out as
its working directory, and `uv` must be available in the worker environment.
Before presenting the flow as reviewer-ready, package the repo into a worker
image or add an explicit checkout/working-directory step.

## Why Not Spark Or Kafka Now

Spark and Kafka are not the right next tools for this project yet.

- Spark is useful for large-scale distributed data processing. Our current data
  is metadata-scale JSON, not large genomic matrices or TB-scale parquet.
- Kafka is useful for streaming events. Our current ingestion is batch metadata
  ingestion, not a real-time event stream.

## Why Keep Airflow

Airflow is kept as an optional data-engineering reference because it is common
in DE workflows. However, it is not the primary course-aligned path right now.

## Current Agent Boundary

The project now has local tools:

- `search_catalog`
- `get_dataset_details`
- `generate_grounded_answer`

And a local agent scaffold:

```bash
make agent
```

This produces a tool trace and uses dataset-detail tool output in the final
answer, but the LLM is not yet autonomously selecting tools.
The next agentic upgrade would be:

```text
LLM decides which tool to call
-> app executes the tool
-> LLM observes tool output
-> LLM decides whether another tool is needed
-> final grounded answer
```

That is closer to a full LLM agent. The current version is the safer scaffold
before adding autonomous tool selection.
