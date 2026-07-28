import unittest

from evaluation.evaluation_report import build_evaluation_report, render_markdown


class EvaluationReportTest(unittest.TestCase):
    def test_report_combines_retrieval_answer_and_claim_checks(self) -> None:
        report = build_evaluation_report(
            catalog_path="data/processed/catalog.json",
            questions_path="eval/questions_seed.json",
            limit=1,
        )

        self.assertEqual(1, report["questions"])
        self.assertEqual(1.0, report["pass_rate"])
        result = report["results"][0]
        self.assertIn("retrieval_checks", result)
        self.assertIn("answer_checks", result)
        self.assertIn("claim_checks", result)
        self.assertIn("answer_excerpt", result)

    def test_markdown_report_explains_why_case_passed(self) -> None:
        report = build_evaluation_report(
            catalog_path="data/processed/catalog.json",
            questions_path="eval/questions_seed.json",
            limit=1,
        )

        markdown = render_markdown(report)

        self.assertIn("Expected datasets", markdown)
        self.assertIn("Retrieved datasets", markdown)
        self.assertIn("Retrieval checks", markdown)
        self.assertIn("Answer checks", markdown)
        self.assertIn("Claim checks", markdown)
        self.assertIn("Answer excerpt", markdown)


if __name__ == "__main__":
    unittest.main()
