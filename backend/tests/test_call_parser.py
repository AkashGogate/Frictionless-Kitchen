"""Unit tests for the call-parsing layer, at the transcript level (no audio).

Covers TESTING.md synthetic cases 1, 2, 5, 7 — docs/TESTING.md #6.
"""
from app.call_parser import parse_call


def test_clean_single_call():
    call = parse_call("Fire two salmon on the grill", speaker_turn="speaker-0")
    assert call.is_call is True
    assert call.item == "salmon"
    assert call.quantity == 2
    assert call.station == "grill"


def test_overlapping_calls_different_stations():
    a = parse_call("Fire one burger on the grill", speaker_turn="speaker-0")
    b = parse_call("Need one risotto on the saute", speaker_turn="speaker-1")
    assert (a.item, a.station) == ("burger", "grill")
    assert (b.item, b.station) == ("risotto", "saute")
    assert a.speaker_turn != b.speaker_turn


def test_truncated_shouted_phrasing():
    call = parse_call("SALMON TWO GRILL NOW", speaker_turn="speaker-0")
    assert call.item == "salmon"
    assert call.quantity == 2
    assert call.station == "grill"

    call2 = parse_call("86 the duck", speaker_turn="speaker-1")
    assert call2.is_call is True
    assert call2.item == "duck"


def test_false_trigger_background_chatter_ignored():
    chatter = parse_call("did you catch the game last night", speaker_turn="speaker-0")
    assert chatter.is_call is False

    real_call = parse_call("fire three salad on pantry", speaker_turn="speaker-1")
    assert real_call.is_call is True
    assert real_call.item == "salad"
    assert real_call.quantity == 3


def test_word_number_quantity():
    call = parse_call("fire three tacos", speaker_turn="speaker-0")
    assert call.quantity == 3


def test_no_item_recognized_but_has_fire_verb_is_still_a_call():
    call = parse_call("fire it up", speaker_turn="speaker-0")
    assert call.is_call is True
    assert call.item is None
