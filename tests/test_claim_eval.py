import unittest

from evaluation.claim_eval import verify_answer_claims


class ClaimEvalTest(unittest.TestCase):
    def test_claim_eval_passes_candidate_answer_with_uncertainty(self) -> None:
        question = {
            "id": "q",
            "question": "What datasets are available for KRAS G12C research in NSCLC?",
            "expected_dataset_ids": ["gdc:TCGA-LUAD"],
            "expected_absent_dataset_ids": ["gdc:TCGA-BRCA"],
        }
        answer = (
            "TCGA-LUAD is a candidate dataset from GDC for KRAS G12C research in NSCLC. "
            "Limitation: KRAS G12C-positive case counts are not verified."
        )

        result = verify_answer_claims(question, answer)

        self.assertTrue(result["passed"])
        self.assertEqual([], result["failures"])

    def test_claim_eval_fails_unsupported_confirmed_variant_claim(self) -> None:
        question = {
            "id": "q",
            "question": "What datasets are available for KRAS G12C research in NSCLC?",
            "expected_dataset_ids": ["gdc:TCGA-LUAD"],
            "expected_absent_dataset_ids": [],
        }
        answer = (
            "gdc:TCGA-LUAD has confirmed KRAS G12C-positive cases for NSCLC research."
        )

        result = verify_answer_claims(question, answer)

        self.assertFalse(result["passed"])
        self.assertEqual(
            "unsupported_variant_or_case_count_claim",
            result["failures"][0]["type"],
        )

    def test_claim_eval_fails_absent_dataset_leak(self) -> None:
        question = {
            "id": "q",
            "question": "Which NSCLC datasets are relevant?",
            "expected_dataset_ids": ["gdc:TCGA-LUAD"],
            "expected_absent_dataset_ids": ["gdc:TCGA-BRCA"],
        }
        answer = "gdc:TCGA-LUAD and gdc:TCGA-BRCA are both relevant NSCLC datasets."

        result = verify_answer_claims(question, answer)

        self.assertFalse(result["passed"])
        self.assertEqual("absent_dataset_leak", result["failures"][0]["type"])

    def test_claim_eval_respects_min_expected_dataset_hits(self) -> None:
        question = {
            "id": "q",
            "question": "Which datasets include methylation profiles in cBioPortal?",
            "expected_dataset_ids": [
                "cbioportal:uvm_tcga_pan_can_atlas_2018",
                "cbioportal:ucs_tcga_pan_can_atlas_2018",
                "cbioportal:thym_tcga_pan_can_atlas_2018",
            ],
            "min_expected_dataset_hits": 1,
            "expected_absent_dataset_ids": ["gdc:TCGA-LUAD"],
        }
        answer = (
            "cbioportal:thym_tcga_pan_can_atlas_2018 is a cBioPortal candidate "
            "with methylation profile metadata. Limitation: patient-level analysis "
            "was not performed."
        )

        result = verify_answer_claims(question, answer)

        self.assertTrue(result["passed"])


if __name__ == "__main__":
    unittest.main()
