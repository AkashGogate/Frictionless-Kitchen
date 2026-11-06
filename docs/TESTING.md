# TESTING.md

## Why this is a first-class deliverable
The hardest part of this project — noise-robust, multi-speaker, overlapping call parsing — is exactly the kind of thing that "works in the quiet demo room, breaks in the real room." A rigorous eval suite is both the engineering safety net and the better live demo.

## 1. Tooling
- Pipecat → Coval integration (documented) — use it rather than building an eval harness from scratch.

## 2. Synthetic test set
1. Single clean call (baseline).
2. Two overlapping calls, different stations (core hard case).
3. Three+ simultaneous calls (stress case).
4. Call against a sustained noise bed.
5. Truncated/shouted/non-standard phrasing.
6. Accented speech — don't skip, known weak spot.
7. False-trigger check — background chatter that is not a call.

## 3. Metrics
Call-parse accuracy per condition, false-trigger rate, missed-call rate under overlap, end-to-end latency.

## 4. The interview narrative
Pick one specific failure Coval caught, show the condition, what broke, the fix, and the before/after metric.

## 5. Live-demo safety net
Every synthetic clip doubles as a "play a test scenario" option in the public demo UI.

## 6. Live-mic path status (fixed 2026-11-06)
Live-mic used to send browser SpeechRecognition transcripts straight to the backend — that never touched Deepgram, so it wasn't the thing being applied for. Fixed: browser MediaRecorder now streams raw webm/opus audio over the WebSocket as binary frames; the backend forwards it to Deepgram's live STT (`backend/app/deepgram_live.py`) and the resulting transcript runs through the identical `parse_call -> check_mismatch -> log` path the scenario fallback uses. Unverified end-to-end against a real `DEEPGRAM_API_KEY` as of this fix — only the degrade-gracefully-without-a-key branch has been exercised live.

## 7. Audio-level corpus + eval harness (built 2026-11-06)
Real audio now exists: `backend/audio_gen/generate_samples.py` generates 7 WAV clips into `audio-samples/` via macOS `say` + real numpy/soundfile signal mixing — genuine overlapping speech (TC2/TC3) and a genuine escalating white-noise bed (TC4), not just text fixtures. `audio-samples/manifest.json` holds each clip's ground truth.

`backend/eval/run_eval.py` runs that corpus through Deepgram's prerecorded STT (`backend/eval/deepgram_prerecorded.py`) and the SAME `parse_call`/`check_mismatch` code the live server uses, scores call-parse accuracy / false-trigger / missed-call / latency, and writes `audio-samples/scorecard.md`.

**The Coval gap, stated plainly:** this project's docs call for Pipecat → Coval integration specifically. Coval (coval.dev) is a third-party hosted product needing its own account/API key, which this build doesn't have — so it isn't wired in. What's built instead is a local, Deepgram-grounded harness covering the same test classes and metrics. If a `COVAL_API_KEY` shows up later, swap `transcribe_file` for Coval's ingestion API; the manifest/scoring logic doesn't need to change.

**Verified:** the scorer itself is unit-tested (`tests/test_eval_scoring.py`) to actually catch a misheard quantity and a false-trigger, not just pass cleanly — and `--mode mock` ran clean (trivially 100%, since it skips real STT) to prove the harness runs end to end. **Not verified:** real Deepgram transcription of the generated audio — needs `DEEPGRAM_API_KEY`, same gap as the live-mic path.

Accented-speech caveat (TC6): uses a different macOS `say` voice/locale (en_IN) as a stand-in for a real accent — a known limitation of synthetic TTS, not a substitute for real accented speakers.

## 8. Current status
`backend/tests/test_call_parser.py` and `backend/tests/test_mismatch.py` cover synthetic cases 1, 2, 5, 7 at the **transcript** level (text in, structured call out) — this is the logic Claude Code can verify without touching audio. `backend/tests/fixtures/transcripts.json` holds the corpus, reused by the parser tests now and by the demo's "play a test scenario" button once audio clips exist. Audio-level noise/overlap/Coval testing is not implemented yet (step 5 of CLAUDE.md's build order) — that requires real or synthesized audio files in `audio-samples/`, which don't exist yet.
