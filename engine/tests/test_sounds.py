import json
import wave
from pathlib import Path

from steadytype_engine.commands import ToneName

ROOT = Path(__file__).resolve().parents[2]
SOUNDS = ROOT / "assets" / "sounds"
MANIFEST = json.loads((SOUNDS / "manifest.json").read_text(encoding="utf-8"))

TONES = (
    ToneName.CORRECT, ToneName.WRONG, ToneName.RACE_START, ToneName.RACE_WARNING,
    ToneName.RACE_END, ToneName.LESSON_DONE, ToneName.GOAL_REACHED,
)


def test_every_engine_tone_has_a_sound():
    for tone in TONES:
        assert tone in MANIFEST, tone


def test_the_manifest_has_no_orphan_entries():
    assert set(MANIFEST) == set(TONES)


def test_default_sounds_are_short_mono_wavs():
    for tone in TONES:
        path = SOUNDS / MANIFEST[tone]["synth"]
        with wave.open(str(path)) as wav:
            assert wav.getnchannels() == 1, tone
            assert wav.getframerate() == 44100, tone
            assert wav.getsampwidth() == 2, tone
            milliseconds = wav.getnframes() / wav.getframerate() * 1000
        assert 50 <= milliseconds <= 450, (tone, milliseconds)


def test_every_sound_has_an_alternative_model_version():
    for tone in TONES:
        assert (SOUNDS / MANIFEST[tone]["model"]).exists(), tone
