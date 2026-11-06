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

## 7. Current status
`backend/tests/test_call_parser.py` and `backend/tests/test_mismatch.py` cover synthetic cases 1, 2, 5, 7 at the **transcript** level (text in, structured call out) — this is the logic Claude Code can verify without touching audio. `backend/tests/fixtures/transcripts.json` holds the corpus, reused by the parser tests now and by the demo's "play a test scenario" button once audio clips exist. Audio-level noise/overlap/Coval testing is not implemented yet (step 5 of CLAUDE.md's build order) — that requires real or synthesized audio files in `audio-samples/`, which don't exist yet.
