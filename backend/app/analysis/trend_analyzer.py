from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from app.analysis.keyword_extractor import extract_keywords
from app.analysis.llm_professor_analyzer import analyze_professor_with_llm
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
    weak = [paper for paper in papers if paper.get("match_status") == "weak_candidate"]
    rejected = [paper for paper in papers if paper.get("match_status") == "rejected"]

    recent_3 = [paper for paper in accepted if recency_weight(paper, current_year) == 1.0]
    five_year = [paper for paper in accepted if _year_gte(paper, current_year - 5)]

    analysis_pool = accepted + _low_weight_review(review)
    if not analysis_pool:
        analysis_pool = review + _low_weight_review(weak)

    exclude_terms = _exclude_terms(professor)
    official_list = extract_keywords([official_keywords or ""], top_k=6, exclude_terms=exclude_terms)

    warnings: list[str] = []

    if review:
        warnings.append("검증 필요 논문 일부 포함: needs_review 논문은 보조 근거로만 사용했습니다.")

    if weak and not accepted:
        warnings.append("accepted 논문이 부족하여 weak_candidate는 경향 판단이 아닌 후보 보존 목적으로만 참고합니다.")

    if _homonym_warnings(papers):
        warnings.append("동명이인 가능성으로 검증 필요: 일부 논문 후보에서 소속/주제/공저자 근거가 약합니다.")

    base_texts = _weighted_texts(analysis_pool, current_year)

    if official_keywords:
        base_texts.extend([official_keywords, official_keywords])

    recent_keywords = extract_keywords(
        _weighted_texts(recent_3 or five_year or analysis_pool, current_year),
        _concepts(recent_3 or five_year),
        top_k=5,
        exclude_terms=exclude_terms,
    )

    five_year_keywords = extract_keywords(
        _weighted_texts(five_year or analysis_pool, current_year),
        _concepts(five_year),
        top_k=5,
        exclude_terms=exclude_terms,
    )

    overall_keywords = extract_keywords(
        base_texts,
        _concepts(analysis_pool),
        top_k=8,
        exclude_terms=exclude_terms,
    )

    if not overall_keywords and official_list:
        overall_keywords = official_list

    if len(overall_keywords) < 2:
        warnings.append("공개 논문 키워드 부족")

    timeline = _timeline(analysis_pool, current_year, exclude_terms)

    emerging = _is_emerging_lab(professor, accepted, five_year)
    if emerging:
        warnings.extend(
            [
                "공개 논문 데이터는 제한적입니다.",
                "연구실 소개, 교수소개 페이지, 강의 과목, 프로젝트, 특허, 산업체 경력 키워드를 대체 근거로 함께 확인하세요.",
                "현재 모집 주제는 컨택 시 확인이 필요합니다.",
            ]
        )

    evidence_confidence = confidence_for_papers(accepted, review, emerging)
    analysis_type = "emerging_lab" if emerging else "domestic_db_based"

    representative = select_representative_papers(
        accepted or review or weak,
        overall_keywords,
        current_year,
    )

    recent_important = select_recent_important_papers(
        recent_3 or five_year or accepted or review,
        recent_keywords,
        current_year,
    )

    supporting = select_supporting_papers(review + weak, current_year)

    llm_input_papers = _papers_for_single_llm_analysis(
        representative=representative,
        recent_important=recent_important,
        supporting=supporting,
        source_papers=accepted + review + weak,
        limit=8,
    )

    fallback_analysis = {
        "overall_keywords": overall_keywords,
        "recent_keywords": recent_keywords,
        "five_year_keywords": five_year_keywords,
        "trend_summary": _fallback_trend_summary(five_year_keywords, recent_keywords, official_list),
        "detailed_trend_summary": "공개 논문 키워드와 공식 연구분야를 기준으로 연구 경향을 요약했습니다.",
        "main_research_axis": overall_keywords[:3],
        "recent_shift": None,
        "trend_confidence": evidence_confidence,
        "representative_papers": representative,
        "recent_important_papers": recent_important,
        "supporting_papers": supporting,
        "warnings": warnings,
    }

    llm_payload = {
        "professor_name": getattr(professor, "name", None),
        "official_keywords": official_list,
        "raw_keywords": list(dict.fromkeys([*overall_keywords, *recent_keywords, *five_year_keywords])),
        "papers": llm_input_papers,
        "evidence_confidence": evidence_confidence,
        "warnings": warnings,
    }

    llm_result = analyze_professor_with_llm(llm_payload, fallback_analysis)

    overall_keywords = llm_result.get("overall_keywords", overall_keywords)
    recent_keywords = llm_result.get("recent_keywords", recent_keywords)
    five_year_keywords = llm_result.get("five_year_keywords", five_year_keywords)

    representative = _apply_llm_paper_results(
        representative,
        llm_result.get("representative_papers", []),
    )

    recent_important = _apply_llm_paper_results(
        recent_important,
        llm_result.get("recent_important_papers", []),
    )

    supporting = _apply_llm_paper_results(
        supporting,
        llm_result.get("supporting_papers", []),
    )

    llm_used = bool(llm_result.get("llm_used"))
    llm_provider = llm_result.get("llm_provider")

    return {
        "trend_summary": llm_result.get("trend_summary"),
        "detailed_trend_summary": llm_result.get("detailed_trend_summary"),
        "main_research_axis": llm_result.get("main_research_axis", []),
        "recent_shift": llm_result.get("recent_shift"),
        "recent_keywords": recent_keywords,
        "five_year_keywords": five_year_keywords,
        "overall_keywords": overall_keywords,
        "timeline": timeline,
        "trend_confidence": llm_result.get("trend_confidence") or evidence_confidence,
        "representative_papers": representative,
        "recent_important_papers": recent_important,
        "recent_papers": recent_important,
        "interest_related_papers": [],
        "supporting_papers": supporting,
        "excluded_papers_count": len(rejected),
        "evidence_confidence": evidence_confidence,
        "warnings": list(dict.fromkeys([*warnings, *(llm_result.get("warnings") or [])])),
        "analysis_type": analysis_type,
        "llm_used": llm_used,
        "llm_provider": llm_provider,
        "llm_usage_summary": {
            "professor_analysis_called": llm_used,
            "paper_count_sent_to_llm": len(llm_input_papers),
            "mode": "single_call_professor_analysis",
        },
    }


def select_representative_papers(
    papers: list[dict[str, Any]],
    keywords: list[str],
    current_year: int | None = None,
) -> list[dict[str, Any]]:
    current_year = current_year or datetime.now(UTC).year
    scored = []

    for paper in papers:
        score = (
            0.25 * _citation_signal(paper)
            + 0.25 * _topic_centrality(paper, keywords)
            + 0.20 * author_role_weight(paper.get("author_role"))
            + 0.15 * float(paper.get("match_score") or 0)
            + 0.10 * _source_confidence(paper)
            + 0.05 * recency_weight(paper, current_year)
        )
        label = "과거 대표 논문" if paper.get("year") and int(paper["year"]) < current_year - 10 else "대표 논문 후보"
        scored.append((score, paper, label))

    return [
        _paper_item(
            paper,
            category="representative",
            label=label,
            reason="인용 신호, 연구 키워드 중심성, 저자 역할, 매칭 근거를 함께 고려했습니다.",
            why="교수님의 기존 연구축을 이해하기 좋은 대표 논문입니다.",
        )
        for _, paper, label in sorted(scored, reverse=True, key=lambda item: item[0])[:3]
    ]


def select_recent_important_papers(
    papers: list[dict[str, Any]],
    keywords: list[str],
    current_year: int | None = None,
) -> list[dict[str, Any]]:
    current_year = current_year or datetime.now(UTC).year
    scored = []

    for paper in papers:
        score = (
            0.35 * recency_weight(paper, current_year)
            + 0.25 * _topic_centrality(paper, keywords)
            + 0.20 * author_role_weight(paper.get("author_role"))
            + 0.15 * float(paper.get("match_score") or 0)
            + 0.05 * _citation_signal(paper)
        )
        scored.append((score, paper))

    return [
        _paper_item(
            paper,
            category="recent_important",
            label="최근 연구 논문",
            reason="최근성, 최근 키워드 관련성, 저자 역할, 매칭 근거를 함께 고려했습니다.",
            why="최근 3~5년 연구 방향을 파악하기 좋은 논문입니다.",
        )
        for _, paper in sorted(scored, reverse=True, key=lambda item: item[0])[:3]
    ]


def select_supporting_papers(papers: list[dict[str, Any]], current_year: int | None = None) -> list[dict[str, Any]]:
    current_year = current_year or datetime.now(UTC).year
    visible = [paper for paper in papers if paper.get("match_status") in {"needs_review", "weak_candidate"}]
    scored = sorted(
        visible,
        key=lambda paper: (paper.get("match_score") or 0, recency_weight(paper, current_year)),
        reverse=True,
    )

    return [
        _paper_item(
            paper,
            category="supporting",
            label="보조 후보 논문",
            reason="검증 또는 낮은 신뢰도 후보로 보존된 논문입니다.",
            why="관심 주제와 가까워 보이면 컨택 전 추가 확인용으로 살펴볼 수 있습니다.",
        )
        for paper in scored[:5]
    ]


def confidence_for_papers(
    accepted: list[dict[str, Any]],
    review: list[dict[str, Any]],
    emerging: bool = False,
) -> str:
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

        if paper.get("match_status") == "needs_review":
            weight *= 0.6

        if paper.get("match_status") == "weak_candidate":
            weight *= 0.25

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


def _is_emerging_lab(
    professor: Any | None,
    accepted: list[dict[str, Any]],
    five_year: list[dict[str, Any]],
) -> bool:
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
        or (any(keyword in professor_text for keyword in INDUSTRY_KEYWORDS) and len(accepted) < 2)
        or (has_lab_intro and len(accepted) < 2)
    )


def _homonym_warnings(papers: list[dict[str, Any]]) -> bool:
    for paper in papers:
        warnings = paper.get("warnings") or []
        if any("동명이인" in warning or "소속" in warning for warning in warnings):
            return True
    return False


def _timeline(
    papers: list[dict[str, Any]],
    current_year: int,
    exclude_terms: list[str],
) -> dict[str, list[str]]:
    by_year: dict[int, list[dict[str, Any]]] = defaultdict(list)

    for paper in papers:
        if paper.get("year"):
            by_year[int(paper["year"])].append(paper)

    return {
        str(year): extract_keywords(
            _weighted_texts(year_papers, current_year),
            _concepts(year_papers),
            top_k=4,
            exclude_terms=exclude_terms,
        )
        for year, year_papers in sorted(by_year.items())
    }


def _older_keywords(
    papers: list[dict[str, Any]],
    current_year: int,
    exclude_terms: list[str],
) -> list[str]:
    older = [paper for paper in papers if paper.get("year") and int(paper["year"]) < current_year - 5]
    return extract_keywords(_weighted_texts(older, current_year), _concepts(older), top_k=5, exclude_terms=exclude_terms)


def _paper_text(paper: dict[str, Any]) -> str:
    return " ".join(
        [
            paper.get("title_ko") or "",
            paper.get("title_en") or "",
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


def _paper_item(
    paper: dict[str, Any],
    category: str,
    label: str,
    reason: str,
    why: str,
) -> dict[str, Any]:
    return {
        "id": paper.get("id"),
        "title": paper.get("display_title") or paper.get("title_ko") or paper.get("title_en"),
        "year": paper.get("year"),
        "venue": paper.get("venue"),
        "source_list": paper.get("source_list", []),
        "citation_signals": paper.get("citation_signals", {}),
        "match_status": paper.get("match_status"),
        "author_role": paper.get("author_role"),
        "category": category,
        "label": label,
        "category_reason": reason,
        "why_read_this": why,
        "reason": reason,
        "paper_summary": paper.get("paper_summary"),
        "main_topic": paper.get("main_topic"),
        "method_or_focus": paper.get("method_or_focus"),
        "why_it_matters": paper.get("why_it_matters"),
        "summary_limitations": paper.get("summary_limitations", []),
    }


def _timeline_for_llm(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_year: dict[int, list[dict[str, Any]]] = defaultdict(list)

    for paper in papers:
        if paper.get("year"):
            by_year[int(paper["year"])].append(paper)

    return [
        {
            "period": str(year),
            "keywords": _concepts(year_papers)[:6],
            "paper_titles": [paper.get("display_title") for paper in year_papers if paper.get("display_title")][:5],
        }
        for year, year_papers in sorted(by_year.items())
    ]


def _citation_signal(paper: dict[str, Any]) -> float:
    values = [
        value
        for value in (paper.get("citation_signals") or {}).values()
        if isinstance(value, (int, float))
    ]
    return min(max(values or [0]) / 50, 1.0)


def _topic_centrality(paper: dict[str, Any], keywords: list[str]) -> float:
    if not keywords:
        return 0.25

    text = _paper_text(paper).lower()
    return min(
        1.0,
        sum(1 for keyword in keywords if keyword.lower() in text) / max(1, min(5, len(keywords))),
    )


def _source_confidence(paper: dict[str, Any]) -> float:
    values = [
        value
        for value in (paper.get("source_confidence_signals") or {}).values()
        if isinstance(value, (int, float))
    ]

    if not values:
        return 0.5

    return min(1.0, sum(values) / len(values))


def _year_gte(paper: dict[str, Any], minimum_year: int) -> bool:
    return bool(paper.get("year") and int(paper["year"]) >= minimum_year)


def _exclude_terms(professor: Any | None) -> list[str]:
    if not professor:
        return []

    return [
        getattr(professor, "name", "") or "",
        getattr(professor, "english_name", "") or "",
        getattr(professor, "university", "") or "",
        getattr(professor, "department", "") or "",
    ]


def _papers_for_single_llm_analysis(
    representative: list[dict[str, Any]],
    recent_important: list[dict[str, Any]],
    supporting: list[dict[str, Any]],
    source_papers: list[dict[str, Any]],
    limit: int = 8,
) -> list[dict[str, Any]]:
    source_map = {_paper_identity(paper): paper for paper in source_papers}
    selected_items = [*representative, *recent_important, *supporting]

    seen: set[str] = set()
    result: list[dict[str, Any]] = []

    for item in selected_items:
        key = _item_identity(item)

        if key in seen:
            continue

        seen.add(key)
        source = source_map.get(key)

        if not source:
            continue

        if source.get("match_status") == "rejected":
            continue

        result.append(
            {
                "id": key,
                "title": source.get("display_title") or source.get("title_ko") or source.get("title_en"),
                "year": source.get("year"),
                "venue": source.get("venue"),
                "abstract": source.get("abstract"),
                "keywords": source.get("keywords") or [],
                "source_list": source.get("source_list") or [],
                "match_status": source.get("match_status"),
                "author_role": source.get("author_role"),
                "category_hint": item.get("category"),
                "category_reason": item.get("category_reason"),
                "why_read_this": item.get("why_read_this"),
            }
        )

        if len(result) >= limit:
            break

    return result


def _apply_llm_paper_results(
    base_items: list[dict[str, Any]],
    llm_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    llm_map: dict[str, dict[str, Any]] = {}

    for item in llm_items:
        paper_id = item.get("paper_id")
        if paper_id:
            llm_map[str(paper_id)] = item

    merged = []

    for base in base_items:
        key = _item_identity(base)
        llm = llm_map.get(key) or llm_map.get(str(base.get("id")))

        clone = dict(base)

        if llm:
            clone["paper_summary"] = llm.get("paper_summary") or clone.get("paper_summary")
            clone["category_reason"] = llm.get("category_reason") or clone.get("category_reason")
            clone["why_read_this"] = llm.get("why_read_this") or clone.get("why_read_this")
            clone["llm_used"] = True
            clone["llm_provider"] = "gemini"

        merged.append(clone)

    return merged


def _paper_identity(paper: dict[str, Any]) -> str:
    paper_id = paper.get("id")
    if paper_id is not None:
        return f"id:{paper_id}"

    title = paper.get("display_title") or paper.get("title") or paper.get("title_ko") or paper.get("title_en") or ""
    year = paper.get("year") or ""
    return f"title:{title}|year:{year}"


def _item_identity(item: dict[str, Any]) -> str:
    paper_id = item.get("id")
    if paper_id is not None:
        return f"id:{paper_id}"

    title = item.get("title") or item.get("display_title") or ""
    year = item.get("year") or ""
    return f"title:{title}|year:{year}"


def _fallback_trend_summary(
    five_year_keywords: list[str],
    recent_keywords: list[str],
    official_keywords: list[str],
) -> str:
    if five_year_keywords and recent_keywords:
        return (
            f"최근 5년간 {', '.join(five_year_keywords[:3])} 관련 연구가 반복되며, "
            f"최근에는 {', '.join(recent_keywords[:3])} 주제가 나타나는 경향이 있습니다."
        )

    if five_year_keywords:
        return f"최근 5년간 {', '.join(five_year_keywords[:3])} 관련 연구 흐름이 확인됩니다."

    if official_keywords:
        return f"공개 논문 데이터가 제한적이어서, 공식 연구분야 기준으로 {', '.join(official_keywords[:3])} 분야를 중심으로 확인됩니다."

    return "공개 데이터가 부족하여 연구 경향을 확정하기 어렵습니다. 컨택 시 현재 모집 주제와 진행 중인 연구를 확인하는 것이 좋습니다."