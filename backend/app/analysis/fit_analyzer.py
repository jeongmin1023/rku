from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.analysis.keyword_extractor import extract_keywords, similarity
from app.analysis.trend_analyzer import recency_weight
from app.papers.author_role import author_role_weight


def analyze_fit(user_interest: str, papers: list[dict[str, Any]], evidence_confidence: str) -> dict[str, Any]:
    accepted = [paper for paper in papers if paper.get("match_status") == "accepted"]
    review = [paper for paper in papers if paper.get("match_status") == "needs_review"]
    visible = accepted + review
    emerging_like = evidence_confidence == "low" or len(accepted) < 3
    if not visible:
        return _fallback_result(user_interest)

    scored = []
    current_year = datetime.now(UTC).year
    user_keywords = extract_keywords([user_interest], top_k=6)
    for paper in visible:
        text = _paper_text(paper)
        user_topic_similarity = similarity(user_interest, text)
        paper_keywords = extract_keywords([text], paper.get("keywords"), top_k=8)
        keyword_overlap = len(set(user_keywords) & set(paper_keywords)) / max(1, len(set(user_keywords)))
        match_weight = max(0.25, min(1.0, float(paper.get("match_score") or 0.5)))
        score = (
            0.40 * user_topic_similarity
            + 0.20 * keyword_overlap
            + 0.15 * recency_weight(paper, current_year)
            + 0.15 * author_role_weight(paper.get("author_role"))
            + 0.10 * match_weight
        )
        if paper.get("match_status") == "needs_review":
            score *= 0.82
        scored.append((score, paper, paper_keywords))
    scored.sort(reverse=True, key=lambda item: item[0])
    best_score = scored[0][0] if scored else 0
    repeated_related = len([score for score, _, _ in scored if score >= 0.45])
    level = _fit_level(best_score, repeated_related, evidence_confidence, emerging_like)
    related = [_related_item(paper, score, user_interest) for score, paper, _ in scored[:3] if score >= 0.25]
    matched_keywords = extract_keywords(
        [user_interest] + [_paper_text(paper) for score, paper, _ in scored[:3] if score >= 0.25],
        top_k=7,
    )
    return {
        "fit_level": level,
        "interpretation": _interpretation(level, user_interest, matched_keywords, emerging_like),
        "matched_keywords": matched_keywords,
        "related_papers": related,
        "check_points": default_check_points(),
        "evidence_confidence": evidence_confidence,
    }


def default_check_points() -> list[str]:
    return [
        "현재 연구실에서 해당 주제를 석사 또는 학부연구 주제로 진행할 수 있는지 확인",
        "진행 중인 프로젝트와 모집 예정 주제가 공개 논문 흐름과 같은지 확인",
        "논문 중심 연구와 구현/프로젝트 중심 연구의 비중 확인",
        "필요한 선수지식과 준비 자료 확인",
    ]


def _fallback_result(user_interest: str) -> dict[str, Any]:
    return {
        "fit_level": "판단 보류",
        "interpretation": "공개 논문 데이터가 제한적입니다. 연구실 소개, 교수소개 페이지, 강의 과목, 현재 프로젝트를 중심으로 컨택 시 확인이 필요합니다.",
        "matched_keywords": extract_keywords([user_interest], top_k=5),
        "related_papers": [],
        "check_points": default_check_points(),
        "evidence_confidence": "low",
    }


def _fit_level(score: float, repeated_related: int, confidence: str, emerging_like: bool) -> str:
    if emerging_like and score >= 0.55:
        return "중간, 확인 필요"
    if emerging_like:
        return "판단 보류"
    if score >= 0.72 and repeated_related >= 2:
        return "높음"
    if score >= 0.62:
        return "중간~높음"
    if score >= 0.45:
        return "중간"
    if confidence == "low":
        return "판단 보류"
    return "낮음"


def _interpretation(level: str, user_interest: str, keywords: list[str], emerging_like: bool) -> str:
    keyword_text = ", ".join(keywords[:4]) if keywords else user_interest
    if level == "판단 보류":
        return f"'{user_interest}'와 직접 연결된 공개 근거가 충분하지 않습니다. {keyword_text} 관련 가능성은 연구실 소개와 현재 모집 주제를 통해 확인하는 것이 좋습니다."
    if level == "중간, 확인 필요":
        return f"공개 논문 데이터는 제한적이지만 {keyword_text}와 맞닿아 있는 신호가 있습니다. 신임 연구자, 산업체 경력, 프로젝트 키워드가 실제 모집 주제와 연결되는지는 컨택 시 확인이 필요합니다."
    if level in {"높음", "중간~높음"}:
        return f"최근 공개 논문에서 {keyword_text}와 연결되는 신호가 보입니다. 이 결과는 교수님 평가가 아니라 관심 주제와 연구 방향의 연결성 해석이며, 실제 진행 가능 주제는 컨택 시 확인해야 합니다."
    if level == "중간":
        return f"{keyword_text} 일부가 공개 논문과 맞닿아 있지만 관심 주제 전체를 직접 다룬다고 보기는 어렵습니다. 관련 프로젝트 또는 세부 주제 가능성을 확인해볼 만합니다."
    return f"공개 논문 기준으로는 '{user_interest}'와 직접 연결되는 근거가 제한적입니다. 이는 평가가 아니며 공개 데이터 밖의 프로젝트나 신임 연구 방향은 별도 확인이 필요합니다."


def _related_item(paper: dict[str, Any], score: float, user_interest: str) -> dict[str, Any]:
    return {
        "id": paper.get("id"),
        "title": paper.get("display_title"),
        "year": paper.get("year"),
        "venue": paper.get("venue"),
        "source_list": paper.get("source_list", []),
        "citation_signals": paper.get("citation_signals", {}),
        "match_status": paper.get("match_status"),
        "author_role": paper.get("author_role"),
        "category": "interest_related",
        "category_reason": "사용자 관심 주제와 제목/초록/키워드 유사도를 기준으로 선택했습니다.",
        "why_read_this": f"이 논문은 사용자의 관심 주제인 '{user_interest}'와 가장 직접적으로 연결되는 후보입니다.",
        "connection_reason": "관심 주제 키워드와 제목/초록/키워드 사이의 유사도가 감지됩니다.",
        "connection_signal": round(score, 3),
    }


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
