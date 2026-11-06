# Project Spec — Voice-Native Kitchen Operations Agent

Working name: kitchen-copilot (placeholder)
Author: Akash

## 1. The problem, precisely
Professional kitchens run on an existing verbal protocol — "calling the pass," "86 the salmon," "fire table 12" — because hands are full and the floor is too loud/fast to type or tap a screen. This project digitizes a behavior that already exists; it doesn't invent a new one.

What's missing today: verbal fire calls aren't captured anywhere. A mismatch between what was called and what the ticket says isn't caught until the wrong plate is already out. There's no timestamped record of calls, and no safety net for a misheard count beyond another human's attention — the one resource a loud kitchen doesn't have spare.

The governing test for every feature: remove the microphone — does the task still work, just worse (typing, tapping, writing)? If yes, cut it.

## 2. Why this, personally
Frustration with how easy it's become to do the bare minimum in food service, and real respect for kitchens that still put in the work. The throughline is cost, not front-of-house romance — lower error rates and less labor friction in the back of house is what lets a kitchen that cares charge less and still do it right. Scoped to the kitchen specifically — does not extend to customer-facing ordering.

## 3. Non-goals
- Front-of-house / table-side / customer ordering — already built and crowded (Tablevoice, PopID's Genius Handheld, SoundHound for Restaurants, ConverseNow, VoicePlug, Checkmate).
- Drive-thru / QSR ordering — Deepgram's own OfOne acquisition's lane.
- Any feature with a trivial non-voice substitute.
- Voice-stress/emotion-based inference of anything — not scientifically defensible, not in this project at any scope.

## 4. Core functionality (v1 scope)
1. Live fire-call capture — transcribe and structure spoken calls into order-line objects.
2. Mismatch detection — cross-reference spoken calls against the active ticket queue, flag discrepancies before the plate goes out.
3. Timestamped structured log — every call logged with speaker-turn attribution and timestamp, matched or not.
4. Noise-robust turn handling — tolerate overlapping/simultaneous calls plus ambient kitchen noise without breaking. This is the real technical difficulty of the project.

## 5. Success criteria
- Working pipeline: live or pre-recorded kitchen audio in → structured, timestamped, mismatch-flagged log out.
- Coval-based synthetic test suite with pass/fail scorecard and a documented failure-found-and-fixed story.
- A public, demoable surface with a safe fallback.
- An honest account of what breaks under hard conditions and what was done about it.

## 6. Target users / advertisable reach
Small/independent restaurant kitchens, reached through Akash's existing network — not an invented user base.

## 7. Alignment notes (Deepgram JD, for reference)
- Scoped project, shipped end-to-end — resist scope creep.
- Contribute to production Deepgram codebase — build on Pipecat, scope a real example/PR.
- Agentic tooling as default — use Claude Code throughout, keep notes on specific instances.
- Improve a workflow with AI tools — the Coval eval loop is this bullet.
- First-principles reasoning — design decisions defensible on their own terms, not copied from a competitor.
