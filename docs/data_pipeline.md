# Data Pipeline

This project now has a small local data pipeline for turning source metadata into
the normalized `DatasetRecord` catalog used by retrieval and answers.

The pipeline is intentionally local-first. It does not require a cloud server,
database, orchestrator, or large genomic file downloads.

## Pipeline Goal

The goal is to replace a purely hand-written catalog with a repeatable data
engineering flow:

```text
source metadata
-> raw JSON extracts
-> normalized DatasetRecord objects
-> processed catalog
-> quality checks
-> retrieval evaluation
-> evidence-aware answers
```

This connects the LLM/RAG project to data engineering concepts without
overbuilding too early.

## Current Sources

The pipeline supports curated seed extracts plus live GDC and cBioPortal API
modes.

By default, it uses curated seed extracts for:

- GDC/TCGA project metadata
- cBioPortal study metadata

Current records:

- `TCGA-LUAD`
- `TCGA-LUSC`
- `TCGA-BRCA` as a non-lung comparison dataset
- cBioPortal study views for the same canonical datasets

The GDC extract can also be run in live mode. The small default live mode fetches
the same core three projects used by the seed catalog:

```bash
uv run python -m scripts.ingest_gdc --live
```

For a broader real-data pass, use the TCGA default panel:

```bash
uv run python -m scripts.ingest_gdc --live --tcga-defaults
```

This writes `data/raw/gdc/projects_live.json` by default instead of overwriting
the reproducible seed extract.

For the expanded TCGA pass, discover all current TCGA projects from GDC:

```bash
uv run python -m scripts.ingest_gdc --live --all-tcga
```

For a broader project-level pass, fetch basic metadata for all public GDC
projects in one bulk API request:

```bash
uv run python -m scripts.ingest_gdc --live --all-projects --limit 120
```

This wider mode is useful for reliability testing because it introduces
non-TCGA projects such as APOLLO, CPTAC, CMI, and other GDC programs. It is
still project-level metadata; it does not verify patient-level mutations or
download genomic files.

cBioPortal also supports live study metadata and molecular-profile ingestion,
while the default seed mode remains available for reproducible local runs:

```bash
uv run python -m scripts.ingest_cbioportal --live --tcga-defaults
```

This writes `data/raw/cbioportal/studies_live.json` by default instead of
overwriting the reproducible seed extract.

For the expanded TCGA pass, discover all current cBioPortal TCGA PanCancer Atlas
studies:

```bash
uv run python -m scripts.ingest_cbioportal --live --all-tcga
```

## Files

Pipeline scripts:

- `scripts/ingest_gdc.py`: writes the first raw GDC seed extract or live GDC API extract
- `scripts/ingest_cbioportal.py`: writes the first raw cBioPortal seed extract or live cBioPortal API extract
- `scripts/build_catalog.py`: transforms raw extracts into `DatasetRecord` JSON
- `scripts/validate_catalog.py`: runs catalog quality checks

Pipeline data:

- `data/raw/gdc/projects_seed.json`: raw GDC seed extract
- `data/raw/gdc/projects_live.json`: optional live GDC TCGA project extract
- `data/raw/gdc/projects_all_tcga_live.json`: optional expanded live GDC TCGA project extract
- `data/raw/gdc/projects_all_live.json`: optional broad live GDC project extract
- `data/raw/cbioportal/studies_seed.json`: raw cBioPortal seed extract
- `data/raw/cbioportal/studies_live.json`: optional live cBioPortal TCGA study extract
- `data/raw/cbioportal/studies_all_tcga_live.json`: optional expanded live cBioPortal TCGA study extract
- `data/processed/catalog.json`: pipeline-built normalized catalog
- `data/processed/catalog_live_gdc.json`: optional catalog built from live GDC plus seed cBioPortal records
- `data/processed/catalog_live.json`: optional catalog built from live GDC plus live cBioPortal records
- `data/processed/catalog_expanded_live.json`: optional expanded catalog built from all discovered TCGA metadata
- `data/processed/catalog_broad_live.json`: optional broad catalog built from GDC all-project metadata plus cBioPortal TCGA metadata
- `data/processed/seed_catalog.json`: original hand-curated catalog fallback

## Commands

Run extraction:

```bash
uv run python -m scripts.ingest_gdc
uv run python -m scripts.ingest_cbioportal
```

Build the processed catalog:

```bash
uv run python -m scripts.build_catalog
```

Validate the processed catalog:

```bash
uv run python -m scripts.validate_catalog
```

Run retrieval evaluation against the pipeline-built catalog:

```bash
uv run python -m evaluation.retrieval_eval --catalog data/processed/catalog.json
```

Build and evaluate the broader live GDC catalog:

```bash
make live-gdc-catalog
```

This command keeps cBioPortal on seed data, but expands the GDC side to the
configured TCGA project panel.

Build and evaluate the broader live GDC + cBioPortal catalog:

```bash
make live-catalog
```

This command pulls live GDC project metadata and live cBioPortal study/molecular
profile metadata, then normalizes both into one catalog.

Build and evaluate the expanded all-TCGA metadata catalog:

```bash
make expanded-live-catalog
```

This command discovers all current GDC TCGA projects and all cBioPortal TCGA
PanCancer Atlas studies, then evaluates retrieval with `eval/questions_live.json`.

Build and evaluate the broader metadata catalog:

```bash
make broad-live-catalog
```

This command uses GDC all-project basic metadata and cBioPortal TCGA PanCancer
Atlas metadata. The default `GDC_PROJECT_LIMIT` is `120`, which currently covers
all public GDC projects returned by the API; lower it for quicker smoke runs.

Run an evidence-aware answer against the pipeline-built catalog:

```bash
uv run python -m src.answer "What datasets are available for KRAS G12C research in NSCLC?" --catalog data/processed/catalog.json
```

## Data Engineering Mapping

### Extract

`scripts/ingest_gdc.py` and `scripts/ingest_cbioportal.py` create source-specific
raw extracts.

`scripts/ingest_gdc.py --live` can call the public GDC API for project metadata.
`--tcga-defaults` expands that live pull to a broader panel of TCGA cancer
projects. The downstream transform and retrieval code do not need to change
because the raw output shape stays stable.

`--all-projects` uses the GDC projects list endpoint to fetch broad
project-level metadata in bulk. This is intentionally less detailed than the
per-project TCGA metadata path, but it is much faster and better for testing
retrieval behavior under a wider catalog.

`scripts/ingest_cbioportal.py --live` can call the public cBioPortal API for
study metadata and molecular profiles. This adds study-level sample counts,
publication IDs, cancer type metadata, and molecular profile availability.

### Raw Layer

Raw source metadata is stored under `data/raw/`.

This layer preserves source-specific concepts such as:

- GDC project IDs
- GDC data categories
- GDC experimental strategies
- cBioPortal study IDs
- cBioPortal molecular profiles

### Transform

`scripts/build_catalog.py` maps source-specific fields into the shared
`DatasetRecord` schema.

Examples:

- GDC `project_id` becomes `dataset_id = gdc:TCGA-LUAD`
- cBioPortal `study_id` becomes `dataset_id = cbioportal:...`
- GDC data categories become user-facing `data_types`
- cBioPortal molecular profiles become both `molecular_profiles` and boolean
  availability flags
- source-specific raw metadata is preserved under `source_metadata`

### Processed Layer

The processed catalog lives at `data/processed/catalog.json`.

This is the catalog that retrieval, answer generation, and evaluation can use.

### Quality Checks

`scripts/validate_catalog.py` checks:

- no duplicate `dataset_id`
- required identity fields are present
- records have evidence items
- records have limitations
- expected seed records are present

These checks are basic, but they create the right habit: do not send catalog
data to RAG before validating it.

### Evaluation

`evaluation/retrieval_eval.py` can evaluate either the original hand-curated
catalog or the pipeline-built catalog.

The pipeline is only useful if its output still supports retrieval behavior:

- expected datasets appear
- expected sources appear
- out-of-scope records stay absent for scoped queries

## Current Limitations

- The default catalog is still small; optional live catalogs increase GDC and
  cBioPortal metadata coverage.
- Case counts and sample counts are not verified.
- KRAS G12C-positive counts are not confirmed.
- The pipeline stores metadata only; it does not download raw genomic files.

## Next Pipeline Upgrades

1. Review retrieval behavior on the expanded full live catalog.
2. Extend live GDC extraction from project metadata to file metadata.
3. Add richer cBioPortal clinical/sample-list extraction.
3. Store pipeline run metadata, such as run ID and extracted timestamp.
4. Add richer quality checks for disease/source consistency.
5. Optionally write a DuckDB copy of the processed catalog for SQL exploration.
6. Add a simple Makefile or task runner after the commands stabilize.
