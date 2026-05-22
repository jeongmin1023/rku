from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field


KOREAN_RE = re.compile(r"[가-힣]")
ENGLISH_RE = re.compile(r"[A-Za-z]")


class NormalizedPaperCandidate(BaseModel):
    source: str
    source_id: str
    title_ko: str | None = None
    title_en: str | None = None
    normalized_title: str
    authors: list[str] = Field(default_factory=list)
    author_affiliations: list[str] = Field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    uci: str | None = None
    abstract: str | None = None
    keywords: list[str] = Field(default_factory=list)
    citation_count: int | None = None
    citation_source: str | None = None
    url: str | None = None
    raw_payload: dict[str, Any] = Field(default_factory=dict)
    source_confidence: float = 0.5
    language: str = "unknown"
    source_warnings: list[str] = Field(default_factory=list)


def normalize_kci_item(item: dict[str, Any]) -> NormalizedPaperCandidate:
    title_ko = item.get("title_ko") or _maybe_korean_title(item.get("title"))
    title_en = item.get("title_en") or _maybe_english_title(item.get("title"))
    display_title = title_en or title_ko or item.get("title") or "Untitled"
    affiliations = _as_list(item.get("author_affiliations") or item.get("affiliations"))
    warnings = _candidate_warnings(item, affiliations)
    confidence = _confidence_from_item(
        item,
        default=0.9 if affiliations else 0.65,
        name_only_default=0.2,
    )
    return NormalizedPaperCandidate(
        source="kci",
        source_id=str(item.get("source_id") or item.get("kci_id") or item.get("uci") or display_title),
        title_ko=title_ko,
        title_en=title_en,
        normalized_title=normalize_title(display_title),
        authors=_as_list(item.get("authors")),
        author_affiliations=affiliations,
        year=_to_int(item.get("year") or item.get("publication_year")),
        venue=item.get("venue") or item.get("journal"),
        doi=normalize_doi(item.get("doi")),
        uci=item.get("uci") or item.get("kci_id"),
        abstract=item.get("abstract"),
        keywords=_as_list(item.get("keywords")),
        citation_count=_to_int(item.get("citation_count")),
        citation_source="kci",
        url=item.get("url"),
        raw_payload=item,
        source_confidence=confidence,
        language=detect_language(" ".join([display_title, item.get("abstract") or ""])),
        source_warnings=warnings,
    )


def normalize_openalex_item(item: dict[str, Any]) -> NormalizedPaperCandidate:
    title = item.get("title") or item.get("display_name") or "Untitled"
    authorships = item.get("authorships", [])
    authors = [
        (authorship.get("author") or {}).get("display_name")
        for authorship in authorships
        if (authorship.get("author") or {}).get("display_name")
    ] or _as_list(item.get("authors"))
    affiliations: list[str] = []
    openalex_author_ids: list[str] = []
    for authorship in authorships:
        author_id = (authorship.get("author") or {}).get("id")
        if author_id:
            openalex_author_ids.append(author_id)
        for institution in authorship.get("institutions", []):
            name = institution.get("display_name")
            if name:
                affiliations.append(name)
    affiliations.extend(_as_list(item.get("author_affiliations") or item.get("institutions")))
    concepts = [
        concept.get("display_name")
        for concept in item.get("concepts", [])
        if concept.get("display_name")
    ]
    topics = [
        topic.get("display_name")
        for topic in item.get("topics", [])
        if topic.get("display_name")
    ]
    source = item.get("primary_location", {}).get("source") or {}
    warnings = _candidate_warnings(item, affiliations)
    if item.get("author_candidates_count", 1) and int(item.get("author_candidates_count", 1)) > 1:
        warnings.append("OpenAlex Author 후보가 여러 명입니다.")
    confidence = _confidence_from_item(
        item,
        default=0.9 if item.get("openalex_author_id") or openalex_author_ids else 0.75,
        name_only_default=0.2,
    )
    raw_payload = dict(item)
    if openalex_author_ids:
        raw_payload["openalex_author_ids"] = openalex_author_ids
    return NormalizedPaperCandidate(
        source="openalex",
        source_id=str(item.get("id") or item.get("source_id") or title),
        title_ko=item.get("title_ko") or _maybe_korean_title(title),
        title_en=item.get("title_en") or _maybe_english_title(title),
        normalized_title=normalize_title(title),
        authors=list(dict.fromkeys(authors)),
        author_affiliations=list(dict.fromkeys(affiliations)),
        year=_to_int(item.get("publication_year") or item.get("year")),
        venue=item.get("venue") or source.get("display_name"),
        doi=normalize_doi(item.get("doi")),
        uci=item.get("uci"),
        abstract=item.get("abstract") or restore_abstract(item.get("abstract_inverted_index")),
        keywords=list(dict.fromkeys(_as_list(item.get("keywords")) + concepts + topics)),
        citation_count=_to_int(item.get("cited_by_count") or item.get("citation_count")),
        citation_source="openalex",
        url=item.get("url") or item.get("id"),
        raw_payload=raw_payload,
        source_confidence=confidence,
        language=detect_language(" ".join([title, item.get("abstract") or ""])),
        source_warnings=warnings,
    )


def normalize_crossref_item(item: dict[str, Any]) -> NormalizedPaperCandidate:
    title = _first(item.get("title")) or item.get("title_en") or item.get("title_ko") or "Untitled"
    authors = []
    for author in item.get("author", []):
        name = " ".join(part for part in [author.get("given"), author.get("family")] if part)
        if name:
            authors.append(name)
    authors.extend(_as_list(item.get("authors")))
    affiliations = _as_list(item.get("author_affiliations") or item.get("affiliations"))
    year = _crossref_year(item) or _to_int(item.get("year"))
    warnings = _candidate_warnings(item, affiliations)
    if not normalize_doi(item.get("DOI") or item.get("doi")):
        warnings.append("Crossref 후보에 DOI가 없어 메타데이터 신뢰도를 낮췄습니다.")
    return NormalizedPaperCandidate(
        source="crossref",
        source_id=str(item.get("DOI") or item.get("doi") or item.get("source_id") or title),
        title_ko=item.get("title_ko") or _maybe_korean_title(title),
        title_en=item.get("title_en") or _maybe_english_title(title),
        normalized_title=normalize_title(title),
        authors=list(dict.fromkeys(authors)),
        author_affiliations=affiliations,
        year=year,
        venue=_first(item.get("container-title")) or item.get("venue"),
        doi=normalize_doi(item.get("DOI") or item.get("doi")),
        uci=item.get("uci"),
        abstract=_strip_tags(item.get("abstract")),
        keywords=_as_list(item.get("subject") or item.get("keywords")),
        citation_count=_to_int(item.get("is-referenced-by-count") or item.get("citation_count")),
        citation_source="crossref",
        url=item.get("URL") or item.get("url"),
        raw_payload=item,
        source_confidence=_confidence_from_item(item, default=0.8 if item.get("DOI") or item.get("doi") else 0.55),
        language=detect_language(" ".join([title, item.get("abstract") or ""])),
        source_warnings=warnings,
    )


def normalize_dbpia_item(item: dict[str, Any]) -> NormalizedPaperCandidate:
    return _normalize_title_author_source_item(item, source="dbpia", default_confidence=0.65)


def normalize_riss_item(item: dict[str, Any]) -> NormalizedPaperCandidate:
    return _normalize_title_author_source_item(item, source="riss", default_confidence=0.65)


def normalize_lab_publication_item(item: dict[str, Any]) -> NormalizedPaperCandidate:
    return _normalize_title_author_source_item(item, source="professor_lab_page_publication", default_confidence=1.0)


def _normalize_title_author_source_item(
    item: dict[str, Any],
    source: str,
    default_confidence: float,
) -> NormalizedPaperCandidate:
    title_ko = item.get("title_ko") or _maybe_korean_title(item.get("title"))
    title_en = item.get("title_en") or _maybe_english_title(item.get("title"))
    display_title = title_en or title_ko or item.get("title") or "Untitled"
    affiliations = _as_list(item.get("author_affiliations") or item.get("affiliations"))
    warnings = _candidate_warnings(item, affiliations)
    return NormalizedPaperCandidate(
        source=source,
        source_id=str(item.get("source_id") or item.get("id") or item.get("uci") or display_title),
        title_ko=title_ko,
        title_en=title_en,
        normalized_title=normalize_title(display_title),
        authors=_as_list(item.get("authors")),
        author_affiliations=affiliations,
        year=_to_int(item.get("year") or item.get("publication_year")),
        venue=item.get("venue") or item.get("journal"),
        doi=normalize_doi(item.get("doi")),
        uci=item.get("uci") or item.get("kci_id"),
        abstract=item.get("abstract"),
        keywords=_as_list(item.get("keywords")),
        citation_count=_to_int(item.get("citation_count")),
        citation_source=item.get("citation_source") or source,
        url=item.get("url"),
        raw_payload=item,
        source_confidence=_confidence_from_item(item, default=default_confidence, name_only_default=0.2),
        language=detect_language(" ".join([display_title, item.get("abstract") or ""])),
        source_warnings=warnings,
    )


def normalize_title(title: str | None) -> str:
    if not title:
        return ""
    lowered = title.lower()
    lowered = re.sub(r"[\W_]+", " ", lowered, flags=re.UNICODE)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    cleaned = doi.strip().lower()
    cleaned = cleaned.replace("https://doi.org/", "").replace("http://doi.org/", "")
    return cleaned or None


def restore_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    if not inverted_index:
        return None
    positions: list[tuple[int, str]] = []
    for word, indexes in inverted_index.items():
        positions.extend((index, word) for index in indexes)
    return " ".join(word for _, word in sorted(positions))


def detect_language(text: str | None) -> str:
    if not text:
        return "unknown"
    has_ko = bool(KOREAN_RE.search(text))
    has_en = bool(ENGLISH_RE.search(text))
    if has_ko and has_en:
        return "mixed"
    if has_ko:
        return "ko"
    if has_en:
        return "en"
    return "unknown"


def _candidate_warnings(item: dict[str, Any], affiliations: list[str]) -> list[str]:
    warnings = list(_as_list(item.get("source_warnings")))
    if not affiliations:
        warnings.append("저자 소속 정보가 불명확합니다.")
    if item.get("name_only_match"):
        warnings.append("이름만으로 검색된 후보입니다.")
    return list(dict.fromkeys(warnings))


def _confidence_from_item(
    item: dict[str, Any],
    default: float,
    name_only_default: float = 0.2,
) -> float:
    if item.get("name_only_match"):
        return float(item.get("source_confidence", name_only_default))
    return float(item.get("source_confidence", default))


def _as_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [part.strip() for part in re.split(r"[,;|]", value) if part.strip()]
    return [str(value).strip()]


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _first(value: Any) -> str | None:
    if isinstance(value, list) and value:
        return str(value[0])
    if isinstance(value, str):
        return value
    return None


def _maybe_korean_title(title: str | None) -> str | None:
    if title and KOREAN_RE.search(title):
        return title
    return None


def _maybe_english_title(title: str | None) -> str | None:
    if title and ENGLISH_RE.search(title) and not KOREAN_RE.search(title):
        return title
    return None


def _strip_tags(text: str | None) -> str | None:
    if not text:
        return None
    return re.sub(r"<[^>]+>", " ", text).strip()


def _crossref_year(item: dict[str, Any]) -> int | None:
    for key in ("published-print", "published-online", "created", "issued"):
        date_parts = (item.get(key) or {}).get("date-parts")
        if date_parts and date_parts[0]:
            return _to_int(date_parts[0][0])
    return None
