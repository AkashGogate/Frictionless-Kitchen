# kitchen-copilot

Voice-native kitchen operations agent. Captures spoken fire calls in a live, noisy, multi-speaker kitchen, structures them, and flags mismatches against the active ticket queue before the wrong plate goes out. Not a chatbot with a mic icon — every feature requires that there's no non-voice fallback mid-service.

Docs: [PROJECT_SPEC.md](PROJECT_SPEC.md) (read first) → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) → [docs/TESTING.md](docs/TESTING.md) → [CLAUDE.md](CLAUDE.md) (build order).

## Status
Backend happy-path + mismatch detection + call-parser + unit tests implemented. Live Deepgram/Pipecat wiring needs a `DEEPGRAM_API_KEY`. Frontend demo page scaffolded. Coval integration and audio-level noise-robustness pass are next (see docs/TESTING.md §6).

## Layout
- `backend/` — Pipecat pipeline, call-parser, mismatch detector, log store, FastAPI/WebSocket server.
- `frontend/` — demo page (live-mic + test-scenario buttons, log view).
- `tests/` symlinked via `backend/tests/` — unit tests for call-parsing/mismatch logic + synthetic transcript fixtures.
- `docs/` — architecture, testing, tech stack, user flow, demo plan, requirements.
- `audio-samples/` — real/recorded kitchen audio (empty for now).

## Running the backend
```bash
cd backend
uv sync
export DEEPGRAM_API_KEY=...   # only needed for live audio, not for unit tests
uv run uvicorn app.server:app --reload --port 8000
```

## Running tests
```bash
cd backend
uv run pytest -v
```

## Running the frontend
```bash
cd frontend
npm install
npm run dev
```
