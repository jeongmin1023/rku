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
        "recent_keywords": json.dumps(result["recent_keywords"], ensure_ascii=False),
        "five_year_keywords": json.dumps(result["five_year_keywords"], ensure_ascii=False),
        "overall_keywords": json.dumps(result["overall_keywords"], ensure_ascii=False),
        "timeline_json": json.dumps(result["timeline"], ensure_ascii=False),
        "representative_papers_json": json.dumps(result["representative_papers"], ensure_ascii=False),
        "recent_papers_json": json.dumps(result["recent_papers"], ensure_ascii=False),
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
