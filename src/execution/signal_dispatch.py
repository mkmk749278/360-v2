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
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

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

    tp1 = _sf.round_qty(symbol, total_qty * _TP1_FRACTION)
    tp2 = _sf.round_qty(symbol, total_qty * _TP2_FRACTION)
    # tp3 absorbs the rounding residual; floored again so it stays
    # on a stepSize boundary.  May be 0 if total_qty is a small
    # number of stepSize units — that's fine; FSM treats tp3_qty=0
    # as "no tp3 leg" and the residual rides to SL/pre-TP.
    tp3 = _sf.round_qty(symbol, total_qty - tp1 - tp2)

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
        tp1 = total_qty
        tp2 = 0.0
        tp3 = 0.0
        log.info(
            "signal_dispatch: symbol={} tp legs below MIN_NOTIONAL "
            "(tp1 notional=${:.2f} < ${:.2f}) — consolidating into "
            "single tp1=full-position",
            symbol, tp1 * entry_price / total_qty * tp1, min_notional,
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
        if user_mode not in ("live", "both"):
            log.info(
                "signal_dispatch: skipping non-live user uid={} mode={} "
                "signal_id={}",
                uid, user_mode, signal_id,
            )
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
        if _uo.is_user_auto_paused_uid(uid):
            log.warning(
                "signal_dispatch: skipping AUTO-PAUSED user uid={} "
                "signal_id={} — user must resume via Trade tab or "
                "re-save mode='live' in Settings",
                uid, signal_id,
            )
            return False

        # Per-user notional override (2026-05-20).  Each user can
        # set their own ``notional_usd`` via the auto-trade settings
        # page; falls back to ``_DEFAULT_NOTIONAL_USD`` ($500) when
        # unset, store offline, or lookup fails.  Computed inside
        # the per-user closure so a smaller-wallet user's override
        # doesn't shrink the position for everyone else on the same
        # signal.
        user_notional = _uo.resolve_notional_usd(uid, _DEFAULT_NOTIONAL_USD)
        total_qty, tp1_qty, tp2_qty, tp3_qty = _compute_qty_split(
            symbol, entry_price, notional_usd=user_notional,
        )
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
            )
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
            )
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
    log.info(
        "signal_dispatch: signal_id={} symbol={} direction={} "
        "active_users={} placed={} rejected={}",
        signal_id, symbol, direction, len(uids), placed, len(uids) - placed,
    )
    return placed


async def close_fsm_positions_for_signal(
    signal_id: str,
    *,
    symbol: str,
    direction: str,
    reason: str,
) -> int:
    """Cancel native SL/TP orders + place a MARKET close for every user
    who has a non-terminal FSM position for ``signal_id``.

    Called by :meth:`src.trade_monitor.TradeMonitor._broker_close_full`
    on every non-TP close path (INVALIDATED, SL_HIT detected engine-
    side, EXPIRED, CANCELLED) so the Binance position closes in
    lockstep with engine signal state — the B12 safety guarantee.

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

        placer = _op.OrderPlacer(uid)

        # Cancel all open bracket orders — tolerant of -2011 (already
        # gone, filled, or expired).  Cancel first so the MARKET close
        # below doesn't fight with a pending SL/TP that might otherwise
        # also close the position and over-reduce.
        for order_id in (
            pos.sl_order_id,
            pos.sl_be_order_id,
            pos.tp1_order_id,
            pos.tp2_order_id,
            pos.tp3_order_id,
        ):
            if not order_id:
                continue
            try:
                await placer.cancel_order(symbol=pos.symbol, order_id=order_id)
            except _op.OrderPlacementError as exc:
                log.warning(
                    "close_fsm: cancel_order failed uid={} signal_id={} "
                    "order_id={} exc={}",
                    uid, signal_id, order_id, exc,
                )

        # Place REDUCE_ONLY MARKET to close the remaining position.
        # ``reduceOnly=true`` is a safety net: if Binance already closed
        # the position (e.g. native SL fired milliseconds before we got
        # here), this will fail with -2022 "ReduceOnly Order is rejected"
        # which we absorb below rather than crashing.
        remaining = max(pos.total_qty - pos.closed_qty, pos.total_qty)
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
