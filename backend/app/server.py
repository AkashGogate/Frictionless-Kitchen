"""FastAPI/WebSocket demo server.

ARCHITECTURE.md #2.2: the public demo ships BOTH the live-mic path and the
test-scenario fallback through the identical call_parser -> mismatch -> log
code path, so the demo is honestly representative either way.
"""
from __future__ import annotations

import asyncio
import json
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.call_parser import parse_call
from app.log_store import init_db, make_session_factory, write_result
from app.mismatch import check_mismatch
from app.deepgram_live import stream_transcripts
from app.session import KitchenSession, SessionLimitExceeded
from app.ticket_queue import TicketQueue

engine, SessionFactory = make_session_factory()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(engine)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ponytail: wide open for a public demo; narrow to the Vercel origin once that URL exists.
    allow_methods=["*"],
    allow_headers=["*"],
)

# ponytail: one in-memory queue per demo session id; fine for a single-instance demo.
_queues: dict[str, TicketQueue] = {}
_active: dict[str, KitchenSession] = {}


def _client_ip(request_or_ws) -> str:
    return request_or_ws.client.host if request_or_ws.client else "unknown"


@app.post("/session/start")
async def start_session(request: Request):
    client_ip = _client_ip(request)
    session_id = str(uuid.uuid4())
    try:
        session = KitchenSession(session_id, client_ip)
    except SessionLimitExceeded as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    _active[session_id] = session
    _queues[session_id] = TicketQueue()
    return {"session_id": session_id, "max_seconds": session.seconds_remaining()}


@app.post("/session/{session_id}/kill")
async def kill_session(session_id: str):
    session = _active.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="unknown session")
    session.close()
    _active.pop(session_id, None)
    _queues.pop(session_id, None)
    return {"killed": True}


def _fixture_path() -> str:
    import pathlib
    return str(pathlib.Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "transcripts.json")


@app.get("/scenarios")
async def list_scenarios():
    """Backs the demo UI's 'Play a test scenario' button (DEMO_PLAN.md #4)."""
    with open(_fixture_path()) as f:
        data = json.load(f)
    return [{"name": c["name"], "description": c["description"]} for c in data]


@app.websocket("/ws/{session_id}")
async def call_log_ws(websocket: WebSocket, session_id: str):
    """Streams parsed/mismatch-checked calls to the frontend live log (USER_FLOW.md #9).

    Accepts either {"type": "transcript", "text": ..., "speaker_turn": ...} for a
    live-mic client-side-transcribed turn, or {"type": "scenario", "name": ...}
    to replay a fixture scenario through the same parse->mismatch->log path.
    """
    session = _active.get(session_id)
    if session is None:
        await websocket.close(code=4404, reason="unknown session")
        return

    await websocket.accept()
    queue = _queues[session_id]

    mic_audio_queue: asyncio.Queue[bytes | None] | None = None
    mic_task: asyncio.Task | None = None

    async def _emit_result(call, result):
        async with SessionFactory() as db_session:
            await write_result(db_session, result)
        await websocket.send_json({
            "raw_text": call.raw_text,
            "item": call.item,
            "quantity": call.quantity,
            "station": call.station,
            "speaker_turn": call.speaker_turn,
            "is_call": call.is_call,
            "matched": result.matched,
            "reason": result.reason,
            "ticket_id": result.ticket_id,
        })

    async def _consume_mic_audio(audio_queue: asyncio.Queue[bytes | None]):
        """Live-mic path: forward browser audio to Deepgram, run results through
        the same parse_call -> check_mismatch -> log path the scenario path uses
        (fixes the two-pipelines-behind-one-UI gap: both sources hit Deepgram)."""
        async def _chunks():
            while True:
                chunk = await audio_queue.get()
                if chunk is None:
                    return
                yield chunk

        async for speaker_turn, text in stream_transcripts(_chunks()):
            call = parse_call(text, speaker_turn=speaker_turn)
            result = check_mismatch(call, queue)
            await _emit_result(call, result)

    try:
        while not session.expired():
            msg = await websocket.receive()

            if msg.get("type") == "websocket.disconnect":
                break

            if "bytes" in msg and msg["bytes"] is not None:
                # Binary frame = a MediaRecorder audio chunk from the live-mic path.
                if "DEEPGRAM_API_KEY" not in os.environ:
                    await websocket.send_json({"error": "DEEPGRAM_API_KEY not set on the server; live mic needs it"})
                    continue
                if mic_audio_queue is None:
                    mic_audio_queue = asyncio.Queue()
                    mic_task = asyncio.create_task(_consume_mic_audio(mic_audio_queue))
                await mic_audio_queue.put(msg["bytes"])
                continue

            if "text" not in msg or msg["text"] is None:
                continue
            payload = json.loads(msg["text"])

            if payload.get("type") == "mic_stop" and mic_audio_queue is not None:
                await mic_audio_queue.put(None)
                continue

            if payload.get("type") == "scenario":
                with open(_fixture_path()) as f:
                    scenarios = {c["name"]: c for c in json.load(f)}
                scenario = scenarios.get(payload["name"])
                if scenario is None:
                    await websocket.send_json({"error": f"unknown scenario {payload['name']!r}"})
                    continue
                for turn in scenario["turns"]:
                    call = parse_call(turn["text"], speaker_turn=turn["speaker_turn"])
                    result = check_mismatch(call, queue)
                    await _emit_result(call, result)
    except WebSocketDisconnect:
        pass
    finally:
        if mic_audio_queue is not None:
            await mic_audio_queue.put(None)
        if mic_task is not None:
            await mic_task
        session.close()
        _active.pop(session_id, None)
        _queues.pop(session_id, None)
