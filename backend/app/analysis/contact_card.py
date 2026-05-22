from __future__ import annotations

from typing import Any

from app.analysis.fit_analyzer import analyze_fit, default_check_points


def build_contact_card(
    professor: Any,
    papers: list[dict[str, Any]],
    analysis: dict[str, Any],
    user_interest: str | None = None,
) -> dict[str, Any]:
    fit = analyze_fit(user_interest, papers, analysis.get("evidence_confidence", "low")) if user_interest else None
    representative = (analysis.get("representative_papers") or [])[:1]
    recent = (analysis.get("recent_important_papers") or analysis.get("recent_papers") or [])[:1]
    interest_related = (fit or {}).get("related_papers", [])[:1]

    reading_list: list[dict[str, Any]] = []
    reading_list.extend(
        _reading_items(
            representative,
            "대표 논문",
            "이 논문은 교수님의 기존 연구축을 이해하기 좋은 대표 논문입니다.",
        )
    )
    reading_list.extend(
        _reading_items(
            recent,
            "최근 연구 논문",
            "이 논문은 최근 3~5년 내 연구 방향을 파악하기 좋습니다.",
        )
    )
    reading_list.extend(
        _reading_items(
            interest_related,
            "관심주제 관련 논문",
            "이 논문은 사용자의 관심 주제와 가장 직접적으로 연결되는 후보입니다.",
        )
    )

    if not reading_list:
        reading_list.append(
            {
                "title": "공개 논문 데이터 제한",
                "year": None,
                "why_read": "논문보다 연구실 소개, 교수소개 페이지, 프로젝트 정보를 먼저 확인하세요.",
                "category": "확인 필요",
            }
        )

    keywords = analysis.get("recent_keywords") or analysis.get("overall_keywords") or []
    email_points = [
        f"{keyword} 관련 공개 연구 흐름을 보고 관심을 갖게 되었음을 구체적으로 언급"
        for keyword in keywords[:3]
    ] or ["교수소개 페이지의 연구 키워드와 본인의 관심 주제가 만나는 지점을 구체적으로 언급"]

    return {
        "professor_id": professor.id,
        "professor_name": professor.name,
        "reading_list": reading_list[:3],
        "questions": [
            "현재 연구실에서 해당 주제를 석사 주제로 진행할 수 있나요?",
            "관련 프로젝트나 과제가 진행 중인가요?",
            "학부 단계에서 준비하면 좋은 선수지식은 무엇인가요?",
            "논문 중심 연구와 프로젝트 중심 연구의 비중은 어느 정도인가요?",
            "학부연구생 또는 예비 대학원생이 참여할 수 있는 주제가 있나요?",
        ],
        "email_points": email_points,
        "check_points": default_check_points(),
        "evidence_confidence": analysis.get("evidence_confidence", "low"),
    }


def _reading_items(items: list[dict[str, Any]], category: str, why: str) -> list[dict[str, Any]]:
    return [
        {
            "id": item.get("id"),
            "title": item.get("title"),
            "year": item.get("year"),
            "venue": item.get("venue"),
            "why_read": item.get("why_read_this") or why,
            "category": category,
        }
        for item in items
    ]
