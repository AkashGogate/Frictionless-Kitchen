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

## Audio-level eval (docs/TESTING.md §7)
```bash
cd backend
.venv/bin/python audio_gen/generate_samples.py   # macOS only (uses `say`); regenerates audio-samples/
.venv/bin/python -m eval.run_eval --mode mock    # proves the scoring harness; real numbers need DEEPGRAM_API_KEY
```
Scorecard written to `audio-samples/scorecard.md`. See docs/TESTING.md §7 for the honest Coval-vs-this-harness gap.

## Deployment scaffold
- `backend/Dockerfile` + `backend/fly.toml` — builds and runs clean (verified locally with `docker build` + `docker run`, hits `/scenarios` and `/session/start` correctly). Deploy: `fly launch --no-deploy` once, then `fly secrets set DEEPGRAM_API_KEY=...` and `fly deploy` (needs a Fly.io account — not set up yet).
- `.github/workflows/test.yml` — runs `pytest` on every push/PR touching `backend/`.
- `frontend/config.js` — set `window.KITCHEN_COPILOT_API` to the real backend URL once it's deployed; defaults to `localhost:8000` until then. Frontend deploys to Vercel with zero config (plain static HTML, no build step).

## Running the frontend
```bash
cd frontend
npm install
npm run dev
```
