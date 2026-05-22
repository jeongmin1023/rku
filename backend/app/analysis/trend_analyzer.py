from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from app.analysis.keyword_extractor import extract_keywords
from app.papers.author_role import author_role_weight


EMERGING_KEYWORDS = ("조교수", "신임", "assistant professor")
INDUSTRY_KEYWORDS = ("연구소", "기업", "ai lab", "samsung", "lg", "naver", "kakao", "etri")


def analyze_trends(
    papers: list[dict[str, Any]],
    official_keywords: str | None = None,
    professor: Any | None = None,
) -> dict[str, Any]:
    current_year = datetime.now(UTC).year
    accepted = [paper for paper in papers if paper.get("match_status") == "accepted"]
    review = [paper for paper in papers if paper.get("match_status") == "needs_review"]
    recent_3 = [paper for paper in accepted if recency_weight(paper, current_year) == 1.0]
    five_year = [paper for paper in accepted if _year_gte(paper, current_year - 5)]
    emerging = _is_emerging_lab(professor, accepted, five_year)

    warnings: list[str] = []
    if review:
        warnings.append("검증 필요 논문 일부 포함: needs_review 논문은 보조 근거로만 사용했습니다.")
    if _homonym_warnings(papers):
        warnings.append("동명이인 가능성으로 검증 필요: 일부 논문 후보에서 소속/주제/공저자 근거가 약합니다.")
    if emerging:
        warnings.extend(
            [
                "공개 논문 데이터는 제한적입니다.",
                "연구실 소개, 교수소개 페이지, 강의 과목, 프로젝트, 특허, 산업체 경력 키워드를 대체 근거로 함께 확인하세요.",
                "현재 모집 주제는 컨택 시 확인이 필요합니다.",
            ]
        )

    analysis_pool = accepted + _low_weight_review(review)
    if not analysis_pool:
        analysis_pool = review

    base_texts = _weighted_texts(analysis_pool, current_year)
    if official_keywords:
        base_texts.extend([official_keywords, official_keywords])
    recent_keywords = extract_keywords(
        _weighted_texts(recent_3 or five_year or analysis_pool, current_year),
        _concepts(recent_3 or five_year),
        top_k=6,
    )
    five_year_keywords = extract_keywords(
        _weighted_texts(five_year or analysis_pool, current_year),
        _concepts(five_year),
        top_k=7,
    )
    overall_keywords = extract_keywords(base_texts, _concepts(analysis_pool), top_k=8)

    timeline: dict[str, list[str]] = {}
    by_year: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for paper in analysis_pool:
        if paper.get("year"):
            by_year[int(paper["year"])].append(paper)
    for year, year_papers in sorted(by_year.items()):
        timeline[str(year)] = extract_keywords(_weighted_texts(year_papers, current_year), _concepts(year_papers), top_k=4)

    evidence_confidence = confidence_for_papers(accepted, review, emerging)
    analysis_type = "emerging_lab" if emerging else "paper_based"
    return {
        "trend_summary": _summary(recent_keywords, five_year_keywords, overall_keywords, review, analysis_type),
        "recent_keywords": recent_keywords,
        "five_year_keywords": five_year_keywords,
        "overall_keywords": overall_keywords,
        "timeline": timeline,
        "representative_papers": select_representative_papers(accepted or analysis_pool, overall_keywords, current_year),
        "recent_papers": select_recent_papers(recent_3 or five_year or analysis_pool, recent_keywords, current_year),
        "evidence_confidence": evidence_confidence,
        "warnings": list(dict.fromkeys(warnings)),
        "analysis_type": analysis_type,
    }


def select_representative_papers(
    papers: list[dict[str, Any]],
    keywords: list[str],
    current_year: int | None = None,
) -> list[dict[str, Any]]:
    current_year = current_year or datetime.now(UTC).year
    scored = []
    for paper in papers:
        keyword_bonus = sum(1 for keyword in keywords if keyword.lower() in _paper_text(paper).lower())
        citation_values = [value for value in (paper.get("citation_signals") or {}).values() if isinstance(value, int)]
        citations = max(citation_values or [0])
        role_weight = author_role_weight(paper.get("author_role"))
        score = citations + keyword_bonus * 8 + role_weight * 12 + paper.get("match_score", 0) * 20
        label = "과거 대표 논문" if paper.get("year") and paper["year"] < current_year - 10 else "대표 논문 후보"
        scored.append((score, paper, label))
    return [
        _paper_item(paper, label=label, reason="인용 신호, 연구 키워드 연결성, 저자 역할을 함께 고려했습니다.")
        for _, paper, label in sorted(scored, reverse=True, key=lambda item: item[0])[:3]
    ]


def select_recent_papers(
    papers: list[dict[str, Any]],
    keywords: list[str],
    current_year: int | None = None,
) -> list[dict[str, Any]]:
    current_year = current_year or datetime.now(UTC).year
    scored = []
    for paper in papers:
        keyword_bonus = sum(1 for keyword in keywords if keyword.lower() in _paper_text(paper).lower())
        score = (
            recency_weight(paper, current_year) * 30
            + author_role_weight(paper.get("author_role")) * 8
            + keyword_bonus * 6
            + paper.get("match_score", 0) * 20
        )
        scored.append((score, paper))
    return [
        _paper_item(paper, label="최근 연구 흐름", reason="최근성, 저자 역할, 연구 키워드 연결성을 기준으로 골랐습니다.")
        for _, paper in sorted(scored, reverse=True, key=lambda item: item[0])[:3]
    ]


def confidence_for_papers(accepted: list[dict[str, Any]], review: list[dict[str, Any]], emerging: bool = False) -> str:
    if emerging:
        return "low"
    if len(accepted) >= 5 and len(review) <= len(accepted):
        return "high"
    if len(accepted) >= 2 or len(review) >= 2:
        return "medium"
    return "low"


def recency_weight(paper: dict[str, Any], current_year: int | None = None) -> float:
    current_year = current_year or datetime.now(UTC).year
    year = paper.get("year")
    if not year:
        return 0.4
    age = current_year - int(year)
    if age <= 3:
        return 1.0
    if age <= 5:
        return 0.8
    if age <= 10:
        return 0.5
    return 0.25


def _weighted_texts(papers: list[dict[str, Any]], current_year: int) -> list[str]:
    texts: list[str] = []
    for paper in papers:
        weight = recency_weight(paper, current_year) * author_role_weight(paper.get("author_role"))
        repeats = max(1, round(weight * 4))
        texts.extend([_paper_text(paper)] * repeats)
    return texts


def _low_weight_review(review: list[dict[str, Any]]) -> list[dict[str, Any]]:
    weighted = []
    for paper in review:
        clone = dict(paper)
        clone["match_score"] = min(float(clone.get("match_score") or 0), 0.62)
        weighted.append(clone)
    return weighted


def _is_emerging_lab(professor: Any | None, accepted: list[dict[str, Any]], five_year: list[dict[str, Any]]) -> bool:
    professor_text = " ".join(
        str(value or "")
        for value in [
            getattr(professor, "title", "") if professor else "",
            getattr(professor, "lab_name", "") if professor else "",
            getattr(professor, "official_keywords", "") if professor else "",
        ]
    ).lower()
    has_lab_intro = bool(getattr(professor, "lab_name", None) or getattr(professor, "lab_url", None)) if professor else False
    return (
        len(accepted) < 3
        or len(five_year) < 2
        or any(keyword in professor_text for keyword in EMERGING_KEYWORDS)
        or any(keyword in professor_text for keyword in INDUSTRY_KEYWORDS)
        or (has_lab_intro and len(accepted) < 2)
    )


def _homonym_warnings(papers: list[dict[str, Any]]) -> bool:
    for paper in papers:
        warnings = paper.get("warnings") or []
        if any("동명이인" in warning for warning in warnings):
            return True
    return False


def _paper_text(paper: dict[str, Any]) -> str:
    return " ".join(
        [
            paper.get("display_title") or "",
            paper.get("abstract") or "",
            " ".join(paper.get("keywords") or []),
            paper.get("venue") or "",
        ]
    )


def _concepts(papers: list[dict[str, Any]]) -> list[str]:
    concepts: list[str] = []
    for paper in papers:
        concepts.extend(paper.get("keywords") or [])
    return concepts


def _paper_item(paper: dict[str, Any], label: str, reason: str) -> dict[str, Any]:
    return {
        "id": paper.get("id"),
        "title": paper.get("display_title"),
        "year": paper.get("year"),
        "venue": paper.get("venue"),
        "citation_signals": paper.get("citation_signals", {}),
        "match_status": paper.get("match_status"),
        "author_role": paper.get("author_role"),
        "label": label,
        "reason": reason,
    }


def _summary(
    recent_keywords: list[str],
    five_year_keywords: list[str],
    overall_keywords: list[str],
    review: list[dict[str, Any]],
    analysis_type: str,
) -> str:
    if analysis_type == "emerging_lab":
        basis = ", ".join(five_year_keywords[:4] or overall_keywords[:4]) or "교수소개 페이지 키워드"
        return f"공개 논문 데이터는 제한적입니다. 현재는 {basis} 관련 공개 정보와 연구실 소개를 중심으로 연구 방향을 확인할 수 있습니다."
    recent = ", ".join(recent_keywords[:4]) or "최근 키워드"
    five = ", ".join(five_year_keywords[:4]) or "최근 5년 키워드"
    suffix = " 검증 필요 논문 일부가 보조 근거로 포함되었습니다." if review else ""
    return f"최근 3년에는 {recent} 흐름이 보이며, 최근 5년 기준으로는 {five} 키워드가 반복됩니다.{suffix}"


def _year_gte(paper: dict[str, Any], minimum_year: int) -> bool:
    return bool(paper.get("year") and int(paper["year"]) >= minimum_year)
