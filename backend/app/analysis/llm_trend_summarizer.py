from __future__ import annotations

import os
from typing import Any


def summarize_trend(payload: dict[str, Any]) -> dict[str, Any]:
    """Summarize cleaned evidence into readable trend text.

    The MVP does not require an external LLM key. If a key is later configured,
    this function is the single extension point. The fallback is intentionally
    evidence-only and never evaluates or ranks professors.
    """

    if not os.getenv("LABFIT_LLM_API_KEY"):
        return template_summary(payload)
    # External LLM integration is deliberately not implemented in the MVP so the
    # service remains offline-safe. Keep the same JSON shape for future wiring.
    return template_summary(payload)


def template_summary(payload: dict[str, Any]) -> dict[str, Any]:
    professor_name = payload.get("professor_name") or "해당 교수님"
    official = payload.get("official_keywords") or []
    recent_3 = payload.get("recent_3_year_keywords") or []
    recent_5 = payload.get("recent_5_year_keywords") or []
    older = payload.get("older_keywords") or []
    warnings = list(payload.get("warnings") or [])
    confidence = payload.get("evidence_confidence") or "low"

    emerging_limited = "공개 논문 데이터는 제한적입니다." in warnings

    if recent_5 and not emerging_limited:
        summary = (
            f"최근 5년간 {', '.join(recent_5[:4])} 관련 키워드가 반복되며, "
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
            f"공개 논문 데이터는 제한적입니다. 다만 공개 후보 기준으로는 "
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
        "confidence": confidence,
        "warnings": list(dict.fromkeys(warnings)),
    }
