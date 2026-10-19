"""X11 capture with XRecord. Wayland blocks this; there the window keeps focus."""

from __future__ import annotations

import threading
from collections.abc import Callable

from steadytype_engine.keys import Key, KeyEvent, Modifier, Side

KEYSYMS = {
    "Return": Key.ENTER, "KP_Enter": Key.NUMPAD_ENTER, "Tab": Key.TAB,
    "space": Key.SPACE, "BackSpace": Key.BACKSPACE, "Delete": Key.DELETE,
    "Escape": Key.ESCAPE, "Insert": Key.INSERT, "Home": Key.HOME, "End": Key.END,
    "Page_Up": Key.PAGE_UP, "Page_Down": Key.PAGE_DOWN,
    "Up": Key.UP, "Down": Key.DOWN, "Left": Key.LEFT, "Right": Key.RIGHT,
    "comma": Key.COMMA, "period": Key.PERIOD, "slash": Key.SLASH,
    "semicolon": Key.SEMICOLON, "apostrophe": Key.APOSTROPHE, "minus": Key.MINUS,
    "equal": Key.EQUALS, "bracketleft": Key.LEFT_BRACKET,
    "bracketright": Key.RIGHT_BRACKET, "backslash": Key.BACKSLASH, "grave": Key.GRAVE,
}
KEYSYMS.update({f"F{i}": getattr(Key, f"F{i}") for i in range(1, 13)})
KEYSYMS.update({f"KP_{d}": getattr(Key, f"DIGIT_{d}") for d in range(10)})

MODIFIERS = {
    "Shift_L": (Key.LEFT_SHIFT, Modifier.SHIFT, Side.LEFT),
    "Shift_R": (Key.RIGHT_SHIFT, Modifier.SHIFT, Side.RIGHT),
    "Control_L": (Key.LEFT_CONTROL, Modifier.CONTROL, Side.LEFT),
    "Control_R": (Key.RIGHT_CONTROL, Modifier.CONTROL, Side.RIGHT),
    "Alt_L": (Key.LEFT_ALT, Modifier.ALT, Side.LEFT),
    "Alt_R": (Key.RIGHT_ALT, Modifier.ALT, Side.RIGHT),
    "Super_L": (Key.LEFT_META, Modifier.META, Side.LEFT),
    "Super_R": (Key.RIGHT_META, Modifier.META, Side.RIGHT),
}


def key_for(name: str) -> Key | None:
    if name in KEYSYMS:
        return KEYSYMS[name]
    if len(name) == 1:
        if name.isalpha():
            return getattr(Key, name.upper())
        if name.isdigit():
            return getattr(Key, f"DIGIT_{name}")
    return None


class LinuxCapture:
    def __init__(self, callback: Callable[[KeyEvent], None] | None = None) -> None:
        self.callback = callback
        self._display = None
        self._thread = None
        self._context = None

    def start(self, callback: Callable[[KeyEvent], None] | None = None) -> bool:
        if callback is not None:
            self.callback = callback
        try:
            from Xlib import XK, X, display
            from Xlib.ext import record
            from Xlib.protocol import rq
        except ImportError:
            return False
        try:
            self._display = display.Display()
        except Exception:  # noqa: BLE001 - no X server, so no capture
            return False
        self._x, self._xk, self._record, self._rq = X, XK, record, rq
        context = self._display.record_create_context(0, [record.AllClients], [{
            "core_requests": (0, 0), "core_replies": (0, 0),
            "ext_requests": (0, 0, 0, 0), "ext_replies": (0, 0, 0, 0),
            "delivered_events": (0, 0), "device_events": (X.KeyPress, X.KeyRelease),
            "errors": (0, 0), "client_started": False, "client_died": False}])
        self._context = context
        self._thread = threading.Thread(target=self._run, args=(context,), daemon=True)
        self._thread.start()
        return True

    def _run(self, context) -> None:
        self._display.record_enable_context(context, self._on_reply)

    def _on_reply(self, reply) -> None:
        data = reply.data
        X, XK, rq = self._x, self._xk, self._rq
        while data:
            event, data = rq.EventField(None).parse_binary_value(
                data, self._display.display, None, None)
            if event.type not in (X.KeyPress, X.KeyRelease):
                continue
            keysym = self._display.keycode_to_keysym(event.detail, 0)
            name = XK.keysym_to_string(keysym)
            if not name or self.callback is None:
                continue
            pressed = event.type == X.KeyPress
            if name in MODIFIERS:
                key, modifier, side = MODIFIERS[name]
                self.callback(KeyEvent(kind="down" if pressed else "up", key=key,
                                       text="", modifiers=frozenset({modifier}),
                                       side=side))
                continue
            key = key_for(name)
            if key is None:
                continue
            text = name if (len(name) == 1 and not name.isalpha()) else ""
            if len(name) == 1:
                text = name
            self.callback(KeyEvent(kind="down" if pressed else "up", key=key,
                                   text=text, modifiers=frozenset()))

    def stop(self) -> None:
        try:
            if self._display is not None and self._context is not None:
                self._display.record_disable_context(self._context)
                self._display.flush()
        finally:
            self._context = None
