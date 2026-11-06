# TECH_STACK.md

## Backend / agent runtime
- Python 3.11+
- Pipecat — audio pipeline orchestration (transport → VAD/turn-detection → STT → processing → TTS).
- Daily transport (WebRTC) via Pipecat's native integration.
- Deepgram STT (Nova-3 or Flux) with `diarize=true` for per-speaker-turn labels.
- Turn-taking: Pipecat's Silero VAD + Deepgram's end-of-utterance signal.
- Call-parsing layer: keyword/rule-based first pass (menu item names, quantities, station keywords) with a small LLM fallback for ambiguous phrasing.
- Ticket/order queue: mocked — a seeded SQLite table standing in for a real POS feed.
- Structured log store: SQLite via SQLAlchemy (async).
- API/WebSocket layer: FastAPI + WebSocket.
- TTS (mismatch alerts): Deepgram TTS (Aura).

## Frontend / demo surface
- Next.js/React. Minimal by design.

## Eval/testing
- Coval, via Pipecat's documented Coval integration.

## Hosting
- Backend: a persistent-connection host — Fly.io (default) or Render/AWS Fargate/EC2. Not Vercel for the agent runtime.
- Frontend: Vercel.

## Explicitly not used
- Vercel for the agent runtime.
- Any voice-stress/emotion/deception inference.
- Real POS/kitchen-display integration (mocked instead, stated honestly).
