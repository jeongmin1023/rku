from app.paper_sources.base import load_sample_json
from app.papers.normalizer import normalize_crossref_item, normalize_kci_item, normalize_openalex_item


def test_mock_responses_normalize_to_common_candidate_schema() -> None:
    kci_item = load_sample_json("sample_kci_response.json")["papers"][0]
    openalex_item = load_sample_json("sample_openalex_response.json")["results"][0]
    crossref_item = load_sample_json("sample_crossref_response.json")["items"][0]

    kci = normalize_kci_item(kci_item)
    openalex = normalize_openalex_item(openalex_item)
    crossref = normalize_crossref_item(crossref_item)

    assert kci.source == "kci"
    assert openalex.source == "openalex"
    assert crossref.source == "crossref"
    assert kci.normalized_title == openalex.normalized_title == crossref.normalized_title
    assert kci.doi == "10.5555/labfit.2025.001"
    assert kci.language in {"ko", "mixed"}
    assert isinstance(kci.source_warnings, list)
