"""Every gate in `Scanner._prepare_signal` must be measurable.

WHY (2026-10-23, gate audit). Sixteen hard rejects in `_prepare_signal` called
neither `_stamp_suppressed` nor `_stamp_prescoring_suppressed`: the MTF gate,
the longs 15m-regime gate, the counter-trend mover block, the CT macro gates,
the risk plan, the correlated-exposure cap, the composite-score floor, the
stat filter and the SMC / trend hard gates among them. So the Suppression
Quality Audit could not say whether any of them saved money or cost it, while
it ranked the gates that did stamp. The scan loop also dropped arbitration
losers and global-cooldown skips with only a DEBUG line, and seven `except`
blocks swallowed errors without `fail_open.record`.

Derived from the source, not listed: a new gate added tomorrow fails here until
it stamps.
"""
from __future__ import annotations

import inspect

from src.scanner import Scanner

# A reject is exempt only when there is no candidate to stamp.
_NO_CANDIDATE_MARKERS = (
    "eval error for",   # the evaluator raised; no signal exists
    "if sig is None:",  # the evaluator returned nothing
)


def _source_lines() -> list[str]:
    return inspect.getsource(Scanner._prepare_signal).split("\n")


def test_every_reject_in_prepare_signal_is_stamped():
    lines = _source_lines()
    prev = 0
    unstamped = []
    for i, line in enumerate(lines):
        if "return _reject(" not in line:
            continue
        block = "\n".join(lines[prev:i])
        prev = i + 1
        if "_stamp_suppressed" in block or "_stamp_prescoring_suppressed" in block:
            continue
        tail = "\n".join(lines[max(0, i - 3):i])
        if any(m in tail for m in _NO_CANDIDATE_MARKERS):
            continue
        unstamped.append(f"line +{i}: {line.strip()}")
    assert not unstamped, (
        "gate(s) in _prepare_signal reject without stamping the candidate — the "
        "suppression audit cannot measure them:\n" + "\n".join(unstamped)
    )


def test_no_except_in_prepare_signal_swallows_silently():
    lines = _source_lines()
    silent = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not (stripped.startswith("except") and "Exception" in stripped):
            continue
        indent = len(line) - len(line.lstrip())
        body = []
        for nxt in lines[i + 1:]:
            if nxt.strip() and len(nxt) - len(nxt.lstrip()) <= indent:
                break
            body.append(nxt)
        text = "\n".join(body)
        if not any(k in text for k in ("fail_open.record", "raise", "_suppression_counters")):
            silent.append(f"line +{i}: {stripped}")
    assert not silent, (
        "except block(s) in _prepare_signal neither count nor re-raise:\n"
        + "\n".join(silent)
    )


def test_scan_loop_drops_are_counted():
    """Arbitration losers and global-cooldown skips leave a counter and a stamp."""
    src = inspect.getsource(Scanner._scan_symbol)
    assert "scalp_arbitration_lost:" in src
    assert src.count('"scalp_arbitration")') >= 2  # both the replaced and the rejected candidate
    assert src.count("enqueue_stage:global_cooldown:") >= 2  # scalp and non-scalp branches
