from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CrawlRequest(BaseModel):
    university: str = Field(min_length=1)
    department: str = Field(min_length=1)
    url: HttpUrl


class ProfessorCandidate(BaseModel):
    name: str
    english_name: str | None = None
    title: str | None = None
    university: str | None = None
    department: str | None = None
    lab_name: str | None = None
    email: str | None = None
    profile_url: str | None = None
    lab_url: str | None = None
    official_keywords: str | None = None
    source_url: str
    extraction_confidence: float = 0.4
    evidence: list[str] = Field(default_factory=list)


class ProfessorConfirmItem(BaseModel):
    name: str
    english_name: str | None = None
    title: str | None = None
    lab_name: str | None = None
    email: str | None = None
    profile_url: str | None = None
    lab_url: str | None = None
    official_keywords: str | None = None
    extraction_confidence: float = 0.5
    excluded: bool = False


class ConfirmProfessorsRequest(BaseModel):
    professors: list[ProfessorConfirmItem]


class DepartmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    university: str
    department: str
    source_url: str
    created_at: datetime


class ProfessorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    department_id: int
    name: str
    english_name: str | None = None
    title: str | None = None
    university: str
    department: str
    lab_name: str | None = None
    email: str | None = None
    profile_url: str | None = None
    lab_url: str | None = None
    official_keywords: str | None = None
    source_url: str
    extraction_confidence: float
    analysis_type: str
    evidence_confidence: str
    created_at: datetime


class CrawlResponse(BaseModel):
    department: DepartmentOut
    professors: list[ProfessorOut]
    warnings: list[str] = Field(default_factory=list)


class MasterPaperOut(BaseModel):
    id: int
    title_ko: str | None = None
    title_en: str | None = None
    display_title: str
    authors: list[str] = Field(default_factory=list)
    author_affiliations: list[str] = Field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    uci: str | None = None
    abstract: str | None = None
    keywords: list[str] = Field(default_factory=list)
    source_list: list[str] = Field(default_factory=list)
    source_ids: dict[str, list[str]] = Field(default_factory=dict)
    citation_signals: dict[str, int | None] = Field(default_factory=dict)
    duplicate_status: str
    merge_confidence: float = 0.5
    merge_notes: list[str] = Field(default_factory=list)
    source_confidence_signals: dict[str, float] = Field(default_factory=dict)
    url: str | None = None


class ProfessorPaperOut(BaseModel):
    id: int
    master_paper: MasterPaperOut
    match_score: float
    match_status: str
    author_role: str | None = None
    evidence_notes: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class AnalysisOut(BaseModel):
    trend_summary: str
    recent_keywords: list[str]
    five_year_keywords: list[str]
    overall_keywords: list[str]
    timeline: dict[str, list[str]]
    representative_papers: list[dict[str, Any]]
    recent_papers: list[dict[str, Any]]
    evidence_confidence: str
    warnings: list[str]


class ProfessorCardOut(ProfessorOut):
    keywords: list[str] = Field(default_factory=list)
    trend_summary: str | None = None
    warnings: list[str] = Field(default_factory=list)
    accepted_paper_count: int = 0
    needs_review_paper_count: int = 0
    rejected_paper_count: int = 0
    source_coverage: dict[str, int] = Field(default_factory=dict)


class ProfessorDetailOut(ProfessorOut):
    department_info: DepartmentOut
    papers: list[ProfessorPaperOut]
    analysis: AnalysisOut


class HarvestProfessorResponse(BaseModel):
    professor: ProfessorOut
    source_candidate_count: int
    master_paper_count: int
    accepted_count: int
    needs_review_count: int
    weak_candidate_count: int
    rejected_count: int
    analysis: AnalysisOut


class HarvestDepartmentResponse(BaseModel):
    department: DepartmentOut
    results: list[HarvestProfessorResponse]


class FitRequest(BaseModel):
    user_interest: str = Field(min_length=1)


class FitOut(BaseModel):
    fit_level: str
    interpretation: str
    matched_keywords: list[str]
    related_papers: list[dict[str, Any]]
    check_points: list[str]
    evidence_confidence: str


class ContactCardOut(BaseModel):
    professor_id: int
    professor_name: str
    reading_list: list[dict[str, Any]]
    questions: list[str]
    email_points: list[str]
    check_points: list[str]
    evidence_confidence: str
