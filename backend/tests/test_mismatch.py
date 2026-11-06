"""Unit tests for mismatch detection against the mocked ticket queue."""
from app.call_parser import parse_call
from app.mismatch import check_mismatch
from app.ticket_queue import TicketQueue


def test_matched_call_fulfills_ticket_line():
    queue = TicketQueue()
    call = parse_call("fire two salmon on the grill", speaker_turn="speaker-0")
    result = check_mismatch(call, queue)
    assert result.matched is True
    assert result.ticket_id == "T1"
    assert queue.tickets[0].fulfilled is True


def test_quantity_mismatch_flagged():
    queue = TicketQueue()
    call = parse_call("fire one salmon on the grill", speaker_turn="speaker-0")
    result = check_mismatch(call, queue)
    assert result.matched is False
    assert "quantity mismatch" in result.reason


def test_item_with_no_open_ticket_flagged():
    queue = TicketQueue()
    call = parse_call("fire two oysters", speaker_turn="speaker-0")
    result = check_mismatch(call, queue)
    assert result.matched is False
    assert "no open ticket line" in result.reason


def test_background_chatter_never_flagged_as_mismatch():
    queue = TicketQueue()
    call = parse_call("did you catch the game last night", speaker_turn="speaker-0")
    result = check_mismatch(call, queue)
    assert result.matched is True
    assert result.reason is None


def test_same_item_cannot_be_fulfilled_twice():
    queue = TicketQueue()
    first = check_mismatch(parse_call("fire two salmon on the grill", speaker_turn="speaker-0"), queue)
    second = check_mismatch(parse_call("fire two salmon on the grill", speaker_turn="speaker-1"), queue)
    assert first.matched is True
    assert second.matched is False
