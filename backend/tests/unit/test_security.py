from datetime import timedelta

from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)


def test_hash_password_creates_valid_hash():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert hashed != password
    assert len(hashed) > 0
    assert "$argon2" in hashed or "$2b$" in hashed  # Check for typical hash prefixes


def test_verify_password_correct():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert verify_password("wrong_password", hashed) is False


def test_create_access_token():
    user_id = "test_user_id"
    token = create_access_token(subject=user_id)
    assert len(token) > 0

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert "exp" in payload


def test_decode_access_token_expired():
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


def test_decode_access_token_invalid():
    assert decode_access_token("invalid_token") is None
