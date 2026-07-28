import unittest
from unittest.mock import patch

from evaluation.rag_live_eval import evaluate_rag_outputs


class RagLiveEvalTest(unittest.TestCase):
    def test_default_eval_uses_deterministic_answers(self) -> None:
        report = evaluate_rag_outputs(
            catalog_path="data/processed/seed_catalog.json",
            questions_path="eval/questions_seed.json",
            limit=1,
        )

        self.assertEqual("deterministic_fallback", report["answer_mode"])
        self.assertEqual("local_heuristic_judge", report["judge_mode"])
        self.assertEqual(1, report["questions"])
        self.assertIn("relevance", report["average_scores"])

    def test_live_answer_mode_uses_rag_runner(self) -> None:
        with patch(
            "evaluation.rag_live_eval.run_rag",
            return_value=(
                "gdc:TCGA-LUAD is a candidate NSCLC dataset. "
                "Evidence source: catalog. Limitation: variant-positive cases are not verified."
            ),
        ) as run_rag_mock:
            report = evaluate_rag_outputs(
                catalog_path="data/processed/seed_catalog.json",
                questions_path="eval/questions_seed.json",
                limit=1,
                live_answers=True,
            )

        self.assertEqual("live_llm_rag", report["answer_mode"])
        run_rag_mock.assert_called_once()

    def test_eval_can_filter_questions_by_id(self) -> None:
        report = evaluate_rag_outputs(
            catalog_path="data/processed/seed_catalog.json",
            questions_path="eval/questions_seed.json",
            ids=["q008", "q013"],
        )

        self.assertEqual(2, report["questions"])
        self.assertEqual(["q008", "q013"], [item["id"] for item in report["results"]])


if __name__ == "__main__":
    unittest.main()
