"""LLM-backed RAG flow for biomedical dataset discovery."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from src.answer import generate_answer, match_level
from src.catalog import load_catalog
from src.retriever import RetrievalResult, search


DEFAULT_CATALOG_PATH = "data/processed/catalog.json"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_OPENAI_BASE_URL = "https://api.openai.com/v1"


@dataclass(frozen=True)
class RagContext:
    question: str
    retrieved: list[RetrievalResult]


def format_context(question: str, retrieved: list[RetrievalResult]) -> str:
    """Format retrieved records as compact, evidence-aware context."""

    blocks: list[str] = []
    for index, result in enumerate(retrieved, start=1):
        record = result.record
        evidence_lines = [
            (
                f"- {item.field}: {item.value} "
                f"(source={item.source}; confidence={item.confidence}; supports={item.supports})"
            )
            for item in record.evidence_items[:3]
        ]
        limitation_lines = [f"- {item}" for item in record.limitations[:3]]
        blocks.append(
            "\n".join(
                [
                    f"[{index}] {record.dataset_id}",
                    f"canonical_dataset_id: {record.canonical_dataset_id}",
                    f"source: {record.source}",
                    f"title: {record.title}",
                    f"source_url: {record.source_url}",
                    f"match_level: {match_level(question, record)}",
                    f"retrieval_score: {result.score:.1f}",
                    f"matched_terms: {', '.join(result.matched_terms)}",
                    f"diseases: {', '.join(record.diseases)}",
                    f"cancer_types: {', '.join(record.cancer_types)}",
                    f"primary_sites: {', '.join(record.primary_sites)}",
                    f"data_types: {', '.join(record.data_types)}",
                    f"has_clinical: {record.has_clinical}",
                    f"has_expression: {record.has_expression}",
                    f"has_mutation: {record.has_mutation}",
                    f"has_copy_number: {record.has_copy_number}",
                    f"biomarker_notes: {record.biomarker_notes}",
                    "evidence_items:",
                    "\n".join(evidence_lines) if evidence_lines else "- none",
                    "limitations:",
                    "\n".join(limitation_lines) if limitation_lines else "- none",
                ]
            )
        )
    return "\n\n".join(blocks)


def build_prompt(question: str, context: str) -> str:
    """Build the grounded prompt used for the LLM answer."""

    return "\n".join(
        [
            "You are a biomedical dataset discovery assistant.",
            "",
            "Task:",
            "Answer the user's dataset-discovery question using only the provided catalog context.",
            "",
            "Rules:",
            "- Do not provide medical advice, treatment recommendations, diagnosis, or prognosis.",
            "- Do not claim that a dataset has confirmed gene, mutation, or variant-positive cases unless the context explicitly says so.",
            "- Do not use outside biomedical knowledge to fill missing catalog evidence.",
            "- Distinguish candidate relevance from confirmed evidence.",
            "- Mention important limitations, especially missing KRAS G12C or gene-specific case counts.",
            "- Prefer dataset IDs, source systems, evidence, and source URLs over general biomedical background.",
            "- Cite catalog entries by bracket number, for example [1] or [2], when explaining evidence.",
            "- If the user asks whether a named dataset can answer a scoped question, answer directly before listing alternatives.",
            "- If the catalog does not support an answer, say what is missing instead of guessing.",
            "",
            "Output format:",
            "1. Short answer",
            "2. Candidate datasets",
            "3. Evidence and limitations",
            "4. Recommended follow-up checks",
            "",
            f"User question:\n{question}",
            "",
            f"Catalog context:\n{context}",
        ]
    )


def retrieve_context(
    question: str,
    catalog_path: str = DEFAULT_CATALOG_PATH,
    top_k: int = 4,
) -> RagContext:
    records = load_catalog(catalog_path)
    return RagContext(question=question, retrieved=search(question, records, top_k=top_k))


def _extract_response_text(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]

    output = payload.get("output", [])
    parts: list[str] = []
    for item in output if isinstance(output, list) else []:
        for content in item.get("content", []) if isinstance(item, dict) else []:
            if isinstance(content, dict):
                text = content.get("text")
                if isinstance(text, str):
                    parts.append(text)
    return "\n".join(parts).strip()


def call_openai_responses_api(
    prompt: str,
    model: str = DEFAULT_MODEL,
    timeout: int = 60,
) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Use --dry-run or set the key.")

    base_url = os.environ.get("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL).rstrip("/")
    request = Request(
        f"{base_url}/responses",
        data=json.dumps({"model": model, "input": prompt}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310 - configured API endpoint
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI API request failed: {error.code} {body}") from error
    except URLError as error:
        raise RuntimeError(f"OpenAI API request failed: {error}") from error

    text = _extract_response_text(payload)
    if not text:
        raise RuntimeError("OpenAI API response did not contain output text.")
    return text


def run_rag(
    question: str,
    catalog_path: str = DEFAULT_CATALOG_PATH,
    top_k: int = 4,
    model: str = DEFAULT_MODEL,
    live: bool = False,
    show_prompt: bool = False,
) -> str:
    context = retrieve_context(question, catalog_path=catalog_path, top_k=top_k)
    if not context.retrieved:
        return generate_answer(question, top_k=top_k, catalog_path=catalog_path)

    formatted_context = format_context(question, context.retrieved)
    prompt = build_prompt(question, formatted_context)

    if show_prompt:
        return prompt

    if live:
        return call_openai_responses_api(prompt, model=model)

    fallback = generate_answer(question, top_k=top_k, catalog_path=catalog_path)
    return "\n".join(
        [
            "DRY RUN: LLM call was not executed.",
            f"Model configured for live mode: {model}",
            "",
            "Prompt preview:",
            prompt,
            "",
            "Deterministic fallback answer:",
            fallback,
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--catalog", default=DEFAULT_CATALOG_PATH)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--show-prompt", action="store_true")
    args = parser.parse_args()

    print(
        run_rag(
            args.question,
            catalog_path=args.catalog,
            top_k=args.top_k,
            model=args.model,
            live=args.live,
            show_prompt=args.show_prompt,
        )
    )


if __name__ == "__main__":
    main()
