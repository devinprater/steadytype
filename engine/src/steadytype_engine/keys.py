"""Normalized key events shared by every platform layer."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum


class Side(Enum):
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


class Modifier(Enum):
    SHIFT = "shift"
    CONTROL = "control"
    ALT = "alt"
    META = "meta"
    CAPS_LOCK = "caps_lock"
    NUM_LOCK = "num_lock"


class Key(str, Enum):
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    E = "e"
    F = "f"
    G = "g"
    H = "h"
    I = "i"
    J = "j"
    K = "k"
    L = "l"
    M = "m"
    N = "n"
    O = "o"
    P = "p"
    Q = "q"
    R = "r"
    S = "s"
    T = "t"
    U = "u"
    V = "v"
    W = "w"
    X = "x"
    Y = "y"
    Z = "z"
    DIGIT_0 = "0"
    DIGIT_1 = "1"
    DIGIT_2 = "2"
    DIGIT_3 = "3"
    DIGIT_4 = "4"
    DIGIT_5 = "5"
    DIGIT_6 = "6"
    DIGIT_7 = "7"
    DIGIT_8 = "8"
    DIGIT_9 = "9"
    SPACE = "space"
    ENTER = "enter"
    NUMPAD_ENTER = "numpad_enter"
    TAB = "tab"
    ESCAPE = "escape"
    BACKSPACE = "backspace"
    DELETE = "delete"
    INSERT = "insert"
    HOME = "home"
    END = "end"
    PAGE_UP = "page_up"
    PAGE_DOWN = "page_down"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    F1 = "f1"
    F2 = "f2"
    F3 = "f3"
    F4 = "f4"
    F5 = "f5"
    F6 = "f6"
    F7 = "f7"
    F8 = "f8"
    F9 = "f9"
    F10 = "f10"
    F11 = "f11"
    F12 = "f12"
    LEFT_SHIFT = "left_shift"
    RIGHT_SHIFT = "right_shift"
    LEFT_CONTROL = "left_control"
    RIGHT_CONTROL = "right_control"
    LEFT_ALT = "left_alt"
    RIGHT_ALT = "right_alt"
    LEFT_META = "left_meta"
    RIGHT_META = "right_meta"
    CAPS_LOCK = "caps_lock"
    NUM_LOCK = "num_lock"
    COMMA = "comma"
    PERIOD = "period"
    SLASH = "slash"
    SEMICOLON = "semicolon"
    APOSTROPHE = "apostrophe"
    LEFT_BRACKET = "left_bracket"
    RIGHT_BRACKET = "right_bracket"
    BACKSLASH = "backslash"
    GRAVE = "grave"
    MINUS = "minus"
    EQUALS = "equals"
    NUMPAD_ADD = "numpad_add"
    NUMPAD_SUBTRACT = "numpad_subtract"
    NUMPAD_MULTIPLY = "numpad_multiply"
    NUMPAD_DIVIDE = "numpad_divide"
    NUMPAD_DECIMAL = "numpad_decimal"
    UNKNOWN = "unknown"
    NUMPAD_0 = "numpad_0"
    NUMPAD_1 = "numpad_1"
    NUMPAD_2 = "numpad_2"
    NUMPAD_3 = "numpad_3"
    NUMPAD_4 = "numpad_4"
    NUMPAD_5 = "numpad_5"
    NUMPAD_6 = "numpad_6"
    NUMPAD_7 = "numpad_7"
    NUMPAD_8 = "numpad_8"
    NUMPAD_9 = "numpad_9"


@dataclass(frozen=True)
class KeyEvent:
    """One physical key action, already normalized by the platform layer."""

    kind: str
    key: Key
    text: str | None
    modifiers: frozenset[Modifier]
    side: Side
    is_repeat: bool
    scan_code: int
    timestamp: float

    def with_repeat(self) -> "KeyEvent":
        return replace(self, is_repeat=True)
