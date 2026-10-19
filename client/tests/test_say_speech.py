import time

from steadytype_client.speech import SaySpeech


class FakeProcess:
    def __init__(self, text, log, delay=0.02):
        self.text, self.log, self.delay = text, log, delay
        self.done = False

    def wait(self):
        self.log.append(("start", self.text))
        time.sleep(self.delay)
        self.done = True
        self.log.append(("end", self.text))

    def poll(self):
        return 0 if self.done else None

    def terminate(self):
        self.done = True
        self.log.append(("stopped", self.text))


def make(log):
    speech = SaySpeech()
    speech._spawn = lambda text: FakeProcess(text, log)
    return speech


def test_two_lines_are_spoken_one_after_the_other():
    log = []
    speech = make(log)
    speech.speak("first")
    speech.speak("second")
    for _ in range(60):
        if len([e for e in log if e[0] == "end"]) >= 2:
            break
        time.sleep(0.05)
    assert [e for e in log if e[0] == "start"] == [("start", "first"), ("start", "second")]
    first_end = log.index(("end", "first"))
    second_start = log.index(("start", "second"))
    assert first_end < second_start


def test_an_interrupt_drops_what_is_waiting():
    log = []
    speech = make(log)
    speech.speak("keep")
    speech.speak("drop")
    speech.stop()
    assert ("stopped", "keep") in log or log == []


def test_interrupt_speaks_the_new_line_without_waiting_for_the_queue():
    log = []
    speech = make(log)
    speech.speak("old")
    speech.speak("new", interrupt=True)
    for _ in range(60):
        if ("start", "new") in log:
            break
        time.sleep(0.05)
    assert ("start", "new") in log
