"""Streamlit reviewer UI for the biomedical dataset discovery assistant."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
load_dotenv(PROJECT_ROOT / ".env")

from src.agent import run_agent
from src.api import DEFAULT_FEEDBACK_PATH, feedback_payload, feedback_summary_payload
from src.rag import run_rag
from src.tools import DEFAULT_CATALOG_PATH


DEFAULT_QUESTION = "Are there public datasets for KRAS G12C NSCLC with RNA-seq data?"
DEFAULT_MODEL = "gpt-4o-mini"


def _search_results(agent_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract search results from an agent trace."""

    for item in agent_result.get("tool_trace", []):
        if item.get("name") == "search_catalog":
            return item.get("output", {}).get("results", [])
    return []


def _render_result_card(result: dict[str, Any]) -> None:
    source = result.get("source", "unknown")
    match = result.get("match_level", "candidate")
    st.markdown(f"#### {result['dataset_id']}")
    st.caption(f"{source} · match: {match} · score: {result.get('score', 0):.2f}")
    st.write(result.get("title", "Untitled dataset"))
    data_types = ", ".join(result.get("data_types", [])) or "Not specified"
    st.write(f"**Data types:** {data_types}")
    limitations = result.get("limitations", [])
    if limitations:
        st.warning(limitations[0], icon="⚠️")
    source_url = result.get("source_url")
    if source_url:
        st.link_button("Open source record", source_url)
    st.divider()


def _render_assistant(catalog_path: str) -> None:
    st.subheader("Dataset discovery")
    st.caption(
        "Search normalized GDC and cBioPortal metadata. Local reviewer mode does "
        "not require an API key; live mode uses the OpenAI Responses API."
    )

    with st.form("dataset_question"):
        question = st.text_area("Research question", value=DEFAULT_QUESTION, height=100)
        top_k = st.select_slider("Top K", options=[3, 4, 5], value=4)
        requested_mode = st.radio(
            "Answer mode",
            ["Local reviewer mode", "Live OpenAI RAG"],
            horizontal=True,
        )
        submitted = st.form_submit_button("Ask", type="primary")

    if submitted:
        if not question.strip():
            st.error("Enter a research question.")
        elif requested_mode == "Live OpenAI RAG" and not os.environ.get(
            "OPENAI_API_KEY"
        ):
            st.error(
                "OPENAI_API_KEY is not set. Choose Local reviewer mode or add "
                "the key to the environment."
            )
        else:
            with st.spinner("Searching the catalog and building a grounded answer..."):
                agent_result = run_agent(
                    question.strip(),
                    catalog_path=catalog_path,
                    top_k=top_k,
                )
                answer = agent_result["final_answer"]
                answer_mode = "deterministic local tool workflow"
                if requested_mode == "Live OpenAI RAG":
                    answer = run_rag(
                        question.strip(),
                        catalog_path=catalog_path,
                        top_k=top_k,
                        model=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL),
                        live=True,
                    )
                    answer_mode = "live OpenAI RAG"

            st.session_state["last_result"] = agent_result
            st.session_state["last_answer"] = answer
            st.session_state["last_question"] = question.strip()
            st.session_state["last_mode"] = answer_mode

    result = st.session_state.get("last_result")
    if not result:
        st.info("Ask a question to see a grounded answer and tool trace.")
        return

    answer_column, datasets_column = st.columns([1.15, 0.85], gap="large")
    with answer_column:
        st.markdown("### Grounded answer")
        st.caption(f"Mode: {st.session_state['last_mode']}")
        st.code(st.session_state["last_answer"], language=None, wrap_lines=True)

        st.markdown("### Tool trace")
        for index, item in enumerate(result["tool_trace"], start=1):
            with st.expander(f"{index}. {item['name']}"):
                st.json(
                    {
                        "input": item.get("input", {}),
                        "output": item.get("output", {}),
                    }
                )

        st.markdown("### Feedback")
        with st.form("answer_feedback", clear_on_submit=True):
            rating = st.select_slider("Rating", options=[1, 2, 3, 4, 5], value=5)
            comment = st.text_input("Optional comment")
            feedback_submitted = st.form_submit_button("Save feedback")
        if feedback_submitted:
            feedback_payload(
                {
                    "question": st.session_state["last_question"],
                    "rating": rating,
                    "comment": comment,
                    "source": "streamlit_ui",
                }
            )
            st.success("Feedback saved.")

    with datasets_column:
        st.markdown("### Retrieved datasets")
        for search_result in _search_results(result):
            _render_result_card(search_result)


def _render_monitoring(feedback_path: Path | str = DEFAULT_FEEDBACK_PATH) -> None:
    st.subheader("Feedback monitoring")
    st.caption(f"Feedback log: `{feedback_path}`")
    summary = feedback_summary_payload(feedback_path=feedback_path)

    metric_columns = st.columns(4)
    metric_columns[0].metric("Total feedback", summary["total_events"])
    metric_columns[1].metric(
        "Average rating",
        f"{summary['average_rating']:.2f}"
        if summary["average_rating"] is not None
        else "N/A",
    )
    metric_columns[2].metric(
        "Positive rate",
        f"{summary['positive_rate'] * 100:.0f}%"
        if summary["positive_rate"] is not None
        else "N/A",
    )
    metric_columns[3].metric("Low ratings", summary["low_rating_count"])

    st.markdown("### Rating distribution")
    chart_data = {
        "rating": [str(rating) for rating in range(1, 6)],
        "count": [
            summary["rating_counts"][str(rating)] for rating in range(1, 6)
        ],
    }
    st.bar_chart(chart_data, x="rating", y="count", horizontal=True)

    st.markdown("### Recent feedback")
    if not summary["recent_events"]:
        st.info("No feedback has been submitted yet.")
        return

    for event in summary["recent_events"]:
        with st.container(border=True):
            st.markdown(f"**Rating {event['rating']} · {event.get('source', 'unknown')}**")
            st.write(event.get("question", ""))
            if event.get("comment"):
                st.write(event["comment"])
            st.caption(event.get("created_at", ""))

    with st.expander("Raw monitoring payload"):
        st.code(json.dumps(summary, indent=2), language="json")


def main() -> None:
    st.set_page_config(
        page_title="Biomedical Dataset Discovery Assistant",
        page_icon="🧬",
        layout="wide",
        menu_items={
            "About": (
                "LLM Zoomcamp capstone: evidence-aware discovery of public "
                "biomedical datasets."
            )
        },
    )
    st.title("🧬 Biomedical Dataset Discovery Assistant")
    st.write(
        "Find candidate public biomedical datasets, inspect source evidence, "
        "and avoid unsupported mutation or case-count claims."
    )
    st.caption(f"Catalog: `{DEFAULT_CATALOG_PATH}`")

    assistant_tab, monitoring_tab = st.tabs(["Assistant", "Monitoring"])
    with assistant_tab:
        _render_assistant(DEFAULT_CATALOG_PATH)
    with monitoring_tab:
        _render_monitoring()


if __name__ == "__main__":
    main()
