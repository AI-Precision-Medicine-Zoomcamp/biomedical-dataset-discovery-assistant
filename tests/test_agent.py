import unittest

from src.agent import run_agent
from src.tools import get_dataset_details, search_catalog


class AgentTest(unittest.TestCase):
    def test_search_catalog_tool_returns_dataset_results(self) -> None:
        result = search_catalog(
            "What datasets are available for KRAS G12C research in NSCLC?",
            catalog_path="data/processed/seed_catalog.json",
            top_k=2,
        )

        self.assertEqual("search_catalog", result.name)
        self.assertEqual(2, len(result.output["results"]))
        self.assertIn("dataset_id", result.output["results"][0])

    def test_dataset_details_tool_marks_missing_ids(self) -> None:
        result = get_dataset_details(
            ["gdc:TCGA-LUAD", "missing:DATASET"],
            catalog_path="data/processed/seed_catalog.json",
            question="KRAS G12C NSCLC datasets",
        )

        self.assertTrue(result.output["details"][0]["found"])
        self.assertEqual("medium", result.output["details"][0]["match_level"])
        self.assertFalse(result.output["details"][1]["found"])

    def test_agent_returns_answer_and_tool_trace(self) -> None:
        result = run_agent(
            "What datasets are available for KRAS G12C research in NSCLC?",
            catalog_path="data/processed/seed_catalog.json",
            top_k=2,
        )

        self.assertIn("final_answer", result)
        self.assertIn("tool_trace", result)
        self.assertEqual(
            ["search_catalog", "get_dataset_details", "generate_grounded_answer"],
            [item["name"] for item in result["tool_trace"]],
        )
        self.assertTrue(result["tool_trace"][-1]["input"]["uses_dataset_details"])
        self.assertIn("Tool-grounded candidate dataset records", result["final_answer"])
        self.assertIn("not clinical recommendations", result["final_answer"])


if __name__ == "__main__":
    unittest.main()
