from __future__ import annotations

from app.models import Professor
from app.paper_sources.base import PaperSourceAdapter, load_sample_json, professor_matches_item
from app.papers.normalizer import (
    NormalizedPaperCandidate,
    normalize_crossref_item,
    normalize_dbpia_item,
    normalize_kci_item,
    normalize_openalex_item,
)


class MockClient(PaperSourceAdapter):
    source_name = "mock"

    def search_papers_for_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        """Full offline source used by tests and demos when external APIs are unavailable."""

        candidates: list[NormalizedPaperCandidate] = []
        kci = load_sample_json("sample_kci_response.json")
        candidates.extend(normalize_kci_item(item) for item in kci["papers"] if professor_matches_item(professor, item))
        openalex = load_sample_json("sample_openalex_response.json")
        candidates.extend(
            normalize_openalex_item(item) for item in openalex["results"] if professor_matches_item(professor, item)
        )
        crossref = load_sample_json("sample_crossref_response.json")
        candidates.extend(
            normalize_crossref_item(item) for item in crossref["items"] if professor_matches_item(professor, item)
        )
        try:
            dbpia = load_sample_json("sample_dbpia_response.json")
            candidates.extend(
                normalize_dbpia_item(item) for item in dbpia["papers"] if professor_matches_item(professor, item)
            )
        except FileNotFoundError:
            pass
        return candidates
