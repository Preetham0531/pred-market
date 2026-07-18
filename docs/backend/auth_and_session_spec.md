# Auth And Session Spec

This document defines the Pred-Market V1 authentication, session, role, and route-protection model.

The production auth owner is:

```text
FastAPI backend
```

The Next.js frontend renders auth UI and calls backend APIs. It must not store access tokens in localStorage.

## 1. Auth Goals

Auth must protect:

```text
wallet balances
orders
positions
market suggestion submissions
admin review actions
settlement actions
audit history
private user analytics
```

Auth must support:

```text
sign-up
sign-in
sign-out
session refresh
email verification
password reset
role checks
admin MFA requirement
session revocation
account lockout
audit logging
WebSocket authentication
```

## 2. Security Defaults

Password storage:

```text
Argon2id
unique salt per password
server-side pepper optional through secret manager
never store plaintext passwords
never log password fields
```

Session storage:

```text
short-lived access session
rotating refresh token
refresh token hash stored in database
browser session delivered through HttpOnly Secure SameSite cookie
CSRF token required for mutating browser requests
```

Do not use:

```text
localStorage tokens
plaintext refresh tokens in database
long-lived bearer tokens in JavaScript
admin actions without MFA
```

## 3. Roles

V1 roles:

```text
USER
ADMIN
CHECKER
MARKET_CREATOR
MARKET_MAKER
```

Role behavior:

```text
USER can trade, view wallet, view portfolio, suggest markets
ADMIN can review markets, pause markets, upload evidence, view risk queue
CHECKER can approve resolution proposals made by another admin
MARKET_CREATOR can create admin-originated markets
MARKET_MAKER can access future maker tools and incentives
```

Role rules:

```text
roles are assigned server-side only
frontend role checks are display hints only
backend must enforce all role gates
admin self-approval is blocked
checker must differ from maker for settlement approval
```

## 4. Route Access Rules

Public routes:

```text
/markets
/markets/{market_id}
/categories/{category_slug}
/sign-in
/sign-up
/forgot-password
/reset-password
/verify-email
```

Signed-in routes:

```text
/watchlist
/portfolio
/orders
/wallet
/markets/suggest
/account/security
```

Admin routes:

```text
/admin
/admin/*
```

Admin route requirements:

```text
active session
ADMIN role
MFA verified for sensitive actions
account status ACTIVE
```

## 5. API Endpoints

Base path:

```text
/api/v1
```

Auth endpoints:

```text
POST /auth/sign-up
POST /auth/sign-in
POST /auth/sign-out
POST /auth/refresh
GET /auth/me
POST /auth/verify-email/request
POST /auth/verify-email/confirm
POST /auth/password-reset/request
POST /auth/password-reset/confirm
POST /auth/ws-ticket
```

All mutating browser requests must include:

```text
CSRF token
Idempotency-Key where command creates financial or admin effects
```

## 6. Sign-Up Flow

Input:

```text
email
password
display_name
terms_acceptance
jurisdiction_hint
```

Server flow:

```text
normalize email
check duplicate email
validate password strength
hash password with Argon2id
create user status ACTIVE or PENDING_REVIEW depending on jurisdiction
assign USER role
create default wallet in simulated mode
send email verification token
create audit log
create session if policy allows
```

Response:

```text
user profile
session cookie
csrf token
```

## 7. Sign-In Flow

Input:

```text
email
password
```

Server flow:

```text
normalize email
load user by email
reject if status is SUSPENDED or CLOSED
reject if locked_until is in future
verify password hash
increment failed_login_count on failure
lock account after configured failure threshold
reset failed_login_count on success
create session
rotate refresh token
record last_login_at
create audit log
```

Generic error:

```text
Invalid email or password.
```

Do not reveal whether the email exists.

## 8. Sign-Out Flow

Server flow:

```text
revoke current refresh token
delete session cookie
write audit log
return success
```

Sign-out should be idempotent.

## 9. Refresh Flow

Server flow:

```text
read refresh cookie
hash presented token
find active refresh token row
reject if expired or revoked
revoke old token
issue new token
update session expiry
return new session cookie
```

Refresh-token reuse detection:

```text
revoke all sessions for user
mark account PENDING_REVIEW if risk threshold is high
write security audit event
```

## 10. Email Verification

Token table:

```text
email_verification_tokens
```

Rules:

```text
store token hash only
expire token after configured TTL
single use only
rate limit request endpoint
do not reveal whether email exists
```

On confirmation:

```text
set users.email_verified_at
mark token used
write audit log
```

## 11. Password Reset

Token table:

```text
password_reset_tokens
```

Rules:

```text
store token hash only
expire token quickly
single use only
rate limit by email and IP
do not reveal whether email exists
```

On successful reset:

```text
update password_hash
revoke all existing refresh tokens
reset failed_login_count
write audit log
```

## 12. Admin MFA

V1 requirement:

```text
admins must have MFA before sensitive production actions
```

Sensitive actions:

```text
approve market
pause market
upload resolution evidence
create resolution proposal
approve resolution
settle market
void market
manual wallet adjustment
change user status
assign roles
```

Early simulated build may show MFA status as mocked, but production backend must enforce it.

## 13. Session Database Tables

Extend `users` with:

```text
email_verified_at TIMESTAMPTZ NULL
failed_login_count INTEGER NOT NULL DEFAULT 0
locked_until TIMESTAMPTZ NULL
last_login_at TIMESTAMPTZ NULL
```

Add `auth_sessions`:

```text
id UUID PRIMARY KEY
user_id UUID NOT NULL REFERENCES users(id)
refresh_token_hash TEXT NOT NULL UNIQUE
user_agent TEXT NULL
ip_hash TEXT NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now()
expires_at TIMESTAMPTZ NOT NULL
revoked_at TIMESTAMPTZ NULL
revoked_reason TEXT NULL
```

Add `email_verification_tokens`:

```text
id UUID PRIMARY KEY
user_id UUID NOT NULL REFERENCES users(id)
token_hash TEXT NOT NULL UNIQUE
expires_at TIMESTAMPTZ NOT NULL
used_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Add `password_reset_tokens`:

```text
id UUID PRIMARY KEY
user_id UUID NOT NULL REFERENCES users(id)
token_hash TEXT NOT NULL UNIQUE
expires_at TIMESTAMPTZ NOT NULL
used_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Add `admin_mfa_factors`:

```text
id UUID PRIMARY KEY
user_id UUID NOT NULL REFERENCES users(id)
factor_type TEXT NOT NULL
secret_ref TEXT NOT NULL
enabled_at TIMESTAMPTZ NOT NULL
last_used_at TIMESTAMPTZ NULL
disabled_at TIMESTAMPTZ NULL
```

## 14. WebSocket Auth

Private WebSocket streams must not reuse long-lived credentials in the browser.

Flow:

```text
frontend calls POST /api/v1/auth/ws-ticket
backend verifies session cookie
backend returns short-lived one-use ticket
frontend opens WebSocket with ticket
backend validates ticket and subscribes user to private channels
ticket expires quickly
```

Private channels:

```text
user:{user_id}:orders
user:{user_id}:positions
user:{user_id}:wallet
user:{user_id}:notifications
```

## 15. Audit Events

Auth audit event types:

```text
USER_SIGNED_UP
USER_SIGNED_IN
USER_SIGNED_OUT
SESSION_REFRESHED
SESSION_REVOKED
PASSWORD_RESET_REQUESTED
PASSWORD_RESET_COMPLETED
EMAIL_VERIFICATION_REQUESTED
EMAIL_VERIFIED
ACCOUNT_LOCKED
ROLE_ASSIGNED
ROLE_REMOVED
ADMIN_MFA_ENABLED
ADMIN_MFA_DISABLED
```

Audit logs must include:

```text
actor_user_id when available
target_user_id when available
request_id
ip_hash
user_agent
created_at
metadata
```

## 16. Required Tests

Test cases:

```text
sign-up creates user and wallet
duplicate email rejected
weak password rejected
sign-in succeeds with valid password
sign-in returns generic failure for bad credentials
failed attempts lock account
suspended user cannot sign in
sign-out revokes session
refresh rotates token
refresh-token reuse revokes sessions
email verification token expires
password reset token expires
password reset revokes sessions
USER cannot access admin endpoint
ADMIN without MFA cannot perform sensitive action
admin self-approval rejected
WebSocket ticket expires
```

## 17. Reference Material

Implementation should be checked against:

```text
Next.js authentication guide:
https://nextjs.org/docs/app/guides/authentication

FastAPI OAuth2/JWT guide:
https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

FastAPI WebSockets guide:
https://fastapi.tiangolo.com/advanced/websockets/

OWASP Authentication Cheat Sheet:
https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

OWASP Password Storage Cheat Sheet:
https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

OWASP CSRF Prevention Cheat Sheet:
https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html

OWASP Session Management Cheat Sheet:
https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
```
