"""Small retrieval backends for the normalized dataset catalog."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from src.models import DatasetRecord


TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?")

STOPWORDS = {
    "are",
    "and",
    "both",
    "but",
    "can",
    "cancer",
    "catalog",
    "comparison",
    "contain",
    "currently",
    "data",
    "dataset",
    "datasets",
    "exist",
    "for",
    "have",
    "has",
    "help",
    "i",
    "in",
    "include",
    "is",
    "not",
    "or",
    "metadata",
    "of",
    "profiles",
    "provide",
    "public",
    "research",
    "studies",
    "study",
    "support",
    "the",
    "to",
    "what",
    "which",
    "with",
    "want",
    "we",
}

SYNONYMS: dict[str, set[str]] = {
    "nsclc": {
        "nsclc",
        "non-small cell lung cancer",
        "non small cell lung cancer",
        "luad",
        "lusc",
        "lung adenocarcinoma",
        "lung squamous cell carcinoma",
    },
    "expression": {"expression", "rna-seq", "rna seq", "mrna"},
    "rna-seq": {"rna-seq", "rna seq", "expression", "mrna"},
    "mutation": {"mutation", "mutations", "simple nucleotide variation", "snv"},
    "molecular": {"molecular", "mutation", "expression", "copy number"},
    "clinical": {"clinical", "diagnosis", "tumor stage", "survival"},
    "colon": {
        "colon",
        "coad",
        "colorectal",
        "rectum",
        "read",
        "colon adenocarcinoma",
        "rectum adenocarcinoma",
    },
    "colorectal": {
        "colon",
        "coad",
        "colorectal",
        "rectum",
        "read",
        "colon adenocarcinoma",
        "rectum adenocarcinoma",
    },
    "melanoma": {"melanoma", "skcm", "skin cutaneous melanoma"},
    "cbioportal": {"cbioportal", "cbio portal"},
    "gdc": {"gdc", "genomic data commons"},
    "ovarian": {"ovarian", "ovary", "ov", "serous ovarian"},
    "prostate": {"prostate", "prad", "prostate adenocarcinoma"},
    "kidney": {"kidney", "renal", "kirc", "kirp", "kich"},
    "brain": {"brain", "glioma", "gbm", "lgg", "glioblastoma"},
    "glioma": {"brain", "glioma", "gbm", "lgg", "glioblastoma"},
    "bladder": {"bladder", "blca", "urothelial"},
    "stomach": {"stomach", "gastric", "stad"},
    "gastric": {"stomach", "gastric", "stad"},
    "liver": {"liver", "lihc", "hepatocellular"},
    "thyroid": {"thyroid", "thca"},
    "cervical": {"cervical", "cervix", "cesc"},
    "uterine": {"uterine", "uterus", "endometrial", "ucec", "ucs"},
    "head": {"head", "neck", "hnsc"},
}

SITE_GROUPS: dict[str, set[str]] = {
    "lung": {"lung", "luad", "lusc", "nsclc"},
    "breast": {"breast", "brca"},
    "colon_rectum": {"colon", "coad", "colorectal", "rectum", "read"},
    "skin": {"melanoma", "skin", "skcm", "uvm"},
    "prostate": {"prostate", "prad"},
    "kidney": {"kidney", "renal", "kirc", "kirp", "kich"},
    "brain": {"brain", "glioma", "gbm", "lgg"},
    "ovary": {"ovarian", "ovary", "ov"},
    "bladder": {"bladder", "blca"},
    "stomach": {"stomach", "gastric", "stad"},
    "liver": {"liver", "lihc", "hepatocellular"},
    "thyroid": {"thyroid", "thca"},
    "cervix": {"cervical", "cervix", "cesc"},
    "uterus": {"uterine", "uterus", "endometrial", "ucec", "ucs"},
    "head_neck": {"head", "neck", "hnsc"},
}


@dataclass(frozen=True)
class RetrievalResult:
    record: DatasetRecord
    score: float
    matched_terms: list[str]


def normalize_text(text: str) -> str:
    return text.lower().replace("_", " ")


def tokenize(text: str) -> set[str]:
    return {
        token
        for token in TOKEN_PATTERN.findall(normalize_text(text))
        if token not in STOPWORDS
    }


def expand_query(query: str) -> set[str]:
    normalized = normalize_text(query)
    terms = tokenize(normalized)
    for trigger, expansions in SYNONYMS.items():
        if trigger in normalized or trigger in terms:
            for expansion in expansions:
                terms.update(tokenize(expansion))
    return terms


def excluded_site_groups(query: str) -> set[str]:
    """Return site groups mentioned in simple exclusion phrases."""

    normalized = normalize_text(query)
    exclusions: set[str] = set()
    for marker in ["not ", "without ", "exclude ", "excluding "]:
        start = normalized.find(marker)
        if start == -1:
            continue
        excluded_text = normalized[start + len(marker) :]
        excluded_terms = expand_query(excluded_text)
        for site_name, terms in SITE_GROUPS.items():
            if excluded_terms & terms:
                exclusions.add(site_name)
    return exclusions


def score_record(
    query_terms: set[str],
    record: DatasetRecord,
    exact_query_terms: set[str] | None = None,
    excluded_sites: set[str] | None = None,
) -> tuple[float, list[str]]:
    text = normalize_text(record.searchable_text())
    record_terms = tokenize(text)
    matched_terms = sorted(term for term in query_terms if term in record_terms)

    score = float(len(matched_terms))
    exact_terms = exact_query_terms or query_terms

    record_ids = tokenize(
        " ".join(
            [
                record.dataset_id,
                record.canonical_dataset_id,
                record.source_record_id,
            ]
        )
    )
    record_ids -= {"gdc", "cbioportal", "tcga"}
    has_exact_id_match = bool(exact_terms & record_ids)
    if has_exact_id_match:
        score += 40.0

    for phrase in [
        "breast cancer",
        "lung cancer",
        "lung adenocarcinoma",
        "lung squamous cell carcinoma",
        "non-small cell lung cancer",
        "kras g12c",
        "rna-seq",
        "copy number",
    ]:
        if phrase in query_terms:
            continue
        if phrase in text and all(token in query_terms for token in tokenize(phrase)):
            score += 5.0

    if normalize_text(record.dataset_id) in text:
        score += 0.0
    if "cbioportal" in query_terms and normalize_text(record.source) == "cbioportal":
        score += 4.0
    if "gdc" in query_terms and normalize_text(record.source) == "gdc":
        score += 4.0
    if "cbioportal" in query_terms and normalize_text(record.source) != "cbioportal":
        score -= 60.0
    if "gdc" in query_terms and normalize_text(record.source) != "gdc":
        score -= 60.0
    if "mutation" in query_terms and record.has_mutation:
        score += 2.0
    if ("rna-seq" in query_terms or "expression" in query_terms) and record.has_expression:
        score += 2.0
    if "clinical" in query_terms and record.has_clinical:
        score += 2.0
    if "copy" in query_terms and "number" in query_terms and record.has_copy_number:
        score += 2.0

    gene_terms = {"egfr", "kras"}
    queried_genes = query_terms & gene_terms
    if queried_genes and not has_exact_id_match:
        gene_text = normalize_text(
            " ".join(
                [
                    *record.explicit_genes,
                    *record.inferred_genes,
                    *record.explicit_mutations,
                    *record.inferred_mutations,
                    record.biomarker_notes,
                ]
            )
        )
        if any(gene in gene_text for gene in queried_genes):
            score += 6.0
        else:
            score -= 30.0

    site_text = normalize_text(
        " ".join([*record.primary_sites, *record.cancer_types, record.title])
    )
    excluded_sites = excluded_sites or set()
    if excluded_sites and not has_exact_id_match:
        excluded_site_match = any(
            any(term in site_text for term in SITE_GROUPS[site_name])
            for site_name in excluded_sites
        )
        if excluded_site_match:
            score -= 100.0

    matched_site_groups = [
        site_name
        for site_name, terms in SITE_GROUPS.items()
        if query_terms & terms
    ]
    if matched_site_groups and not has_exact_id_match:
        site_matches = any(
            any(term in site_text for term in SITE_GROUPS[site_name])
            for site_name in matched_site_groups
        )
        if not site_matches:
            score -= 60.0

    return score, matched_terms


def keyword_search(
    query: str,
    records: list[DatasetRecord],
    top_k: int = 5,
) -> list[RetrievalResult]:
    query_terms = expand_query(query)
    exact_query_terms = tokenize(query)
    excluded_sites = excluded_site_groups(query)
    results: list[RetrievalResult] = []

    for record in records:
        score, matched_terms = score_record(
            query_terms,
            record,
            exact_query_terms,
            excluded_sites=excluded_sites,
        )
        if score > 0:
            results.append(
                RetrievalResult(
                    record=record,
                    score=score,
                    matched_terms=matched_terms,
                )
            )

    return sorted(
        results,
        key=lambda result: (
            result.score,
            result.record.canonical_dataset_id,
            result.record.source,
        ),
        reverse=True,
    )[:top_k]


def _tfidf_vectors(
    records: list[DatasetRecord],
) -> tuple[list[Counter[str]], dict[str, float]]:
    document_terms = [Counter(tokenize(record.searchable_text())) for record in records]
    document_count = len(document_terms)
    document_frequency: Counter[str] = Counter()
    for terms in document_terms:
        document_frequency.update(terms.keys())

    idf = {
        term: math.log((1 + document_count) / (1 + frequency)) + 1
        for term, frequency in document_frequency.items()
    }
    return document_terms, idf


def _weighted_vector(terms: Counter[str], idf: dict[str, float]) -> dict[str, float]:
    return {
        term: frequency * idf.get(term, 0.0)
        for term, frequency in terms.items()
    }


def _cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0

    shared_terms = set(left) & set(right)
    numerator = sum(left[term] * right[term] for term in shared_terms)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)


def tfidf_search(
    query: str,
    records: list[DatasetRecord],
    top_k: int = 5,
) -> list[RetrievalResult]:
    """Search with an in-memory TF-IDF cosine baseline."""

    document_terms, idf = _tfidf_vectors(records)
    query_terms = Counter(expand_query(query))
    query_vector = _weighted_vector(query_terms, idf)
    results: list[RetrievalResult] = []

    for record, terms in zip(records, document_terms):
        record_vector = _weighted_vector(terms, idf)
        score = _cosine_similarity(query_vector, record_vector)
        if score > 0:
            matched_terms = sorted(set(query_terms) & set(terms))
            results.append(RetrievalResult(record=record, score=score, matched_terms=matched_terms))

    return sorted(
        results,
        key=lambda result: (
            result.score,
            result.record.canonical_dataset_id,
            result.record.source,
        ),
        reverse=True,
    )[:top_k]


def hybrid_search(
    query: str,
    records: list[DatasetRecord],
    top_k: int = 5,
    keyword_weight: float = 0.8,
) -> list[RetrievalResult]:
    """Combine tuned keyword rules with the TF-IDF semantic baseline."""

    keyword_results = keyword_search(query, records, top_k=len(records))
    tfidf_results = tfidf_search(query, records, top_k=len(records))
    keyword_max = max((result.score for result in keyword_results), default=0.0)
    tfidf_max = max((result.score for result in tfidf_results), default=0.0)

    by_id: dict[str, dict[str, object]] = {}
    for result in keyword_results:
        by_id[result.record.dataset_id] = {
            "record": result.record,
            "keyword_score": result.score / keyword_max if keyword_max else 0.0,
            "tfidf_score": 0.0,
            "matched_terms": set(result.matched_terms),
        }

    for result in tfidf_results:
        item = by_id.get(result.record.dataset_id)
        if item is None:
            continue
        item["tfidf_score"] = result.score / tfidf_max if tfidf_max else 0.0
        item["matched_terms"] = set(item["matched_terms"]) | set(result.matched_terms)

    results = []
    for item in by_id.values():
        score = (
            keyword_weight * float(item["keyword_score"])
            + (1.0 - keyword_weight) * float(item["tfidf_score"])
        )
        if score > 0:
            results.append(
                RetrievalResult(
                    record=item["record"],  # type: ignore[arg-type]
                    score=score,
                    matched_terms=sorted(item["matched_terms"]),  # type: ignore[arg-type]
                )
            )

    return sorted(
        results,
        key=lambda result: (
            result.score,
            result.record.canonical_dataset_id,
            result.record.source,
        ),
        reverse=True,
    )[:top_k]


def search(
    query: str,
    records: list[DatasetRecord],
    top_k: int = 5,
    method: str = "hybrid",
) -> list[RetrievalResult]:
    if method == "keyword":
        return keyword_search(query, records, top_k=top_k)
    if method == "tfidf":
        return tfidf_search(query, records, top_k=top_k)
    if method == "hybrid":
        return hybrid_search(query, records, top_k=top_k)
    raise ValueError(f"Unknown retrieval method: {method}")
