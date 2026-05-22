from __future__ import annotations

import json
from typing import Any

from app.models import AnalysisResult, MasterPaper, ProfessorPaper
from app.analysis.llm_paper_summarizer import fallback_paper_summary


def loads_json(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def master_paper_to_dict(master: MasterPaper) -> dict[str, Any]:
    return {
        "id": master.id,
        "title_ko": master.title_ko,
        "title_en": master.title_en,
        "display_title": master.display_title,
        "authors": loads_json(master.authors_json, []),
        "author_affiliations": loads_json(master.author_affiliations_json, []),
        "year": master.year,
        "venue": master.venue,
        "doi": master.doi,
        "uci": master.uci,
        "abstract": master.abstract,
        "keywords": loads_json(master.keywords_json, []),
        "source_list": loads_json(master.source_list_json, []),
        "source_ids": loads_json(master.source_ids_json, {}),
        "citation_signals": loads_json(master.citation_signals_json, {}),
        "duplicate_status": master.duplicate_status,
        "merge_confidence": master.merge_confidence,
        "merge_notes": loads_json(master.merge_notes_json, []),
        "source_confidence_signals": loads_json(master.source_confidence_signals_json, {}),
        "url": master.url,
    }


def professor_paper_to_dict(link: ProfessorPaper) -> dict[str, Any]:
    master = master_paper_to_dict(link.master_paper)
    summary_fields = fallback_paper_summary(
        {
            **master,
            "match_status": link.match_status,
            "author_role": link.author_role,
        }
    )
    return {
        "id": link.id,
        "master_paper": master,
        "match_score": link.match_score,
        "match_status": link.match_status,
        "author_role": link.author_role,
        "evidence_notes": loads_json(link.evidence_notes_json, {}),
        "warnings": loads_json(link.warnings_json, []),
        "paper_summary": summary_fields["paper_summary"],
        "main_topic": summary_fields["main_topic"],
        "method_or_focus": summary_fields["method_or_focus"],
        "why_it_matters": summary_fields["why_it_matters"],
        "summary_limitations": summary_fields["summary_limitations"],
        "why_read_this": None,
        "category_reason": None,
    }


def analysis_to_dict(analysis: AnalysisResult | None) -> dict[str, Any]:
    if analysis is None:
        return empty_analysis()
    return {
        "trend_summary": analysis.trend_summary,
        "detailed_trend_summary": analysis.detailed_trend_summary,
        "main_research_axis": loads_json(analysis.main_research_axis_json, []),
        "recent_shift": analysis.recent_shift,
        "recent_keywords": loads_json(analysis.recent_keywords, []),
        "five_year_keywords": loads_json(analysis.five_year_keywords, []),
        "overall_keywords": loads_json(analysis.overall_keywords, []),
        "timeline": loads_json(analysis.timeline_json, {}),
        "trend_confidence": analysis.trend_confidence,
        "representative_papers": loads_json(analysis.representative_papers_json, []),
        "recent_important_papers": loads_json(analysis.recent_important_papers_json, []),
        "recent_papers": loads_json(analysis.recent_papers_json, []),
        "interest_related_papers": loads_json(analysis.interest_related_papers_json, []),
        "supporting_papers": loads_json(analysis.supporting_papers_json, []),
        "excluded_papers_count": analysis.excluded_papers_count,
        "evidence_confidence": analysis.evidence_confidence,
        "warnings": loads_json(analysis.warnings_json, []),
        "llm_used": bool(analysis.llm_used),
        "llm_provider": analysis.llm_provider,
    }


def empty_analysis() -> dict[str, Any]:
    return {
        "trend_summary": "논문 수집 전입니다. 공개 논문과 연구실 정보를 수집하면 연구 경향을 확인할 수 있습니다.",
        "detailed_trend_summary": None,
        "main_research_axis": [],
        "recent_shift": None,
        "recent_keywords": [],
        "five_year_keywords": [],
        "overall_keywords": [],
        "timeline": {},
        "trend_confidence": "low",
        "representative_papers": [],
        "recent_important_papers": [],
        "recent_papers": [],
        "interest_related_papers": [],
        "supporting_papers": [],
        "excluded_papers_count": 0,
        "evidence_confidence": "low",
        "warnings": ["논문 수집 전"],
        "llm_used": False,
        "llm_provider": None,
    }


def linked_paper_analysis_dict(link: ProfessorPaper) -> dict[str, Any]:
    master = master_paper_to_dict(link.master_paper)
    summary_fields = fallback_paper_summary(
        {
            **master,
            "match_status": link.match_status,
            "author_role": link.author_role,
        }
    )
    master.update(
        {
            "match_score": link.match_score,
            "match_status": link.match_status,
            "author_role": link.author_role,
            "evidence_notes": loads_json(link.evidence_notes_json, {}),
            "warnings": loads_json(link.warnings_json, []),
            **summary_fields,
        }
    )
    return master
