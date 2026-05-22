from __future__ import annotations

import json
from abc import ABC, abstractmethod
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from app.models import Professor
from app.papers.normalizer import NormalizedPaperCandidate, normalize_title


SAMPLE_DATA_DIR = Path(__file__).resolve().parents[2] / "sample_data"


class PaperSourceAdapter(ABC):
    """Common adapter interface for paper metadata sources.

    Search should stay broad. School, department, and official keywords are
    matching evidence, not hard filters at collection time.
    """

    source_name: str

    @abstractmethod
    def search_by_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        """Return candidates for a professor-name centered search."""

    def search_by_title(self, title: str) -> list[NormalizedPaperCandidate]:
        """Optional metadata enrichment by title."""

        return []

    @abstractmethod
    def normalize(self, raw_payload: dict[str, Any]) -> NormalizedPaperCandidate:
        """Normalize one raw source item."""

    def search_papers_for_professor(self, professor: Professor) -> list[NormalizedPaperCandidate]:
        """Backward-compatible alias for older services/tests."""

        return self.search_by_professor(professor)


def load_sample_json(filename: str) -> dict[str, Any]:
    return json.loads((SAMPLE_DATA_DIR / filename).read_text(encoding="utf-8"))


def professor_matches_item(professor: Professor, item: dict[str, Any]) -> bool:
    names = {_norm(professor.name)}
    if professor.english_name:
        names.add(_norm(professor.english_name))
        parts = professor.english_name.split()
        if len(parts) >= 2:
            names.add(_norm(f"{parts[-1]}, {parts[0]}"))
            names.add(_norm(f"{parts[0][0]} {parts[-1]}"))

    item_names = {_norm(str(name)) for name in item.get("professor_names", [])}
    item_names.update(_norm(str(name)) for name in item.get("authors", []))
    return bool(names & item_names)


def title_matches_item(title: str, item: dict[str, Any], threshold: float = 0.82) -> bool:
    needle = normalize_title(title)
    if not needle:
        return False
    titles = [
        item.get("title"),
        item.get("title_ko"),
        item.get("title_en"),
        _first(item.get("title")),
    ]
    return any(
        SequenceMatcher(None, needle, normalize_title(candidate)).ratio() >= threshold
        for candidate in titles
        if candidate
    )


def _first(value: Any) -> str | None:
    if isinstance(value, list) and value:
        return str(value[0])
    if isinstance(value, str):
        return value
    return None


def _norm(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum() or "\uac00" <= ch <= "\ud7a3")
