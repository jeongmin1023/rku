from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import get_db, init_db
from app.models import Department, Professor
from app.schemas import (
    ConfirmProfessorsRequest,
    ContactCardOut,
    CrawlRequest,
    CrawlResponse,
    FitOut,
    FitRequest,
    HarvestDepartmentResponse,
    HarvestProfessorResponse,
    ProfessorCardOut,
    ProfessorDetailOut,
)
from app.services.department_service import confirm_professors, crawl_and_create_department
from app.services.paper_harvest_service import harvest_department, harvest_professor
from app.services.professor_service import contact_card, create_fit_result, professor_cards, professor_detail


app = FastAPI(
    title="LabFit Backend MVP",
    description="교수님 평가가 아니라 공개 연구 근거와 관심 주제의 연결성을 탐색하는 백엔드 MVP",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/departments/crawl", response_model=CrawlResponse)
def crawl_department(request: CrawlRequest, db: Session = Depends(get_db)) -> dict:
    department, warnings = crawl_and_create_department(db, request)
    return {"department": department, "professors": department.professors, "warnings": warnings}


@app.post("/api/departments/{department_id}/professors/confirm", response_model=CrawlResponse)
def confirm_department_professors(
    department_id: int,
    request: ConfirmProfessorsRequest,
    db: Session = Depends(get_db),
) -> dict:
    department = _get_department(db, department_id)
    professors = confirm_professors(db, department, request)
    return {"department": department, "professors": professors, "warnings": []}


@app.post("/api/departments/{department_id}/papers/harvest", response_model=HarvestDepartmentResponse)
def harvest_department_papers(department_id: int, db: Session = Depends(get_db)) -> dict:
    department = _get_department(db, department_id)
    return {"department": department, "results": harvest_department(db, department)}


@app.post("/api/professors/{professor_id}/papers/harvest", response_model=HarvestProfessorResponse)
def harvest_professor_papers(professor_id: int, db: Session = Depends(get_db)) -> dict:
    professor = _get_professor(db, professor_id)
    return harvest_professor(db, professor)


@app.get("/api/departments/{department_id}/professors", response_model=list[ProfessorCardOut])
def get_department_professors(department_id: int, db: Session = Depends(get_db)) -> list[dict]:
    department = _get_department(db, department_id)
    return professor_cards(department.professors)


@app.get("/api/professors/{professor_id}", response_model=ProfessorDetailOut)
def get_professor(professor_id: int, db: Session = Depends(get_db)) -> dict:
    professor = _get_professor(db, professor_id)
    return professor_detail(professor)


@app.post("/api/professors/{professor_id}/fit", response_model=FitOut)
def fit_professor(professor_id: int, request: FitRequest, db: Session = Depends(get_db)) -> dict:
    professor = _get_professor(db, professor_id)
    return create_fit_result(db, professor, request.user_interest)


@app.post("/api/professors/{professor_id}/contact-card", response_model=ContactCardOut)
def professor_contact_card(professor_id: int, request: FitRequest, db: Session = Depends(get_db)) -> dict:
    professor = _get_professor(db, professor_id)
    return contact_card(professor, request.user_interest)


def _get_department(db: Session, department_id: int) -> Department:
    department = db.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department


def _get_professor(db: Session, professor_id: int) -> Professor:
    professor = db.get(Professor, professor_id)
    if not professor:
        raise HTTPException(status_code=404, detail="Professor not found")
    return professor
