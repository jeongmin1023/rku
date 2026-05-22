from __future__ import annotations

import time

import requests

from app.models import Professor
from app.paper_sources.base import PaperSourceAdapter, load_sample_json, professor_matches_item
from app.papers.normalizer import NormalizedPaperCandidate, normalize_crossref_item


class CrossrefClient(PaperSourceAdapter):
    source_name = "crossref"

    def __init__(self, timeout: int = 10) -> None:
        self.timeout = timeout

    def search_papers_for_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        live = self._live_search(professor)
        return live or self._sample(professor)

    def _live_search(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        query = " ".join(part for part in [professor.english_name or professor.name, professor.university] if part)
        try:
            time.sleep(0.35)
            response = requests.get(
                "https://api.crossref.org/works",
                params={"query.bibliographic": query, "rows": 5},
                timeout=self.timeout,
                headers={"User-Agent": "LabFitResearchMVP/0.1"},
            )
            response.raise_for_status()
            items = response.json().get("message", {}).get("items", [])
            return [normalize_crossref_item(item) for item in items]
        except requests.RequestException:
            return []

    def _sample(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        payload = load_sample_json("sample_crossref_response.json")
        return [normalize_crossref_item(item) for item in payload["items"] if professor_matches_item(professor, item)]
