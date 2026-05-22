# LabFit MVP

LabFit은 교수님을 평가하거나 순위를 매기는 서비스가 아닙니다. 공개 논문·연구실 정보를 바탕으로 사용자의 관심 주제와 연구실 방향의 연결성을 확인하는 연구실 탐색 도구입니다.

## Backend

```bash
cd backend
python -m pip install -r requirements.txt
set LABFIT_USE_MOCK_ONLY=1
python -m uvicorn app.main:app --reload
```

자세한 내용은 `backend/README.md`를 확인하세요.

## Frontend

```bash
cd frontend
npm.cmd install
npm.cmd run dev
```

기본 mock mode에서는 백엔드 없이도 `http://localhost:3000`에서 전체 UI 흐름을 확인할 수 있습니다. 실제 API 연결은 `frontend/.env.example`을 참고해 `NEXT_PUBLIC_USE_MOCKS=false`로 전환하면 됩니다.
