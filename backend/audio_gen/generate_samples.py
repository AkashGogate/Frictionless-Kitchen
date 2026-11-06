"""Generates the TESTING.md synthetic audio corpus with real TTS + real signal
mixing (numpy/soundfile, pulled in as pipecat deps) — macOS `say` is the TTS
engine, so this only runs on macOS. No network/API key needed.

This produces actual audio files with actual overlapping speech and actual
noise beds, not just the text-level fixtures in tests/fixtures/transcripts.json.
Honest limitation: "accented speech" uses a different `say` voice/locale as a
stand-in for a real accent, which is a real limitation of synthetic TTS, not a
substitute for real accented speakers — noted here and in docs/TESTING.md.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

SAMPLE_RATE = 16000
OUT_DIR = Path(__file__).resolve().parent.parent.parent / "audio-samples"
MANIFEST_PATH = OUT_DIR / "manifest.json"


def _say(text: str, voice: str = "Samantha") -> np.ndarray:
    """Render text to a mono float32 array at SAMPLE_RATE via macOS `say`."""
    tmp = OUT_DIR / "_tmp_say.wav"
    subprocess.run(
        ["say", "-v", voice, "-o", str(tmp), "--file-format=WAVE",
         f"--data-format=LEI16@{SAMPLE_RATE}", text],
        check=True, capture_output=True,
    )
    audio, sr = sf.read(tmp, dtype="float32")
    assert sr == SAMPLE_RATE
    tmp.unlink()
    return audio


def _pad_to(a: np.ndarray, length: int) -> np.ndarray:
    if len(a) >= length:
        return a[:length]
    return np.pad(a, (0, length - len(a)))


def _mix(clips: list[tuple[np.ndarray, int]]) -> np.ndarray:
    """Mix (audio, start_sample) pairs into one track, summed and clipped to [-1, 1]."""
    total_len = max(start + len(a) for a, start in clips)
    out = np.zeros(total_len, dtype="float32")
    for a, start in clips:
        out[start:start + len(a)] += a
    return np.clip(out, -1.0, 1.0)


def _white_noise(length: int, rms: float) -> np.ndarray:
    noise = np.random.default_rng(42).normal(0, 1, length).astype("float32")
    noise *= rms / (np.sqrt(np.mean(noise**2)) + 1e-9)
    return noise


def generate() -> list[dict]:
    OUT_DIR.mkdir(exist_ok=True)
    manifest = []

    def save(name: str, audio: np.ndarray, description: str, expected_calls: list[dict]):
        path = OUT_DIR / f"{name}.wav"
        sf.write(path, audio, SAMPLE_RATE)
        manifest.append({"name": name, "file": path.name, "description": description, "expected_calls": expected_calls})

    # TC1: single clean call (baseline)
    a = _say("Fire two salmon on the grill")
    save("tc1_clean_single_call", a, "Single clean call, baseline happy path.",
         [{"text": "Fire two salmon on the grill", "item": "salmon", "quantity": 2, "station": "grill"}])

    # TC2: two overlapping calls, different stations — second starts 60% into the first
    a1 = _say("Fire one burger on the grill")
    a2 = _say("Need one risotto on the saute")
    overlap_start = int(len(a1) * 0.6)
    mixed = _mix([(a1, 0), (a2, overlap_start)])
    save("tc2_overlapping_two_stations", mixed, "Two overlapping calls, different stations — the core hard case.",
         [{"text": "Fire one burger on the grill", "item": "burger", "quantity": 1, "station": "grill"},
          {"text": "Need one risotto on the saute", "item": "risotto", "quantity": 1, "station": "saute"}])

    # TC3: three+ simultaneous calls (stress case) — all start together
    b1 = _say("Fire two chicken on the grill")
    b2 = _say("Need one duck on the pass")
    b3 = _say("Fire three tacos")
    mixed3 = _mix([(b1, 0), (b2, 0), (b3, 0)])
    save("tc3_three_simultaneous", mixed3, "Three simultaneous calls, full overlap — stress case.",
         [{"text": "Fire two chicken on the grill", "item": "chicken", "quantity": 2, "station": "grill"},
          {"text": "Need one duck on the pass", "item": "duck", "quantity": 1, "station": "pass"},
          {"text": "Fire three tacos", "item": "tacos", "quantity": 3, "station": None}])

    # TC4: call against a sustained, increasing noise bed
    c = _say("Fire two scallops on the saute")
    noise = _white_noise(len(c), rms=0.0)  # built up below in 3 escalating segments
    third = len(c) // 3
    noise_ramped = np.concatenate([
        _white_noise(third, rms=0.02),
        _white_noise(third, rms=0.06),
        _white_noise(len(c) - 2 * third, rms=0.12),
    ])
    noisy = np.clip(c + noise_ramped, -1.0, 1.0)
    save("tc4_noise_bed_ramp", noisy, "Clean call against an escalating white-noise bed (stand-in for exhaust fan/sizzling/clatter).",
         [{"text": "Fire two scallops on the saute", "item": "scallops", "quantity": 2, "station": "saute"}])

    # TC5: truncated/shouted/non-standard phrasing
    d = _say("SALMON TWO GRILL NOW")
    save("tc5_truncated_shouted", d, "Truncated/shouted non-standard phrasing.",
         [{"text": "SALMON TWO GRILL NOW", "item": "salmon", "quantity": 2, "station": "grill"}])

    # TC6: accented speech — different `say` voice/locale as a stand-in (see module docstring caveat)
    e = _say("Fire one lamb on the grill", voice="Rishi")
    save("tc6_accented_speech", e, "Accented speech (en_IN voice stand-in — not a real accent corpus, a known limitation).",
         [{"text": "Fire one lamb on the grill", "item": "lamb", "quantity": 1, "station": "grill"}])

    # TC7: false-trigger check — background chatter, not a call, mixed with a real call
    chatter = _say("did you catch the game last night")
    real_call = _say("fire three salad on pantry")
    mixed7 = _mix([(chatter, 0), (real_call, len(chatter) + SAMPLE_RATE // 2)])  # 0.5s gap, not overlapping
    save("tc7_false_trigger_chatter", mixed7, "Background chatter (not a call) followed by a real call — chatter must be ignored.",
         [{"text": "did you catch the game last night", "item": None, "quantity": 0, "station": None, "is_call": False},
          {"text": "fire three salad on pantry", "item": "salad", "quantity": 3, "station": "pantry"}])

    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    m = generate()
    print(f"Generated {len(m)} audio clips into {OUT_DIR}")
    for entry in m:
        print(" -", entry["name"], "->", entry["file"])
