"""Mismatch detection: cross-reference a parsed call against the active ticket queue.

PROJECT_SPEC.md #4.2 — flag discrepancies before the plate goes out.
"""
from __future__ import annotations

from app.models import MismatchResult, ParsedCall
from app.ticket_queue import TicketQueue


def check_mismatch(call: ParsedCall, queue: TicketQueue) -> MismatchResult:
    if not call.is_call:
        # Not a fire call at all (background chatter) — nothing to match, nothing to flag.
        return MismatchResult(call=call, matched=True, reason=None)

    if call.item is None:
        return MismatchResult(call=call, matched=False, reason="no menu item recognized in call")

    line = queue.find_open_line(call.item, call.station)
    if line is None:
        return MismatchResult(
            call=call, matched=False,
            reason=f"no open ticket line for '{call.item}'" + (f" at {call.station}" if call.station else ""),
        )

    if line.quantity != call.quantity:
        return MismatchResult(
            call=call, matched=False, ticket_id=line.ticket_id,
            reason=f"quantity mismatch: called {call.quantity}, ticket expects {line.quantity}",
        )

    queue.fulfill(line)
    return MismatchResult(call=call, matched=True, ticket_id=line.ticket_id)
