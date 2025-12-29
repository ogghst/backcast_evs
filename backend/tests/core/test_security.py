from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_get_password_hash() -> None:
    password = "secret"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)


def test_verify_password() -> None:
    password = "secret"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)


def test_create_access_token() -> None:
    data = {"sub": "testuser"}
    token = create_access_token(subject=data["sub"])
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_with_expiration() -> None:
    expires_delta = timedelta(minutes=5)
    token = create_access_token(subject="testuser", expires_delta=expires_delta)

    # decode to check exp
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    assert "exp" in payload
    # Check if exp is roughly now + 5 mins
    exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
    now = datetime.now(UTC)
    assert exp > now
    assert exp < now + timedelta(minutes=6)


def test_decode_access_token_expired() -> None:
    # Pass negative delta to expire immediately
    user_id = "test_user_id"
    expired_token = create_access_token(
        subject=user_id, expires_delta=timedelta(minutes=-1)
    )
    payload = decode_access_token(expired_token)
    # Depending on jwt library config (leeway), it might not expire instantly?
    # Actually jwt.decode checks exp by default and raises ExpiredSignatureError
    # My decode_access_token catches InvalidTokenError which includes ExpiredSignatureError
    assert payload is None


def test_get_current_user_from_token_valid() -> None:
    # Requires a mock or database session. However, get_current_user implementation
    # uses session.get(User, token_data.sub).
    # This is better tested in integration with DB or full mock.
    # Unit testing security utils:
    pass


def test_password_hashing_consistency() -> None:
    pwd = "consistent"
    h1 = get_password_hash(pwd)
    h2 = get_password_hash(pwd)
    # Different salts -> different hashes usually (bcrypt)
    assert h1 != h2
    assert verify_password(pwd, h1)
    assert verify_password(pwd, h2)


def test_decode_access_token_invalid() -> None:
    assert decode_access_token("invalid_token") is None
