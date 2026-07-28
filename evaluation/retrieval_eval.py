"""Run retrieval evaluation against a selected catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from src.catalog import load_catalog
from src.retriever import search


DEFAULT_QUESTIONS_PATH = Path("eval/questions_seed.json")
DEFAULT_CATALOG_PATH = Path("data/processed/seed_catalog.json")


def load_questions(path: Path | str = DEFAULT_QUESTIONS_PATH) -> list[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate(
    top_k: int = 5,
    catalog_path: Path | str = DEFAULT_CATALOG_PATH,
    questions_path: Path | str = DEFAULT_QUESTIONS_PATH,
    method: str = "hybrid",
) -> dict[str, Any]:
    records = load_catalog(catalog_path)
    questions = load_questions(questions_path)
    results = []

    for question in questions:
        retrieved = search(question["question"], records, top_k=top_k, method=method)
        retrieved_ids = [result.record.dataset_id for result in retrieved]
        expected_ids = question.get("expected_dataset_ids", [])
        expected_sources = question.get("expected_sources", [])
        expected_absent_ids = question.get("expected_absent_dataset_ids", [])
        expected_top_ids = question.get("expected_top_dataset_ids", [])
        min_expected_hits = int(question.get("min_expected_dataset_hits", 1))

        expected_retrieved_ids = [
            dataset_id for dataset_id in expected_ids if dataset_id in retrieved_ids
        ]
        dataset_hit = (
            len(expected_retrieved_ids) >= min_expected_hits
            if expected_ids
            else True
        )
        top_hit = (
            retrieved_ids[0] in expected_top_ids
            if expected_top_ids and retrieved_ids
            else True
        )
        source_hit = (
            any(result.record.source in expected_sources for result in retrieved)
            if expected_sources
            else True
        )
        absent_hit = not any(
            dataset_id in retrieved_ids for dataset_id in expected_absent_ids
        )

        results.append(
            {
                "id": question["id"],
                "question": question["question"],
                "expected_dataset_ids": expected_ids,
                "expected_absent_dataset_ids": expected_absent_ids,
                "expected_top_dataset_ids": expected_top_ids,
                "retrieved_dataset_ids": retrieved_ids,
                "expected_retrieved_ids": expected_retrieved_ids,
                "dataset_hit": dataset_hit,
                "top_hit": top_hit,
                "source_hit": source_hit,
                "absent_hit": absent_hit,
                "top_results": [
                    {
                        "dataset_id": result.record.dataset_id,
                        "canonical_dataset_id": result.record.canonical_dataset_id,
                        "source": result.record.source,
                        "score": result.score,
                        "matched_terms": result.matched_terms,
                    }
                    for result in retrieved
                ],
            }
        )

    dataset_hits = sum(1 for result in results if result["dataset_hit"])
    top_hits = sum(1 for result in results if result["top_hit"])
    source_hits = sum(1 for result in results if result["source_hit"])
    absent_hits = sum(1 for result in results if result["absent_hit"])
    total = len(results)

    return {
        "catalog_path": str(catalog_path),
        "questions_path": str(questions_path),
        "method": method,
        "top_k": top_k,
        "questions": total,
        "dataset_hit_rate": dataset_hits / total if total else 0.0,
        "top_hit_rate": top_hits / total if total else 0.0,
        "source_hit_rate": source_hits / total if total else 0.0,
        "absent_hit_rate": absent_hits / total if total else 0.0,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS_PATH)
    parser.add_argument(
        "--method",
        choices=["keyword", "tfidf", "hybrid"],
        default="hybrid",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = evaluate(
        top_k=args.top_k,
        catalog_path=args.catalog,
        questions_path=args.questions,
        method=args.method,
    )
    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("Retrieval evaluation")
    print(f"Catalog: {report['catalog_path']}")
    print(f"Questions file: {report['questions_path']}")
    print(f"Method: {report['method']}")
    print(f"Questions: {report['questions']}")
    print(f"Top K: {report['top_k']}")
    print(f"Dataset hit rate: {report['dataset_hit_rate']:.2f}")
    print(f"Top hit rate: {report['top_hit_rate']:.2f}")
    print(f"Source hit rate: {report['source_hit_rate']:.2f}")
    print(f"Absent hit rate: {report['absent_hit_rate']:.2f}")
    print()

    for result in report["results"]:
        status = (
            "PASS"
            if (
                result["dataset_hit"]
                and result["top_hit"]
                and result["source_hit"]
                and result["absent_hit"]
            )
            else "FAIL"
        )
        print(f"{status} {result['id']}: {result['question']}")
        for item in result["top_results"][:3]:
            print(
                "  "
                f"{item['dataset_id']} "
                f"({item['source']}, score={item['score']:.1f})"
            )
        print()


if __name__ == "__main__":
    main()
