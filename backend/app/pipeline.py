"""Pipecat skeleton: audio in -> Deepgram STT (diarized) -> call-parsing -> mismatch -> log.

CLAUDE.md build order step 1. This wires the real Pipecat/Deepgram services;
it needs a running Daily room + DEEPGRAM_API_KEY to actually move audio, so it
is exercised live in `backend/app/server.py`'s /session endpoint, not in unit
tests (those test call_parser/mismatch directly on transcript text instead).
"""
from __future__ import annotations

import os

from pipecat.frames.frames import Frame, TranscriptionFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.transports.services.daily import DailyParams, DailyTransport

from app.log_store import write_result
from app.call_parser import parse_call
from app.mismatch import check_mismatch
from app.ticket_queue import TicketQueue


class CallProcessor(FrameProcessor):
    """Turns each diarized transcription frame into a logged, mismatch-checked call."""

    def __init__(self, queue: TicketQueue, session_factory, on_result=None) -> None:
        super().__init__()
        self._queue = queue
        self._session_factory = session_factory
        self._on_result = on_result

    async def process_frame(self, frame: Frame, direction: FrameDirection) -> None:
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame):
            speaker_turn = getattr(frame, "user_id", None) or "speaker-0"
            call = parse_call(frame.text, speaker_turn=speaker_turn)
            result = check_mismatch(call, self._queue)

            async with self._session_factory() as db_session:
                await write_result(db_session, result)

            if self._on_result:
                await self._on_result(result)

        await self.push_frame(frame, direction)


def build_pipeline(room_url: str, token: str, session_factory, on_result=None) -> PipelineTask:
    """Daily transport -> diarized Deepgram STT -> CallProcessor -> log store."""
    transport = DailyTransport(
        room_url, token, "kitchen-copilot",
        DailyParams(audio_in_enabled=True, audio_out_enabled=True, vad_audio_passthrough=True),
    )

    stt = DeepgramSTTService(
        api_key=os.environ["DEEPGRAM_API_KEY"],
        live_options={"model": "nova-3", "diarize": True, "smart_format": True},
    )

    call_processor = CallProcessor(TicketQueue(), session_factory, on_result=on_result)

    pipeline = Pipeline([transport.input(), stt, call_processor, transport.output()])
    return PipelineTask(pipeline, params=PipelineParams(allow_interruptions=True))


async def run_pipeline(task: PipelineTask) -> None:
    runner = PipelineRunner()
    await runner.run(task)
