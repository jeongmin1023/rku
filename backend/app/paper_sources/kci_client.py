from __future__ import annotations

import os
import time

import requests

from app.models import Professor
from app.paper_sources.base import PaperSourceAdapter, load_sample_json, professor_matches_item
from app.papers.normalizer import NormalizedPaperCandidate, normalize_kci_item


class KCIClient(PaperSourceAdapter):
    source_name = "kci"

    def __init__(self, api_key: str | None = None, timeout: int = 10) -> None:
        self.api_key = api_key or os.getenv("KCI_API_KEY")
        self.timeout = timeout

    def search_papers_for_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        if not self.api_key:
            return self._sample(professor)
        try:
            time.sleep(0.35)
            # KCI deployments vary by contract. Keep the live call conservative and
            # fall back to mock data unless a compatible endpoint is configured.
            endpoint = os.getenv("KCI_API_URL")
            if not endpoint:
                return self._sample(professor)
            response = requests.get(
                endpoint,
                params={"key": self.api_key, "author": professor.name, "university": professor.university},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            return [normalize_kci_item(item) for item in payload.get("papers", [])]
        except requests.RequestException:
            return self._sample(professor)

    def _sample(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        payload = load_sample_json("sample_kci_response.json")
        return [normalize_kci_item(item) for item in payload["papers"] if professor_matches_item(professor, item)]
