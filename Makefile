.PHONY: ingest ingest-gdc-live ingest-cbioportal-live ingest-gdc-all-tcga ingest-gdc-all-projects ingest-cbioportal-all-tcga build-catalog validate eval retrieval-compare answer answer-eval llm-judge-eval rag-output-eval claim-eval eval-report reviewer-check expanded-answer-eval broad-answer-eval rag agent api streamlit ui test pipeline live-gdc-catalog live-catalog expanded-live-catalog broad-live-catalog docker-build docker-run

CATALOG ?= data/processed/catalog.json
QUESTIONS ?= eval/questions_seed.json
REPORT_OUTPUT ?= docs/evaluation_report_reliability.md
GDC_LIVE_RAW ?= data/raw/gdc/projects_live.json
CBIOPORTAL_LIVE_RAW ?= data/raw/cbioportal/studies_live.json
GDC_ALL_TCGA_RAW ?= data/raw/gdc/projects_all_tcga_live.json
GDC_ALL_PROJECTS_RAW ?= data/raw/gdc/projects_all_live.json
CBIOPORTAL_ALL_TCGA_RAW ?= data/raw/cbioportal/studies_all_tcga_live.json
LIVE_CATALOG ?= data/processed/catalog_live_gdc.json
FULL_LIVE_CATALOG ?= data/processed/catalog_live.json
EXPANDED_LIVE_CATALOG ?= data/processed/catalog_expanded_live.json
BROAD_LIVE_CATALOG ?= data/processed/catalog_broad_live.json
GDC_PROJECT_LIMIT ?= 120
QUESTION ?= What datasets are available for KRAS G12C research in NSCLC?
MODEL ?= gpt-4o-mini
LIVE ?=
LIMIT ?=
export UV_CACHE_DIR ?= .uv-cache

ingest:
	uv run python -m scripts.ingest_gdc
	uv run python -m scripts.ingest_cbioportal

ingest-gdc-live:
	uv run python -m scripts.ingest_gdc --live --tcga-defaults --output $(GDC_LIVE_RAW)

ingest-cbioportal-live:
	uv run python -m scripts.ingest_cbioportal --live --tcga-defaults --output $(CBIOPORTAL_LIVE_RAW)

ingest-gdc-all-tcga:
	uv run python -m scripts.ingest_gdc --live --all-tcga --output $(GDC_ALL_TCGA_RAW)

ingest-gdc-all-projects:
	uv run python -m scripts.ingest_gdc --live --all-projects --limit $(GDC_PROJECT_LIMIT) --output $(GDC_ALL_PROJECTS_RAW)

ingest-cbioportal-all-tcga:
	uv run python -m scripts.ingest_cbioportal --live --all-tcga --output $(CBIOPORTAL_ALL_TCGA_RAW)

build-catalog:
	uv run python -m scripts.build_catalog --output $(CATALOG)

validate:
	uv run python -m scripts.validate_catalog --catalog $(CATALOG)

eval:
	uv run python -m evaluation.retrieval_eval --catalog $(CATALOG) --questions $(QUESTIONS)

retrieval-compare:
	uv run python -m evaluation.retrieval_compare --catalog $(CATALOG) --questions $(QUESTIONS)

answer-eval:
	uv run python -m evaluation.answer_eval --catalog $(CATALOG) --questions $(QUESTIONS)

llm-judge-eval:
	uv run python -m evaluation.llm_judge_eval --catalog $(CATALOG) --questions $(QUESTIONS) --model $(MODEL) $(LIVE) $(LIMIT)

rag-output-eval:
	uv run python -m evaluation.rag_live_eval --catalog $(CATALOG) --questions $(QUESTIONS) --model $(MODEL) $(LIVE) $(LIMIT)

claim-eval:
	uv run python -m evaluation.claim_eval --catalog $(CATALOG) --questions $(QUESTIONS) $(LIMIT)

eval-report:
	uv run python -m evaluation.evaluation_report --catalog $(CATALOG) --questions $(QUESTIONS) --output $(REPORT_OUTPUT) $(LIMIT)

reviewer-check:
	$(MAKE) test
	$(MAKE) pipeline
	$(MAKE) retrieval-compare
	$(MAKE) answer-eval
	$(MAKE) claim-eval
	$(MAKE) eval-report REPORT_OUTPUT=docs/evaluation_report_seed.md

expanded-answer-eval:
	uv run python -m evaluation.answer_eval --catalog $(EXPANDED_LIVE_CATALOG) --questions eval/questions_live.json

broad-answer-eval:
	uv run python -m evaluation.answer_eval --catalog $(BROAD_LIVE_CATALOG) --questions eval/questions_live.json

answer:
	uv run python -m src.answer "$(QUESTION)" --catalog $(CATALOG)

rag:
	uv run python -m src.rag "$(QUESTION)" --catalog $(CATALOG) --model $(MODEL)

agent:
	uv run python -m src.agent "$(QUESTION)" --catalog $(CATALOG)

api:
	uv run python -m src.api --catalog $(CATALOG)

streamlit:
	uv run streamlit run src/streamlit_app.py

ui: streamlit

test:
	uv run python -m unittest discover -s tests

pipeline: ingest build-catalog validate eval

live-gdc-catalog: ingest-gdc-live
	uv run python -m scripts.ingest_cbioportal
	uv run python -m scripts.build_catalog --gdc-raw $(GDC_LIVE_RAW) --output $(LIVE_CATALOG)
	uv run python -m scripts.validate_catalog --catalog $(LIVE_CATALOG)
	uv run python -m evaluation.retrieval_eval --catalog $(LIVE_CATALOG)

live-catalog: ingest-gdc-live ingest-cbioportal-live
	uv run python -m scripts.build_catalog --gdc-raw $(GDC_LIVE_RAW) --cbioportal-raw $(CBIOPORTAL_LIVE_RAW) --output $(FULL_LIVE_CATALOG)
	uv run python -m scripts.validate_catalog --catalog $(FULL_LIVE_CATALOG)
	uv run python -m evaluation.retrieval_eval --catalog $(FULL_LIVE_CATALOG)

expanded-live-catalog: ingest-gdc-all-tcga ingest-cbioportal-all-tcga
	uv run python -m scripts.build_catalog --gdc-raw $(GDC_ALL_TCGA_RAW) --cbioportal-raw $(CBIOPORTAL_ALL_TCGA_RAW) --output $(EXPANDED_LIVE_CATALOG)
	uv run python -m scripts.validate_catalog --catalog $(EXPANDED_LIVE_CATALOG)
	uv run python -m evaluation.retrieval_eval --catalog $(EXPANDED_LIVE_CATALOG) --questions eval/questions_live.json

broad-live-catalog: ingest-gdc-all-projects ingest-cbioportal-all-tcga
	uv run python -m scripts.build_catalog --gdc-raw $(GDC_ALL_PROJECTS_RAW) --cbioportal-raw $(CBIOPORTAL_ALL_TCGA_RAW) --output $(BROAD_LIVE_CATALOG)
	uv run python -m scripts.validate_catalog --catalog $(BROAD_LIVE_CATALOG)
	uv run python -m evaluation.retrieval_eval --catalog $(BROAD_LIVE_CATALOG) --questions eval/questions_live.json

docker-build:
	docker build -t biomedical-dataset-discovery .

docker-run:
	docker run --rm biomedical-dataset-discovery
