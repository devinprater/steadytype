import pytest
from steadytype_client.store import Store


def test_student_signs_in_with_a_username_only(tmp_path):
    store = Store(tmp_path / "s.db")
    store.create_student("prater.devin")
    assert store.find_student("prater.devin").username == "prater.devin"
    assert store.find_student("PRATER.DEVIN").username == "prater.devin"
    assert store.find_student("nobody.here") is None


def test_duplicate_username_is_rejected(tmp_path):
    store = Store(tmp_path / "s.db")
    store.create_student("prater.devin")
    with pytest.raises(ValueError, match="already"):
        store.create_student("prater.devin")


def test_staff_need_the_right_password(tmp_path):
    store = Store(tmp_path / "s.db")
    store.create_staff("admin", "a long staff password", "Teacher")
    assert store.verify_staff("admin", "a long staff password").role == "staff"
    assert store.verify_staff("admin", "wrong") is None
    assert store.find_student("admin") is None


def test_students_cannot_sign_in_as_staff(tmp_path):
    store = Store(tmp_path / "s.db")
    store.create_student("prater.devin")
    assert store.verify_staff("prater.devin", "") is None
    assert store.verify_staff("prater.devin", "asdf") is None


def test_passwords_are_never_written_in_plain_text(tmp_path):
    store = Store(tmp_path / "s.db")
    store.create_staff("admin", "a long staff password", "Teacher")
    assert b"a long staff password" not in (tmp_path / "s.db").read_bytes()


def test_remember_stores_only_the_username(tmp_path):
    store = Store(tmp_path / "s.db")
    store.create_student("prater.devin")
    store.set_remember("prater.devin", True)
    assert store.remembered_username() == "prater.devin"


def test_preferences_and_attempts_round_trip(tmp_path):
    store = Store(tmp_path / "s.db")
    account = store.create_student("prater.devin")
    store.save_preferences(account.id, {"rate": 0.7})
    assert store.load_preferences(account.id) == {"rate": 0.7}
    store.save_attempt(account.id, {"id": "a1", "wpm": 30.0})
    assert store.attempts(account.id) == [{"id": "a1", "wpm": 30.0}]
