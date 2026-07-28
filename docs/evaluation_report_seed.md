# Evaluation Report

This report combines retrieval checks, answer guardrails, and reverse claim verification.

## Summary

- Catalog: `data/processed/catalog.json`
- Questions: `eval/questions_seed.json`
- Retrieval method: `hybrid`
- Retrieval top-k: `5`
- Answer top-k: `4`
- Questions evaluated: `14`
- Overall pass rate: `1.00`

## Cases

### q001: PASS

Question: What public datasets exist for NSCLC?

Expected datasets:

- `gdc:TCGA-LUAD`
- `gdc:TCGA-LUSC`

Minimum expected hits: `2`

Expected absent datasets:

- none

Retrieved datasets:

- `cbioportal:lusc_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-LUSC` (expected)
- `cbioportal:luad_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-LUAD` (expected)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`

Answer excerpt:

```text
Question: What public datasets exist for NSCLC?
Candidate dataset records from the current catalog:
- cbioportal:lusc_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-LUSC)
  Match level: candidate
  Why it appears: Lung Squamous Cell Carcinoma TCGA PanCancer Atlas; data types: mutation, mRNA expression, clinical, copy number.
  Evidence:
  - molecular_profiles: mutations; mRNA expression; copy number alterations (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-LUSC (cBioPortal raw study extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.
  Source URL: https://www.cbioportal.org/study/summary?id=lusc_tcga_pan_can_atlas_2018
```

### q002: PASS

Question: Which public datasets are available for lung adenocarcinoma?

Expected datasets:

- `gdc:TCGA-LUAD`

Minimum expected hits: `1`

Expected absent datasets:

- none

Retrieved datasets:

- `cbioportal:luad_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-LUAD` (expected)
- `cbioportal:lusc_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-LUSC` (candidate)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`

Answer excerpt:

```text
Question: Which public datasets are available for lung adenocarcinoma?
Candidate dataset records from the current catalog:
- cbioportal:luad_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-LUAD)
  Match level: candidate
  Why it appears: Lung Adenocarcinoma TCGA PanCancer Atlas; data types: mutation, mRNA expression, clinical, copy number.
  Evidence:
  - molecular_profiles: mutations; mRNA expression; copy number alterations (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-LUAD (cBioPortal raw study extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.
  Source URL: https://www.cbioportal.org/study/summary?id=luad_tcga_pan_can_atlas_2018
```

### q003: PASS

Question: Which datasets are available for lung squamous cell carcinoma?

Expected datasets:

- `gdc:TCGA-LUSC`

Minimum expected hits: `1`

Expected absent datasets:

- none

Retrieved datasets:

- `cbioportal:lusc_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-LUSC` (expected)
- `cbioportal:luad_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-LUAD` (candidate)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`

Answer excerpt:

```text
Question: Which datasets are available for lung squamous cell carcinoma?
Candidate dataset records from the current catalog:
- cbioportal:lusc_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-LUSC)
  Match level: candidate
  Why it appears: Lung Squamous Cell Carcinoma TCGA PanCancer Atlas; data types: mutation, mRNA expression, clinical, copy number.
  Evidence:
  - molecular_profiles: mutations; mRNA expression; copy number alterations (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-LUSC (cBioPortal raw study extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.
  Source URL: https://www.cbioportal.org/study/summary?id=lusc_tcga_pan_can_atlas_2018
```

### q004: PASS

Question: Compare TCGA-LUAD and TCGA-LUSC.

Expected datasets:

- `gdc:TCGA-LUAD`
- `gdc:TCGA-LUSC`

Minimum expected hits: `2`

Expected absent datasets:

- none

Retrieved datasets:

- `cbioportal:luad_tcga_pan_can_atlas_2018` (candidate)
- `cbioportal:lusc_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-LUSC` (expected)
- `gdc:TCGA-LUAD` (expected)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`

Answer excerpt:

```text
Question: Compare TCGA-LUAD and TCGA-LUSC.
Candidate dataset records from the current catalog:
- cbioportal:luad_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-LUAD)
  Match level: candidate
  Why it appears: Lung Adenocarcinoma TCGA PanCancer Atlas; data types: mutation, mRNA expression, clinical, copy number.
  Evidence:
  - molecular_profiles: mutations; mRNA expression; copy number alterations (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-LUAD (cBioPortal raw study extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.
  Source URL: https://www.cbioportal.org/study/summary?id=luad_tcga_pan_can_atlas_2018
```

### q005: PASS

Question: Which datasets contain RNA-seq data for lung cancer?

Expected datasets:

- `gdc:TCGA-LUAD`
- `gdc:TCGA-LUSC`

Minimum expected hits: `2`

Expected absent datasets:

- none

Retrieved datasets:

- `cbioportal:luad_tcga_pan_can_atlas_2018` (candidate)
- `cbioportal:lusc_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-LUSC` (expected)
- `gdc:TCGA-LUAD` (expected)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`

Answer excerpt:

```text
Question: Which datasets contain RNA-seq data for lung cancer?
Candidate dataset records from the current catalog:
- cbioportal:luad_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-LUAD)
  Match level: candidate
  Why it appears: Lung Adenocarcinoma TCGA PanCancer Atlas; data types: mutation, mRNA expression, clinical, copy number.
  Evidence:
  - molecular_profiles: mutations; mRNA expression; copy number alterations (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-LUAD (cBioPortal raw study extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.
  Source URL: https://www.cbioportal.org/study/summary?id=luad_tcga_pan_can_atlas_2018
```

### q006: PASS

Question: Which datasets can support EGFR mutation research?

Expected datasets:

- `gdc:TCGA-LUAD`
- `gdc:TCGA-LUSC`

Minimum expected hits: `2`

Expected absent datasets:

- `gdc:TCGA-BRCA`
- `cbioportal:brca_tcga_pan_can_atlas_2018`

Retrieved datasets:

- `gdc:TCGA-LUSC` (expected)
- `gdc:TCGA-LUAD` (expected)
- `cbioportal:luad_tcga_pan_can_atlas_2018` (candidate)
- `cbioportal:lusc_tcga_pan_can_atlas_2018` (candidate)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`

Answer excerpt:

```text
Question: Which datasets can support EGFR mutation research?
Candidate dataset records from the current catalog:
- gdc:TCGA-LUSC (GDC, TCGA-LUSC)
  Match level: medium
  Why it appears: TCGA Lung Squamous Cell Carcinoma; data types: RNA-seq, clinical, mutation, copy number.
  Evidence:
  - dataset_id: TCGA-LUSC (GDC raw project extract; confidence=high)
  - data_categories: Transcriptome Profiling; Simple Nucleotide Variation; Clinical; Copy Number Variation (GDC raw project extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive case counts are not verified in this raw extract.
  Source URL: https://portal.gdc.cancer.gov/projects/TCGA-LUSC
```

### q007: PASS

Question: Which datasets can support KRAS mutation research?

Expected datasets:

- `gdc:TCGA-LUAD`
- `gdc:TCGA-LUSC`

Minimum expected hits: `2`

Expected absent datasets:

- `gdc:TCGA-BRCA`
- `cbioportal:brca_tcga_pan_can_atlas_2018`

Retrieved datasets:

- `gdc:TCGA-LUSC` (expected)
- `gdc:TCGA-LUAD` (expected)
- `cbioportal:luad_tcga_pan_can_atlas_2018` (candidate)
- `cbioportal:lusc_tcga_pan_can_atlas_2018` (candidate)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`

Answer excerpt:

```text
Question: Which datasets can support KRAS mutation research?
Candidate dataset records from the current catalog:
- gdc:TCGA-LUSC (GDC, TCGA-LUSC)
  Match level: medium
  Why it appears: TCGA Lung Squamous Cell Carcinoma; data types: RNA-seq, clinical, mutation, copy number.
  Evidence:
  - dataset_id: TCGA-LUSC (GDC raw project extract; confidence=high)
  - data_categories: Transcriptome Profiling; Simple Nucleotide Variation; Clinical; Copy Number Variation (GDC raw project extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive case counts are not verified in this raw extract.
  Source URL: https://portal.gdc.cancer.gov/projects/TCGA-LUSC
```

### q008: PASS

Question: What datasets are available for KRAS G12C research in NSCLC?

Expected datasets:

- `gdc:TCGA-LUAD`
- `gdc:TCGA-LUSC`

Minimum expected hits: `2`

Expected absent datasets:

- none

Retrieved datasets:

- `cbioportal:lusc_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-LUSC` (expected)
- `cbioportal:luad_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-LUAD` (expected)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`

Answer excerpt:

```text
Question: What datasets are available for KRAS G12C research in NSCLC?
Candidate dataset records from the current catalog:
- cbioportal:lusc_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-LUSC)
  Match level: medium
  Why it appears: Lung Squamous Cell Carcinoma TCGA PanCancer Atlas; data types: mutation, mRNA expression, clinical, copy number.
  Evidence:
  - molecular_profiles: mutations; mRNA expression; copy number alterations (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-LUSC (cBioPortal raw study extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.
  Source URL: https://www.cbioportal.org/study/summary?id=lusc_tcga_pan_can_atlas_2018
```

### q009: PASS

Question: Which datasets include both clinical metadata and molecular data?

Expected datasets:

- `gdc:TCGA-LUAD`
- `gdc:TCGA-LUSC`

Minimum expected hits: `2`

Expected absent datasets:

- none

Retrieved datasets:

- `gdc:TCGA-BRCA` (candidate)
- `gdc:TCGA-LUSC` (expected)
- `gdc:TCGA-LUAD` (expected)
- `cbioportal:brca_tcga_pan_can_atlas_2018` (candidate)
- `cbioportal:luad_tcga_pan_can_atlas_2018` (candidate)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:brca_tcga_pan_can_atlas_2018`, `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-BRCA`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`

Answer excerpt:

```text
Question: Which datasets include both clinical metadata and molecular data?
Candidate dataset records from the current catalog:
- gdc:TCGA-BRCA (GDC, TCGA-BRCA)
  Match level: candidate
  Why it appears: TCGA Breast Invasive Carcinoma; data types: RNA-seq, clinical, mutation, copy number.
  Evidence:
  - dataset_id: TCGA-BRCA (GDC raw project extract; confidence=high)
  - data_categories: Transcriptome Profiling; Simple Nucleotide Variation; Clinical; Copy Number Variation (GDC raw project extract; confidence=medium)
  Key limitation: This is not a lung cancer or NSCLC dataset and should not be treated as relevant to NSCLC questions.
  Source URL: https://portal.gdc.cancer.gov/projects/TCGA-BRCA
```

### q010: PASS

Question: Which cBioPortal studies are relevant to NSCLC?

Expected datasets:

- `cbioportal:luad_tcga_pan_can_atlas_2018`
- `cbioportal:lusc_tcga_pan_can_atlas_2018`

Minimum expected hits: `2`

Expected absent datasets:

- `cbioportal:brca_tcga_pan_can_atlas_2018`

Retrieved datasets:

- `cbioportal:lusc_tcga_pan_can_atlas_2018` (expected)
- `cbioportal:luad_tcga_pan_can_atlas_2018` (expected)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`
- warning `source_not_explicit`: Dataset is mentioned, but the source label is not explicit near the answer text.
- warning `source_not_explicit`: Dataset is mentioned, but the source label is not explicit near the answer text.

Answer excerpt:

```text
Question: Which cBioPortal studies are relevant to NSCLC?
Candidate dataset records from the current catalog:
- cbioportal:lusc_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-LUSC)
  Match level: candidate
  Why it appears: Lung Squamous Cell Carcinoma TCGA PanCancer Atlas; data types: mutation, mRNA expression, clinical, copy number.
  Evidence:
  - molecular_profiles: mutations; mRNA expression; copy number alterations (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-LUSC (cBioPortal raw study extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.
  Source URL: https://www.cbioportal.org/study/summary?id=lusc_tcga_pan_can_atlas_2018
```

### q011: PASS

Question: Which cBioPortal studies provide mutation profiles for LUAD?

Expected datasets:

- `cbioportal:luad_tcga_pan_can_atlas_2018`

Minimum expected hits: `1`

Expected absent datasets:

- `cbioportal:brca_tcga_pan_can_atlas_2018`

Retrieved datasets:

- `cbioportal:luad_tcga_pan_can_atlas_2018` (expected)
- `cbioportal:lusc_tcga_pan_can_atlas_2018` (candidate)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`
- warning `source_not_explicit`: Dataset is mentioned, but the source label is not explicit near the answer text.
- warning `source_not_explicit`: Dataset is mentioned, but the source label is not explicit near the answer text.

Answer excerpt:

```text
Question: Which cBioPortal studies provide mutation profiles for LUAD?
Candidate dataset records from the current catalog:
- cbioportal:luad_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-LUAD)
  Match level: candidate
  Why it appears: Lung Adenocarcinoma TCGA PanCancer Atlas; data types: mutation, mRNA expression, clinical, copy number.
  Evidence:
  - molecular_profiles: mutations; mRNA expression; copy number alterations (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-LUAD (cBioPortal raw study extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.
  Source URL: https://www.cbioportal.org/study/summary?id=luad_tcga_pan_can_atlas_2018
```

### q012: PASS

Question: Which breast cancer comparison datasets are currently in the catalog?

Expected datasets:

- `gdc:TCGA-BRCA`
- `cbioportal:brca_tcga_pan_can_atlas_2018`

Minimum expected hits: `2`

Expected absent datasets:

- none

Retrieved datasets:

- `cbioportal:brca_tcga_pan_can_atlas_2018` (expected)
- `gdc:TCGA-BRCA` (expected)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:brca_tcga_pan_can_atlas_2018`, `gdc:TCGA-BRCA`

Answer excerpt:

```text
Question: Which breast cancer comparison datasets are currently in the catalog?
Candidate dataset records from the current catalog:
- cbioportal:brca_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-BRCA)
  Match level: candidate
  Why it appears: Breast Invasive Carcinoma TCGA PanCancer Atlas; data types: mutation, mRNA expression, clinical, copy number.
  Evidence:
  - molecular_profiles: mutations; mRNA expression; copy number alterations (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-BRCA (cBioPortal raw study extract; confidence=medium)
  Key limitation: This is not a lung cancer or NSCLC dataset and should not be treated as relevant to NSCLC questions.
  Source URL: https://www.cbioportal.org/study/summary?id=brca_tcga_pan_can_atlas_2018
```

### q013: PASS

Question: Which NSCLC datasets have confirmed KRAS G12C-positive case counts?

Expected datasets:

- `gdc:TCGA-LUAD`
- `gdc:TCGA-LUSC`

Minimum expected hits: `2`

Expected absent datasets:

- `gdc:TCGA-BRCA`
- `cbioportal:brca_tcga_pan_can_atlas_2018`

Retrieved datasets:

- `gdc:TCGA-LUSC` (expected)
- `cbioportal:lusc_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-LUAD` (expected)
- `cbioportal:luad_tcga_pan_can_atlas_2018` (candidate)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`

Answer excerpt:

```text
Question: Which NSCLC datasets have confirmed KRAS G12C-positive case counts?
Candidate dataset records from the current catalog:
- gdc:TCGA-LUSC (GDC, TCGA-LUSC)
  Match level: medium
  Why it appears: TCGA Lung Squamous Cell Carcinoma; data types: RNA-seq, clinical, mutation, copy number.
  Evidence:
  - dataset_id: TCGA-LUSC (GDC raw project extract; confidence=high)
  - data_categories: Transcriptome Profiling; Simple Nucleotide Variation; Clinical; Copy Number Variation (GDC raw project extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive case counts are not verified in this raw extract.
  Source URL: https://portal.gdc.cancer.gov/projects/TCGA-LUSC
```

### q014: PASS

Question: Can TCGA-BRCA answer an NSCLC mutation research question?

Expected datasets:

- `gdc:TCGA-BRCA`

Minimum expected hits: `1`

Expected absent datasets:

- none

Retrieved datasets:

- `gdc:TCGA-BRCA` (expected)
- `cbioportal:brca_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-LUSC` (candidate)
- `gdc:TCGA-LUAD` (candidate)
- `cbioportal:lusc_tcga_pan_can_atlas_2018` (candidate)

Retrieval checks:

- `dataset_hit`: PASS
- `top_hit`: PASS
- `source_hit`: PASS
- `absent_hit`: PASS

Answer checks:

- `dataset_hit`: PASS
- `absent_hit`: PASS
- `keyword_hit`: PASS
- `has_limitation`: PASS
- `has_evidence`: PASS
- `labels_uncertainty`: PASS
- `no_medical_advice`: PASS

Claim checks:

- `passed`: PASS
- `mentioned_dataset_ids`: `cbioportal:brca_tcga_pan_can_atlas_2018`, `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:TCGA-BRCA`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`

Answer excerpt:

```text
Question: Can TCGA-BRCA answer an NSCLC mutation research question?
Candidate dataset records from the current catalog:
- gdc:TCGA-BRCA (GDC, TCGA-BRCA)
  Match level: candidate
  Why it appears: TCGA Breast Invasive Carcinoma; data types: RNA-seq, clinical, mutation, copy number.
  Evidence:
  - dataset_id: TCGA-BRCA (GDC raw project extract; confidence=high)
  - data_categories: Transcriptome Profiling; Simple Nucleotide Variation; Clinical; Copy Number Variation (GDC raw project extract; confidence=medium)
  Key limitation: This is not a lung cancer or NSCLC dataset and should not be treated as relevant to NSCLC questions.
  Source URL: https://portal.gdc.cancer.gov/projects/TCGA-BRCA
```
