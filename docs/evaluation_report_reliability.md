# Evaluation Report

This report combines retrieval checks, answer guardrails, and reverse claim verification.

## Summary

- Catalog: `data/processed/catalog_broad_live.json`
- Questions: `eval/questions_reliability.json`
- Retrieval method: `hybrid`
- Retrieval top-k: `5`
- Answer top-k: `4`
- Questions evaluated: `12`
- Overall pass rate: `1.00`

## Cases

### rel_q001: PASS

Question: I need public datasets for EGFR-mutant lung adenocarcinoma with clinical metadata.

Expected datasets:

- `gdc:TCGA-LUAD`
- `cbioportal:luad_tcga_pan_can_atlas_2018`

Minimum expected hits: `1`

Expected absent datasets:

- `gdc:TCGA-BRCA`
- `cbioportal:brca_tcga_pan_can_atlas_2018`

Retrieved datasets:

- `gdc:TCGA-LUAD` (expected)
- `gdc:TCGA-LUSC` (candidate)
- `cbioportal:luad_tcga_pan_can_atlas_2018` (expected)
- `gdc:APOLLO-LUAD` (candidate)
- `gdc:CDDP_EAGLE-1` (candidate)

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
- `mentioned_dataset_ids`: `cbioportal:luad_tcga_pan_can_atlas_2018`, `cbioportal:lusc_tcga_pan_can_atlas_2018`, `gdc:APOLLO-LUAD`, `gdc:TCGA-LUAD`, `gdc:TCGA-LUSC`

Answer excerpt:

```text
Question: I need public datasets for EGFR-mutant lung adenocarcinoma with clinical metadata.
Candidate dataset records from the current catalog:
- gdc:TCGA-LUAD (GDC, TCGA-LUAD)
  Match level: medium
  Why it appears: Lung Adenocarcinoma; data types: RNA-seq, clinical, mutation, copy number.
  Evidence:
  - dataset_id: TCGA-LUAD (GDC raw project extract; confidence=high)
  - data_categories: Transcriptome Profiling; Simple Nucleotide Variation; Clinical; Copy Number Variation (GDC raw project extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive case counts are not verified in this raw extract.
  Source URL: https://portal.gdc.cancer.gov/projects/TCGA-LUAD
```

### rel_q002: PASS

Question: Are there public datasets for KRAS G12C NSCLC with RNA-seq data?

Expected datasets:

- `gdc:TCGA-LUAD`
- `gdc:TCGA-LUSC`
- `cbioportal:luad_tcga_pan_can_atlas_2018`
- `cbioportal:lusc_tcga_pan_can_atlas_2018`

Minimum expected hits: `2`

Expected absent datasets:

- `gdc:TCGA-BRCA`
- `cbioportal:brca_tcga_pan_can_atlas_2018`

Retrieved datasets:

- `cbioportal:lusc_tcga_pan_can_atlas_2018` (expected)
- `cbioportal:luad_tcga_pan_can_atlas_2018` (expected)
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
Question: Are there public datasets for KRAS G12C NSCLC with RNA-seq data?
Candidate dataset records from the current catalog:
- cbioportal:lusc_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-LUSC)
  Match level: medium
  Why it appears: Lung Squamous Cell Carcinoma (TCGA, PanCancer Atlas); data types: mutation, mRNA expression, copy number, methylation, clinical.
  Evidence:
  - molecular_profiles: armlevel cna; copy number alteration; generic assay; genetic ancestry; log2 copy-number values; methylation; methylation (hm27 and hm450 merge); methylation (hm450); mrna expression; mrna expression z-scores relative to all samples (log rna seq v2 rsem); mrna expression z-scores relative to diploid samples (rna seq v2 rsem); mrna expression z-scores relative to normal samples (log rna seq v2 rsem); mrna expression, rsem (batch normalized from illumina hiseq rnaseqv2); mutation extended; mutations; protein expression (rppa); protein expression z-scores (rppa); protein level; putative arm-level copy-number from gistic; putative copy-number alterations from gistic; structural variant; structural variants (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-LUSC (cBioPortal raw study extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.
  Source URL: https://www.cbioportal.org/study/summary?id=lusc_tcga_pan_can_atlas_2018
```

### rel_q003: PASS

Question: Which datasets can compare LUAD and LUSC mutation profiles?

Expected datasets:

- `gdc:TCGA-LUAD`
- `gdc:TCGA-LUSC`
- `cbioportal:luad_tcga_pan_can_atlas_2018`
- `cbioportal:lusc_tcga_pan_can_atlas_2018`

Minimum expected hits: `2`

Expected absent datasets:

- `gdc:TCGA-BRCA`
- `cbioportal:brca_tcga_pan_can_atlas_2018`

Retrieved datasets:

- `cbioportal:luad_tcga_pan_can_atlas_2018` (expected)
- `cbioportal:lusc_tcga_pan_can_atlas_2018` (expected)
- `gdc:TCGA-LUAD` (expected)
- `gdc:TCGA-LUSC` (expected)
- `gdc:TCGA-MESO` (candidate)

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
Question: Which datasets can compare LUAD and LUSC mutation profiles?
Candidate dataset records from the current catalog:
- cbioportal:luad_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-LUAD)
  Match level: candidate
  Why it appears: Lung Adenocarcinoma (TCGA, PanCancer Atlas); data types: mutation, mRNA expression, copy number, methylation, clinical.
  Evidence:
  - molecular_profiles: armlevel cna; copy number alteration; generic assay; genetic ancestry; log2 copy-number values; methylation; methylation (hm27 and hm450 merge); methylation (hm450); mrna expression; mrna expression z-scores relative to all samples (log rna seq v2 rsem); mrna expression z-scores relative to diploid samples (rna seq v2 rsem); mrna expression z-scores relative to normal samples (log rna seq v2 rsem); mrna expression, rsem (batch normalized from illumina hiseq rnaseqv2); mutation extended; mutations; protein expression (rppa); protein expression z-scores (rppa); protein level; putative arm-level copy-number from gistic; putative copy-number alterations from gistic; structural variant; sv data (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-LUAD (cBioPortal raw study extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.
  Source URL: https://www.cbioportal.org/study/summary?id=luad_tcga_pan_can_atlas_2018
```

### rel_q004: PASS

Question: Find cBioPortal studies with mutation and copy-number data for breast cancer.

Expected datasets:

- `cbioportal:brca_tcga_pan_can_atlas_2018`

Minimum expected hits: `1`

Expected absent datasets:

- `gdc:TCGA-BRCA`

Retrieved datasets:

- `cbioportal:brca_tcga_pan_can_atlas_2018` (expected)

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
- warning `source_not_explicit`: Dataset is mentioned, but the source label is not explicit near the answer text.

Answer excerpt:

```text
Question: Find cBioPortal studies with mutation and copy-number data for breast cancer.
Candidate dataset records from the current catalog:
- cbioportal:brca_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-BRCA)
  Match level: candidate
  Why it appears: Breast Invasive Carcinoma (TCGA, PanCancer Atlas); data types: mutation, mRNA expression, copy number, methylation, clinical.
  Evidence:
  - molecular_profiles: armlevel cna; copy number alteration; generic assay; genetic ancestry; log2 copy-number values; methylation; methylation (hm27 and hm450 merge); methylation (hm450); mrna expression; mrna expression z-scores relative to all samples (log rna seq v2 rsem); mrna expression z-scores relative to diploid samples (rna seq v2 rsem); mrna expression z-scores relative to normal samples (log rna seq v2 rsem); mrna expression, rsem (batch normalized from illumina hiseq rnaseqv2); mutation extended; mutations; phosphoprotein site level expression data by cptac (tmt, log2ratio); phosphosite quantification; protein expression (rppa); protein expression z-scores (mass spectrometry by cptac); protein expression z-scores (rppa); protein level; protein levels (mass spectrometry by cptac); putative arm-level copy-number from gistic; putative copy-number alterations from gistic; structural variant; structural variants (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-BRCA (cBioPortal raw study extract; confidence=medium)
  Key limitation: This is not a lung cancer or NSCLC dataset and should not be treated as relevant to NSCLC questions.
  Source URL: https://www.cbioportal.org/study/summary?id=brca_tcga_pan_can_atlas_2018
```

### rel_q005: PASS

Question: Which GDC projects are useful for glioma transcriptomics?

Expected datasets:

- `gdc:TCGA-GBM`
- `gdc:TCGA-LGG`

Minimum expected hits: `1`

Expected absent datasets:

- `cbioportal:gbm_tcga_pan_can_atlas_2018`
- `cbioportal:lgg_tcga_pan_can_atlas_2018`
- `gdc:TCGA-BRCA`

Retrieved datasets:

- `gdc:TCGA-GBM` (expected)
- `gdc:TCGA-LGG` (expected)
- `gdc:TCGA-PCPG` (candidate)
- `gdc:CPTAC-3` (candidate)

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
- `mentioned_dataset_ids`: `cbioportal:gbm_tcga_pan_can_atlas_2018`, `cbioportal:lgg_tcga_pan_can_atlas_2018`, `gdc:CPTAC-3`, `gdc:TCGA-GBM`, `gdc:TCGA-LGG`, `gdc:TCGA-PCPG`
- warning `source_not_explicit`: Dataset is mentioned, but the source label is not explicit near the answer text.
- warning `source_not_explicit`: Dataset is mentioned, but the source label is not explicit near the answer text.

Answer excerpt:

```text
Question: Which GDC projects are useful for glioma transcriptomics?
Candidate dataset records from the current catalog:
- gdc:TCGA-GBM (GDC, TCGA-GBM)
  Match level: candidate
  Why it appears: Glioblastoma Multiforme; data types: unknown.
  Evidence:
  - dataset_id: TCGA-GBM (GDC raw project extract; confidence=high)
  - data_categories:  (GDC raw project extract; confidence=medium)
  Key limitation: Live GDC project metadata does not verify gene-specific or variant-positive case counts.
  Source URL: https://portal.gdc.cancer.gov/projects/TCGA-GBM
```

### rel_q006: PASS

Question: I want melanoma datasets with mutation data but not colorectal cancer cohorts.

Expected datasets:

- `gdc:TCGA-SKCM`
- `cbioportal:skcm_tcga_pan_can_atlas_2018`

Minimum expected hits: `1`

Expected absent datasets:

- `gdc:TCGA-COAD`
- `gdc:TCGA-READ`
- `cbioportal:coadread_tcga_pan_can_atlas_2018`

Retrieved datasets:

- `cbioportal:skcm_tcga_pan_can_atlas_2018` (expected)
- `gdc:TCGA-SKCM` (expected)
- `cbioportal:uvm_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-UVM` (candidate)

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
- `mentioned_dataset_ids`: `cbioportal:skcm_tcga_pan_can_atlas_2018`, `cbioportal:uvm_tcga_pan_can_atlas_2018`, `gdc:TCGA-SKCM`, `gdc:TCGA-UVM`

Answer excerpt:

```text
Question: I want melanoma datasets with mutation data but not colorectal cancer cohorts.
Candidate dataset records from the current catalog:
- cbioportal:skcm_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-SKCM)
  Match level: candidate
  Why it appears: Skin Cutaneous Melanoma (TCGA, PanCancer Atlas); data types: mutation, mRNA expression, copy number, methylation, clinical.
  Evidence:
  - molecular_profiles: armlevel cna; copy number alteration; generic assay; genetic ancestry; log2 copy-number values; methylation; methylation (hm27 and hm450 merge); methylation (hm450); mrna expression; mrna expression z-scores relative to all samples (log rna seq v2 rsem); mrna expression z-scores relative to diploid samples (rna seq v2 rsem); mrna expression, rsem (batch normalized from illumina hiseq rnaseqv2); mutation extended; mutations; protein expression (rppa); protein expression z-scores (rppa); protein level; putative arm-level copy-number from gistic; putative copy-number alterations from gistic; structural variant; structural variants (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-SKCM (cBioPortal raw study extract; confidence=medium)
  Key limitation: Live cBioPortal study metadata does not verify gene-specific or variant-positive sample counts.
  Source URL: https://www.cbioportal.org/study/summary?id=skcm_tcga_pan_can_atlas_2018
```

### rel_q007: PASS

Question: Can I use TCGA-BRCA for prostate cancer biomarker discovery?

Expected datasets:

- `gdc:TCGA-BRCA`

Minimum expected hits: `1`

Expected absent datasets:

- none

Retrieved datasets:

- `gdc:TCGA-BRCA` (expected)
- `cbioportal:brca_tcga_pan_can_atlas_2018` (candidate)
- `cbioportal:prad_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-PRAD` (candidate)
- `gdc:CMI-MPC` (candidate)

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
- `mentioned_dataset_ids`: `cbioportal:brca_tcga_pan_can_atlas_2018`, `cbioportal:prad_tcga_pan_can_atlas_2018`, `gdc:TCGA-BRCA`, `gdc:TCGA-PRAD`

Answer excerpt:

```text
Question: Can I use TCGA-BRCA for prostate cancer biomarker discovery?
Candidate dataset records from the current catalog:
- gdc:TCGA-BRCA (GDC, TCGA-BRCA)
  Match level: candidate
  Why it appears: Breast Invasive Carcinoma; data types: RNA-seq, clinical, mutation, copy number.
  Evidence:
  - dataset_id: TCGA-BRCA (GDC raw project extract; confidence=high)
  - data_categories: Transcriptome Profiling; Simple Nucleotide Variation; Clinical; Copy Number Variation (GDC raw project extract; confidence=medium)
  Key limitation: This is not a lung cancer or NSCLC dataset and should not be treated as relevant to NSCLC questions.
  Source URL: https://portal.gdc.cancer.gov/projects/TCGA-BRCA
```

### rel_q008: PASS

Question: Which datasets have both clinical metadata and copy-number profiles for head and neck cancer?

Expected datasets:

- `gdc:TCGA-HNSC`
- `cbioportal:hnsc_tcga_pan_can_atlas_2018`

Minimum expected hits: `1`

Expected absent datasets:

- `gdc:TCGA-PRAD`

Retrieved datasets:

- `cbioportal:hnsc_tcga_pan_can_atlas_2018` (expected)
- `gdc:TCGA-HNSC` (expected)
- `gdc:CPTAC-3` (candidate)

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
- `mentioned_dataset_ids`: `cbioportal:hnsc_tcga_pan_can_atlas_2018`, `gdc:CPTAC-3`, `gdc:TCGA-HNSC`

Answer excerpt:

```text
Question: Which datasets have both clinical metadata and copy-number profiles for head and neck cancer?
Candidate dataset records from the current catalog:
- cbioportal:hnsc_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-HNSC)
  Match level: candidate
  Why it appears: Head and Neck Squamous Cell Carcinoma (TCGA, PanCancer Atlas); data types: mutation, mRNA expression, copy number, methylation, clinical.
  Evidence:
  - molecular_profiles: armlevel cna; copy number alteration; generic assay; genetic ancestry; log2 copy-number values; methylation; methylation (hm27 and hm450 merge); methylation (hm450); mrna expression; mrna expression z-scores relative to all samples (log rna seq v2 rsem); mrna expression z-scores relative to diploid samples (rna seq v2 rsem); mrna expression z-scores relative to normal samples (log rna seq v2 rsem); mrna expression, rsem (batch normalized from illumina hiseq rnaseqv2); mutation extended; mutations; protein expression (rppa); protein expression z-scores (rppa); protein level; putative arm-level copy-number from gistic; putative copy-number alterations from gistic; structural variant; structural variants (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-HNSC (cBioPortal raw study extract; confidence=medium)
  Key limitation: Live cBioPortal study metadata does not verify gene-specific or variant-positive sample counts.
  Source URL: https://www.cbioportal.org/study/summary?id=hnsc_tcga_pan_can_atlas_2018
```

### rel_q009: PASS

Question: Which datasets can support colorectal cancer expression analysis?

Expected datasets:

- `gdc:TCGA-COAD`
- `gdc:TCGA-READ`
- `cbioportal:coadread_tcga_pan_can_atlas_2018`

Minimum expected hits: `1`

Expected absent datasets:

- `gdc:TCGA-SKCM`

Retrieved datasets:

- `cbioportal:coadread_tcga_pan_can_atlas_2018` (expected)
- `gdc:TCGA-READ` (expected)
- `gdc:TCGA-COAD` (expected)
- `gdc:MATCH-H` (candidate)
- `gdc:CPTAC-2` (candidate)

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
- `mentioned_dataset_ids`: `cbioportal:coadread_tcga_pan_can_atlas_2018`, `gdc:MATCH-H`, `gdc:TCGA-COAD`, `gdc:TCGA-READ`

Answer excerpt:

```text
Question: Which datasets can support colorectal cancer expression analysis?
Candidate dataset records from the current catalog:
- cbioportal:coadread_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-COADREAD)
  Match level: candidate
  Why it appears: Colorectal Adenocarcinoma (TCGA, PanCancer Atlas); data types: mutation, mRNA expression, copy number, methylation, clinical.
  Evidence:
  - molecular_profiles: armlevel cna; copy number alteration; generic assay; genetic ancestry; log2 copy-number values; methylation; methylation (hm27 and hm450 merge); methylation (hm450); mrna expression; mrna expression z-scores relative to all samples (log rna seq v2 rsem); mrna expression z-scores relative to diploid samples (rna seq v2 rsem); mrna expression z-scores relative to normal samples (log rna seq v2 rsem); mrna expression, rsem (batch normalized from illumina hiseq rnaseqv2); mutation extended; mutations; protein expression (rppa); protein expression z-scores (rppa); protein level; protein level z-scores (mass spectrometry by cptac); protein levels (mass spectrometry by cptac); putative arm-level copy-number from gistic; putative copy-number alterations from gistic; structural variant; structural variants (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-COADREAD (cBioPortal raw study extract; confidence=medium)
  Key limitation: Live cBioPortal study metadata does not verify gene-specific or variant-positive sample counts.
  Source URL: https://www.cbioportal.org/study/summary?id=coadread_tcga_pan_can_atlas_2018
```

### rel_q010: PASS

Question: Which public resources can help inspect ovarian cancer mutation and clinical data?

Expected datasets:

- `gdc:TCGA-OV`
- `cbioportal:ov_tcga_pan_can_atlas_2018`

Minimum expected hits: `1`

Expected absent datasets:

- `gdc:TCGA-LUAD`

Retrieved datasets:

- `cbioportal:ov_tcga_pan_can_atlas_2018` (expected)
- `gdc:APOLLO-OV` (candidate)
- `gdc:TCGA-OV` (expected)
- `gdc:CPTAC-2` (candidate)
- `gdc:FM-AD` (candidate)

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
- `mentioned_dataset_ids`: `cbioportal:ov_tcga_pan_can_atlas_2018`, `gdc:APOLLO-OV`, `gdc:CPTAC-2`, `gdc:TCGA-OV`

Answer excerpt:

```text
Question: Which public resources can help inspect ovarian cancer mutation and clinical data?
Candidate dataset records from the current catalog:
- cbioportal:ov_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-OV)
  Match level: candidate
  Why it appears: Ovarian Serous Cystadenocarcinoma (TCGA, PanCancer Atlas); data types: mutation, mRNA expression, copy number, methylation, clinical.
  Evidence:
  - molecular_profiles: armlevel cna; copy number alteration; generic assay; genetic ancestry; log2 copy-number values; methylation; methylation (hm27 and hm450 merge); methylation (hm450); mrna expression; mrna expression z-scores relative to all samples (log rna seq v2 rsem); mrna expression z-scores relative to diploid samples (rna seq v2 rsem); mrna expression, rsem (batch normalized from illumina hiseq rnaseqv2); mutation extended; mutations; phosphoprotein site level expression data by cptac (tmt, log2ratio); phosphosite quantification; protein expression (rppa); protein expression z-scores (rppa); protein level; protein level z-scores (mass spectrometry by cptac); protein levels (mass spectrometry by cptac); putative arm-level copy-number from gistic; putative copy-number alterations from gistic; structural variant; structural variants (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-OV (cBioPortal raw study extract; confidence=medium)
  Key limitation: Live cBioPortal study metadata does not verify gene-specific or variant-positive sample counts.
  Source URL: https://www.cbioportal.org/study/summary?id=ov_tcga_pan_can_atlas_2018
```

### rel_q011: PASS

Question: Which cBioPortal studies include methylation and expression profiles for lung adenocarcinoma?

Expected datasets:

- `cbioportal:luad_tcga_pan_can_atlas_2018`

Minimum expected hits: `1`

Expected absent datasets:

- `gdc:TCGA-LUAD`

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
Question: Which cBioPortal studies include methylation and expression profiles for lung adenocarcinoma?
Candidate dataset records from the current catalog:
- cbioportal:luad_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-LUAD)
  Match level: candidate
  Why it appears: Lung Adenocarcinoma (TCGA, PanCancer Atlas); data types: mutation, mRNA expression, copy number, methylation, clinical.
  Evidence:
  - molecular_profiles: armlevel cna; copy number alteration; generic assay; genetic ancestry; log2 copy-number values; methylation; methylation (hm27 and hm450 merge); methylation (hm450); mrna expression; mrna expression z-scores relative to all samples (log rna seq v2 rsem); mrna expression z-scores relative to diploid samples (rna seq v2 rsem); mrna expression z-scores relative to normal samples (log rna seq v2 rsem); mrna expression, rsem (batch normalized from illumina hiseq rnaseqv2); mutation extended; mutations; protein expression (rppa); protein expression z-scores (rppa); protein level; putative arm-level copy-number from gistic; putative copy-number alterations from gistic; structural variant; sv data (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-LUAD (cBioPortal raw study extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.
  Source URL: https://www.cbioportal.org/study/summary?id=luad_tcga_pan_can_atlas_2018
```

### rel_q012: PASS

Question: Do we have confirmed EGFR-positive sample counts for LUAD datasets?

Expected datasets:

- `gdc:TCGA-LUAD`
- `cbioportal:luad_tcga_pan_can_atlas_2018`

Minimum expected hits: `1`

Expected absent datasets:

- `gdc:TCGA-BRCA`

Retrieved datasets:

- `cbioportal:luad_tcga_pan_can_atlas_2018` (expected)
- `gdc:TCGA-LUSC` (candidate)
- `gdc:TCGA-LUAD` (expected)
- `cbioportal:lusc_tcga_pan_can_atlas_2018` (candidate)
- `gdc:TCGA-MESO` (candidate)

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
Question: Do we have confirmed EGFR-positive sample counts for LUAD datasets?
Candidate dataset records from the current catalog:
- cbioportal:luad_tcga_pan_can_atlas_2018 (cBioPortal, TCGA-LUAD)
  Match level: medium
  Why it appears: Lung Adenocarcinoma (TCGA, PanCancer Atlas); data types: mutation, mRNA expression, copy number, methylation, clinical.
  Evidence:
  - molecular_profiles: armlevel cna; copy number alteration; generic assay; genetic ancestry; log2 copy-number values; methylation; methylation (hm27 and hm450 merge); methylation (hm450); mrna expression; mrna expression z-scores relative to all samples (log rna seq v2 rsem); mrna expression z-scores relative to diploid samples (rna seq v2 rsem); mrna expression z-scores relative to normal samples (log rna seq v2 rsem); mrna expression, rsem (batch normalized from illumina hiseq rnaseqv2); mutation extended; mutations; protein expression (rppa); protein expression z-scores (rppa); protein level; putative arm-level copy-number from gistic; putative copy-number alterations from gistic; structural variant; sv data (cBioPortal raw study extract; confidence=medium)
  - canonical_dataset_id: TCGA-LUAD (cBioPortal raw study extract; confidence=medium)
  Key limitation: Specific EGFR, KRAS, or KRAS G12C-positive sample counts are not verified in this raw extract.
  Source URL: https://www.cbioportal.org/study/summary?id=luad_tcga_pan_can_atlas_2018
```
