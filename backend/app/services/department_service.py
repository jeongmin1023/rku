from __future__ import annotations

from sqlalchemy.orm import Session

from app.crawler.department_crawler import crawl_department_page
from app.models import Department, Professor
from app.schemas import ConfirmProfessorsRequest, CrawlRequest


def crawl_and_create_department(db: Session, request: CrawlRequest) -> tuple[Department, list[str]]:
    result = crawl_department_page(request.university, request.department, str(request.url))
    department = Department(
        university=request.university,
        department=request.department,
        source_url=str(request.url),
    )
    db.add(department)
    db.flush()

    for candidate in result.professors:
        db.add(
            Professor(
                department_id=department.id,
                name=candidate.name,
                english_name=candidate.english_name,
                title=candidate.title,
                university=request.university,
                department=request.department,
                lab_name=candidate.lab_name,
                email=candidate.email,
                profile_url=candidate.profile_url,
                lab_url=candidate.lab_url,
                official_keywords=candidate.official_keywords,
                source_url=candidate.source_url,
                extraction_confidence=candidate.extraction_confidence,
            )
        )
    db.commit()
    db.refresh(department)
    return department, result.warnings


def confirm_professors(
    db: Session,
    department: Department,
    request: ConfirmProfessorsRequest,
) -> list[Professor]:
    for professor in list(department.professors):
        db.delete(professor)
    db.flush()
    professors: list[Professor] = []
    for item in request.professors:
        if item.excluded:
            continue
        professor = Professor(
            department_id=department.id,
            name=item.name,
            english_name=item.english_name,
            title=item.title,
            university=department.university,
            department=department.department,
            lab_name=item.lab_name,
            email=item.email,
            profile_url=item.profile_url,
            lab_url=item.lab_url,
            official_keywords=item.official_keywords,
            source_url=department.source_url,
            extraction_confidence=item.extraction_confidence,
        )
        db.add(professor)
        professors.append(professor)
    db.commit()
    return professors
