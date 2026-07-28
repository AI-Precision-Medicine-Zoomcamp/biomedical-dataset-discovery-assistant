import unittest

from evaluation.answer_eval import evaluate_answer_text


class AnswerEvalTest(unittest.TestCase):
    def test_answer_eval_passes_grounded_candidate_answer(self) -> None:
        question = {
            "id": "q",
            "question": "What datasets are available for KRAS G12C research in NSCLC?",
            "expected_dataset_ids": ["gdc:TCGA-LUAD"],
            "expected_absent_dataset_ids": ["gdc:TCGA-BRCA"],
            "expected_keywords": ["KRAS G12C", "NSCLC"],
        }
        answer = (
            "gdc:TCGA-LUAD is a candidate NSCLC dataset for KRAS G12C research. "
            "Evidence source: GDC metadata. Limitation: KRAS G12C-positive case "
            "counts are not verified."
        )

        result = evaluate_answer_text(question, answer)

        self.assertTrue(result["passed"])

    def test_answer_eval_fails_absent_dataset_leak(self) -> None:
        question = {
            "id": "q",
            "question": "Which NSCLC datasets are relevant?",
            "expected_dataset_ids": ["gdc:TCGA-LUAD"],
            "expected_absent_dataset_ids": ["gdc:TCGA-BRCA"],
            "expected_keywords": ["NSCLC"],
        }
        answer = (
            "gdc:TCGA-LUAD and gdc:TCGA-BRCA are candidate NSCLC datasets. "
            "Evidence source: catalog. Limitation: not verified."
        )

        result = evaluate_answer_text(question, answer)

        self.assertFalse(result["passed"])
        self.assertFalse(result["absent_hit"])

    def test_answer_eval_accepts_canonical_id_for_positive_match(self) -> None:
        question = {
            "id": "q",
            "question": "Which public datasets are available for lung adenocarcinoma?",
            "expected_dataset_ids": ["gdc:TCGA-LUAD"],
            "expected_absent_dataset_ids": ["gdc:TCGA-BRCA"],
            "expected_keywords": ["LUAD"],
        }
        answer = (
            "TCGA-LUAD is a candidate LUAD dataset. "
            "Evidence source: GDC metadata. Limitation: variant-positive cases are not verified."
        )

        result = evaluate_answer_text(question, answer)

        self.assertTrue(result["dataset_hit"])
        self.assertTrue(result["absent_hit"])
        self.assertTrue(result["passed"])


if __name__ == "__main__":
    unittest.main()
