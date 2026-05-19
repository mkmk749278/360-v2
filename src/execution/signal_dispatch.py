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
import time
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from src.utils import get_logger

log = get_logger("execution.signal_dispatch")


# Per-user notional cap.  Matches B18 default — using the cap as
# the default sizing means ``assert_position_cap`` is satisfied
# without per-user lookup.  A future PR adds user-configurable
# overrides up to the policy floor ($2000).
_DEFAULT_NOTIONAL_USD = 500.0

# TP qty split — sums to 100%.  Matches §3.2a doctrine (banking
# the bonus tail across TP legs after pre-TP grabs the primary
# slice).  Pre-TP fill cancels TP2 + TP3 (PR-7) so the residual
# rides toward TP1 only.
_TP1_FRACTION = 0.30
_TP2_FRACTION = 0.40
_TP3_FRACTION = 0.30

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


def _compute_qty_split(
    symbol: str, entry_price: float,
) -> Tuple[float, float, float, float]:
    """Return ``(total_qty, tp1_qty, tp2_qty, tp3_qty)`` for a
    $500-notional position on ``symbol`` at the given entry price.

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
    rounded total_qty fails MIN_NOTIONAL (the order would be rejected
    by Binance with -4164; better to skip cleanly than to fire a
    doomed order through the FSM + circuit-breaker chain).
    """
    from src.execution import symbol_filters as _sf

    if entry_price <= 0:
        return (0.0, 0.0, 0.0, 0.0)

    raw_qty = _DEFAULT_NOTIONAL_USD / entry_price
    total_qty = _sf.round_qty(symbol, raw_qty)
    if total_qty <= 0:
        return (0.0, 0.0, 0.0, 0.0)
    if not _sf.meets_min_notional(symbol, total_qty, entry_price):
        log.info(
            "signal_dispatch: symbol={} qty={:.8f} price={:.8f} below "
            "MIN_NOTIONAL after LOT_SIZE rounding — skipping",
            symbol, total_qty, entry_price,
        )
        return (0.0, 0.0, 0.0, 0.0)

    tp1 = _sf.round_qty(symbol, total_qty * _TP1_FRACTION)
    tp2 = _sf.round_qty(symbol, total_qty * _TP2_FRACTION)
    # tp3 absorbs the rounding residual; floored again so it stays
    # on a stepSize boundary.  May be 0 if total_qty is a small
    # number of stepSize units — that's fine; FSM treats tp3_qty=0
    # as "no tp3 leg" and the residual rides to SL/pre-TP.
    tp3 = _sf.round_qty(symbol, total_qty - tp1 - tp2)
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
    """
    # Lazy import to avoid circular dep: position_fsm imports the
    # signing-service client which imports the engine bootstrap.
    from src.execution import position_fsm as _fsm

    uids = _active_uids()
    if not uids:
        return 0

    total_qty, tp1_qty, tp2_qty, tp3_qty = _compute_qty_split(symbol, entry_price)
    if total_qty <= 0:
        log.warning(
            "signal_dispatch: zero qty for signal_id={} symbol={} entry={} — skipping",
            signal_id, symbol, entry_price,
        )
        return 0

    async def _one_user(uid: str) -> bool:
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
            )
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
            return False

    results = await asyncio.gather(
        *(_one_user(uid) for uid in uids),
        return_exceptions=False,
    )
    placed = sum(1 for r in results if r)
    log.info(
        "signal_dispatch: signal_id={} symbol={} direction={} "
        "active_users={} placed={} rejected={}",
        signal_id, symbol, direction, len(uids), placed, len(uids) - placed,
    )
    return placed
