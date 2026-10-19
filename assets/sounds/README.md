# Sound cues

Seven short sounds, one for each tone the engine can emit. They carry meaning that
speech would be too slow to deliver: correct, wrong, the race markers, the end of a
lesson, and the practice goal.

`manifest.json` maps each engine tone name to two files:

- `synth/` — generated sine cues with a short attack and decay. These are the default.
  They are 44.1 kHz, mono, 16-bit, between 82 and 413 ms, and identical on every platform.
- `model/` — Stable Audio 3 Small SFX, generated locally with the prompts below, then
  trimmed to the first onset, faded, and peaked at -3 dBFS. These are alternatives for
  auditioning. Several are longer than a lesson should wait, so they are not the default.

`audition.html` plays both sets.

## What each cue means

| Name | Meaning | Synth length |
|---|---|---|
| `correct` | A key was right | 82 ms |
| `wrong` | A key was wrong | 204 ms |
| `race_start` | The timed race begins | 236 ms |
| `race_warning` | Ten seconds left in the race | 144 ms |
| `race_end` | The race is over | 256 ms |
| `lesson_done` | The lesson is finished | 413 ms |
| `goal_reached` | The daily practice goal is met | 364 ms |

## Regenerating the model set

From `C:\ai\audio.cpp`, with the Stable Audio 3 Small SFX package installed:

```
audiocpp_cli.exe --task gen --family stable_audio \
  --model "C:/ai/audio.cpp/models/Stable-Audio-3-Small-SFX-GGUF" \
  --backend cuda --device 0 --seed 41 --duration-seconds 2.0 \
  --text "<prompt>" --out "<name>.wav"
```

Prompts used:

- correct — one short soft high-pitched wooden tick, dry, quiet, no reverb, no music, single sound
- wrong — two short low muffled thuds close together, dry, quiet, no reverb, no music
- race_start — three quick rising electronic beeps, clean, dry, no reverb, no music
- race_warning — two quick identical mid-pitch beeps, clean, dry, no reverb, no music
- race_end — three quick descending electronic beeps, clean, dry, no reverb, no music
- lesson_done — a short warm rising four-note marimba chime, dry, no reverb, no music
- goal_reached — a bright two-note bell chime, short, dry, no reverb, no music
