"""Create the first raw GDC project metadata extract.

This is a local, reproducible seed extract. It keeps the pipeline shape honest:
extract raw source metadata first, then transform it into DatasetRecord objects
in a separate step.

By default this script writes a curated seed extract. Use ``--live`` to fetch
project metadata from the GDC API while preserving the same raw output shape.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


DEFAULT_OUTPUT_PATH = Path("data/raw/gdc/projects_seed.json")
DEFAULT_LIVE_OUTPUT_PATH = Path("data/raw/gdc/projects_live.json")
DEFAULT_ALL_PROJECTS_OUTPUT_PATH = Path("data/raw/gdc/projects_all_live.json")
GDC_API_BASE_URL = "https://api.gdc.cancer.gov"
DEFAULT_PROJECT_IDS = ["TCGA-LUAD", "TCGA-LUSC", "TCGA-BRCA"]
DEFAULT_TCGA_PROJECT_IDS = [
    "TCGA-LUAD",
    "TCGA-LUSC",
    "TCGA-BRCA",
    "TCGA-COAD",
    "TCGA-READ",
    "TCGA-GBM",
    "TCGA-LGG",
    "TCGA-OV",
    "TCGA-PRAD",
    "TCGA-SKCM",
    "TCGA-KIRC",
    "TCGA-HNSC",
    "TCGA-STAD",
    "TCGA-LIHC",
    "TCGA-BLCA",
    "TCGA-UCEC",
    "TCGA-CESC",
    "TCGA-THCA",
]

GDC_PROJECTS = [
    {
        "project_id": "TCGA-LUAD",
        "program": "TCGA",
        "name": "TCGA Lung Adenocarcinoma",
        "primary_site": "lung",
        "disease_terms": ["non-small cell lung cancer", "lung cancer"],
        "cancer_types": ["lung adenocarcinoma", "LUAD"],
        "cohort_tags": ["NSCLC", "TCGA", "tumor", "adult"],
        "data_categories": [
            "Transcriptome Profiling",
            "Simple Nucleotide Variation",
            "Clinical",
            "Copy Number Variation",
        ],
        "experimental_strategies": ["RNA-Seq", "WXS"],
        "clinical_attributes": ["diagnosis", "tumor stage", "survival"],
        "inferred_genes": ["EGFR", "KRAS"],
        "inferred_mutations": ["KRAS G12C"],
        "biomarker_notes": (
            "LUAD is a strong candidate disease context for EGFR and KRAS "
            "mutation-oriented discovery, but this seed extract does not "
            "verify specific variant-positive cases."
        ),
        "limitations": [
            "Specific EGFR, KRAS, or KRAS G12C-positive case counts are not verified in this raw extract.",
            "The local pipeline stores metadata only and does not download or analyze raw genomic files.",
        ],
    },
    {
        "project_id": "TCGA-LUSC",
        "program": "TCGA",
        "name": "TCGA Lung Squamous Cell Carcinoma",
        "primary_site": "lung",
        "disease_terms": ["non-small cell lung cancer", "lung cancer"],
        "cancer_types": ["lung squamous cell carcinoma", "LUSC"],
        "cohort_tags": ["NSCLC", "TCGA", "tumor", "adult"],
        "data_categories": [
            "Transcriptome Profiling",
            "Simple Nucleotide Variation",
            "Clinical",
            "Copy Number Variation",
        ],
        "experimental_strategies": ["RNA-Seq", "WXS"],
        "clinical_attributes": ["diagnosis", "tumor stage", "survival"],
        "inferred_genes": ["EGFR", "KRAS"],
        "inferred_mutations": ["KRAS G12C"],
        "biomarker_notes": (
            "LUSC is relevant to NSCLC discovery and may support mutation-oriented "
            "search, but KRAS G12C relevance is weaker unless specific cases are verified."
        ),
        "limitations": [
            "Specific EGFR, KRAS, or KRAS G12C-positive case counts are not verified in this raw extract.",
            "KRAS G12C-oriented relevance should be treated as candidate-level unless variant-positive cases are confirmed.",
        ],
    },
    {
        "project_id": "TCGA-BRCA",
        "program": "TCGA",
        "name": "TCGA Breast Invasive Carcinoma",
        "primary_site": "breast",
        "disease_terms": ["breast cancer"],
        "cancer_types": ["breast invasive carcinoma", "BRCA"],
        "cohort_tags": ["TCGA", "tumor", "adult", "non-lung comparison"],
        "data_categories": [
            "Transcriptome Profiling",
            "Simple Nucleotide Variation",
            "Clinical",
            "Copy Number Variation",
        ],
        "experimental_strategies": ["RNA-Seq", "WXS"],
        "clinical_attributes": ["diagnosis", "tumor stage", "survival"],
        "inferred_genes": [],
        "inferred_mutations": [],
        "biomarker_notes": (
            "Included to test that lung cancer queries do not always return every TCGA cancer project."
        ),
        "limitations": [
            "This is not a lung cancer or NSCLC dataset and should not be treated as relevant to NSCLC questions."
        ],
    },
]


def _seed_by_project_id() -> dict[str, dict[str, Any]]:
    return {record["project_id"]: record for record in GDC_PROJECTS}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _extract_nested_names(items: Any) -> list[str]:
    names: list[str] = []
    for item in _as_list(items):
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict):
            value = (
                item.get("name")
                or item.get("data_category")
                or item.get("experimental_strategy")
            )
            if value:
                names.append(str(value))
    return sorted(set(names))


def _get_summary(response: dict[str, Any]) -> dict[str, Any]:
    summary = response.get("summary", {})
    return summary if isinstance(summary, dict) else {}


def _response_data(response: dict[str, Any]) -> dict[str, Any]:
    data = response.get("data", response)
    return data if isinstance(data, dict) else response


def _first_text(value: Any) -> str:
    items = _as_list(value)
    if not items:
        return ""
    return str(items[0])


def _choose_primary_site(
    value: Any,
    project_name: str,
    seed_record: dict[str, Any],
) -> str:
    if seed_record.get("primary_site"):
        return str(seed_record["primary_site"])

    sites = [str(item) for item in _as_list(value) if str(item)]
    if not sites:
        return ""

    normalized_name = project_name.lower()
    for site in sites:
        normalized_site = site.lower()
        if normalized_site in normalized_name:
            return site
        for part in normalized_site.replace(",", " ").replace("and", " ").split():
            if len(part) >= 4 and part in normalized_name:
                return site

    return sites[0]


def normalize_gdc_project_response(
    project_id: str,
    response: dict[str, Any],
    seed_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Normalize one GDC API project response into the raw pipeline shape."""

    seed_record = seed_record or {}
    data = _response_data(response)
    summary = _get_summary(data)
    data_categories = _extract_nested_names(
        summary.get("data_categories") or data.get("data_categories")
    )
    experimental_strategies = _extract_nested_names(
        summary.get("experimental_strategies") or data.get("experimental_strategies")
    )
    program = data.get("program", seed_record.get("program", ""))
    if isinstance(program, dict):
        program = program.get("name", "")

    name = str(data.get("name") or seed_record.get("name") or project_id)
    primary_site = _choose_primary_site(data.get("primary_site"), name, seed_record)
    program_value = str(program or seed_record.get("program", ""))
    disease_terms = (
        seed_record.get("disease_terms")
        or _extract_nested_names(data.get("disease_type"))
        or [primary_site]
    )
    limitations = seed_record.get("limitations") or [
        "Live GDC project metadata does not verify gene-specific or variant-positive case counts.",
        "The local pipeline stores project-level metadata only and does not download or analyze raw genomic files.",
    ]
    cohort_tags = seed_record.get("cohort_tags") or [
        tag for tag in [program_value, "tumor", "project-level metadata"] if tag
    ]

    return {
        "project_id": str(data.get("project_id") or project_id),
        "program": program_value,
        "name": name,
        "primary_site": primary_site,
        "disease_terms": disease_terms,
        "cancer_types": seed_record.get("cancer_types") or [name],
        "cohort_tags": cohort_tags,
        "data_categories": data_categories or seed_record.get("data_categories", []),
        "experimental_strategies": experimental_strategies
        or seed_record.get("experimental_strategies", []),
        "clinical_attributes": seed_record.get("clinical_attributes", []),
        "inferred_genes": seed_record.get("inferred_genes", []),
        "inferred_mutations": seed_record.get("inferred_mutations", []),
        "biomarker_notes": seed_record.get("biomarker_notes", ""),
        "limitations": limitations,
        "case_count": summary.get("case_count"),
        "file_count": summary.get("file_count"),
        "api_response": response,
    }


def fetch_gdc_project(project_id: str, timeout: int = 20) -> dict[str, Any]:
    query = urlencode(
        {
            "expand": "program,summary,summary.data_categories,summary.experimental_strategies",
        }
    )
    url = f"{GDC_API_BASE_URL}/projects/{project_id}?{query}"
    with urlopen(url, timeout=timeout) as response:  # nosec B310 - public metadata API
        return json.loads(response.read().decode("utf-8"))


def fetch_project_ids(
    timeout: int = 30,
    program_names: list[str] | None = None,
) -> list[str]:
    filters = None
    if program_names:
        filters = {
            "op": "in",
            "content": {"field": "program.name", "value": program_names},
        }
    query = urlencode(
        {
            **({"filters": json.dumps(filters)} if filters else {}),
            "fields": "project_id",
            "format": "JSON",
            "size": "10000",
            "sort": "project_id:asc",
        }
    )
    url = f"{GDC_API_BASE_URL}/projects?{query}"
    with urlopen(url, timeout=timeout) as response:  # nosec B310 - public metadata API
        payload = json.loads(response.read().decode("utf-8"))
    hits = payload.get("data", {}).get("hits", [])
    return sorted(hit["project_id"] for hit in hits if hit.get("project_id"))


def fetch_gdc_projects_bulk(limit: int | None = None, timeout: int = 30) -> list[dict[str, Any]]:
    size = str(limit or 10000)
    query = urlencode(
        {
            "fields": "project_id,name,program.name,primary_site,disease_type",
            "format": "JSON",
            "size": size,
            "sort": "project_id:asc",
        }
    )
    url = f"{GDC_API_BASE_URL}/projects?{query}"
    with urlopen(url, timeout=timeout) as response:  # nosec B310 - public metadata API
        payload = json.loads(response.read().decode("utf-8"))

    seed_records = _seed_by_project_id()
    hits = payload.get("data", {}).get("hits", [])
    records = [
        normalize_gdc_project_response(
            str(hit.get("project_id")),
            hit,
            seed_records.get(str(hit.get("project_id"))),
        )
        for hit in hits
        if hit.get("project_id")
    ]
    return records


def fetch_tcga_project_ids(timeout: int = 30) -> list[str]:
    return fetch_project_ids(timeout=timeout, program_names=["TCGA"])


def fetch_live_projects(project_ids: list[str], progress_every: int = 10) -> list[dict[str, Any]]:
    seed_records = _seed_by_project_id()
    records: list[dict[str, Any]] = []
    total = len(project_ids)
    for index, project_id in enumerate(project_ids, start=1):
        if progress_every and (index == 1 or index % progress_every == 0 or index == total):
            print(f"Fetching GDC project {index}/{total}: {project_id}", flush=True)
        response = fetch_gdc_project(project_id)
        records.append(
            normalize_gdc_project_response(
                project_id,
                response,
                seed_records.get(project_id),
            )
        )
    return records


def select_live_project_ids(
    requested_project_ids: list[str] | None,
    use_tcga_defaults: bool = False,
    use_all_tcga: bool = False,
    use_all_projects: bool = False,
    limit: int | None = None,
) -> list[str]:
    if requested_project_ids:
        project_ids = requested_project_ids
    elif use_all_projects:
        project_ids = fetch_project_ids()
    elif use_all_tcga:
        project_ids = fetch_tcga_project_ids()
    elif use_tcga_defaults:
        project_ids = DEFAULT_TCGA_PROJECT_IDS
    else:
        project_ids = DEFAULT_PROJECT_IDS

    if limit is not None:
        return project_ids[:limit]
    return project_ids


def select_output_path(requested_output: Path, live: bool = False) -> Path:
    if live and requested_output == DEFAULT_OUTPUT_PATH:
        return DEFAULT_LIVE_OUTPUT_PATH
    return requested_output


def write_raw_extract(
    output_path: Path,
    records: list[dict[str, Any]] | None = None,
    extract_type: str = "curated_seed_projects",
) -> None:
    records = records or GDC_PROJECTS
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": "GDC",
        "extract_type": extract_type,
        "extracted_at": "2026-07-15",
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
        help="Fetch project metadata from the public GDC API instead of writing the curated seed extract.",
    )
    parser.add_argument(
        "--project-id",
        action="append",
        dest="project_ids",
        help="GDC project ID to fetch in live mode. Can be repeated.",
    )
    parser.add_argument(
        "--tcga-defaults",
        action="store_true",
        help=(
            "In live mode, fetch a broader default panel of common TCGA cancer projects "
            f"({len(DEFAULT_TCGA_PROJECT_IDS)} projects)."
        ),
    )
    parser.add_argument(
        "--all-tcga",
        action="store_true",
        help="In live mode, discover and fetch all TCGA projects from the GDC API.",
    )
    parser.add_argument(
        "--all-projects",
        action="store_true",
        help="In live mode, discover and fetch all project-level metadata from the GDC API.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit selected live projects for reproducible broad-catalog smoke runs.",
    )
    args = parser.parse_args()
    records = GDC_PROJECTS
    extract_type = "curated_seed_projects"
    output_path = select_output_path(args.output, live=args.live)

    if args.live:
        try:
            if args.all_projects and not args.project_ids:
                records = fetch_gdc_projects_bulk(limit=args.limit)
                extract_type = "gdc_api_all_projects"
            else:
                project_ids = select_live_project_ids(
                    args.project_ids,
                    args.tcga_defaults,
                    args.all_tcga,
                    args.all_projects,
                    args.limit,
                )
                records = fetch_live_projects(project_ids)
                if args.all_tcga and not args.project_ids:
                    extract_type = "gdc_api_all_tcga_projects"
                elif args.tcga_defaults and not args.project_ids:
                    extract_type = "gdc_api_tcga_default_projects"
                else:
                    extract_type = "gdc_api_projects"
        except (HTTPError, URLError, TimeoutError) as error:
            if output_path.exists():
                print(
                    f"GDC live ingest failed: {error}. "
                    f"Reusing existing raw extract at {output_path}."
                )
                return
            raise SystemExit(f"GDC live ingest failed: {error}") from error

    write_raw_extract(output_path, records=records, extract_type=extract_type)
    print(f"Wrote {len(records)} GDC raw records to {output_path}")


if __name__ == "__main__":
    main()
