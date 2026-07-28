"""Create the first raw cBioPortal study metadata extract."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


DEFAULT_OUTPUT_PATH = Path("data/raw/cbioportal/studies_seed.json")
DEFAULT_LIVE_OUTPUT_PATH = Path("data/raw/cbioportal/studies_live.json")
CBIOPORTAL_API_BASE_URL = "https://www.cbioportal.org/api"
DEFAULT_STUDY_IDS = [
    "luad_tcga_pan_can_atlas_2018",
    "lusc_tcga_pan_can_atlas_2018",
    "brca_tcga_pan_can_atlas_2018",
]
DEFAULT_TCGA_STUDY_IDS = [
    "luad_tcga_pan_can_atlas_2018",
    "lusc_tcga_pan_can_atlas_2018",
    "brca_tcga_pan_can_atlas_2018",
    "coadread_tcga_pan_can_atlas_2018",
    "gbm_tcga_pan_can_atlas_2018",
    "lgg_tcga_pan_can_atlas_2018",
    "ov_tcga_pan_can_atlas_2018",
    "prad_tcga_pan_can_atlas_2018",
    "skcm_tcga_pan_can_atlas_2018",
    "kirc_tcga_pan_can_atlas_2018",
    "hnsc_tcga_pan_can_atlas_2018",
    "stad_tcga_pan_can_atlas_2018",
    "lihc_tcga_pan_can_atlas_2018",
    "blca_tcga_pan_can_atlas_2018",
    "ucec_tcga_pan_can_atlas_2018",
    "cesc_tcga_pan_can_atlas_2018",
    "thca_tcga_pan_can_atlas_2018",
]
CANONICAL_ID_BY_STUDY_PREFIX = {
    "luad": "TCGA-LUAD",
    "lusc": "TCGA-LUSC",
    "brca": "TCGA-BRCA",
    "coadread": "TCGA-COADREAD",
    "gbm": "TCGA-GBM",
    "lgg": "TCGA-LGG",
    "ov": "TCGA-OV",
    "prad": "TCGA-PRAD",
    "skcm": "TCGA-SKCM",
    "kirc": "TCGA-KIRC",
    "hnsc": "TCGA-HNSC",
    "stad": "TCGA-STAD",
    "lihc": "TCGA-LIHC",
    "blca": "TCGA-BLCA",
    "ucec": "TCGA-UCEC",
    "cesc": "TCGA-CESC",
    "thca": "TCGA-THCA",
}
PRIMARY_SITE_BY_CANCER_TYPE_ID = {
    "luad": "lung",
    "lusc": "lung",
    "brca": "breast",
    "coadread": "colon/rectum",
    "gbm": "brain",
    "lgg": "brain",
    "ov": "ovary",
    "prad": "prostate",
    "skcm": "skin",
    "kirc": "kidney",
    "hnsc": "head and neck",
    "stad": "stomach",
    "lihc": "liver",
    "blca": "bladder",
    "ucec": "uterus",
    "cesc": "cervix",
    "thca": "thyroid",
}

CBIOPORTAL_STUDIES = [
    {
        "study_id": "luad_tcga_pan_can_atlas_2018",
        "canonical_dataset_id": "TCGA-LUAD",
        "name": "Lung Adenocarcinoma TCGA PanCancer Atlas",
        "primary_site": "lung",
        "disease_terms": ["non-small cell lung cancer", "lung cancer"],
        "cancer_types": ["lung adenocarcinoma", "LUAD"],
        "cohort_tags": ["NSCLC", "TCGA", "PanCancer Atlas", "cBioPortal"],
        "molecular_profiles": ["mutations", "mRNA expression", "copy number alterations"],
        "clinical_attributes": ["clinical attributes", "sample attributes"],
        "inferred_genes": ["EGFR", "KRAS"],
        "inferred_mutations": ["KRAS G12C"],
        "biomarker_notes": (
            "cBioPortal is the better source view for follow-up EGFR or KRAS alteration "
            "inspection, but this seed extract does not claim explicit KRAS G12C-positive sample counts."
        ),
        "limitations": [
            "Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.",
            "This record represents a cBioPortal study view, not the official GDC project file catalog.",
        ],
    },
    {
        "study_id": "lusc_tcga_pan_can_atlas_2018",
        "canonical_dataset_id": "TCGA-LUSC",
        "name": "Lung Squamous Cell Carcinoma TCGA PanCancer Atlas",
        "primary_site": "lung",
        "disease_terms": ["non-small cell lung cancer", "lung cancer"],
        "cancer_types": ["lung squamous cell carcinoma", "LUSC"],
        "cohort_tags": ["NSCLC", "TCGA", "PanCancer Atlas", "cBioPortal"],
        "molecular_profiles": ["mutations", "mRNA expression", "copy number alterations"],
        "clinical_attributes": ["clinical attributes", "sample attributes"],
        "inferred_genes": ["EGFR", "KRAS"],
        "inferred_mutations": ["KRAS G12C"],
        "biomarker_notes": (
            "cBioPortal is useful for follow-up molecular profile inspection, but KRAS G12C "
            "relevance should remain candidate-level until variant-positive samples are verified."
        ),
        "limitations": [
            "Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.",
            "This record represents a cBioPortal study view, not the official GDC project file catalog.",
        ],
    },
    {
        "study_id": "brca_tcga_pan_can_atlas_2018",
        "canonical_dataset_id": "TCGA-BRCA",
        "name": "Breast Invasive Carcinoma TCGA PanCancer Atlas",
        "primary_site": "breast",
        "disease_terms": ["breast cancer"],
        "cancer_types": ["breast invasive carcinoma", "BRCA"],
        "cohort_tags": ["TCGA", "PanCancer Atlas", "cBioPortal", "non-lung comparison"],
        "molecular_profiles": ["mutations", "mRNA expression", "copy number alterations"],
        "clinical_attributes": ["clinical attributes", "sample attributes"],
        "inferred_genes": [],
        "inferred_mutations": [],
        "biomarker_notes": "Included to test source-specific and out-of-scope retrieval behavior.",
        "limitations": [
            "This is not a lung cancer or NSCLC dataset and should not be treated as relevant to NSCLC questions."
        ],
    },
]


def _seed_by_study_id() -> dict[str, dict[str, Any]]:
    return {record["study_id"]: record for record in CBIOPORTAL_STUDIES}


def _study_prefix(study_id: str) -> str:
    return study_id.split("_", 1)[0]


def _profile_labels(profiles: list[dict[str, Any]]) -> list[str]:
    labels = []
    for profile in profiles:
        for field in ["molecularAlterationType", "genericAssayType", "name"]:
            label = profile.get(field)
            if label:
                labels.append(str(label).lower().replace("_", " "))
    return sorted(set(labels))


def _data_types_from_profiles(profiles: list[dict[str, Any]]) -> list[str]:
    profile_text = " ".join(_profile_labels(profiles)).lower()
    data_types = []
    if "mutation" in profile_text:
        data_types.append("mutation")
    if "mrna" in profile_text or "expression" in profile_text:
        data_types.append("mRNA expression")
    if "copy number" in profile_text or "cna" in profile_text:
        data_types.append("copy number")
    if "methylation" in profile_text:
        data_types.append("methylation")
    data_types.append("clinical")
    return data_types


def normalize_cbioportal_study_response(
    study_id: str,
    study_response: dict[str, Any],
    molecular_profiles: list[dict[str, Any]],
    seed_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    seed_record = seed_record or {}
    prefix = _study_prefix(study_id)
    cancer_type = study_response.get("cancerType", {})
    if not isinstance(cancer_type, dict):
        cancer_type = {}

    cancer_type_name = str(
        cancer_type.get("name")
        or study_response.get("name")
        or seed_record.get("name")
        or study_id
    )
    short_name = str(cancer_type.get("shortName") or "").strip()
    cancer_types = seed_record.get("cancer_types") or [
        item for item in [cancer_type_name, short_name] if item
    ]
    canonical_dataset_id = (
        seed_record.get("canonical_dataset_id")
        or CANONICAL_ID_BY_STUDY_PREFIX.get(prefix)
        or (f"TCGA-{short_name.upper()}" if short_name else "")
        or f"cbioportal:{study_id}"
    )

    return {
        "study_id": str(study_response.get("studyId") or study_id),
        "canonical_dataset_id": canonical_dataset_id,
        "name": str(study_response.get("name") or seed_record.get("name") or study_id),
        "primary_site": seed_record.get("primary_site")
        or PRIMARY_SITE_BY_CANCER_TYPE_ID.get(prefix, cancer_type_name),
        "disease_terms": seed_record.get("disease_terms") or [cancer_type_name],
        "cancer_types": cancer_types,
        "cohort_tags": seed_record.get("cohort_tags")
        or ["TCGA", "PanCancer Atlas", "cBioPortal"],
        "molecular_profiles": _profile_labels(molecular_profiles),
        "data_types": _data_types_from_profiles(molecular_profiles),
        "clinical_attributes": seed_record.get("clinical_attributes")
        or ["clinical attributes", "sample attributes"],
        "inferred_genes": seed_record.get("inferred_genes", []),
        "inferred_mutations": seed_record.get("inferred_mutations", []),
        "biomarker_notes": seed_record.get("biomarker_notes", ""),
        "limitations": seed_record.get("limitations")
        or [
            "Live cBioPortal study metadata does not verify gene-specific or variant-positive sample counts.",
            "This record represents a cBioPortal study-level view, not patient-level alteration analysis.",
        ],
        "sample_count": study_response.get("allSampleCount"),
        "case_count": study_response.get("allSampleCount"),
        "publication_ids": [
            item.strip()
            for item in str(study_response.get("pmid", "")).split(",")
            if item.strip()
        ],
        "citation": study_response.get("citation", ""),
        "api_response": {
            "study": study_response,
            "molecular_profiles": molecular_profiles,
        },
    }


def _fetch_json(url: str, timeout: int = 60, attempts: int = 3) -> Any:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(url, timeout=timeout) as response:  # nosec B310 - public metadata API
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError) as error:
            last_error = error
            if attempt == attempts:
                break
            time.sleep(float(attempt))
    assert last_error is not None
    raise last_error


def fetch_cbioportal_study(study_id: str, timeout: int = 60) -> dict[str, Any]:
    url = f"{CBIOPORTAL_API_BASE_URL}/studies/{study_id}?projection=SUMMARY"
    return dict(_fetch_json(url, timeout=timeout))


def fetch_cbioportal_molecular_profiles(
    study_id: str,
    timeout: int = 60,
) -> list[dict[str, Any]]:
    url = (
        f"{CBIOPORTAL_API_BASE_URL}/studies/{study_id}"
        "/molecular-profiles?projection=SUMMARY"
    )
    return list(_fetch_json(url, timeout=timeout))


def fetch_tcga_pan_can_atlas_study_ids(timeout: int = 60) -> list[str]:
    url = f"{CBIOPORTAL_API_BASE_URL}/studies?projection=SUMMARY&pageSize=100000"
    studies = _fetch_json(url, timeout=timeout)
    return sorted(
        study["studyId"]
        for study in studies
        if study.get("studyId", "").endswith("_tcga_pan_can_atlas_2018")
    )


def fetch_live_studies(study_ids: list[str]) -> list[dict[str, Any]]:
    seed_records = _seed_by_study_id()
    records: list[dict[str, Any]] = []
    for study_id in study_ids:
        study_response = fetch_cbioportal_study(study_id)
        molecular_profiles = fetch_cbioportal_molecular_profiles(study_id)
        records.append(
            normalize_cbioportal_study_response(
                study_id,
                study_response,
                molecular_profiles,
                seed_records.get(study_id),
            )
        )
    return records


def select_live_study_ids(
    requested_study_ids: list[str] | None,
    use_tcga_defaults: bool = False,
    use_all_tcga: bool = False,
) -> list[str]:
    if requested_study_ids:
        return requested_study_ids
    if use_all_tcga:
        return fetch_tcga_pan_can_atlas_study_ids()
    if use_tcga_defaults:
        return DEFAULT_TCGA_STUDY_IDS
    return DEFAULT_STUDY_IDS


def select_output_path(requested_output: Path, live: bool = False) -> Path:
    if live and requested_output == DEFAULT_OUTPUT_PATH:
        return DEFAULT_LIVE_OUTPUT_PATH
    return requested_output


def write_raw_extract(
    output_path: Path,
    records: list[dict[str, Any]] | None = None,
    extract_type: str = "curated_seed_studies",
) -> None:
    records = records or CBIOPORTAL_STUDIES
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "cBioPortal",
        "extract_type": extract_type,
        "extracted_at": "2026-07-16",
        "records": records,
    }
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)
        file.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Fetch study metadata from the public cBioPortal API instead of writing the curated seed extract.",
    )
    parser.add_argument(
        "--study-id",
        action="append",
        dest="study_ids",
        help="cBioPortal study ID to fetch in live mode. Can be repeated.",
    )
    parser.add_argument(
        "--tcga-defaults",
        action="store_true",
        help=(
            "In live mode, fetch a broader default panel of TCGA PanCancer studies "
            f"({len(DEFAULT_TCGA_STUDY_IDS)} studies)."
        ),
    )
    parser.add_argument(
        "--all-tcga",
        action="store_true",
        help="In live mode, discover and fetch all TCGA PanCancer Atlas studies from cBioPortal.",
    )
    args = parser.parse_args()
    records = CBIOPORTAL_STUDIES
    extract_type = "curated_seed_studies"
    output_path = select_output_path(args.output, live=args.live)

    if args.live:
        study_ids = select_live_study_ids(
            args.study_ids,
            args.tcga_defaults,
            args.all_tcga,
        )
        try:
            records = fetch_live_studies(study_ids)
            if args.all_tcga and not args.study_ids:
                extract_type = "cbioportal_api_all_tcga_pan_can_atlas_studies"
            elif args.tcga_defaults and not args.study_ids:
                extract_type = "cbioportal_api_tcga_default_studies"
            else:
                extract_type = "cbioportal_api_studies"
        except (HTTPError, URLError, TimeoutError) as error:
            if output_path.exists():
                print(
                    f"cBioPortal live ingest failed: {error}. "
                    f"Reusing existing raw extract at {output_path}."
                )
                return
            raise SystemExit(f"cBioPortal live ingest failed: {error}") from error

    write_raw_extract(output_path, records=records, extract_type=extract_type)
    print(f"Wrote {len(records)} cBioPortal raw records to {output_path}")


if __name__ == "__main__":
    main()
