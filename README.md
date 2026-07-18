# Pred-Market

Pred-Market is a V1 prediction market exchange workspace with a Next.js frontend and a FastAPI/PostgreSQL/Redis backend. V1 uses simulated funds only.

The current implementation includes:

```text
- market discovery
- market detail and trade ticket
- category dashboards
- watchlist
- portfolio
- orders
- wallet
- market suggestion flow
- admin review queue
- backend auth/session APIs
- persisted watchlist APIs
- simulated wallet, ledger, orders, matching, positions, settlement
- analytics rollups and FastAPI WebSockets
```

## Development

Start infrastructure:

```bash
docker compose up -d postgres redis
```

Backend runs on port `8010` locally because port `8000` is occupied on the current machine. Postgres is exposed on host port `5433`, Redis on `6379`.

```bash
cd backend
uv sync
alembic upgrade head
python -m app.seed.dev
uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
```

Verify backend startup:

```bash
curl http://localhost:8010/api/v1/health
curl http://localhost:8010/api/v1/categories
curl http://localhost:8010/api/v1/markets
```

Install frontend dependencies:

```bash
npm install
```

Run the frontend on `3000`:

```bash
npm run dev
```

Use `.env.local` for real backend mode:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8010
NEXT_PUBLIC_USE_MOCK_DATA=false
```

Set `NEXT_PUBLIC_USE_MOCK_DATA=true` only for populated visual-preview mode.

Validate the frontend:

```bash
npm run typecheck
npm run lint
npm run build
```

## Notes

Real deposits, withdrawals, KYC/AML, payment-provider integration, and production compliance controls are intentionally out of scope for V1.
