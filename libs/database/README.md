# Database library

Peewee ORM with SQLite (development) and PostgreSQL (production).

## Configuration

- `DATABASE_URL`: SQLite example `sqlite:///./local.db`, PostgreSQL `postgresql://user:pass@host:5432/dbname`
- `DB_TYPE`: optional override; connection is derived from `DATABASE_URL` (no extra env required)

## Usage

1. Call `database.connection.init_db()` at application startup.
2. Call `database.migrations.runner.run_migrations()` to create tables (safe, idempotent).
3. Use `BaseModel` from `database.models` for new models (UUID pk, `created_at`, `updated_at`).

## Indexing and constraints

- Add indexes on frequently queried columns (e.g. `user_id`, `application_id`, `status`, `county`) in model `Meta.indexes`.
- Use `unique=True` on email/confirmation number fields.
- Foreign keys and referential integrity are enforced by Peewee.

## Backups

- SQLite: copy the `.db` file when the app is idle.
- PostgreSQL: use `pg_dump` / your provider’s backup procedures.

All queries use parameterized statements to prevent SQL injection.
