"""Generate a transparent evaluation report for dataset-discovery answers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.answer_eval import evaluate_answer_text
from evaluation.claim_eval import verify_answer_claims
from evaluation.retrieval_eval import evaluate as evaluate_retrieval
from evaluation.retrieval_eval import load_questions
from src.answer import generate_answer
from src.rag import DEFAULT_CATALOG_PATH


DEFAULT_OUTPUT_PATH = Path("docs/evaluation_report_reliability.md")


def _status(value: bool) -> str:
    return "PASS" if value else "FAIL"


def _first_lines(text: str, limit: int = 10) -> str:
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:limit])


def build_evaluation_report(
    catalog_path: str = DEFAULT_CATALOG_PATH,
    questions_path: Path | str = "eval/questions_reliability.json",
    method: str = "hybrid",
    top_k: int = 5,
    answer_top_k: int = 4,
    limit: int | None = None,
) -> dict[str, Any]:
    """Combine retrieval, answer, and claim checks into one report object."""

    retrieval_report = evaluate_retrieval(
        catalog_path=catalog_path,
        questions_path=questions_path,
        method=method,
        top_k=top_k,
    )
    questions = load_questions(questions_path)
    if limit is not None:
        questions = questions[:limit]
        retrieval_results = retrieval_report["results"][:limit]
    else:
        retrieval_results = retrieval_report["results"]

    results = []
    for question, retrieval_result in zip(questions, retrieval_results):
        answer = generate_answer(
            question["question"],
            catalog_path=catalog_path,
            top_k=answer_top_k,
        )
        answer_result = evaluate_answer_text(question, answer)
        claim_result = verify_answer_claims(
            question,
            answer,
            catalog_path=catalog_path,
        )
        passed = all(
            [
                retrieval_result["dataset_hit"],
                retrieval_result["top_hit"],
                retrieval_result["source_hit"],
                retrieval_result["absent_hit"],
                answer_result["passed"],
                claim_result["passed"],
            ]
        )
        results.append(
            {
                "id": question["id"],
                "question": question["question"],
                "expected_dataset_ids": question.get("expected_dataset_ids", []),
                "min_expected_dataset_hits": question.get(
                    "min_expected_dataset_hits",
                    len(question.get("expected_dataset_ids", [])) or 1,
                ),
                "expected_absent_dataset_ids": question.get(
                    "expected_absent_dataset_ids",
                    [],
                ),
                "expected_sources": question.get("expected_sources", []),
                "retrieved_dataset_ids": retrieval_result["retrieved_dataset_ids"],
                "expected_retrieved_ids": retrieval_result["expected_retrieved_ids"],
                "retrieval_checks": {
                    "dataset_hit": retrieval_result["dataset_hit"],
                    "top_hit": retrieval_result["top_hit"],
                    "source_hit": retrieval_result["source_hit"],
                    "absent_hit": retrieval_result["absent_hit"],
                },
                "answer_checks": {
                    "dataset_hit": answer_result["dataset_hit"],
                    "absent_hit": answer_result["absent_hit"],
                    "keyword_hit": answer_result["keyword_hit"],
                    "has_limitation": answer_result["has_limitation"],
                    "has_evidence": answer_result["has_evidence"],
                    "labels_uncertainty": answer_result["labels_uncertainty"],
                    "no_medical_advice": answer_result["no_medical_advice"],
                },
                "claim_checks": {
                    "passed": claim_result["passed"],
                    "mentioned_dataset_ids": claim_result["mentioned_dataset_ids"],
                    "failures": claim_result["failures"],
                    "warnings": claim_result["warnings"],
                },
                "answer_excerpt": _first_lines(answer),
                "passed": passed,
            }
        )

    total = len(results)
    passed = sum(1 for result in results if result["passed"])
    return {
        "catalog_path": str(catalog_path),
        "questions_path": str(questions_path),
        "method": method,
        "top_k": top_k,
        "answer_top_k": answer_top_k,
        "questions": total,
        "pass_rate": passed / total if total else 0.0,
        "results": results,
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render a concise markdown report that explains why each case passed."""

    lines = [
        "# Evaluation Report",
        "",
        "This report combines retrieval checks, answer guardrails, and reverse claim verification.",
        "",
        "## Summary",
        "",
        f"- Catalog: `{report['catalog_path']}`",
        f"- Questions: `{report['questions_path']}`",
        f"- Retrieval method: `{report['method']}`",
        f"- Retrieval top-k: `{report['top_k']}`",
        f"- Answer top-k: `{report['answer_top_k']}`",
        f"- Questions evaluated: `{report['questions']}`",
        f"- Overall pass rate: `{report['pass_rate']:.2f}`",
        "",
        "## Cases",
        "",
    ]

    for result in report["results"]:
        lines.extend(
            [
                f"### {result['id']}: {_status(result['passed'])}",
                "",
                f"Question: {result['question']}",
                "",
                "Expected datasets:",
                "",
            ]
        )
        for dataset_id in result["expected_dataset_ids"]:
            lines.append(f"- `{dataset_id}`")
        if not result["expected_dataset_ids"]:
            lines.append("- none")
        lines.extend(
            [
                "",
                f"Minimum expected hits: `{result['min_expected_dataset_hits']}`",
                "",
                "Expected absent datasets:",
                "",
            ]
        )
        for dataset_id in result["expected_absent_dataset_ids"]:
            lines.append(f"- `{dataset_id}`")
        if not result["expected_absent_dataset_ids"]:
            lines.append("- none")
        lines.extend(["", "Retrieved datasets:", ""])
        for dataset_id in result["retrieved_dataset_ids"]:
            marker = "expected" if dataset_id in result["expected_retrieved_ids"] else "candidate"
            lines.append(f"- `{dataset_id}` ({marker})")

        lines.extend(["", "Retrieval checks:", ""])
        for name, value in result["retrieval_checks"].items():
            lines.append(f"- `{name}`: {_status(value)}")

        lines.extend(["", "Answer checks:", ""])
        for name, value in result["answer_checks"].items():
            lines.append(f"- `{name}`: {_status(value)}")

        lines.extend(["", "Claim checks:", ""])
        lines.append(f"- `passed`: {_status(result['claim_checks']['passed'])}")
        mentioned = result["claim_checks"]["mentioned_dataset_ids"]
        lines.append(
            "- `mentioned_dataset_ids`: "
            + (", ".join(f"`{dataset_id}`" for dataset_id in mentioned) if mentioned else "none")
        )
        if result["claim_checks"]["failures"]:
            for failure in result["claim_checks"]["failures"]:
                lines.append(f"- failure `{failure['type']}`: {failure['reason']}")
        if result["claim_checks"]["warnings"]:
            for warning in result["claim_checks"]["warnings"]:
                lines.append(f"- warning `{warning['type']}`: {warning['reason']}")

        lines.extend(
            [
                "",
                "Answer excerpt:",
                "",
                "```text",
                result["answer_excerpt"],
                "```",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--questions", type=Path, default=Path("eval/questions_reliability.json"))
    parser.add_argument(
        "--method",
        choices=["keyword", "tfidf", "hybrid"],
        default="hybrid",
    )
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--answer-top-k", type=int, default=4)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_evaluation_report(
        catalog_path=args.catalog,
        questions_path=args.questions,
        method=args.method,
        top_k=args.top_k,
        answer_top_k=args.answer_top_k,
        limit=args.limit,
    )

    if args.json:
        print(json.dumps(report, indent=2))
        return

    markdown = render_markdown(report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")

    print("Evaluation report")
    print(f"Output: {args.output}")
    print(f"Questions: {report['questions']}")
    print(f"Pass rate: {report['pass_rate']:.2f}")


if __name__ == "__main__":
    main()
