"""Compare retrieval methods on the same catalog and question set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.retrieval_eval import (
    DEFAULT_CATALOG_PATH,
    DEFAULT_QUESTIONS_PATH,
    evaluate,
)


METHODS = ["keyword", "tfidf", "hybrid"]
SCORE_FIELDS = [
    "dataset_hit_rate",
    "top_hit_rate",
    "source_hit_rate",
    "absent_hit_rate",
]
METHOD_TIE_BREAKER = {
    "hybrid": 2,
    "keyword": 1,
    "tfidf": 0,
}


def compare_methods(
    catalog_path: Path | str = DEFAULT_CATALOG_PATH,
    questions_path: Path | str = DEFAULT_QUESTIONS_PATH,
    top_k: int = 5,
    methods: list[str] | None = None,
) -> dict[str, Any]:
    selected_methods = methods or METHODS
    reports = [
        evaluate(
            top_k=top_k,
            catalog_path=catalog_path,
            questions_path=questions_path,
            method=method,
        )
        for method in selected_methods
    ]
    ranked = sorted(
        reports,
        key=lambda report: (
            *[report[field] for field in SCORE_FIELDS],
            METHOD_TIE_BREAKER.get(str(report["method"]), 0),
        ),
        reverse=True,
    )
    return {
        "catalog_path": str(catalog_path),
        "questions_path": str(questions_path),
        "top_k": top_k,
        "best_method": ranked[0]["method"] if ranked else None,
        "reports": reports,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS_PATH)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = compare_methods(
        catalog_path=args.catalog,
        questions_path=args.questions,
        top_k=args.top_k,
    )

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("Retrieval method comparison")
    print(f"Catalog: {report['catalog_path']}")
    print(f"Questions file: {report['questions_path']}")
    print(f"Top K: {report['top_k']}")
    print(f"Best method: {report['best_method']}")
    print()
    print("method   dataset  top  source  absent")
    for item in report["reports"]:
        print(
            f"{item['method']:<8} "
            f"{item['dataset_hit_rate']:.2f}     "
            f"{item['top_hit_rate']:.2f} "
            f"{item['source_hit_rate']:.2f}    "
            f"{item['absent_hit_rate']:.2f}"
        )


if __name__ == "__main__":
    main()
