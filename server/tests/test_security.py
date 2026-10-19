from steadytype_server.security import (
    check_csrf,
    csrf_token,
    hash_password,
    new_token,
    token_hash,
    verify_password,
)


def test_password_round_trip():
    stored = hash_password("correct horse battery")
    assert stored.startswith("scrypt$")
    assert verify_password("correct horse battery", stored)
    assert not verify_password("wrong", stored)
    assert "correct horse battery" not in stored


def test_tokens_are_unique_and_hashed():
    first, second = new_token(), new_token()
    assert first != second
    assert token_hash(first) != first
    assert len(token_hash(first)) == 64


def test_csrf_round_trip():
    session = {}
    token = csrf_token(session)
    assert check_csrf(session, token)
    assert not check_csrf(session, "wrong")
    assert not check_csrf({}, token)
