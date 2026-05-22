from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    university: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    professors: Mapped[list["Professor"]] = relationship(
        back_populates="department_ref",
        cascade="all, delete-orphan",
    )


class Professor(Base):
    __tablename__ = "professors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    english_name: Mapped[str | None] = mapped_column(String(255))
    title: Mapped[str | None] = mapped_column(String(100))
    university: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=False)
    lab_name: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    profile_url: Mapped[str | None] = mapped_column(Text)
    lab_url: Mapped[str | None] = mapped_column(Text)
    official_keywords: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    extraction_confidence: Mapped[float] = mapped_column(Float, default=0.4)
    analysis_type: Mapped[str] = mapped_column(String(50), default="data_limited")
    evidence_confidence: Mapped[str] = mapped_column(String(20), default="low")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    department_ref: Mapped[Department] = relationship(back_populates="professors")
    paper_links: Mapped[list["ProfessorPaper"]] = relationship(
        back_populates="professor",
        cascade="all, delete-orphan",
    )
    analysis: Mapped["AnalysisResult | None"] = relationship(
        back_populates="professor",
        cascade="all, delete-orphan",
        uselist=False,
    )
    fit_results: Mapped[list["FitResult"]] = relationship(
        back_populates="professor",
        cascade="all, delete-orphan",
    )


class MasterPaper(Base):
    __tablename__ = "master_papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title_ko: Mapped[str | None] = mapped_column(Text)
    title_en: Mapped[str | None] = mapped_column(Text)
    display_title: Mapped[str] = mapped_column(Text, nullable=False)
    authors_json: Mapped[str | None] = mapped_column(Text)
    author_affiliations_json: Mapped[str | None] = mapped_column(Text)
    year: Mapped[int | None] = mapped_column(Integer, index=True)
    venue: Mapped[str | None] = mapped_column(String(255))
    doi: Mapped[str | None] = mapped_column(String(255), index=True)
    uci: Mapped[str | None] = mapped_column(String(255), index=True)
    abstract: Mapped[str | None] = mapped_column(Text)
    keywords_json: Mapped[str | None] = mapped_column(Text)
    source_list_json: Mapped[str | None] = mapped_column(Text)
    source_ids_json: Mapped[str | None] = mapped_column(Text)
    citation_signals_json: Mapped[str | None] = mapped_column(Text)
    duplicate_status: Mapped[str] = mapped_column(String(40), default="unique")
    merge_confidence: Mapped[float] = mapped_column(Float, default=0.5)
    merge_notes_json: Mapped[str | None] = mapped_column(Text)
    source_confidence_signals_json: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    professor_links: Mapped[list["ProfessorPaper"]] = relationship(
        back_populates="master_paper",
        cascade="all, delete-orphan",
    )


class ProfessorPaper(Base):
    __tablename__ = "professor_papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    professor_id: Mapped[int] = mapped_column(ForeignKey("professors.id"), index=True)
    master_paper_id: Mapped[int] = mapped_column(ForeignKey("master_papers.id"), index=True)
    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    match_status: Mapped[str] = mapped_column(String(30), default="weak_candidate", index=True)
    author_role: Mapped[str | None] = mapped_column(String(100))
    evidence_notes_json: Mapped[str | None] = mapped_column(Text)
    warnings_json: Mapped[str | None] = mapped_column(Text)

    professor: Mapped[Professor] = relationship(back_populates="paper_links")
    master_paper: Mapped[MasterPaper] = relationship(back_populates="professor_links")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    professor_id: Mapped[int] = mapped_column(ForeignKey("professors.id"), unique=True, index=True)
    trend_summary: Mapped[str] = mapped_column(Text)
    recent_keywords: Mapped[str | None] = mapped_column(Text)
    five_year_keywords: Mapped[str | None] = mapped_column(Text)
    overall_keywords: Mapped[str | None] = mapped_column(Text)
    timeline_json: Mapped[str | None] = mapped_column(Text)
    representative_papers_json: Mapped[str | None] = mapped_column(Text)
    recent_papers_json: Mapped[str | None] = mapped_column(Text)
    evidence_confidence: Mapped[str] = mapped_column(String(20), default="low")
    warnings_json: Mapped[str | None] = mapped_column(Text)

    professor: Mapped[Professor] = relationship(back_populates="analysis")


class FitResult(Base):
    __tablename__ = "fit_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    professor_id: Mapped[int] = mapped_column(ForeignKey("professors.id"), index=True)
    user_interest: Mapped[str] = mapped_column(Text)
    fit_level: Mapped[str] = mapped_column(String(30))
    interpretation: Mapped[str] = mapped_column(Text)
    matched_keywords: Mapped[str | None] = mapped_column(Text)
    related_papers_json: Mapped[str | None] = mapped_column(Text)
    check_points_json: Mapped[str | None] = mapped_column(Text)
    evidence_confidence: Mapped[str] = mapped_column(String(20), default="low")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))

    professor: Mapped[Professor] = relationship(back_populates="fit_results")
