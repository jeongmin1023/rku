from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.analysis import llm_client
from app.analysis.llm_paper_summarizer import summarize_paper
from app.analysis.llm_trend_summarizer import summarize_trend
from app.analysis.trend_analyzer import analyze_trends


def sample_paper() -> dict:
    return {
        "id": 1,
        "display_title": "LLM 기반 맞춤형 학습 피드백 서비스 연구",
        "abstract": "LLM과 자연어처리를 활용하여 학습자 피드백과 교육 서비스 개인화를 분석한다.",
        "keywords": ["LLM", "자연어처리", "교육 AI"],
        "year": 2025,
        "venue": "교육AI연구",
        "match_status": "accepted",
        "match_score": 0.86,
        "author_role": "first_author",
        "citation_signals": {"kci": 4},
        "source_list": ["kci"],
    }


def test_no_api_key_generates_fallback_paper_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LABFIT_LLM_API_KEY", raising=False)

    summary = summarize_paper(sample_paper())

    assert summary["paper_summary"]
    assert summary["main_topic"]
    assert summary["llm_used"] is False
    assert "LLM 요약 미사용" in summary["summary_limitations"]


def test_gemini_failure_uses_fallback_trend_summary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LABFIT_LLM_API_KEY", "fake-key")

    def fail_call(_: str) -> dict:
        raise llm_client.LLMCallError("network blocked")

    monkeypatch.setattr(llm_client, "call_llm_json", fail_call)

    result = summarize_trend(
        {
            "professor_name": "김민준",
            "official_keywords": ["자연어처리"],
            "recent_keywords": ["LLM", "교육 AI"],
            "five_year_keywords": ["자연어처리", "학습분석"],
            "evidence_confidence": "medium",
            "warnings": [],
        }
    )

    assert result["trend_summary"]
    assert result["llm_used"] is False
    assert result["trend_confidence"] == "medium"


def test_analyze_trends_includes_paper_summary_and_llm_false_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LABFIT_LLM_API_KEY", raising=False)

    result = analyze_trends(
        [sample_paper()],
        "LLM, 자연어처리, 교육 AI",
        professor=SimpleNamespace(name="김민준", title="교수", official_keywords="LLM, 자연어처리, 교육 AI"),
    )

    assert result["trend_summary"]
    assert result["llm_used"] is False
    assert result["representative_papers"][0]["paper_summary"]


def test_mock_gemini_response_marks_llm_used_and_applies_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LABFIT_LLM_API_KEY", "fake-key")

    def fake_call(prompt: str) -> dict:
        if "Generate LabFit research trend wording" in prompt:
            return {
                "trend_summary": "공개 데이터 기준으로 LLM과 교육 AI 연구 흐름이 확인됩니다.",
                "detailed_trend_summary": "공개 논문 제목과 초록 기준으로 LLM, 자연어처리, 교육 AI 흐름이 확인됩니다.",
                "main_research_axis": ["LLM", "교육 AI"],
                "recent_shift": "최근에는 학습자 피드백 응용으로 확장되는 신호가 있습니다.",
                "trend_confidence": "medium",
                "warnings": [],
            }
        return {}

    monkeypatch.setattr(llm_client, "call_llm_json", fake_call)

    result = analyze_trends(
        [sample_paper()],
        "LLM, 자연어처리, 교육 AI",
        professor=SimpleNamespace(name="김민준", title="교수", official_keywords="LLM, 자연어처리, 교육 AI"),
    )

    assert result["llm_used"] is True
    assert result["llm_provider"] == "gemini"
    assert result["trend_summary"].startswith("공개 데이터 기준")
