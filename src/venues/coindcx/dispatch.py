"""CoinDCX fan-out — the same signal, to users who chose CoinDCX.

Called by the router right after the Binance fan-out, with the same signal.
The Binance fan-out skips any user whose venue is ``coindcx`` and this one
skips anyone whose venue is not, so a user is dispatched on exactly one
exchange — the one they chose.

Gates, in the Binance fan-out's order and with its semantics (a test pins
the list), so choosing an exchange never changes *which* signals trade:

1. master switch ``COINDCX_EXECUTION_ENABLED`` (default OFF) and the rollout
   allow-list ``COINDCX_EXECUTION_ALLOWED_UIDS``;
2. venue chosen = coindcx (a venue we could not read resolves to Binance);
3. mode ``live``/``both`` (manual take skips);
4. tier ``auto`` (manual take: ``assist``);
5. auto-pause (manual take skips);
6. per-user path / regime preference (recorded as ``skipped``);
7. notional (same resolver, same noise-floor risk scale) and the B18 position cap;
8. the shared safety chain — global enable, kill switch, per-user disable,
   symbol allow-list, the user's own symbol preference, both circuit breakers,
   the per-user rate limit (``position_fsm._enforce_safety_gates``).
"""

from __future__ import annotations

import asyncio
from collections import Counter
from typing import Any, Dict, Optional

from src.utils import get_logger
from src.venues.coindcx import execution as _ex

log = get_logger("venues.coindcx.dispatch")

VENUE = "coindcx"
_TOTALS: Counter = Counter()


def totals() -> Dict[str, int]:
    return dict(_TOTALS)


def _allowed_uids() -> Optional[set]:
    from config import COINDCX_EXECUTION_ALLOWED_UIDS

    raw = [u.strip() for u in (COINDCX_EXECUTION_ALLOWED_UIDS or "").split(",")]
    uids = {u for u in raw if u}
    return uids or None


def execution_enabled() -> bool:
    from config import COINDCX_EXECUTION_ENABLED

    return bool(COINDCX_EXECUTION_ENABLED)


async def dispatch_signal(
    *,
    signal_id: str,
    symbol: str,
    direction: str,
    entry_price: float,
    sl_price: float,
    tp1_price: float,
    regime_label: Optional[str] = None,
    setup_class: Optional[str] = None,
    risk_scale: float = 1.0,
    _only_uid: Optional[str] = None,
    _manual: bool = False,
) -> Dict[str, Any]:
    """Fan one signal out to CoinDCX users.  Never raises.

    Returns ``{"placed": n, "outcomes": {uid: outcome}}``; for a manual take
    (``_only_uid``) the single outcome is also under ``"result"``.
    """
    _TOTALS["fanouts"] += 1
    if not execution_enabled():
        _TOTALS["skip:disabled"] += 1
        return _manual_refusal(_manual, "CoinDCXDisabled",
                               "CoinDCX auto-trade is not switched on yet.")
    try:
        if _only_uid:
            uids = [_only_uid]
        else:
            from src.venues.coindcx import keystore as _keys

            roster = await asyncio.to_thread(_keys.list_active_uids)
            if roster is None:
                _TOTALS["skip:roster_unreadable"] += 1
                log.warning("coindcx dispatch: roster unreadable — nobody dispatched")
                return {"placed": 0, "outcomes": {}}
            uids = roster
        allowed = _allowed_uids()
        if allowed is not None:
            uids = [u for u in uids if u in allowed]
        if not uids:
            return _manual_refusal(_manual, "NotAllowListed",
                                   "CoinDCX auto-trade is in owner-only testing.")

        from config import COINDCX_DISPATCH_CONCURRENCY

        sem = asyncio.Semaphore(max(1, int(COINDCX_DISPATCH_CONCURRENCY)))

        async def _bounded(uid: str) -> tuple[str, Dict[str, Any]]:
            async with sem:
                return uid, await _one_user(
                    uid=uid, signal_id=signal_id, symbol=symbol, direction=direction,
                    entry_price=entry_price, sl_price=sl_price, tp1_price=tp1_price,
                    regime_label=regime_label, setup_class=setup_class,
                    risk_scale=risk_scale, manual=_manual,
                )

        results = await asyncio.gather(*(_bounded(u) for u in uids))
    except Exception as exc:  # noqa: BLE001 — the router must never see a raise
        _TOTALS["crashed"] += 1
        log.exception("coindcx dispatch crashed signal={}", signal_id)
        _ex._fail_open("coindcx.dispatch", exc)
        return _manual_refusal(_manual, "InternalError", "CoinDCX dispatch failed.")

    outcomes = dict(results)
    placed = sum(1 for o in outcomes.values() if o.get("outcome") == "placed")
    for o in outcomes.values():
        _TOTALS[o.get("note") or o.get("outcome", "unknown")] += 1
    out: Dict[str, Any] = {"placed": placed, "outcomes": outcomes}
    if _only_uid:
        out["result"] = outcomes.get(_only_uid) or {
            "outcome": "rejected", "reject_class": "UnknownDispatchOutcome",
        }
    if outcomes:
        log.info("coindcx dispatch signal={} users={} placed={}", signal_id, len(outcomes), placed)
    return out


def _manual_refusal(manual: bool, cls: str, detail: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"placed": 0, "outcomes": {}}
    if manual:
        out["result"] = {"outcome": "rejected", "reject_class": cls,
                         "reject_detail": detail, "venue": VENUE}
    return out


async def _one_user(
    *,
    uid: str,
    signal_id: str,
    symbol: str,
    direction: str,
    entry_price: float,
    sl_price: float,
    tp1_price: float,
    regime_label: Optional[str],
    setup_class: Optional[str],
    risk_scale: float,
    manual: bool,
) -> Dict[str, Any]:
    from src.api import user_overrides as _uo
    from src.execution import dispatch_log as _dl
    from src.execution import signal_dispatch as _sd

    source = "manual_take" if manual else "auto"

    def _skip(note: str, cls: str = "", detail: str = "") -> Dict[str, Any]:
        out: Dict[str, Any] = {"outcome": "skipped", "note": f"skip:{note}", "venue": VENUE}
        if cls:
            out.update(reject_class=cls, reject_detail=detail)
        return out

    def _reject(cls: str, detail: str) -> Dict[str, Any]:
        _dl.record_rejected(
            firebase_uid=uid, signal_id=signal_id, symbol=symbol, direction=direction,
            entry_price=entry_price, reject_class=cls, reject_detail=detail,
            source=source, venue=VENUE,
        )
        return {"outcome": "rejected", "reject_class": cls, "reject_detail": detail,
                "note": f"rejected:{cls}", "venue": VENUE}

    # 2 — venue.  A user who did not choose CoinDCX (or whose choice we could
    # not read) is never sent a CoinDCX order.
    settings = await asyncio.to_thread(_uo.resolve_venue_settings_uid, uid)
    if settings.get("venue") != VENUE:
        return _skip(f"venue:{settings.get('reason')}", "VenueNotCoinDCX",
                     "Your trading platform is not set to CoinDCX.")

    # 3 — mode
    mode, _reason = _uo.resolve_user_mode_uid_detailed(uid)
    if not manual and mode not in ("live", "both"):
        return _skip("mode")

    # 4 — tier
    from config import AUTO_TRADE_TIER_GATE_ENABLED
    if AUTO_TRADE_TIER_GATE_ENABLED:
        from src.api.auth import can_assist, can_auto

        tier = _sd._resolve_user_tier(uid)
        if not (can_assist if manual else can_auto)(tier):
            return _skip("tier", "TierNotEntitled",
                         f"This needs the {'assist' if manual else 'auto'} plan "
                         f"(your plan: {tier}).")

    # 5 — auto-pause
    if not manual and _uo.is_user_auto_paused_uid(uid):
        return _skip("auto_paused")

    # 6 — per-signal preferences, recorded exactly like Binance's
    if not manual:
        path_pref, regime_pref = _uo.resolve_auto_trade_preferences_uid(uid)
        setup_tok = (setup_class or "").upper()
        if path_pref is not None and setup_tok not in path_pref:
            _dl.record_skipped(
                firebase_uid=uid, signal_id=signal_id, symbol=symbol, direction=direction,
                entry_price=entry_price, skip_reason="path_preference",
                skip_detail=f"{setup_tok or 'this setup'} is not in your auto-trade setup list.",
                source=source, venue=VENUE,
            )
            return _skip("path_pref")
        regime_tok = (regime_label or "").upper()
        if regime_pref is not None and regime_tok not in regime_pref:
            _dl.record_skipped(
                firebase_uid=uid, signal_id=signal_id, symbol=symbol, direction=direction,
                entry_price=entry_price, skip_reason="regime_preference",
                skip_detail=f"Market regime {regime_tok or 'unknown'} is not in your auto-trade regime list.",
                source=source, venue=VENUE,
            )
            return _skip("regime_pref")

    # 7 — size + the B18 position cap
    notional = _uo.resolve_notional_usd(uid, _sd._DEFAULT_NOTIONAL_USD)
    if 0.0 < risk_scale < 1.0:
        notional *= risk_scale
    from src.execution import tripwires as _tw
    try:
        _tw.assert_position_cap(
            notional_usd=notional, cap_usd=notional,
            max_cap_usd=_tw.DEFAULT_POSITION_CAP_MAX_USD,
        )
    except _tw.PositionCapExceeded as exc:
        return _reject("PositionCapExceeded", str(exc))

    # 8 — the shared safety chain (kill switch, allow-lists, breakers, rate limit)
    from src.execution import position_fsm as _fsm
    try:
        _fsm._enforce_safety_gates(firebase_uid=uid, symbol=symbol, signal_id=signal_id)
    except Exception as exc:  # typed refusals from the gate chain
        return _reject(type(exc).__name__, str(exc))

    outcome = await _ex.get_executor().open_position(
        uid=uid, signal_id=signal_id, symbol=symbol, direction=direction,
        entry=entry_price, sl=sl_price, tp1=tp1_price, notional_usdt=notional,
        margin_currency=str(settings.get("margin_currency") or "INR"),
        leverage=float(settings.get("leverage") or 5.0), source=source,
    )
    outcome = dict(outcome)
    outcome.setdefault("venue", VENUE)
    if outcome.get("outcome") == "placed":
        _dl.record_placed(
            firebase_uid=uid, signal_id=signal_id, symbol=symbol, direction=direction,
            entry_price=entry_price, total_qty=float(outcome.get("qty") or 0.0),
            source=source, venue=VENUE,
        )
        outcome["note"] = "placed"
        return outcome
    cls = str(outcome.get("reject_class") or "Rejected")
    if cls not in ("AlreadyActive", "AlreadyHandled"):
        _dl.record_rejected(
            firebase_uid=uid, signal_id=signal_id, symbol=symbol, direction=direction,
            entry_price=entry_price, reject_class=cls,
            reject_detail=str(outcome.get("reject_detail") or ""),
            source=source, venue=VENUE,
        )
    outcome["note"] = f"rejected:{cls}"
    return outcome


async def close_positions_for_signal(signal_id: str, *, reason: str) -> int:
    """Exit every live CoinDCX position on ``signal_id`` (the engine closed
    the signal).  ``invalidated`` spares users on the loose invalidation mode,
    exactly as the Binance close does.  Returns the number closed."""
    from src.api import user_overrides as _uo
    from src.venues.coindcx import positions as _pos

    try:
        live = await asyncio.to_thread(_pos.get_store().live_for_signal, signal_id)
    except Exception as exc:  # noqa: BLE001
        _ex._fail_open("coindcx.close_for_signal.read", exc)
        return 0
    closed = 0
    for p in live:
        if reason == "invalidated":
            mode = _uo.resolve_invalidation_mode_uid(p.uid, "standard")
            if mode == "loose":
                continue
        out = await _ex.get_executor().close_position(p.uid, signal_id, reason=reason)
        if out.get("outcome") == "closed":
            closed += 1
    return closed
