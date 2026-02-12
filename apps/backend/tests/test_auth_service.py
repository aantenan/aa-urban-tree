"""Tests for UserAuthenticationService and auth workflows."""
import pytest

from database.connection import database_proxy
from database.models import User, PasswordReset, LoginAttempt


@pytest.fixture(autouse=True)
def use_memory_db(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    import database.connection as conn
    conn._db = None
    db = conn.get_db()
    database_proxy.initialize(db)
    db.create_tables([User, PasswordReset, LoginAttempt])
    yield
    database_proxy.initialize(None)
    db.close()
    conn._db = None


@pytest.fixture(autouse=True)
def jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AUTH_PROVIDER", "jwt")
    monkeypatch.setenv("JWT_SECRET", "test-secret")


def test_register_and_login() -> None:
    from services.auth_service import UserAuthenticationService
    svc = UserAuthenticationService()
    svc.register("u@example.com", "SecureP4ss")
    out = svc.login("u@example.com", "SecureP4ss")
    assert out["token"]
    assert out["user"]["email"] == "u@example.com"


def test_login_wrong_password() -> None:
    from authentication import InvalidCredentialsError
    from services.auth_service import UserAuthenticationService
    svc = UserAuthenticationService()
    svc.register("u@example.com", "SecureP4ss")
    with pytest.raises(InvalidCredentialsError):
        svc.login("u@example.com", "WrongPass")


def test_register_duplicate_email() -> None:
    from services.auth_service import UserAuthenticationService
    svc = UserAuthenticationService()
    svc.register("u@example.com", "SecureP4ss")
    with pytest.raises(ValueError, match="already registered"):
        svc.register("u@example.com", "OtherP4ss")


def test_password_complexity_on_register() -> None:
    from services.auth_service import UserAuthenticationService
    svc = UserAuthenticationService()
    with pytest.raises(ValueError, match="8"):
        svc.register("u@example.com", "short")


def test_lockout_after_five_failures() -> None:
    from authentication import AccountLockedError
    from services.auth_service import UserAuthenticationService
    svc = UserAuthenticationService()
    svc.register("u@example.com", "SecureP4ss")
    for _ in range(5):
        try:
            svc.login("u@example.com", "wrong")
        except Exception:
            pass
    with pytest.raises(AccountLockedError):
        svc.login("u@example.com", "SecureP4ss")


def test_reset_password_flow() -> None:
    from services.auth_service import UserAuthenticationService
    svc = UserAuthenticationService()
    svc.register("u@example.com", "OldPass1")
    svc.forgot_password("u@example.com")
    pr = PasswordReset.select().order_by(PasswordReset.created_at.desc()).first()
    assert pr is not None
    out = svc.reset_password(pr.reset_token, "NewPass1")
    assert "reset" in out["message"].lower()
    out = svc.login("u@example.com", "NewPass1")
    assert out["token"]


def test_refresh_token() -> None:
    from services.auth_service import UserAuthenticationService
    svc = UserAuthenticationService()
    svc.register("u@example.com", "SecureP4ss")
    login_out = svc.login("u@example.com", "SecureP4ss")
    refresh_out = svc.refresh_token(login_out["token"])
    assert refresh_out["token"] != login_out["token"]
    assert refresh_out["user"]["email"] == "u@example.com"


def test_login_attempt_recorded() -> None:
    from services.auth_service import UserAuthenticationService
    svc = UserAuthenticationService()
    svc.register("u@example.com", "SecureP4ss")
    try:
        svc.login("u@example.com", "wrong", ip_address="127.0.0.1")
    except Exception:
        pass
    attempts = list(LoginAttempt.select().where(LoginAttempt.email == "u@example.com"))
    assert len(attempts) == 1
    assert attempts[0].success is False
    assert attempts[0].ip_address == "127.0.0.1"
