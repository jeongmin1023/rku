from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.analysis.contact_card import build_contact_card
from app.analysis.fit_analyzer import analyze_fit
from app.models import FitResult, Professor
from app.services.serialization import (
    analysis_to_dict,
    linked_paper_analysis_dict,
    loads_json,
    professor_paper_to_dict,
)


def professor_cards(professors: list[Professor]) -> list[dict]:
    cards = []
    for professor in professors:
        analysis = analysis_to_dict(professor.analysis)
        status_counts = _paper_status_counts(professor)
        cards.append(
            {
                **_professor_base(professor),
                "keywords": analysis["five_year_keywords"][:5] or _keyword_list(professor.official_keywords),
                "trend_summary": analysis["trend_summary"],
                "recent_keywords": analysis["recent_keywords"],
                "five_year_keywords": analysis["five_year_keywords"],
                "overall_keywords": analysis["overall_keywords"],
                "trend_confidence": analysis["trend_confidence"],
                "warnings": analysis["warnings"],
                "accepted_paper_count": status_counts["accepted"],
                "needs_review_paper_count": status_counts["needs_review"],
                "weak_candidate_count": status_counts["weak_candidate"],
                "rejected_paper_count": status_counts["rejected"],
                "source_coverage": _source_coverage(professor),
            }
        )
    return cards


def professor_detail(professor: Professor) -> dict:
    return {
        **_professor_base(professor),
        "department_info": professor.department_ref,
        "papers": [
            professor_paper_to_dict(link)
            for link in professor.paper_links
            if link.match_status in {"accepted", "needs_review", "weak_candidate"}
        ],
        "analysis": analysis_to_dict(professor.analysis),
    }


def create_fit_result(db: Session, professor: Professor, user_interest: str) -> dict:
    papers = [linked_paper_analysis_dict(link) for link in professor.paper_links]
    fit = analyze_fit(user_interest, papers, professor.evidence_confidence)
    row = FitResult(
        professor_id=professor.id,
        user_interest=user_interest,
        fit_level=fit["fit_level"],
        interpretation=fit["interpretation"],
        matched_keywords=json.dumps(fit["matched_keywords"], ensure_ascii=False),
        related_papers_json=json.dumps(fit["related_papers"], ensure_ascii=False),
        check_points_json=json.dumps(fit["check_points"], ensure_ascii=False),
        evidence_confidence=fit["evidence_confidence"],
    )
    db.add(row)
    db.commit()
    return fit


def contact_card(professor: Professor, user_interest: str | None) -> dict:
    papers = [linked_paper_analysis_dict(link) for link in professor.paper_links]
    return build_contact_card(professor, papers, analysis_to_dict(professor.analysis), user_interest)


def fit_row_to_dict(row: FitResult) -> dict:
    return {
        "fit_level": row.fit_level,
        "interpretation": row.interpretation,
        "matched_keywords": loads_json(row.matched_keywords, []),
        "related_papers": loads_json(row.related_papers_json, []),
        "check_points": loads_json(row.check_points_json, []),
        "evidence_confidence": row.evidence_confidence,
    }


def _professor_base(professor: Professor) -> dict:
    return {
        "id": professor.id,
        "department_id": professor.department_id,
        "name": professor.name,
        "english_name": professor.english_name,
        "title": professor.title,
        "university": professor.university,
        "department": professor.department,
        "lab_name": professor.lab_name,
        "email": professor.email,
        "profile_url": professor.profile_url,
        "lab_url": professor.lab_url,
        "official_keywords": professor.official_keywords,
        "source_url": professor.source_url,
        "extraction_confidence": professor.extraction_confidence,
        "analysis_type": professor.analysis_type,
        "evidence_confidence": professor.evidence_confidence,
        "created_at": professor.created_at,
    }


def _keyword_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.replace(";", ",").split(",") if part.strip()][:5]


def _paper_status_counts(professor: Professor) -> dict[str, int]:
    counts = {"accepted": 0, "needs_review": 0, "weak_candidate": 0, "rejected": 0}
    for link in professor.paper_links:
        if link.match_status in counts:
            counts[link.match_status] += 1
    return counts


def _source_coverage(professor: Professor) -> dict[str, int]:
    coverage: dict[str, int] = {}
    for link in professor.paper_links:
        for source in loads_json(link.master_paper.source_list_json, []):
            label = _source_label(source)
            coverage[label] = coverage.get(label, 0) + 1
    return coverage


def _source_label(source: str) -> str:
    mapping = {
        "kci": "KCI",
        "openalex": "OpenAlex",
        "crossref": "Crossref",
        "dbpia": "DBpia",
        "riss": "RISS",
        "dblp": "DBLP",
        "scienceon": "ScienceON",
        "professor_lab_page_publication": "공식페이지",
    }
    return mapping.get(source.lower(), source)
