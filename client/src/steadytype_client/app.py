"""Start the client: speech, store, sign-in, then the main window."""

from __future__ import annotations

import argparse
from pathlib import Path

from steadytype_engine.loader import load_course

from steadytype_client import __version__
from steadytype_client.config import AppPaths, bundled_content, default_paths
from steadytype_client.sounds import create_player
from steadytype_client.speech import FakeSpeech, SpeechUnavailable, create_speech
from steadytype_client.store import Store


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="steadytype-client")
    parser.add_argument("--version", action="store_true")
    parser.add_argument("--no-speech", action="store_true")
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)

    if args.version:
        print(f"steadytype-client {__version__}")
        return 0

    paths = AppPaths(args.data_dir) if args.data_dir else default_paths()
    if args.self_check:
        from steadytype_client.signin import SignInPresenter

        store = Store(paths.database)
        course_path = bundled_content()
        if course_path is None:
            print("self-check failed: no course files")
            return 2
        course = load_course(course_path)
        SignInPresenter(store)
        print(f"self-check ok: {len(course.lessons)} lessons, {len(store.attempts(0))} attempts")
        return 0

    import wx

    from steadytype_client.main_controller import AppController
    from steadytype_client.signin import SignInPresenter
    from steadytype_client.ui.main import MainFrame
    from steadytype_client.ui.signin import SignInDialog

    app = wx.App(False)
    store = Store(paths.database)

    if args.no_speech:
        speech = FakeSpeech()
    else:
        try:
            speech = create_speech()
        except SpeechUnavailable as error:
            wx.MessageBox(str(error), "SteadyType", wx.OK | wx.ICON_WARNING)
            speech = FakeSpeech()

    player = create_player(paths.sounds)
    course_path = bundled_content()
    if course_path is None:
        wx.MessageBox("The lesson files were not found.", "SteadyType",
                      wx.OK | wx.ICON_ERROR)
        return 1
    course = load_course(course_path)

    dialog = SignInDialog(None, SignInPresenter(store), speak=speech.speak)
    if dialog.ShowModal() != wx.ID_OK:
        return 0
    account = dialog.account

    controller = AppController(store, account, paths, speech, player, course)
    frame = MainFrame(controller)
    frame.Show()
    app.MainLoop()
    return 0
