from __future__ import annotations

from typing import Any

from app.models import Professor
from app.paper_sources.base import PaperSourceAdapter, load_sample_json, professor_matches_item, title_matches_item
from app.papers.normalizer import NormalizedPaperCandidate, normalize_scienceon_item


class ScienceONClient(PaperSourceAdapter):
    source_name = "scienceon"

    def search_by_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        payload = load_sample_json("sample_scienceon_response.json")
        return [self.normalize(item) for item in payload["papers"] if professor_matches_item(professor, item)]

    def search_by_title(self, title: str) -> list[NormalizedPaperCandidate]:
        payload = load_sample_json("sample_scienceon_response.json")
        return [self.normalize(item) for item in payload["papers"] if title_matches_item(title, item)]

    def normalize(self, raw_payload: dict[str, Any]) -> NormalizedPaperCandidate:
        return normalize_scienceon_item(raw_payload)
