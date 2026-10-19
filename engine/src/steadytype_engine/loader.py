"""Read lesson and course files from disk."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .lesson import Course, Lesson, LessonError


def _read_mapping(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise LessonError(f"{path}: {error.strerror}") from error
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise LessonError(f"{path}: {error}") from error
    if not isinstance(data, dict):
        raise LessonError(f"{path}: root must be a mapping")
    return data


def load_lesson(path: Path) -> Lesson:
    return Lesson.from_dict(_read_mapping(Path(path)))


def load_course(path: Path) -> Course:
    path = Path(path)
    data = _read_mapping(path)
    entries = data.get("lessons")
    if not isinstance(entries, list) or not entries:
        raise LessonError("lessons: must be a non-empty list")

    lessons: list[Lesson] = []
    for entry in entries:
        if isinstance(entry, str):
            lessons.append(load_lesson(path.parent / entry))
        elif isinstance(entry, dict):
            lessons.append(Lesson.from_dict(entry))
        else:
            raise LessonError("lessons: each entry must be a path or a lesson mapping")

    return Course.from_lessons(
        schema=data.get("schema"), version=data.get("version"), lessons=lessons)
