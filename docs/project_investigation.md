# Initial Project Investigation

## Mission

Help researchers discover public biomedical datasets relevant to diseases, genes, biomarkers, mutations, assays, and research questions.

This project should behave like a research data navigation assistant. It should answer questions such as:

- What public datasets exist for NSCLC?
- Which datasets contain EGFR-mutant patients?
- Which datasets contain RNA-seq data?
- What datasets are available for KRAS G12C research?
- Compare TCGA-LUAD and TCGA-LUSC datasets.

The system should not be a medical diagnosis assistant. Its job is to help users find and understand public research datasets.

## Zoomcamp Fit

The project maps well to the LLM Zoomcamp requirements:

- Knowledge base: biomedical dataset documentation and dataset metadata
- Retrieval: search over dataset records, metadata fields, and documentation chunks
- RAG: generate grounded answers using retrieved records and source documentation
- Evaluation: compare retrieval and answer quality on curated discovery questions
- UI: provide a simple interface for dataset search and question answering

## Initial Data Source Assessment

### GDC / TCGA

Recommended as a first-phase source.

Strengths:

- Official API is designed for programmatic search and retrieval.
- Metadata is relatively structured.
- TCGA projects are well-known and useful for cancer dataset discovery.
- Good fit for questions about cancer type, project, cases, files, data category, and experimental strategy.

Likely useful entities:

- Projects
- Cases
- Files
- Diagnoses
- Samples
- Data categories and data types

Example datasets:

- TCGA-LUAD
- TCGA-LUSC
- TCGA-BRCA

Risks:

- Some useful details may live at file or case level rather than project level.
- The first version should avoid downloading large genomic files.

### cBioPortal

Recommended as a first-phase source.

Strengths:

- Strong cancer genomics study catalog.
- Useful for mutation, clinical, sample, and molecular profile discovery.
- More directly aligned with questions like EGFR-mutant or KRAS-mutant cohorts.

Likely useful entities:

- Studies
- Cancer types
- Samples
- Patients
- Molecular profiles
- Mutations
- Clinical attributes

Risks:

- Gene and mutation availability may vary by study.
- Some endpoints may require study-specific handling.

### GEO

Recommended for second phase.

Strengths:

- Broad public dataset coverage.
- Important for expression datasets and disease-specific studies outside TCGA.

Risks:

- Metadata is less normalized.
- Disease, platform, sample, and assay labels can be inconsistent.
- Initial ingestion may require more cleaning and manual normalization.

### SRA

Recommended for later expansion, not the initial catalog.

Strengths:

- Rich sequencing-run metadata.
- Useful when users need run-level or raw sequencing discovery.

Risks:

- SRA is more granular than the first project needs.
- Study, sample, experiment, and run levels can complicate the schema.

### Open Targets

Recommended as a supporting knowledge source, not a primary dataset catalog.

Strengths:

- Useful for disease-gene-target relationships.
- Can support query expansion, such as mapping EGFR to lung cancer or KRAS G12C to relevant disease areas.

Risks:

- It is not primarily a dataset catalog.
- Adding it too early may distract from dataset discovery.

## MVP Recommendation

The first version should focus on public cancer dataset discovery using GDC/TCGA and cBioPortal.

Suggested first scope:

- Disease area: lung cancer
- Project examples: TCGA-LUAD, TCGA-LUSC
- Related query concepts: NSCLC, LUAD, LUSC, EGFR, KRAS, KRAS G12C, RNA-seq
- Data sources: GDC/TCGA and cBioPortal
- Search type: metadata keyword search first
- RAG type: answer from retrieved dataset records plus short source documentation snippets

This keeps the first version realistic while leaving room to add GEO, SRA,
deeper metadata, and UI polish later.

## Non-Hardcoded Architecture

Avoid building one-off functions such as:

```python
find_nsclc_datasets()
find_egfr_datasets()
```

Prefer general interfaces such as:

```python
search_datasets(query, filters=None, top_k=10)
```

Example filters:

```python
{
    "disease": "NSCLC",
    "gene": "EGFR",
    "mutation": "L858R",
    "data_type": "RNA-Seq",
    "source": ["GDC", "cBioPortal"]
}
```

This allows the retrieval implementation to evolve from keyword search to vector search, hybrid search, or reranking without changing the rest of the application.

## Proposed Dataset Record Schema

All source-specific metadata should be normalized into one shared record shape.

Initial fields:

```text
dataset_id
source
title
description
disease
cancer_type
primary_site
genes
mutations
data_types
assays
sample_count
case_count
organism
platform
access_level
url
source_metadata
```

Notes:

- `source_metadata` should preserve useful source-specific fields without forcing them into the shared schema too early.
- `genes`, `mutations`, `data_types`, and `assays` should be lists.
- `sample_count` and `case_count` should be optional because not every source exposes them consistently.

## Proposed Project Structure

```text
biomedical-dataset-discovery/
  README.md
  docs/
    project_investigation.md
  data/
    raw/
    processed/
  src/
    config.py
    models.py
    ingest/
      gdc.py
      cbioportal.py
      geo.py
    retrieval/
      base.py
      keyword.py
    rag/
      prompt.py
      pipeline.py
    evaluation/
      questions.json
      evaluate.py
  app/
    streamlit_app.py
```

The first implementation does not need every file immediately. The structure is a guide for keeping responsibilities separate.

## Early Evaluation Questions

Initial evaluation should test dataset discovery, not generic biology knowledge.

Candidate questions:

1. What public datasets exist for NSCLC?
2. Which public datasets are available for lung adenocarcinoma?
3. Which datasets are available for lung squamous cell carcinoma?
4. Compare TCGA-LUAD and TCGA-LUSC.
5. Which datasets contain RNA-seq data for lung cancer?
6. Which datasets can support EGFR mutation research?
7. Which datasets can support KRAS mutation research?
8. What datasets are relevant for KRAS G12C research?
9. Which datasets include clinical metadata and molecular data?
10. Which cBioPortal studies are relevant to NSCLC?

For each question, the evaluation file should eventually include:

```text
question
expected_sources
expected_dataset_ids
expected_keywords
difficulty
notes
```

## Initial Risks

- Dataset metadata can be inconsistent across sources.
- Gene and mutation availability may not be obvious at project level.
- GEO and SRA can expand the project scope too quickly.
- RAG answers may sound confident even when retrieval is weak.
- The assistant must cite or name the datasets it used.

## Next Steps

1. Create the initial project skeleton.
2. Define the `DatasetRecord` model.
3. Create a small hand-curated seed catalog for TCGA-LUAD, TCGA-LUSC, and a few cBioPortal studies.
4. Build a simple keyword retriever over the normalized records.
5. Add the first 10 evaluation questions.
6. Add a minimal RAG pipeline that answers only from retrieved records.
7. Expand ingestion from official APIs after the retrieval prototype is working.
