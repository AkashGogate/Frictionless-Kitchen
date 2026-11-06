"""Thin wrapper around Deepgram's live-transcription WebSocket API.

Used by the demo's live-mic path so browser audio actually goes through
Deepgram (not the browser's own SpeechRecognition) — see server.py's
/ws/{session_id} binary-frame handling. This is deliberately a raw
`websockets` client against Deepgram's `listen` endpoint rather than pulling
in the full Pipecat/Daily transport: the demo page sends audio directly over
plain WebSocket (MediaRecorder webm/opus chunks), it never joins a Daily
room, so Pipecat's transport layer doesn't apply here. pipeline.py still owns
the production Daily/Pipecat path for a real kitchen mic array.

NOT exercised against a live DEEPGRAM_API_KEY in this build — the
request/response shape below follows Deepgram's documented streaming API,
but treat it as unverified until run with a real key (be honest about this
in the demo, per PROJECT_SPEC.md's "honest account" success criterion).
"""
from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator

import websockets

DEEPGRAM_LISTEN_URL = (
    "wss://api.deepgram.com/v1/listen"
    "?model=nova-3&diarize=true&smart_format=true&punctuate=true&interim_results=false"
)


async def stream_transcripts(audio_chunks: AsyncIterator[bytes]) -> AsyncIterator[tuple[str, str]]:
    """Forward audio chunks to Deepgram, yield (speaker_turn, text) for each final transcript.

    audio_chunks: an async iterator of raw webm/opus bytes from the browser's MediaRecorder.
    Deepgram auto-detects the WebM/Opus container; no encoding/sample_rate params needed.
    """
    api_key = os.environ["DEEPGRAM_API_KEY"]
    async with websockets.connect(
        DEEPGRAM_LISTEN_URL, additional_headers={"Authorization": f"Token {api_key}"}
    ) as dg_ws:

        async def _sender():
            async for chunk in audio_chunks:
                await dg_ws.send(chunk)
            await dg_ws.send(json.dumps({"type": "CloseStream"}))

        import asyncio
        sender_task = asyncio.create_task(_sender())
        try:
            async for raw in dg_ws:
                event = json.loads(raw)
                if event.get("type") != "Results" or not event.get("is_final"):
                    continue
                alt = event.get("channel", {}).get("alternatives", [{}])[0]
                text = alt.get("transcript", "")
                if not text:
                    continue
                speakers = {w.get("speaker") for w in alt.get("words", []) if "speaker" in w}
                speaker_turn = f"speaker-{speakers.pop()}" if len(speakers) == 1 else "speaker-0"
                yield speaker_turn, text
        finally:
            sender_task.cancel()
