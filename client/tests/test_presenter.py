from steadytype_client.presenter import LessonPresenter
from steadytype_client.sounds import NullPlayer
from steadytype_client.speech import FakeSpeech
from steadytype_engine.keys import Key, KeyEvent, Side
from steadytype_engine.lesson import Lesson
from steadytype_engine.preferences import Preferences
from steadytype_engine.scoring import Goals

LESSON = Lesson.from_dict({
    "schema": 1, "id": 1, "unit": 1, "ordinal": 1, "title": "T",
    "teaches": ["a"], "kind": "keyboarding", "end_key": "space",
    "repeat": 2, "intro": "Type a.", "tasks": [{"text": "a"}],
})


def _key(char):
    key = Key.SPACE if char == " " else Key(char)
    return KeyEvent(kind="down", key=key, text=char, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0, timestamp=0.0)


def make(prefs=None, save=None):
    speech, player = FakeSpeech(), NullPlayer()
    presenter = LessonPresenter(LESSON, prefs or Preferences(), Goals(), speech,
                                player, save=save or (lambda record: None))
    return presenter, speech, player


def test_speech_goes_to_the_engine_and_tones_to_the_player():
    presenter, speech, player = make()
    presenter.start()
    assert speech.spoken[0][0] == "Type a."
    presenter.handle(_key("a"))
    assert "correct" in player.played


def test_tones_off_means_no_sound():
    presenter, _speech, player = make(prefs=Preferences(tones=False))
    presenter.start()
    presenter.handle(_key("a"))
    assert player.played == []


def test_finishing_saves_one_attempt_and_speaks_the_result():
    saved = []
    presenter, _speech, _player = make(save=saved.append)
    presenter.start()
    for _ in range(2):
        presenter.handle(_key("a"))
        presenter.handle(_key(" "))
    assert len(saved) == 1
    assert any("accuracy" in text for text, _ in _speech.spoken)
