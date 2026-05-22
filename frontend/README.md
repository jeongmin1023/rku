# LabFit Frontend

Next.js + TypeScript + Tailwind CSS로 구현한 LabFit 프론트엔드입니다. 교수님 평가나 순위가 아니라 공개 근거와 관심 주제의 연결성을 탐색하는 UI를 목표로 합니다.

## 실행

```bash
cd frontend
npm.cmd install
npm.cmd run dev
```

브라우저에서 `http://localhost:3000`을 엽니다.

PowerShell 실행 정책 때문에 `npm` 대신 `npm.cmd`를 권장합니다.

## Mock Mode

기본값은 mock mode입니다. 백엔드가 실행되지 않아도 전체 화면 흐름을 확인할 수 있습니다.

```env
NEXT_PUBLIC_USE_MOCKS=true
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

실제 백엔드에 연결하려면:

```env
NEXT_PUBLIC_USE_MOCKS=false
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

백엔드 mock 수집까지 함께 보려면 백엔드에서 `LABFIT_USE_MOCK_ONLY=1`을 켜고 실행하세요.

## 데모 플로우

1. 홈에서 학교명, 학과명, 교수소개 페이지 URL, 관심 연구주제를 입력합니다.
2. `교수님 목록 가져오기`를 누릅니다.
3. 크롤링 결과 확인 화면에서 교수명/연구분야를 수정하거나 제외할 수 있습니다.
4. `논문 수집 시작`을 누릅니다.
5. 논문 후보 수, MasterPaper 병합 수, accepted/needs_review/rejected 수를 확인합니다.
6. 교수님 카드 목록에서 연구 키워드, 연구 흐름, 근거 신뢰도를 확인합니다.
7. `자세히 보기`에서 연구 요약, 논문, 관심 주제 비교, 컨택 준비 탭을 확인합니다.
8. 카드의 비교 아이콘으로 최대 3명의 연구 방향을 나란히 확인합니다.

## UI 원칙

- 교수님 순위, 별점, 점수 경쟁 UI를 사용하지 않습니다.
- 비교는 우열 비교가 아니라 연구 방향을 나란히 확인하는 기능입니다.
- 인용수는 합산하지 않고 출처별 “인용 신호”로 표시합니다.
- `needs_review`, `공개 논문 데이터 제한`, `근거 신뢰도`를 명확히 표시합니다.
- 논문이 적은 경우 낮은 평가가 아니라 Emerging Lab 또는 공개 데이터 제한으로 안내합니다.

## 주요 파일

- `app/page.tsx`: 전체 화면 플로우
- `lib/api.ts`: backend API와 mock mode 전환
- `lib/mock-data.ts`: 오프라인 데모 데이터
- `components/ProfessorDetail.tsx`: 상세 탭 4개
- `components/ComparePanel.tsx`: 연구 방향 비교
- `components/PaperCard.tsx`: 출처별 인용 신호와 match status 표시
