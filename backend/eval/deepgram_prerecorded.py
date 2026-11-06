"""Deepgram's prerecorded (file-upload) transcription REST API — used by the
eval harness to transcribe audio-samples/*.wav offline (no live WebSocket
needed for file-based eval). Separate from deepgram_live.py (the live-mic
streaming path) because the two use different Deepgram endpoints entirely.

Unverified against a real DEEPGRAM_API_KEY, same caveat as deepgram_live.py.
"""
from __future__ import annotations

import os

import httpx

DEEPGRAM_PRERECORDED_URL = (
    "https://api.deepgram.com/v1/listen"
    "?model=nova-3&diarize=true&smart_format=true&punctuate=true"
)


async def transcribe_file(wav_path: str) -> list[tuple[str, str]]:
    """Returns a list of (speaker_turn, text) utterances, diarized, in order."""
    api_key = os.environ["DEEPGRAM_API_KEY"]
    with open(wav_path, "rb") as f:
        audio_bytes = f.read()

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            DEEPGRAM_PRERECORDED_URL,
            headers={"Authorization": f"Token {api_key}", "Content-Type": "audio/wav"},
            content=audio_bytes,
        )
        resp.raise_for_status()
        data = resp.json()

    utterances = data["results"]["utterances"]
    return [(f"speaker-{u['speaker']}", u["transcript"]) for u in utterances]
