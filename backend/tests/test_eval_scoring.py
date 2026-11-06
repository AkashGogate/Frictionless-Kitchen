"""Proves eval/run_eval.py's scorer actually detects failures, not just passes
cleanly on the happy path — ponytail's bar for non-trivial logic."""
from eval.run_eval import _score


def test_perfect_match_scores_clean():
    expected = [{"text": "fire two salmon on the grill", "item": "salmon", "quantity": 2, "station": "grill"}]
    utterances = [("speaker-0", "fire two salmon on the grill")]
    r = _score("t", "mock", 0.0, expected, utterances)
    assert r.matched_expected == 1
    assert r.missed_calls == 0
    assert r.false_triggers == 0


def test_misheard_quantity_counts_as_missed():
    expected = [{"text": "fire two salmon on the grill", "item": "salmon", "quantity": 2, "station": "grill"}]
    utterances = [("speaker-0", "fire one salmon on the grill")]  # STT misheard "two" as "one"
    r = _score("t", "mock", 0.0, expected, utterances)
    assert r.missed_calls == 1
    assert r.matched_expected == 0


def test_spurious_extra_call_counts_as_false_trigger():
    expected = [{"text": "fire two salmon on the grill", "item": "salmon", "quantity": 2, "station": "grill"}]
    utterances = [
        ("speaker-0", "fire two salmon on the grill"),
        ("speaker-1", "fire one burger on the grill"),  # hallucinated/misattributed extra call
    ]
    r = _score("t", "mock", 0.0, expected, utterances)
    assert r.matched_expected == 1
    assert r.false_triggers == 1


def test_chatter_wrongly_parsed_as_call_is_not_a_false_trigger_if_expected_present():
    expected = [{"text": "background noise", "item": None, "quantity": 0, "station": None, "is_call": False}]
    utterances = [("speaker-0", "background noise")]  # parse_call will mark this non-call text as not a call
    r = _score("t", "mock", 0.0, expected, utterances)
    assert r.matched_expected == 1
    assert r.false_triggers == 0
