"""Known-stale timeframe detection for the money path (2026-07-27, follow-up to #811).

#811 fixed the *cause* — the 15m timeframe had no live feed, so every core
pair's 15m array sat frozen at boot while 15m ATR sized live SL/TP geometry,
fed the pre-TP threshold, and drove the BTC regime kill switch.  This module is
the *guard*: it makes the next freeze — a stream that silently stops, a symbol
whose frames dry up — impossible to score on unnoticed.

**Why a guard is not redundant with the fix.**  ``candle_coverage`` (#811) pages
when the feed as a whole goes stale.  It cannot say whether a *particular
signal* was scored on a stale bar, and it does not stop that signal from being
built.  A watchdog that reports a problem after the geometry has already shipped
is a detector, not a guard.

**Refusing, not clamping.**  Where a timeframe is known-stale, the honest answer
is to withhold its indicators, not to hand a consumer an old number that looks
current.  Every consumer of 15m already owns a written fallback for *absent*
15m — MOVER_TREND_PULLBACK falls to 5m ATR (``scalp.py``), QCB falls to the
legacy 5m compression check, ``pre_tp_stamping.resolve_pre_tp_threshold``
returns the ``"static"`` source when ``atr_val <= 0``.  So refusal routes into
paths that already exist and are already tested, rather than inventing one.

**Unknown is not stale — deliberately asymmetric.**  ``last_kline_age_seconds``
returns ``None`` when a (symbol, timeframe) has never been stamped: a restored
snapshot, a fresh bucket, a test stub.  Monitoring may treat that as
not-fresh and page (it does — see the ``candle_coverage`` probe).  The money
path must not: refusing on a missing stamp would degrade every pair's geometry
after a snapshot restore, which is a worse failure than the one being guarded.
So this module refuses **only on a positive age above the bound**.

**Dark-first (CLAUDE.md § Project Phase).**  Two flags, and they are not the
same flag.  Measurement — the counters below — is ON from the moment this
ships and is visible in ops through the ``stale_tf_scoring`` liveness probe.
The *user-visible effect*, withholding indicators from a live evaluator, is
gated on ``STALE_TF_REFUSE_ENABLED`` and ships **false**: it changes what the
money path computes, so it is activated only after the owner has read a real
window of measurement showing what it would have withheld.

Cost: ``last_kline_age_seconds`` is an in-memory dict lookup.  No network, no
Firestore, nothing added to a hot loop but two dict reads per scanned symbol.
"""
from __future__ import annotations

import threading
from typing import Any, Dict, Optional

from src.utils import get_logger

log = get_logger("data_freshness")

# Timeframes whose staleness reaches the money path.  15m is the one that
# actually froze; the rest are here because the same argument applies to any
# timeframe an evaluator sizes geometry from, and a list is cheaper to extend
# than a special case.  1d/1w are excluded on purpose — they are LevelBook
# seeding data refreshed on the seed path, not from the tape.
GUARDED_TIMEFRAMES: tuple[str, ...] = ("15m",)

_counts: Dict[str, int] = {}
_last: Dict[str, Any] = {}
_lock = threading.Lock()


def _bump(key: str, detail: Optional[Dict[str, Any]] = None) -> None:
    with _lock:
        _counts[key] = _counts.get(key, 0) + 1
        if detail is not None:
            _last[key] = detail


def snapshot() -> Dict[str, Any]:
    """Pure read of the staleness counters (safe to call from a probe)."""
    with _lock:
        return {"counts": dict(_counts), "last": dict(_last)}


def reset() -> None:
    """Test hook — the counters are process-lifetime and module-global."""
    with _lock:
        _counts.clear()
        _last.clear()


def timeframe_age_seconds(store: Any, symbol: str, timeframe: str) -> Optional[float]:
    """Age of the newest bar the store holds, or ``None`` when unknowable.

    Fail-open by contract: a store that cannot answer (stub, missing method,
    unexpected shape) yields ``None``, which every caller treats as "no
    evidence of staleness" rather than as evidence of freshness.
    """
    try:
        getter = getattr(store, "last_kline_age_seconds", None)
        if getter is None:
            return None
        age = getter(symbol, timeframe)
        return None if age is None else float(age)
    except (TypeError, ValueError, AttributeError):
        return None
    except Exception as exc:  # pragma: no cover — defensive
        from src import fail_open

        fail_open.record("data_freshness.timeframe_age_seconds", exc)
        return None


def known_stale_age(
    store: Any, symbol: str, timeframe: str, max_age_sec: Optional[float] = None
) -> Optional[float]:
    """Return the age when the series is *known* stale, else ``None``.

    ``None`` covers both "fresh" and "cannot tell" — the two cases the money
    path must treat identically (see the module docstring on asymmetry).
    """
    if max_age_sec is None:
        from config import STALE_TF_MAX_AGE_SEC

        max_age_sec = STALE_TF_MAX_AGE_SEC
    age = timeframe_age_seconds(store, symbol, timeframe)
    if age is None or age <= float(max_age_sec):
        return None
    return age


def refusal_enabled() -> bool:
    """Is the user-visible half armed?  Default false — dark-first."""
    try:
        from src import runtime_tunables as _rt

        override = _rt.get("stale_tf_refuse_enabled")
        if override is not None:
            return bool(override)
    except Exception:  # pragma: no cover — tunables are optional
        pass
    from config import STALE_TF_REFUSE_ENABLED

    return bool(STALE_TF_REFUSE_ENABLED)


def audit_indicators(
    *,
    store: Any,
    symbol: str,
    indicators: Dict[str, dict],
    timeframes: tuple[str, ...] = GUARDED_TIMEFRAMES,
    max_age_sec: Optional[float] = None,
) -> Dict[str, dict]:
    """Measure staleness for *symbol*; withhold stale timeframes only when armed.

    Always counts.  Returns ``indicators`` unchanged while the refusal flag is
    off, so the measurement runs live against the real scan path without
    touching a single signal — which is the only way the eventual activation
    decision can be made on data rather than on argument.
    """
    stale: Dict[str, float] = {}
    for tf in timeframes:
        if tf not in indicators:
            continue
        age = known_stale_age(store, symbol, tf, max_age_sec)
        if age is not None:
            stale[tf] = age
    if not stale:
        return indicators

    armed = refusal_enabled()
    for tf, age in stale.items():
        _bump(
            f"scoring:{tf}",
            {"symbol": symbol, "age_sec": round(age, 1), "withheld": armed},
        )
        if armed:
            _bump(f"withheld:{tf}")
    log.warning(
        "stale timeframe at scoring time: {} {} (withheld={})",
        symbol,
        {tf: round(age) for tf, age in stale.items()},
        armed,
    )
    if not armed:
        return indicators
    return {tf: ind for tf, ind in indicators.items() if tf not in stale}


def gate_should_skip(store: Any, symbol: str, timeframe: str, gate: str) -> bool:
    """Should a gate decline to rule because its input is known-stale?

    Same two-flag shape: the refusal is counted whether or not it is applied,
    so the ops surface shows how often the gate *would have* declined before
    anyone changes what it does.  A gate that rules on a frozen window is not
    failing open or closed — it is repeating a verdict from whenever the data
    stopped, which is neither.
    """
    age = known_stale_age(store, symbol, timeframe)
    if age is None:
        return False
    armed = refusal_enabled()
    _bump(
        f"gate:{gate}",
        {"symbol": symbol, "timeframe": timeframe, "age_sec": round(age, 1), "skipped": armed},
    )
    return armed
