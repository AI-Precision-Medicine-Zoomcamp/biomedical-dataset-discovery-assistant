"""Evidence-aware answer generation over retrieved dataset records."""

from __future__ import annotations

import argparse

from src.catalog import load_catalog
from src.models import DatasetRecord
from src.retriever import RetrievalResult, search


GENE_TERMS = {"egfr", "kras"}
MUTATION_TERMS = {"g12c", "kras g12c"}


def _contains_any(text: str, terms: set[str]) -> bool:
    normalized = text.lower()
    return any(term in normalized for term in terms)


def _record_terms(record: DatasetRecord) -> str:
    values = [
        *record.explicit_genes,
        *record.inferred_genes,
        *record.explicit_mutations,
        *record.inferred_mutations,
        record.biomarker_notes,
    ]
    return " ".join(values).lower()


def match_level(query: str, record: DatasetRecord) -> str:
    """Return a conservative, query-time match label for a record."""

    normalized_query = query.lower()
    record_terms = _record_terms(record)

    if _contains_any(normalized_query, MUTATION_TERMS):
        if _contains_any(" ".join(record.explicit_mutations).lower(), MUTATION_TERMS):
            return "strong"
        if record.has_mutation and _contains_any(record_terms, MUTATION_TERMS):
            return "medium"
        return "weak"

    if _contains_any(normalized_query, GENE_TERMS):
        explicit_gene_text = " ".join(record.explicit_genes).lower()
        if record.has_mutation and _contains_any(explicit_gene_text, GENE_TERMS):
            return "strong"
        if record.has_mutation and _contains_any(record_terms, GENE_TERMS):
            return "medium"
        return "weak"

    return "candidate"


def _summarize_record(question: str, result: RetrievalResult) -> list[str]:
    record = result.record
    evidence = record.evidence_items[:2]
    lines = [
        f"- {record.dataset_id} ({record.source}, {record.canonical_dataset_id})",
        f"  Match level: {match_level(question, record)}",
        f"  Why it appears: {record.title}; data types: {', '.join(record.data_types) or 'unknown'}.",
    ]

    if evidence:
        lines.append("  Evidence:")
        for item in evidence:
            lines.append(
                f"  - {item.field}: {item.value} "
                f"({item.source}; confidence={item.confidence})"
            )

    if record.limitations:
        lines.append(f"  Key limitation: {record.limitations[0]}")

    lines.append(f"  Source URL: {record.source_url}")
    return lines


def generate_answer(
    question: str,
    top_k: int = 4,
    catalog_path: str = "data/processed/seed_catalog.json",
) -> str:
    """Generate a grounded, non-clinical answer from the selected catalog."""

    records = load_catalog(catalog_path)
    retrieved = search(question, records, top_k=top_k)

    if not retrieved:
        return "\n".join(
            [
                f"Question: {question}",
                "",
                "No matching dataset records were found in the current catalog.",
                "Current scope: GDC/TCGA and cBioPortal seed records for LUAD, LUSC, and BRCA comparison data.",
                "Limitation: this does not mean no public dataset exists; it means this prototype catalog does not contain one yet.",
            ]
        )

    lines = [
        f"Question: {question}",
        "",
        "Candidate dataset records from the current catalog:",
    ]
    for result in retrieved:
        lines.extend(_summarize_record(question, result))

    lines.extend(
        [
            "",
            "Interpretation guardrail:",
            "These are dataset-discovery candidates, not clinical recommendations.",
            "When gene or mutation evidence is inferred rather than explicit, the answer should be treated as a lead for follow-up inspection, not confirmed cohort evidence.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--catalog", default="data/processed/seed_catalog.json")
    args = parser.parse_args()
    print(generate_answer(args.question, top_k=args.top_k, catalog_path=args.catalog))


if __name__ == "__main__":
    main()
