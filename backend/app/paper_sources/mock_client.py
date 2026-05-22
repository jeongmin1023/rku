from __future__ import annotations

from typing import Any

from app.models import Professor
from app.paper_sources.base import PaperSourceAdapter, load_sample_json, professor_matches_item, title_matches_item
from app.papers.normalizer import (
    NormalizedPaperCandidate,
    normalize_crossref_item,
    normalize_dbpia_item,
    normalize_kci_item,
    normalize_riss_item,
    normalize_scienceon_item,
)


class MockClient(PaperSourceAdapter):
    """Offline aggregate source for demos and tests.

    OpenAlex is deliberately excluded from the default mock pipeline.
    """

    source_name = "mock"

    def search_by_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        candidates: list[NormalizedPaperCandidate] = []
        for filename, key, normalizer in _SOURCES:
            payload = load_sample_json(filename)
            candidates.extend(normalizer(item) for item in payload[key] if professor_matches_item(professor, item))
        return candidates

    def search_by_title(self, title: str) -> list[NormalizedPaperCandidate]:
        candidates: list[NormalizedPaperCandidate] = []
        for filename, key, normalizer in _SOURCES:
            payload = load_sample_json(filename)
            candidates.extend(normalizer(item) for item in payload[key] if title_matches_item(title, item))
        return candidates

    def normalize(self, raw_payload: dict[str, Any]) -> NormalizedPaperCandidate:
        source = raw_payload.get("source")
        if source == "riss":
            return normalize_riss_item(raw_payload)
        if source == "dbpia":
            return normalize_dbpia_item(raw_payload)
        if source == "scienceon":
            return normalize_scienceon_item(raw_payload)
        if source == "crossref":
            return normalize_crossref_item(raw_payload)
        return normalize_kci_item(raw_payload)


_SOURCES = [
    ("sample_kci_response.json", "papers", normalize_kci_item),
    ("sample_riss_response.json", "papers", normalize_riss_item),
    ("sample_dbpia_response.json", "papers", normalize_dbpia_item),
    ("sample_scienceon_response.json", "papers", normalize_scienceon_item),
    ("sample_crossref_response.json", "items", normalize_crossref_item),
]
