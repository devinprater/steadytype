from steadytype_client.main_controller import is_panic
from steadytype_client.router import CommandRouter
from steadytype_engine.keys import Key, KeyEvent, Modifier, Side


def press(key, clock):
    return KeyEvent(kind="down", key=key, text=None, modifiers=frozenset(),
                    side=Side.NONE, is_repeat=False, scan_code=0,
                    timestamp=clock[0])


def test_the_panic_chord_is_control_alt_shift_x():
    clock = [0.0]

    def chord(mods):
        event = press(Key.X, clock)
        return type(event)(**{**event.__dict__, "modifiers": frozenset(mods)})

    assert is_panic(chord({Modifier.CONTROL, Modifier.ALT, Modifier.SHIFT}))
    assert not is_panic(chord({Modifier.CONTROL, Modifier.ALT}))
    assert not is_panic(chord({Modifier.CONTROL, Modifier.SHIFT}))


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
