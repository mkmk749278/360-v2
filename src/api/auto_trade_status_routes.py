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

import asyncio
import time
from typing import Any, Callable, Optional

from fastapi import Depends, FastAPI, HTTPException, status

from src.utils import get_logger

log = get_logger("api.auto_trade_status_routes")


def _active_path_names() -> list[str]:
    """Canonical, sorted list of user-selectable evaluator paths (setup
    classes) — the path analogue of the symbol allowlist.

    Sourced from ``ACTIVE_PATH_PORTFOLIO_ROLES`` so the app's path picker
    can never drift from the engine's actual emitting paths (CLAUDE.md
    flags the SetupClass values as stringly-coupled — single source of
    truth).  Auxiliary sub-evaluators intentionally excluded (they have
    no standalone portfolio role).  Resolved lazily so a missing import
    at boot never hard-fails the status endpoint.
    """
    try:
        from src.signal_quality import ACTIVE_PATH_PORTFOLIO_ROLES
        return sorted(sc.value for sc in ACTIVE_PATH_PORTFOLIO_ROLES)
    except Exception:
        return []


# The three regime buckets the app offers (mapped to backend regime
# labels server-side by ``_normalise_regime_input``).  Static — kept
# beside the path helper so both eligibility dimensions ship together.
_REGIME_OPTIONS: list[str] = ["TRENDING", "RANGING", "CHOPPY"]


# ---------------------------------------------------------------------------
# Per-user TTL cache for the runtime-status endpoint.
# The endpoint does 4–5 async reads (kill-switch, keystore, user row, mode,
# allowlist).  A 10 s TTL captures the polling pattern (app refreshes
# every 5–15 s) while staying fresh enough for armed/disarmed transitions.
# Invalidated explicitly when the user's mode changes via PUT
# /api/settings/user/auto-trade so a toggle is reflected on the next poll.
# ---------------------------------------------------------------------------

_RUNTIME_CACHE_TTL_S: float = 10.0
_runtime_cache: dict[str, tuple[dict, float]] = {}  # uid → (payload, mono)


def invalidate_runtime_cache(firebase_uid: str) -> None:
    """Drop the cached runtime-status for one user.

    Called from the PUT /api/settings/user/auto-trade handler so a mode
    toggle is reflected on the app's next runtime-status poll rather than
    waiting up to ``_RUNTIME_CACHE_TTL_S`` seconds.
    """
    _runtime_cache.pop(firebase_uid, None)


def register(
    app: FastAPI,
    *,
    auth: Callable,
    identity_dep: Callable,
    get_engine: Optional[Callable[[], Any]] = None,
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
            # 5s-cached, but a cache-miss is a blocking Firestore read —
            # thread it off the shared loop on this per-poll path.
            globally_enabled = await asyncio.to_thread(ks.is_globally_enabled)
            user_disabled = await asyncio.to_thread(
                ks.is_user_disabled, firebase_uid
            )
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
        card.  Superset of ``/api/auto-trade/user-status`` plus the
        fields the app needs to render a per-gate green/yellow/red:

            {
              "auto_trade_globally_enabled": bool,
              "auto_trade_user_disabled": bool,
              "binance_key_connected": bool,
              "user_mode": "live" | "paper" | "off" | null,
              "user_tier": "free|assist|auto|paid|all-access|owner",
              "tier_gate_enabled": bool,
              "tier_allows_auto": bool,
              "auto_paused": bool,       # dispatcher pause (paused_reason set)
              "path_preference": list[str] | null,    # null=all, []=block-all
              "regime_preference": list[str] | null,
              "preferences_block_all": bool,
              "allowed_symbols": list[str],
              "armed": bool,            # all user-state gates green
            }

        ``armed`` = ``globally_enabled AND !user_disabled AND
        binance_key_connected AND user_mode in ("live", "both") AND
        tier_allows_auto AND !auto_paused AND !preferences_block_all``
        — every USER-STATE gate the dispatcher checks before placing an
        order, including the three that skip silently with no
        dispatch-activity row (tier, auto-pause, block-all prefs; added
        2026-07-17 after the card showed all-green over a silent tier
        skip).  "both" fires real Binance orders AND runs the paper
        simulator simultaneously, so it counts as armed.  The symbol
        allowlist and a restrictive-but-non-empty path/regime preference
        are per-signal filters (orders remain possible), so they're
        surfaced as data rather than collapsed into ``armed``.

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

        # Fast path: serve cached payload if it's still fresh.
        _cached = _runtime_cache.get(firebase_uid)
        if _cached is not None:
            _payload, _written = _cached
            if time.monotonic() - _written < _RUNTIME_CACHE_TTL_S:
                return _payload

        # Reuse the per-user-status logic for the two kill-switch flags.
        globally_enabled = False
        user_disabled = False
        if _kill_switch.is_initialised():
            try:
                ks = _kill_switch.get_client()
                # Kill-switch reads are 5s-cached, but a cache-miss does a
                # blocking Firestore read — thread both so a cold read on
                # this per-poll path can't stall the shared event loop.
                globally_enabled = bool(
                    await asyncio.to_thread(ks.is_globally_enabled)
                )
                user_disabled = bool(
                    await asyncio.to_thread(ks.is_user_disabled, firebase_uid)
                )
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
                    # Blocking Firestore read — thread it off the loop.
                    await asyncio.to_thread(_fk.get_key_blob, firebase_uid)
                    binance_key_connected = True
                except _fk.KeyBlobNotFoundError:
                    binance_key_connected = False
        except Exception:
            log.exception(
                "runtime_status: keystore read failed uid={}", firebase_uid,
            )

        # Per-user mode — read THIS user's row from
        # ``user_auto_trade_settings``, keyed by ``firebase_uid →
        # user_id``.
        #
        # Pre-2026-05-23 this consulted
        # ``operator_auto_trade_override()`` (which returns the
        # most-recently-updated row across the *whole* table — a
        # single-operator MVP shortcut for engine-side consumers that
        # don't know which user_id to look up) and then fell back to
        # the engine-global ``user_settings.get_auto_trade()``.  Both
        # paths leak operator/engine-wide state into every user's
        # response.  Visible consequences owner reported 2026-05-23
        # ("many owner changes are applying to all users"):
        #
        #   1. Owner flips mode → paper on their device → every other
        #      authenticated user's runtime-status returns
        #      ``user_mode = "paper"`` because they read the SAME
        #      most-recently-updated row.  Lumin's Pulse tab keys its
        #      "Trading not enabled" CTA off that field, so brand-new
        #      users saw the engine 30-day chart + a $0.00 PnL card
        #      instead of the CTA.
        #   2. ``armed`` was evaluated against the operator's mode,
        #      so the Live-tab armed badge lit green for users who
        #      had no Binance key connected.
        #
        # Correct behaviour: resolve firebase_uid → user_id → read
        # the per-user row.  Users without a row (haven't opted in
        # via the Trade tab) get ``user_mode = None`` → ``armed =
        # false`` → Pulse renders the not-enabled CTA.  No fallback
        # to operator / engine-global state — both of those are
        # operator config, never user state.
        #
        # The same two reads (user row + auto-trade row) also carry
        # every field the dispatcher's SILENT skip gates consume —
        # tier/paid_until (entitlement gate), paused_reason
        # (auto-pause gate), path/regime preference (eligibility
        # gates).  Computing their verdicts here costs zero extra
        # reads and stops the armed card lying: pre-2026-07-17 the
        # card showed all-green while dispatch silently skipped a
        # lapsed/free-tier user before any dispatch-activity row
        # (owner-reported: "connected and ARMED but trading not
        # happening", zero recent activity).
        user_mode: Optional[str] = None
        user_tier: str = "free"  # fail closed, same direction as dispatch
        auto_paused: bool = False
        path_preference: Optional[list[str]] = None
        regime_preference: Optional[list[str]] = None
        try:
            from src.api import user_overrides as _uo
            from src.api import users as _users
            from src.api.auth import effective_tier as _effective_tier

            user_store = _users.get_singleton()
            override_store = _uo.get_singleton()
            if user_store is not None and override_store is not None:
                user = await user_store.aget_by_firebase_uid(firebase_uid)
                if user is not None:
                    user_tier = _effective_tier(
                        getattr(user, "tier", None),
                        getattr(user, "paid_until", None),
                    )
                    row = await override_store.aget_auto_trade(int(user.user_id))
                    mode = row.get("mode")
                    if isinstance(mode, str) and mode:
                        user_mode = mode.lower()
                    # Same predicate as is_user_auto_paused: any
                    # non-null paused_reason means the dispatcher
                    # skips this user until they resume.
                    auto_paused = bool(row.get("paused_reason"))
                    # None = no preference (all eligible); [] is a
                    # meaningful explicit block-all — mirror the
                    # dispatcher's resolve_auto_trade_preferences_uid
                    # semantics exactly (uppercase compare tokens).
                    _path_raw = row.get("path_preference")
                    if isinstance(_path_raw, list):
                        path_preference = sorted(
                            str(s).upper() for s in _path_raw
                        )
                    _regime_raw = row.get("regime_preference")
                    if isinstance(_regime_raw, list):
                        regime_preference = sorted(
                            str(r).upper() for r in _regime_raw
                        )
        except Exception:
            log.exception(
                "runtime_status: per-user mode read failed uid={}",
                firebase_uid,
            )

        # Tier gate verdict — definitionally the same rule the dispatch
        # money path applies (auth.effective_tier ↔ signal_dispatch.
        # _resolve_user_tier stay in lockstep).  Read the flag inside
        # the handler so ops env flips and tests take effect without a
        # process restart of this module's import-time state.
        import config as _config

        tier_gate_enabled = bool(
            getattr(_config, "AUTO_TRADE_TIER_GATE_ENABLED", True)
        )
        from src.api.auth import can_auto as _can_auto

        tier_allows_auto = (not tier_gate_enabled) or _can_auto(user_tier)
        # An explicit empty preference set blocks every signal — the
        # only preference state that guarantees zero orders, so it
        # unarms.  A restrictive-but-non-empty set stays armed (it's a
        # per-signal filter, surfaced for the app to render as a
        # warning, mirroring how allowed_symbols is presented).
        preferences_block_all = path_preference == [] or regime_preference == []

        # Symbol allowlist — re-read at request time so an operator
        # env-var change doesn't require an app refetch + the value
        # the app sees matches what the next order will be checked
        # against.  ``allowed_symbols`` is the engine-wide cap;
        # ``effective_allowed_symbols`` is the intersection with this
        # user's symbol_preference (defaults to engine-wide when the
        # user has set no preference).
        allowlist_set = _tripwires._load_symbol_allowlist()
        if not allowlist_set and get_engine is not None:
            # Isolated-mode display truth (2026-07-18, same container class
            # as the KMS-init bug #736): the PairManager singleton lives in
            # the ENGINE process, so this api container's in-process
            # resolution returns the block-all empty set and every user
            # rendered "Watching 0 symbols" while the engine container was
            # trading a full universe.  Fall back to the engine-published
            # pairs snapshot (regular + mover-promoted) — the same source
            # /api/pairs serves.  Display-only: real order gating runs
            # engine-side where the singleton exists.
            try:
                _eng = get_engine()
                _pp = (
                    _eng.published_pairs()
                    if hasattr(_eng, "published_pairs")
                    else None
                )
                if isinstance(_pp, dict):
                    allowlist_set = {
                        str(row.get("symbol", "")).upper()
                        for group in ("regular", "promoting")
                        for row in (_pp.get(group) or [])
                        if isinstance(row, dict) and row.get("symbol")
                    }
            except Exception:
                log.exception(
                    "runtime_status: pairs-snapshot allowlist fallback failed"
                )
        allowlist = sorted(allowlist_set)
        try:
            # Helper does two synchronous SQLite reads (user row +
            # auto-trade row) — run off the event loop.
            effective = await asyncio.to_thread(
                _tripwires.effective_allowed_symbols_for_user,
                firebase_uid,
                allowlist=allowlist_set,
            )
        except Exception:
            log.exception(
                "runtime_status: effective allowlist resolution failed uid={}",
                firebase_uid,
            )
            effective = allowlist

        # Full conjunction of every USER-STATE gate the dispatcher
        # checks before an order — tightened 2026-07-17 to include the
        # three gates that previously skipped silently (tier,
        # auto-pause, block-all preferences).  Deliberately tightened
        # in place rather than versioned: the change is strictly
        # green→yellow (it can only remove a false positive), and old
        # app builds already render armed=false with green legacy rows
        # (their client-side pause AND), so they degrade to an honest
        # badge that under-explains, never a lying one.
        armed = (
            globally_enabled
            and not user_disabled
            and binance_key_connected
            and user_mode in ("live", "both")
            and tier_allows_auto
            and not auto_paused
            and not preferences_block_all
        )

        result = {
            "auto_trade_globally_enabled": globally_enabled,
            "auto_trade_user_disabled": user_disabled,
            "binance_key_connected": binance_key_connected,
            "user_mode": user_mode,
            "user_tier": user_tier,
            "tier_gate_enabled": tier_gate_enabled,
            "tier_allows_auto": tier_allows_auto,
            "auto_paused": auto_paused,
            "path_preference": path_preference,
            "regime_preference": regime_preference,
            "preferences_block_all": preferences_block_all,
            "allowed_symbols": allowlist,
            "effective_allowed_symbols": effective,
            "allowed_paths": _active_path_names(),
            "regime_options": _REGIME_OPTIONS,
            "armed": armed,
        }
        _runtime_cache[firebase_uid] = (result, time.monotonic())
        return result

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
            # list_positions_for_user does a synchronous Firestore
            # .stream() — run it off the event loop so a slow Firestore
            # round-trip doesn't freeze every other request.
            positions = await asyncio.to_thread(
                _ps.list_positions_for_user, firebase_uid
            )
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


    @app.get(
        "/api/auto-trade/recent-events",
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def auto_trade_recent_events(
        identity: Any = Depends(identity_dep),
        limit: int = 20,
    ) -> dict:
        """Return the user's recent dispatch events (placed + rejected),
        newest first.  Drives the Trade-tab Recent Activity card so
        users can see why a signal didn't open on their Binance
        account (most commonly: ``-2019 'Margin is insufficient'``
        → empty Futures wallet; ``-2014`` → IP whitelist changed; etc.).

        Response shape::

            {
              "events": [
                {
                  "event_id": str,
                  "signal_id": str,
                  "symbol": str,
                  "direction": "LONG" | "SHORT",
                  "outcome": "placed" | "rejected",
                  "timestamp": str (ISO-8601 UTC),
                  "entry_price": float,
                  "total_qty": float,
                  "reject_class": str | null,
                  "reject_detail": str | null,
                  "reject_binance_code": int | null,
                  "reject_binance_msg": str | null,
                }, ...
              ]
            }

        ``limit`` capped server-side at 100 to bound query cost.
        Returns ``{"events": []}`` when the dispatch_log isn't
        initialised (engine boot without GCP env) — UI gracefully
        renders the empty-state copy.
        """
        from src.execution import dispatch_log as _dl

        firebase_uid = _extract_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Recent events requires Firebase sign-in. "
                    "Sign in with your Lumin account and try again."
                ),
            )

        # list_recent_events does a blocking Firestore query.stream() —
        # thread it so this per-visit Trade-tab poll can't stall the loop.
        events = await asyncio.to_thread(
            _dl.list_recent_events, firebase_uid, limit=limit
        )
        return {
            "events": [
                {
                    "event_id": e.event_id,
                    "signal_id": e.signal_id,
                    "symbol": e.symbol,
                    "direction": e.direction,
                    "outcome": e.outcome,
                    "timestamp": (
                        e.timestamp.isoformat()
                        if e.timestamp is not None
                        else None
                    ),
                    "entry_price": e.entry_price,
                    "total_qty": e.total_qty,
                    "reject_class": e.reject_class,
                    "reject_detail": e.reject_detail,
                    "reject_binance_code": e.reject_binance_code,
                    "reject_binance_msg": e.reject_binance_msg,
                    "source": e.source,
                }
                for e in events
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
