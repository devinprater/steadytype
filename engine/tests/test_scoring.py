import pytest

from steadytype_engine.scoring import Goals, Metrics, accuracy_star, speed_star, stars


def test_wpm_uses_five_characters_per_word():
    metrics = Metrics(characters=412, keypresses=430, errors=18,
                      first_try_correct=376, active_seconds=96)
    assert metrics.wpm == pytest.approx(51.5, abs=0.05)


def test_accuracy_counts_corrected_mistakes():
    metrics = Metrics(characters=412, keypresses=430, errors=18,
                      first_try_correct=376, active_seconds=96)
    assert metrics.accuracy == pytest.approx(95.81, abs=0.01)


def test_real_accuracy_counts_first_try_characters():
    metrics = Metrics(characters=412, keypresses=430, errors=18,
                      first_try_correct=376, active_seconds=96)
    assert metrics.real_accuracy == pytest.approx(91.26, abs=0.01)


@pytest.mark.parametrize(
    ("accuracy", "expected"), [(98, 5), (97.9, 4), (95, 4), (90, 3), (80, 2), (79.9, 1)],
)
def test_accuracy_star_boundaries(accuracy, expected):
    assert accuracy_star(accuracy) == expected


@pytest.mark.parametrize(
    ("wpm", "expected"), [(20, 5), (18, 4), (15, 3), (10, 2), (9.9, 1)],
)
def test_speed_star_boundaries(wpm, expected):
    assert speed_star(wpm, 20) == expected


def test_stars_take_the_lower_of_accuracy_and_speed():
    fast_and_sloppy = Metrics(characters=500, keypresses=600, errors=100,
                              first_try_correct=400, active_seconds=60)
    assert stars(fast_and_sloppy, Goals()) == 2
