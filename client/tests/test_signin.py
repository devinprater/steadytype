import pytest
from steadytype_client.signin import SignInError, SignInPresenter
from steadytype_client.store import Store


def test_sign_in_reports_one_plain_error(tmp_path):
    presenter = SignInPresenter(Store(tmp_path / "s.db"))
    with pytest.raises(SignInError, match="do not match"):
        presenter.sign_in("nobody", "nothing", False)


def test_created_account_can_sign_in(tmp_path):
    presenter = SignInPresenter(Store(tmp_path / "s.db"))
    presenter.create_account("dana", "a long password", "Dana")
    assert presenter.sign_in("dana", "a long password", False).display_name == "Dana"


def test_remembering_a_username_survives_a_new_presenter(tmp_path):
    store = Store(tmp_path / "s.db")
    presenter = SignInPresenter(store)
    presenter.create_account("dana", "a long password", "Dana")
    presenter.sign_in("dana", "a long password", True)
    assert SignInPresenter(store).remembered() == "dana"
