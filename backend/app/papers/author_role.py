from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any


AUTHOR_ROLE_WEIGHTS = {
    "corresponding_author": 1.0,
    "last_author": 1.0,
    "first_author": 0.9,
    "co_first_author": 0.85,
    "middle_coauthor": 0.45,
    "unknown": 0.6,
}


def detect_author_role(
    professor_name: str,
    english_name: str | None,
    authors: list[str],
    paper: dict[str, Any] | None = None,
) -> str:
    if not authors:
        return "unknown"
    names = _name_variants(professor_name, english_name)
    matched_name = _best_matched_author_name(names, authors)
    if not matched_name:
        return "unknown"

    paper = paper or {}
    if _listed_in(paper.get("corresponding_authors"), matched_name, names):
        return "corresponding_author"
    if _listed_in(paper.get("co_first_authors"), matched_name, names):
        return "co_first_author"

    best_index = None
    best_score = 0.0
    for index, author in enumerate(authors):
        for name in names:
            score = SequenceMatcher(None, _norm(name), _norm(author)).ratio()
            if score > best_score:
                best_score = score
                best_index = index
    if best_score < 0.62 or best_index is None:
        return "unknown"
    if best_index == 0:
        return "first_author"
    if best_index == len(authors) - 1:
        return "last_author"
    return "middle_coauthor"


def author_role_weight(role: str | None) -> float:
    return AUTHOR_ROLE_WEIGHTS.get(role or "unknown", 0.6)


def _best_matched_author_name(names: list[str], authors: list[str]) -> str | None:
    best_name = None
    best_score = 0.0
    for author in authors:
        for name in names:
            score = SequenceMatcher(None, _norm(name), _norm(author)).ratio()
            if score > best_score:
                best_score = score
                best_name = author
    return best_name if best_score >= 0.62 else None


def _listed_in(value: Any, matched_name: str, variants: list[str]) -> bool:
    if not value:
        return False
    values = value if isinstance(value, list) else [value]
    normalized = {_norm(item) for item in values}
    return _norm(matched_name) in normalized or bool({_norm(name) for name in variants} & normalized)


def _name_variants(professor_name: str, english_name: str | None) -> list[str]:
    names = [professor_name]
    if english_name:
        names.append(english_name)
        names.append(_initial_name(english_name))
        parts = english_name.split()
        if len(parts) >= 2:
            names.append(f"{parts[-1]}, {parts[0]}")
    return list(dict.fromkeys(names))


def _initial_name(name: str) -> str:
    parts = name.split()
    if len(parts) < 2:
        return name
    return f"{parts[0][0]} {parts[-1]}"


def _norm(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum() or "\uac00" <= ch <= "\ud7a3")
