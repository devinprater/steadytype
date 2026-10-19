"""Spoken names and locations for keys the course teaches."""

from __future__ import annotations

SPOKEN = {
    " ": "space", "\n": "enter", ".": "period", ",": "comma", "/": "slash",
    ";": "semicolon", "'": "apostrophe", "[": "left bracket", "]": "right bracket",
    "\\": "backslash", "`": "grave", "-": "minus", "=": "equals",
}

KEY_HINTS = {
    "a": "on the home row, left hand, little finger",
    "s": "on the home row, left hand, ring finger",
    "d": "on the home row, left hand, middle finger",
    "f": "on the home row, left hand, index finger, next to the bump",
    "g": "on the home row, left hand, index finger",
    "h": "on the home row, right hand, index finger",
    "j": "on the home row, right hand, index finger, next to the bump",
    "k": "on the home row, right hand, middle finger",
    "l": "on the home row, right hand, ring finger",
    ";": "on the home row, right hand, little finger",
    "q": "on the top row, left hand, little finger",
    "w": "on the top row, left hand, ring finger",
    "e": "on the top row, left hand, middle finger",
    "r": "on the top row, left hand, index finger",
    "t": "on the top row, left hand, index finger",
    "y": "on the top row, right hand, index finger",
    "u": "on the top row, right hand, index finger",
    "i": "on the top row, right hand, middle finger",
    "o": "on the top row, right hand, ring finger",
    "p": "on the top row, right hand, little finger",
    "z": "on the bottom row, left hand, little finger",
    "x": "on the bottom row, left hand, ring finger",
    "c": "on the bottom row, left hand, middle finger",
    "v": "on the bottom row, left hand, index finger",
    "b": "on the bottom row, left hand, index finger",
    "n": "on the bottom row, right hand, index finger",
    "m": "on the bottom row, right hand, index finger",
    ",": "on the bottom row, right hand, middle finger",
    ".": "on the bottom row, right hand, ring finger",
    "/": "on the bottom row, right hand, little finger",
    " ": "the long key at the bottom, press it with a thumb",
    "enter": "at the right end of the home row, or on the numpad",
    "tab": "at the left end of the top letter row",
    "escape": "at the top left corner of the keyboard",
    "backspace": "at the top right of the main section",
    "delete": "in the six pack above the arrows",
    "up": "in the arrow cluster, below the six pack",
    "down": "in the arrow cluster, below the six pack",
    "left": "in the arrow cluster, below the six pack",
    "right": "in the arrow cluster, below the six pack",
}

for _digit, _finger in zip("1234567890",
                           ["left little finger", "left ring finger",
                            "left middle finger", "left index finger",
                            "left index finger", "right index finger",
                            "right index finger", "right middle finger",
                            "right ring finger", "right little finger"]):
    KEY_HINTS[_digit] = f"on the number row, {_finger}"

for _n in range(1, 13):
    KEY_HINTS[f"f{_n}"] = "in the function row along the top"


def spoken(value: str) -> str:
    """A key name as a person would say it."""
    return SPOKEN.get(value, value)
