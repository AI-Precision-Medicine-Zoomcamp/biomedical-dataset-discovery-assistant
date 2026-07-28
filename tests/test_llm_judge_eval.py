import unittest

from evaluation.llm_judge_eval import (
    build_judge_prompt,
    evaluate_with_judge,
    parse_judge_response,
)


class LlmJudgeEvalTest(unittest.TestCase):
    def test_build_judge_prompt_contains_safety_and_expected_ids(self) -> None:
        question = {
            "id": "q",
            "question": "What datasets are available for KRAS G12C research in NSCLC?",
            "expected_dataset_ids": ["gdc:TCGA-LUAD"],
            "expected_absent_dataset_ids": ["gdc:TCGA-BRCA"],
            "expected_keywords": ["KRAS G12C", "NSCLC"],
            "answer_checks": ["labels uncertainty"],
        }

        prompt = build_judge_prompt(question, "candidate answer")

        self.assertIn("not allowed to provide medical advice", prompt)
        self.assertIn("gdc:TCGA-LUAD", prompt)
        self.assertIn("gdc:TCGA-BRCA", prompt)
        self.assertIn('"relevance"', prompt)

    def test_parse_judge_response_normalizes_scores(self) -> None:
        payload = parse_judge_response(
            """
            {
              "relevance": 5,
              "groundedness": 4,
              "uncertainty": 5,
              "safety": 5,
              "usefulness": 4,
              "passed": true,
              "rationale": "Grounded and safe."
            }
            """
        )

        self.assertTrue(payload["passed"])
        self.assertEqual(5, payload["relevance"])
        self.assertEqual("Grounded and safe.", payload["rationale"])

    def test_evaluate_with_local_judge_returns_scores(self) -> None:
        report = evaluate_with_judge(
            catalog_path="data/processed/seed_catalog.json",
            questions_path="eval/questions_seed.json",
            limit=1,
        )

        self.assertEqual("local_heuristic_judge", report["mode"])
        self.assertEqual(1, report["questions"])
        self.assertIn("relevance", report["average_scores"])
        self.assertIn("judge", report["results"][0])


if __name__ == "__main__":
    unittest.main()
