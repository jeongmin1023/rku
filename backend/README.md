# LabFit Backend MVP

LabFit은 교수님을 평가하거나 순위를 매기는 서비스가 아닙니다. 학과 공식 페이지와 공개 학술 데이터의 근거를 바탕으로, 사용자의 관심 주제와 연구실 방향의 연결성을 탐색하도록 돕는 백엔드 MVP입니다.

## 주요 흐름

1. 학과 교수소개 URL에서 교수님 후보를 추출합니다.
2. KCI, OpenAlex, Crossref, Mock 소스에서 논문 후보를 가져옵니다.
3. 모든 후보를 `NormalizedPaperCandidate`로 표준화합니다.
4. `PaperResolver`가 DOI, UCI/KCI ID, 제목 유사도, 저자, 연도 기준으로 `MasterPaper`를 병합합니다.
5. `ProfessorPaperMatcher`가 교수님-논문 매칭 신뢰도를 계산합니다.
6. accepted 논문 중심, needs_review 논문 보조 근거로 연구 경향과 연구핏, 컨택 준비 카드를 생성합니다.

## 설치

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Python 3.12 권장입니다. Python 3.14에서는 일부 구버전 네이티브 패키지 빌드가 실패할 수 있습니다.

## 실행

```bash
cd backend
set LABFIT_USE_MOCK_ONLY=1
python -m uvicorn app.main:app --reload
```

API 문서는 실행 후 `http://127.0.0.1:8000/docs`에서 볼 수 있습니다.

## 환경 변수

- `DATABASE_URL`: 기본값 `sqlite:///./labfit.db`
- `OPENALEX_MAILTO`: OpenAlex polite pool용 이메일, 선택
- `KCI_API_KEY`: KCI API 키, 선택
- `KCI_API_URL`: KCI 계약형 엔드포인트가 있을 때 사용
- `LABFIT_USE_MOCK_ONLY=1`: 외부 API 없이 `backend/sample_data`만 사용

## API

- `POST /api/departments/crawl`
- `POST /api/departments/{department_id}/professors/confirm`
- `POST /api/departments/{department_id}/papers/harvest`
- `POST /api/professors/{professor_id}/papers/harvest`
- `GET /api/departments/{department_id}/professors`
- `GET /api/professors/{professor_id}`
- `POST /api/professors/{professor_id}/fit`
- `POST /api/professors/{professor_id}/contact-card`

## 데이터 수집 구조

`paper_sources/base.py`의 `PaperSourceAdapter`가 공통 인터페이스입니다.

```python
search_papers_for_professor(professor: Professor) -> list[NormalizedPaperCandidate]
```

구현체는 `KCIClient`, `OpenAlexClient`, `CrossrefClient`, `MockClient`입니다. KCI 키가 없거나 OpenAlex/Crossref 호출이 실패하면 샘플 JSON으로 fallback합니다. Crossref는 DOI/제목 기반 메타데이터 보강 성격으로 사용하며, 단독 확정 근거로 쓰지 않습니다.

## Paper 구조

- `NormalizedPaperCandidate`: 소스별 원본 응답을 표준 필드로 변환한 후보
- `MasterPaper`: DOI/UCI/제목 유사도/저자/연도를 기준으로 병합한 논문 마스터
- `ProfessorPaper`: 교수님과 MasterPaper 사이의 매칭 점수, 판정, 근거, 경고

인용 신호는 합산하지 않고 `citation_signals_json`에 출처별로 따로 저장합니다.

```json
{
  "kci": 4,
  "openalex": 21,
  "crossref": 0
}
```

## 데이터 오염 방지

매칭 공식은 다음 요소를 함께 반영합니다.

- 이름/영문명/이니셜 일치
- 학교명, 학과명, 소속 유사도
- 공식 연구 키워드와 제목/초록/키워드 유사도
- 반복 공저자 신호
- DOI/UCI/다중 소스 agreement
- 연구실 페이지 publication 보조 근거
- 논문 연도 타당성
- 소스 신뢰도

교수명만으로 accepted 처리하지 않습니다. 이름이 같아도 소속이 다르거나 주제가 맞지 않으면 `needs_review`, `weak_candidate`, `rejected`로 내려갑니다. 분석은 accepted 논문 중심이며, needs_review 논문은 보조 근거와 경고를 포함해 사용합니다.

## Emerging Lab Mode

accepted 논문이 3편 미만이거나 최근 5년 논문이 부족하면 `emerging_lab`으로 표시합니다.

- “공개 논문 데이터는 제한적입니다.”
- “연구실 소개, 교수소개 페이지, 강의 과목, 프로젝트 키워드를 중심으로 분석했습니다.”
- “현재 모집 주제는 컨택 시 확인이 필요합니다.”

이 상태는 낮은 평가가 아니라 공개 데이터 부족 상태입니다.

## 샘플 데이터

`backend/sample_data`에는 다음 케이스가 들어 있습니다.

- 논문 데이터가 충분한 교수
- 동명이인/소속 오염 가능성이 있는 교수
- 논문이 적은 신임교수
- KCI와 OpenAlex 중복 논문
- DOI 중복
- 제목만 조금 다른 중복
- 공동저자 논문
- 최근 논문과 과거 대표 논문

## 테스트

```bash
cd backend
python -m pytest app/tests
```

검증 항목:

- 교수소개 HTML 추출
- KCI/OpenAlex/Crossref mock 정규화
- DOI 기반 병합
- 유사 제목 기반 병합
- 다른 소속 논문 오염 방지
- Emerging Lab Mode
- 관심 주제 fit 분석

## MVP 한계

- 학과 페이지 크롤러는 범용 휴리스틱 기반이라 모든 대학 HTML을 완벽하게 처리하지 못합니다.
- KCI 실제 API는 계약/키/엔드포인트 차이가 있어 mock fallback 중심으로 구성했습니다.
- 한글-영문 제목 의미 유사도는 규칙 기반 근사입니다.
- LLM 없이 빈도 기반 키워드와 간단한 유사도를 사용합니다.
- ORCID, DBLP, 연구실 publication 정밀 파싱은 확장 지점만 마련했습니다.

## 향후 확장

- 교수 확인/수정 UI와 연동
- ORCID, DBLP, Semantic Scholar 소스 추가
- 학과별 크롤러 템플릿/선택자 학습
- 연구실 publication 페이지 정밀 파싱
- LLM 기반 요약/주제 군집화 옵션
- 관리자 검수 큐와 rejected 후보 재검토 워크플로
