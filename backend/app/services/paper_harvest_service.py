from __future__ import annotations

import json
import os
from collections import Counter
from difflib import SequenceMatcher
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crawler.professor_page_crawler import extract_lab_publication_titles
from app.models import Department, MasterPaper, Professor, ProfessorPaper
from app.paper_sources.base import PaperSourceAdapter
from app.paper_sources.crossref_client import CrossrefClient
from app.paper_sources.dbpia_client import DBpiaClient
from app.paper_sources.kci_client import KCIClient
from app.paper_sources.mock_client import MockClient
from app.paper_sources.riss_client import RISSClient
from app.paper_sources.scienceon_client import ScienceONClient
from app.papers.matcher import ACCEPTED, NEEDS_REVIEW, REJECTED, WEAK_CANDIDATE, score_master_paper_match
from app.papers.normalizer import NormalizedPaperCandidate, normalize_lab_publication_item, normalize_title
from app.papers.resolver import MasterPaperDraft, PaperResolver
from app.services.analysis_service import run_and_store_analysis
from app.services.serialization import loads_json, master_paper_to_dict


def default_adapters() -> list[PaperSourceAdapter]:
    if os.getenv("LABFIT_USE_MOCK_ONLY", "").lower() in {"1", "true", "yes"}:
        return [MockClient()]
    return [KCIClient(), RISSClient(), DBpiaClient(), ScienceONClient(), CrossrefClient()]


def harvest_department(db: Session, department: Department) -> list[dict]:
    return [harvest_professor(db, professor) for professor in department.professors]


def harvest_professor(
    db: Session,
    professor: Professor,
    adapters: Iterable[PaperSourceAdapter] | None = None,
) -> dict:
    adapters = list(adapters or default_adapters())
    candidates = _collect_candidates(professor, adapters)

    resolver = PaperResolver()
    drafts = resolver.resolve(candidates)
    repeated_coauthors = _repeated_coauthors(drafts, professor)
    lab_titles = _lab_publication_titles(professor)

    current_links: list[ProfessorPaper] = []
    for draft in drafts:
        master = _upsert_master_paper(db, draft)
        paper_dict = master_paper_to_dict(master)
        result = score_master_paper_match(
            professor,
            paper_dict,
            repeated_coauthors=repeated_coauthors,
            lab_publication_titles=lab_titles,
        )
        link = _upsert_professor_paper(db, professor.id, master.id)
        link.match_score = result.score
        link.match_status = result.status
        link.author_role = result.author_role
        link.evidence_notes_json = result.evidence_notes_json
        link.warnings_json = result.warnings_json
        db.add(link)
        current_links.append(link)

    _preserve_name_matched_candidates(current_links)
    db.commit()
    db.refresh(professor)
    analysis = run_and_store_analysis(db, professor)
    counts = Counter(link.match_status for link in current_links)

    accepted_count = counts[ACCEPTED]
    needs_review_count = counts[NEEDS_REVIEW]
    weak_candidate_count = counts[WEAK_CANDIDATE]
    rejected_count = counts[REJECTED]
    analysis_ready_count = accepted_count + needs_review_count
    review_candidate_count = needs_review_count + weak_candidate_count
    candidate_pool_count = accepted_count + needs_review_count + weak_candidate_count
    excluded_count = rejected_count
    warning_count = sum(len(loads_json(link.warnings_json, [])) for link in current_links)
    master_count = len(drafts)

    return {
        "professor": professor,
        "source_candidate_count": len(candidates),
        "master_paper_count": master_count,
        "accepted_count": accepted_count,
        "needs_review_count": needs_review_count,
        "weak_candidate_count": weak_candidate_count,
        "rejected_count": rejected_count,
        "analysis_ready_count": analysis_ready_count,
        "review_candidate_count": review_candidate_count,
        "candidate_pool_count": candidate_pool_count,
        "excluded_count": excluded_count,
        "warning_count": warning_count,
        "usable_rate": _percent(analysis_ready_count, master_count),
        "candidate_pool_rate": _percent(candidate_pool_count, master_count),
        "excluded_rate": _percent(excluded_count, master_count),
        "analysis": analysis,
    }


def _collect_candidates(professor: Professor, adapters: list[PaperSourceAdapter]) -> list[NormalizedPaperCandidate]:
    candidates: list[NormalizedPaperCandidate] = []
    lab_titles = _lab_publication_titles(professor)
    for title in lab_titles:
        candidates.append(
            normalize_lab_publication_item(
                {
                    "title": title,
                    "authors": [professor.name],
                    "year": _extract_year(title),
                    "source_confidence": 1.0,
                    "source_warnings": ["교수 공식 페이지 또는 연구실 페이지 publication 섹션에서 발견된 제목입니다."],
                }
            )
        )

    crossref_adapters = [adapter for adapter in adapters if adapter.source_name == "crossref"]
    primary_adapters = [adapter for adapter in adapters if adapter.source_name != "crossref"]

    for adapter in primary_adapters:
        candidates.extend(adapter.search_by_professor(professor))

    title_pool = list(dict.fromkeys([candidate.title_ko or candidate.title_en or candidate.normalized_title for candidate in candidates]))
    for adapter in crossref_adapters:
        for title in title_pool[:12]:
            candidates.extend(adapter.search_by_title(title))

    return candidates


def _upsert_master_paper(db: Session, draft: MasterPaperDraft) -> MasterPaper:
    master = _find_existing_master(db, draft)
    json_fields = draft.to_json_fields()
    if master is None:
        master = MasterPaper(
            title_ko=draft.title_ko,
            title_en=draft.title_en,
            display_title=draft.display_title,
            year=draft.year,
            venue=draft.venue,
            doi=draft.doi,
            uci=draft.uci,
            abstract=draft.abstract,
            duplicate_status=draft.duplicate_status,
            merge_confidence=draft.merge_confidence,
            url=draft.url,
            **json_fields,
        )
        db.add(master)
        db.flush()
        return master

    master.title_ko = master.title_ko or draft.title_ko
    master.title_en = master.title_en or draft.title_en
    master.display_title = master.title_ko or master.title_en or master.display_title
    master.year = master.year or draft.year
    master.venue = master.venue or draft.venue
    master.doi = master.doi or draft.doi
    master.uci = master.uci or draft.uci
    master.abstract = _longer(master.abstract, draft.abstract)
    master.duplicate_status = "merged" if draft.duplicate_status != "unique" else master.duplicate_status
    master.merge_confidence = max(master.merge_confidence or 0.0, draft.merge_confidence)
    master.url = master.url or draft.url
    _merge_json_list(master, "authors_json", draft.authors)
    _merge_json_list(master, "author_affiliations_json", draft.author_affiliations)
    _merge_json_list(master, "keywords_json", draft.keywords)
    _merge_json_list(master, "source_list_json", draft.source_list)
    _merge_json_dict_of_lists(master, "source_ids_json", draft.source_ids)
    _merge_json_dict(master, "citation_signals_json", draft.citation_signals)
    _merge_json_list(master, "merge_notes_json", draft.merge_notes)
    _merge_json_dict(master, "source_confidence_signals_json", draft.source_confidence_signals)
    db.add(master)
    db.flush()
    return master


def _find_existing_master(db: Session, draft: MasterPaperDraft) -> MasterPaper | None:
    if draft.doi:
        master = db.scalar(select(MasterPaper).where(MasterPaper.doi == draft.doi))
        if master:
            return master
    if draft.uci:
        master = db.scalar(select(MasterPaper).where(MasterPaper.uci == draft.uci))
        if master:
            return master
    candidates = db.scalars(select(MasterPaper).where(MasterPaper.year == draft.year)).all()
    normalized = normalize_title(draft.display_title)
    for master in candidates:
        master_authors = loads_json(master.authors_json, [])
        if (
            SequenceMatcher(None, normalized, normalize_title(master.display_title)).ratio() >= 0.92
            and _authors_overlap(draft.authors, master_authors)
        ):
            return master
    return None


def _upsert_professor_paper(db: Session, professor_id: int, master_paper_id: int) -> ProfessorPaper:
    link = db.scalar(
        select(ProfessorPaper).where(
            ProfessorPaper.professor_id == professor_id,
            ProfessorPaper.master_paper_id == master_paper_id,
        )
    )
    if link:
        return link
    link = ProfessorPaper(professor_id=professor_id, master_paper_id=master_paper_id)
    db.add(link)
    db.flush()
    return link


def _preserve_name_matched_candidates(links: list[ProfessorPaper]) -> None:
    if not links or any(link.match_status != REJECTED for link in links):
        return
    for link in sorted(links, key=lambda item: item.match_score, reverse=True)[:5]:
        link.match_status = WEAK_CANDIDATE
        link.match_score = max(link.match_score, 0.25)
        warnings = loads_json(link.warnings_json, [])
        warnings.append("이름 중심 검색 후보를 검증용으로 보존했습니다. 분석에는 낮은 가중치로만 사용하세요.")
        link.warnings_json = json.dumps(list(dict.fromkeys(warnings)), ensure_ascii=False)


def _repeated_coauthors(drafts: list[MasterPaperDraft], professor: Professor) -> Counter[str]:
    professor_names = {_norm(professor.name)}
    if professor.english_name:
        professor_names.add(_norm(professor.english_name))
    counts: Counter[str] = Counter()
    for draft in drafts:
        for author in draft.authors:
            normalized = _norm(author)
            if normalized and normalized not in professor_names:
                counts[normalized] += 1
    return counts


def _lab_publication_titles(professor: Professor) -> list[str]:
    titles = extract_lab_publication_titles(professor.lab_url) + extract_lab_publication_titles(professor.profile_url)
    return list(dict.fromkeys(titles))


def _merge_json_list(master: MasterPaper, attr: str, values: list[str]) -> None:
    current = json.loads(getattr(master, attr) or "[]")
    setattr(master, attr, json.dumps(list(dict.fromkeys([*current, *values])), ensure_ascii=False))


def _merge_json_dict(master: MasterPaper, attr: str, values: dict) -> None:
    current = json.loads(getattr(master, attr) or "{}")
    current.update(values)
    setattr(master, attr, json.dumps(current, ensure_ascii=False))


def _merge_json_dict_of_lists(master: MasterPaper, attr: str, values: dict[str, list[str]]) -> None:
    current = json.loads(getattr(master, attr) or "{}")
    for key, incoming in values.items():
        current.setdefault(key, [])
        current[key] = list(dict.fromkeys([*current[key], *incoming]))
    setattr(master, attr, json.dumps(current, ensure_ascii=False))


def _longer(left: str | None, right: str | None) -> str | None:
    if not left:
        return right
    if not right:
        return left
    return right if len(right) > len(left) else left


def _extract_year(title: str) -> int | None:
    import re

    match = re.search(r"\b(19|20)\d{2}\b", title)
    return int(match.group(0)) if match else None


def _percent(value: int, total: int) -> float:
    if not total:
        return 0.0
    return round((value / total) * 100, 1)


def _norm(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum() or "\uac00" <= ch <= "\ud7a3")


def _authors_overlap(left: list[str], right: list[str]) -> bool:
    return bool({_norm(author) for author in left} & {_norm(author) for author in right})
