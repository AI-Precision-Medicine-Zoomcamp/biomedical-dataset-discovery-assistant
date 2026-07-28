import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.build_catalog import build_catalog, transform_cbioportal_study, write_catalog
from scripts.build_catalog import transform_gdc_project
from scripts.ingest_cbioportal import (
    DEFAULT_LIVE_OUTPUT_PATH as DEFAULT_CBIOPORTAL_LIVE_OUTPUT_PATH,
    DEFAULT_OUTPUT_PATH as DEFAULT_CBIOPORTAL_OUTPUT_PATH,
    DEFAULT_STUDY_IDS,
    DEFAULT_TCGA_STUDY_IDS,
    normalize_cbioportal_study_response,
    select_live_study_ids,
    select_output_path as select_cbioportal_output_path,
    write_raw_extract as write_cbioportal_raw,
)
from scripts.ingest_gdc import (
    DEFAULT_LIVE_OUTPUT_PATH,
    DEFAULT_OUTPUT_PATH,
    DEFAULT_PROJECT_IDS,
    DEFAULT_TCGA_PROJECT_IDS,
    normalize_gdc_project_response,
    select_live_project_ids,
    select_output_path,
    write_raw_extract as write_gdc_raw,
)
from scripts.validate_catalog import validate_catalog


class PipelineTest(unittest.TestCase):
    def test_seed_pipeline_builds_valid_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            gdc_raw = root / "raw" / "gdc.json"
            cbioportal_raw = root / "raw" / "cbioportal.json"
            catalog_path = root / "processed" / "catalog.json"

            write_gdc_raw(gdc_raw)
            write_cbioportal_raw(cbioportal_raw)
            records = build_catalog(gdc_raw, cbioportal_raw)
            write_catalog(records, catalog_path)

            self.assertEqual(6, len(records))
            self.assertEqual([], validate_catalog(catalog_path))

    def test_normalize_cbioportal_study_response_maps_live_metadata(self) -> None:
        study_response = {
            "studyId": "skcm_tcga_pan_can_atlas_2018",
            "name": "Skin Cutaneous Melanoma (TCGA, PanCancer Atlas)",
            "allSampleCount": 470,
            "pmid": "29625048,29596782",
            "citation": "TCGA, Cell 2018",
            "cancerType": {
                "id": "skcm",
                "name": "Skin Cutaneous Melanoma",
                "shortName": "SKCM",
            },
        }
        molecular_profiles = [
            {"molecularAlterationType": "MUTATION_EXTENDED"},
            {"molecularAlterationType": "COPY_NUMBER_ALTERATION"},
            {"molecularAlterationType": "MRNA_EXPRESSION"},
            {"genericAssayType": "METHYLATION"},
        ]

        record = normalize_cbioportal_study_response(
            "skcm_tcga_pan_can_atlas_2018",
            study_response,
            molecular_profiles,
        )

        self.assertEqual("TCGA-SKCM", record["canonical_dataset_id"])
        self.assertEqual("skin", record["primary_site"])
        self.assertIn("Skin Cutaneous Melanoma", record["cancer_types"])
        self.assertIn("mutation", record["data_types"])
        self.assertIn("mRNA expression", record["data_types"])
        self.assertIn("copy number", record["data_types"])
        self.assertIn("methylation", record["data_types"])
        self.assertEqual(470, record["sample_count"])
        self.assertEqual(["29625048", "29596782"], record["publication_ids"])

    def test_normalize_cbioportal_study_response_uses_short_name_for_canonical_id(self) -> None:
        study_response = {
            "studyId": "acc_tcga_pan_can_atlas_2018",
            "name": "Adrenocortical Carcinoma (TCGA, PanCancer Atlas)",
            "allSampleCount": 92,
            "cancerType": {
                "id": "acc",
                "name": "Adrenocortical Carcinoma",
                "shortName": "ACC",
            },
        }

        record = normalize_cbioportal_study_response(
            "acc_tcga_pan_can_atlas_2018",
            study_response,
            [{"molecularAlterationType": "MUTATION_EXTENDED"}],
        )

        self.assertEqual("TCGA-ACC", record["canonical_dataset_id"])

    def test_cbioportal_live_selection_supports_default_tcga_panel(self) -> None:
        self.assertEqual(DEFAULT_STUDY_IDS, select_live_study_ids(None))
        self.assertEqual(
            DEFAULT_TCGA_STUDY_IDS,
            select_live_study_ids(None, use_tcga_defaults=True),
        )
        self.assertEqual(
            ["skcm_tcga_pan_can_atlas_2018"],
            select_live_study_ids(
                ["skcm_tcga_pan_can_atlas_2018"],
                use_tcga_defaults=True,
            ),
        )

    def test_cbioportal_live_selection_can_discover_all_tcga_studies(self) -> None:
        with patch(
            "scripts.ingest_cbioportal.fetch_tcga_pan_can_atlas_study_ids",
            return_value=["acc_tcga_pan_can_atlas_2018"],
        ):
            self.assertEqual(
                ["acc_tcga_pan_can_atlas_2018"],
                select_live_study_ids(None, use_all_tcga=True),
            )
            self.assertEqual(
                ["skcm_tcga_pan_can_atlas_2018"],
                select_live_study_ids(
                    ["skcm_tcga_pan_can_atlas_2018"],
                    use_tcga_defaults=True,
                    use_all_tcga=True,
                ),
            )

    def test_cbioportal_live_mode_uses_separate_default_output_path(self) -> None:
        self.assertEqual(
            DEFAULT_CBIOPORTAL_LIVE_OUTPUT_PATH,
            select_cbioportal_output_path(DEFAULT_CBIOPORTAL_OUTPUT_PATH, live=True),
        )
        self.assertEqual(
            DEFAULT_CBIOPORTAL_OUTPUT_PATH,
            select_cbioportal_output_path(DEFAULT_CBIOPORTAL_OUTPUT_PATH, live=False),
        )

    def test_normalize_gdc_project_response_preserves_live_metadata(self) -> None:
        response = {
            "project_id": "TCGA-LUAD",
            "name": "TCGA Lung Adenocarcinoma",
            "primary_site": "Lung",
            "program": {"name": "TCGA"},
            "summary": {
                "data_categories": [
                    {"data_category": "Clinical"},
                    {"data_category": "Simple Nucleotide Variation"},
                ],
                "experimental_strategies": [
                    {"experimental_strategy": "RNA-Seq"},
                    {"experimental_strategy": "WXS"},
                ],
            },
        }
        seed = {
            "disease_terms": ["non-small cell lung cancer"],
            "cancer_types": ["lung adenocarcinoma", "LUAD"],
            "cohort_tags": ["NSCLC"],
            "limitations": ["Variant-positive cases are not verified."],
        }

        record = normalize_gdc_project_response("TCGA-LUAD", response, seed)

        self.assertEqual("TCGA-LUAD", record["project_id"])
        self.assertEqual("TCGA", record["program"])
        self.assertEqual("Lung", record["primary_site"])
        self.assertEqual(
            ["Clinical", "Simple Nucleotide Variation"],
            record["data_categories"],
        )
        self.assertEqual(["RNA-Seq", "WXS"], record["experimental_strategies"])
        self.assertEqual(["non-small cell lung cancer"], record["disease_terms"])
        self.assertEqual(response, record["api_response"])

    def test_normalize_gdc_project_response_adds_generic_live_limitations(self) -> None:
        response = {
            "project_id": "TCGA-COAD",
            "name": "TCGA Colon Adenocarcinoma",
            "primary_site": "Colon",
            "program": {"name": "TCGA"},
            "summary": {
                "data_categories": [{"data_category": "Clinical"}],
                "experimental_strategies": [],
            },
        }

        record = normalize_gdc_project_response("TCGA-COAD", response)

        self.assertEqual(["Colon"], record["disease_terms"])
        self.assertEqual(["TCGA Colon Adenocarcinoma"], record["cancer_types"])
        self.assertIn("TCGA", record["cohort_tags"])
        self.assertTrue(record["limitations"])

    def test_normalize_gdc_project_response_chooses_name_matching_primary_site(self) -> None:
        response = {
            "project_id": "TCGA-SKCM",
            "name": "Skin Cutaneous Melanoma",
            "primary_site": ["Colon", "Skin", "Brain"],
            "disease_type": ["Nevi and Melanomas"],
            "program": {"name": "TCGA"},
            "summary": {"data_categories": [], "experimental_strategies": []},
        }

        record = normalize_gdc_project_response("TCGA-SKCM", response)

        self.assertEqual("Skin", record["primary_site"])
        self.assertEqual(["Nevi and Melanomas"], record["disease_terms"])

    def test_live_project_selection_supports_default_tcga_panel(self) -> None:
        self.assertEqual(DEFAULT_PROJECT_IDS, select_live_project_ids(None))
        self.assertEqual(
            DEFAULT_TCGA_PROJECT_IDS,
            select_live_project_ids(None, use_tcga_defaults=True),
        )

    def test_live_project_selection_can_discover_all_gdc_projects(self) -> None:
        with patch(
            "scripts.ingest_gdc.fetch_project_ids",
            return_value=["BEATAML1.0-COHORT", "TCGA-LUAD"],
        ):
            self.assertEqual(
                ["BEATAML1.0-COHORT", "TCGA-LUAD"],
                select_live_project_ids(None, use_all_projects=True),
            )
            self.assertEqual(
                ["TCGA-SKCM"],
                select_live_project_ids(
                    ["TCGA-SKCM"],
                    use_all_tcga=True,
                    use_all_projects=True,
                ),
            )
        self.assertEqual(
            ["TCGA-OV"],
            select_live_project_ids(["TCGA-OV"], use_tcga_defaults=True),
        )

    def test_live_project_selection_can_discover_all_tcga_projects(self) -> None:
        with patch(
            "scripts.ingest_gdc.fetch_tcga_project_ids",
            return_value=["TCGA-ACC"],
        ):
            self.assertEqual(
                ["TCGA-ACC"],
                select_live_project_ids(None, use_all_tcga=True),
            )
            self.assertEqual(
                ["TCGA-OV"],
                select_live_project_ids(
                    ["TCGA-OV"],
                    use_tcga_defaults=True,
                    use_all_tcga=True,
                ),
            )

    def test_live_project_selection_supports_limit_for_broad_runs(self) -> None:
        with patch(
            "scripts.ingest_gdc.fetch_project_ids",
            return_value=["PROJECT-001", "PROJECT-002", "PROJECT-003"],
        ):
            self.assertEqual(
                ["PROJECT-001", "PROJECT-002"],
                select_live_project_ids(None, use_all_projects=True, limit=2),
            )

    def test_live_mode_uses_separate_default_output_path(self) -> None:
        self.assertEqual(
            DEFAULT_LIVE_OUTPUT_PATH,
            select_output_path(DEFAULT_OUTPUT_PATH, live=True),
        )
        self.assertEqual(
            DEFAULT_OUTPUT_PATH,
            select_output_path(DEFAULT_OUTPUT_PATH, live=False),
        )

    def test_gdc_transform_keeps_clinical_flags_consistent(self) -> None:
        raw_record = {
            "project_id": "TCGA-TEST",
            "name": "TCGA Test",
            "primary_site": "Lung",
            "data_categories": ["Simple Nucleotide Variation"],
            "experimental_strategies": ["WXS"],
            "disease_terms": ["test disease"],
            "cancer_types": ["test cancer"],
            "cohort_tags": [],
            "limitations": ["Clinical metadata was not present in this fixture."],
        }

        record = transform_gdc_project(raw_record)

        self.assertNotIn("clinical", record["data_types"])
        self.assertFalse(record["has_clinical"])
        self.assertIn("mutation", record["data_types"])
        self.assertTrue(record["has_mutation"])

    def test_cbioportal_transform_repairs_legacy_canonical_fallback(self) -> None:
        record = transform_cbioportal_study(
            {
                "study_id": "acc_tcga_pan_can_atlas_2018",
                "canonical_dataset_id": "cbioportal:acc_tcga_pan_can_atlas_2018",
                "name": "Adrenocortical Carcinoma (TCGA, PanCancer Atlas)",
                "primary_site": "adrenal gland",
                "disease_terms": ["Adrenocortical Carcinoma"],
                "cancer_types": ["Adrenocortical Carcinoma", "ACC"],
                "cohort_tags": ["TCGA", "cBioPortal"],
                "molecular_profiles": ["mutation extended"],
                "limitations": ["Study-level metadata only."],
            }
        )

        self.assertEqual("TCGA-ACC", record["canonical_dataset_id"])
        self.assertIn("TCGA-ACC", record["external_ids"])


if __name__ == "__main__":
    unittest.main()
