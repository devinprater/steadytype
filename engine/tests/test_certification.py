import pytest

from steadytype_engine.certification import score_test, word_errors

TARGET = "the quick brown fox jumps over the lazy dog"


def test_perfect_text_has_no_errors():
    assert word_errors(TARGET, TARGET) == 0


def test_one_wrong_word_is_one_error():
    assert word_errors(TARGET.replace("brown", "brawn"), TARGET) == 1


def test_a_missing_word_and_an_extra_word_each_count_once():
    assert word_errors(TARGET.rsplit(" ", 1)[0], TARGET) == 1
    assert word_errors(TARGET + " extra", TARGET) == 1


def test_net_speed_deducts_one_word_per_error_per_minute():
    typed = "word " * 100
    wrong = typed.replace("word", "ward", 5)
    result = score_test(wrong, typed, 60)
    assert result.error_words == 5
    assert result.gross_wpm == pytest.approx(100.0)
    assert result.net_wpm == pytest.approx(95.0)


def test_pass_needs_both_the_speed_and_the_error_limit():
    typed = "word " * 100
    assert score_test(typed, typed, 60).passed
    eleven = typed.replace("word", "ward", 11)
    assert score_test(eleven, typed, 60).error_words == 11
    assert not score_test(eleven, typed, 60).passed
