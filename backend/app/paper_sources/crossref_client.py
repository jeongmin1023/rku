from __future__ import annotations

import time
from typing import Any

import requests

from app.models import Professor
from app.paper_sources.base import PaperSourceAdapter, load_sample_json, professor_matches_item, title_matches_item
from app.papers.normalizer import NormalizedPaperCandidate, normalize_crossref_item


class CrossrefClient(PaperSourceAdapter):
    """DOI/title metadata enrichment source.

    Crossref is intentionally not used as a hard professor-paper decision
    source. It enriches candidate titles found from domestic or official pages.
    """

    source_name = "crossref"

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def search_by_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        # Offline demo still exposes professor search, but live use is title-first.
        payload = load_sample_json("sample_crossref_response.json")
        return [self.normalize(item) for item in payload["items"] if professor_matches_item(professor, item)]

    def search_by_title(self, title: str) -> list[NormalizedPaperCandidate]:
        live = self._live_title_search(title)
        if live:
            return live
        payload = load_sample_json("sample_crossref_response.json")
        return [self.normalize(item) for item in payload["items"] if title_matches_item(title, item)]

    def normalize(self, raw_payload: dict[str, Any]) -> NormalizedPaperCandidate:
        return normalize_crossref_item(raw_payload)

    def _live_title_search(self, title: str) -> list[NormalizedPaperCandidate]:
        try:
            time.sleep(0.35)
            response = requests.get(
                "https://api.crossref.org/works",
                params={"query.title": title, "rows": 3},
                timeout=self.timeout,
                headers={"User-Agent": "LabFitResearchMVP/0.2 (mailto:local@example.invalid)"},
            )
            response.raise_for_status()
            items = response.json().get("message", {}).get("items", [])
            return [self.normalize(item) for item in items]
        except requests.RequestException:
            return []
