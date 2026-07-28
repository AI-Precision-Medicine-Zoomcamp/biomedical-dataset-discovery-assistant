"""Reverse-check answer claims against the catalog evidence."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from evaluation.answer_eval import DEFAULT_QUESTIONS_PATH, load_questions
from src.answer import generate_answer
from src.catalog import load_catalog
from src.models import DatasetRecord
from src.rag import DEFAULT_CATALOG_PATH


UNSUPPORTED_VERIFICATION_PATTERNS = [
    re.compile(r"\bconfirmed\b.*\b(case|sample|cohort|count)", re.IGNORECASE),
    re.compile(r"\bverified\b.*\b(case|sample|cohort|count)", re.IGNORECASE),
    re.compile(r"\bpositive\b.*\b(case|sample|cohort|count)", re.IGNORECASE),
    re.compile(r"\bhas\b.*\bKRAS G12C-positive\b", re.IGNORECASE),
]

UNCERTAINTY_TERMS = [
    "not verified",
    "not confirmed",
    "does not verify",
    "does not confirm",
    "do not verify",
    "do not confirm",
    "unverified",
    "not explicit",
    "not available",
    "unknown",
    "candidate",
]


def _record_lookup(records: list[DatasetRecord]) -> dict[str, DatasetRecord]:
    lookup = {}
    for record in records:
        lookup[record.dataset_id.lower()] = record
        lookup[record.canonical_dataset_id.lower()] = record
        lookup[record.source_record_id.lower()] = record
    return lookup


def _mentioned_records(answer: str, records: list[DatasetRecord]) -> list[DatasetRecord]:
    normalized = answer.lower()
    mentioned = []
    seen = set()
    for record in records:
        aliases = {
            record.dataset_id.lower(),
            record.canonical_dataset_id.lower(),
            record.source_record_id.lower(),
        }
        if aliases & set(re.findall(r"[a-z0-9:_\-.]+", normalized)):
            if record.dataset_id not in seen:
                mentioned.append(record)
                seen.add(record.dataset_id)
    return mentioned


def _source_claim_supported(answer: str, record: DatasetRecord) -> bool:
    normalized = answer.lower()
    source = record.source.lower()
    dataset_aliases = [
        record.dataset_id.lower(),
        record.canonical_dataset_id.lower(),
        record.source_record_id.lower(),
    ]
    if not any(alias in normalized for alias in dataset_aliases):
        return True
    if source in normalized:
        return True
    return ":" not in record.dataset_id


def _has_explicit_variant_evidence(record: DatasetRecord) -> bool:
    evidence_values = []
    for item in record.evidence_items:
        evidence_values.extend(item.value.split("; "))

    text = " ".join([*record.explicit_mutations, *evidence_values]).lower()
    return "kras g12c" in text


def _unsupported_verification_sentences(answer: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", answer.strip())
    unsupported = []
    for sentence in sentences:
        normalized = sentence.lower()
        if normalized.startswith("question:"):
            continue
        if any(term in normalized for term in UNCERTAINTY_TERMS):
            continue
        if any(pattern.search(sentence) for pattern in UNSUPPORTED_VERIFICATION_PATTERNS):
            unsupported.append(sentence)
    return unsupported


def verify_answer_claims(
    question: dict[str, Any],
    answer: str,
    catalog_path: str = DEFAULT_CATALOG_PATH,
) -> dict[str, Any]:
    """Check whether answer claims are supported by catalog records."""

    records = load_catalog(catalog_path)
    normalized = answer.lower()
    failures = []
    warnings = []

    expected_ids = question.get("expected_dataset_ids", [])
    absent_ids = question.get("expected_absent_dataset_ids", [])
    min_expected_hits = int(question.get("min_expected_dataset_hits", len(expected_ids)))

    mentioned_expected_ids = [
        dataset_id
        for dataset_id in expected_ids
        if dataset_id.lower() in normalized
        or dataset_id.lower().split(":", 1)[-1] in normalized
    ]
    if expected_ids and len(mentioned_expected_ids) < min_expected_hits:
        missing_ids = [
            dataset_id
            for dataset_id in expected_ids
            if dataset_id not in mentioned_expected_ids
        ]
        failures.append(
            {
                "type": "missing_expected_dataset",
                "claim": ", ".join(missing_ids),
                "reason": (
                    "Answer did not mention enough expected datasets by "
                    f"source-specific or canonical ID: {len(mentioned_expected_ids)} "
                    f"found, {min_expected_hits} required."
                ),
            }
        )

    for dataset_id in absent_ids:
        if dataset_id.lower() in normalized:
            failures.append(
                {
                    "type": "absent_dataset_leak",
                    "claim": dataset_id,
                    "reason": "Answer mentioned a dataset explicitly marked absent for this question.",
                }
            )

    mentioned = _mentioned_records(answer, records)
    for record in mentioned:
        if not _source_claim_supported(answer, record):
            warnings.append(
                {
                    "type": "source_not_explicit",
                    "claim": record.dataset_id,
                    "reason": "Dataset is mentioned, but the source label is not explicit near the answer text.",
                }
            )

    unsupported_verification_sentences = _unsupported_verification_sentences(answer)
    has_unsupported_verification_claim = bool(unsupported_verification_sentences)
    asks_variant_counts = any(
        term in question["question"].lower()
        for term in ["kras g12c", "positive case", "case count", "sample count"]
    )
    if has_unsupported_verification_claim or asks_variant_counts:
        records_with_explicit_variant = [
            record.dataset_id for record in mentioned if _has_explicit_variant_evidence(record)
        ]
        if has_unsupported_verification_claim and not records_with_explicit_variant:
            failures.append(
                {
                    "type": "unsupported_variant_or_case_count_claim",
                    "claim": unsupported_verification_sentences[0],
                    "reason": "Answer appears to claim explicit variant/case-count support, but the catalog only supports candidate-level evidence.",
                }
            )
        if asks_variant_counts and "not verified" not in normalized and "not confirmed" not in normalized:
            failures.append(
                {
                    "type": "missing_uncertainty_for_variant_counts",
                    "claim": "variant-positive case or sample count answer",
                    "reason": "Question asks for specific variant/count evidence, but answer does not clearly say it is not verified.",
                }
            )

    return {
        "id": question["id"],
        "question": question["question"],
        "passed": not failures,
        "mentioned_dataset_ids": [record.dataset_id for record in mentioned],
        "failures": failures,
        "warnings": warnings,
    }


def evaluate_claims(
    catalog_path: str = DEFAULT_CATALOG_PATH,
    questions_path: Path | str = DEFAULT_QUESTIONS_PATH,
    limit: int | None = None,
) -> dict[str, Any]:
    questions = load_questions(questions_path)
    if limit is not None:
        questions = questions[:limit]

    results = []
    for question in questions:
        answer = generate_answer(
            question["question"],
            catalog_path=catalog_path,
            top_k=4,
        )
        result = verify_answer_claims(question, answer, catalog_path=catalog_path)
        result["answer"] = answer
        results.append(result)

    total = len(results)
    passed = sum(1 for result in results if result["passed"])
    return {
        "catalog_path": str(catalog_path),
        "questions_path": str(questions_path),
        "questions": total,
        "claim_pass_rate": passed / total if total else 0.0,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS_PATH)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = evaluate_claims(
        catalog_path=args.catalog,
        questions_path=args.questions,
        limit=args.limit,
    )

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("Claim verification evaluation")
    print(f"Catalog: {report['catalog_path']}")
    print(f"Questions file: {report['questions_path']}")
    print(f"Questions: {report['questions']}")
    print(f"Claim pass rate: {report['claim_pass_rate']:.2f}")
    print()
    for result in report["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status} {result['id']}: {result['question']}")
        if result["failures"]:
            for failure in result["failures"]:
                print(f"  {failure['type']}: {failure['reason']}")
        print()


if __name__ == "__main__":
    main()
