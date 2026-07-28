"""Build the processed DatasetRecord catalog from raw source extracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.models import DatasetRecord


DEFAULT_GDC_RAW_PATH = Path("data/raw/gdc/projects_seed.json")
DEFAULT_CBIOPORTAL_RAW_PATH = Path("data/raw/cbioportal/studies_seed.json")
DEFAULT_OUTPUT_PATH = Path("data/processed/catalog.json")


def read_raw_records(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        payload = json.load(file)
    return list(payload.get("records", []))


def _has_category(record: dict[str, Any], needle: str) -> bool:
    values = [
        *record.get("data_categories", []),
        *record.get("experimental_strategies", []),
        *record.get("molecular_profiles", []),
    ]
    return any(needle.lower() in value.lower() for value in values)


def _canonical_from_cbioportal_study(record: dict[str, Any]) -> str:
    current = record.get("canonical_dataset_id", "")
    if current and not str(current).startswith("cbioportal:"):
        return str(current)

    study_id = str(record["study_id"])
    prefix = study_id.split("_", 1)[0]
    if prefix:
        return f"TCGA-{prefix.upper()}"
    return str(current or study_id)


def transform_gdc_project(record: dict[str, Any]) -> dict[str, Any]:
    project_id = record["project_id"]
    data_categories = record.get("data_categories", [])
    assays = record.get("experimental_strategies", [])
    data_types = []
    if _has_category(record, "Clinical"):
        data_types.append("clinical")
    if _has_category(record, "Transcriptome") or _has_category(record, "RNA"):
        data_types.insert(0, "RNA-seq")
    if _has_category(record, "Nucleotide") or _has_category(record, "WXS"):
        data_types.append("mutation")
    if _has_category(record, "Copy Number"):
        data_types.append("copy number")

    return {
        "schema_version": 1,
        "dataset_id": f"gdc:{project_id}",
        "canonical_dataset_id": project_id,
        "source": "GDC",
        "source_record_id": project_id,
        "source_url": f"https://portal.gdc.cancer.gov/projects/{project_id}",
        "title": record["name"],
        "description": (
            f"GDC project record for {record['name']}, included in the normalized dataset catalog."
        ),
        "diseases": record.get("disease_terms", []),
        "cancer_types": record.get("cancer_types", []),
        "primary_sites": [record.get("primary_site", "")],
        "organisms": ["Homo sapiens"],
        "cohort_tags": record.get("cohort_tags", []),
        "data_types": data_types,
        "data_categories": data_categories,
        "assays": assays,
        "molecular_profiles": [],
        "has_clinical": "clinical" in data_types,
        "has_expression": "RNA-seq" in data_types,
        "has_mutation": "mutation" in data_types,
        "has_copy_number": "copy number" in data_types,
        "has_methylation": False,
        "clinical_attributes": record.get("clinical_attributes", []),
        "explicit_genes": [],
        "inferred_genes": record.get("inferred_genes", []),
        "explicit_mutations": [],
        "inferred_mutations": record.get("inferred_mutations", []),
        "biomarker_notes": record.get("biomarker_notes", ""),
        "case_count": record.get("case_count"),
        "sample_count": None,
        "access_level": "mixed",
        "study_design": "TCGA cancer genomics project",
        "publication_ids": [],
        "external_ids": [project_id],
        "evidence_level": "pipeline_seed",
        "evidence_items": [
            {
                "field": "dataset_id",
                "value": project_id,
                "source": "GDC raw project extract",
                "supports": "Official project identity for dataset discovery.",
                "confidence": "high",
            },
            {
                "field": "data_categories",
                "value": "; ".join(data_categories),
                "source": "GDC raw project extract",
                "supports": "Dataset may support expression, mutation, clinical, and copy-number oriented discovery.",
                "confidence": "medium",
            },
        ],
        "limitations": record.get("limitations", []),
        "curation_status": "pipeline_seed",
        "last_verified": "2026-07-08",
        "source_metadata": {"gdc": record},
    }


def transform_cbioportal_study(record: dict[str, Any]) -> dict[str, Any]:
    study_id = record["study_id"]
    canonical_dataset_id = _canonical_from_cbioportal_study(record)
    molecular_profiles = record.get("molecular_profiles", [])
    data_types = record.get("data_types") or [
        "mutation",
        "mRNA expression",
        "clinical",
        "copy number",
    ]
    return {
        "schema_version": 1,
        "dataset_id": f"cbioportal:{study_id}",
        "canonical_dataset_id": canonical_dataset_id,
        "source": "cBioPortal",
        "source_record_id": study_id,
        "source_url": f"https://www.cbioportal.org/study/summary?id={study_id}",
        "title": record["name"],
        "description": (
            f"cBioPortal study view for {record['name']}, included in the normalized dataset catalog."
        ),
        "diseases": record.get("disease_terms", []),
        "cancer_types": record.get("cancer_types", []),
        "primary_sites": [record.get("primary_site", "")],
        "organisms": ["Homo sapiens"],
        "cohort_tags": record.get("cohort_tags", []),
        "data_types": data_types,
        "data_categories": ["Cancer Genomics Study"],
        "assays": [],
        "molecular_profiles": molecular_profiles,
        "has_clinical": "clinical" in [item.lower() for item in data_types],
        "has_expression": _has_category(record, "expression"),
        "has_mutation": _has_category(record, "mutation"),
        "has_copy_number": _has_category(record, "copy number"),
        "has_methylation": _has_category(record, "methylation"),
        "clinical_attributes": record.get("clinical_attributes", []),
        "explicit_genes": [],
        "inferred_genes": record.get("inferred_genes", []),
        "explicit_mutations": [],
        "inferred_mutations": record.get("inferred_mutations", []),
        "biomarker_notes": record.get("biomarker_notes", ""),
        "case_count": record.get("case_count"),
        "sample_count": record.get("sample_count"),
        "access_level": "open",
        "study_design": "cBioPortal cancer genomics study",
        "publication_ids": record.get("publication_ids", []),
        "external_ids": [study_id, canonical_dataset_id],
        "evidence_level": record.get("evidence_level", "pipeline_seed"),
        "evidence_items": [
            {
                "field": "molecular_profiles",
                "value": "; ".join(molecular_profiles),
                "source": "cBioPortal raw study extract",
                "supports": "Study is suitable for follow-up molecular profile and gene-oriented inspection.",
                "confidence": "medium",
            },
            {
                "field": "canonical_dataset_id",
                "value": canonical_dataset_id,
                "source": "cBioPortal raw study extract",
                "supports": "Connects this cBioPortal source view to the canonical TCGA dataset.",
                "confidence": "medium",
            },
        ],
        "limitations": record.get("limitations", []),
        "curation_status": "pipeline_seed",
        "last_verified": "2026-07-16",
        "source_metadata": {"cbioportal": record},
    }


def build_catalog(gdc_raw_path: Path, cbioportal_raw_path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    records.extend(transform_gdc_project(record) for record in read_raw_records(gdc_raw_path))
    records.extend(
        transform_cbioportal_study(record)
        for record in read_raw_records(cbioportal_raw_path)
    )

    for record in records:
        DatasetRecord.from_dict(record)

    return sorted(records, key=lambda item: item["dataset_id"])


def write_catalog(records: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=2)
        file.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gdc-raw", type=Path, default=DEFAULT_GDC_RAW_PATH)
    parser.add_argument("--cbioportal-raw", type=Path, default=DEFAULT_CBIOPORTAL_RAW_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args()

    records = build_catalog(args.gdc_raw, args.cbioportal_raw)
    write_catalog(records, args.output)
    print(f"Wrote {len(records)} normalized DatasetRecord objects to {args.output}")


if __name__ == "__main__":
    main()
