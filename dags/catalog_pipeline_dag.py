"""Airflow DAG skeleton for the local catalog pipeline.

This file is intentionally small and optional. It mirrors the local pipeline
commands without making Airflow a default project dependency.
"""

from __future__ import annotations

from datetime import datetime

try:
    from airflow import DAG
    from airflow.operators.bash import BashOperator
except ImportError:  # Airflow is optional for local development.
    DAG = None
    BashOperator = None


if DAG is not None and BashOperator is not None:
    with DAG(
        dag_id="biomedical_catalog_pipeline",
        description="Build and validate the biomedical DatasetRecord catalog.",
        start_date=datetime(2026, 7, 15),
        schedule=None,
        catchup=False,
        tags=["llm-zoomcamp", "biomedical", "catalog"],
    ) as dag:
        ingest_gdc = BashOperator(
            task_id="ingest_gdc",
            bash_command="cd /app && python -m scripts.ingest_gdc",
        )

        ingest_cbioportal = BashOperator(
            task_id="ingest_cbioportal",
            bash_command="cd /app && python -m scripts.ingest_cbioportal",
        )

        build_catalog = BashOperator(
            task_id="build_catalog",
            bash_command="cd /app && python -m scripts.build_catalog",
        )

        validate_catalog = BashOperator(
            task_id="validate_catalog",
            bash_command="cd /app && python -m scripts.validate_catalog",
        )

        retrieval_eval = BashOperator(
            task_id="retrieval_eval",
            bash_command=(
                "cd /app && "
                "PYTHONPATH=. python -m evaluation.retrieval_eval "
                "--catalog data/processed/catalog.json"
            ),
        )

        [ingest_gdc, ingest_cbioportal] >> build_catalog >> validate_catalog >> retrieval_eval
