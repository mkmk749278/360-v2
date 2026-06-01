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

# TP qty split — sums to 100%.  Two legs only (TP3 removed per owner
# directive 2026-05-26): TP1 takes the first 30%, TP2 closes the
# remainder.  When pre-TP fires first (the typical path), TP2 is
# cancelled and the residual rides toward TP1 with SL at BE.
# FSM skips placement for any leg with qty <= 0.
_TP1_FRACTION = 0.30
_TP2_FRACTION = 0.70
_TP3_FRACTION = 0.00

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
    # Rounding residual: the last active TP leg absorbs the dust so
    # tp1+tp2+tp3 == total_qty exactly (Binance rejects non-reconciling
    # order sets).  With _TP3_FRACTION=0.00 (TP3 removed), the residual
    # goes to TP2; otherwise tp3 gets it and FSM skips tp3 when qty=0.
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
    regime_label: Optional[str] = None,
    setup_class: Optional[str] = None,
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
        # Per-user invalidation aggressiveness (B17).  Stored on the
        # Position at placement time so the per-user FSM path can
        # enforce the correct mode when per-user soft-invalidation
        # lands.  The engine-wide TradeMonitor still uses
        # INVALIDATION_MODE_DEFAULT for the engine's signal book;
        # this field is forwarded to the per-user Position only.
        user_invalidation_mode = _uo.resolve_invalidation_mode_uid(
            uid, str(_DEFAULT_INV_MODE or "standard")
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
            )
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
                pretp_threshold_pct=user_pretp_threshold,
                pretp_fraction=user_grab_fraction,
                invalidation_mode=user_invalidation_mode,
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
    excluded_modes: Optional[frozenset] = None,
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

        # Per-user invalidation mode filter: loose-mode users survive
        # engine invalidation; their native SL/TP bracket is still live.
        if excluded_modes and pos.invalidation_mode in excluded_modes:
            log.info(
                "close_fsm: skipping uid={} signal_id={} "
                "invalidation_mode={} excluded by caller (reason={})",
                uid, signal_id, pos.invalidation_mode, reason,
            )
            continue

        placer = _op.OrderPlacer(uid)

        # Cancel all open bracket orders — tolerant of -2011/-20121 (already
        # gone, filled, or expired).  Cancel first so the MARKET close
        # below doesn't fight with a pending SL/TP that might otherwise
        # also close the position and over-reduce.
        # SL and TP orders are algo orders (placed via /fapi/v1/algoOrder);
        # cancel via cancel_algo_order, not cancel_order.
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
            await placer.cancel_algo_order(symbol=pos.symbol, algo_id=order_id)
        except _op.OrderPlacementError as exc:
            log.warning(
                "close_single_fsm: cancel_algo_order failed uid={} signal_id={} "
                "algo_id={} exc={}",
                uid, signal_id, order_id, exc,
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
