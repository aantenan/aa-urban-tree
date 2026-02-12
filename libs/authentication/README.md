# Authentication library

Pluggable auth (mock for dev, JWT for prod), plus shared utilities for password, JWT, session, lockout, and route protection.

## Provider interface

`AuthProvider` defines: `authenticate`, `verify`, `register`, `logout`, `refresh_token`, `reset_password`, `lock_account`, `unlock_account`. JWT payload includes user id, email, and role.

- **get_provider(user_repository=None)** returns the configured provider (`AUTH_PROVIDER=mock|jwt`). For JWT you must pass a `UserRepository` (see below); otherwise a stub is returned.
- **MockAuthProvider**: in-memory users (configurable via `MOCK_AUTH_USERS`), tokens, lockout; supports all interface methods.
- **JwtAuthProvider(user_repository)**: full implementation with signing, validation, refresh, lockout, password rules; requires a `UserRepository` implementation (e.g. backend DB adapter).

## UserRepository (for JWT)

Protocol used by `JwtAuthProvider`: `get_by_email`, `get_by_id`, `create_user`, `update_password`, `set_account_status`, `record_login_attempt`, `create_password_reset`, `get_password_reset`, `mark_password_reset_used`, `email_exists`. Implement with your DB (e.g. Peewee models) and pass to `get_provider(user_repository=...)`.

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
