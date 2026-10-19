"""Lesson and course models, validated on load."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any


class LessonError(Exception):
    pass


class TaskKind(Enum):
    TEXT = "text"
    KEY = "key"
    COMBO = "combo"
    GAME = "game"


class EndKey(Enum):
    SPACE = "space"
    ENTER = "enter"
    NONE = "none"


class LessonKind(Enum):
    KEYBOARDING = "keyboarding"
    GAME = "game"
    DICTATION = "dictation"
    RACE = "race"


@dataclass(frozen=True)
class Task:
    text: str
    help: str | None = None
    kind: TaskKind = TaskKind.TEXT

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Task:
        if not isinstance(data, Mapping):
            raise LessonError("tasks: each task must be a mapping")
        text = data.get("text")
        if not isinstance(text, str) or not text:
            raise LessonError("tasks: text must be a non-empty string")
        help_text = data.get("help")
        if help_text is not None and not isinstance(help_text, str):
            raise LessonError("tasks: help must be a string")
        raw_kind = data.get("kind", "text")
        try:
            kind = TaskKind(raw_kind)
        except ValueError:
            raise LessonError(f"tasks: kind {raw_kind!r} is not a task kind") from None
        return cls(text=text, help=help_text, kind=kind)


@dataclass(frozen=True)
class Lesson:
    id: int
    unit: int
    ordinal: int
    title: str
    teaches: tuple[str, ...]
    kind: LessonKind
    end_key: EndKey
    repeat: int
    intro: str
    tasks: tuple[Task, ...]

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Lesson:
        if not isinstance(data, Mapping):
            raise LessonError("lesson: expected a mapping")

        def need_text(field: str) -> str:
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                raise LessonError(f"{field}: must be a non-empty string")
            return value.strip()

        for field in ("id", "unit", "ordinal"):
            value = data.get(field)
            if not isinstance(value, int) or isinstance(value, bool):
                raise LessonError(f"{field}: must be an integer")

        raw_kind = data.get("kind")
        try:
            kind = LessonKind(raw_kind)
        except (ValueError, TypeError):
            raise LessonError(f"kind: {raw_kind!r} is not a lesson kind") from None

        raw_end = data.get("end_key")
        try:
            end_key = EndKey(raw_end)
        except (ValueError, TypeError):
            raise LessonError(f"end_key: {raw_end!r} is not an end key") from None

        repeat = data.get("repeat")
        if repeat not in (2, 4) or isinstance(repeat, bool):
            raise LessonError("repeat: must be 2 or 4")

        teaches = data.get("teaches", [])
        if not isinstance(teaches, Sequence) or isinstance(teaches, str):
            raise LessonError("teaches: must be a list of characters")
        teaches_tuple = tuple(teaches)
        if kind is not LessonKind.GAME and not teaches_tuple:
            raise LessonError("teaches: must name at least one key")

        raw_tasks = data.get("tasks")
        if not isinstance(raw_tasks, Sequence) or isinstance(raw_tasks, str) or not raw_tasks:
            raise LessonError("tasks: must be a non-empty list")

        return cls(
            id=data["id"],
            unit=data["unit"],
            ordinal=data["ordinal"],
            title=need_text("title"),
            teaches=teaches_tuple,
            kind=kind,
            end_key=end_key,
            repeat=repeat,
            intro=need_text("intro"),
            tasks=tuple(Task.from_dict(task) for task in raw_tasks),
        )


@dataclass(frozen=True)
class Course:
    schema: int
    version: str
    lessons: tuple[Lesson, ...]

    @classmethod
    def from_lessons(cls, schema: int, version: str, lessons: Sequence[Lesson]) -> Course:
        if schema != 1:
            raise LessonError(f"schema: {schema!r} is not supported")
        if not isinstance(version, str) or not version:
            raise LessonError("version: must be a non-empty string")
        seen: set[int] = set()
        for lesson in lessons:
            if lesson.id in seen:
                raise LessonError(f"duplicate lesson id {lesson.id}")
            seen.add(lesson.id)
        return cls(schema=schema, version=version,
                   lessons=tuple(sorted(lessons, key=lambda lesson: lesson.ordinal)))

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Course:
        if not isinstance(data, Mapping):
            raise LessonError("course: expected a mapping")
        raw_lessons = data.get("lessons")
        if not isinstance(raw_lessons, Sequence) or isinstance(raw_lessons, str):
            raise LessonError("lessons: must be a list")
        return cls.from_lessons(
            schema=data.get("schema"),
            version=data.get("version"),
            lessons=[Lesson.from_dict(item) for item in raw_lessons],
        )
