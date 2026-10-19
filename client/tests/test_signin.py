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


def test_the_server_address_is_saved_and_cleaned(tmp_path):
    presenter = SignInPresenter(Store(tmp_path / "s.db"))
    assert presenter.set_server_address(" https://typing.school.org/ ") == "https://typing.school.org"
    assert SignInPresenter(presenter.store).server_address() == "https://typing.school.org"
    assert presenter.set_server_address("") == ""
    assert presenter.server_address() == ""


def test_a_bad_server_address_gets_a_plain_error(tmp_path):
    presenter = SignInPresenter(Store(tmp_path / "s.db"))
    with pytest.raises(SignInError, match="https://"):
        presenter.set_server_address("typing.school.org")


def test_a_student_known_only_to_the_server_can_sign_in(tmp_path):
    calls = []

    def remote(server, username):
        calls.append((server, username))
        return "token-123"

    presenter = SignInPresenter(Store(tmp_path / "s.db"), remote=remote)
    presenter.set_server_address("https://typing.school.org")
    account = presenter.sign_in_student("Prater.Devin")
    assert account.username == "prater.devin"
    assert calls == [("https://typing.school.org", "prater.devin")]
    assert presenter.store.get_setting("sync_token") == "token-123"
    assert presenter.store.get_setting("sync_server") == "https://typing.school.org"


def test_a_student_the_server_does_not_know_still_gets_that_error(tmp_path):
    presenter = SignInPresenter(Store(tmp_path / "s.db"), remote=lambda *_: None)
    presenter.set_server_address("https://typing.school.org")
    with pytest.raises(SignInError, match="Ask your teacher"):
        presenter.sign_in_student("nobody.here")


def test_staff_can_sign_in_through_the_server_on_a_new_machine(tmp_path):
    presenter = SignInPresenter(Store(tmp_path / "s.db"),
                                remote_staff=lambda *_: "staff-token")
    presenter.set_server_address("https://typing.school.org")
    account = presenter.sign_in_staff("Owner", "a long staff password")
    assert account.role == "staff"
    assert presenter.store.get_setting("sync_token") == "staff-token"
    assert presenter.sign_in_staff("owner", "a long staff password").role == "staff"


def test_offline_student_sign_in_never_calls_a_server(tmp_path):
    def explode(*_):
        raise AssertionError("no server should be called")

    presenter = SignInPresenter(Store(tmp_path / "s.db"), remote=explode)
    presenter.create_student("prater.devin")
    assert presenter.sign_in_student("prater.devin").role == "student"
