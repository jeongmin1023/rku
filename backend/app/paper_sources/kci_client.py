from __future__ import annotations

import os
import time
from typing import Any

import requests

from app.models import Professor
from app.paper_sources.base import PaperSourceAdapter, load_sample_json, professor_matches_item, title_matches_item
from app.papers.normalizer import NormalizedPaperCandidate, normalize_kci_item


class KCIClient(PaperSourceAdapter):
    source_name = "kci"

    def __init__(self, api_key: str | None = None, timeout: int = 10) -> None:
        self.api_key = api_key or os.getenv("KCI_API_KEY")
        self.timeout = timeout

    def search_by_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        if not self.api_key or not os.getenv("KCI_API_URL"):
            return self._sample_by_professor(professor)
        try:
            time.sleep(0.35)
            response = requests.get(
                os.environ["KCI_API_URL"],
                params={"key": self.api_key, "author": professor.name},
                timeout=self.timeout,
                headers={"User-Agent": "LabFitResearchMVP/0.2"},
            )
            response.raise_for_status()
            return [self.normalize(item) for item in response.json().get("papers", [])]
        except requests.RequestException:
            return self._sample_by_professor(professor)

    def search_by_title(self, title: str) -> list[NormalizedPaperCandidate]:
        payload = load_sample_json("sample_kci_response.json")
        return [self.normalize(item) for item in payload["papers"] if title_matches_item(title, item)]

    def normalize(self, raw_payload: dict[str, Any]) -> NormalizedPaperCandidate:
        return normalize_kci_item(raw_payload)

    def _sample_by_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        payload = load_sample_json("sample_kci_response.json")
        return [self.normalize(item) for item in payload["papers"] if professor_matches_item(professor, item)]
