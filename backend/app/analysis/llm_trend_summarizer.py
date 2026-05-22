from __future__ import annotations
from app.analysis.llm_professor_analyzer import analyze_professor_with_llm

import json
from typing import Any

from app.analysis import llm_client


def summarize_trend(payload: dict[str, Any]) -> dict[str, Any]:
    """Turn cleaned evidence into readable trend text.

    Gemini is used only for wording already-cleaned evidence. If no key is
    configured or any call/parsing step fails, the deterministic template is
    returned with the same JSON shape.
    """

    fallback = template_summary(payload)
    try:
        data = llm_client.call_llm_json(_prompt(payload))
    except (llm_client.LLMUnavailable, llm_client.LLMCallError, ValueError) as exc:
        fallback["warnings"] = list(fallback.get("warnings") or [])
        fallback["warnings"].append(f"LLM trend_summary fallback: {exc}")
        fallback["llm_used"] = False
        fallback["llm_provider"] = None
        return fallback

    warnings = list(dict.fromkeys([*_as_list(data.get("warnings")), *fallback["warnings"]]))
    confidence = _confidence(data.get("trend_confidence") or data.get("confidence"), fallback["trend_confidence"])
    result = {
        "trend_summary": _clean_text(data.get("trend_summary")) or fallback["trend_summary"],
        "detailed_trend_summary": _clean_text(data.get("detailed_trend_summary")) or fallback["detailed_trend_summary"],
        "main_research_axis": _as_list(data.get("main_research_axis"))[:4] or fallback["main_research_axis"],
        "recent_shift": _clean_text(data.get("recent_shift")) or fallback["recent_shift"],
        "trend_confidence": confidence,
        "confidence": confidence,
        "warnings": warnings,
        "llm_used": True,
        "llm_provider": llm_client.provider_name(),
    }
    return result


def template_summary(payload: dict[str, Any]) -> dict[str, Any]:
    professor_name = payload.get("professor_name") or "해당 교수님"
    official = payload.get("official_keywords") or []
    recent_3 = payload.get("recent_keywords") or payload.get("recent_3_year_keywords") or []
    recent_5 = payload.get("five_year_keywords") or payload.get("recent_5_year_keywords") or []
    older = payload.get("older_keywords") or []
    warnings = list(payload.get("warnings") or [])
    confidence = payload.get("evidence_confidence") or "low"

    emerging_limited = "공개 논문 데이터는 제한적입니다." in warnings

    if recent_5 and not emerging_limited:
        summary = (
            f"최근 5년간 {', '.join(recent_5[:4])} 관련 연구 신호가 반복되며, "
            f"최근에는 {', '.join((recent_3 or recent_5)[:3])} 주제가 나타나는 경향이 있습니다."
        )
        detail = (
            f"{professor_name}의 공개 논문 후보에서는 {', '.join(recent_5[:5])} 흐름이 확인됩니다. "
            f"최근 3년 자료에서는 {', '.join((recent_3 or recent_5)[:4])} 키워드가 상대적으로 두드러집니다. "
            "needs_review 논문은 보조 근거로만 반영했으며, 실제 진행 중인 모집 주제는 컨택 시 확인하는 것이 좋습니다."
        )
        axis = recent_5[:3]
        shift = f"{', '.join(older[:2])}에서 {', '.join(recent_3[:2])} 쪽으로 확장되는 신호가 있습니다." if older and recent_3 else None
    elif recent_5 and emerging_limited:
        summary = (
            "공개 논문 데이터는 제한적입니다. 다만 공개 후보 기준으로는 "
            f"{', '.join(recent_5[:4])} 관련 연구 신호가 확인됩니다."
        )
        detail = (
            f"{professor_name}의 공개 논문 데이터는 아직 제한적입니다. "
            f"현재 확인 가능한 후보에서는 {', '.join(recent_5[:5])} 키워드가 보이며, "
            "연구실 소개와 현재 모집 주제를 함께 확인하는 것이 좋습니다."
        )
        axis = recent_5[:3]
        shift = None
    elif official:
        summary = f"공개 논문 데이터가 제한적이어서, 공식 연구분야 기준으로 {', '.join(official[:4])} 분야를 중심으로 확인됩니다."
        detail = (
            f"{professor_name}의 공개 논문 키워드는 충분하지 않습니다. "
            f"현재는 교수소개 페이지와 연구실 소개에 나온 {', '.join(official[:5])} 정보를 중심으로 연구 방향을 참고할 수 있습니다. "
            "현재 모집 주제와 진행 중인 프로젝트는 컨택 시 직접 확인해야 합니다."
        )
        axis = official[:3]
        shift = None
    else:
        summary = "공개 데이터가 부족하여 연구 경향을 확정하기 어렵습니다. 컨택 시 현재 모집 주제와 진행 중인 연구를 확인하는 것이 좋습니다."
        detail = summary
        axis = []
        shift = None
        warnings.append("공개 논문 키워드 부족")

    return {
        "trend_summary": summary,
        "detailed_trend_summary": detail,
        "main_research_axis": axis,
        "recent_shift": shift,
        "trend_confidence": confidence,
        "confidence": confidence,
        "warnings": list(dict.fromkeys(warnings)),
        "llm_used": False,
        "llm_provider": None,
    }


def _prompt(payload: dict[str, Any]) -> str:
    safe_payload = {
        "professor_name": payload.get("professor_name"),
        "official_keywords": payload.get("official_keywords") or [],
        "overall_keywords": payload.get("overall_keywords") or [],
        "recent_keywords": payload.get("recent_keywords") or payload.get("recent_3_year_keywords") or [],
        "five_year_keywords": payload.get("five_year_keywords") or payload.get("recent_5_year_keywords") or [],
        "timeline": payload.get("timeline") or [],
        "papers": [
            {
                "title": paper.get("title") or paper.get("display_title"),
                "year": paper.get("year"),
                "paper_summary": paper.get("paper_summary"),
                "match_status": paper.get("match_status"),
                "source_list": paper.get("source_list") or [],
            }
            for paper in payload.get("papers", [])[:12]
        ],
        "evidence_confidence": payload.get("evidence_confidence"),
        "warnings": payload.get("warnings") or [],
    }
    return f"""
Generate LabFit research trend wording from cleaned evidence.
LabFit is not a professor ranking, scoring, or evaluation product.
Use only the provided keywords, timeline, paper titles, paper summaries, match status, source list, and warnings.
Do not invent papers, citations, impact factor, lab atmosphere, or unsupported research topics.
Use neutral Korean expressions such as 공개 데이터 기준, 검증 필요, 확인 필요, 공식 연구분야 기반.
Avoid professor quality judgments.

Return JSON:
{{
  "trend_summary": "one Korean sentence for a professor card",
  "detailed_trend_summary": "3-5 Korean sentences for a detail page",
  "main_research_axis": ["2-4 axes"],
  "recent_shift": "recent change or null",
  "trend_confidence": "high | medium | low",
  "warnings": []
}}

Evidence JSON:
{json.dumps(safe_payload, ensure_ascii=False)}
""".strip()


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def _confidence(value: Any, fallback: str) -> str:
    text = str(value or "").strip().lower()
    return text if text in {"high", "medium", "low"} else fallback
