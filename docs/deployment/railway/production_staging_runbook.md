# Railway Production-Style Staging Runbook

This runbook operates Pred-Market as an externally reachable staging exchange using simulated funds only.

## Service Topology

```text
Railway project: wholesome-mindfulness
Environment: production

pred-market          Next.js frontend
pred-market-backend  FastAPI backend
Postgres             source-of-truth database
Redis                rate limits, MFA challenges, WebSocket tickets
```

The browser uses the frontend Railway domain. REST calls stay on that domain through the Next.js `/api/v1/*` rewrite. WebSockets connect to the backend Railway domain using a short-lived ticket.

## Ownership

Codex can perform:

- code, migrations, automated tests, Docker builds, Git commits, and deployments
- creating/configuring the backend Railway service
- non-secret Railway variables and generated application keys
- staging reference-data seed and health checks

The account owner must perform:

- add the Resend API key as a sealed variable
- add the one-time admin bootstrap password as a sealed variable
- scan the authenticator QR code and store recovery codes offline
- enable and review Railway volume backups, usage, and billing

## Railway Service Settings

Both application services use repository root `/` as build context.

Frontend:

```text
Source: Preetham0531/pred-market
Branch: main
Config file: /railway.frontend.json
```

Backend:

```text
Source: Preetham0531/pred-market
Branch: main
Config file: /railway.backend.json
Healthcheck: /health/ready
Pre-deploy: alembic upgrade head
Port: 8080
```

Railway requires a custom config path to be selected in each service's Settings. The path is absolute from the repository root and does not follow a monorepo root-directory setting.

## Backend Variables

```text
PORT=8080
ENVIRONMENT=staging
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
CORS_ORIGINS=https://${{pred-market.RAILWAY_PUBLIC_DOMAIN}}
FRONTEND_BASE_URL=https://${{pred-market.RAILWAY_PUBLIC_DOMAIN}}
COOKIE_SECURE=true
DEMO_SEED_ENABLED=false
PUBLIC_SIGNUP_ENABLED=true
EMAIL_VERIFICATION_REQUIRED=false
ADMIN_MFA_REQUIRED=true
EMAIL_DELIVERY_ENABLED=false
ADMIN_BOOTSTRAP_EMAIL=bindelapreetham2004@gmail.com
JWT_SECRET_KEY=<sealed random value>
MFA_ENCRYPTION_KEY=<sealed Fernet key>
```

After Resend is configured:

```text
EMAIL_DELIVERY_ENABLED=true
RESEND_API_KEY=<sealed owner-provided value>
RESEND_FROM=Pred-Market <onboarding@resend.dev>
```

Until a sender domain is verified, email verification stays non-blocking. Do not enable `EMAIL_VERIFICATION_REQUIRED` until public verification and password-reset delivery have been tested.

## Frontend Variables

```text
NEXT_PUBLIC_USE_MOCK_DATA=false
NEXT_PUBLIC_USE_DIRECT_API=false
INTERNAL_API_BASE_URL=http://${{pred-market-backend.RAILWAY_PRIVATE_DOMAIN}}:8080
NEXT_PUBLIC_WS_BASE_URL=wss://${{pred-market-backend.RAILWAY_PUBLIC_DOMAIN}}
```

`NEXT_PUBLIC_*` values are compiled into the Next.js build, so changing them requires a frontend redeploy.

## First Deployment

1. Deploy backend and wait for `/health/ready` to return `200`.
2. Confirm the migration pre-deploy command reached Alembic head.
3. Run the idempotent staging seed:

   ```bash
   railway run --service pred-market-backend --environment production --no-local -- python -m app.seed.staging
   ```

4. Set the bootstrap password without printing it:

   ```bash
   railway variable set ADMIN_BOOTSTRAP_PASSWORD --stdin --service pred-market-backend --environment production
   ```

5. Bootstrap the admin:

   ```bash
   railway run --service pred-market-backend --environment production --no-local -- python -m app.seed.create_admin
   ```

6. Delete the bootstrap password immediately:

   ```bash
   railway variable delete ADMIN_BOOTSTRAP_PASSWORD --service pred-market-backend --environment production
   ```

7. Configure frontend variables and redeploy.
8. Sign in as `bindelapreetham2004@gmail.com`, enroll authenticator MFA, download all ten recovery codes, then confirm `/admin` works.

## Acceptance Checks

```bash
curl -fsS https://BACKEND_DOMAIN/health/live
curl -fsS https://BACKEND_DOMAIN/health/ready
curl -fsS https://FRONTEND_DOMAIN/api/v1/categories
curl -fsS https://FRONTEND_DOMAIN/api/v1/markets
```

Browser checks:

- `/` is public and shows the product landing page.
- `/markets` shows six clearly labeled simulation markets.
- signup creates a `USER`, never an `ADMIN`.
- admin password login requires setup or a TOTP challenge.
- replaying a TOTP code fails.
- admin actions fail without an MFA-verified session.
- simulated deposit, order creation, cancellation, wallet, portfolio, and order book work.
- public/private WebSocket channels connect without CORS or origin failures.

## Everyday Commands

```bash
railway status
railway service status --json
railway logs --service pred-market-backend
railway logs --service pred-market
railway redeploy --service pred-market-backend
railway redeploy --service pred-market
railway open
```

Never paste `railway variable list --kv` or JSON variable output into a ticket or chat because those formats include raw secrets.

## Migration And Seed Operations

Migration status:

```bash
railway run --service pred-market-backend --environment production --no-local -- alembic current
railway run --service pred-market-backend --environment production --no-local -- alembic heads
```

Apply migrations manually only when diagnosing a failed pre-deploy:

```bash
railway run --service pred-market-backend --environment production --no-local -- alembic upgrade head
```

The staging seed is idempotent. It creates ten categories, the approved-source registry, and six simulated markets. It does not create shared-password traders or import the local twenty-user simulation.

## Backup And Restore

In Railway, open `Postgres -> Volumes -> Backups`:

1. Enable daily backups.
2. Enable weekly backups.
3. Create one manual backup immediately after migration, seed, and admin bootstrap.
4. Record backup timestamp and migration revision.

Test restores in a separate Railway environment or database service. Never restore over the only working database as a test.

## Rollback

Application rollback:

1. Open the failed service deployment history.
2. Select the last known-good deployment.
3. Redeploy that image.
4. Verify `/health/ready` and frontend REST proxy calls.

Database rollback:

- Prefer a forward-fix migration.
- Use `alembic downgrade` only when the migration explicitly supports safe data reversal.
- Restore a volume backup only after identifying the data-loss window and stopping writes.

## Monitoring

Monitor:

```text
Frontend: https://pred-market-production.up.railway.app/
Backend:  https://BACKEND_DOMAIN/health/ready
```

Alert on non-2xx responses, response latency, deployment restarts, PostgreSQL storage, Redis memory, and Railway spend. Backend readiness intentionally fails if PostgreSQL or Redis is unavailable; liveness only proves the process is running.

## Security Boundaries

- Never commit `.env`, passwords, JWT keys, Fernet keys, Resend keys, database URLs, TOTP secrets, or recovery codes.
- Access JWT and refresh tokens remain in HttpOnly cookies.
- Browser mutations require the readable CSRF cookie value in `X-CSRF-Token`.
- Refresh tokens are opaque, hashed in PostgreSQL, and rotated.
- TOTP secrets are encrypted; recovery codes are hashed and one-time use.
- Admin MFA is mandatory. Trader MFA is optional.
- Admin impersonation remains read-only and audited.
- This environment must not process real deposits, withdrawals, KYC, or real-money contracts.

## Official Railway References

- Config as code: https://docs.railway.com/config-as-code
- Monorepo deployment: https://docs.railway.com/deployments/monorepo
- Reference variables: https://docs.railway.com/variables
- Private networking: https://docs.railway.com/networking/private-networking
- Volume backups: https://docs.railway.com/volumes/backups
