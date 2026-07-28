import unittest

from src.answer import generate_answer, match_level
from src.catalog import load_catalog


class AnswerTest(unittest.TestCase):
    def test_kras_g12c_answer_labels_uncertainty(self) -> None:
        answer = generate_answer(
            "What datasets are available for KRAS G12C research in NSCLC?",
            top_k=2,
        )

        self.assertIn("Match level: medium", answer)
        self.assertIn("not clinical recommendations", answer)
        self.assertIn("not verified", answer)

    def test_match_level_is_query_specific(self) -> None:
        records = load_catalog()
        luad = next(record for record in records if record.dataset_id == "gdc:TCGA-LUAD")

        self.assertEqual(
            "medium",
            match_level("KRAS G12C NSCLC datasets", luad),
        )
        self.assertEqual(
            "candidate",
            match_level("What public datasets exist for NSCLC?", luad),
        )

    def test_no_match_answer_is_explicit_about_catalog_scope(self) -> None:
        answer = generate_answer("Which melanoma proteomics datasets are loaded?")

        self.assertIn("No matching dataset records", answer)
        self.assertIn("prototype catalog", answer)


if __name__ == "__main__":
    unittest.main()
