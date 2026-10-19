from pathlib import Path

from steadytype_engine.lesson import EndKey, TaskKind
from steadytype_engine.loader import load_course

ROOT = Path(__file__).resolve().parents[2]
COURSE = load_course(ROOT / "content" / "course.yaml")


def test_course_has_seventy_two_lessons():
    assert [lesson.id for lesson in COURSE.lessons] == list(range(1, 73))


def test_every_lesson_has_practice_tasks():
    for lesson in COURSE.lessons:
        assert len(lesson.tasks) >= 3, f"lesson {lesson.id} has {len(lesson.tasks)} tasks"


def test_no_task_uses_an_untaught_character():
    taught: set[str] = {" "}
    for lesson in COURSE.lessons:
        taught.update(lesson.teaches)
        for task in lesson.tasks:
            if task.kind is not TaskKind.TEXT:
                continue
            unknown = set(task.text) - taught
            assert not unknown, f"lesson {lesson.id}: {sorted(unknown)} in {task.text!r}"


def test_a_lesson_teaching_enter_does_not_end_tasks_with_enter():
    for lesson in COURSE.lessons:
        if "enter" not in lesson.teaches:
            continue
        assert lesson.end_key is not EndKey.ENTER, (
            f"lesson {lesson.id}: teaches enter but uses enter as its end key")


def test_every_lesson_declares_what_it_teaches():
    for lesson in COURSE.lessons:
        assert lesson.teaches, f"lesson {lesson.id}"
