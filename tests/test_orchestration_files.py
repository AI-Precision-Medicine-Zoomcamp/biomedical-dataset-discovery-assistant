import unittest
from pathlib import Path


class OrchestrationFilesTest(unittest.TestCase):
    def test_kestra_flow_mentions_pipeline_tasks(self) -> None:
        content = Path("flows/catalog_pipeline.yml").read_text(encoding="utf-8")

        for task_id in [
            "ingest_gdc",
            "ingest_cbioportal",
            "build_catalog",
            "validate_catalog",
            "retrieval_eval",
            "answer_eval",
        ]:
            self.assertIn(task_id, content)

    def test_airflow_dag_still_exists_as_optional_reference(self) -> None:
        self.assertTrue(Path("dags/catalog_pipeline_dag.py").exists())

    def test_docker_compose_serves_api_ui(self) -> None:
        content = Path("docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn("python -m src.api", content)
        self.assertIn("8000:8000", content)
        self.assertIn("/health", content)

    def test_makefile_has_reviewer_check_target(self) -> None:
        content = Path("Makefile").read_text(encoding="utf-8")

        self.assertIn("reviewer-check:", content)
        self.assertIn("REPORT_OUTPUT=docs/evaluation_report_seed.md", content)


if __name__ == "__main__":
    unittest.main()
