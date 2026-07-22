# Pred-Market AWS Phase 1-2 Setup

This guide covers the first production path for Pred-Market:

1. AWS account foundation.
2. Phase 1: production container/deployment files.
3. Phase 2: AWS RDS PostgreSQL.

Domain setup is intentionally excluded here.

## Target Architecture

```text
Browser
  -> HTTPS domain later
  -> Caddy reverse proxy
  -> Next.js frontend container
  -> FastAPI backend container
  -> AWS RDS PostgreSQL
  -> Redis container for staging, ElastiCache later
```

For the final production application, Redis should move to ElastiCache and the app containers should run on ECS Fargate. For the first staging deployment, these files also work on a single server.

## AWS Account Foundation

### 1. Secure The Root Account

1. Sign in to AWS as root.
2. Open the account/security page.
3. Assign MFA to root.
4. Choose authenticator app or hardware key.
5. Scan the QR code with Google Authenticator, Microsoft Authenticator, 1Password, Authy, or Aegis.
6. Store backup/recovery details safely.
7. Stop using root for daily work.

Official AWS root MFA guide: https://docs.aws.amazon.com/IAM/latest/UserGuide/enable-virt-mfa-for-root.html

### 2. Create Daily Admin Access

Preferred path: IAM Identity Center.

1. Open IAM Identity Center.
2. Enable it for the account.
3. Create user: your daily admin email.
4. Create group: `PredMarketAdmins`.
5. Create or assign a permission set with administrator access for setup.
6. Assign the group to your AWS account.
7. Sign out from root.
8. Sign in through the IAM Identity Center access portal.
9. Add MFA to this daily admin user.

Official guide: https://docs.aws.amazon.com/singlesignon/latest/userguide/getting-started.html

### 3. Set Billing And Budget Alerts

Create a monthly cost budget immediately.

Recommended staging budget:

```text
Budget type: Cost budget
Period: Monthly
Amount: 50 USD
Alerts: 50%, 80%, 100%
Email: your billing/admin email
```

Official AWS Budgets guide: https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-create.html

### 4. Install And Configure AWS CLI

Install AWS CLI v2 locally.

```bash
brew install awscli
aws --version
```

If using IAM Identity Center:

```bash
aws configure sso
```

Use:

```text
Region: ap-south-1 for India-focused staging
Output: json
```

Verify:

```bash
aws sts get-caller-identity
```

Official CLI configuration docs: https://docs.aws.amazon.com/cli/latest/reference/configure/

## Phase 1: Production Container Files

The repo now includes:

```text
Dockerfile.frontend
backend/Dockerfile
docker-compose.production.yml
ops/Caddyfile
.env.production.example
.dockerignore
```

Local production-build verification:

```bash
cd /Users/preethambindela/pred-market
cp .env.production.example .env.production
```

Edit `.env.production` with safe staging values.

For local container testing before AWS RDS, use the existing local DB:

```text
DATABASE_URL=postgresql+psycopg://pred_market:pred_market@host.docker.internal:5433/pred_market
REDIS_URL=redis://redis:6379/0
APP_DOMAIN=localhost
CORS_ORIGINS=http://localhost
COOKIE_SECURE=false
```

Then:

```bash
docker compose up -d postgres
docker compose --env-file .env.production -f docker-compose.production.yml build
```

Run migrations against the configured database:

```bash
docker compose --env-file .env.production -f docker-compose.production.yml run --rm backend alembic upgrade head
```

Start production containers:

```bash
docker compose --env-file .env.production -f docker-compose.production.yml up -d
```

Check:

```bash
curl http://localhost/api/v1/health
```

## Phase 2: AWS RDS PostgreSQL

### Recommended RDS Settings For Staging

```text
Engine: PostgreSQL
Template: Dev/Test
DB identifier: pred-market-staging
Database name: pred_market
Master username: pred_market_app
Instance: db.t4g.micro or db.t4g.small
Storage: 20-50 GB gp3
Public access: No
Backups: enabled
Backup retention: 7 days
Encryption: enabled
Deletion protection: enabled after initial setup
Multi-AZ: off for staging, on for production
```

### Create RDS In AWS Console

1. Open RDS.
2. Choose Create database.
3. Choose Standard create.
4. Choose PostgreSQL.
5. Set DB identifier: `pred-market-staging`.
6. Set DB name: `pred_market`.
7. Set username: `pred_market_app`.
8. Generate a strong password and store it in a password manager.
9. Choose private access, not public access.
10. Enable storage encryption.
11. Enable automated backups.
12. Create the database.

Official backup docs: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html

### Store The RDS URL

Your production connection string will look like:

```text
postgresql+psycopg://pred_market_app:PASSWORD@RDS_ENDPOINT:5432/pred_market
```

Put that into Secrets Manager later. For the current Compose-based staging template, put it into `.env.production` on the server only.

### Run Migrations

After the backend container can reach RDS:

```bash
docker compose --env-file .env.production -f docker-compose.production.yml run --rm backend alembic upgrade head
```

### View The Database

Recommended database tools:

```text
DBeaver
TablePlus
pgAdmin
DataGrip
psql
```

Do not make RDS public for normal use. Use a tunnel or AWS Session Manager later.

If using an SSH tunnel through a server that can reach RDS:

```bash
ssh -L 5439:RDS_ENDPOINT:5432 ubuntu@SERVER_PUBLIC_IP
```

Then connect your DB client to:

```text
Host: localhost
Port: 5439
Database: pred_market
User: pred_market_app
Password: RDS password
```

## Acceptance Checklist

Phase 1 is ready when:

```text
Frontend image builds.
Backend image builds.
Caddy routes /api and /ws to backend.
Backend health endpoint returns database ok.
Migrations run from the backend container.
No secrets are committed.
```

Phase 2 is ready when:

```text
RDS PostgreSQL exists.
RDS is private.
Backups are enabled.
Database URL is stored outside Git.
Alembic migrations apply cleanly.
Backend health says database ok.
```
