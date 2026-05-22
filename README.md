# LabFit MVP

LabFit은 교수님을 평가하거나 순위를 매기는 앱이 아닙니다. 특정 대학·학과의 교수소개 페이지와 공개 논문 메타데이터를 바탕으로, 대학원 진학 희망자가 자신의 관심 연구주제와 연구실 방향의 연결성을 탐색하도록 돕는 도구입니다.

## 실행

### Backend

```powershell
cd backend
python -m pip install -r requirements.txt
$env:LABFIT_USE_MOCK_ONLY="1"
python -m uvicorn app.main:app --reload
```

API 문서는 `http://127.0.0.1:8000/docs`에서 확인할 수 있습니다.

### Frontend

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

프론트는 기본 mock mode로도 전체 화면 흐름을 볼 수 있습니다. 실제 backend에 연결하려면 `NEXT_PUBLIC_USE_MOCKS=false`와 `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000`을 설정하세요.

## 현재 수집 구조

- 기본 파이프라인은 KCI, RISS, DBpia, ScienceON, Crossref 중심입니다.
- OpenAlex는 기본 수집 파이프라인에서 제외했고, 향후 확장 가능한 선택 소스로만 남겨두었습니다.
- Crossref는 DOI/title 기반 메타데이터 보강용으로 사용합니다.
- 인용수와 이용수는 합산하지 않고 source별 인용 신호로 따로 표시합니다.

## 데이터 흐름

`Paper Candidate -> NormalizedPaperCandidate -> MasterPaper -> ProfessorPaper -> AnalysisResult`

여러 사이트에서 같은 논문이 들어오면 DOI, UCI/KCI ID, 제목 유사도, 저자, 연도, venue 근거로 병합합니다. 애매한 후보는 무리하게 합치지 않고 `duplicate_possible`로 남깁니다.

## 연구 경향 요약

연구 경향성은 accepted 논문 중심으로 만들고, needs_review 논문은 낮은 가중치의 보조 근거로만 사용합니다. 공개 논문이 부족하면 공식 연구분야와 연구실 소개 키워드를 활용하며, LLM API가 없어도 템플릿 기반 fallback이 동작합니다.

LLM은 연구력 평가나 논문 진위 판정자가 아닙니다. 이미 정제된 키워드와 논문 근거를 읽기 쉬운 문장으로 정리하는 역할만 맡도록 분리되어 있습니다.
