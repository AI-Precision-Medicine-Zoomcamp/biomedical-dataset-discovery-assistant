from src.catalog import group_by_canonical_id, load_catalog
from src.models import DatasetRecord
from src.retriever import search
from evaluation.retrieval_compare import compare_methods
from scripts.build_catalog import transform_gdc_project
import unittest


class RetrieverTest(unittest.TestCase):
    def test_nsclc_query_retrieves_lung_records(self) -> None:
        records = load_catalog()
        results = search("What public datasets exist for NSCLC?", records, top_k=5)
        result_ids = {result.record.dataset_id for result in results}

        self.assertIn("gdc:TCGA-LUAD", result_ids)
        self.assertIn("gdc:TCGA-LUSC", result_ids)

    def test_cbioportal_query_prefers_cbioportal_records(self) -> None:
        records = load_catalog()
        results = search(
            "Which cBioPortal studies are relevant to NSCLC?",
            records,
            top_k=3,
            method="keyword",
        )

        self.assertTrue(results)
        self.assertEqual("cBioPortal", results[0].record.source)

    def test_breast_query_prefers_brca_records(self) -> None:
        records = load_catalog()
        results = search(
            "Which breast cancer comparison datasets are currently in the catalog?",
            records,
            top_k=2,
        )
        result_ids = {result.record.dataset_id for result in results}

        self.assertEqual(
            {
                "gdc:TCGA-BRCA",
                "cbioportal:brca_tcga_pan_can_atlas_2018",
            },
            result_ids,
        )

    def test_colon_query_prefers_colon_records_over_generic_cancer_matches(self) -> None:
        records = [
            DatasetRecord.from_dict(
                transform_gdc_project(
                    {
                        "project_id": "TCGA-COAD",
                        "name": "Colon Adenocarcinoma",
                        "primary_site": "Colon",
                        "data_categories": ["Clinical", "Simple Nucleotide Variation"],
                        "experimental_strategies": ["WXS"],
                        "disease_terms": ["Colon"],
                        "cancer_types": ["Colon Adenocarcinoma"],
                        "cohort_tags": ["TCGA"],
                        "limitations": ["Project-level metadata only."],
                    }
                )
            ),
            DatasetRecord.from_dict(
                transform_gdc_project(
                    {
                        "project_id": "TCGA-SKCM",
                        "name": "Skin Cutaneous Melanoma",
                        "primary_site": "Skin",
                        "data_categories": ["Clinical", "Simple Nucleotide Variation"],
                        "experimental_strategies": ["WXS"],
                        "disease_terms": ["Skin"],
                        "cancer_types": ["Skin Cutaneous Melanoma"],
                        "cohort_tags": ["TCGA"],
                        "limitations": ["Project-level metadata only."],
                    }
                )
            ),
            DatasetRecord.from_dict(
                transform_gdc_project(
                    {
                        "project_id": "TCGA-STAD",
                        "name": "Stomach Adenocarcinoma",
                        "primary_site": "Stomach",
                        "data_categories": ["Clinical", "Simple Nucleotide Variation"],
                        "experimental_strategies": ["WXS"],
                        "disease_terms": ["Stomach"],
                        "cancer_types": ["Stomach Adenocarcinoma"],
                        "cohort_tags": ["TCGA"],
                        "limitations": ["Project-level metadata only."],
                    }
                )
            ),
        ]

        results = search("What public datasets exist for colon cancer?", records, top_k=3)
        result_ids = {result.record.dataset_id for result in results}

        self.assertTrue(results)
        self.assertEqual("gdc:TCGA-COAD", results[0].record.dataset_id)
        self.assertNotIn("gdc:TCGA-SKCM", result_ids)
        self.assertNotIn("gdc:TCGA-STAD", result_ids)

    def test_negated_site_terms_are_excluded(self) -> None:
        records = [
            DatasetRecord.from_dict(
                transform_gdc_project(
                    {
                        "project_id": "TCGA-SKCM",
                        "name": "Skin Cutaneous Melanoma",
                        "primary_site": "Skin",
                        "data_categories": ["Simple Nucleotide Variation"],
                        "experimental_strategies": ["WXS"],
                        "disease_terms": ["Skin"],
                        "cancer_types": ["Skin Cutaneous Melanoma"],
                        "cohort_tags": ["TCGA"],
                        "limitations": ["Project-level metadata only."],
                    }
                )
            ),
            DatasetRecord.from_dict(
                transform_gdc_project(
                    {
                        "project_id": "TCGA-COAD",
                        "name": "Colon Adenocarcinoma",
                        "primary_site": "Colon",
                        "data_categories": ["Simple Nucleotide Variation"],
                        "experimental_strategies": ["WXS"],
                        "disease_terms": ["Colon"],
                        "cancer_types": ["Colon Adenocarcinoma"],
                        "cohort_tags": ["TCGA"],
                        "limitations": ["Project-level metadata only."],
                    }
                )
            ),
        ]

        results = search(
            "I want melanoma datasets with mutation data but not colorectal cancer cohorts.",
            records,
            top_k=2,
        )
        result_ids = {result.record.dataset_id for result in results}

        self.assertIn("gdc:TCGA-SKCM", result_ids)
        self.assertNotIn("gdc:TCGA-COAD", result_ids)

    def test_tfidf_search_is_available_as_baseline(self) -> None:
        records = load_catalog()
        results = search(
            "Which datasets are available for lung adenocarcinoma?",
            records,
            top_k=3,
            method="tfidf",
        )

        self.assertTrue(results)
        self.assertIn("luad", results[0].record.dataset_id.lower())

    def test_hybrid_search_keeps_source_specific_queries_clean(self) -> None:
        records = load_catalog()
        results = search(
            "Which cBioPortal studies provide mutation profiles for LUAD?",
            records,
            top_k=3,
            method="hybrid",
        )

        self.assertTrue(results)
        self.assertTrue(all(result.record.source == "cBioPortal" for result in results))

    def test_retrieval_compare_reports_best_method(self) -> None:
        report = compare_methods(
            catalog_path="data/processed/seed_catalog.json",
            questions_path="eval/questions_seed.json",
        )

        self.assertEqual("hybrid", report["best_method"])
        self.assertEqual(["keyword", "tfidf", "hybrid"], [item["method"] for item in report["reports"]])

    def test_related_source_views_group_by_canonical_dataset(self) -> None:
        records = load_catalog()
        grouped = group_by_canonical_id(records)

        self.assertEqual(
            {
                "gdc:TCGA-LUAD",
                "cbioportal:luad_tcga_pan_can_atlas_2018",
            },
            {record.dataset_id for record in grouped["TCGA-LUAD"]},
        )


if __name__ == "__main__":
    unittest.main()
