from __future__ import annotations

import os
import time
from typing import Any

import requests

from app.models import Professor
from app.paper_sources.base import PaperSourceAdapter, load_sample_json, professor_matches_item
from app.papers.normalizer import NormalizedPaperCandidate, normalize_openalex_item


class OpenAlexClient(PaperSourceAdapter):
    source_name = "openalex"
    base_url = "https://api.openalex.org"

    def __init__(self, timeout: int = 12) -> None:
        self.timeout = timeout
        self.mailto = os.getenv("OPENALEX_MAILTO")

    def search_papers_for_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        live = self._live_search(professor)
        return live or self._sample(professor)

    def _live_search(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        query = " ".join(
            part
            for part in [professor.english_name or professor.name, professor.university, professor.official_keywords]
            if part
        )
        params: dict[str, Any] = {"search": query, "per-page": 20}
        if self.mailto:
            params["mailto"] = self.mailto
        try:
            time.sleep(0.35)
            response = requests.get(
                f"{self.base_url}/works",
                params=params,
                timeout=self.timeout,
                headers={"User-Agent": "LabFitResearchMVP/0.1"},
            )
            response.raise_for_status()
            items = response.json().get("results", [])
            return [normalize_openalex_item(item) for item in items]
        except requests.RequestException:
            return []

    def _sample(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        payload = load_sample_json("sample_openalex_response.json")
        return [normalize_openalex_item(item) for item in payload["results"] if professor_matches_item(professor, item)]
