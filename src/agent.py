"""A minimal tool-using agent scaffold for dataset discovery."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from typing import Any

from src.tools import (
    DEFAULT_CATALOG_PATH,
    ToolResult,
    generate_grounded_answer,
    get_dataset_details,
    search_catalog,
)


def run_agent(
    question: str,
    catalog_path: str = DEFAULT_CATALOG_PATH,
    top_k: int = 4,
) -> dict[str, Any]:
    """Run a transparent local tool-using workflow.

    This is an agent scaffold: it uses tools and returns a trace, but the LLM is
    not yet choosing tools autonomously.
    """

    trace: list[ToolResult] = []

    search_result = search_catalog(question, catalog_path=catalog_path, top_k=top_k)
    trace.append(search_result)

    dataset_ids = [
        result["dataset_id"]
        for result in search_result.output.get("results", [])
    ]
    detail_result: ToolResult | None = None
    if dataset_ids:
        detail_result = get_dataset_details(
            dataset_ids,
            catalog_path=catalog_path,
            question=question,
        )
        trace.append(detail_result)

    answer_result = generate_grounded_answer(
        question,
        catalog_path=catalog_path,
        top_k=top_k,
        details=detail_result.output["details"] if detail_result else None,
    )
    trace.append(answer_result)

    return {
        "question": question,
        "mode": "local_tool_agent_scaffold",
        "agent_note": (
            "This workflow calls local tools and returns a trace. "
            "LLM autonomous tool selection is a planned next step."
        ),
        "final_answer": answer_result.output["answer"],
        "tool_trace": [asdict(item) for item in trace],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--catalog", default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_agent(args.question, catalog_path=args.catalog, top_k=args.top_k)
    if args.json:
        print(json.dumps(result, indent=2))
        return

    print(result["final_answer"])
    print()
    print("Tool trace:")
    for index, item in enumerate(result["tool_trace"], start=1):
        print(f"{index}. {item['name']}")


if __name__ == "__main__":
    main()
