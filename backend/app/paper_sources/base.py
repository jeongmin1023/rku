from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from app.models import Professor
from app.papers.normalizer import NormalizedPaperCandidate


SAMPLE_DATA_DIR = Path(__file__).resolve().parents[2] / "sample_data"


class PaperSourceAdapter(ABC):
    source_name: str

    @abstractmethod
    def search_papers_for_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        """Return source-specific candidates normalized into the common schema."""


def load_sample_json(filename: str) -> dict[str, Any]:
    return json.loads((SAMPLE_DATA_DIR / filename).read_text(encoding="utf-8"))


def professor_matches_item(professor: Professor, item: dict[str, Any]) -> bool:
    names = {professor.name}
    if professor.english_name:
        names.add(professor.english_name)
    item_names = {str(name) for name in item.get("professor_names", [])}
    return bool(names & item_names)
