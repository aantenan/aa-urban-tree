"""Default dev users to seed so mock auth can resolve user_id by email."""
# Emails here should match MOCK_AUTH_USERS (or mock default: dev@example.com, admin@example.com).
# Password hash is placeholder; mock auth does not use DB for login.
DEFAULT_SEED_USERS = [
    {"email": "dev@example.com", "password_hash": "seeded"},
    {"email": "admin@example.com", "password_hash": "seeded"},
    {"email": "jon@doe.com", "password_hash": "seeded"},
]
