"""Quality checks for the processed DatasetRecord catalog."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from src.catalog import load_catalog


DEFAULT_CATALOG_PATH = Path("data/processed/catalog.json")


def validate_catalog(path: Path) -> list[str]:
    records = load_catalog(path)
    errors: list[str] = []
    dataset_ids = [record.dataset_id for record in records]

    duplicates = [item for item, count in Counter(dataset_ids).items() if count > 1]
    if duplicates:
        errors.append(f"Duplicate dataset_id values: {', '.join(sorted(duplicates))}")

    required = [
        "dataset_id",
        "canonical_dataset_id",
        "source",
        "source_record_id",
        "source_url",
        "title",
        "description",
    ]
    for record in records:
        for field in required:
            if not getattr(record, field):
                errors.append(f"{record.dataset_id}: missing required field {field}")
        if not record.evidence_items:
            errors.append(f"{record.dataset_id}: missing evidence_items")
        if not record.limitations:
            errors.append(f"{record.dataset_id}: missing limitations")
        if not record.primary_sites:
            errors.append(f"{record.dataset_id}: missing primary_sites")

    expected_ids = {
        "gdc:TCGA-LUAD",
        "gdc:TCGA-LUSC",
        "gdc:TCGA-BRCA",
        "cbioportal:luad_tcga_pan_can_atlas_2018",
        "cbioportal:lusc_tcga_pan_can_atlas_2018",
        "cbioportal:brca_tcga_pan_can_atlas_2018",
    }
    missing_ids = expected_ids - set(dataset_ids)
    if missing_ids:
        errors.append(f"Missing expected seed records: {', '.join(sorted(missing_ids))}")

    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_PATH)
    args = parser.parse_args()

    errors = validate_catalog(args.catalog)
    if errors:
        print("Catalog validation failed")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    records = load_catalog(args.catalog)
    print(f"Catalog validation passed: {len(records)} records in {args.catalog}")


if __name__ == "__main__":
    main()
