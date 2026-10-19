import pytest
from steadytype_client.signin import SignInError, SignInPresenter, check_username
from steadytype_client.store import Store


def test_usernames_are_last_name_dot_first_name():
    assert check_username("Prater.Devin") == "prater.devin"
    with pytest.raises(SignInError, match="lastname.firstname"):
        check_username("devin")
    with pytest.raises(SignInError, match="lastname.firstname"):
        check_username("prater.devin.2")


def test_student_signs_in_with_a_username(tmp_path):
    presenter = SignInPresenter(Store(tmp_path / "s.db"))
    presenter.create_student("prater.devin")
    assert presenter.sign_in_student("prater.devin").role == "student"


def test_unknown_student_gets_one_plain_error(tmp_path):
    presenter = SignInPresenter(Store(tmp_path / "s.db"))
    with pytest.raises(SignInError, match="Ask your teacher"):
        presenter.sign_in_student("nobody.here")


def test_staff_sign_in_needs_the_password(tmp_path):
    presenter = SignInPresenter(Store(tmp_path / "s.db"))
    presenter.create_staff("admin", "a long staff password", "Teacher")
    assert presenter.sign_in_staff("admin", "a long staff password").role == "staff"
    with pytest.raises(SignInError, match="do not match"):
        presenter.sign_in_staff("admin", "wrong")


def test_a_student_cannot_use_the_staff_path(tmp_path):
    presenter = SignInPresenter(Store(tmp_path / "s.db"))
    presenter.create_student("prater.devin")
    with pytest.raises(SignInError, match="do not match"):
        presenter.sign_in_staff("prater.devin", "asdf")


def test_remembering_a_username_survives_a_new_presenter(tmp_path):
    store = Store(tmp_path / "s.db")
    presenter = SignInPresenter(store)
    presenter.create_student("prater.devin")
    presenter.sign_in_student("prater.devin", remember=True)
    assert SignInPresenter(store).remembered() == "prater.devin"
