"""A race is a one minute sprint against a pacer at a set speed."""

from __future__ import annotations

from collections.abc import Callable

from steadytype_engine.dictation import Passage

from steadytype_client.timed import TimedTestRunner

RACE_PASSAGE = Passage(
    title="The sprint",
    text="Keep your hands light and your eyes ahead. The pacer holds one speed, "
         "and yours is the only hand on the keys. Stay with it as long as you can.",
)


class RaceRunner(TimedTestRunner):
    def __init__(self, save: Callable, speak: Callable, target_wpm: float = 30.0,
                 seconds: int = 60, display: Callable | None = None,
                 passage: Passage = RACE_PASSAGE, **kwargs) -> None:
        super().__init__(passage, seconds, save=save, speak=speak, display=display,
                         **kwargs)
        self.seconds = seconds
        self.target_wpm = target_wpm

    def start(self) -> None:
        self.speak(f"Race. {self.seconds} seconds against a pacer at "
                   f"{self.target_wpm:.0f} words a minute. {self.passage.text}", True)
        super().start()

    def _finish_if_over(self) -> None:
        if self.done or self.test.state.name != "FINISHED":
            return
        self.done = True
        result = self.test.finish()
        self.save(self.test.attempt_record(self.lesson_id, result))
        beat = result.net_wpm >= self.target_wpm
        verdict = ("You beat the pacer." if beat else "The pacer beat you this time.")
        self.speak(f"Race over. {result.net_wpm:.0f} words per minute. {verdict}", True)
