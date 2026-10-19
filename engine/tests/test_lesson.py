from pathlib import Path

import pytest

from steadytype_engine.lesson import Course, EndKey, Lesson, LessonError, TaskKind

VALID = {
    "schema": 1,
    "id": 14,
    "unit": 2,
    "ordinal": 14,
    "title": "New letters: U I O P",
    "teaches": ["u", "i", "o", "p"],
    "kind": "keyboarding",
    "end_key": "space",
    "repeat": 4,
    "intro": "These four letters are typed with the right hand.",
    "tasks": [{"text": "u", "help": "U is above J."}, {"text": "juju"}],
}


def test_minimal_lesson_loads():
    lesson = Lesson.from_dict(VALID)
    assert lesson.id == 14
    assert lesson.end_key is EndKey.SPACE
    assert lesson.tasks[1].kind is TaskKind.TEXT
    assert lesson.tasks[1].help is None


@pytest.mark.parametrize(
    ("change", "message"),
    [({"repeat": 3}, "repeat"), ({"kind": "quiz"}, "kind"),
     ({"title": ""}, "title"), ({"tasks": []}, "tasks")],
)
def test_bad_lesson_names_the_field(change, message):
    data = {**VALID, **change}
    with pytest.raises(LessonError, match=message):
        Lesson.from_dict(data)


def test_duplicate_ids_are_rejected():
    with pytest.raises(LessonError, match="duplicate"):
        Course.from_dict({"schema": 1, "version": "1", "lessons": [VALID, VALID]})


def test_course_orders_lessons_by_ordinal():
    second = {**VALID, "id": 2, "ordinal": 2, "title": "Two"}
    first = {**VALID, "id": 1, "ordinal": 1, "title": "One"}
    course = Course.from_dict({"schema": 1, "version": "1", "lessons": [second, first]})
    assert [lesson.id for lesson in course.lessons] == [1, 2]
