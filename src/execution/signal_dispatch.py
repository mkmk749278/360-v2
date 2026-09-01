"""Signal → server-side FSM bridge.

When the engine's signal router dispatches a signal (post-gate-chain,
post-Telegram-send), this module fans the signal out to every user
who has a connected Binance key — calling
:func:`src.execution.position_fsm.place_signal` per user so the
server-side execution stack actually fires the trade.

Without this bridge, the entire 14-PR roadmap's order-placement
machinery sits idle: PositionWorker subscribes to fills, FSM
transitions through states, mark-price feed watches for pre-TP,
reconciler diffs against Binance — but no orders are ever placed,
because nothing calls ``place_signal``.

Design choices for v1
---------------------

* **Position sizing**: fixed $500 notional per signal per user.
  Matches the B18 default per-user position cap from #431, so the
  ``assert_position_cap`` tripwire is satisfied by construction.
  A future PR introduces per-user position-size overrides via a
  ``users/{uid}/settings/auto_trade`` Firestore doc.

* **TP qty split**: 30% / 40% / 30% across TP1 / TP2 / TP3.  Matches
  the doctrine of "bank early on the bonus tail" — the residual
  after pre-TP (50%) is enough to fill TP1 (30%) + TP2 (40%) + TP3
  (30%) = 100% which slightly over-commits if pre-TP fires.
  ``_apply_pretp_fill`` (PR-7) cancels TP2 + TP3 on pre-TP fill so
  the residual rides toward TP1 only, which resolves the over-
  commit cleanly.  See ``OWNER_BRIEF §3.2a``.

* **Per-user dispatch**: fan-out via asyncio.gather with
  ``return_exceptions=True`` so one user's failure (e.g. KMS
  outage, Binance permission drift) doesn't block other users.

* **User-roster freshness**: 30-second cache on the
  ``list_active_uids`` query.  Newly-connected user waits up to
  30s for the engine to notice them on the next signal.  Tradeoff
  documented; future work could push-invalidate via Firestore
  trigger.

This module does NOT decide WHEN to fire — it's called by
:mod:`src.signal_router` after the gate chain accepts a signal +
the Telegram dispatch completes.  See :func:`dispatch_signal_to_active_users`.
"""

from __future__ import annotations

import asyncio
import os
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.execution import position_state as _ps
from src.utils import get_logger

log = get_logger("execution.signal_dispatch")


# Per-user notional cap.  Matches B18 default — using the cap as
# the default sizing means ``assert_position_cap`` is satisfied
# without per-user lookup.  A future PR adds user-configurable
# overrides up to the policy floor ($2000).
_DEFAULT_NOTIONAL_USD = 500.0

# Auto-pause threshold for consecutive ``-2019 Margin is insufficient``
# rejections (2026-05-24). After this many in a row for a single user,
# we stop dispatching to them and mark their auto-trade row with
# ``paused_reason='insufficient_margin'`` so the app can show the
# "wallet empty — top up + resume" banner. Resets to zero on the next
# successful place for that user, OR on any reject reason OTHER than
# -2019 (since the user clearly engaged Binance but failed for a
# different reason — wallet emptiness isn't the persistent state).
#
# Threshold of 3 chosen so a brief funding gap during the signal-fanout
# window doesn't pause the user; sustained emptiness does. Env-
# overridable per B8.
_INSUFFICIENT_MARGIN_PAUSE_THRESHOLD: int = max(
    1, int(os.getenv("INSUFFICIENT_MARGIN_PAUSE_THRESHOLD", "3"))
)

# Binance Futures rejection code we trip on. Stable numeric contract
# (see Binance Futures API error codes docs) — same constant the app
# uses for its plain-English translation in
# ``server_side_execution_models.dart::DispatchEventTranslation``.
_BINANCE_INSUFFICIENT_MARGIN_CODE = -2019

# Per-user consecutive-reject counter. Process-local — survives the
# fanout, gets reset on any successful place. On engine restart the
# counter resets and we re-pause if the wallet is still empty, which
# is the correct conservative default.
_consec_insufficient_margin: Dict[str, int] = defaultdict(int)

# TP qty split — sums to 100%.  Sourced from config (Session 34, 2026-06-24):
# the engine default is TP1-full (TP1=1.0, TP2=TP3=0.0) so the whole position
# closes at TP1 against a fixed SL — no pre-TP banking, no invalidation — which
# the Profit-Lab on 494 live signals showed beats the engine's real exits by
# +19.14%.  Env-overridable via TP{1,2,3}_CLOSE_FRACTION to restore a ladder.
# Read lazily in ``_compute_quantities`` so tests can monkeypatch config.
# FSM skips placement for any leg with qty <= 0; the last active leg absorbs
# the rounding residual.

# Entry regimes that position_fsm._regime_exit_path routes to the CANCEL exit
# path (bank pre-TP, market-close the residual immediately).  Used by the
# session-19 full-grab fee optimisation.  Counter-trend 5m / 15m-not-
# confirming cases also route to CANCEL but can't be detected at dispatch
# without re-deriving the full FSM logic; RANGING/QUIET are the dominant
# CANCEL-bound cases (~76% of cycles) and are unambiguous from regime_label.
#: Every ``Position`` attribute holding the algo id of an order that PROTECTS or
#: EXITS the position, and which therefore has to come down when the position
#: does.  **Derived from the dataclass, not typed out**, and that is the whole
#: point of it existing.
#:
#: The two close paths below each carried a hand-written five-name tuple
#: (``sl_order_id, sl_be_order_id, tp1..tp3``).  #908 added a sixth protective
#: order — the trail governor's ``trail_stop_order_id`` — and joined neither
#: list, so a governed position's stop survived every close path in the engine:
#: PROMUSDT closed 2026-08-11 10:16:51 with its reduce-only stop still resting
#: 28 minutes later, where it would have fired against whatever position was
#: opened on that symbol next.  Binance does not retire these for us (see
#: ``order_placer.place_stop_loss`` — the auto-cancel claim was borrowed from a
#: different order type and is false for a CONDITIONAL ``STOP_MARKET``).
#:
#: A list of names excludes exactly the orders somebody already thought of and
#: is silent by construction on the next one — the ``is_tradfi_perp`` rule, at
#: the cleanup layer.  So it is no longer a list: ``position_state`` DERIVES it
#: from the dataclass's own fields and both this module and ``position_fsm``
#: read that one tuple.  A test asserting a hand-kept copy against the
#: dataclass catches the drift; not keeping the copy is what prevents it.
_PROTECTIVE_ORDER_ATTRS: Tuple[str, ...] = _ps.PROTECTIVE_ORDER_ATTRS

_CANCEL_BOUND_REGIMES: frozenset = frozenset({"RANGING", "QUIET"})

# Entry regimes where pre-TP is suppressed when TRENDING_PRETP_SUPPRESSED
# is enabled.  In these regimes the position thesis is to ride the trend —
# banking 50% at +0.35% caps the runner and leaves 50% exposed to the same
# underlying risk with no upside.
_TRENDING_REGIMES: frozenset = frozenset({"TRENDING_UP", "TRENDING_DOWN"})


def _shadow_telemetry_on() -> bool:
    """Whether dark-flag shadow telemetry is enabled (lazy config read).

    Lazy import keeps the flag monkeypatchable in tests via
    ``config.DARK_FLAG_SHADOW_TELEMETRY`` and lets an operator flip it at
    runtime via the env var without reimporting this module.
    """
    from config import DARK_FLAG_SHADOW_TELEMETRY as _flag
    return bool(_flag)


def _trending_pretp_would_suppress(grab_fraction: float, regime_label: Optional[str]) -> bool:
    """Flag-independent predicate: would TRENDING pre-TP suppression apply here?

    Mirrors the gating condition of :func:`_apply_trending_pretp_suppress`
    minus the ``TRENDING_PRETP_SUPPRESSED`` flag check.  Used both by the
    apply function and by the shadow-telemetry path, so "would fire" is
    counted from the exact same predicate that drives the real behaviour.
    """
    return grab_fraction > 0 and (regime_label or "").upper() in _TRENDING_REGIMES


def _apply_trending_pretp_suppress(grab_fraction: float, regime_label: Optional[str]) -> float:
    """Return ``0.0`` (skip pre-TP) when the TRENDING suppression applies.

    In TRENDING_UP/DOWN entry regimes the position thesis is to ride the
    trend.  Banking 50% of the position at +0.35% (the pre-TP LIMIT) caps
    the runner while leaving the residual exposed to the same underlying risk
    with no upside.  Binance realized data (session 20 analysis) shows >40min
    TRENDING holds net +$1.049 at 67% win rate vs <40min holds at -$0.492 /
    39% win — suppressing pre-TP lets those runners develop.

    Pure function so the decision is unit-testable without the full dispatch
    harness.  See ``config.TRENDING_PRETP_SUPPRESSED``.
    """
    from config import TRENDING_PRETP_SUPPRESSED as _flag
    if _flag and _trending_pretp_would_suppress(grab_fraction, regime_label):
        return 0.0
    return grab_fraction


def _would_fsm_trail(
    regime_5m: Optional[str], regime_15m: Optional[str], direction: str
) -> bool:
    """Mirror of ``position_fsm._select_exit_path`` returning True iff a pre-TP
    fill would route to the TRAILING runner path (keep TP2 live + ATR trail).

    Kept in lock-step with the FSM predicate so dispatch only applies the
    trend-runner profile (bank small + later) when the FSM will actually run a
    trail — otherwise we'd bank a 30% partial and then CANCEL-close the residual,
    which is strictly worse than the default.  A unit test asserts the two stay
    aligned.  VOLATILE routes to its own (tighten) path, not the trail.
    """
    r5 = (regime_5m or "").upper()
    r15 = (regime_15m or "").upper()
    side = (direction or "").upper()
    if r5 not in ("TRENDING_UP", "TRENDING_DOWN"):
        return False
    trade_long = side == "LONG"
    if (r5 == "TRENDING_UP") != trade_long:
        return False  # 5m counter-trend
    if r15 not in ("TRENDING_UP", "TRENDING_DOWN"):
        return False  # 15m not trending — FSM declines the trail
    if (r15 == "TRENDING_UP") != trade_long:
        return False  # 15m counter to trade direction
    return True


def _apply_regime_trend_runner(
    grab_fraction: float,
    pretp_threshold: float,
    sl_dist_pct: float,
    regime_5m: Optional[str],
    regime_15m: Optional[str],
    direction: str,
) -> tuple[float, float, bool]:
    """Regime-per-exit runner profile for trend-aligned signals (§3.2b).

    When enabled and the FSM would trail this position, bank a SMALL partial
    (``REGIME_TREND_GRAB_FRACTION``, 30%) at a RAISED pre-TP threshold floored at
    ``sl_dist_pct × REGIME_TREND_PRETP_R_FACTOR`` (1.0R), then let the residual
    ride the trail.  Returns ``(grab, threshold, applied)``.  No-op (returns the
    inputs unchanged, applied=False) when disabled, when pre-TP is already
    suppressed (``grab_fraction <= 0`` — respects entry-only / user-OFF /
    allowlist), or when the FSM would not trail.  Pure → unit-testable.
    """
    from config import REGIME_PER_EXIT_ENABLED as _enabled
    from config import REGIME_TREND_PRETP_R_FACTOR as _r_factor
    from config import REGIME_TREND_GRAB_FRACTION as _grab
    if not _enabled or grab_fraction <= 0:
        return grab_fraction, pretp_threshold, False
    if not _would_fsm_trail(regime_5m, regime_15m, direction):
        return grab_fraction, pretp_threshold, False
    raised = pretp_threshold
    if sl_dist_pct > 0:
        raised = max(pretp_threshold, sl_dist_pct * _r_factor)
    return float(_grab), float(raised), True


def _cancel_fullgrab_would_apply(grab_fraction: float, regime_label: Optional[str]) -> bool:
    """Flag-independent predicate: would the CANCEL-path full-grab apply here?

    Mirrors the gating condition of :func:`_apply_cancel_fullgrab` minus the
    ``PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED`` flag check.  Shared by the
    apply function and the shadow-telemetry path.
    """
    return grab_fraction > 0 and (regime_label or "").upper() in _CANCEL_BOUND_REGIMES


def _apply_cancel_fullgrab(grab_fraction: float, regime_label: Optional[str]) -> float:
    """Return ``1.0`` (full grab) when the CANCEL-path fee optimisation applies
    to this position, else ``grab_fraction`` unchanged.

    Applies only when the flag is on, a pre-TP would otherwise fire
    (``grab_fraction > 0``), and the entry regime is one the FSM routes to the
    CANCEL exit path.  Pure function so the decision is unit-testable without
    the full dispatch harness.  See ``config.PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED``.
    """
    from config import PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED as _flag
    if _flag and _cancel_fullgrab_would_apply(grab_fraction, regime_label):
        return 1.0
    return grab_fraction

# User-roster cache TTL.  30s is the published SLA for "newly-
# connected user starts receiving signals."  Reduces Firestore
# load while keeping the operator-visible behaviour predictable.
_ACTIVE_UIDS_TTL_S = 30.0


@dataclass
class _CachedUids:
    uids: List[str]
    fetched_at_monotonic: float


_cache: Optional[_CachedUids] = None


def _active_uids() -> List[str]:
    """Return the cached list of users with a connected Binance key.
    Refreshes via Firestore at most once per :data:`_ACTIVE_UIDS_TTL_S`.

    Cache miss / expiry falls back to a fresh
    :func:`firestore_keystore.list_active_uids` query.  Keystore
    not-initialised returns an empty list, which makes this
    function return an empty list — signal dispatch then no-ops
    cleanly (signal still goes to Telegram via the legacy path).
    """
    global _cache
    from src.security import firestore_keystore as _ks

    now = time.monotonic()
    if _cache is not None and (now - _cache.fetched_at_monotonic) < _ACTIVE_UIDS_TTL_S:
        return _cache.uids
    uids = _ks.list_active_uids()
    _cache = _CachedUids(uids=list(uids), fetched_at_monotonic=now)
    return _cache.uids


def reset_cache_for_test() -> None:
    """Test-only — drop the active-uids cache."""
    global _cache
    _cache = None
    _TIER_CACHE.clear()
    _FANOUT_TOTALS.clear()


# ---------------------------------------------------------------------------
# Fan-out outcome telemetry (2026-07-18)
# ---------------------------------------------------------------------------
# Why this exists: every per-user gate in ``_one_user`` that skips BEFORE a
# dispatch_log row (mode, tier, auto-pause, path/regime preference) is
# deliberately silent per-user — but that made a *fleet-wide* silent-skip
# blackout invisible: signals kept emitting, the fan-out kept running, and
# zero users ever reached an order attempt, with nothing counting it and
# nothing paging (2026-07-18 owner report: "auto trade not happening to
# anyone", undiagnosable without VPS log access).  These monotonic
# per-process counters cost nothing on the hot path (dict increments), feed
# ONE summary log line per fan-out, and drive the ``auto_dispatch``
# feature-liveness probe via :func:`auto_dispatch_health_check`.

_FANOUT_TOTALS: Dict[str, float] = defaultdict(float)

# Fan-outs (to a non-empty roster) tolerated with zero order attempts across
# ALL users before the liveness probe flags a blackout.  ~15 paid signals/day
# means 5 ≈ several hours of paid signals nobody's account even attempted.
_AUTO_DISPATCH_GAP_THRESHOLD: int = max(
    1, int(os.getenv("AUTO_DISPATCH_GAP_THRESHOLD", "5"))
)


def dispatch_totals() -> Dict[str, float]:
    """Snapshot of the monotonic fan-out counters (auto path only).

    Keys: ``fanouts_total`` (auto fan-outs invoked),
    ``fanouts_with_users_total`` (… that saw a non-empty keyed roster),
    ``attempts_total`` (per-user dispatches that reached the order path —
    placed + rejected, i.e. everything that writes a dispatch_log row),
    ``placed_total``, ``skipped_total``, plus per-reason ``skip:*`` /
    ``rejected:*`` breakdowns.
    """
    return dict(_FANOUT_TOTALS)


def auto_dispatch_health_check(
    state: Dict[str, Optional[float]],
    totals: Optional[Dict[str, float]] = None,
    *,
    gap_threshold: Optional[int] = None,
) -> Tuple[bool, str]:
    """Pure predicate for the ``auto_dispatch`` feature-liveness probe.

    Violates when ≥ ``gap_threshold`` auto fan-outs have reached a
    non-empty keyed-user roster since the last order *attempt* anywhere in
    the fleet — the signature of every user being silently skipped (fleet-
    wide tier lapse, mode-resolution breakage, preference wipe…).  Signals
    being sparse is fine: the gap is measured in fan-outs, not cycles, so a
    quiet tape can never page and a blackout can't hide between cycles.

    ``state`` is caller-owned mutable memory across probe cycles (keys:
    ``attempts``, ``fan_at_last_attempt``).  Pure in the ops-detector sense:
    all inputs are parameters, no hidden I/O, so tests drive it with plain
    dicts.
    """
    t = totals if totals is not None else dispatch_totals()
    threshold = (
        _AUTO_DISPATCH_GAP_THRESHOLD if gap_threshold is None else gap_threshold
    )
    fan = float(t.get("fanouts_with_users_total", 0.0))
    fan_empty = float(t.get("fanouts_empty_roster_total", 0.0))
    attempts = float(t.get("attempts_total", 0.0))

    # Watermark resets: first cycle, or a process restart zeroed the
    # monotonic counters below a stored watermark.
    restarted = (
        attempts < float(state.get("attempts") or 0.0)
        or fan < float(state.get("fan_at_last_attempt") or 0.0)
        or fan_empty < float(state.get("empty_at_last_roster") or 0.0)
    )
    if state.get("attempts") is None or restarted:
        state["attempts"] = attempts
        state["fan_at_last_attempt"] = fan
        state["empty_at_last_roster"] = fan_empty
        return True, "baseline captured"

    # Empty-roster blackout: fan-outs keep resolving ZERO keyed users.
    # ``list_active_uids`` fails soft to [] — a dead keystore otherwise
    # looks identical to "no customers".  Watermark advances whenever a
    # fan-out sees a non-empty roster.
    if fan > float(state["fan_at_last_attempt"] or 0.0) or attempts > float(
        state["attempts"] or 0.0
    ):
        state["empty_at_last_roster"] = fan_empty
    empty_gap = fan_empty - float(state["empty_at_last_roster"] or 0.0)

    # Silent-skip blackout: fan-outs reach keyed users but no user's
    # dispatch ever reaches the order path.  Watermark advances on every
    # order attempt (placed OR rejected).
    if attempts > float(state["attempts"] or 0.0):
        state["fan_at_last_attempt"] = fan
    state["attempts"] = attempts
    skip_gap = fan - float(state["fan_at_last_attempt"] or 0.0)

    if empty_gap >= threshold:
        return False, (
            f"{empty_gap:.0f} consecutive signals fanned out to an EMPTY "
            f"keyed-user roster — keystore offline or list_active_uids "
            f"failing (check engine WARN logs)"
        )
    if skip_gap >= threshold:
        skips = {
            k.removeprefix("skip:"): v
            for k, v in t.items()
            if k.startswith("skip:") and v > 0
        }
        top = ", ".join(
            f"{k}={v:.0f}"
            for k, v in sorted(skips.items(), key=lambda kv: -kv[1])[:4]
        ) or "none recorded"
        return False, (
            f"{skip_gap:.0f} signals fanned out to keyed users with ZERO "
            f"order attempts for anyone — every user is being silently "
            f"skipped; check the fan-out summary log (cumulative skips: "
            f"{top})"
        )
    # Publish the FUNNEL, not just the gap.  Until 2026-08-31 the healthy
    # message carried ``attempts`` and ``fanouts`` and nothing else, so
    # ``placed_total`` / ``skipped_total`` / the per-reason ``skip:*`` and
    # ``rejected:*`` breakdowns — all of them computed on every fan-out —
    # appeared on no surface in either repo, in either state.  "How many of
    # today's signals actually reached Binance, and what stopped the rest"
    # was therefore unanswerable from the one page built to answer it.
    # Note ``skip {skip_gap}`` below is a GAP since the last order attempt,
    # not a count of skips; the cumulative count is ``skipped``, and reading
    # the first as the second is how a fleet of silent skips looks like zero.
    placed = float(t.get("placed_total", 0.0))
    skipped = float(t.get("skipped_total", 0.0))
    reasons = {
        k.split(":", 1)[1]: v
        for k, v in t.items()
        if (k.startswith("skip:") or k.startswith("rejected:")) and v > 0
    }
    top = ", ".join(
        f"{k}={v:.0f}"
        for k, v in sorted(reasons.items(), key=lambda kv: -kv[1])[:4]
    )
    return True, (
        f"placed={placed:.0f} rejected={attempts - placed:.0f} "
        f"skipped={skipped:.0f} over {fan:.0f} fan-out(s) to a keyed roster"
        + (f"; top reasons: {top}" if top else "")
        + f" (gaps: skip {skip_gap:.0f}, empty-roster {empty_gap:.0f}; "
        f"threshold {threshold})"
    )


# ---------------------------------------------------------------------------
# Entitlement (B16 two-tier model) — hands-off auto-execution is AUTO-only
# ---------------------------------------------------------------------------

# uid → (effective_tier, expiry_monotonic).  Small in-process TTL cache so the
# per-signal dispatch gate doesn't hit SQLite for every user on every signal
# (Cost Discipline — mirror the keystore/kill-switch cache pattern).  Tier
# changes are rare (subscription events), so 30s staleness is acceptable: a
# just-subscribed user waits <=30s for their first auto-trade; a just-lapsed
# one keeps it <=30s (RTDN + the read-time expiry check below are the
# authoritative downgrade).
_TIER_CACHE: Dict[str, Tuple[str, float]] = {}
_TIER_CACHE_TTL_S: float = 30.0


def _resolve_user_tier(uid: str) -> str:
    """Resolve a firebase uid → effective subscription tier (expiry-aware).

    Returns ``"free"`` when the user is unknown, their paid window has
    lapsed, or the lookup fails — i.e. **fails closed**: we never run
    hands-off auto-execution for an account we can't confirm is entitled.
    """
    now = time.monotonic()
    cached = _TIER_CACHE.get(uid)
    if cached is not None and cached[1] > now:
        return cached[0]
    tier = "free"
    try:
        from datetime import datetime, timezone

        from src.api import users as _users
        from src.api.auth import can_assist

        store = _users.get_singleton()
        if store is not None:
            user = store.get_by_firebase_uid(uid)
            if user is not None:
                tier = (user.tier or "free").lower()
                # A lapsed paid window downgrades to free at read time
                # (defence-in-depth alongside RTDN expiry events).
                if (
                    can_assist(tier)
                    and user.paid_until is not None
                    and user.paid_until <= datetime.now(timezone.utc)
                ):
                    tier = "free"
    except Exception as exc:  # fail closed — no unpaid auto-execution
        log.warning("signal_dispatch: tier resolve failed uid={}: {}", uid, exc)
        tier = "free"
    _TIER_CACHE[uid] = (tier, now + _TIER_CACHE_TTL_S)
    return tier


def _compute_qty_split(
    symbol: str,
    entry_price: float,
    notional_usd: Optional[float] = None,
) -> Tuple[float, float, float, float]:
    """Return ``(total_qty, tp1_qty, tp2_qty, tp3_qty)`` for a
    ``notional_usd``-notional position on ``symbol`` at the given
    entry price.  ``notional_usd=None`` → use the engine default
    (``_DEFAULT_NOTIONAL_USD``, $500).

    Per-symbol precision enforced via :mod:`symbol_filters`
    (LOT_SIZE.stepSize floor + MIN_NOTIONAL guard).  Without this
    rounding, Binance rejects every order on symbols with stepSize
    ≥ 0.001 (most non-major pairs) with ``code=-1111 "Precision is
    over the maximum defined for this asset"``.

    The total_qty is floored to stepSize.  Each TP leg is also
    floored to stepSize so partial closes don't violate precision.
    TP3 then absorbs the rounding residual so the three TPs sum to
    ≤ total_qty (any micro-residual stays open as dust — closes on
    SL or expiry).

    Defensive: returns all zeros when entry_price <= 0 OR when the
    rounded total_qty fails MIN_NOTIONAL even after a one-stepSize
    snap-up (see snap-up note below).  A doomed order is never fired
    through the FSM + circuit-breaker chain; the caller records a
    "NotionalTooSmall" reject event so the user sees why in the app.

    Snap-up: when the floored qty gives notional < MIN_NOTIONAL, we
    try adding exactly one stepSize.  For a $5 notional at $17.58
    price, stepSize=0.001 → floored qty=0.284 → $4.993 (just below
    Binance's $5 floor). Adding one step → 0.285 × $17.58 = $5.01,
    which clears MIN_NOTIONAL.  The overage above the user's stated
    notional is at most ``entry_price × step_size`` (cents for major
    USDT-M pairs, always < $0.10).
    """
    from src.execution import symbol_filters as _sf

    if entry_price <= 0:
        return (0.0, 0.0, 0.0, 0.0)

    notional = float(notional_usd) if notional_usd and notional_usd > 0 else _DEFAULT_NOTIONAL_USD
    raw_qty = notional / entry_price
    total_qty = _sf.round_qty(symbol, raw_qty)
    if total_qty <= 0:
        return (0.0, 0.0, 0.0, 0.0)
    if not _sf.meets_min_notional(symbol, total_qty, entry_price):
        # Try bumping by one stepSize.  The LOT_SIZE floor often
        # shaves the last cent below MIN_NOTIONAL on small notionals;
        # one step up restores compliance with negligible overshoot.
        sf = _sf.get_filters(symbol)
        if sf is not None and sf.step_size > 0:
            qty_snapped = total_qty + sf.step_size
            if _sf.meets_min_notional(symbol, qty_snapped, entry_price):
                log.info(
                    "signal_dispatch: symbol={} MIN_NOTIONAL snap-up "
                    "{:.8f}→{:.8f} qty (${:.4f}→${:.4f})",
                    symbol, total_qty, qty_snapped,
                    total_qty * entry_price, qty_snapped * entry_price,
                )
                total_qty = qty_snapped
            else:
                log.info(
                    "signal_dispatch: symbol={} qty={:.8f} price={:.8f} "
                    "notional=${:.4f} below MIN_NOTIONAL even after snap-up "
                    "(user notional ${:.2f}) — skipping",
                    symbol, total_qty, entry_price,
                    total_qty * entry_price, notional,
                )
                return (0.0, 0.0, 0.0, 0.0)
        else:
            log.info(
                "signal_dispatch: symbol={} qty={:.8f} price={:.8f} "
                "notional=${:.4f} below MIN_NOTIONAL after LOT_SIZE "
                "rounding, no filter entry for snap-up — skipping",
                symbol, total_qty, entry_price, total_qty * entry_price,
            )
            return (0.0, 0.0, 0.0, 0.0)

    from config import TP1_CLOSE_FRACTION as _TP1_FRACTION
    from config import TP2_CLOSE_FRACTION as _TP2_FRACTION
    from config import TP3_CLOSE_FRACTION as _TP3_FRACTION

    tp1 = _sf.round_qty(symbol, total_qty * _TP1_FRACTION)
    tp2 = _sf.round_qty(symbol, total_qty * _TP2_FRACTION)
    # Rounding residual: the last active TP leg absorbs the dust so
    # tp1+tp2+tp3 == total_qty exactly (Binance rejects non-reconciling
    # order sets).  Engine default TP1=1.0/TP2=0.0/TP3=0.0 → tp1≈total,
    # tp2 absorbs the (near-zero) residual and stays 0, tp3=0.  When TP3 is
    # disabled the residual goes to TP2; otherwise tp3 gets it and the FSM
    # skips any leg whose qty rounds to 0.
    _residual = _sf.round_qty(symbol, total_qty - tp1 - tp2)
    if _TP3_FRACTION <= 0.0:
        tp2 = tp2 + _residual
        tp3 = 0.0
    else:
        tp3 = _residual

    # MIN_NOTIONAL guard on TP legs.  Binance enforces MIN_NOTIONAL
    # on every TAKE_PROFIT_MARKET order with explicit quantity (code
    # -4164 "Order's notional must be no smaller than X").  At $5–$10
    # total notional the 30%/40%/30% legs are $1.50/$2/$1.50 — all
    # below the $5 Binance floor — so every TP order is rejected
    # silently.  When any leg is below MIN_NOTIONAL, consolidate all
    # quantity into tp1 (single-leg full close at TP1 price) and zero
    # out tp2/tp3.  The SL's ``closePosition=true`` backstop is still
    # present; pre-TP partial close fires for the fraction regardless.
    f_check = _sf.get_filters(symbol)
    min_notional = (
        f_check.min_notional
        if f_check is not None and f_check.min_notional > 0
        else 5.0
    )
    if tp1 > 0 and tp1 * entry_price < min_notional:
        # All legs too small — tp1 takes the full position.
        _tp1_leg_notional = tp1 * entry_price
        tp1 = total_qty
        tp2 = 0.0
        tp3 = 0.0
        log.info(
            "signal_dispatch: symbol={} tp legs below MIN_NOTIONAL "
            "(tp1 notional=${:.2f} < ${:.2f}) — consolidating into "
            "single tp1=full-position",
            symbol, _tp1_leg_notional, min_notional,
        )
    elif tp2 > 0 and tp2 * entry_price < min_notional:
        # tp2/tp3 too small — roll everything into tp1.
        tp1 = total_qty
        tp2 = 0.0
        tp3 = 0.0
        log.info(
            "signal_dispatch: symbol={} tp2 leg below MIN_NOTIONAL "
            "(tp2 notional=${:.2f} < ${:.2f}) — consolidating into "
            "single tp1=full-position",
            symbol, tp2 * entry_price, min_notional,
        )
    elif tp3 > 0 and tp3 * entry_price < min_notional:
        # tp3 too small — give its residual to tp1, disable tp3.
        tp1 = _sf.round_qty(symbol, total_qty - tp2)
        tp3 = 0.0
        log.info(
            "signal_dispatch: symbol={} tp3 leg below MIN_NOTIONAL "
            "(tp3 notional=${:.2f} < ${:.2f}) — rolling into tp1",
            symbol, tp3 * entry_price, min_notional,
        )

    return (total_qty, tp1, tp2, tp3)


async def dispatch_signal_to_active_users(
    *,
    signal_id: str,
    symbol: str,
    direction: str,  # "LONG" | "SHORT"
    entry_price: float,
    sl_price: float,
    tp1_price: float,
    tp2_price: float,
    tp3_price: float,
    regime_label: Optional[str] = None,
    regime_label_15m: Optional[str] = None,
    atr_percentile: float = 50.0,
    atr_value: float = 0.0,
    setup_class: Optional[str] = None,
    entry_zone_low: Optional[float] = None,
    entry_zone_high: Optional[float] = None,
    valid_for_minutes: int = 0,
    current_price: float = 0.0,
    risk_scale: float = 1.0,
    _only_uid: Optional[str] = None,
    _manual: bool = False,
    _manual_result: Optional[Dict[str, Any]] = None,
) -> int:
    """Fan a signal out to every active user's server-side FSM.

    Called by :mod:`src.signal_router` after the gate chain
    accepts a signal + the Telegram dispatch completes.  Returns
    the count of users for whom the dispatch SUCCEEDED (entry
    order placed; SL/TP best-effort per PR-6).

    Per-user failures are caught + logged but do NOT block other
    users.  A failure could be: tripwire reject (symbol allowlist,
    rate limit, position cap, global enable flag off), KMS outage,
    Binance key revoked, etc.  Each failure mode is surfaced via
    the typed exceptions from PR-6 + PR-14 wiring.

    When no users have connected a key (cold-deploy or all users
    using the legacy client-side path), this function returns 0
    without touching anything.

    Manual take (owner-approved 2026-07-17): ``_only_uid`` + ``_manual``
    are the internal plumbing for :func:`dispatch_signal_to_uid_manual`
    — a single explicit user instead of the roster, with the mode /
    auto-pause / path-regime preference gates skipped (the user's tap IS
    the consent those gates encode) and the tier gate applied at
    ``can_assist`` instead of ``can_auto``.  Everything downstream —
    per-user sizing, tripwires, ``place_signal``'s safety-gate chain,
    dispatch_log — is byte-identical to the auto path.  ``_manual_result``
    (a caller-owned dict) is filled with the terminal outcome so the API
    can answer the user's request synchronously.  External callers use
    the public wrapper, never these parameters.
    """
    # Lazy import to avoid circular dep: position_fsm imports the
    # signing-service client which imports the engine bootstrap.
    from src.execution import position_fsm as _fsm

    # ── FSM LIMIT-entry shadow (S41, docs/FSM_LIMIT_ENTRY_DESIGN.md) ──
    # Stamp-and-shadow phase of the owner-approved LIMIT-at-zone + TTL
    # entry: while FSM_LIMIT_ENTRY_ENABLED is off, log per real dispatch
    # whether the LIMIT would have filled instantly (dispatch price already
    # inside the zone), rested, or had no zone (market-order semantics).
    # Read this before activation — the expected picture is in_zone for the
    # large majority, with the resting tail matching the signal book's
    # EXPIRED_NO_FILL rate.  Zero behaviour change while dark.
    try:
        from config import (
            FSM_LIMIT_ENTRY_ENABLED as _limit_on,
            FSM_ENTRY_TTL_FALLBACK_MIN as _ttl_fallback,
        )
        if not _limit_on and _shadow_telemetry_on():
            if entry_zone_low is not None and entry_zone_high is not None:
                _px = current_price if current_price > 0 else entry_price
                _in_zone = entry_zone_low <= _px <= entry_zone_high
                _mode = "in_zone" if _in_zone else "would_rest"
            else:
                _mode = "market_semantics"
            log.info(
                "[SHADOW] FSM_LIMIT_ENTRY {} {} {} mode={} zone=[{},{}] "
                "ttl_min={} — MARKET entry placed (flag off)",
                signal_id, symbol, direction, _mode,
                entry_zone_low, entry_zone_high,
                valid_for_minutes or _ttl_fallback,
            )
    except Exception as _sh_exc:  # noqa: BLE001 — shadow must never block dispatch
        log.debug("FSM_LIMIT_ENTRY shadow error (non-blocking): {}", _sh_exc)

    uids = [_only_uid] if _only_uid else _active_uids()
    if not uids:
        # Cold deploy / keystore offline / roster query failing.  Count it:
        # signals flowing while the roster is CONSISTENTLY empty is its own
        # blackout signature (list_active_uids fails soft to [] — without
        # this line a dead keystore looks identical to "no customers").
        _FANOUT_TOTALS["fanouts_total"] += 1
        _FANOUT_TOTALS["fanouts_empty_roster_total"] += 1
        return 0

    _dispatch_source = "manual_take" if _manual else "auto"

    # Per-fan-out outcome tally (fan-out telemetry, 2026-07-18).  One
    # Counter per signal; folded into the module-level monotonic totals
    # after the gather so the summary log + liveness probe can tell
    # "orders attempted and rejected" apart from "everyone silently
    # skipped".  ``skip:*`` = gate skips before any dispatch_log row;
    # ``rejected:*`` / ``placed`` = the order path was reached.
    outcomes: Counter = Counter()

    def _note(reason: str) -> None:
        outcomes[reason] += 1

    def _capture(**fields: Any) -> None:
        """Write the terminal outcome into the caller's result dict
        (manual take only — the auto fan-out passes no sink)."""
        if _manual_result is not None:
            _manual_result.update(fields)

    async def _one_user(uid: str) -> bool:
        # Per-user mode gate (2026-05-24). The pre-2026-05-24 dispatcher
        # fanned every signal to every user with a connected Binance key
        # — ignoring the user's ``mode`` preference entirely. A user who
        # picked "paper" or "off" still got live Binance orders fired
        # against their wallet, surfaced in Recent Activity as -2019
        # rejections when the Futures wallet was empty. Owner-reported
        # 2026-05-24 with screenshots of the Trade > Live tab showing
        # "Mode = live ✗ (Currently PAPER)" alongside -2019 entries —
        # the in-app gate label was honest but the dispatcher wasn't
        # honouring it.
        #
        # Skip silently when mode != 'live': no signing service call,
        # no dispatch_log row, no auto-pause accrual. This makes the
        # "Mode = live" indicator in the armed card the actual gate
        # rather than a status display divorced from behaviour.
        from src.api import user_overrides as _uo
        user_mode = _uo.resolve_user_mode_uid(uid)
        if not _manual and user_mode not in ("live", "both"):
            log.info(
                "signal_dispatch: skipping non-live user uid={} mode={} "
                "signal_id={}",
                uid, user_mode, signal_id,
            )
            _note("skip:mode")
            return False

        # Entitlement gate (B16 two-tier model, 2026-06-24).  Hands-off
        # server-side auto-execution is the AUTO tier (₹2000/mo).  Free and
        # assist (one-tap) users never get an unattended order placed for
        # them here — assist places orders client-side from the app, free
        # places none.  Reversible via AUTO_TRADE_TIER_GATE_ENABLED.  Fails
        # closed: an unconfirmed tier resolves to free and is skipped.
        from config import AUTO_TRADE_TIER_GATE_ENABLED as _tier_gate
        if _tier_gate:
            # Manual take is the assist-tier product surface (one-tap
            # order on the user's own key), so the manual path gates at
            # can_assist; the unattended fan-out stays at can_auto.
            from src.api.auth import can_assist as _can_assist
            from src.api.auth import can_auto as _can_auto
            _tier_ok = _can_assist if _manual else _can_auto
            _user_tier = _resolve_user_tier(uid)
            if not _tier_ok(_user_tier):
                log.info(
                    "signal_dispatch: skipping user uid={} tier={} "
                    "signal_id={} manual={} — {} requires the {} tier",
                    uid, _user_tier, signal_id, _manual,
                    "one-tap take" if _manual else "hands-off auto-execution",
                    "assist" if _manual else "auto",
                )
                _capture(
                    outcome="rejected",
                    reject_class="TierNotEntitled",
                    reject_detail=(
                        f"One-tap take requires the assist tier or higher "
                        f"(your effective tier: {_user_tier})."
                    ),
                )
                _note("skip:tier")
                return False

        # Auto-pause gate (2026-05-24). After
        # ``_INSUFFICIENT_MARGIN_PAUSE_THRESHOLD`` consecutive ``-2019``
        # rejections we mark the user paused; from then on every
        # signal short-circuits here without touching the signing
        # service or recording a dispatch_log row. The app surfaces
        # the pause state in the user-facing auto-mode status so the
        # user can top up their wallet and call ``POST /api/auto-mode/
        # resume-mine`` to resume.  Recovery: go to Trade → Live and
        # tap "Resume", or save mode='live' in Auto-trade Settings
        # (which auto-resumes as of 2026-05-25).
        if not _manual and _uo.is_user_auto_paused_uid(uid):
            log.warning(
                "signal_dispatch: skipping AUTO-PAUSED user uid={} "
                "signal_id={} — user must resume via Trade tab or "
                "re-save mode='live' in Settings",
                uid, signal_id,
            )
            _note("skip:auto_paused")
            return False

        # Per-user path + regime trade-eligibility gate (2026-06-20).
        # The user picks which evaluator paths (setup classes) and which
        # entry regimes are allowed to auto-trade live for them — the
        # path/regime analogue of ``symbol_preference``.  ``None`` = no
        # preference (every path / regime eligible).  A configured set
        # (incl. the explicit empty set = block-all) means "only these
        # auto-trade for me".  Skip silently here — before the signing
        # service, sizing, or any dispatch_log row — exactly like the
        # mode gate above, so an unwanted path/regime never fires an
        # order.  This is the LIVE eligibility filter; the engine-wide
        # symbol allowlist + per-user symbol gate (position_fsm) still
        # apply on top.
        _path_pref, _regime_pref = (
            (None, None) if _manual
            else _uo.resolve_auto_trade_preferences_uid(uid)
        )
        #
        # These two are also the only gates in this function that can let
        # one signal through and stop the next one on an otherwise-armed
        # account — every gate above is a property of the ACCOUNT, so when
        # one of them is closed nothing trades at all.  That makes them the
        # answer to "some of my signals trade and some don't", and until
        # 2026-08-31 they returned here writing nothing anywhere.  They now
        # stamp a ``skipped`` dispatch_log row so the app can say which of
        # the user's own preferences declined this signal; the
        # account-level gates above deliberately do not (see
        # ``dispatch_log.record_skipped`` for the cost argument).
        from src.execution import dispatch_log as _dl_skip
        if _path_pref is not None:
            _setup_tok = (setup_class or "").upper()
            if _setup_tok not in _path_pref:
                log.info(
                    "signal_dispatch: skipping user uid={} signal_id={} — "
                    "setup {} not in user path preference (size={})",
                    uid, signal_id, _setup_tok or "<none>", len(_path_pref),
                )
                _dl_skip.record_skipped(
                    firebase_uid=uid,
                    signal_id=signal_id,
                    symbol=symbol,
                    direction=direction,
                    entry_price=entry_price,
                    skip_reason="path_preference",
                    skip_detail=(
                        f"{_setup_tok or 'this setup'} is not in your "
                        f"auto-trade setup list."
                    ),
                    source=_dispatch_source,
                )
                _note("skip:path_pref")
                return False
        if _regime_pref is not None:
            _regime_tok = (regime_label or "").upper()
            if _regime_tok not in _regime_pref:
                log.info(
                    "signal_dispatch: skipping user uid={} signal_id={} — "
                    "regime {} not in user regime preference (size={})",
                    uid, signal_id, _regime_tok or "<none>", len(_regime_pref),
                )
                _dl_skip.record_skipped(
                    firebase_uid=uid,
                    signal_id=signal_id,
                    symbol=symbol,
                    direction=direction,
                    entry_price=entry_price,
                    skip_reason="regime_preference",
                    skip_detail=(
                        f"Market regime {_regime_tok or 'unknown'} is not in "
                        f"your auto-trade regime list."
                    ),
                    source=_dispatch_source,
                )
                _note("skip:regime_pref")
                return False

        # Manual-take dup guard (2026-07-17).  The auto fan-out fires at
        # most once per signal (signal_router calls it exactly once at
        # publish), but a manual take can race a prior auto placement or
        # a double-tap — and ``place_signal`` does NOT check for an
        # existing position before firing the MARKET entry
        # (position_state.put_position is a blind upsert keyed on
        # (uid, signal_id)).  Without this guard a second take would
        # place a second real entry and overwrite the position doc.
        if _manual:
            from src.execution import position_state as _ps
            try:
                _existing = _ps.get_position(uid, signal_id)
            except _ps.PositionNotFoundError:
                _existing = None
            except Exception as _dup_exc:
                # Fail CLOSED on a store error: refuse the take rather
                # than risk a double entry on real money.
                log.warning(
                    "signal_dispatch: manual take dup-guard read failed "
                    "uid={} signal_id={}: {} — refusing take",
                    uid, signal_id, _dup_exc,
                )
                _capture(
                    outcome="rejected",
                    reject_class="DupGuardUnavailable",
                    reject_detail=(
                        "Could not confirm you don't already hold this "
                        "position — try again in a moment."
                    ),
                )
                _note("skip:dup_guard_unavailable")
                return False
            if _existing is not None and not _ps.is_terminal(_existing.state):
                log.info(
                    "signal_dispatch: manual take refused uid={} "
                    "signal_id={} — position already active (state={})",
                    uid, signal_id, _existing.state,
                )
                _capture(
                    outcome="rejected",
                    reject_class="AlreadyActive",
                    reject_detail=(
                        "You already hold a position on this signal "
                        f"(state: {getattr(_existing.state, 'value', _existing.state)})."
                    ),
                )
                _note("skip:already_active")
                return False

        # Per-user notional override (2026-05-20).  Each user can
        # set their own ``notional_usd`` via the auto-trade settings
        # page; falls back to ``_DEFAULT_NOTIONAL_USD`` ($500) when
        # unset, store offline, or lookup fails.  Computed inside
        # the per-user closure so a smaller-wallet user's override
        # doesn't shrink the position for everyone else on the same
        # signal.
        user_notional = _uo.resolve_notional_usd(uid, _DEFAULT_NOTIONAL_USD)
        # Risk-constant sizing for noise-floor-widened stops (2026-07-07):
        # when the scanner widened the stop by factor F (risk_scale = 1/F),
        # shrink the notional by the same factor so capital-at-risk per trade
        # is IDENTICAL to the un-widened trade. Never scales UP (cap at 1.0)
        # and never below MIN_NOTIONAL floors — _compute_qty_split's existing
        # min-notional snap/reject handles the tiny-position edge.
        if 0.0 < risk_scale < 1.0:
            user_notional = user_notional * risk_scale
        from config import PRE_TP_GRAB_FRACTION as _DEFAULT_GRAB_FRACTION
        from config import PRE_TP_THRESHOLD_PCT as _DEFAULT_PRETP_THRESHOLD
        from config import INVALIDATION_MODE_DEFAULT as _DEFAULT_INV_MODE
        user_grab_fraction = _uo.resolve_grab_fraction_uid(
            uid, float(_DEFAULT_GRAB_FRACTION)
        )
        # Per-user pre-TP threshold (the "close at 0.3% vs 0.5%" dial).
        # Until 2026-06-01 this was never read by dispatch — every user's
        # pre-TP LIMIT rested at the place_signal default regardless of
        # their setting.  Resolve it here and forward to the FSM so the
        # LIMIT price reflects the user's choice.
        user_pretp_threshold = _uo.resolve_pretp_threshold_uid(
            uid, float(_DEFAULT_PRETP_THRESHOLD)
        )
        # Per-user master pre-TP enable toggle (2026-05-29 fix).  The app's
        # "Pre-TP grab" ON/OFF switch writes user_pretp_settings.enabled but
        # was never consulted by the execution path — a user who turned
        # pre-TP OFF still had it fire.  Honour it here: a disabled user gets
        # grab_fraction 0 → pretp_controller.should_fire_pretp skips (the FSM
        # tick path) and close_fsm_partial_for_signal skips (the TradeMonitor
        # backstop).  The position still OPENS with full SL/TP geometry; only
        # the pre-TP partial close is suppressed.
        if not _uo.resolve_pretp_enabled_uid(uid, default=True):
            log.debug(
                "signal_dispatch: pre-TP suppressed — user master toggle OFF "
                "uid={} signal_id={}",
                uid, signal_id,
            )
            user_grab_fraction = 0.0
        # Per-user pre-TP regime + setup allowlist gates (PR-F).
        # If the user has configured an allowlist and the signal's regime
        # or setup is not on it, zero the grab fraction so pretp_controller
        # skips pre-TP for this position (pretp_qty = 0 → SKIPPED on fire).
        # Empty / None allowlist = "allow all" (default — no restriction).
        _allowed_regimes, _allowed_setups = _uo.resolve_pretp_allowlists_uid(uid)
        if _allowed_regimes and regime_label:
            if regime_label.upper() not in _allowed_regimes:
                log.debug(
                    "signal_dispatch: pre-TP suppressed by regime allowlist "
                    "uid={} regime={} allowed={}",
                    uid, regime_label, _allowed_regimes,
                )
                user_grab_fraction = 0.0
        if user_grab_fraction > 0 and _allowed_setups and setup_class:
            if setup_class.upper() not in _allowed_setups:
                log.debug(
                    "signal_dispatch: pre-TP suppressed by setup allowlist "
                    "uid={} setup={} allowed={}",
                    uid, setup_class, _allowed_setups,
                )
                user_grab_fraction = 0.0
        # Regime-per-exit: trend-aligned runner profile (§3.2b, owner-signed-off
        # 2026-06-21).  Supersedes the legacy TRENDING_PRETP_SUPPRESSED grab→0 for
        # trend-aligned entries.  Instead of skipping pre-TP entirely (full ride,
        # no BE) OR banking 50% at the flat +0.35% (caps the runner — TRENDING_UP
        # capture −10% in the all-time Raw Edge), bank a SMALL partial (30%) LATER
        # (pre-TP floored at 1.0R of the stop) and let the FSM trail the residual
        # past TP2.  Applied only when the FSM would actually trail (5m+15m trend
        # aligned with the trade) so we never bank-then-CANCEL.  When the flag is
        # OFF, fall back to the legacy suppress/shadow behaviour unchanged.
        _sl_dist_pct_for_regime = (
            abs(entry_price - sl_price) / entry_price * 100.0
            if (entry_price > 0 and sl_price > 0)
            else 0.0
        )
        from config import REGIME_PER_EXIT_ENABLED as _regime_per_exit_on
        if _regime_per_exit_on:
            _grab_before_runner = user_grab_fraction
            _thr_before_runner = user_pretp_threshold
            user_grab_fraction, user_pretp_threshold, _runner_applied = (
                _apply_regime_trend_runner(
                    user_grab_fraction,
                    user_pretp_threshold,
                    _sl_dist_pct_for_regime,
                    regime_label,
                    regime_label_15m,
                    direction,
                )
            )
            if _runner_applied:
                log.debug(
                    "signal_dispatch: regime-per-exit trend runner — uid={} "
                    "signal_id={} regime={}/{} grab {:.2f}→{:.2f} thr {:.3f}%→{:.3f}% "
                    "(bank small + later, trail the residual)",
                    uid, signal_id, regime_label, regime_label_15m,
                    _grab_before_runner, user_grab_fraction,
                    _thr_before_runner, user_pretp_threshold,
                )
        else:
            # Legacy TRENDING pre-TP suppression (session 20).  grab→0 in a
            # TRENDING entry regime — full ride, no pre-TP.
            _grab_before_trending_suppress = user_grab_fraction
            user_grab_fraction = _apply_trending_pretp_suppress(user_grab_fraction, regime_label)
            if user_grab_fraction != _grab_before_trending_suppress:
                log.debug(
                    "signal_dispatch: pre-TP suppressed — TRENDING entry regime "
                    "uid={} signal_id={} regime={} (grab {:.2f} → 0.00)",
                    uid, signal_id, regime_label, _grab_before_trending_suppress,
                )
            elif _shadow_telemetry_on() and _trending_pretp_would_suppress(
                _grab_before_trending_suppress, regime_label
            ):
                # Flag off but the gate matched — record what TRENDING_PRETP_SUPPRESSED
                # would have done so its blast radius is measurable before activation.
                log.info(
                    "signal_dispatch: [SHADOW] TRENDING_PRETP_SUPPRESSED would skip "
                    "pre-TP — uid={} signal_id={} regime={} grab={:.2f} (flag off, no-op)",
                    uid, signal_id, regime_label, _grab_before_trending_suppress,
                )
        # CANCEL-path fee optimisation (session 19, ships dark).  A RANGING/
        # QUIET entry regime routes the pre-TP to the CANCEL exit path, which
        # banks a partial via the maker LIMIT and then MARKET-closes the
        # residual at once (a 3rd fee + taker slippage on every win, with no
        # ride-to-TP1 benefit).  Closing the FULL position at the LIMIT
        # instead yields the same exit for 2 maker fees and no slippage.
        _grab_before_fullgrab = user_grab_fraction
        user_grab_fraction = _apply_cancel_fullgrab(user_grab_fraction, regime_label)
        if user_grab_fraction != _grab_before_fullgrab:
            log.debug(
                "signal_dispatch: full-grab pre-TP on CANCEL-bound regime "
                "uid={} signal_id={} regime={} (was grab={:.2f} → 1.00)",
                uid, signal_id, regime_label, _grab_before_fullgrab,
            )
        elif _shadow_telemetry_on() and _cancel_fullgrab_would_apply(
            _grab_before_fullgrab, regime_label
        ):
            # Flag off but the gate matched — record what the CANCEL-path
            # full-grab would have done so its impact is measurable first.
            log.info(
                "signal_dispatch: [SHADOW] PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED "
                "would full-grab — uid={} signal_id={} regime={} grab={:.2f} "
                "(flag off, no-op)",
                uid, signal_id, regime_label, _grab_before_fullgrab,
            )
        # SR_FLIP pre-TP R-scaling (change B — ships dark).
        # Truth-report: SR_FLIP's SL averages 1–2.5% wide (1×ATR minimum) but
        # the ATR-adaptive pre-TP threshold averages only 0.503% raw.  On a
        # 2.5% SL that is 0.20R — the banked half captures minimal reward
        # relative to the structural risk.  When enabled, the threshold is
        # floored at SL_dist_pct × SR_FLIP_PRETP_R_FACTOR (default 0.35R) so
        # wide-SL signals bank at a meaningful R-multiple.  Tight-SL signals
        # (SL < threshold/factor) are unaffected.
        if setup_class and setup_class.upper() == "SR_FLIP_RETEST" and user_grab_fraction > 0:
            from config import SR_FLIP_PRETP_R_FACTOR as _SR_FLIP_R_FACTOR
            from config import SR_FLIP_PRETP_R_SCALING_ENABLED as _SR_FLIP_RSCALE
            if sl_price > 0 and entry_price > 0:
                _sl_dist_pct = abs(entry_price - sl_price) / entry_price * 100.0
                _r_scaled_threshold = _sl_dist_pct * _SR_FLIP_R_FACTOR
                _scaling_binds = _r_scaled_threshold > user_pretp_threshold
                if _SR_FLIP_RSCALE and _scaling_binds:
                    log.debug(
                        "signal_dispatch: SR_FLIP pre-TP R-scaling raised threshold "
                        "uid={} signal_id={} sl_dist={:.3f}% old={:.3f}% new={:.3f}%",
                        uid, signal_id, _sl_dist_pct,
                        user_pretp_threshold, _r_scaled_threshold,
                    )
                    user_pretp_threshold = _r_scaled_threshold
                elif not _SR_FLIP_RSCALE and _scaling_binds and _shadow_telemetry_on():
                    log.info(
                        "signal_dispatch: [SHADOW] SR_FLIP_RSCALE_WOULD_RAISE "
                        "uid={} signal_id={} sl_dist={:.3f}% current={:.3f}% "
                        "would_raise_to={:.3f}% (flag off, no-op)",
                        uid, signal_id, _sl_dist_pct,
                        user_pretp_threshold, _r_scaled_threshold,
                    )

        # LSR pre-TP R-scaling (LSR geometry rebuild, win-side — ships dark).
        # Mirror of the SR_FLIP block above: LSR's structural sweep-stop is wide
        # while the ATR-adaptive pre-TP banks a tiny +0.47 nibble.  Floor the
        # threshold at SL_dist_pct × LSR_PRETP_R_FACTOR so surviving wins bank a
        # real R-multiple.  Does not touch the stop.
        if (
            setup_class
            and setup_class.upper() == "LIQUIDITY_SWEEP_REVERSAL"
            and user_grab_fraction > 0
        ):
            from config import LSR_PRETP_R_FACTOR as _LSR_R_FACTOR
            from config import LSR_PRETP_R_SCALING_ENABLED as _LSR_RSCALE
            if sl_price > 0 and entry_price > 0:
                _lsr_sl_dist_pct = abs(entry_price - sl_price) / entry_price * 100.0
                _lsr_r_threshold = _lsr_sl_dist_pct * _LSR_R_FACTOR
                _lsr_binds = _lsr_r_threshold > user_pretp_threshold
                if _LSR_RSCALE and _lsr_binds:
                    log.debug(
                        "signal_dispatch: LSR pre-TP R-scaling raised threshold "
                        "uid={} signal_id={} sl_dist={:.3f}% old={:.3f}% new={:.3f}%",
                        uid, signal_id, _lsr_sl_dist_pct,
                        user_pretp_threshold, _lsr_r_threshold,
                    )
                    user_pretp_threshold = _lsr_r_threshold
                elif not _LSR_RSCALE and _lsr_binds and _shadow_telemetry_on():
                    log.info(
                        "signal_dispatch: [SHADOW] LSR_RSCALE_WOULD_RAISE "
                        "uid={} signal_id={} sl_dist={:.3f}% current={:.3f}% "
                        "would_raise_to={:.3f}% (flag off, no-op)",
                        uid, signal_id, _lsr_sl_dist_pct,
                        user_pretp_threshold, _lsr_r_threshold,
                    )

        # Per-user invalidation aggressiveness (B17).  Stored on the
        # Position at placement time so the per-user FSM path can
        # enforce the correct mode when per-user soft-invalidation
        # lands.  The engine-wide TradeMonitor still uses
        # INVALIDATION_MODE_DEFAULT for the engine's signal book;
        # this field is forwarded to the per-user Position only.
        user_invalidation_mode = _uo.resolve_invalidation_mode_uid(
            uid, str(_DEFAULT_INV_MODE or "standard")
        )
        # Per-symbol management mode (Signals-tab full vs entry, 2026-06-20).
        # "entry" = engine places entry + protective SL only, then hands the
        # position to the user.  Implemented by reusing tested levers:
        #   • grab_fraction → 0   → no pre-TP LIMIT / no tick-based pre-TP
        #   • invalidation  → loose → engine invalidation does not force-close
        #                            (loose-mode FSM positions survive engine
        #                            invalidations — trade_monitor.py ~2057)
        #   • management_mode='entry' → place_signal lays NO TP ladder
        # The SL is still placed, so the naked-position invariant holds.
        # Per-user live exit mechanism (2026-08-10).  Read once here and
        # stamped on the Position, never re-read per bar — the governor runs
        # on the monitor clock and a SQLite read there is the hot-loop rule.
        user_exit_mechanism = _uo.resolve_exit_mechanism_uid(uid)
        management_mode = _uo.resolve_symbol_management_uid(uid, symbol)
        if management_mode == "entry":
            user_grab_fraction = 0.0
            user_invalidation_mode = "loose"
            log.info(
                "signal_dispatch: ENTRY-ONLY management uid={} symbol={} "
                "signal_id={} — entry + SL only, user manages the rest",
                uid, symbol, signal_id,
            )
        total_qty, tp1_qty, tp2_qty, tp3_qty = _compute_qty_split(
            symbol, entry_price, notional_usd=user_notional,
        )
        # Hard position-cap tripwire — B18 blast-radius cap.
        # Fires if user_notional exceeds the system-wide max ($2 000).
        # Defensive backstop: normal operation always passes since
        # resolve_notional_usd returns DB-stored values bounded by the UI.
        from src.execution import tripwires as _tw
        try:
            _tw.assert_position_cap(
                notional_usd=user_notional,
                cap_usd=user_notional,
                max_cap_usd=_tw.DEFAULT_POSITION_CAP_MAX_USD,
            )
        except _tw.PositionCapExceeded as exc:
            log.warning(
                "signal_dispatch: position cap exceeded uid={} signal_id={} "
                "notional=${:.2f} exc={}",
                uid, signal_id, user_notional, exc,
            )
            from src.execution import dispatch_log as _dl
            _dl.record_rejected(
                firebase_uid=uid,
                signal_id=signal_id,
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                reject_class="PositionCapExceeded",
                reject_detail=str(exc),
                source=_dispatch_source,
            )
            _capture(
                outcome="rejected",
                reject_class="PositionCapExceeded",
                reject_detail=str(exc),
            )
            _note("rejected:PositionCapExceeded")
            return False
        if total_qty <= 0:
            log.info(
                "signal_dispatch: zero qty for uid={} signal_id={} symbol={} "
                "entry={} notional=${} — skipping (below MIN_NOTIONAL after "
                "LOT_SIZE rounding even with snap-up)",
                uid, signal_id, symbol, entry_price, user_notional,
            )
            # Surface the skip in Recent Activity so the user knows WHY
            # no order was placed rather than seeing complete silence.
            from src.execution import dispatch_log as _dl
            _dl.record_rejected(
                firebase_uid=uid,
                signal_id=signal_id,
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                reject_class="NotionalTooSmall",
                reject_detail=(
                    f"Position size ${user_notional:.0f} is too small to "
                    f"place a {symbol} order at ${entry_price:.4f}. "
                    f"Increase your notional in Settings → Server-side "
                    f"auto-trade (minimum ~$10 recommended)."
                ),
                source=_dispatch_source,
            )
            _capture(
                outcome="rejected",
                reject_class="NotionalTooSmall",
                reject_detail=(
                    f"Position size ${user_notional:.0f} is too small for "
                    f"{symbol} — increase your notional in Settings."
                ),
            )
            _note("rejected:NotionalTooSmall")
            return False
        try:
            await _fsm.place_signal(
                firebase_uid=uid,
                signal_id=signal_id,
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                sl_price=sl_price,
                tp1_price=tp1_price,
                tp2_price=tp2_price,
                tp3_price=tp3_price,
                total_qty=total_qty,
                tp1_qty=tp1_qty,
                tp2_qty=tp2_qty,
                tp3_qty=tp3_qty,
                pretp_threshold_pct=user_pretp_threshold,
                pretp_fraction=user_grab_fraction,
                invalidation_mode=user_invalidation_mode,
                management_mode=management_mode,
                entry_regime=regime_label or "",
                entry_regime_15m=regime_label_15m or "",
                atr_percentile_at_entry=float(atr_percentile),
                atr_value_at_entry=float(atr_value),
                exit_mechanism=user_exit_mechanism,
            )
            # Record the successful placement for the user-facing
            # Recent Activity card.  Soft-fail inside the helper.
            from src.execution import dispatch_log as _dl
            _dl.record_placed(
                firebase_uid=uid,
                signal_id=signal_id,
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                total_qty=total_qty,
                source=_dispatch_source,
            )
            _capture(
                outcome="placed",
                symbol=symbol,
                direction=direction,
                entry_price=float(entry_price),
                total_qty=float(total_qty),
            )
            _note("placed")
            # Successful placement resets the consecutive -2019 counter.
            # If the user previously had a string of insufficient-margin
            # rejects but topped up + resumed, the next place succeeds
            # here and we wipe the counter so we don't carry stale
            # state into the next dispatch.
            _consec_insufficient_margin.pop(uid, None)
            return True
        except Exception as exc:
            # Typed exceptions from the safety-gate chain (PR-14
            # wiring) + tripwires (PR-8) reach here.  Log + count
            # the rejection but don't raise — other users may still
            # have a valid path.
            #
            # ``str(exc)`` carries the full diagnostic when the
            # exception is an ``OrderPlacementError`` subclass —
            # specifically the Binance error code + status + message
            # for ``OrderRejectedByBinance`` (e.g. ``code=-2010
            # status=400 message=Account has insufficient balance for
            # requested action``).  Without it, the log only shows
            # the exception class name and operators can't tell
            # margin-insufficiency from precision-too-high from
            # leverage-not-set.  PR-G follow-up 2026-05-19.
            log.info(
                "signal_dispatch: rejected uid={} signal_id={} symbol={} "
                "reason={} detail={!r}",
                uid, signal_id, symbol, type(exc).__name__, str(exc),
            )
            # Extract Binance code + msg from the SignResponse body
            # when the rejection was an OrderRejectedByBinance — the
            # app's Recent Activity card surfaces these as the
            # plain-English explanation (e.g. -2019 → "Margin is
            # insufficient — top up your Futures wallet").
            b_code = None
            b_msg = None
            sig_resp = getattr(exc, "signing_response", None)
            if sig_resp is not None:
                body = getattr(sig_resp, "binance_body", None)
                if isinstance(body, dict):
                    raw_code = body.get("code")
                    if raw_code is not None:
                        try:
                            b_code = int(raw_code)
                        except (TypeError, ValueError):
                            pass
                    raw_msg = body.get("msg") or body.get("message")
                    if isinstance(raw_msg, str):
                        b_msg = raw_msg
            from src.execution import dispatch_log as _dl
            _dl.record_rejected(
                firebase_uid=uid,
                signal_id=signal_id,
                symbol=symbol,
                direction=direction,
                entry_price=entry_price,
                reject_class=type(exc).__name__,
                reject_detail=str(exc),
                reject_binance_code=b_code,
                reject_binance_msg=b_msg,
                source=_dispatch_source,
            )
            _capture(
                outcome="rejected",
                reject_class=type(exc).__name__,
                reject_detail=str(exc),
                reject_binance_code=b_code,
                reject_binance_msg=b_msg,
            )
            _note(f"rejected:{type(exc).__name__}")
            # Feed the blast-radius circuit breakers (B18 tripwires
            # #4/#5).  Only real placement failures count — the helper
            # ignores gate rejections by type and -2019 by code, so a
            # kill-switch refusal or empty wallet can never trip a
            # breaker.  On trip it persists the disable / engages the
            # global kill switch itself.  Must never raise: this is a
            # failure handler and other users' dispatches are in
            # flight.
            try:
                _tw.record_order_placement_failure(
                    firebase_uid=uid, exc=exc, binance_code=b_code,
                )
            except Exception:
                log.exception(
                    "signal_dispatch: circuit-breaker feed failed uid={} "
                    "signal_id={}",
                    uid, signal_id,
                )
            # Consecutive-insufficient-margin tracker → auto-pause.
            # Owner-reported 2026-05-23: every signal was creating a
            # fresh "Insufficient margin" entry in the user's Recent
            # Activity card. After ``_INSUFFICIENT_MARGIN_PAUSE_THRESHOLD``
            # in a row we pause the user's dispatcher so the next
            # signal short-circuits at the gate above without spamming
            # the activity log. The pause persists until the user calls
            # ``POST /api/auto-mode/resume-mine`` (typically after
            # topping up).
            #
            # Any reject reason OTHER than -2019 clears the counter:
            # the user clearly engaged Binance but failed for a
            # different reason — wallet emptiness isn't the persistent
            # state we're tracking here.
            if b_code == _BINANCE_INSUFFICIENT_MARGIN_CODE:
                _consec_insufficient_margin[uid] += 1
                if (
                    _consec_insufficient_margin[uid]
                    >= _INSUFFICIENT_MARGIN_PAUSE_THRESHOLD
                ):
                    paused_at = _uo.pause_user_auto_trade_uid(
                        uid, "insufficient_margin",
                    )
                    log.warning(
                        "signal_dispatch: auto-paused uid={} after {} "
                        "consecutive -2019 rejects (paused_at={})",
                        uid,
                        _consec_insufficient_margin[uid],
                        paused_at,
                    )
                    # Counter stays at threshold so a transient store
                    # failure on the pause persist doesn't double-count
                    # the next time; resume_user_auto_trade is what
                    # clears the cycle.
            else:
                _consec_insufficient_margin.pop(uid, None)
            return False

    results = await asyncio.gather(
        *(_one_user(uid) for uid in uids),
        return_exceptions=False,
    )
    placed = sum(1 for r in results if r)
    # Honest outcome split: "rejected" = the order path was reached and a
    # dispatch_log row exists; "skipped" = a silent per-user gate (mode /
    # tier / pause / prefs) — the pre-2026-07-18 line lumped both into
    # "rejected", which hid a fleet-wide silent-skip blackout in plain
    # sight.  One line per fan-out; grep target when "no trades" is
    # reported.
    rejected = sum(v for k, v in outcomes.items() if k.startswith("rejected:"))
    skipped = sum(v for k, v in outcomes.items() if k.startswith("skip:"))
    log.info(
        "signal_dispatch: fan-out summary signal_id={} symbol={} "
        "direction={} active_users={} placed={} rejected={} skipped={} "
        "outcomes={} source={}",
        signal_id, symbol, direction, len(uids), placed, rejected, skipped,
        dict(outcomes), _dispatch_source,
    )
    # Fold into the monotonic totals feeding the auto_dispatch liveness
    # probe — auto fan-outs only, so a manual take can neither mask nor
    # trigger a fleet-wide blackout alert.
    if not _manual:
        _FANOUT_TOTALS["fanouts_total"] += 1
        if uids:
            _FANOUT_TOTALS["fanouts_with_users_total"] += 1
        _FANOUT_TOTALS["attempts_total"] += placed + rejected
        _FANOUT_TOTALS["placed_total"] += placed
        _FANOUT_TOTALS["skipped_total"] += skipped
        for k, v in outcomes.items():
            if k != "placed":
                _FANOUT_TOTALS[k] += v
    return placed


async def dispatch_signal_to_uid_manual(
    *,
    uid: str,
    signal_id: str,
    symbol: str,
    direction: str,
    entry_price: float,
    sl_price: float,
    tp1_price: float,
    tp2_price: float,
    tp3_price: float,
    regime_label: Optional[str] = None,
    regime_label_15m: Optional[str] = None,
    atr_percentile: float = 50.0,
    atr_value: float = 0.0,
    setup_class: Optional[str] = None,
) -> Dict[str, Any]:
    """Manual take (owner-approved 2026-07-17): place ONE signal for ONE
    user who explicitly tapped "Take trade" in the app.

    Same money path as the auto fan-out — per-user sizing, position-cap
    tripwire, ``place_signal``'s full safety-gate chain, dispatch_log —
    with three deliberate differences the user's tap justifies:

    * mode / auto-pause / path-regime preference gates are skipped
      (those encode *unattended* consent; the tap is explicit consent);
    * the tier gate applies at ``can_assist`` (one-tap is the assist-tier
      product surface) instead of ``can_auto``;
    * a ``(uid, signal_id)`` dup guard refuses a take when a non-terminal
      position already exists (double-tap / raced auto-dispatch).

    Returns a result dict: ``{"outcome": "placed", symbol, direction,
    entry_price, total_qty}`` or ``{"outcome": "rejected", reject_class,
    reject_detail[, reject_binance_code, reject_binance_msg]}``.
    """
    result: Dict[str, Any] = {}
    await dispatch_signal_to_active_users(
        signal_id=signal_id,
        symbol=symbol,
        direction=direction,
        entry_price=entry_price,
        sl_price=sl_price,
        tp1_price=tp1_price,
        tp2_price=tp2_price,
        tp3_price=tp3_price,
        regime_label=regime_label,
        regime_label_15m=regime_label_15m,
        atr_percentile=atr_percentile,
        atr_value=atr_value,
        setup_class=setup_class,
        _only_uid=uid,
        _manual=True,
        _manual_result=result,
    )
    if not result:
        # Terminal outcome that produced no capture (defensive — every
        # path above writes one; a crash inside gather would raise).
        result = {
            "outcome": "rejected",
            "reject_class": "UnknownDispatchOutcome",
            "reject_detail": "Take did not complete — check Recent Activity.",
        }
    result.setdefault("signal_id", signal_id)
    return result


async def dispatch_manual_trade(
    *,
    uid: str,
    ref_id: str,               # alert_id | signal_id — dedup key + coid seed
    symbol: str,
    direction: str,            # "LONG" | "SHORT"
    entry_type: str,           # "market" | "limit"
    entry_price: float,        # LIMIT price (entry_type=limit) / sizing anchor
    sl_price: float = 0.0,     # optional (user_owned may be entry-only)
    tp_prices: Optional[List[float]] = None,  # 0..3 legs, optional
    valid_for_minutes: int = 0,  # LIMIT-entry TTL
) -> Dict[str, Any]:
    """Server-side user-directed manual trade (manual trade builder).

    Places a trade the user built on the chart — MARKET entry or a resting
    LIMIT at ``entry_price``, with OPTIONAL user-set SL/TP — on their
    server-connected key.  Sizes at the user's fixed notional, gates at
    ``can_assist``, stamps ``protection_mode="user_owned"`` (SL optional; the
    naked-position invariant, ops detector, and reconciler backstop exempt
    it), and is idempotent on ``(uid, ref_id)``.  Runs the SAME
    ``place_signal`` safety-gate chain (global enable, kill switch, symbol
    allowlist, position cap, rate limit) + dispatch_log as auto/take.

    Gated by ``MANUAL_TRADE_BUILDER_ENABLED``; the endpoint pre-checks it too.
    Returns the ``TakeSignalResult``-shaped dict the app already parses.
    """
    def _reject(reject_class: str, detail: str, **extra: Any) -> Dict[str, Any]:
        return {
            "outcome": "rejected", "reject_class": reject_class,
            "reject_detail": detail, "ref_id": ref_id, **extra,
        }

    # Ops-controllable live switch (runtime tunable, falls back to the config
    # env default when Firestore isn't wired — get() never raises on read).
    from src import runtime_tunables as _rt
    if not bool(_rt.get("manual_trade_builder_enabled")):
        return _reject(
            "ManualTradeBuilderDisabled",
            "The manual trade builder is not enabled on this engine yet.",
        )

    direction = (direction or "").upper()
    if direction not in ("LONG", "SHORT"):
        return _reject("BadRequest", f"direction must be LONG or SHORT, got {direction!r}.")
    entry_type = (entry_type or "").lower()
    if entry_type not in ("market", "limit"):
        return _reject("BadRequest", f"entry_type must be market or limit, got {entry_type!r}.")
    if entry_price <= 0:
        return _reject("BadRequest", "A positive entry/mark price is required to size the trade.")
    if entry_type == "limit" and entry_price <= 0:
        return _reject("BadRequest", "A limit entry needs a positive entry price.")

    # Tier gate — can_assist (manual placement is the assist-tier surface),
    # same rule the endpoint pre-checks and dispatch applies elsewhere.
    from config import AUTO_TRADE_TIER_GATE_ENABLED as _tier_gate
    if _tier_gate:
        from src.api.auth import can_assist as _can_assist
        _tier = _resolve_user_tier(uid)
        if not _can_assist(_tier):
            return _reject(
                "TierNotEntitled",
                f"Building a trade requires the Assist plan or higher "
                f"(your effective tier: {_tier}).",
            )

    # Dup-guard on (uid, ref_id): place_signal is a blind upsert keyed on
    # (uid, signal_id), so without this a double-tap / retry would fire a
    # second real entry. Fail CLOSED on a store error — refuse rather than
    # risk a double entry on real money.
    from src.execution import position_state as _ps
    try:
        _existing = _ps.get_position(uid, ref_id)
    except _ps.PositionNotFoundError:
        _existing = None
    except Exception as _dup_exc:
        log.warning(
            "dispatch_manual_trade: dup-guard read failed uid={} ref_id={}: {} "
            "— refusing", uid, ref_id, _dup_exc,
        )
        return _reject(
            "DupGuardUnavailable",
            "Could not confirm you don't already hold this position — try again.",
        )
    if _existing is not None and not _ps.is_terminal(_existing.state):
        return _reject(
            "AlreadyActive",
            "You already hold a position on this "
            f"({getattr(_existing.state, 'value', _existing.state)}).",
        )

    # Sizing — user notional → total qty (MIN_NOTIONAL / stepSize handled by
    # _compute_qty_split), then split across the user's provided TP legs.
    from src.api import user_overrides as _uo
    from src.execution import symbol_filters as _sf
    _notional = _uo.resolve_notional_usd(uid, _DEFAULT_NOTIONAL_USD)
    total_qty, _t1, _t2, _t3 = _compute_qty_split(symbol, entry_price, notional_usd=_notional)
    if total_qty <= 0:
        from src.execution import dispatch_log as _dl
        _dl.record_rejected(
            firebase_uid=uid, signal_id=ref_id, symbol=symbol, direction=direction,
            entry_price=entry_price, reject_class="NotionalTooSmall",
            reject_detail=(
                f"Position size ${_notional:.0f} is too small to place a {symbol} "
                f"order at ${entry_price:.6g}. Increase your notional in Settings."
            ),
            source="manual_trade",
        )
        return _reject(
            "NotionalTooSmall",
            f"Position size ${_notional:.0f} is too small for {symbol} — "
            "increase your notional in Settings.",
        )

    _legs = [float(p) for p in (tp_prices or []) if p and float(p) > 0][:3]
    tp1_price = tp2_price = tp3_price = 0.0
    tp1_qty = tp2_qty = tp3_qty = 0.0
    if _legs:
        # Even split of total_qty across the provided TP legs; the last leg
        # absorbs the stepSize rounding residual so the legs sum to total_qty.
        _n = len(_legs)
        _per = _sf.round_qty(symbol, total_qty / _n)
        _qtys = [_per] * _n
        _qtys[-1] = _sf.round_qty(symbol, total_qty - _per * (_n - 1))
        _prices = [tp1_price, tp2_price, tp3_price]
        _qcols = [tp1_qty, tp2_qty, tp3_qty]
        for _i in range(_n):
            _prices[_i] = _legs[_i]
            _qcols[_i] = _qtys[_i]
        tp1_price, tp2_price, tp3_price = _prices
        tp1_qty, tp2_qty, tp3_qty = _qcols

    # Blast-radius position cap (B18) — defensive parity with the auto path.
    from src.execution import tripwires as _tw
    try:
        _tw.assert_position_cap(
            notional_usd=_notional, cap_usd=_notional,
            max_cap_usd=_tw.DEFAULT_POSITION_CAP_MAX_USD,
        )
    except _tw.PositionCapExceeded as _cap_exc:
        return _reject("PositionCapExceeded", str(_cap_exc))

    from src.execution import position_fsm as _fsm
    from src.execution import dispatch_log as _dl
    try:
        pos = await _fsm.place_signal(
            uid,
            signal_id=ref_id,
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            sl_price=sl_price if (sl_price and sl_price > 0) else 0.0,
            tp1_price=tp1_price, tp2_price=tp2_price, tp3_price=tp3_price,
            total_qty=total_qty, tp1_qty=tp1_qty, tp2_qty=tp2_qty, tp3_qty=tp3_qty,
            pretp_fraction=0.0,            # user manages exits — no engine pre-TP
            invalidation_mode="loose",     # engine invalidation never force-closes
            management_mode="full",
            protection_mode="user_owned",
            entry_type=entry_type,
            valid_for_minutes=valid_for_minutes,
        )
    except Exception as exc:  # noqa: BLE001 — turn any placement failure into a reject
        b_code = None
        b_msg = None
        sig_resp = getattr(exc, "signing_response", None)
        if sig_resp is not None:
            body = getattr(sig_resp, "binance_body", None)
            if isinstance(body, dict):
                try:
                    b_code = int(body.get("code")) if body.get("code") is not None else None
                except (TypeError, ValueError):
                    b_code = None
                _raw = body.get("msg") or body.get("message")
                b_msg = _raw if isinstance(_raw, str) else None
        log.info(
            "dispatch_manual_trade: rejected uid={} ref_id={} symbol={} "
            "reason={} detail={!r}",
            uid, ref_id, symbol, type(exc).__name__, str(exc),
        )
        _dl.record_rejected(
            firebase_uid=uid, signal_id=ref_id, symbol=symbol, direction=direction,
            entry_price=entry_price, reject_class=type(exc).__name__,
            reject_detail=str(exc), reject_binance_code=b_code,
            reject_binance_msg=b_msg, source="manual_trade",
        )
        return _reject(
            type(exc).__name__, str(exc),
            reject_binance_code=b_code, reject_binance_msg=b_msg,
        )

    _dl.record_placed(
        firebase_uid=uid, signal_id=ref_id, symbol=symbol, direction=direction,
        entry_price=entry_price, total_qty=total_qty, source="manual_trade",
    )
    _resting = pos.state == _ps.PositionState.PENDING_ENTRY
    return {
        "outcome": "placed",
        "ref_id": ref_id,
        "symbol": symbol,
        "direction": direction,
        "entry_price": float(entry_price),
        "total_qty": float(total_qty),
        "entry_type": entry_type,
        "resting": _resting,   # True → LIMIT rests until filled/expired
        "state": getattr(pos.state, "value", str(pos.state)),
    }


async def close_fsm_positions_for_signal(
    signal_id: str,
    *,
    symbol: str,
    direction: str,
    reason: str,
    excluded_modes: Optional[frozenset] = None,
    only_uid: Optional[str] = None,
) -> int:
    """Cancel native SL/TP orders + place a MARKET close for every user
    who has a non-terminal FSM position for ``signal_id``.

    Called by :meth:`src.trade_monitor.TradeMonitor._broker_close_full`
    on every non-TP close path (INVALIDATED, SL_HIT detected engine-
    side, EXPIRED, CANCELLED) so the Binance position closes in
    lockstep with engine signal state — the B12 safety guarantee.

    ``excluded_modes``: when provided, positions whose
    ``invalidation_mode`` is in the set are skipped.  Used by the
    invalidation path (reason="invalidated") to let loose-mode users
    ride to their native SL/TP rather than being closed by the
    engine's regime/EMA/momentum kill.

    ``only_uid``: restrict the fan-out to ONE user.  This is what the app's
    "Close position" button reaches (2026-09-01, owner: *"user can close that
    trade from our app too without visiting binance"*), and it is a parameter
    rather than a second function on purpose — everything below it is the
    hardened close: cancel the bracket first so a resting stop cannot fire
    against our own market order, tolerate -2022 because Binance may have
    flattened us a millisecond earlier, mark terminal so the monitor stops
    re-attempting.  A second implementation would be a second thing to keep
    correct, and this repo has paid for that in every measurement lane that
    grew its own resolver.  Note the scope: it closes the user's POSITION and
    leaves the signal in the engine's book, which is the honest split — one
    subscriber exiting early is not the setup being invalidated for everyone.

    Returns the count of users whose positions were actually closed
    (i.e. the MARKET close order was accepted OR the position was
    already terminal/not found).

    Fail-soft: per-user errors are logged but never propagate — a
    failure for one user must not prevent the close for others.
    """
    from datetime import datetime, timezone

    from src.execution import order_placer as _op
    from src.execution import position_state as _ps

    if not _ps.is_initialised():
        # position_state not booted (dev / test context without GCP) —
        # no-op cleanly rather than raising.
        return 0

    uids = _active_uids()
    if only_uid is not None:
        # Deliberately NOT intersected with ``_active_uids()``: that set is
        # the auto-trade fan-out roster, and a user who has since turned
        # auto-trade off still owns any position it opened.  Refusing to
        # close it because they are no longer on the roster would strand a
        # real position behind a button that says it closes it.
        uids = [only_uid]
    if not uids:
        return 0

    closed = 0

    for uid in uids:
        # Load position from Firestore.  Not found → this user had no
        # FSM position for this signal (e.g. they were mode=paper when
        # the signal fired).  Terminal → already closed by native SL/TP.
        try:
            pos = _ps.get_position(uid, signal_id)
        except _ps.PositionNotFoundError:
            continue
        except Exception as exc:
            log.warning(
                "close_fsm: get_position failed uid={} signal_id={} exc={}",
                uid, signal_id, exc,
            )
            continue

        if _ps.is_terminal(pos.state):
            continue

        # Per-user invalidation mode filter: loose-mode users survive
        # engine invalidation; their native SL/TP bracket is still live.
        if excluded_modes and pos.invalidation_mode in excluded_modes:
            log.info(
                "close_fsm: skipping uid={} signal_id={} "
                "invalidation_mode={} excluded by caller (reason={})",
                uid, signal_id, pos.invalidation_mode, reason,
            )
            continue

        # A position the trail governor has taken over does not answer to the
        # signal's SL any more — the handover CANCELLED that stop on the
        # exchange, deliberately, and replaced it with the mechanism's own.
        #
        # Without this the handover was cosmetic for any trade that reached its
        # original SL: TradeMonitor still evaluates the signal against that
        # level and closes everyone on a hit, so the governed position exited
        # on a rule the mechanism had removed — and exited WORSE, because what
        # was a stop resting AT the level became a market close at monitor-loop
        # latency.  Measured 2026-08-11: PROMUSDT signal SL_HIT at 04:46:39
        # (-3.00% designed), position market-closed 12s later at 2.177 against
        # an entry of 2.289 — **-4.89%**.  The canary was being scored on an
        # exit the mechanism does not have.
        #
        # Scoped as narrowly as it can be, and the narrowness is the argument:
        # ONLY `sl_hit`, and ONLY once `trail_governing` is true.  Pre-handover
        # the evaluator's SL is still live and still governs, so those close
        # normally.  `invalidated` / `expired` / `cancelled` continue to close
        # everyone, governed or not — those are the engine deciding to be out
        # of the trade entirely rather than a level being touched, and B12's
        # lockstep guarantee plus the hold-time bound both depend on them.
        if reason == "sl_hit" and bool(getattr(pos, "trail_governing", False)):
            log.info(
                "close_fsm: skipping uid={} signal_id={} {} — the trail "
                "governor holds this exit (mechanism={}, parked={}); the "
                "signal's SL was cancelled at handover and is not this "
                "position's stop",
                uid, signal_id, pos.symbol,
                getattr(pos, "exit_mechanism", ""),
                getattr(pos, "trail_stop_price", 0.0),
            )
            continue

        placer = _op.OrderPlacer(uid)

        # Cancel all open bracket orders — tolerant of -2011/-20121 (already
        # gone, filled, or expired).  Cancel first so the MARKET close
        # below doesn't fight with a pending SL/TP that might otherwise
        # also close the position and over-reduce.
        # SL and TP orders are algo orders (placed via /fapi/v1/algoOrder);
        # cancel via cancel_algo_order, not cancel_order.
        for attr in _PROTECTIVE_ORDER_ATTRS:
            order_id = int(getattr(pos, attr, 0) or 0)
            if not order_id:
                continue
            try:
                await placer.cancel_algo_order(symbol=pos.symbol, algo_id=order_id)
            except _op.OrderPlacementError as exc:
                log.warning(
                    "close_fsm: cancel_algo_order failed uid={} signal_id={} "
                    "algo_id={} exc={}",
                    uid, signal_id, order_id, exc,
                )

        # Place REDUCE_ONLY MARKET to close the remaining position.
        # ``reduceOnly=true`` is a safety net: if Binance already closed
        # the position (e.g. native SL fired milliseconds before we got
        # here), this will fail with -2022 "ReduceOnly Order is rejected"
        # which we absorb below rather than crashing.
        # Defensively: if closed_qty somehow exceeds total_qty (shouldn't
        # happen but Firestore partial writes are possible), fall back to
        # total_qty so we don't send a zero-qty order.
        remaining = pos.total_qty - pos.closed_qty
        if remaining <= 0:
            remaining = pos.total_qty

        market_close_ok = False
        try:
            await placer.place_market_close(
                signal_id=signal_id,
                symbol=pos.symbol,
                direction=pos.side,
                quantity=remaining,
            )
            market_close_ok = True
        except _op.OrderRejectedByBinance as exc:
            sig_resp = getattr(exc, "signing_response", None)
            b_code = None
            if sig_resp is not None:
                body = getattr(sig_resp, "binance_body", None)
                if isinstance(body, dict):
                    try:
                        b_code = int(body.get("code", 0))
                    except (TypeError, ValueError):
                        pass
            if b_code == -2022:
                # -2022: ReduceOnly rejected — position already flat on
                # Binance's side (native SL/TP beat us here).  That's
                # fine — we still want to mark the Firestore doc closed.
                log.info(
                    "close_fsm: -2022 ReduceOnly rejected — position "
                    "already flat on Binance uid={} signal_id={}",
                    uid, signal_id,
                )
                market_close_ok = True  # treat as success
            else:
                log.error(
                    "close_fsm: MARKET close rejected uid={} signal_id={} "
                    "symbol={} reason={} code={} exc={}",
                    uid, signal_id, pos.symbol, reason, b_code, exc,
                )
        except _op.OrderPlacementError as exc:
            log.error(
                "close_fsm: MARKET close FAILED uid={} signal_id={} "
                "symbol={} reason={} exc={}",
                uid, signal_id, pos.symbol, reason, exc,
            )

        # Mark the Firestore position terminal regardless of whether
        # the MARKET order succeeded — an engine restart / reconciler
        # will catch any remaining Binance state drift.  Without this
        # mark the TradeMonitor would re-attempt close on every tick.
        now = datetime.now(timezone.utc)
        pos.state = _ps.PositionState.CLOSED
        pos.close_reason = reason[:20]  # short label fits in the doc
        pos.closed_at = now
        pos.last_event_at = now
        try:
            _ps.put_position(pos)
        except Exception as exc:
            log.error(
                "close_fsm: put_position failed uid={} signal_id={} exc={}",
                uid, signal_id, exc,
            )

        closed += 1
        log.info(
            "close_fsm: closed uid={} signal_id={} symbol={} reason={} "
            "market_close_ok={}",
            uid, signal_id, pos.symbol, reason, market_close_ok,
        )

    return closed


def get_fsm_positions_for_signal(
    signal_id: str,
) -> list:
    """Return ``[(uid, Position), ...]`` for every non-terminal FSM position
    that is currently open for ``signal_id``.

    Used by the per-user tight-mode invalidation check in TradeMonitor so
    it can iterate users without importing position_state directly.  Returns
    an empty list when position_state is not initialised or no positions exist.
    """
    from src.execution import position_state as _ps

    if not _ps.is_initialised():
        return []

    result = []
    for uid in _active_uids():
        try:
            pos = _ps.get_position(uid, signal_id)
        except _ps.PositionNotFoundError:
            continue
        except Exception as exc:
            log.debug(
                "get_fsm_positions_for_signal: get_position failed "
                "uid={} signal_id={} exc={}",
                uid, signal_id, exc,
            )
            continue
        if not _ps.is_terminal(pos.state):
            result.append((uid, pos))
    return result


async def close_single_fsm_position(
    uid: str,
    signal_id: str,
    *,
    symbol: str,
    direction: str,
    reason: str,
) -> bool:
    """Cancel native bracket orders + place a MARKET close for a single user.

    Returns ``True`` when the close was successfully attempted, ``False`` when
    the position was not found, already terminal, or position_state is not
    initialised.  Fail-soft: Binance / Firestore errors are logged but not
    re-raised — the reconciler is the safety net.
    """
    from datetime import datetime, timezone

    from src.execution import order_placer as _op
    from src.execution import position_state as _ps

    if not _ps.is_initialised():
        return False

    try:
        pos = _ps.get_position(uid, signal_id)
    except _ps.PositionNotFoundError:
        return False
    except Exception as exc:
        log.warning(
            "close_single_fsm: get_position failed uid={} signal_id={} exc={}",
            uid, signal_id, exc,
        )
        return False

    if _ps.is_terminal(pos.state):
        return False

    placer = _op.OrderPlacer(uid)

    for attr in _PROTECTIVE_ORDER_ATTRS:
        order_id = int(getattr(pos, attr, 0) or 0)
        if not order_id:
            continue
        try:
            await placer.cancel_algo_order(symbol=pos.symbol, algo_id=order_id)
        except _op.OrderPlacementError as exc:
            log.warning(
                "close_single_fsm: cancel_algo_order failed uid={} signal_id={} "
                "attr={} algo_id={} exc={}",
                uid, signal_id, attr, order_id, exc,
            )

    remaining = pos.total_qty - pos.closed_qty
    if remaining <= 0:
        remaining = pos.total_qty

    market_close_ok = False
    try:
        await placer.place_market_close(
            signal_id=signal_id,
            symbol=pos.symbol,
            direction=pos.side,
            quantity=remaining,
        )
        market_close_ok = True
    except _op.OrderRejectedByBinance as exc:
        sig_resp = getattr(exc, "signing_response", None)
        b_code = None
        if sig_resp is not None:
            body = getattr(sig_resp, "binance_body", None)
            if isinstance(body, dict):
                try:
                    b_code = int(body.get("code", 0))
                except (TypeError, ValueError):
                    pass
        if b_code == -2022:
            log.info(
                "close_single_fsm: -2022 ReduceOnly rejected — already flat "
                "uid={} signal_id={}",
                uid, signal_id,
            )
            market_close_ok = True
        else:
            log.error(
                "close_single_fsm: MARKET close rejected uid={} signal_id={} "
                "reason={} code={} exc={}",
                uid, signal_id, reason, b_code, exc,
            )
    except _op.OrderPlacementError as exc:
        log.error(
            "close_single_fsm: MARKET close FAILED uid={} signal_id={} "
            "reason={} exc={}",
            uid, signal_id, reason, exc,
        )

    now = datetime.now(timezone.utc)
    pos.state = _ps.PositionState.CLOSED
    pos.close_reason = reason[:20]
    pos.closed_at = now
    pos.last_event_at = now
    try:
        _ps.put_position(pos)
    except Exception as exc:
        log.error(
            "close_single_fsm: put_position failed uid={} signal_id={} exc={}",
            uid, signal_id, exc,
        )

    log.info(
        "close_single_fsm: closed uid={} signal_id={} symbol={} reason={} "
        "market_close_ok={}",
        uid, signal_id, pos.symbol, reason, market_close_ok,
    )
    return True


async def close_fsm_partial_for_signal(
    signal_id: str,
    *,
    symbol: str,
    direction: str,
    fraction: float,
    mark_price: float,
) -> int:
    """Place a REDUCE_ONLY MARKET order for ``fraction`` of each user's
    open FSM position for ``signal_id``.

    Called by :meth:`src.trade_monitor.TradeMonitor._check_pre_tp_grab`
    to execute the §3.2a pre-TP partial close for server-side FSM users
    whose positions were opened via the signing-service path (not CCXT).

    The CCXT ``OrderManager.close_partial`` path is a no-op for these
    users because their entry qty is never recorded in
    ``_open_quantities``.  This function fills that gap.

    **MIN_NOTIONAL guard**: Binance enforces a per-symbol minimum
    notional (typically $5 USDT) on every order.  For small positions
    (e.g. 10 USDT notional at 10×), the partial close qty × price can
    fall below $5 after LOT_SIZE flooring.  When that happens we close
    the full remaining position instead so the pre-TP banking is never
    silently skipped — a full close at pre-TP is strictly better than
    leaving the position open with no protection.

    Returns the count of users for whom a partial order was placed.
    """
    from src.execution import order_placer as _op
    from src.execution import position_state as _ps
    from src.execution import symbol_filters as _sf

    if not _ps.is_initialised():
        return 0

    uids = _active_uids()
    if not uids:
        return 0

    fraction = max(0.0, min(1.0, fraction))
    placed = 0

    for uid in uids:
        try:
            pos = _ps.get_position(uid, signal_id)
        except _ps.PositionNotFoundError:
            continue
        except Exception as exc:
            log.warning(
                "close_fsm_partial: get_position failed uid={} signal_id={} exc={}",
                uid, signal_id, exc,
            )
            continue

        if _ps.is_terminal(pos.state):
            continue
        if pos.pretp_fired:
            continue  # idempotent — don't double-fire

        # pretp_fraction <= 0 means pre-TP is disabled for THIS position
        # (user master toggle OFF, or suppressed by the per-user regime/
        # setup allowlist at dispatch).  Treat 0 as "skip" rather than
        # falling back to the engine-wide ``fraction`` constant — otherwise
        # the TradeMonitor backstop would re-fire a pre-TP close the user
        # explicitly opted out of.
        if pos.pretp_fraction <= 0:
            continue

        base_qty = pos.filled_qty if pos.filled_qty > 0 else pos.total_qty
        remaining = pos.total_qty - pos.closed_qty
        if remaining <= 0:
            remaining = base_qty

        # Use the per-position grab fraction stored at dispatch time (= user's
        # configured setting, stamped onto the position by place_signal).
        # This honours the per-user slider rather than the engine-wide config.
        effective_fraction = max(0.30, min(1.00, pos.pretp_fraction)) if pos.pretp_fraction > 0 else fraction

        # Compute the fractional close qty and apply LOT_SIZE rounding.
        # round_qty floors to stepSize so Binance never rejects -1111.
        raw_qty = base_qty * effective_fraction
        close_qty = _sf.round_qty(symbol, raw_qty)

        if close_qty <= 0:
            log.warning(
                "close_fsm_partial: qty=0 after rounding uid={} signal_id={} "
                "raw_qty={:.8f} symbol={}",
                uid, signal_id, raw_qty, symbol,
            )
            continue

        # MIN_NOTIONAL check.  A small position where `fraction × qty × price`
        # falls below Binance's $5 floor (-4164) can't be partially closed.
        # Fall back to closing the full remaining position so the pre-TP banking
        # actually executes rather than silently failing.
        if mark_price > 0 and not _sf.meets_min_notional(symbol, close_qty, mark_price):
            full_qty = _sf.round_qty(symbol, remaining)
            if full_qty > 0 and _sf.meets_min_notional(symbol, full_qty, mark_price):
                log.info(
                    "close_fsm_partial: partial qty {:.8f} (${:.4f}) below "
                    "MIN_NOTIONAL for {} — upgrading to full close qty={:.8f}",
                    close_qty, close_qty * mark_price, symbol, full_qty,
                )
                close_qty = full_qty
            else:
                log.warning(
                    "close_fsm_partial: qty {:.8f} below MIN_NOTIONAL and "
                    "full-close fallback also fails for {} — skipping uid={}",
                    close_qty, symbol, uid,
                )
                continue

        placer = _op.OrderPlacer(uid)
        try:
            await placer.place_pretp_partial(
                signal_id=signal_id,
                symbol=symbol,
                direction=direction,
                quantity=close_qty,
            )
            # Mark position so the 5s poll doesn't double-fire.
            pos.pretp_fired = True
            pos.last_event_at = __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            )
            try:
                _ps.put_position(pos)
            except Exception as exc:
                log.warning(
                    "close_fsm_partial: put_position failed uid={} signal_id={} exc={}",
                    uid, signal_id, exc,
                )
            placed += 1
            log.info(
                "close_fsm_partial: pre-TP placed uid={} signal_id={} "
                "symbol={} qty={:.8f} fraction={:.2f}",
                uid, signal_id, symbol, close_qty, fraction,
            )
        except _op.OrderRejectedByBinance as exc:
            sig_resp = getattr(exc, "signing_response", None)
            b_code = None
            if sig_resp is not None:
                body = getattr(sig_resp, "binance_body", None)
                if isinstance(body, dict):
                    try:
                        b_code = int(body.get("code", 0))
                    except (TypeError, ValueError):
                        pass
            log.error(
                "close_fsm_partial: Binance rejected pre-TP uid={} signal_id={} "
                "symbol={} code={} exc={}",
                uid, signal_id, symbol, b_code, exc,
            )
        except _op.OrderPlacementError as exc:
            log.error(
                "close_fsm_partial: placement failed uid={} signal_id={} "
                "symbol={} exc={}",
                uid, signal_id, symbol, exc,
            )

    return placed
