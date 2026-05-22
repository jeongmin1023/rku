from app.paper_sources.base import load_sample_json
from app.papers.normalizer import normalize_crossref_item, normalize_dbpia_item, normalize_kci_item, normalize_openalex_item
from app.papers.resolver import PaperResolver


def test_same_doi_merges_to_one_master_paper() -> None:
    kci = normalize_kci_item(load_sample_json("sample_kci_response.json")["papers"][0])
    openalex = normalize_openalex_item(load_sample_json("sample_openalex_response.json")["results"][0])

    masters = PaperResolver().resolve([kci, openalex])

    assert len(masters) == 1
    assert masters[0].duplicate_status == "merged"
    assert set(masters[0].source_list) == {"kci", "openalex"}


def test_similar_title_author_year_merges_without_doi() -> None:
    kci = normalize_kci_item(load_sample_json("sample_kci_response.json")["papers"][1])
    openalex = normalize_openalex_item(load_sample_json("sample_openalex_response.json")["results"][1])

    masters = PaperResolver().resolve([kci, openalex])

    assert len(masters) == 1
    assert masters[0].duplicate_status == "merged"


def test_kci_and_dbpia_korean_title_variant_merges_without_doi() -> None:
    kci = normalize_kci_item(load_sample_json("sample_kci_response.json")["papers"][1])
    dbpia = normalize_dbpia_item(load_sample_json("sample_dbpia_response.json")["papers"][0])

    masters = PaperResolver().resolve([kci, dbpia])

    assert len(masters) == 1
    assert masters[0].duplicate_status == "merged"
    assert set(masters[0].source_list) == {"kci", "dbpia"}
    assert masters[0].citation_signals["kci"] == 9
    assert masters[0].citation_signals["dbpia"] == 3


def test_openalex_and_crossref_same_doi_merge() -> None:
    openalex = normalize_openalex_item(load_sample_json("sample_openalex_response.json")["results"][0])
    crossref = normalize_crossref_item(load_sample_json("sample_crossref_response.json")["items"][0])

    masters = PaperResolver().resolve([openalex, crossref])

    assert len(masters) == 1
    assert masters[0].doi == "10.5555/labfit.2025.001"
    assert masters[0].merge_confidence >= 0.9
