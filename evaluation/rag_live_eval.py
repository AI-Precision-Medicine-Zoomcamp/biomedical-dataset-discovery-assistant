"""Evaluate deterministic or live LLM-backed RAG answers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluation.answer_eval import DEFAULT_QUESTIONS_PATH, load_questions
from evaluation.llm_judge_eval import (
    JUDGE_DIMENSIONS,
    build_judge_prompt,
    heuristic_judge,
    parse_judge_response,
)
from src.answer import generate_answer
from src.rag import DEFAULT_CATALOG_PATH, DEFAULT_MODEL, call_openai_responses_api, run_rag


def evaluate_rag_outputs(
    catalog_path: str = DEFAULT_CATALOG_PATH,
    questions_path: Path | str = DEFAULT_QUESTIONS_PATH,
    limit: int | None = None,
    ids: list[str] | None = None,
    live_answers: bool = False,
    live_judge: bool = False,
    model: str = DEFAULT_MODEL,
    include_prompts: bool = False,
) -> dict[str, Any]:
    """Generate RAG answers and evaluate whether they meet project expectations."""

    questions = load_questions(questions_path)
    if ids:
        selected_ids = set(ids)
        questions = [question for question in questions if question["id"] in selected_ids]
    if limit is not None:
        questions = questions[:limit]

    results = []
    for question in questions:
        if live_answers:
            answer = run_rag(
                question["question"],
                catalog_path=catalog_path,
                top_k=4,
                model=model,
                live=True,
            )
            answer_mode = "live_llm_rag"
        else:
            answer = generate_answer(
                question["question"],
                catalog_path=catalog_path,
                top_k=4,
            )
            answer_mode = "deterministic_fallback"

        judge_prompt = build_judge_prompt(question, answer)
        if live_judge:
            judge_text = call_openai_responses_api(judge_prompt, model=model)
            judge = parse_judge_response(judge_text)
            judge_mode = "live_llm_judge"
        else:
            judge_text = ""
            judge = heuristic_judge(question, answer)
            judge_mode = "local_heuristic_judge"

        item = {
            "id": question["id"],
            "question": question["question"],
            "answer_mode": answer_mode,
            "judge_mode": judge_mode,
            "answer": answer,
            "judge": judge,
        }
        if include_prompts:
            item["judge_prompt"] = judge_prompt
            item["judge_raw_response"] = judge_text
        results.append(item)

    total = len(results)
    passed = sum(1 for result in results if result["judge"]["passed"])
    average_scores = {
        dimension: (
            sum(result["judge"][dimension] for result in results) / total
            if total
            else 0.0
        )
        for dimension in JUDGE_DIMENSIONS
    }
    return {
        "catalog_path": str(catalog_path),
        "questions_path": str(questions_path),
        "answer_mode": "live_llm_rag" if live_answers else "deterministic_fallback",
        "judge_mode": "live_llm_judge" if live_judge else "local_heuristic_judge",
        "model": model if live_answers or live_judge else None,
        "questions": total,
        "pass_rate": passed / total if total else 0.0,
        "average_scores": average_scores,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS_PATH)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--ids", nargs="+")
    parser.add_argument("--live-answers", action="store_true")
    parser.add_argument("--live-judge", action="store_true")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--include-prompts", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = evaluate_rag_outputs(
        catalog_path=args.catalog,
        questions_path=args.questions,
        limit=args.limit,
        ids=args.ids,
        live_answers=args.live_answers,
        live_judge=args.live_judge,
        model=args.model,
        include_prompts=args.include_prompts,
    )

    if args.json:
        print(json.dumps(report, indent=2))
        return

    print("RAG output evaluation")
    print(f"Catalog: {report['catalog_path']}")
    print(f"Questions file: {report['questions_path']}")
    print(f"Answer mode: {report['answer_mode']}")
    print(f"Judge mode: {report['judge_mode']}")
    print(f"Questions: {report['questions']}")
    print(f"Pass rate: {report['pass_rate']:.2f}")
    print("Average scores:")
    for dimension, score in report["average_scores"].items():
        print(f"  {dimension}: {score:.2f}")
    print()
    for result in report["results"]:
        status = "PASS" if result["judge"]["passed"] else "FAIL"
        print(f"{status} {result['id']}: {result['question']}")
        print(f"  answer_mode: {result['answer_mode']}")
        print(f"  judge_mode: {result['judge_mode']}")
        print(f"  rationale: {result['judge']['rationale']}")
        print()


if __name__ == "__main__":
    main()
