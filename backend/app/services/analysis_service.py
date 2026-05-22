from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.analysis.trend_analyzer import analyze_trends
from app.models import AnalysisResult, Professor
from app.services.serialization import analysis_to_dict, linked_paper_analysis_dict


def run_and_store_analysis(db: Session, professor: Professor) -> dict:
    paper_dicts = [linked_paper_analysis_dict(link) for link in professor.paper_links]
    result = analyze_trends(paper_dicts, professor.official_keywords, professor=professor)
    professor.analysis_type = result.get("analysis_type", "data_limited")
    professor.evidence_confidence = result["evidence_confidence"]

    payload = {
        "trend_summary": result["trend_summary"],
        "detailed_trend_summary": result.get("detailed_trend_summary"),
        "recent_keywords": json.dumps(result["recent_keywords"], ensure_ascii=False),
        "five_year_keywords": json.dumps(result["five_year_keywords"], ensure_ascii=False),
        "overall_keywords": json.dumps(result["overall_keywords"], ensure_ascii=False),
        "timeline_json": json.dumps(result["timeline"], ensure_ascii=False),
        "trend_confidence": result.get("trend_confidence", result["evidence_confidence"]),
        "main_research_axis_json": json.dumps(result.get("main_research_axis", []), ensure_ascii=False),
        "recent_shift": result.get("recent_shift"),
        "representative_papers_json": json.dumps(result["representative_papers"], ensure_ascii=False),
        "recent_important_papers_json": json.dumps(result.get("recent_important_papers", []), ensure_ascii=False),
        "recent_papers_json": json.dumps(result["recent_papers"], ensure_ascii=False),
        "interest_related_papers_json": json.dumps(result.get("interest_related_papers", []), ensure_ascii=False),
        "supporting_papers_json": json.dumps(result.get("supporting_papers", []), ensure_ascii=False),
        "excluded_papers_count": result.get("excluded_papers_count", 0),
        "llm_used": result.get("llm_used", False),
        "llm_provider": result.get("llm_provider"),
        "evidence_confidence": result["evidence_confidence"],
        "warnings_json": json.dumps(result["warnings"], ensure_ascii=False),
    }
    if professor.analysis:
        for key, value in payload.items():
            setattr(professor.analysis, key, value)
    else:
        professor.analysis = AnalysisResult(professor_id=professor.id, **payload)
    db.add(professor)
    db.commit()
    db.refresh(professor)
    return analysis_to_dict(professor.analysis)
