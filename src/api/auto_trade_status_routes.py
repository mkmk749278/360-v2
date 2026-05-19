"""``GET /api/auto-trade/user-status`` — per-user auto-trade state.

Surfaces the user-facing status the Lumin app needs to render the
"your auto-trade is disabled" banner on the Trade tab.  Reads two
Firestore fields per request:

* ``users/{uid}.auto_trade_disabled`` — bool; True when the per-user
  circuit breaker has tripped (PR-8) OR an operator has manually
  disabled the user via the Telegram bot.
* ``kill_switch/global.auto_trade_globally_enabled`` — bool; False
  on fresh deploy until the operator explicitly flips the flag (#431
  no-staged-beta safety floor).

Both reads go through the KillSwitchClient's 5-second cache so this
endpoint is cheap even when the Lumin app polls aggressively on
Trade-tab refresh.

The response is intentionally minimal — just the booleans + a human-
readable reason when disabled.  The Lumin app's Trade-tab banner
renders the reason verbatim so a future doctrine change can update
the messaging without an app release.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from fastapi import Depends, FastAPI, HTTPException, status

from src.utils import get_logger

log = get_logger("api.auto_trade_status_routes")


def register(
    app: FastAPI,
    *,
    auth: Callable,
    identity_dep: Callable,
) -> None:
    """Wire ``GET /api/auto-trade/user-status`` onto the given app.

    Same wiring pattern as ``binance_connect_routes`` from PR-2 —
    auth dep gates access; identity dep resolves to the
    Firebase-authed user.
    """

    @app.get(
        "/api/auto-trade/user-status",
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def auto_trade_user_status(
        identity: Any = Depends(identity_dep),
    ) -> dict:
        """Return the user's auto-trade enablement state.

        Response shape:

            {
              "auto_trade_globally_enabled": bool,
              "auto_trade_user_disabled": bool,
              "disabled_reason": str | "",
              "disabled_at": str | null,  # ISO-8601 UTC if disabled
            }

        ``auto_trade_globally_enabled`` AND
        ``!auto_trade_user_disabled`` must both be true for the user
        to actually trade.  The Lumin app surfaces:

        * Banner "Auto-trade globally paused" when the global flag
          is False.
        * Banner "Your auto-trade is disabled: <reason>" when the
          user-specific flag is True.
        """
        # Local import — KillSwitchClient is the engine-side
        # singleton from PR-8 + PR-14, initialised by bootstrap.
        # Lazy import so this module loads even when the server-
        # side execution stack isn't enabled (legacy test paths).
        from src.execution import kill_switch as _kill_switch

        firebase_uid = _extract_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Auto-trade status requires Firebase sign-in. "
                    "Sign in with your Lumin account and try again."
                ),
            )

        if not _kill_switch.is_initialised():
            # Engine boot path that didn't wire the server-side
            # execution stack (no GCP env vars).  Default-safe
            # response: globally NOT enabled (auto-trade is off);
            # user not specifically disabled.  This matches the
            # default-deny doctrine + lets the Lumin app render
            # the "auto-trade globally paused" banner.
            return {
                "auto_trade_globally_enabled": False,
                "auto_trade_user_disabled": False,
                "disabled_reason": "",
                "disabled_at": None,
            }

        ks = _kill_switch.get_client()
        try:
            globally_enabled = ks.is_globally_enabled()
            user_disabled = ks.is_user_disabled(firebase_uid)
        except Exception as exc:
            log.exception(
                "auto_trade_user_status: Firestore read failed uid={}",
                firebase_uid,
            )
            # On Firestore failure, return the safe default rather
            # than 500 — the Lumin app can still render the legacy
            # client-side UI; only the banner is degraded.
            return {
                "auto_trade_globally_enabled": False,
                "auto_trade_user_disabled": False,
                "disabled_reason": f"status read failed: {type(exc).__name__}",
                "disabled_at": None,
            }
        return {
            "auto_trade_globally_enabled": bool(globally_enabled),
            "auto_trade_user_disabled": bool(user_disabled),
            "disabled_reason": "",
            "disabled_at": None,
        }


    @app.get(
        "/api/auto-trade/runtime-status",
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def auto_trade_runtime_status(
        identity: Any = Depends(identity_dep),
    ) -> dict:
        """Composite runtime status for the Live tab's "Auto-trade armed"
        card.  Superset of ``/api/auto-trade/user-status`` plus three
        fields the app needs to render a per-gate green/yellow/red:

            {
              "auto_trade_globally_enabled": bool,
              "auto_trade_user_disabled": bool,
              "binance_key_connected": bool,
              "user_mode": "live" | "paper" | "off" | null,
              "allowed_symbols": list[str],
              "armed": bool,            # all gates green
            }

        ``armed`` = ``globally_enabled AND !user_disabled AND
        binance_key_connected AND user_mode == "live"`` — the four gates
        the FSM checks before placing an order.  Symbol allowlist is
        per-signal (not per-user state), so it's surfaced as a list
        rather than collapsed into ``armed``.

        Lazy-loads kill_switch + firestore_keystore so this route still
        responds (default-safe) when the engine boots without GCP env.
        """
        from src.execution import kill_switch as _kill_switch
        from src.execution import tripwires as _tripwires

        firebase_uid = _extract_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Auto-trade runtime status requires Firebase sign-in."
                ),
            )

        # Reuse the per-user-status logic for the two kill-switch flags.
        globally_enabled = False
        user_disabled = False
        if _kill_switch.is_initialised():
            try:
                ks = _kill_switch.get_client()
                globally_enabled = bool(ks.is_globally_enabled())
                user_disabled = bool(ks.is_user_disabled(firebase_uid))
            except Exception:
                log.exception(
                    "runtime_status: kill switch read failed uid={}",
                    firebase_uid,
                )

        # Binance key connectivity — does the user have a Firestore key
        # blob?  Same read the new connect-status endpoint does, kept
        # local to avoid a self-call.
        binance_key_connected = False
        try:
            from src.security import firestore_keystore as _fk
            if _fk.is_initialised():
                try:
                    _fk.get_key_blob(firebase_uid)
                    binance_key_connected = True
                except _fk.KeyBlobNotFoundError:
                    binance_key_connected = False
        except Exception:
            log.exception(
                "runtime_status: keystore read failed uid={}", firebase_uid,
            )

        # Per-user mode — fetched from per-user overrides, falling
        # back to engine-global user_settings when unset.  Matches the
        # resolution order paper_order_manager uses for sizing.
        user_mode: Optional[str] = None
        try:
            from src.api import user_overrides as _uo
            override = _uo.operator_auto_trade_override()
            mode = override.get("mode")
            if isinstance(mode, str) and mode:
                user_mode = mode.lower()
        except Exception:
            log.exception("runtime_status: user override read failed")
        if user_mode is None:
            try:
                from src import user_settings as _us
                stored = _us.get_auto_trade()
                mode = stored.get("mode")
                if isinstance(mode, str) and mode:
                    user_mode = mode.lower()
            except Exception:
                pass

        # Symbol allowlist — re-read at request time so an operator
        # env-var change doesn't require an app refetch + the value
        # the app sees matches what the next order will be checked
        # against.
        allowlist = sorted(_tripwires._load_symbol_allowlist())

        armed = (
            globally_enabled
            and not user_disabled
            and binance_key_connected
            and user_mode == "live"
        )

        return {
            "auto_trade_globally_enabled": globally_enabled,
            "auto_trade_user_disabled": user_disabled,
            "binance_key_connected": binance_key_connected,
            "user_mode": user_mode,
            "allowed_symbols": allowlist,
            "armed": armed,
        }

    @app.get(
        "/api/auto-trade/positions",
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def auto_trade_positions(
        identity: Any = Depends(identity_dep),
    ) -> dict:
        """Return the user's open positions from Firestore.

        Response shape:

            {
              "positions": [
                {
                  "signal_id": str,
                  "symbol": str,
                  "side": "LONG" | "SHORT",
                  "state": str,
                  "entry_price_target": float,
                  "entry_price_filled": float,
                  "sl_price": float,
                  "tp1_price": float,
                  "total_qty": float,
                  "filled_qty": float,
                  "realized_pnl_total": float,
                  "pretp_fired": bool,
                  "created_at": str | null,   # ISO-8601 UTC
                },
                ...
              ]
            }

        Closed positions are excluded — the Live-tab card is meant to
        show what's *open right now*.  Historical PnL flows through
        the trade-records endpoint (TBD) which preserves terminal-state
        rows past their close.
        """
        from src.execution import position_state as _ps

        firebase_uid = _extract_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Auto-trade positions requires Firebase sign-in.",
            )

        if not _ps._db:
            # position_state not initialised — engine ran without
            # the server-side execution stack.  Empty list is the
            # safe-default response; the app renders "no open
            # positions" which is doctrinally accurate (the engine
            # isn't tracking any).
            return {"positions": []}

        try:
            positions = _ps.list_positions_for_user(firebase_uid)
        except _ps.PositionStateNotInitialisedError:
            return {"positions": []}
        except Exception:
            log.exception(
                "auto_trade_positions: Firestore read failed uid={}",
                firebase_uid,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not reach the position store. Please retry.",
            )

        return {
            "positions": [
                {
                    "signal_id": p.signal_id,
                    "symbol": p.symbol,
                    "side": p.side,
                    "state": p.state.value,
                    "entry_price_target": p.entry_price_target,
                    "entry_price_filled": p.entry_price_filled,
                    "sl_price": p.sl_price,
                    "tp1_price": p.tp1_price,
                    "total_qty": p.total_qty,
                    "filled_qty": p.filled_qty,
                    "realized_pnl_total": p.realized_pnl_total,
                    "pretp_fired": p.pretp_fired,
                    "created_at": (
                        p.created_at.isoformat()
                        if p.created_at is not None
                        else None
                    ),
                }
                for p in positions
            ],
        }


def _extract_firebase_uid(identity: Any) -> Optional[str]:
    """Same logic as binance_connect_routes — Firebase-authed users
    return their uid; static-token bypass / legacy JWT return None
    (this endpoint requires a Firebase identity)."""
    if identity is None:
        return None
    firebase_uid = getattr(identity, "firebase_uid", None)
    if isinstance(firebase_uid, str) and firebase_uid:
        return firebase_uid
    return None
