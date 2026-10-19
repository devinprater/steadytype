import pytest
from steadytype_client.store import Store


def test_account_round_trip(tmp_path):
    store = Store(tmp_path / "s.db")
    store.create_account("dana", "correct horse battery", "Dana")
    assert store.verify("dana", "correct horse battery").display_name == "Dana"
    assert store.verify("dana", "wrong") is None


def test_duplicate_username_is_rejected(tmp_path):
    store = Store(tmp_path / "s.db")
    store.create_account("dana", "password one", "Dana")
    with pytest.raises(ValueError, match="already"):
        store.create_account("dana", "password two", "Other")


def test_remember_stores_only_the_username(tmp_path):
    store = Store(tmp_path / "s.db")
    store.create_account("dana", "password one", "Dana")
    store.set_remember("dana", True)
    assert store.remembered_username() == "dana"
    assert b"password one" not in (tmp_path / "s.db").read_bytes()


def test_preferences_and_attempts_round_trip(tmp_path):
    store = Store(tmp_path / "s.db")
    account = store.create_account("dana", "password one", "Dana")
    store.save_preferences(account.id, {"rate": 0.7})
    assert store.load_preferences(account.id) == {"rate": 0.7}
    store.save_attempt(account.id, {"id": "a1", "wpm": 30.0})
    assert store.attempts(account.id) == [{"id": "a1", "wpm": 30.0}]
