# Authentication library

Pluggable auth (mock for dev, JWT for prod), plus shared utilities for password, JWT, session, lockout, and route protection.

## Provider

- `get_provider()` returns the configured provider (`AUTH_PROVIDER=mock|jwt`).
- **Mock**: configurable fake users via `MOCK_AUTH_USERS` (see backend docs).
- **JWT**: implement `JwtAuthProvider` using `authentication.utils.jwt` and your user store.

## Utilities

### Password
- `hash_password(password)` / `verify_password(password, hashed)` — bcrypt (`BCRYPT_SALT_ROUNDS`).
- `validate_password_complexity(password, min_length=8, require_upper/lower/digit=True)` — returns `(ok, error_message)`.

### JWT
- `create_token(payload, expire_seconds=...)` — signed token with `exp`/`iat` (`JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXPIRE_SECONDS`).
- `decode_token(token)` / `validate_token(token)` — decode or validate (returns `None` if invalid/expired).

### Session
- `SESSION_EXPIRE_SECONDS` (default 7200 = 2h), `WARNING_BEFORE_EXPIRE_SECONDS` (default 300 = 5 min).
- `seconds_until_expiry(exp_claim)` / `should_warn_expiry(exp_claim)` for session UX.

### Lockout
- `LockoutTracker(max_attempts=5, lockout_seconds=900)` — in-memory; call `record_failure(id)` on failed login, `reset(id)` on success, `is_locked(id)` before attempting login.

### Email
- `validate_email_format(email)` — returns `(ok, error_message)`.
- `check_email_unique(email, is_taken)` — async; use with a DB check callback.

### Errors
- `InvalidCredentialsError`, `AccountLockedError`, `TokenInvalidError`, `PasswordComplexityError` — use `.public_message` for API responses (security-conscious).

### Middleware (FastAPI)
- `get_current_user` — Depends() that validates Bearer token and returns payload; raises 401 if missing/invalid.
- `require_auth` — alias for `get_current_user`.

## Env (optional)

- `AUTH_PROVIDER`, `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXPIRE_SECONDS`
- `BCRYPT_SALT_ROUNDS`, `SESSION_EXPIRE_SECONDS`, `WARNING_BEFORE_EXPIRE_SECONDS`
- `LOCKOUT_MAX_ATTEMPTS`, `LOCKOUT_SECONDS`
