import os

import pytest

wx = pytest.importorskip("wx")

pytestmark = pytest.mark.skipif(os.environ.get("STEADYTYPE_UI") != "1",
                                reason="set STEADYTYPE_UI=1 to build windows")


@pytest.fixture(scope="module")
def app():
    return wx.App(False)


def test_surface_has_no_children(app):
    from steadytype_client.ui.surface import LessonSurface

    frame = wx.Frame(None)
    surface = LessonSurface(frame)
    surface.show("add", 1)
    assert [child for child in surface.GetChildren() if isinstance(child, wx.Control)] == []
    frame.Destroy()


def test_main_frame_builds_with_menus(app, tmp_path):
    from steadytype_client.config import AppPaths, bundled_content
    from steadytype_client.main_controller import AppController
    from steadytype_client.sounds import NullPlayer
    from steadytype_client.speech import FakeSpeech
    from steadytype_client.store import Store
    from steadytype_client.ui.main import MainFrame
    from steadytype_engine.loader import load_course

    store = Store(tmp_path / "s.db")
    account = store.create_student("prater.devin")
    course = load_course(bundled_content())
    controller = AppController(store, account, AppPaths(tmp_path), FakeSpeech(),
                               NullPlayer(), course)
    frame = MainFrame(controller)
    assert frame.GetMenuBar() is not None
    assert [child for child in frame.surface.GetChildren() if isinstance(child, wx.Control)] == []
    frame.Destroy()


def test_sign_in_dialog_focuses_the_button_when_a_name_is_remembered(app, tmp_path):
    from steadytype_client.signin import SignInPresenter
    from steadytype_client.store import Store
    from steadytype_client.ui.signin import SignInDialog

    store = Store(tmp_path / "s.db")
    store.create_student("prater.devin")
    store.set_remember("prater.devin", True)
    dialog = SignInDialog(None, SignInPresenter(store))
    assert dialog.username.GetValue() == "prater.devin"
    assert dialog.remember.GetValue() is True
    dialog.Destroy()


def test_progress_dialog_lists_attempts(app):
    from steadytype_client.ui.progress import ProgressDialog, attempt_line, summary_line

    attempts = [
        {"lesson_id": 3, "stars": 4, "accuracy": 95.0, "wpm": 22.0,
         "active_seconds": 120, "ended_at": "2026-10-19T14:00:00"},
        {"lesson_id": 4, "stars": 5, "accuracy": 98.0, "wpm": 30.0,
         "active_seconds": 180, "ended_at": "2026-10-19T15:00:00"},
    ]
    assert "2 lessons finished" in summary_line(attempts)
    assert attempt_line(attempts[0]).startswith("Lesson 3: 4 stars")
    dialog = ProgressDialog(None, attempts)
    assert dialog.list.GetCount() == 2
    dialog.Destroy()
