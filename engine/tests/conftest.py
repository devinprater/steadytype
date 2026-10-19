import pytest

from steadytype_engine.scoring import AttemptRecord, KeyStat


def _record(index: int, lesson_id: int, wpm: float, kind: str = "practice",
            stats: tuple[KeyStat, ...] = (), day: str = "2026-10-19") -> AttemptRecord:
    return AttemptRecord(
        id=f"00000000-0000-0000-0000-{index:012d}", lesson_id=lesson_id, kind=kind,
        started_at=f"{day}T14:0{index % 10}:00+00:00",
        ended_at=f"{day}T14:0{index % 10}:59+00:00",
        active_seconds=60, characters=200, keypresses=210, errors=10,
        wpm=wpm, accuracy=95.0, real_accuracy=92.0, stars=4,
        key_stats=stats, device_id="test", client_version="0.1.0",
    )


@pytest.fixture
def attempts():
    speeds = [45, 40, 35, 30, 25, 20, 20, 25]
    lessons = [1, 1, 2, 2, 3, 3, 3, 3]
    stats = (KeyStat("p", 20, 5), KeyStat("q", 18, 4), KeyStat("r", 12, 1))
    records = [
        _record(index, lesson, speed, stats=stats)
        for index, (lesson, speed) in enumerate(zip(lessons, speeds))
    ]
    records.append(_record(99, 3, 90.0, kind="certification"))
    return records
