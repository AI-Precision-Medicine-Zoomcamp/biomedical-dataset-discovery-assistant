# Week 3 Meeting Prep

This document maps the Biomedical Dataset Discovery Assistant project to the Week 3 theme:

```text
Project Definition -> Knowledge Base Construction
```

## Project Summary

Project: Biomedical Dataset Discovery Assistant

Goal:

Help professional research users discover public biomedical datasets relevant to diseases, genes, biomarkers, mutations, data types, and research questions.

Core problem:

Public biomedical datasets are distributed across multiple platforms. Each platform has different metadata structures, terminology, and search workflows. The assistant will normalize metadata across sources and help users identify candidate datasets with evidence and limitations.

## Repository Setup

Status: first runnable prototype.

Current repository contains planning documents plus the first seed-catalog retrieval implementation:

- `README.md`
- `docs/project_investigation.md`
- `docs/domain_background.md`
- `docs/data_sources.md`
- `docs/data_schema.md`
- `docs/project_status.md`
- `docs/week3_meeting_prep.md`
- `docs/evaluation_plan.md`
- `eval/questions_seed.json`
- `data/processed/seed_catalog.json`
- `src/models.py`
- `src/catalog.py`
- `src/retriever.py`
- `src/answer.py`
- `scripts/ingest_gdc.py`
- `scripts/ingest_cbioportal.py`
- `scripts/build_catalog.py`
- `scripts/validate_catalog.py`
- `evaluation/retrieval_eval.py`
- `tests/test_retriever.py`
- `tests/test_answer.py`

Implementation has started, but it is still an MVP. The current answer layer is deterministic and grounded in retrieved records; it is not yet a full LLM-backed RAG flow.

## Primary RAG Document Sources

These are documentation sources that can be collected, chunked, and indexed for RAG support.

### Phase 1 Documentation

- GDC API and data model documentation
- GDC project, case, file, and annotation documentation
- cBioPortal API documentation
- cBioPortal study, sample, mutation, molecular profile, and clinical data documentation

### Phase 2 Documentation

- GEO programmatic access documentation
- NCBI Entrez / E-utilities documentation for GEO DataSets
- SRA metadata and accession documentation
- Open Targets Platform API documentation

The first RAG prototype should prioritize GDC and cBioPortal documentation. GEO, SRA, and Open Targets should remain planned extensions.

## Structured Data Sources

These are metadata sources that can become structured records in the dataset catalog.

### Phase 1 Structured Sources

- GDC/TCGA project metadata
- GDC case metadata
- GDC file metadata
- cBioPortal study metadata
- cBioPortal molecular profile metadata
- cBioPortal clinical/sample metadata where available

### Phase 2 Structured Sources

- GEO dataset or series metadata
- SRA study/sample/experiment/run metadata
- Open Targets disease-gene-target relationship data for query expansion

## Knowledge Base Design

The knowledge base will have two complementary parts.

### 1. Dataset Catalog

Structured metadata records normalized into `DatasetRecord`.

Used for:

- dataset discovery
- filtering
- ranking
- evidence-based RAG answers
- evaluation

### 2. Documentation Index

Chunked documentation from GDC, cBioPortal, and later sources.

Used for:

- explaining source-specific fields
- explaining data access details
- answering questions about platform terminology
- supporting RAG answers when metadata alone is not enough

The first prototype should mainly answer from the dataset catalog and use documentation as supporting context.

## Ingestion Strategy

### Step 1: Seed Catalog

Manually create a small seed catalog using the normalized schema.

Initial records:

- `gdc:TCGA-LUAD`
- `gdc:TCGA-LUSC`
- one or more cBioPortal lung cancer studies

Purpose:

- validate schema
- build the first retriever
- create evaluation examples
- avoid getting blocked by API complexity too early

Current implementation:

```text
scripts/ingest_gdc.py
scripts/ingest_cbioportal.py
-> data/raw/
-> scripts/build_catalog.py
-> data/processed/catalog.json
-> scripts/validate_catalog.py
```

This is a local data-engineering pipeline over curated seed metadata. It is not
yet live API ingestion, but it establishes the extract/raw/transform/processed
shape needed for later GDC and cBioPortal API loaders.

### Step 2: Source-Specific Loaders

Implement separate loaders for each source:

```text
GDC metadata       -> GDC loader       -> DatasetRecord
cBioPortal metadata -> cBioPortal loader -> DatasetRecord
GEO metadata       -> GEO loader       -> DatasetRecord
```

Retrieval and RAG should only depend on `DatasetRecord`, not source-specific API responses.

### Step 3: Documentation Collection

Collect and chunk selected official documentation pages for GDC and cBioPortal.

Store chunks separately from dataset records so the system can distinguish:

- dataset evidence
- platform/documentation explanation

## Retrieval Strategy

### First Version

Use keyword retrieval over normalized dataset records.

Searchable fields:

- dataset ID
- title
- description
- diseases
- cancer types
- primary sites
- cohort tags
- data types
- assays
- molecular profiles
- explicit and inferred genes
- explicit and inferred mutations
- limitations

Current implementation details:

- synonym expansion maps `NSCLC` to LUAD/LUSC and lung cancer terms
- exact dataset IDs such as `TCGA-BRCA` receive a ranking boost
- non-lung comparison records are penalized for explicit NSCLC/lung queries
- retrieved records retain matched terms, scores, source, and canonical dataset IDs for evaluation

### Later Versions

Add:

- vector search
- hybrid retrieval
- metadata filters
- reranking
- query expansion using disease and gene synonyms

## Evaluation Planning

Evaluation should be split into retrieval evaluation and answer evaluation.

### Retrieval Evaluation

Measure whether the system retrieves expected dataset records.

Possible metrics:

- top-k hit rate
- recall@k
- precision@k for curated questions
- whether expected source appears in retrieved results
- whether explicitly out-of-scope records are absent from the result set

### Answer Evaluation

Measure whether the final RAG answer is useful and safe.

Checks:

- names relevant dataset IDs
- explains why each dataset matches
- mentions data types
- distinguishes explicit evidence from inferred relevance
- includes limitations when evidence is weak
- avoids unsupported medical or treatment claims

Current deterministic answer checks:

- KRAS G12C answers must label match level as candidate or medium unless explicit mutation evidence exists
- answers must include limitations when variant-positive case counts are not verified
- no-match answers must say that the current seed catalog lacks a record rather than claiming no public data exists

## Example User Questions

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

## Potential Evaluation Questions

Initial evaluation questions can reuse the example questions, but each should include expected records or expected concepts.

Example evaluation record:

```json
{
  "question": "What datasets are available for KRAS G12C research in NSCLC?",
  "expected_dataset_ids": ["gdc:TCGA-LUAD", "gdc:TCGA-LUSC"],
  "expected_keywords": ["NSCLC", "KRAS", "mutation", "lung"],
  "expected_behavior": [
    "returns candidate datasets",
    "labels KRAS G12C evidence as not explicitly verified unless metadata supports it",
    "mentions limitations"
  ]
}
```

## Architecture Alignment

Planned flow:

```text
source APIs / seed metadata
-> source-specific ingestion
-> normalized DatasetRecord catalog
-> retrieval index
-> retrieved dataset context
-> evidence-aware answer with evidence and limitations
-> evaluation
-> UI
```

Near-term production flow:

```text
retrieved DatasetRecord context
-> grounded prompt
-> LLM answer
-> answer checks / LLM-as-judge
-> logged query and feedback
```

Key architecture principle:

```text
source-specific ingestion can change
DatasetRecord should stay stable
retrieval and RAG should depend on DatasetRecord
```

## Week 4 Deliverables

Target deliverables:

- Repository initialized with planning docs
- Project skeleton created
- `DatasetRecord` model implemented
- small seed catalog created
- 5-10 dataset discovery evaluation questions refined against the seed catalog
- initial keyword retrieval prototype working
- first RAG prompt drafted
- clear distinction between dataset metadata context and documentation context

## Current Gaps Before Week 4

Needs implementation:

- project skeleton
- `src/models.py`
- seed catalog JSON
- retrieval code
- evaluation file
- RAG prompt and pipeline

Needs refinement:

- exact cBioPortal study IDs for the first seed catalog
- exact GDC fields to fetch during API ingestion
- final retrieval metrics for the first evaluation script
