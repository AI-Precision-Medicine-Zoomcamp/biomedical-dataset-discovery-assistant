"""Local tools used by the dataset discovery agent."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from src.answer import generate_answer, match_level
from src.catalog import load_catalog
from src.models import DatasetRecord
from src.retriever import search


DEFAULT_CATALOG_PATH = "data/processed/catalog.json"


@dataclass(frozen=True)
class ToolResult:
    name: str
    input: dict[str, Any]
    output: dict[str, Any]


def _record_summary(question: str, record: DatasetRecord, score: float) -> dict[str, Any]:
    return {
        "dataset_id": record.dataset_id,
        "canonical_dataset_id": record.canonical_dataset_id,
        "source": record.source,
        "title": record.title,
        "source_url": record.source_url,
        "match_level": match_level(question, record),
        "score": score,
        "data_types": record.data_types,
        "limitations": record.limitations[:2],
    }


def search_catalog(
    question: str,
    catalog_path: str = DEFAULT_CATALOG_PATH,
    top_k: int = 4,
) -> ToolResult:
    records = load_catalog(catalog_path)
    results = search(question, records, top_k=top_k)
    return ToolResult(
        name="search_catalog",
        input={"question": question, "catalog_path": catalog_path, "top_k": top_k},
        output={
            "results": [
                _record_summary(question, result.record, result.score)
                for result in results
            ]
        },
    )


def get_dataset_details(
    dataset_ids: list[str],
    catalog_path: str = DEFAULT_CATALOG_PATH,
    question: str | None = None,
) -> ToolResult:
    records = load_catalog(catalog_path)
    by_id = {record.dataset_id: record for record in records}
    details = []

    for dataset_id in dataset_ids:
        record = by_id.get(dataset_id)
        if record is None:
            details.append({"dataset_id": dataset_id, "found": False})
            continue
        details.append(
            {
                "dataset_id": record.dataset_id,
                "found": True,
                "canonical_dataset_id": record.canonical_dataset_id,
                "source": record.source,
                "title": record.title,
                "source_url": record.source_url,
                "match_level": match_level(question, record) if question else None,
                "diseases": record.diseases,
                "cancer_types": record.cancer_types,
                "primary_sites": record.primary_sites,
                "data_types": record.data_types,
                "evidence_items": [asdict(item) for item in record.evidence_items[:3]],
                "limitations": record.limitations[:3],
            }
        )

    return ToolResult(
        name="get_dataset_details",
        input={
            "dataset_ids": dataset_ids,
            "catalog_path": catalog_path,
            "question": question,
        },
        output={"details": details},
    )


def _format_detail_answer(question: str, details: list[dict[str, Any]]) -> str:
    found_details = [detail for detail in details if detail.get("found")]
    if not found_details:
        return "\n".join(
            [
                f"Question: {question}",
                "",
                "No matching dataset details were found in the current catalog.",
                "Limitation: this does not mean no public dataset exists; it means this prototype catalog does not contain one yet.",
            ]
        )

    lines = [
        f"Question: {question}",
        "",
        "Tool-grounded candidate dataset records from the current catalog:",
    ]
    for detail in found_details:
        data_types = ", ".join(detail.get("data_types", [])) or "unknown"
        match = detail.get("match_level") or "candidate"
        lines.extend(
            [
                f"- {detail['dataset_id']} ({detail['source']}, {detail['canonical_dataset_id']})",
                f"  Match level: {match}",
                f"  Why it appears: {detail['title']}; data types: {data_types}.",
            ]
        )

        evidence_items = detail.get("evidence_items", [])
        if evidence_items:
            lines.append("  Evidence:")
            for item in evidence_items[:2]:
                lines.append(
                    f"  - {item['field']}: {item['value']} "
                    f"({item['source']}; confidence={item['confidence']})"
                )

        limitations = detail.get("limitations", [])
        if limitations:
            lines.append(f"  Key limitation: {limitations[0]}")

        lines.append(f"  Source URL: {detail['source_url']}")

    lines.extend(
        [
            "",
            "Interpretation guardrail:",
            "These are dataset-discovery candidates, not clinical recommendations.",
            "When gene or mutation evidence is inferred rather than explicit, the answer should be treated as a lead for follow-up inspection, not confirmed cohort evidence.",
        ]
    )
    return "\n".join(lines)


def generate_grounded_answer(
    question: str,
    catalog_path: str = DEFAULT_CATALOG_PATH,
    top_k: int = 4,
    details: list[dict[str, Any]] | None = None,
) -> ToolResult:
    answer = (
        _format_detail_answer(question, details)
        if details is not None
        else generate_answer(question, catalog_path=catalog_path, top_k=top_k)
    )
    return ToolResult(
        name="generate_grounded_answer",
        input={
            "question": question,
            "catalog_path": catalog_path,
            "top_k": top_k,
            "uses_dataset_details": details is not None,
        },
        output={"answer": answer},
    )
