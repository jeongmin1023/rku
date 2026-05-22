from __future__ import annotations

import json
from typing import Any

from app.analysis import llm_client


def analyze_professor_with_llm(
    payload: dict[str, Any],
    fallback: dict[str, Any],
) -> dict[str, Any]:
    """
    교수님 1명에 대해 Gemini를 1번만 호출해서
    키워드, 연구 경향, 논문 요약, 논문 분류 이유를 한 번에 받는다.
    실패하면 fallback을 그대로 반환한다.
    """
    if not llm_client.is_llm_available():
        fallback["llm_used"] = False
        fallback["llm_provider"] = None
        fallback["warnings"] = list(fallback.get("warnings") or [])
        fallback["warnings"].append("LLM 비활성화: Gemini API 키가 없거나 환경변수가 설정되지 않았습니다.")
        return fallback

    prompt = _build_prompt(payload)

    try:
        result = llm_client.call_llm_json(prompt)
    except Exception as exc:
        fallback["llm_used"] = False
        fallback["llm_provider"] = None
        fallback["warnings"] = list(fallback.get("warnings") or [])
        fallback["warnings"].append(f"LLM 종합 분석 fallback: {exc}")
        return fallback

    normalized = _normalize_result(result, fallback)
    normalized["llm_used"] = True
    normalized["llm_provider"] = "gemini"
    return normalized


def _build_prompt(payload: dict[str, Any]) -> str:
    safe_payload = json.dumps(payload, ensure_ascii=False)

    return f"""
너는 대학원 진학 희망자를 돕는 연구실 탐색 보조자다.

아래 데이터는 특정 교수님의 공개 논문 후보와 공식 연구분야에서 추출한 정보다.
너의 역할은 교수님을 평가하는 것이 아니라, 학생이 연구실 방향을 이해할 수 있도록
논문 기반 연구 경향과 읽을 논문을 정리하는 것이다.

중요 규칙:
- 교수님을 평가하지 마라.
- 교수님 순위, 점수, 추천 표현을 쓰지 마라.
- "우수한 교수", "연구력이 높다", "논문 퀄리티가 좋다" 같은 표현 금지.
- 제공된 논문 제목, 초록, 키워드, 연도, 출처 안에서만 판단해라.
- 없는 논문, 없는 키워드, 없는 인용수, 없는 IF를 만들지 마라.
- rejected 논문은 사용하지 마라.
- needs_review 논문은 "검증 필요 후보"라고 표시해라.
- 데이터가 부족하면 "공개 데이터 기준", "확인 필요"라고 표현해라.
- 응답은 반드시 JSON만 반환해라. 마크다운, 설명문, 코드블록 금지.

해야 할 일:
1. 의미 없는 반복 단어를 제거하고 연구 주제 키워드를 정리한다.
2. 최근 3~5년 연구 경향을 한 문장으로 요약한다.
3. 상세 연구 경향을 3~5문장으로 작성한다.
4. 대표 논문, 최근 연구 논문, 보조 후보 논문을 고른다.
5. 각 논문에 paper_summary, category_reason, why_read_this를 작성한다.
6. 논문 요약은 초록이 있으면 초록 중심, 초록이 없으면 제목/키워드 기준이라고 명시한다.

입력 데이터:
{safe_payload}

반환 JSON 형식:
{{
  "overall_keywords": ["키워드1", "키워드2"],
  "recent_keywords": ["키워드1", "키워드2"],
  "five_year_keywords": ["키워드1", "키워드2"],
  "trend_summary": "교수님 카드에 표시할 한 문장",
  "detailed_trend_summary": "상세 페이지용 3~5문장",
  "main_research_axis": ["연구축1", "연구축2"],
  "recent_shift": "최근 변화 설명 또는 null",
  "trend_confidence": "high | medium | low",
  "representative_papers": [
    {{
      "paper_id": "입력 paper id",
      "paper_summary": "논문 요약 2~3문장",
      "category_reason": "대표 논문으로 분류한 이유",
      "why_read_this": "학생이 이 논문을 읽어야 하는 이유"
    }}
  ],
  "recent_important_papers": [
    {{
      "paper_id": "입력 paper id",
      "paper_summary": "논문 요약 2~3문장",
      "category_reason": "최근 연구 논문으로 분류한 이유",
      "why_read_this": "학생이 이 논문을 읽어야 하는 이유"
    }}
  ],
  "supporting_papers": [
    {{
      "paper_id": "입력 paper id",
      "paper_summary": "논문 요약 2~3문장",
      "category_reason": "보조 후보로 둔 이유",
      "why_read_this": "추가 확인용으로 볼 이유"
    }}
  ],
  "warnings": []
}}
"""


def _normalize_result(result: dict[str, Any], fallback: dict[str, Any]) -> dict[str, Any]:
    def list_value(key: str, default: list[Any] | None = None) -> list[Any]:
        value = result.get(key)
        if isinstance(value, list):
            return value
        return default or []

    def str_value(key: str, default: str | None = None) -> str | None:
        value = result.get(key)
        if isinstance(value, str):
            return value
        return default

    return {
        "overall_keywords": list_value("overall_keywords", fallback.get("overall_keywords", [])),
        "recent_keywords": list_value("recent_keywords", fallback.get("recent_keywords", [])),
        "five_year_keywords": list_value("five_year_keywords", fallback.get("five_year_keywords", [])),
        "trend_summary": str_value("trend_summary", fallback.get("trend_summary")),
        "detailed_trend_summary": str_value("detailed_trend_summary", fallback.get("detailed_trend_summary")),
        "main_research_axis": list_value("main_research_axis", fallback.get("main_research_axis", [])),
        "recent_shift": str_value("recent_shift", fallback.get("recent_shift")),
        "trend_confidence": str_value("trend_confidence", fallback.get("trend_confidence", "medium")),
        "representative_papers": list_value("representative_papers", fallback.get("representative_papers", [])),
        "recent_important_papers": list_value("recent_important_papers", fallback.get("recent_important_papers", [])),
        "supporting_papers": list_value("supporting_papers", fallback.get("supporting_papers", [])),
        "warnings": list_value("warnings", fallback.get("warnings", [])),
    }
