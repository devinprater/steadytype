import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_cli_runs_a_lesson_from_stdin():
    script = "f1\nf1\nf2\nf2\n"
    result = subprocess.run(
        [sys.executable, "-m", "steadytype_engine.cli",
         str(ROOT / "engine" / "tests" / "fixtures" / "lesson_one.yaml")],
        input=script, capture_output=True, text=True, timeout=10, check=False,
    )
    assert result.returncode == 0
    assert "SPEAK:" in result.stdout
    assert "TONE: correct" in result.stdout
    assert "END" in result.stdout


def test_cli_reports_an_unknown_key_and_keeps_going():
    script = "wat\nf1\nf1\nf2\nf2\n"
    result = subprocess.run(
        [sys.executable, "-m", "steadytype_engine.cli",
         str(ROOT / "engine" / "tests" / "fixtures" / "lesson_one.yaml")],
        input=script, capture_output=True, text=True, timeout=10, check=False,
    )
    assert "ERROR: unknown key wat" in result.stdout
    assert result.returncode == 0
