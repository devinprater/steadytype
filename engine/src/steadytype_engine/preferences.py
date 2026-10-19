"""Per-student settings. Values come from the client and sync through the server."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Feedback(Enum):
    TONE = "tone"
    WORD = "word"
    BOTH = "both"


class Verbosity(Enum):
    BRIEF = "brief"
    STANDARD = "standard"
    DETAILED = "detailed"


class TypingExperience(Enum):
    LITTLE = "little"
    SOME = "some"
    A_LOT = "a_lot"


class Echo(Enum):
    OFF = "off"
    WORDS = "words"
    EVERY_KEY = "every_key"


class Pitch(Enum):
    HIGH = "high"
    LOW = "low"


@dataclass(frozen=True)
class Preferences:
    feedback: Feedback = Feedback.BOTH
    verbosity: Verbosity = Verbosity.STANDARD
    typing_experience: TypingExperience = TypingExperience.SOME
    double_press_ms: int = 500
    echo: Echo = Echo.WORDS
    echo_pitch: Pitch = Pitch.HIGH
    one_handed: bool = False
    laptop_keyboard: bool = False
    tones: bool = True
    rate: float = 0.5
    pitch: float = 0.5
    volume: float = 1.0
    voice: str | None = None

    def __post_init__(self) -> None:
        if not 300 <= self.double_press_ms <= 900:
            raise ValueError("double_press_ms must be between 300 and 900")
