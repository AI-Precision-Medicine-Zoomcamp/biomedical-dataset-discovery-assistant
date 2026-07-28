import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from src.api import (
    ask_payload,
    feedback_payload,
    feedback_summary_payload,
    render_home_page,
    render_monitoring_page,
    search_payload,
)


class ApiTest(unittest.TestCase):
    def test_search_payload_returns_catalog_results(self) -> None:
        payload = search_payload(
            "Which public datasets exist for NSCLC?",
            catalog_path="data/processed/seed_catalog.json",
            top_k=2,
        )

        self.assertTrue(payload["ok"])
        self.assertEqual(2, len(payload["results"]))
        self.assertIn("dataset_id", payload["results"][0])

    def test_ask_payload_returns_answer_and_trace(self) -> None:
        payload = ask_payload(
            "What datasets are available for KRAS G12C research in NSCLC?",
            catalog_path="data/processed/seed_catalog.json",
            top_k=2,
        )

        self.assertTrue(payload["ok"])
        self.assertIn("answer", payload)
        self.assertIn("tool_trace", payload)
        self.assertEqual(
            ["search_catalog", "get_dataset_details", "generate_grounded_answer"],
            [item["name"] for item in payload["tool_trace"]],
        )

    def test_empty_question_is_rejected(self) -> None:
        self.assertFalse(search_payload(" ")["ok"])
        self.assertFalse(ask_payload("")["ok"])

    def test_feedback_payload_writes_jsonl_event(self) -> None:
        with TemporaryDirectory() as tmpdir:
            feedback_path = Path(tmpdir) / "feedback.jsonl"

            payload = feedback_payload(
                {
                    "question": "Which datasets exist for NSCLC?",
                    "rating": 5,
                    "answer_id": "demo-answer",
                    "comment": "Useful answer.",
                },
                feedback_path=feedback_path,
            )

            self.assertTrue(payload["ok"])
            self.assertTrue(feedback_path.exists())
            self.assertIn("Useful answer", feedback_path.read_text(encoding="utf-8"))

    def test_feedback_payload_rejects_invalid_events(self) -> None:
        self.assertFalse(feedback_payload({"question": "", "rating": 5})["ok"])
        self.assertFalse(
            feedback_payload(
                {"question": "Which datasets exist for NSCLC?", "rating": 6}
            )["ok"]
        )

    def test_feedback_summary_payload_returns_monitoring_metrics(self) -> None:
        with TemporaryDirectory() as tmpdir:
            feedback_path = Path(tmpdir) / "feedback.jsonl"

            feedback_payload(
                {"question": "Which datasets exist for NSCLC?", "rating": 5},
                feedback_path=feedback_path,
            )
            feedback_payload(
                {
                    "question": "Any melanoma datasets?",
                    "rating": 2,
                    "comment": "Missed source evidence.",
                },
                feedback_path=feedback_path,
            )

            payload = feedback_summary_payload(feedback_path=feedback_path)

            self.assertTrue(payload["ok"])
            self.assertEqual(2, payload["total_events"])
            self.assertEqual(3.5, payload["average_rating"])
            self.assertEqual(0.5, payload["positive_rate"])
            self.assertEqual(1, payload["low_rating_count"])
            self.assertEqual(1, payload["rating_counts"]["5"])
            self.assertEqual(2, len(payload["recent_events"]))

    def test_render_home_page_contains_reviewer_ui_controls(self) -> None:
        html = render_home_page("data/processed/catalog.json")

        self.assertIn("Biomedical Dataset Discovery Assistant", html)
        self.assertIn("/ask", html)
        self.assertIn("/feedback", html)
        self.assertIn("Retrieved datasets", html)

    def test_render_monitoring_page_contains_feedback_summary_controls(self) -> None:
        html = render_monitoring_page()

        self.assertIn("Monitoring", html)
        self.assertIn("/feedback/summary", html)
        self.assertIn("Recent Feedback", html)


if __name__ == "__main__":
    unittest.main()
