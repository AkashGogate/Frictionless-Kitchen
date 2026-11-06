# USER_FLOW.md

## Primary flow — live kitchen session
1. Session start (manual trigger for v1).
2. Kitchen mic/array streams continuously via Daily/WebRTC into Pipecat.
3. VAD + Deepgram end-of-utterance segment the stream into discrete turns.
4. Deepgram STT (diarized) returns text + anonymous speaker-turn label per turn.
5. Call-parsing layer extracts item, quantity, station/table reference.
6. Mismatch check against the mocked active-ticket queue — match logs clean, mismatch gets flagged.
7. On mismatch only: spoken TTS alert back to the kitchen and/or a flag on the live log.
8. Every call, matched or not, is written to the structured log with timestamp + speaker-turn id.
9. Frontend log updates live over WebSocket.

## Secondary flow — demo/test mode
1. Visitor picks "Use your own mic" or "Play a test scenario."
2. Own-mic path streams via the same Daily/WebRTC route as production; test-scenario path streams a pre-recorded synthetic clip through the identical pipeline.
3. Both produce the same live log + mismatch output, within the session cap from ARCHITECTURE.md.

## Tertiary flow — eval (not a live user flow)
Coval-connected suite runs the full synthetic test set against the deployed pipeline on demand/CI.
