"""Windows low-level keyboard capture, normalized for the engine."""

from __future__ import annotations

import ctypes
import threading
from collections.abc import Callable
from ctypes import wintypes

from steadytype_engine.keys import Key, KeyEvent, Modifier, Side

WH_KEYBOARD_LL = 13
WM_KEYDOWN, WM_SYSKEYDOWN, WM_KEYUP, WM_SYSKEYUP = 0x0100, 0x0104, 0x0101, 0x0105

LETTERS = {0x41 + i: chr(ord("a") + i) for i in range(26)}
DIGITS = {0x30 + i: str(i) for i in range(10)}
SHIFTED_DIGITS = ")!@#$%^&*("
PUNCTUATION = {
    0xBA: (";", ":"), 0xBB: ("=", "+"), 0xBC: (",", "<"), 0xBD: ("-", "_"),
    0xBE: (".", ">"), 0xBF: ("/", "?"), 0xC0: ("`", "~"), 0xDB: ("[", "{"),
    0xDC: ("\\", "|"), 0xDD: ("]", "}"), 0xDE: ("'", '"'),
}
NAMED = {
    0x20: Key.SPACE, 0x0D: Key.ENTER, 0x09: Key.TAB, 0x1B: Key.ESCAPE,
    0x08: Key.BACKSPACE, 0x2E: Key.DELETE, 0x2D: Key.INSERT, 0x24: Key.HOME,
    0x23: Key.END, 0x21: Key.PAGE_UP, 0x22: Key.PAGE_DOWN, 0x25: Key.LEFT,
    0x26: Key.UP, 0x27: Key.RIGHT, 0x28: Key.DOWN, 0x14: Key.CAPS_LOCK,
    0x90: Key.NUM_LOCK,
}
MODIFIER_KEYS = {
    0xA0: (Key.LEFT_SHIFT, Modifier.SHIFT, Side.LEFT),
    0xA1: (Key.RIGHT_SHIFT, Modifier.SHIFT, Side.RIGHT),
    0xA2: (Key.LEFT_CONTROL, Modifier.CONTROL, Side.LEFT),
    0xA3: (Key.RIGHT_CONTROL, Modifier.CONTROL, Side.RIGHT),
    0xA4: (Key.LEFT_ALT, Modifier.ALT, Side.LEFT),
    0xA5: (Key.RIGHT_ALT, Modifier.ALT, Side.RIGHT),
    0x5B: (Key.LEFT_META, Modifier.META, Side.LEFT),
    0x5C: (Key.RIGHT_META, Modifier.META, Side.RIGHT),
}
NUMPAD = {0x60 + i: Key(f"numpad_{i}") for i in range(10)}
NUMPAD.update({0x6A: Key.NUMPAD_MULTIPLY, 0x6B: Key.NUMPAD_ADD,
               0x6D: Key.NUMPAD_SUBTRACT, 0x6E: Key.NUMPAD_DECIMAL,
               0x6F: Key.NUMPAD_DIVIDE})


def is_key_down(wparam: int) -> bool:
    return wparam in (WM_KEYDOWN, WM_SYSKEYDOWN)


def map_key(vk: int, scan: int, extended: bool, shift: bool, control: bool,
            alt: bool) -> KeyEvent | None:
    modifiers = set()
    if shift:
        modifiers.add(Modifier.SHIFT)
    if control:
        modifiers.add(Modifier.CONTROL)
    if alt:
        modifiers.add(Modifier.ALT)
    frozen = frozenset(modifiers)
    side = Side.NONE
    text: str | None = None

    if vk in MODIFIER_KEYS:
        key, modifier, side = MODIFIER_KEYS[vk]
        frozen = frozenset({modifier})
    elif vk in LETTERS:
        key = Key(LETTERS[vk])
        text = LETTERS[vk].upper() if shift else LETTERS[vk]
    elif vk in DIGITS:
        key = Key(DIGITS[vk])
        text = SHIFTED_DIGITS[DIGITS[vk] == "0" and 0 or int(DIGITS[vk])] if shift else DIGITS[vk]
    elif vk in PUNCTUATION:
        plain, shifted = PUNCTUATION[vk]
        text = shifted if shift else plain
        key = _key_for_text(text)
    elif vk in NUMPAD:
        key = NUMPAD[vk]
        text = str(vk - 0x60) if 0x60 <= vk <= 0x69 else None
    elif 0x70 <= vk <= 0x7B:
        key = Key(f"f{vk - 0x6F}")
    elif vk == 0x0D and extended:
        key = Key.NUMPAD_ENTER
    elif vk in NAMED:
        key = NAMED[vk]
        text = " " if key is Key.SPACE else None
    else:
        return None

    return KeyEvent(kind="down", key=key, text=text, modifiers=frozen, side=side,
                    is_repeat=False, scan_code=scan, timestamp=0.0)


def _key_for_text(text: str) -> Key:
    names = {",": Key.COMMA, ".": Key.PERIOD, "/": Key.SLASH, ";": Key.SEMICOLON,
             "'": Key.APOSTROPHE, "[": Key.LEFT_BRACKET, "]": Key.RIGHT_BRACKET,
             "\\": Key.BACKSLASH, "`": Key.GRAVE, "-": Key.MINUS, "=": Key.EQUALS}
    return names.get(text, Key.UNKNOWN)


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wintypes.DWORD), ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
user32.SetWindowsHookExW.restype = wintypes.HHOOK
user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
user32.CallNextHookEx.restype = ctypes.c_ssize_t
user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
user32.GetAsyncKeyState.restype = ctypes.c_short


class WindowsCapture:
    def __init__(self, callback: Callable[[KeyEvent], None] | None = None) -> None:
        self._callback = callback
        self._thread: threading.Thread | None = None
        self._thread_id = 0
        self.active = False
        self._hook = None
        self.error = 0

    def start(self, callback: Callable[[KeyEvent], None] | None = None) -> bool:
        if callback is not None:
            self._callback = callback
        if self.active:
            return True
        started = threading.Event()
        self._thread = threading.Thread(target=self._run, args=(started,), daemon=True)
        self._thread.start()
        started.wait(2.0)
        return self.active

    def _run(self, started: threading.Event) -> None:
        pressed: set[int] = set()

        def handler(code, wparam, lparam):
            if code < 0:
                return user32.CallNextHookEx(None, code, wparam, lparam)
            info = ctypes.cast(lparam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            if not is_key_down(wparam):
                pressed.discard(info.vkCode)
                return 1
            shift = bool(user32.GetAsyncKeyState(0x10) & 0x8000)
            control = bool(user32.GetAsyncKeyState(0x11) & 0x8000)
            alt = bool(user32.GetAsyncKeyState(0x12) & 0x8000)
            event = map_key(info.vkCode, info.scanCode, bool(info.flags & 0x01),
                            shift, control, alt)
            if event is not None and self._callback is not None:
                if info.vkCode in pressed:
                    from dataclasses import replace
                    event = replace(event, is_repeat=True)
                else:
                    pressed.add(info.vkCode)
                self._callback(event)
            return 1

        self._proc = HOOKPROC(handler)
        self._thread_id = kernel32.GetCurrentThreadId()
        self._hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._proc,
                                              kernel32.GetModuleHandleW(None), 0)
        self.error = ctypes.get_last_error() if not self._hook else 0
        self.active = bool(self._hook)
        started.set()
        if not self.active:
            return
        message = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(message))
            user32.DispatchMessageW(ctypes.byref(message))
        user32.UnhookWindowsHookEx(self._hook)
        self.active = False

    def stop(self) -> None:
        if not self.active:
            return
        user32.PostThreadMessageW(self._thread_id, 0x0012, 0, 0)
        self.active = False
