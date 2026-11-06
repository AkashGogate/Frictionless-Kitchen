# CLAUDE.md

Context for Claude Code when implementation starts. Read PROJECT_SPEC.md, docs/ARCHITECTURE.md, docs/TESTING.md first.

## Non-negotiable constraints
- No front-of-house/customer-ordering features — back-of-house only.
- No feature with a trivial non-voice substitute.
- No voice-stress/emotion-inference anything.
- Agent runtime needs a persistent-connection host, not plain serverless/Vercel.
- Public demo surface ships with both the live-mic path AND the test-scenario fallback, plus a session/time cap — never the live-mic path alone.

## Build order
1. `backend/` — Pipecat skeleton: audio in → Deepgram STT → call-parsing stub → log stub (single-speaker clean-audio happy path first).
2. `tests/` — synthetic clips, starting with the clean and two-overlapping-calls cases — don't wait for "done" backend to start this.
3. Mismatch detection against a mocked ticket queue.
4. Noise-robustness pass — layer in noise-bed and overlap cases, iterate.
5. Coval integration via Pipecat's documented connector.
6. `frontend/` — minimal demo page: live-mic button, test-scenario button, log display, mismatch display.
7. Hosting: backend to a persistent-connection host, frontend to Vercel; rate limiting and session caps before any link is shared.

When in doubt: apply the mic-removal test from PROJECT_SPEC.md §1. Flag ambiguity back to Akash rather than guessing scope.
