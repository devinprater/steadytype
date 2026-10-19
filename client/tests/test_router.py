from steadytype_client.router import CommandRouter
from steadytype_engine.keys import Key, KeyEvent, Side


def press(key, clock):
    return KeyEvent(kind="down", key=key, text=None, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0,
                    timestamp=clock[0])


def test_two_f2_presses_mean_next():
    clock = [0.0]
    router = CommandRouter(now=lambda: clock[0])
    assert router.feed(press(Key.F2, clock)) is None
    clock[0] = 0.2
    assert router.feed(press(Key.F2, clock)) == "next"


def test_three_escape_presses_mean_quit():
    clock = [0.0]
    router = CommandRouter(now=lambda: clock[0])
    router.feed(press(Key.ESCAPE, clock))
    router.feed(press(Key.ESCAPE, clock))
    clock[0] = 0.3
    assert router.feed(press(Key.ESCAPE, clock)) == "quit"


def test_commands_can_be_disabled_for_the_function_key_lesson():
    clock = [0.0]
    router = CommandRouter(now=lambda: clock[0], enabled=False)
    router.feed(press(Key.F2, clock))
    clock[0] = 0.2
    assert router.feed(press(Key.F2, clock)) is None
