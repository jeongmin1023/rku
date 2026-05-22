# LabFit Frontend

Next.js + TypeScript + Tailwind CSS로 구현한 LabFit UI입니다. 교수님 평가/순위 UI가 아니라 공개 근거와 관심 연구주제의 연결성을 탐색하는 화면을 제공합니다.

## 실행

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

브라우저에서 `http://localhost:3000`을 엽니다.

## Mock Mode

기본값은 mock mode입니다. backend가 실행되지 않아도 전체 화면 흐름을 확인할 수 있습니다.

```env
NEXT_PUBLIC_USE_MOCKS=true
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

실제 backend에 연결하려면:

```env
NEXT_PUBLIC_USE_MOCKS=false
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

## 데모 플로우

1. 학교명, 학과명, 교수소개 페이지 URL, 관심 연구주제를 입력합니다.
2. 크롤링 결과 확인 화면에서 교수님 후보를 수정하거나 제외합니다.
3. 논문 수집을 시작하면 KCI, RISS, DBpia, ScienceON, Crossref 중심 후보가 정리됩니다.
4. 교수님 카드에서 연구 키워드, 연구 경향성 한 줄, 근거 신뢰도, 출처 커버리지를 확인합니다.
5. 상세 페이지에서 연구 경향성, 최근 3년/5년 키워드, 대표 논문, 최근 연구 논문, 관심주제 관련 논문, 보조 후보 논문을 봅니다.
6. 컨택 준비 카드에서 읽을 논문 3개, 질문, 메일 포인트를 정리합니다.

## UI 원칙

- 교수님 순위, 별점, 점수 경쟁 UI를 사용하지 않습니다.
- 비교 화면은 우열 비교가 아니라 연구 방향을 나란히 보는 기능입니다.
- 인용수/이용수는 합산하지 않고 source별 인용 신호로 표시합니다.
- `needs_review`, `weak_candidate`, `공개 데이터 제한`, `근거 신뢰도`를 명확히 표시합니다.
