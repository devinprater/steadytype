from pathlib import Path

from steadytype_engine.lesson import EndKey, TaskKind
from steadytype_engine.loader import load_course

ROOT = Path(__file__).resolve().parents[2]
COURSE = load_course(ROOT / "content" / "course.yaml")


def test_course_has_five_seed_lessons():
    assert [lesson.id for lesson in COURSE.lessons] == [1, 2, 3, 4, 5]


def test_no_task_uses_an_untaught_character():
    taught: set[str] = {" "}
    for lesson in COURSE.lessons:
        taught.update(lesson.teaches)
        for task in lesson.tasks:
            if task.kind is not TaskKind.TEXT:
                continue
            unknown = set(task.text) - taught
            assert not unknown, f"lesson {lesson.id}: {sorted(unknown)} in {task.text!r}"


def test_a_task_teaching_enter_does_not_use_enter_as_its_end_key():
    for lesson in COURSE.lessons:
        for task in lesson.tasks:
            if task.kind is TaskKind.KEY and task.text == "enter":
                assert lesson.end_key is EndKey.NONE, f"lesson {lesson.id}"


def test_every_lesson_declares_what_it_teaches():
    for lesson in COURSE.lessons:
        assert lesson.teaches, f"lesson {lesson.id}"
