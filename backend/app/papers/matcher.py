from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

from app.papers.author_role import author_role_weight, detect_author_role


ACCEPTED = "accepted"
NEEDS_REVIEW = "needs_review"
WEAK_CANDIDATE = "weak_candidate"
REJECTED = "rejected"


@dataclass
class MatchResult:
    score: float
    status: str
    author_role: str
    evidence_notes_json: str
    warnings_json: str


def score_master_paper_match(
    professor: Any,
    paper: dict[str, Any],
    repeated_coauthors: Counter[str] | None = None,
    lab_publication_titles: list[str] | None = None,
) -> MatchResult:
    repeated_coauthors = repeated_coauthors or Counter()
    lab_publication_titles = lab_publication_titles or []

    author_role = detect_author_role(professor.name, getattr(professor, "english_name", None), paper.get("authors", []), paper)
    name_score, name_note = _name_score(professor.name, paper.get("authors", []))
    english_score, english_note = _english_name_score(getattr(professor, "english_name", None), paper.get("authors", []))
    affiliation_score, affiliation_note = _affiliation_score(getattr(professor, "university", ""), paper)
    department_score, department_note = _department_score(getattr(professor, "department", ""), paper)
    topic_score, topic_matches = _topic_score(professor, paper)
    coauthor_score, coauthor_note = _coauthor_score(professor, paper, repeated_coauthors, author_role)
    identifier_score, identifier_note = _identifier_score(paper)
    lab_page_evidence = _lab_page_evidence(paper, lab_publication_titles)
    career_year_score = _career_year_score(paper)
    source_confidence_score = _source_confidence_score(paper)
    cross_source_score, source_note = _cross_source_agreement_score(paper)

    raw_score = (
        0.16 * name_score
        + 0.08 * english_score
        + 0.16 * affiliation_score
        + 0.08 * department_score
        + 0.14 * topic_score
        + 0.10 * coauthor_score
        + 0.10 * identifier_score
        + 0.08 * lab_page_evidence
        + 0.04 * career_year_score
        + 0.03 * source_confidence_score
        + 0.03 * cross_source_score
    )

    warnings = _warnings(
        name_score=name_score,
        english_score=english_score,
        affiliation_score=affiliation_score,
        department_score=department_score,
        topic_score=topic_score,
        coauthor_score=coauthor_score,
        identifier_score=identifier_score,
        author_role=author_role,
        paper=paper,
    )
    score = _apply_contamination_guards(
        raw_score,
        name_score=name_score,
        affiliation_score=affiliation_score,
        department_score=department_score,
        topic_score=topic_score,
        identifier_score=identifier_score,
        author_role=author_role,
    )
    status = status_from_score(score)
    if warnings and status == ACCEPTED:
        status = NEEDS_REVIEW

    evidence = {
        "name": name_note,
        "english_name": english_note,
        "affiliation": affiliation_note,
        "department": department_note,
        "topic": f"Matched keywords: {', '.join(topic_matches)}" if topic_matches else "No strong topic overlap found",
        "coauthors": coauthor_note,
        "identifier": identifier_note,
        "lab_page_evidence": "Lab/profile publication title matched" if lab_page_evidence >= 0.9 else "No strong lab page publication match",
        "career_year": f"Career-year plausibility signal {career_year_score:.2f}",
        "source_confidence": f"Average source confidence {source_confidence_score:.2f}",
        "source_agreement": source_note,
        "warning": "; ".join(warnings) if warnings else None,
        "score_components": {
            "NameScore": round(name_score, 3),
            "EnglishNameScore": round(english_score, 3),
            "AffiliationScore": round(affiliation_score, 3),
            "DepartmentScore": round(department_score, 3),
            "TopicScore": round(topic_score, 3),
            "CoAuthorScore": round(coauthor_score, 3),
            "IdentifierScore": round(identifier_score, 3),
            "LabPageEvidence": round(lab_page_evidence, 3),
            "CareerYearScore": round(career_year_score, 3),
            "SourceConfidenceScore": round(source_confidence_score, 3),
            "CrossSourceAgreementScore": round(cross_source_score, 3),
        },
    }
    return MatchResult(
        score=round(score, 3),
        status=status,
        author_role=author_role,
        evidence_notes_json=json.dumps(evidence, ensure_ascii=False),
        warnings_json=json.dumps(warnings, ensure_ascii=False),
    )


def status_from_score(score: float) -> str:
    if score >= 0.82:
        return ACCEPTED
    if score >= 0.62:
        return NEEDS_REVIEW
    if score >= 0.42:
        return WEAK_CANDIDATE
    return REJECTED


def _name_score(professor_name: str, authors: list[str]) -> tuple[float, str]:
    best = _best_similarity([professor_name], authors)
    if best >= 0.92:
        return 1.0, "Korean/local name matched"
    if best >= 0.72:
        return 0.72, "Korean/local name partially matched"
    return max(0.0, best * 0.45), "Professor name was not clearly matched"


def _english_name_score(english_name: str | None, authors: list[str]) -> tuple[float, str]:
    if not english_name:
        return 0.5, "English name not available; neutral signal used"
    variants = [english_name, _initial_name(english_name)]
    parts = english_name.split()
    if len(parts) >= 2:
        variants.append(f"{parts[-1]}, {parts[0]}")
    best = _best_similarity(variants, authors)
    if best >= 0.92:
        return 1.0, "English name matched"
    if best >= 0.68:
        return 0.72, "English initial or abbreviated form partially matched"
    return max(0.0, best * 0.5), "English name was not clearly matched"


def _affiliation_score(university: str, paper: dict[str, Any]) -> tuple[float, str]:
    affiliations = " ".join(paper.get("author_affiliations", [])).lower()
    if not affiliations:
        return 0.2, "Author affiliation is unclear"
    if university and university.lower() in affiliations:
        return 1.0, "Current university found in paper affiliation"
    similarity = SequenceMatcher(None, university.lower(), affiliations).ratio() if university else 0.0
    if similarity >= 0.55:
        return 0.48, "Affiliation partially resembles current university"
    return 0.05, "Current university not found in paper affiliation"


def _department_score(department: str, paper: dict[str, Any]) -> tuple[float, str]:
    affiliations = " ".join(paper.get("author_affiliations", [])).lower()
    if not affiliations:
        return 0.25, "Department affiliation is unclear"
    if department and department.lower() in affiliations:
        return 1.0, "Current department found in paper affiliation"
    department_tokens = _tokens(department)
    affiliation_tokens = _tokens(affiliations)
    overlap = department_tokens & affiliation_tokens
    if overlap:
        return 0.55, f"Department tokens partially matched: {', '.join(sorted(overlap))}"
    return 0.1, "Current department not found in paper affiliation"


def _topic_score(professor: Any, paper: dict[str, Any]) -> tuple[float, list[str]]:
    professor_terms = _tokens(getattr(professor, "official_keywords", "") or "")
    paper_terms = _tokens(
        " ".join(
            [
                paper.get("display_title") or "",
                paper.get("abstract") or "",
                " ".join(paper.get("keywords", [])),
                paper.get("venue") or "",
            ]
        )
    )
    if not professor_terms:
        return 0.35, []
    if not paper_terms:
        return 0.2, []
    overlap = sorted(professor_terms & paper_terms)
    score = min(1.0, len(overlap) / max(1, min(len(professor_terms), 6)) + (0.15 if overlap else 0))
    return score, overlap


def _coauthor_score(
    professor: Any,
    paper: dict[str, Any],
    repeated_coauthors: Counter[str],
    author_role: str,
) -> tuple[float, str]:
    authors = [_norm(author) for author in paper.get("authors", [])]
    professor_names = {_norm(professor.name)}
    if getattr(professor, "english_name", None):
        professor_names.add(_norm(professor.english_name))
        professor_names.add(_norm(_initial_name(professor.english_name)))
    coauthors = [author for author in authors if author not in professor_names]
    if not coauthors:
        return 0.4, "No coauthor network signal"
    repeated = sum(1 for author in coauthors if repeated_coauthors[author] >= 2)
    role_factor = author_role_weight(author_role)
    score = min(1.0, (0.25 + repeated / max(1, len(coauthors))) * role_factor + 0.15)
    if repeated:
        return score, f"{repeated} recurring coauthors found"
    return score, "No recurring coauthors found"


def _identifier_score(paper: dict[str, Any]) -> tuple[float, str]:
    source_ids = paper.get("source_ids", {})
    if source_ids.get("openalex_author") or source_ids.get("orcid") or source_ids.get("dblp"):
        return 1.0, "Stable author identifier matched"
    if len(paper.get("source_list", [])) >= 2 and (paper.get("doi") or paper.get("uci")):
        return 0.72, "DOI/UCI and cross-source metadata agree"
    if paper.get("doi") or paper.get("uci"):
        return 0.35, "Paper identifier exists but author identifier is not confirmed"
    return 0.0, "No DOI/UCI/author identifier signal"


def _lab_page_evidence(paper: dict[str, Any], lab_titles: list[str]) -> float:
    title = paper.get("display_title") or ""
    if not title or not lab_titles:
        return 0.0
    best = max(SequenceMatcher(None, title.lower(), lab_title.lower()).ratio() for lab_title in lab_titles)
    return 1.0 if best >= 0.92 else best * 0.65


def _career_year_score(paper: dict[str, Any]) -> float:
    year = paper.get("year")
    if not year:
        return 0.5
    if 1970 <= int(year) <= 2026:
        return 1.0
    return 0.15


def _source_confidence_score(paper: dict[str, Any]) -> float:
    values = [
        float(value)
        for value in (paper.get("source_confidence_signals") or {}).values()
        if isinstance(value, int | float)
    ]
    if values:
        return min(1.0, sum(values) / len(values))
    source_list = set(paper.get("source_list", []))
    default_map = {
        "professor_lab_page_publication": 1.0,
        "kci": 0.82,
        "openalex": 0.8,
        "dblp": 0.85,
        "crossref": 0.8,
        "riss": 0.65,
        "dbpia": 0.65,
    }
    if not source_list:
        return 0.2
    return min(1.0, sum(default_map.get(source, 0.5) for source in source_list) / len(source_list))


def _cross_source_agreement_score(paper: dict[str, Any]) -> tuple[float, str]:
    sources = paper.get("source_list", [])
    merge_confidence = float(paper.get("merge_confidence") or 0.5)
    if len(sources) >= 3:
        return min(1.0, 0.75 + merge_confidence * 0.25), f"{', '.join(sources)} refer to the same paper"
    if len(sources) == 2:
        return min(0.9, 0.55 + merge_confidence * 0.25), f"{sources[0]} and {sources[1]} refer to the same paper"
    return 0.25, "Single-source candidate"


def _apply_contamination_guards(
    score: float,
    name_score: float,
    affiliation_score: float,
    department_score: float,
    topic_score: float,
    identifier_score: float,
    author_role: str,
) -> float:
    if name_score >= 0.9 and affiliation_score < 0.25 and topic_score < 0.25:
        return min(score, 0.39)
    if name_score >= 0.9 and affiliation_score < 0.25 and identifier_score < 0.5:
        return min(score, 0.41)
    if name_score >= 0.9 and affiliation_score < 0.45 and department_score < 0.35 and topic_score < 0.35:
        return min(score, 0.58)
    if author_role == "middle_coauthor" and topic_score < 0.35:
        return min(score, 0.61)
    if name_score < 0.6:
        return min(score, 0.39)
    return score


def _warnings(
    name_score: float,
    english_score: float,
    affiliation_score: float,
    department_score: float,
    topic_score: float,
    coauthor_score: float,
    identifier_score: float,
    author_role: str,
    paper: dict[str, Any],
) -> list[str]:
    warnings: list[str] = []
    if name_score >= 0.75 and affiliation_score < 0.35:
        warnings.append("동명이인 가능성으로 검증 필요: 이름은 유사하지만 현재 학교 소속 근거가 약합니다.")
    if name_score >= 0.75 and topic_score < 0.25:
        warnings.append("동명이인 가능성으로 검증 필요: 이름은 유사하지만 연구 주제가 다릅니다.")
    if name_score >= 0.75 and coauthor_score < 0.35 and identifier_score < 0.5:
        warnings.append("동명이인 가능성으로 검증 필요: 반복 공저자 네트워크 또는 식별자 근거가 약합니다.")
    if english_score < 0.35 and not _has_korean_author_signal(paper):
        warnings.append("영문명 매칭 근거가 약합니다.")
    if department_score < 0.25:
        warnings.append("학과 소속 근거가 불명확합니다.")
    if author_role == "middle_coauthor" and topic_score < 0.35:
        warnings.append("공동저자 오염 가능성: middle_coauthor이고 공식 연구 키워드와 연결성이 낮습니다.")
    if paper.get("duplicate_status") == "duplicate_possible":
        warnings.append("다른 후보와 중복 가능성이 있으나 자동 병합하지 않았습니다.")
    for note in paper.get("merge_notes", []):
        if "여러 명" in note or "불명확" in note or "이름만" in note:
            warnings.append(note)
    return list(dict.fromkeys(warnings))


def _best_similarity(names: list[str], authors: list[str]) -> float:
    best = 0.0
    for author in authors:
        for name in names:
            best = max(best, SequenceMatcher(None, _norm(name), _norm(author)).ratio())
    return best


def _has_korean_author_signal(paper: dict[str, Any]) -> bool:
    return any(re.search(r"[가-힣]", author) for author in paper.get("authors", []))


def _tokens(text: str) -> set[str]:
    stopwords = {
        "and",
        "the",
        "for",
        "with",
        "from",
        "using",
        "based",
        "study",
        "analysis",
        "연구",
        "기반",
        "분석",
        "학과",
        "대학교",
    }
    return {
        token.lower()
        for token in re.findall(r"[A-Za-z가-힣0-9]{2,}", text or "")
        if token.lower() not in stopwords
    }


def _initial_name(name: str) -> str:
    parts = name.split()
    if len(parts) < 2:
        return name
    return f"{parts[0][0]} {parts[-1]}"


def _norm(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum() or "\uac00" <= ch <= "\ud7a3")
