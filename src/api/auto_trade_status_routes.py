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
