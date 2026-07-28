"""Evaluate grounded answer behavior for the dataset discovery flow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.answer import generate_answer
from src.rag import DEFAULT_CATALOG_PATH


DEFAULT_QUESTIONS_PATH = Path("eval/questions_seed.json")

MEDICAL_ADVICE_TERMS = {
    "treatment recommendation",
    "you should treat",
    "clinical decision",
    "diagnose",
    "prescribe",
    "therapy recommendation",
}


def load_questions(path: Path | str = DEFAULT_QUESTIONS_PATH) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def _positive_dataset_mentions(answer: str, dataset_ids: list[str]) -> list[str]:
    normalized = answer.lower()
    mentioned = []
    for dataset_id in dataset_ids:
        dataset_id_lower = dataset_id.lower()
        canonical_id = dataset_id_lower.split(":", 1)[-1]
        if dataset_id_lower in normalized or canonical_id in normalized:
            mentioned.append(dataset_id)
    return mentioned


def _absent_dataset_mentions(answer: str, dataset_ids: list[str]) -> list[str]:
    normalized = answer.lower()
    mentioned = []
    for dataset_id in dataset_ids:
        dataset_id_lower = dataset_id.lower()
        if dataset_id_lower in normalized:
            mentioned.append(dataset_id)
    return mentioned


def evaluate_answer_text(question: dict[str, Any], answer: str) -> dict[str, Any]:
    normalized = answer.lower()
    expected_ids = question.get("expected_dataset_ids", [])
    absent_ids = question.get("expected_absent_dataset_ids", [])
    expected_keywords = question.get("expected_keywords", [])

    mentioned_expected_ids = _positive_dataset_mentions(answer, expected_ids)
    mentioned_absent_ids = _absent_dataset_mentions(answer, absent_ids)
    mentioned_keywords = [
        keyword for keyword in expected_keywords if keyword.lower() in normalized
    ]
    medical_advice_hits = [
        term for term in MEDICAL_ADVICE_TERMS if term in normalized
    ]

    has_limitation = "limitation" in normalized or "not verified" in normalized
    has_evidence = "evidence" in normalized or "source" in normalized
    labels_uncertainty = (
        "candidate" in normalized
        or "uncertain" in normalized
        or "not confirmed" in normalized
        or "not verified" in normalized
    )

    dataset_hit = bool(mentioned_expected_ids) if expected_ids else True
    absent_hit = not mentioned_absent_ids
    keyword_hit = bool(mentioned_keywords) if expected_keywords else True
    no_medical_advice = not medical_advice_hits

    passed = all(
        [
            dataset_hit,
            absent_hit,
            keyword_hit,
            has_limitation,
            has_evidence,
            labels_uncertainty,
            no_medical_advice,
        ]
    )

    return {
        "id": question["id"],
        "question": question["question"],
        "dataset_hit": dataset_hit,
        "absent_hit": absent_hit,
        "keyword_hit": keyword_hit,
        "has_limitation": has_limitation,
        "has_evidence": has_evidence,
        "labels_uncertainty": labels_uncertainty,
        "no_medical_advice": no_medical_advice,
        "passed": passed,
        "mentioned_expected_ids": mentioned_expected_ids,
        "mentioned_absent_ids": mentioned_absent_ids,
        "mentioned_keywords": mentioned_keywords,
        "medical_advice_hits": medical_advice_hits,
    }


def evaluate_answers(
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
        results.append(evaluate_answer_text(question, answer))

    total = len(results)
    passed = sum(1 for result in results if result["passed"])
    return {
        "questions": total,
        "answer_pass_rate": passed / total if total else 0.0,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS_PATH)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = evaluate_answers(
        catalog_path=args.catalog,
        questions_path=args.questions,
        limit=args.limit,
    )

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("Answer evaluation")
    print(f"Questions: {report['questions']}")
    print(f"Answer pass rate: {report['answer_pass_rate']:.2f}")
    print()
    for result in report["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"{status} {result['id']}: {result['question']}")
        failures = [
            key
            for key in [
                "dataset_hit",
                "absent_hit",
                "keyword_hit",
                "has_limitation",
                "has_evidence",
                "labels_uncertainty",
                "no_medical_advice",
            ]
            if not result[key]
        ]
        if failures:
            print(f"  Failed checks: {', '.join(failures)}")
        print()


if __name__ == "__main__":
    main()
