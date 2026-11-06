"""Shared data shapes for a parsed kitchen call and its mismatch result."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ParsedCall:
    raw_text: str
    item: str | None
    quantity: int
    station: str | None
    speaker_turn: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_call: bool = True  # False => classified as background chatter, not a fire call


@dataclass
class MismatchResult:
    call: ParsedCall
    matched: bool
    reason: str | None = None  # populated only when matched is False
    ticket_id: str | None = None
