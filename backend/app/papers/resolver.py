from __future__ import annotations

import json
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from app.papers.normalizer import NormalizedPaperCandidate, normalize_title


@dataclass
class MasterPaperDraft:
    title_ko: str | None = None
    title_en: str | None = None
    display_title: str = ""
    authors: list[str] = field(default_factory=list)
    author_affiliations: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    uci: str | None = None
    abstract: str | None = None
    keywords: list[str] = field(default_factory=list)
    source_list: list[str] = field(default_factory=list)
    source_ids: dict[str, list[str]] = field(default_factory=dict)
    citation_signals: dict[str, int | None] = field(default_factory=dict)
    duplicate_status: str = "unique"
    merge_confidence: float = 0.5
    merge_notes: list[str] = field(default_factory=list)
    source_confidence_signals: dict[str, float] = field(default_factory=dict)
    url: str | None = None
    candidates: list[NormalizedPaperCandidate] = field(default_factory=list)

    def to_json_fields(self) -> dict[str, str]:
        return {
            "authors_json": json.dumps(self.authors, ensure_ascii=False),
            "author_affiliations_json": json.dumps(self.author_affiliations, ensure_ascii=False),
            "keywords_json": json.dumps(self.keywords, ensure_ascii=False),
            "source_list_json": json.dumps(self.source_list, ensure_ascii=False),
            "source_ids_json": json.dumps(self.source_ids, ensure_ascii=False),
            "citation_signals_json": json.dumps(self.citation_signals, ensure_ascii=False),
            "merge_notes_json": json.dumps(self.merge_notes, ensure_ascii=False),
            "source_confidence_signals_json": json.dumps(self.source_confidence_signals, ensure_ascii=False),
        }


class PaperResolver:
    def resolve(self, candidates: list[NormalizedPaperCandidate]) -> list[MasterPaperDraft]:
        masters: list[MasterPaperDraft] = []
        for candidate in candidates:
            target, note, confidence = self._find_merge_target(candidate, masters)
            if target is None:
                possible = self._has_possible_duplicate(candidate, masters)
                masters.append(
                    self._from_candidate(
                        candidate,
                        duplicate_status="duplicate_possible" if possible else "unique",
                        note="유사 중복 후보가 있으나 자동 병합 기준에는 미달했습니다." if possible else "단일 후보로 MasterPaper를 생성했습니다.",
                        confidence=0.45 if possible else candidate.source_confidence,
                    )
                )
            else:
                self._merge(target, candidate, note=note, confidence=confidence)
        return masters

    def _find_merge_target(
        self,
        candidate: NormalizedPaperCandidate,
        masters: list[MasterPaperDraft],
    ) -> tuple[MasterPaperDraft | None, str, float]:
        for master in masters:
            if candidate.doi and master.doi and candidate.doi == master.doi:
                return master, "DOI exact match", 1.0
            if candidate.uci and master.uci and candidate.uci == master.uci:
                return master, "UCI/KCI ID exact match", 0.97

            title_similarity = _title_similarity(candidate, master)
            if (
                title_similarity >= 0.92
                and _year_matches(candidate.year, master.year)
                and _authors_overlap(candidate.authors, master.authors)
            ):
                return master, f"normalized_title similarity {title_similarity:.2f} with year and author match", min(0.96, title_similarity)

            translated_similarity = _translated_title_similarity(candidate, master)
            if (
                translated_similarity >= 0.82
                and _year_matches(candidate.year, master.year)
                and (_venue_matches(candidate.venue, master.venue) or _authors_overlap(candidate.authors, master.authors))
            ):
                return master, f"translated/title similarity {translated_similarity:.2f} with year and venue/author match", min(0.9, translated_similarity)
        return None, "", 0.0

    def _has_possible_duplicate(
        self,
        candidate: NormalizedPaperCandidate,
        masters: list[MasterPaperDraft],
    ) -> bool:
        return any(
            _title_similarity(candidate, master) >= 0.78
            and (_year_matches(candidate.year, master.year) or _authors_overlap(candidate.authors, master.authors))
            for master in masters
        )

    def _from_candidate(
        self,
        candidate: NormalizedPaperCandidate,
        duplicate_status: str,
        note: str,
        confidence: float,
    ) -> MasterPaperDraft:
        display_title = candidate.title_ko or candidate.title_en or candidate.normalized_title
        source_key = candidate.citation_source or candidate.source
        return MasterPaperDraft(
            title_ko=candidate.title_ko,
            title_en=candidate.title_en,
            display_title=display_title,
            authors=list(dict.fromkeys(candidate.authors)),
            author_affiliations=list(dict.fromkeys(candidate.author_affiliations)),
            year=candidate.year,
            venue=candidate.venue,
            doi=candidate.doi,
            uci=candidate.uci,
            abstract=candidate.abstract,
            keywords=list(dict.fromkeys(candidate.keywords)),
            source_list=[candidate.source],
            source_ids={candidate.source: [candidate.source_id]},
            citation_signals={source_key: candidate.citation_count},
            duplicate_status=duplicate_status,
            merge_confidence=round(confidence, 3),
            merge_notes=[note, *candidate.source_warnings],
            source_confidence_signals={candidate.source: candidate.source_confidence},
            url=candidate.url,
            candidates=[candidate],
        )

    def _merge(self, master: MasterPaperDraft, candidate: NormalizedPaperCandidate, note: str, confidence: float) -> None:
        master.title_ko = master.title_ko or candidate.title_ko
        master.title_en = master.title_en or candidate.title_en
        master.display_title = master.title_ko or master.title_en or master.display_title
        master.authors = _merge_unique(master.authors, candidate.authors)
        master.author_affiliations = _merge_unique(master.author_affiliations, candidate.author_affiliations)
        master.year = master.year or candidate.year
        master.venue = master.venue or candidate.venue
        master.doi = master.doi or candidate.doi
        master.uci = master.uci or candidate.uci
        master.abstract = _longer(master.abstract, candidate.abstract)
        master.keywords = _merge_unique(master.keywords, candidate.keywords)
        master.source_list = _merge_unique(master.source_list, [candidate.source])
        master.source_ids.setdefault(candidate.source, [])
        if candidate.source_id not in master.source_ids[candidate.source]:
            master.source_ids[candidate.source].append(candidate.source_id)
        citation_key = candidate.citation_source or candidate.source
        master.citation_signals[citation_key] = candidate.citation_count
        master.duplicate_status = "merged"
        master.merge_confidence = round(max(master.merge_confidence, confidence), 3)
        master.merge_notes = _merge_unique(master.merge_notes, [note, *candidate.source_warnings])
        master.source_confidence_signals[candidate.source] = max(
            master.source_confidence_signals.get(candidate.source, 0.0),
            candidate.source_confidence,
        )
        master.url = master.url or candidate.url
        master.candidates.append(candidate)


def _title_similarity(candidate: NormalizedPaperCandidate, master: MasterPaperDraft) -> float:
    candidate_titles = _candidate_titles(candidate)
    master_titles = _master_titles(master)
    return max(SequenceMatcher(None, left, right).ratio() for left in candidate_titles for right in master_titles)


def _translated_title_similarity(candidate: NormalizedPaperCandidate, master: MasterPaperDraft) -> float:
    pairs = [(left, right) for left in _candidate_titles(candidate) for right in _master_titles(master)]
    return max((_token_similarity(left, right) for left, right in pairs), default=0.0)


def _candidate_titles(candidate: NormalizedPaperCandidate) -> list[str]:
    titles = [candidate.normalized_title]
    for title in (candidate.title_ko, candidate.title_en):
        if title:
            titles.append(normalize_title(title))
    return [title for title in titles if title]


def _master_titles(master: MasterPaperDraft) -> list[str]:
    titles = [normalize_title(master.display_title)]
    for title in (master.title_ko, master.title_en):
        if title:
            titles.append(normalize_title(title))
    return [title for title in titles if title]


def _authors_overlap(left: list[str], right: list[str]) -> bool:
    left_norm = {_normalize_author(author) for author in left}
    right_norm = {_normalize_author(author) for author in right}
    return bool(left_norm & right_norm)


def _token_similarity(left: str, right: str) -> float:
    stopwords = {"with", "using", "for", "and", "the", "of", "a", "an", "based", "기반", "연구", "분석"}
    left_tokens = {token for token in left.lower().split() if token not in stopwords}
    right_tokens = {token for token in right.lower().split() if token not in stopwords}
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _normalize_author(author: str) -> str:
    return "".join(ch for ch in author.lower() if ch.isalnum() or "\uac00" <= ch <= "\ud7a3")


def _year_matches(left: int | None, right: int | None) -> bool:
    return bool(left and right and left == right)


def _venue_matches(left: str | None, right: str | None) -> bool:
    if not left or not right:
        return False
    return SequenceMatcher(None, normalize_title(left), normalize_title(right)).ratio() >= 0.85


def _merge_unique(left: list[str], right: list[str]) -> list[str]:
    return list(dict.fromkeys([*left, *right]))


def _longer(left: str | None, right: str | None) -> str | None:
    if not left:
        return right
    if not right:
        return left
    return right if len(right) > len(left) else left
