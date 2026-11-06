"""Rule-based call-parsing layer (TECH_STACK.md: keyword/rule-based first pass).

Deliberately simple regex/keyword matching: the hard problem in this project is
upstream audio robustness (noise, overlap), not NLU sophistication. Takes a
transcript (diarized speaker-turn text) and returns a structured ParsedCall.
"""
from __future__ import annotations

import re

from app.models import ParsedCall

MENU_ITEMS: dict[str, str] = {
    "salmon": "salmon", "steak": "steak", "ribeye": "steak", "burger": "burger",
    "fries": "fries", "salad": "salad", "soup": "soup", "pasta": "pasta",
    "risotto": "risotto", "chicken": "chicken", "duck": "duck", "lamb": "lamb",
    "scallops": "scallops", "oysters": "oysters", "tacos": "tacos",
}

STATION_KEYWORDS: dict[str, str] = {
    "grill": "grill", "saute": "saute", "fry": "fry",
    "pantry": "pantry", "pass": "pass", "expo": "pass",
}

WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

_TICKET_RE = re.compile(r"\btable\s+(\d+)\b|\bticket\s+(\d+)\b", re.IGNORECASE)
_QTY_RE = re.compile(r"\b(\d+)\b")

FIRE_VERBS = ("fire", "order", "calling", "need", "86")


def _find_quantity(text: str) -> int:
    m = _QTY_RE.search(text)
    if m:
        return int(m.group(1))
    for word, n in WORD_NUMBERS.items():
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            return n
    return 1


def _find_item(text_lower: str) -> str | None:
    for keyword, canonical in MENU_ITEMS.items():
        if keyword in text_lower:
            return canonical
    return None


def _find_station(text_lower: str) -> str | None:
    for keyword, canonical in STATION_KEYWORDS.items():
        if keyword in text_lower:
            return canonical
    return None


def parse_call(raw_text: str, speaker_turn: str) -> ParsedCall:
    """Parse one diarized utterance into a structured call, or mark it as not a call.

    Non-goal per PROJECT_SPEC.md: no LLM here for v1 scope correctness tests;
    TECH_STACK.md allows an LLM fallback for ambiguous phrasing later.
    """
    text_lower = raw_text.lower()
    item = _find_item(text_lower)
    has_fire_verb = any(v in text_lower for v in FIRE_VERBS)

    # Fires per TESTING.md #7: background chatter that names no item and no fire verb is ignored.
    is_call = item is not None or has_fire_verb

    return ParsedCall(
        raw_text=raw_text,
        item=item,
        quantity=_find_quantity(text_lower) if item else 0,
        station=_find_station(text_lower),
        speaker_turn=speaker_turn,
        is_call=is_call,
    )
