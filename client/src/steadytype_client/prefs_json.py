"""Preferences to and from JSON, keeping the enum values."""

from __future__ import annotations

import dataclasses

from steadytype_engine.preferences import (
    Echo,
    Feedback,
    Pitch,
    Preferences,
    TypingExperience,
    Verbosity,
)

ENUMS = {
    "feedback": Feedback, "verbosity": Verbosity, "typing_experience": TypingExperience,
    "echo": Echo, "echo_pitch": Pitch,
}


def to_dict(prefs: Preferences) -> dict:
    body = dataclasses.asdict(prefs)
    for name, enum_type in ENUMS.items():
        value = body.get(name)
        if isinstance(value, enum_type):
            body[name] = value.value
    return body


def from_dict(data: dict) -> Preferences:
    kwargs = {}
    for field in dataclasses.fields(Preferences):
        if field.name not in data:
            continue
        value = data[field.name]
        enum_type = ENUMS.get(field.name)
        kwargs[field.name] = enum_type(value) if enum_type else value
    return Preferences(**kwargs)
