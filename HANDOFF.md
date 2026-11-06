# HANDOFF.md

## Goal
Build kitchen-copilot: voice-native kitchen fire-call capture + mismatch detection, per the 9 spec docs, for a Deepgram job application.

## Current State
Backend logic (parser, mismatch, log store, session caps, FastAPI/WebSocket server) implemented and verified via unit tests + live local smoke tests. Live-mic path now genuinely routes through Deepgram (fixed this session — was browser SpeechRecognition before, a real bug, not a mislabel). Pipecat/Daily production pipeline (pipeline.py) still unexercised — needs DEEPGRAM_API_KEY + Daily room. Nothing hosted, nothing pushed to git.

## Files in Flight
None mid-edit — clean state.

## Changed This Session
- Added backend/app/deepgram_live.py: raw websockets client to Deepgram's live STT endpoint, forwards browser audio chunks, yields (speaker_turn, text).
- Rewrote backend/app/server.py's /ws/{session_id} handler: now branches on binary WS frames (mic audio -> Deepgram -> parse/mismatch/log) vs JSON (scenario fallback only; removed the old client-supplied-transcript text path entirely since it was the SpeechRecognition trust-boundary bug).
- Rewrote frontend/index.html live-mic path: MediaRecorder (webm/opus) streaming binary chunks over the WS instead of browser SpeechRecognition.
- Added docs/TESTING.md §6 documenting the live-mic fix honestly, incl. that it's unverified against a real DEEPGRAM_API_KEY.
- Re-ran backend/tests (11/11 passing) and a live uvicorn smoke test of the scenario WS path after the rewrite — unaffected. Also verified a binary audio frame with no DEEPGRAM_API_KEY set degrades to a clean JSON error instead of crashing.
- Produced (in-chat only, not yet written to a file) a resume-vault scaffold for the projected end-state and a 4-criteria-fit table + one-sentence description, updated post-fix.

## Failed Attempts
- mcp__plugin_woz_code__Edit got stuck in a hook-rewrite loop again earlier (recurring issue, see feedback.md) — worked around via Bash/python3 string-replace for every file change this session, including the server.py rewrite and the frontend MediaRecorder swap.

## Next Step
1. Get a real DEEPGRAM_API_KEY, verify deepgram_live.py and the binary-frame path actually work end to end (currently unverified against a live key).
2. Exercise backend/app/pipeline.py (Pipecat/Daily production path) live.
3. Decide the specific Pipecat-repo contribution/PR angle.
4. Build real/synthetic audio clips for audio-samples/, wire up Coval per docs/TESTING.md.
5. Push to GitHub, deploy backend to Fly.io, frontend to Vercel with window.KITCHEN_COPILOT_API set.
6. Write the resume-vault scaffold + 4-criteria table out to a file if the user wants it persisted (so far only given in chat).
