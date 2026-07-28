import unittest

from src.streamlit_app import _search_results


class StreamlitAppTest(unittest.TestCase):
    def test_search_results_extracts_catalog_output(self) -> None:
        result = {
            "tool_trace": [
                {
                    "name": "search_catalog",
                    "output": {"results": [{"dataset_id": "gdc:TCGA-LUAD"}]},
                },
                {"name": "generate_grounded_answer", "output": {"answer": "ok"}},
            ]
        }

        self.assertEqual(
            [{"dataset_id": "gdc:TCGA-LUAD"}],
            _search_results(result),
        )

    def test_search_results_returns_empty_list_without_search_tool(self) -> None:
        self.assertEqual([], _search_results({"tool_trace": []}))


if __name__ == "__main__":
    unittest.main()
