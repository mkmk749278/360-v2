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


# ---------------------------------------------------------------------------
# Marking an open position — where the live price comes from
# ---------------------------------------------------------------------------


async def _live_marks(get_engine: Optional[Callable[[], Any]]) -> tuple[dict, Optional[float]]:
    """``({symbol: price}, stamped_at_epoch | None)`` for pricing open rows.

    Two sources, one meaning.  In single-process mode the mark-price feed is
    in this process.  In isolated mode (live on the VPS) it is not — the api
    container has no feed and no signing socket — so the engine publishes its
    marks to ``snapshot:position_marks`` and this reads them.

    ``stamped_at`` is returned rather than assumed, and the caller puts it on
    the wire.  A mark with no age beside it is the defect ops paid for on
    2026-07-30: a live-looking price printed next to state from another clock,
    under the word "now".  An empty mapping is a legitimate answer — nothing
    open, nothing subscribed — and is not the same as a failure to read, which
    returns an empty mapping with ``None`` for the stamp and makes every row
    render its mark as unknown rather than as absent.
    """
    # In-process first: it is the freshest thing available and needs no hop.
    try:
        from src.execution import mark_price_feed as _mpf

        feed = _mpf.get_instance()
        if feed is not None:
            prices = {
                sym: float(px)
                for sym, px in feed.all_prices().items()
                if isinstance(px, (int, float)) and px > 0
            }
            if prices:
                return prices, time.time()
    except Exception:
        log.debug("_live_marks: in-process feed unavailable", exc_info=True)

    engine = get_engine() if get_engine is not None else None
    reader = getattr(engine, "read_position_marks", None)
    if reader is None:
        return {}, None
    try:
        payload = await reader()
    except Exception:
        log.warning("_live_marks: snapshot read failed", exc_info=True)
        return {}, None
    if not isinstance(payload, dict):
        return {}, None
    stamped = payload.get("__stamped_at__")
    prices = {
        sym: float(px)
        for sym, px in payload.items()
        if sym != "__stamped_at__" and isinstance(px, (int, float)) and px > 0
    }
    return prices, (float(stamped) if isinstance(stamped, (int, float)) else None)


async def _exchange_book(
    get_engine: Optional[Callable[[], Any]], firebase_uid: str
) -> tuple[dict, Optional[float], str]:
    """``({symbol: row}, stamped_at, state)`` — what BINANCE says this user
    holds.

    ``state`` is the part that matters, and it has three values because an
    empty book has three causes with three different next moves:

    * ``"reporting"`` — the engine is publishing and this is the account. An
      empty book here really does mean no open positions.
    * ``"not_reported"`` — the engine is publishing and has never heard
      anything about this user: no worker running, or nothing since boot.
    * ``"unavailable"`` — we could not read at all (engine stopped publishing,
      Redis down, or an engine that predates the key).

    Collapsing those renders a cold engine as a flat account, which is the
    exact confusion this endpoint exists to end.
    """
    # Single-process mode: the index is in this process.
    try:
        from src.execution import exchange_positions as _xp

        if _xp.get_generation() > 0:
            return (_xp.for_user(firebase_uid), time.time(), "reporting")
    except Exception:
        log.debug("_exchange_book: in-process index unavailable", exc_info=True)

    engine = get_engine() if get_engine is not None else None
    reader = getattr(engine, "read_exchange_positions", None)
    if reader is None:
        return ({}, None, "unavailable")
    try:
        payload = await reader()
    except Exception:
        log.warning("_exchange_book: snapshot read failed", exc_info=True)
        return ({}, None, "unavailable")
    if not isinstance(payload, dict):
        return ({}, None, "unavailable")
    users = payload.get("users")
    if not isinstance(users, dict):
        return ({}, None, "unavailable")
    stamped = payload.get("stamped_at")
    book = users.get(firebase_uid)
    return (
        book if isinstance(book, dict) else {},
        float(stamped) if isinstance(stamped, (int, float)) else None,
        "reporting" if isinstance(book, dict) else "not_reported",
    )


def _unrealized(side: str, entry: float, mark: float, qty: float) -> tuple:
    """``(pnl_usd, pnl_pct)`` on the position, or ``(None, None)``.

    ``pnl_pct`` is the move on the ENTRY PRICE — the same thing Binance's own
    position row calls the price change, and the same thing the signal card
    beside it shows.  It is deliberately NOT divided by the stop distance:
    this engine sizes at a fixed notional, so R equalises nothing here and
    would put a number on screen that disagrees with both Binance and the
    feed (see the repo's "PnL % leads; R is the bridge" rule).
    """
    if entry <= 0 or mark <= 0 or qty <= 0:
        return (None, None)
    direction = 1.0 if str(side).upper() == "LONG" else -1.0
    pct = direction * (mark - entry) / entry * 100.0
    return (round(direction * (mark - entry) * qty, 8), round(pct, 4))


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
        # Readability travels WITH the value.  These two booleans are False
        # for three different worlds — the store was never initialised in this
        # process, the Firestore read raised, or the flag is honestly off — and
        # the app rendered all three as "a safety pause is active for all
        # accounts … trading resumes automatically", telling a user whose key
        # IS connected to go and connect one (owner screenshot 2026-09-02).
        # Two of those worlds never resume and neither is a safety pause.
        globally_enabled = False
        user_disabled = False
        flags_readable = False
        key_readable = False
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
                flags_readable = True
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
                    # Presence only — this field answers "does a key
                    # document exist", never "give me the key".  It used to
                    # call get_key_blob, fetching (and discarding) an
                    # encrypted secret on every poll.  has_key caches the
                    # boolean and every writer invalidates it, so a fresh
                    # connect still shows at once.
                    #
                    # The "~8,600 reads a day from one open Trade tab" figure
                    # first written here was INFERRED from an assumed 10s poll
                    # and is wrong: grep for Timer.periodic in lumin-app finds
                    # no runtime-status poll at all — the Trade tab fetches on
                    # open and pull-to-refresh behind a 60s SWR cache.  Right
                    # cut, invented number.
                    binance_key_connected = bool(
                        await asyncio.to_thread(_fk.has_key, firebase_uid)
                    )
                    key_readable = True
                except _fk.KeyBlobNotFoundError:
                    binance_key_connected = False
                    key_readable = True
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
            # Whether we could OBSERVE the two fields above.  False means the
            # value beside it is a default, not an answer — the app must not
            # promise an automatic resume it cannot see coming, and must not
            # tell a user to connect a key it could not check for.
            "global_flags_readable": bool(flags_readable),
            "binance_key_readable": bool(key_readable),
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

    @app.post(
        "/api/auto-trade/resume-disabled-mine",
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def auto_trade_resume_disabled_mine(
        identity: Any = Depends(identity_dep),
    ) -> dict:
        """Self-service recovery from a per-user breaker disable
        (owner-approved 2026-07-18).

        The per-user circuit breaker (B18 #5) persists its disable in
        Firestore; until this endpoint the only recovery was the owner-run
        ``/api/admin/users/auto-trade-enable`` — a support round-trip and
        subscriber downtime for every trip.  The paused card's
        "Re-enable auto-trade" button calls this instead: the signed-in
        user clears their OWN flag, rate-limited to once per
        ``AUTO_TRADE_SELF_REENABLE_COOLDOWN_HOURS`` (default 6) so a
        genuinely failing account can't flap through a failure storm.
        Blast radius is unchanged — the breaker re-trips on new
        qualifying failures exactly as before, and user-setup rejections
        (-2019 / -4411) never feed it (#740).

        Response: ``{ok, auto_trade_disabled, already_enabled}``.
        429 with a human-readable retry hint inside the cooldown.
        """
        from datetime import datetime, timedelta, timezone

        from src.execution import kill_switch as _kill_switch

        firebase_uid = _extract_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=(
                    "Re-enabling auto-trade requires Firebase sign-in. "
                    "Sign in with your Lumin account and try again."
                ),
            )
        if not _kill_switch.is_initialised():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="auto-trade controls are not available right now",
            )
        ks = _kill_switch.get_client()

        disabled = bool(
            await asyncio.to_thread(ks.is_user_disabled, firebase_uid)
        )
        if not disabled:
            # Nothing to do — surface honestly so the app can just
            # refresh its status instead of showing an error.
            return {
                "ok": True,
                "auto_trade_disabled": False,
                "already_enabled": True,
            }

        import config as _config

        cooldown_hours = float(
            getattr(_config, "AUTO_TRADE_SELF_REENABLE_COOLDOWN_HOURS", 6.0)
        )
        last = await asyncio.to_thread(
            ks.last_self_reenable_at, firebase_uid
        )
        if last is not None and cooldown_hours > 0:
            try:
                now = datetime.now(timezone.utc)
                elapsed = now - last
                remaining = timedelta(hours=cooldown_hours) - elapsed
                if remaining.total_seconds() > 0:
                    mins = max(1, int(remaining.total_seconds() // 60))
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=(
                            f"You already re-enabled auto-trade recently. "
                            f"Try again in about {mins} minutes, or contact "
                            f"support if this keeps happening."
                        ),
                    )
            except HTTPException:
                raise
            except Exception:
                # Malformed/legacy timestamp → treat as no prior
                # self-re-enable rather than locking the user out.
                log.exception(
                    "resume_disabled_mine: cooldown read failed uid={}",
                    firebase_uid,
                )

        await asyncio.to_thread(ks.enable_user, firebase_uid)
        await asyncio.to_thread(ks.record_self_reenable, firebase_uid)
        disabled_now = bool(
            await asyncio.to_thread(ks.is_user_disabled, firebase_uid)
        )
        invalidate_runtime_cache(firebase_uid)
        log.warning(
            "resume_disabled_mine: uid={} self re-enabled "
            "(read_back_disabled={})",
            firebase_uid, disabled_now,
        )
        return {
            "ok": not disabled_now,
            "auto_trade_disabled": disabled_now,
            "already_enabled": False,
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
        show what's *open right now*.  What each of them CLOSED as is
        ``/api/auto-trade/signal-outcomes``, which joins the terminal
        position document to the dispatch event by signal id.

        **Marked live since 2026-09-01** (owner: *"there we have to show
        exactly how live open traded position shows in binance"*).  Until
        then this returned the entry price and the geometry and nothing about
        what the position is worth now, so the Trade tab could not render what
        the Binance app renders and the user had to leave to find out.  Each
        row now carries ``mark_price``, ``unrealized_pnl``,
        ``unrealized_pnl_pct`` and ``notional`` — priced by the ENGINE (see
        ``_live_marks``), never by the caller, so the price and the position
        state are on one clock.

        ``marks_stamped_at`` / ``marks_age_sec`` ride the envelope rather than
        the rows, because they describe the read and not any one position, and
        a row whose symbol the engine is not marking has ``mark_price: null``
        — a real state (the feed dropped the symbol) that must not read as a
        price of zero.
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

        marks, stamped_at = await _live_marks(get_engine)
        exchange, ex_stamped_at, ex_state = await _exchange_book(
            get_engine, firebase_uid
        )
        seen_symbols: set = set()

        rows = []
        for p in positions:
            ex = exchange.get(p.symbol) or {}
            seen_symbols.add(p.symbol)

            # SIZE AND ENTRY COME FROM THE EXCHANGE when it has told us, and
            # from the engine's own record only when it has not.  That order
            # is the point of this endpoint: the document says what the engine
            # SET UP, and after a partial fill, a manual close or the two-hour
            # backstop that is not what the account holds.  ``qty_source``
            # says which one answered, because a number whose origin the
            # reader cannot see is one they cannot check.
            ex_amount = ex.get("position_amount")
            ex_open = bool(ex.get("is_open"))
            if ex_open and isinstance(ex_amount, (int, float)):
                open_qty = abs(float(ex_amount))
                qty_source = "exchange"
            else:
                open_qty = max(0.0, p.total_qty - p.closed_qty)
                qty_source = "engine"

            ex_entry = ex.get("entry_price")
            if isinstance(ex_entry, (int, float)) and ex_entry > 0:
                entry = float(ex_entry)
                entry_source = "exchange"
            else:
                entry = (
                    p.entry_price_filled
                    if p.entry_price_filled > 0
                    else p.entry_price_target
                )
                entry_source = "engine"

            mark = marks.get(p.symbol)
            pnl_usd, pnl_pct = (
                _unrealized(p.side, entry, mark, open_qty)
                if mark is not None
                else (None, None)
            )

            # The divergence the owner was looking at: an ACTIVE signal on one
            # tab over an empty Trade tab, with nothing anywhere joining the
            # two.  Named here rather than left to be inferred from two nulls,
            # and only asserted when the exchange is actually reporting — an
            # engine that has said nothing is not evidence of anything.
            divergence = None
            if ex_state == "reporting":
                if ex and not ex_open:
                    divergence = "exchange_flat"
                elif not ex:
                    divergence = "exchange_silent"

            rows.append({
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
                # --- what Binance shows beside a position -------------------
                "open_qty": open_qty,
                "entry_price": entry or None,
                "mark_price": mark,
                "notional": (
                    round(mark * open_qty, 8) if mark is not None else None
                ),
                "unrealized_pnl": pnl_usd,
                "unrealized_pnl_pct": pnl_pct,
                # --- the exchange's own columns, from the exchange ----------
                "liquidation_price": ex.get("liquidation_price"),
                "leverage": ex.get("leverage"),
                "margin_type": ex.get("margin_type"),
                "exchange_unrealized_pnl": ex.get("exchange_unrealized_pnl"),
                "exchange_push_age_sec": ex.get("push_age_sec"),
                "exchange_flat_since_epoch": ex.get("flat_since_epoch"),
                "qty_source": qty_source,
                "entry_source": entry_source,
                "divergence": divergence,
                # Closeable only while the exchange still holds something, and
                # only when it is actually reporting: a close against a flat
                # position is a -2022 and a confusing snackbar.  Where the
                # exchange is silent we defer to the engine rather than hiding
                # the button on a position that may well be open.
                "closeable": (
                    open_qty > 0
                    and p.state.value not in ("PENDING", "PENDING_ENTRY")
                    and not (ex_state == "reporting" and ex and not ex_open)
                ),
            })

        # Positions BINANCE holds that the engine has no live record for.
        # Never merged into ``positions`` — they carry no signal, no stop and
        # no target, so every field a managed row renders is absent — and
        # never dropped either: an unmanaged position on a subscriber's
        # account is the most important thing this endpoint can say, and it
        # was invisible on every surface we have.
        unmanaged = []
        if ex_state == "reporting":
            for symbol, ex_row in exchange.items():
                if symbol in seen_symbols or not ex_row.get("is_open"):
                    continue
                amount = float(ex_row.get("position_amount") or 0.0)
                ex_mark = marks.get(symbol)
                ex_px = float(ex_row.get("entry_price") or 0.0)
                qty = abs(amount)
                u_usd, u_pct = (
                    _unrealized(str(ex_row.get("side") or ""), ex_px,
                                ex_mark, qty)
                    if ex_mark is not None and ex_px > 0
                    else (None, None)
                )
                unmanaged.append({
                    "symbol": symbol,
                    "side": ex_row.get("side"),
                    "open_qty": qty,
                    "entry_price": ex_px or None,
                    "mark_price": ex_mark,
                    "unrealized_pnl": u_usd,
                    "unrealized_pnl_pct": u_pct,
                    "liquidation_price": ex_row.get("liquidation_price"),
                    "leverage": ex_row.get("leverage"),
                    "margin_type": ex_row.get("margin_type"),
                    "exchange_push_age_sec": ex_row.get("push_age_sec"),
                })

        return {
            "positions": rows,
            "unmanaged": unmanaged,
            # About the READ, not about any row — see the docstring.
            "marks_stamped_at": stamped_at,
            "marks_age_sec": (
                round(time.time() - stamped_at, 1)
                if stamped_at is not None
                else None
            ),
            # Three states, never two: see ``_exchange_book``.
            "exchange_state": ex_state,
            "exchange_age_sec": (
                round(time.time() - ex_stamped_at, 1)
                if ex_stamped_at is not None
                else None
            ),
        }


    @app.get(
        "/api/auto-trade/signal-outcomes",
        tags=["auto-mode"],
        dependencies=[Depends(auth)],
    )
    async def auto_trade_signal_outcomes(
        identity: Any = Depends(identity_dep),
        limit: int = 40,
    ) -> dict:
        """What happened to each recent signal ON THIS USER'S ACCOUNT.

        Owner, 2026-08-31: *"why don't we show actually same like signal
        it's outcome — actually what traded in binance, so the user can
        understand what the engine produced and what's traded in
        binance"*.

        The two halves already existed and had never been joined.  The
        Signals tab renders the ENGINE's object (entry / SL / TP and a
        live mark) and says so in its own subtitle — *"All Lumin signals
        · Your own trades → Trade tab"*.  The Trade tab renders the
        USER's object, and its only per-signal record was the dispatch
        *event*, which is a record of a placement ATTEMPT: it carries no
        fill, no PnL and no close state, which is why a placed row
        asserts "Position is open" in the present tense forever and can
        sit directly under "YOUR OPEN POSITIONS 0".

        This endpoint is the join, keyed by ``signal_id`` so the app can
        put the user's own outcome on the signal card itself:

            {
              "outcomes": [
                {
                  "signal_id": str,
                  "symbol": str,
                  "direction": "LONG" | "SHORT",
                  "status": "open" | "closed" | "not_traded",
                  "state": str | null,          # FSM state, when a position exists
                  "entry_price_filled": float | null,   # what Binance filled
                  "filled_qty": float | null,
                  "realized_pnl_usd": float | null,
                  "close_reason": str | null,   # "TP1" | "SL" | "MANUAL" | ...
                  "opened_at": str | null,      # ISO-8601 UTC
                  "closed_at": str | null,
                  "not_traded_class": str | null,   # "rejected" | "preference"
                  "not_traded_reason": str | null,  # exception class / skip reason
                  "not_traded_detail": str | null,
                  "binance_code": int | null,
                  "source": "auto" | "manual_take",
                }, ...
              ],
              "closed_window": int,   # closed rows this read covered
              "closed_truncated": bool,
              "events_window": int,
              "events_truncated": bool,
            }

        Three rules the shape carries, each one this repo has already
        paid for on another surface:

        * **Absence is not "not traded".**  A signal with no entry here
          has no record on this account *within the windows named in the
          response* — which is a different fact from a signal this
          account declined, and the caller must not collapse them.  Both
          window sizes and both truncation flags ride the payload so the
          app can say which it is instead of guessing.
        * **"Not traded" is two classes with two different next moves.**
          ``rejected`` means the order path was reached and Binance or a
          tripwire refused (top up, re-whitelist the key, widen the
          symbol list); ``preference`` means the user's OWN path/regime
          filter declined it and nothing was wrong.  Pooling them into
          one grey "skipped" chip is how a working account reads as a
          broken one.
        * **The position wins over the event.**  Where both exist the
          position document is what Binance did; the dispatch event only
          contributes ``source`` (auto fan-out vs the user's own tap).

        Cost: the open half is served from the in-memory live index
        (zero Firestore reads); the closed half is one bounded ordered
        query (``closed_at`` DESC, capped); the event half is the same
        bounded read the Recent Activity card already does.  Nothing
        here streams the never-pruned positions collection — that read
        is the one this system's cost discipline was written about.
        """
        from src.execution import dispatch_log as _dl
        from src.execution import position_state as _ps

        firebase_uid = _extract_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Signal outcomes requires Firebase sign-in.",
            )

        limit = max(1, min(int(limit), 100))

        def _iso(value: Any) -> Optional[str]:
            return value.isoformat() if value is not None else None

        rows: dict[str, dict] = {}
        closed_window = 0
        events_window = 0

        # --- positions (open from the index, closed from the bounded read)
        if _ps._db is not None:
            try:
                open_positions = await asyncio.to_thread(
                    _ps.list_positions_for_user, firebase_uid
                )
            except _ps.PositionStateNotInitialisedError:
                open_positions = []
            except Exception:
                log.exception(
                    "signal_outcomes: open-position read failed uid={}",
                    firebase_uid,
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Could not reach the position store. Please retry.",
                )
            try:
                closed_positions = await asyncio.to_thread(
                    _ps.list_recent_closed_positions_for_user,
                    firebase_uid,
                    limit=limit,
                )
            except _ps.PositionStateNotInitialisedError:
                closed_positions = []
            except Exception:
                log.exception(
                    "signal_outcomes: closed-position read failed uid={}",
                    firebase_uid,
                )
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Could not reach the position store. Please retry.",
                )
            closed_window = len(closed_positions)
            for p in list(closed_positions) + list(open_positions):
                terminal = _ps.is_terminal(p.state)
                rows[p.signal_id] = {
                    "signal_id": p.signal_id,
                    "symbol": p.symbol,
                    "direction": p.side,
                    "status": "closed" if terminal else "open",
                    "state": p.state.value,
                    "entry_price_filled": p.entry_price_filled,
                    "filled_qty": p.filled_qty,
                    "realized_pnl_usd": p.realized_pnl_total,
                    "close_reason": p.close_reason or None,
                    "opened_at": _iso(p.created_at),
                    "closed_at": _iso(p.closed_at),
                    "not_traded_class": None,
                    "not_traded_reason": None,
                    "not_traded_detail": None,
                    "binance_code": None,
                    "source": "auto",
                }

        # --- dispatch events: the "not traded" half, plus ``source``
        events = await asyncio.to_thread(
            _dl.list_recent_events, firebase_uid, limit=limit
        )
        events_window = len(events)
        for e in events:
            existing = rows.get(e.signal_id)
            if existing is not None:
                # A position exists: Binance's own record wins on every
                # money field.  The event still owns ``source``, which no
                # position document carries.
                existing["source"] = e.source
                continue
            if e.outcome == "placed":
                # Placed, but no position document within the windows
                # above — the position is older than the closed read
                # reached.  Recording it as "not traded" would be a
                # fabricated outcome, so it is left out entirely and the
                # window counts below say why it could be missing.
                continue
            if e.outcome == "skipped":
                not_traded_class = "preference"
                reason = e.skip_reason or "preference"
            else:
                not_traded_class = "rejected"
                reason = e.reject_class or "rejected"
            rows[e.signal_id] = {
                "signal_id": e.signal_id,
                "symbol": e.symbol,
                "direction": e.direction,
                "status": "not_traded",
                "state": None,
                "entry_price_filled": None,
                "filled_qty": None,
                "realized_pnl_usd": None,
                "close_reason": None,
                "opened_at": _iso(e.timestamp),
                "closed_at": None,
                "not_traded_class": not_traded_class,
                "not_traded_reason": reason,
                "not_traded_detail": e.reject_detail,
                "binance_code": e.reject_binance_code,
                "source": e.source,
            }

        ordered = sorted(
            rows.values(),
            key=lambda r: (r.get("opened_at") or ""),
            reverse=True,
        )
        return {
            "outcomes": ordered,
            "closed_window": closed_window,
            "closed_truncated": closed_window >= limit,
            "events_window": events_window,
            "events_truncated": events_window >= limit,
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
