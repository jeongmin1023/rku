from __future__ import annotations

from typing import Any

from app.models import Professor
from app.paper_sources.base import PaperSourceAdapter, load_sample_json, professor_matches_item, title_matches_item
from app.papers.normalizer import NormalizedPaperCandidate, normalize_openalex_item


class OpenAlexClient(PaperSourceAdapter):
    """Optional future expansion source.

    LabFit's default pipeline does not instantiate this adapter because Korean
    domestic sources are better suited for the MVP collection strategy.
    """

    source_name = "openalex"

    def search_by_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        payload = load_sample_json("sample_openalex_response.json")
        return [self.normalize(item) for item in payload["results"] if professor_matches_item(professor, item)]

    def search_by_title(self, title: str) -> list[NormalizedPaperCandidate]:
        payload = load_sample_json("sample_openalex_response.json")
        return [self.normalize(item) for item in payload["results"] if title_matches_item(title, item)]

    def normalize(self, raw_payload: dict[str, Any]) -> NormalizedPaperCandidate:
        return normalize_openalex_item(raw_payload)
