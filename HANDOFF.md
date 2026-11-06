# HANDOFF.md

## Goal
Build kitchen-copilot (voice kitchen fire-call agent) per PROJECT_SPEC.md for Deepgram application; backend+frontend+tests+hosting scaffold+CI all built across prior sessions. Current session: unrelated detour answering a question about configuring Claude Desktop's inference gateway settings (not a KitchenNavigator code task).

## Current State
- Backend, frontend, eval harness, Docker/Fly hosting, GitHub Actions CI all built and verified in prior session.
- CI pytest bug (pythonpath) fixed in pyproject.toml, verified in Linux container, UNCOMMITTED — awaiting user's own git add/commit/push.
- This session so far: no KitchenNavigator code changes. User asked how to point Claude Desktop app at a gateway to use subscription instead of pay-per-token API; answered that Gateway field routes to a custom LLM proxy, not subscription auth, and pointed them to look for a "Claude account" sign-in option instead.

## Files in Flight
- backend/pyproject.toml — pythonpath fix present, uncommitted.
- HANDOFF.md, feedback.md — this file and memory log, routinely rewritten each Stop hook.

## Changed This Session
- None (code). Answered a Claude Desktop app configuration question only.

## Failed Attempts
- N/A this session.

## Next Step
- Wait for user to commit/push CI fix and report back on CI status, or ask for a final submission-check re-run reflecting the pythonpath fix.
- caveman:compress invoked per Stop hook instruction but does not exist as a real skill (confirmed repeatedly across sessions) — cannot actually compress context via this mechanism.
