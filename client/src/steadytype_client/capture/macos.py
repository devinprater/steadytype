"""Quartz event tap. Needs Accessibility permission once, in System Settings."""

from __future__ import annotations

import threading
from collections.abc import Callable

from steadytype_engine.keys import Key, KeyEvent, Modifier, Side

VIRTUAL = {
    0: Key.A, 1: Key.S, 2: Key.D, 3: Key.F, 4: Key.H, 5: Key.G, 6: Key.Z, 7: Key.X,
    8: Key.C, 9: Key.V, 11: Key.B, 12: Key.Q, 13: Key.W, 14: Key.E, 15: Key.R,
    16: Key.Y, 17: Key.T, 32: Key.U, 34: Key.I, 31: Key.O, 35: Key.P, 37: Key.L,
    38: Key.J, 40: Key.K, 45: Key.N, 46: Key.M, 18: Key.DIGIT_1, 19: Key.DIGIT_2,
    20: Key.DIGIT_3, 21: Key.DIGIT_4, 23: Key.DIGIT_5, 22: Key.DIGIT_6,
    26: Key.DIGIT_7, 28: Key.DIGIT_8, 25: Key.DIGIT_9, 29: Key.DIGIT_0,
    36: Key.ENTER, 48: Key.TAB, 49: Key.SPACE, 51: Key.BACKSPACE, 53: Key.ESCAPE,
    117: Key.DELETE, 115: Key.HOME, 119: Key.END, 116: Key.PAGE_UP,
    121: Key.PAGE_DOWN, 123: Key.LEFT, 124: Key.RIGHT, 125: Key.DOWN, 126: Key.UP,
    122: Key.F1, 120: Key.F2, 99: Key.F3, 118: Key.F4, 96: Key.F5, 97: Key.F6,
    98: Key.F7, 100: Key.F8, 101: Key.F9, 109: Key.F10, 103: Key.F11, 111: Key.F12,
    27: Key.MINUS, 24: Key.EQUALS, 33: Key.LEFT_BRACKET, 30: Key.RIGHT_BRACKET,
    41: Key.SEMICOLON, 39: Key.APOSTROPHE, 43: Key.COMMA, 47: Key.PERIOD,
    44: Key.SLASH, 42: Key.BACKSLASH, 50: Key.GRAVE,
}

MODIFIERS = {
    56: (Key.LEFT_SHIFT, Modifier.SHIFT, Side.LEFT),
    60: (Key.RIGHT_SHIFT, Modifier.SHIFT, Side.RIGHT),
    59: (Key.LEFT_CONTROL, Modifier.CONTROL, Side.LEFT),
    62: (Key.RIGHT_CONTROL, Modifier.CONTROL, Side.RIGHT),
    58: (Key.LEFT_ALT, Modifier.ALT, Side.LEFT),
    61: (Key.RIGHT_ALT, Modifier.ALT, Side.RIGHT),
    55: (Key.LEFT_META, Modifier.META, Side.LEFT),
    54: (Key.RIGHT_META, Modifier.META, Side.RIGHT),
}

FLAG_SHIFT = 1 << 17
FLAG_CONTROL = 1 << 18
FLAG_ALT = 1 << 19
FLAG_META = 1 << 20


PUNCTUATION = {",": Key.COMMA, ".": Key.PERIOD, "/": Key.SLASH, ";": Key.SEMICOLON,
               "'": Key.APOSTROPHE, "[": Key.LEFT_BRACKET, "]": Key.RIGHT_BRACKET,
               "\\": Key.BACKSLASH, "`": Key.GRAVE, "-": Key.MINUS, "=": Key.EQUALS}


def _key_for_text(text: str) -> Key:
    return PUNCTUATION.get(text, Key.UNKNOWN)


def key_for(virtual_key: int) -> Key | None:
    return VIRTUAL.get(virtual_key)


def modifiers_for(flags: int) -> frozenset[Modifier]:
    found = set()
    if flags & FLAG_SHIFT:
        found.add(Modifier.SHIFT)
    if flags & FLAG_CONTROL:
        found.add(Modifier.CONTROL)
    if flags & FLAG_ALT:
        found.add(Modifier.ALT)
    if flags & FLAG_META:
        found.add(Modifier.META)
    return frozenset(found)


class MacCapture:
    def __init__(self, callback: Callable[[KeyEvent], None] | None = None) -> None:
        self.callback = callback
        self._tap = None
        self._run_loop = None
        self._thread = None
        self._stopping = False

    def start(self, callback: Callable[[KeyEvent], None] | None = None) -> bool:
        if callback is not None:
            self.callback = callback
        try:
            import Quartz
        except ImportError:
            return False
        self._q = Quartz
        check = getattr(Quartz, "AXIsProcessTrusted", None)
        if check is not None and not check():
            # Without permission the tap exists but macOS drops every event.
            prompt = getattr(Quartz, "AXIsProcessTrustedWithOptions", None)
            if prompt is not None:
                try:
                    prompt({Quartz.kAXTrustedCheckOptionPrompt: True})
                except Exception:  # noqa: BLE001, S110 - not fatal
                    pass
            return False
        mask = (Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown)
                | Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp)
                | Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged))
        tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap, Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault, mask, self._on_event, None)
        if not tap:
            return False
        self._tap = tap
        self._stopping = False
        self._thread = threading.Thread(target=self._run, args=(tap,), daemon=True)
        self._thread.start()
        return True

    def _run(self, tap) -> None:
        Quartz = self._q
        source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
        self._run_loop = Quartz.CFRunLoopGetCurrent()
        Quartz.CFRunLoopAddSource(self._run_loop, source,
                                  Quartz.kCFRunLoopCommonModes)
        Quartz.CGEventTapEnable(tap, True)
        Quartz.CFRunLoopRun()

    def _on_event(self, proxy, event_type, event, refcon):
        Quartz = self._q
        if self._stopping or self.callback is None:
            return event
        vk = Quartz.CGEventGetIntegerValueField(
            event, Quartz.kCGKeyboardEventKeycode)
        flags = Quartz.CGEventGetFlags(event)
        if event_type in (Quartz.kCGEventKeyDown,):
            key = key_for(int(vk))
            text = ""
            if key is None or len(str(key.value)) == 1:
                length, buffer = Quartz.CGEventKeyboardGetUnicodeString(
                    event, 4, None, None)
                text = buffer[:length] if length else ""
            if key is None and text:
                key = _key_for_text(text)
            if key is not None:
                self.callback(KeyEvent(kind="down", key=key, text=text,
                                       modifiers=modifiers_for(int(flags))))
        elif event_type == Quartz.kCGEventFlagsChanged:
            entry = MODIFIERS.get(int(vk))
            if entry is not None:
                key, modifier, side = entry
                pressed = bool(modifiers_for(int(flags)) & {modifier})
                self.callback(KeyEvent(kind="down" if pressed else "up",
                                       key=key, text="",
                                       modifiers=frozenset({modifier}), side=side))
        return event

    def stop(self) -> None:
        self._stopping = True
        if self._tap is not None:
            try:
                self._q.CGEventTapEnable(self._tap, False)
                if self._run_loop is not None:
                    self._q.CFRunLoopStop(self._run_loop)
            finally:
                self._tap = None
