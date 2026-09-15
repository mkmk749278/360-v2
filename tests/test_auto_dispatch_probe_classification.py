"""The auto_dispatch probe must page for faults, not for settings (2026-09-15).

Live evidence: the probe was red for 566 consecutive audit cycles reading
"127 signals fanned out to keyed users with ZERO order attempts for anyone —
every user is being silently skipped", while both keyed users were simply set
to off and paper. Nothing was broken.

That is an alarming caption over a healthy subsystem, and this repo has
already recorded what it costs: a red that can never be anything but red is a
dead instrument — it means nothing, so it gets ignored, on the channel that
also carries real faults. The owner's bot had 36 unread when this was found.

The classification is an ALLOW-LIST so a skip reason added tomorrow keeps the
probe red until somebody classifies it. These tests pin that direction: the
dangerous failure here is a new reason silently muting the blackout check.
"""
from __future__ import annotations

from src.execution.signal_dispatch import (
    _DELIBERATE_SKIPS,
    _classify_skips,
)


def test_the_observed_live_state_is_not_a_fault():
    """mode:off + mode:paper — exactly what the box reported."""
    deliberate, faults = _classify_skips({"mode:off": 127, "mode:paper": 127})
    assert faults == {}
    assert deliberate == {"mode:off": 127, "mode:paper": 127}


def test_the_blackout_signature_is_still_a_fault():
    """The three unreadable worlds #1031 split out must never be excused.

    These are the 2026-09-02 signature: the store goes blind, every user is
    skipped for a reason nobody can see, and the counter looks identical to a
    fleet on paper. Telling them apart is the entire reason this probe exists.
    """
    for reason in ("mode:lookup_failed", "mode:store_cold",
                   "mode:user_store_cold", "mode:no_user_row",
                   "mode:mode_unset", "mode:unknown_value"):
        _, faults = _classify_skips({reason: 5})
        assert reason in faults, f"{reason} must keep the probe red"
        assert reason not in _DELIBERATE_SKIPS


def test_a_fault_mixed_with_settings_still_reads_as_a_fault():
    """One lookup_failed under hundreds of deliberate skips is the case that
    must not be averaged away."""
    deliberate, faults = _classify_skips(
        {"mode:off": 900, "mode:paper": 900, "mode:lookup_failed": 1}
    )
    assert faults == {"mode:lookup_failed": 1}
    assert sum(deliberate.values()) == 1800


def test_an_unknown_reason_defaults_to_fault():
    """A skip path added later must not silently mute the probe."""
    _, faults = _classify_skips({"some_new_gate": 3})
    assert faults == {"some_new_gate": 3}


def test_auto_pause_and_dup_guard_are_faults_not_choices():
    """Both mean a user cannot trade for a reason they did not pick —
    auto_paused is a fleet stuck behind margin rejections, and
    dup_guard_unavailable is a failed read."""
    for reason in ("auto_paused", "dup_guard_unavailable"):
        _, faults = _classify_skips({reason: 9})
        assert reason in faults


def test_every_deliberate_reason_is_one_the_dispatcher_can_emit():
    """The allow-list must not drift from the reasons that actually exist.

    Derived from the dispatcher's own source rather than restated, so a
    renamed counter fails here instead of quietly re-reddening the probe.
    """
    import ast
    from pathlib import Path

    src = Path("src/execution/signal_dispatch.py").read_text()
    tree = ast.parse(src)
    emitted = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_note"):
            continue
        arg = node.args[0] if node.args else None
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            emitted.add(arg.value.removeprefix("skip:"))
        elif isinstance(arg, ast.JoinedStr):
            # f"skip:mode:{detail}" — the prefix is what we can pin.
            head = arg.values[0]
            if isinstance(head, ast.Constant):
                emitted.add(head.value.removeprefix("skip:").rstrip(":"))
    for reason in _DELIBERATE_SKIPS:
        root = reason.split(":", 1)[0]
        assert reason in emitted or root in emitted, (
            f"{reason!r} is allow-listed but the dispatcher never emits it — "
            "the list has drifted from the code."
        )


# ------------------------------------------------- the probe, end to end
# Key names taken from the function's own reads, not guessed: it consumes
# ``fanouts_with_users_total`` / ``fanouts_empty_roster_total`` /
# ``attempts_total``, and treats a state with ``attempts is None`` as a cold
# start that captures a baseline rather than judging.
def _state(attempts=0.0, fan_at_last_attempt=0.0, empty_at_last_roster=0.0):
    return {
        "attempts": attempts,
        "fan_at_last_attempt": fan_at_last_attempt,
        "empty_at_last_roster": empty_at_last_roster,
    }


def test_the_probe_goes_GREEN_on_the_exact_counters_the_box_reported():
    from src.execution.signal_dispatch import auto_dispatch_health_check

    ok, msg = auto_dispatch_health_check(
        _state(),
        {
            "fanouts_with_users_total": 127.0,
            "fanouts_empty_roster_total": 0.0,
            "attempts_total": 0.0,
            "placed_total": 0.0, "skipped_total": 254.0,
            "skip:mode:off": 127.0, "skip:mode:paper": 127.0,
        },
        gap_threshold=3,
    )
    assert ok is True, (
        "566 audit cycles of red over two users choosing off and paper is a "
        "dead instrument, not a finding"
    )
    assert "No user is on live" in msg, (
        "going green must not go silent — nobody on live is a revenue fact"
    )


def test_the_probe_stays_RED_when_one_read_actually_failed():
    from src.execution.signal_dispatch import auto_dispatch_health_check

    ok, msg = auto_dispatch_health_check(
        _state(),
        {
            "fanouts_with_users_total": 127.0,
            "fanouts_empty_roster_total": 0.0,
            "attempts_total": 0.0,
            "placed_total": 0.0, "skipped_total": 255.0,
            "skip:mode:off": 127.0, "skip:mode:paper": 127.0,
            "skip:mode:lookup_failed": 1.0,
        },
        gap_threshold=3,
    )
    assert ok is False
    assert "lookup_failed" in msg, "the fault must LEAD, not be buried by count"
    assert msg.index("lookup_failed") < msg.index("by choice")


def test_an_empty_roster_is_still_its_own_alarm():
    """The blackout where list_active_uids returns [] must be untouched by
    this change — a different branch, a different fault."""
    from src.execution.signal_dispatch import auto_dispatch_health_check

    ok, msg = auto_dispatch_health_check(
        _state(),
        {
            "fanouts_with_users_total": 0.0,
            "fanouts_empty_roster_total": 50.0,
            "attempts_total": 0.0,
        },
        gap_threshold=3,
    )
    assert ok is False and "EMPTY" in msg
