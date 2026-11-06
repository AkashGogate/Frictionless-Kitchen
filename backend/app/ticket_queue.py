"""Mocked active-ticket queue — a seeded stand-in for a real POS feed.

TECH_STACK.md is explicit: real POS integration is out of scope for v1.
This is an in-memory seed, not a persisted table, since the ticket queue
is reset per demo session (ARCHITECTURE.md session caps).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TicketLine:
    ticket_id: str
    item: str
    quantity: int
    station: str | None = None
    fulfilled: bool = False


def seed_tickets() -> list[TicketLine]:
    """A small, fixed ticket board. Good enough for v1 — swap for a real POS feed later."""
    return [
        TicketLine(ticket_id="T1", item="salmon", quantity=2, station="grill"),
        TicketLine(ticket_id="T2", item="burger", quantity=1, station="grill"),
        TicketLine(ticket_id="T3", item="risotto", quantity=1, station="saute"),
        TicketLine(ticket_id="T4", item="salad", quantity=3, station="pantry"),
    ]


class TicketQueue:
    """Mutable queue of open ticket lines for one session."""

    def __init__(self, tickets: list[TicketLine] | None = None) -> None:
        self.tickets: list[TicketLine] = tickets if tickets is not None else seed_tickets()

    def find_open_line(self, item: str, station: str | None) -> TicketLine | None:
        for line in self.tickets:
            if line.fulfilled or line.item != item:
                continue
            if station and line.station and line.station != station:
                continue
            return line
        return None

    def fulfill(self, line: TicketLine) -> None:
        line.fulfilled = True
