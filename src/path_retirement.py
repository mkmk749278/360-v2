"""Retire a (setup_class, side) from the live feed — keep measuring it.

Owner-approved 2026-08-13 off the **delivered** book, which matters: every
earlier analysis in that session ran on the dark feed, and the dark feed is by
definition the population our gates already suppressed, so its badness is
partly circular. These two retirements are measured on the 412 closed trades
subscribers actually received.

What the evidence was
---------------------

**`MOVER_TREND_PULLBACK` SHORT** — n=86 across 46 distinct symbols,
−0.854% net/trade, symbol-clustered 95% CI **[−1.585, −0.143]**. That is the
only bucket in the whole delivered book whose interval excludes zero.

The obvious alternative explanation was checked and does not hold. "Shorts
lost because the market rose for 30 days" would apply to every path; instead
**every other path's shorts made +0.739% over 53 trades** in the same window,
a difference of −1.593% with CI [−2.689, −0.594] and 100% of resamples
agreeing. And MVRTP's shorts lose on their own home turf — −0.961% in
TRENDING_DOWN, −1.515% in RANGING. It is the mechanism, not the tape.

The mechanism is legible once stated: MVRTP takes its direction from the MA
stack, so on a crashed alt it shorts the *bounce* in a downtrend, entering at
the 1st–8th percentile of the 24h range — selling near the low of a finished
dump, straight into the squeeze.

**`VOLUME_SURGE_BREAKOUT`** — 11 trades, **zero winners**, 11 distinct symbols,
−17.9% net. At the book's 34.5% win rate P(0 of 11) = 0.0096. Thin, and the
absence of symbol concentration is what makes it worth acting on rather than
watching.

Why divert rather than delete
-----------------------------

A retired path keeps stamping into the dark lane, so the decision can be
re-read on fresh evidence instead of frozen at the moment it was taken. That
is the `cohort_edge` lesson: a gate whose evidence arrives only from what it
lets through can never release, and a path deleted outright can never earn its
way back. Retirement here is a **routing** decision, not a verdict.

Two states, and they are not the same
-------------------------------------

* **dark lane ON** — the row is diverted, measured, and visible in ops.
* **dark lane OFF** — nothing is delivered either way (which is the point),
  but the measurement is lost. That is counted separately and named, because
  "retired and still being measured" and "retired and now invisible" support
  opposite readings of the same panel.

Cost: two string comparisons per enqueued candidate. No new I/O.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

from src import fail_open
from src.utils import get_logger

log = get_logger("path_retirement")

#: Wildcard side — the whole path is retired, both directions.
ANY_SIDE = "*"

#: The retirements the owner signed off, with the evidence in the docstring
#: above. A default rather than a hardcode: `RETIRED_PATHS` overrides it from
#: ops at runtime, so re-arming a path never needs a deploy.
DEFAULT_RETIRED: Tuple[Tuple[str, str], ...] = (
    ("MOVER_TREND_PULLBACK", "SHORT"),
    ("VOLUME_SURGE_BREAKOUT", ANY_SIDE),
)

#: Master switch. Default **ON**, unlike most money-path flags in this repo,
#: and the exception is deliberate: the owner signed this off on measured
#: delivered-book evidence rather than it being shipped ahead of a decision.
#: Turning it off restores today's behaviour exactly.
_ENABLED_DEFAULT = os.getenv("PATH_RETIREMENT_ENABLED", "true").strip().lower() in {
    "1", "true", "yes", "on",
}


def _parse(spec: str) -> List[Tuple[str, str]]:
    """``"MVRTP:SHORT, VSB:*"`` → ``[("MVRTP","SHORT"), ("VSB","*")]``.

    A malformed entry is skipped and counted rather than raising: a bad string
    in a runtime tunable must not be able to stop the scanner, and it must not
    silently retire something nobody named either.
    """
    out: List[Tuple[str, str]] = []
    for chunk in str(spec or "").replace("\n", ",").split(","):
        tok = chunk.strip()
        if not tok:
            continue
        if ":" in tok:
            setup, side = tok.split(":", 1)
        else:
            setup, side = tok, ANY_SIDE
        setup = setup.strip().upper()
        side = (side.strip().upper() or ANY_SIDE)
        if not setup:
            continue
        if side not in ("LONG", "SHORT", ANY_SIDE):
            log.warning("path_retirement: ignoring unparseable side in {!r}", tok)
            continue
        out.append((setup, side))
    return out


def _configured() -> List[Tuple[str, str]]:
    """The live retirement list.

    Read from the runtime tunable so ops can re-arm a path without a deploy,
    falling back to the signed-off default. An **empty string is a real
    value** meaning "retire nothing" — it is how the owner turns the whole
    thing off from a form field, and it must not be confused with "unset".
    """
    try:
        from src import runtime_tunables as _rt

        raw = _rt.get("retired_paths")
        if raw is not None:
            return _parse(str(raw))
    except Exception as exc:
        fail_open.record("path_retirement.configured", exc)
    return list(DEFAULT_RETIRED)


def enabled() -> bool:
    """Is the retirement gate acting at all?

    Fail-OPEN: any error answers True only if the boot default says so. An
    unreadable tunable must not silently start delivering a path the owner
    retired, so the error path keeps the compiled-in default rather than
    inventing permission.
    """
    try:
        from src import runtime_tunables as _rt

        val = _rt.get("path_retirement_enabled")
        if val is not None:
            return bool(val)
    except Exception as exc:
        fail_open.record("path_retirement.enabled", exc)
    return _ENABLED_DEFAULT


def reason_for(setup_class: Any, side: Any) -> Optional[str]:
    """Why this candidate is retired, or ``None`` if it is not.

    Returns a *reason token* rather than a bool so the dark ledger, the
    suppression audit and the ops panel all name the same thing — a counter
    with no cause is what this repo keeps paying for.
    """
    try:
        if not enabled():
            return None
        setup = str(setup_class or "").strip().upper()
        if not setup:
            # An unclassified candidate is NOT retired. Absence of a label is
            # not evidence about the path, and fail-closed here would silently
            # retire every future evaluator that forgot its setup_class.
            return None
        want = str(side or "").strip().upper()
        if want.startswith("DIRECTION."):
            want = want.split(".", 1)[1]
        for r_setup, r_side in _configured():
            if r_setup != setup:
                continue
            if r_side == ANY_SIDE or r_side == want:
                return f"retired:{setup}:{r_side}"
        return None
    except Exception as exc:
        fail_open.record("path_retirement.reason_for", exc)
        return None


def snapshot() -> Dict[str, Any]:
    """What ops renders. One writer, one reader.

    Publishes the parsed list rather than the raw string, so a malformed entry
    shows up as absent here instead of reading as armed.
    """
    try:
        conf = _configured()
        return {
            "enabled": enabled(),
            "retired": [{"setup_class": s, "side": d} for s, d in conf],
            "count": len(conf),
            "default": [{"setup_class": s, "side": d} for s, d in DEFAULT_RETIRED],
            "is_default": sorted(conf) == sorted(DEFAULT_RETIRED),
        }
    except Exception as exc:  # pragma: no cover - defensive
        fail_open.record("path_retirement.snapshot", exc)
        return {"error": str(exc)}
