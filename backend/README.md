# LabFit Backend MVP

LabFit backend는 교수님 평가나 순위 산정이 아니라, 공개 논문·연구실 정보와 사용자의 관심 연구주제 사이의 연결성을 탐색하기 위한 근거 데이터를 만듭니다.

## 실행 방법

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
Copy-Item .env.example .env
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API 문서는 `http://127.0.0.1:8000/docs`에서 확인할 수 있습니다.

## 환경 변수

- `DATABASE_URL`: 기본값 `sqlite:///./labfit.db`
- `LABFIT_USE_MOCK_ONLY=1`: 외부 API 없이 `backend/sample_data`만 사용
- `KCI_API_KEY`, `KCI_API_URL`: KCI 연동이 가능할 때 선택 사용
- `LABFIT_LLM_PROVIDER=gemini`
- `LABFIT_LLM_MODEL=gemini-1.5-flash`
- `LABFIT_LLM_API_KEY`: Gemini 요약 연동용. 없으면 템플릿 fallback 사용

환경변수가 사라졌다면 `backend/.env.example`을 `backend/.env`로 복사하세요. 실제 API 키는 `.env.example`에 넣지 않고, `.env`에만 넣습니다. `.env`는 GitHub에 올리지 않습니다.

OpenAlex는 기본 파이프라인에서 제외했습니다. 선택 확장 소스로 파일은 남아 있지만 default adapters에는 포함되지 않습니다.

## API

- `POST /api/departments/crawl`
- `POST /api/departments/{department_id}/professors/confirm`
- `POST /api/departments/{department_id}/papers/harvest`
- `POST /api/professors/{professor_id}/papers/harvest`
- `GET /api/departments/{department_id}/professors`
- `GET /api/professors/{professor_id}`
- `POST /api/professors/{professor_id}/fit`
- `POST /api/professors/{professor_id}/contact-card`

## 멀티소스 논문 수집

기본 adapter는 `KCIClient`, `RISSClient`, `DBpiaClient`, `ScienceONClient`, `CrossrefClient`입니다.

수집 단계에서는 교수명 중심으로 넓게 검색합니다. 학교명, 학과명, 연구분야는 검색 필터가 아니라 후속 매칭 점수의 근거로만 사용합니다. 교수 공식 프로필 또는 연구실 페이지에서 publication 섹션이 발견되면 가장 높은 신뢰도의 후보로 먼저 반영합니다.

Crossref는 DOI/title 기반 메타데이터 보강용으로 사용하며, 단독 확정 근거로 쓰지 않습니다.

## 데이터 구조

- `NormalizedPaperCandidate`: KCI/RISS/DBpia/ScienceON/Crossref 응답을 공통 스키마로 표준화한 논문 후보
- `MasterPaper`: DOI, UCI/KCI ID, 제목 유사도, 저자, 연도, venue 기준으로 병합한 논문 단위
- `ProfessorPaper`: 교수님과 MasterPaper 사이의 매칭 점수, 상태, 근거, 경고
- `AnalysisResult`: 연구 경향, 키워드, 대표 논문, 최근 연구 논문, 보조 후보

인용수와 이용수는 절대 합산하지 않습니다. `citation_signals_json`에 source별로 저장합니다.

```json
{
  "kci": 4,
  "dbpia": 2,
  "scienceon": 5,
  "crossref": 0
}
```

## 데이터 오염 방지

- 교수명만으로 accepted 처리하지 않습니다.
- 이름이 일치하고 소속이 없으면 rejected가 아니라 `needs_review` 또는 `weak_candidate`로 보존합니다.
- 소속이 명확히 다르고 주제도 맞지 않는 경우만 강하게 낮춥니다.
- 공동저자이고 주제 유사도가 낮으면 accepted로 올리지 않습니다.
- accepted와 needs_review를 분리하고, needs_review는 분석에서 낮은 가중치로만 반영합니다.
- 후보가 전부 rejected가 되면 이름 매칭이 있는 상위 후보를 `weak_candidate`로 보존해 검토 가능성을 남깁니다.

## 연구 경향 분석

키워드 추출은 제목, 초록, source keywords, venue를 사용합니다. 한국어/영어 stopwords와 메뉴 단어를 제거하고, 교수명·학교명·학과명을 제외합니다.

분석 결과는 다음을 포함합니다.

- `trend_summary`
- `detailed_trend_summary`
- `recent_keywords`
- `five_year_keywords`
- `overall_keywords`
- `representative_papers`
- `recent_important_papers`
- `supporting_papers`
- `trend_confidence`

LLM 모듈은 `analysis/llm_client.py`, `analysis/llm_paper_summarizer.py`, `analysis/llm_trend_summarizer.py`, `analysis/llm_keyword_refiner.py`, `analysis/llm_paper_classifier.py`에 분리되어 있습니다. Gemini는 정제된 논문 제목, 초록, 키워드, 연도, 학술지, 출처 데이터를 문장화하는 역할만 하며, 교수님 평가나 논문 진위 판정에는 사용하지 않습니다. API 키가 없거나 호출이 실패하면 기존 규칙 기반 fallback으로 논문 요약과 연구 경향 요약을 생성합니다.

## 테스트

```powershell
cd backend
python -m pytest app/tests
```

검증 항목에는 OpenAlex default 제외, 국내 mock source 정규화, 이름 중심 후보 보존, 키워드 stopword 제거, 대표/최근/보조 논문 분류가 포함됩니다.

## MVP 한계와 확장

- 국내 학술 사이트의 실제 API/크롤링 정책은 기관별로 다르므로 mock fallback을 기본 보장합니다.
- RISS/DBpia/ScienceON 실제 연동은 robots.txt와 이용 정책을 존중하는 범위에서 메타데이터 중심으로 확장해야 합니다.
- ORCID, DBLP, 연구실 publication 정밀 파싱은 추가 확장 지점입니다.
