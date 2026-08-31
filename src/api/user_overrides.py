"""Per-user settings overrides (Phase 2 of per-user expansion).

Stores per-user pre-TP, invalidation, and auto-trade preferences in SQLite
tables that sit alongside the ``users`` table in the same ``lumin.sqlite``
file.  Three tables, one row per user per surface:

    user_pretp_settings(user_id PK, enabled, regime_allowlist (JSON),
                        setup_allowlist (JSON), threshold_pct,
                        atr_multiplier, fee_floor_pct, min_age_sec,
                        max_age_sec, grab_fraction, updated_at)

    user_invalidation_settings(user_id PK, mode, min_age_sec,
                               momentum_threshold_mult, ema_crossover_enabled,
                               regime_shift_enabled, trailing_kill_enabled,
                               trailing_mfe_r_threshold,
                               trailing_retrace_pct, updated_at)

    user_auto_trade_settings(user_id PK, mode, position_size_pct,
                             leverage_cap, max_concurrent_positions,
                             updated_at)

NULL semantics: every column except the PK is nullable.  NULL =
"use the engine default" (which the API layer resolves from
``config/__init__.py`` and ``src.user_settings`` — the engine-wide
store).  A row exists for a user as soon as they PUT one setting;
fields they haven't set stay NULL.

``grab_fraction`` realises OWNER_BRIEF B17 — pre-TP fires a real partial
close of the user-configured fraction.  Range [0.30, 1.00]; engine
default 0.50.  Hard 30% floor (no user can collapse to the pre-2026-05-17
"SL-to-BE-only" behaviour); 100% ceiling.

``user_invalidation_settings.mode`` realises B17's three-mode dial —
``loose`` / ``standard`` / ``tight``.  Default ``standard``.  Tight adds
ATR-trailing kill at MFE >= ``trailing_mfe_r_threshold`` (default 0.3R)
with ``trailing_retrace_pct`` (default 0.5 = 50%) of MFE peak.

The engine signal-evaluation path does NOT consume per-user values
in this PR — strict schema + API.  PR #3 (pretp partial close) and
PR #4 (invalidation per-user modes) wire the engine read paths.
"""

from __future__ import annotations

import asyncio
import json
import secrets
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, FrozenSet, Iterable, List, Optional, Tuple

from src.utils import get_logger

log = get_logger("api.user_overrides")


# ---------------------------------------------------------------------------
# Validation constants — mirror src.user_settings so the wire schema is
# identical and the existing app-side data classes don't need to fork.
# ---------------------------------------------------------------------------


_PRETP_KEYS = frozenset({
    "enabled",
    "regime_allowlist",
    "setup_allowlist",
    "threshold_pct",
    "atr_multiplier",
    "fee_floor_pct",
    "min_age_sec",
    "max_age_sec",
    "grab_fraction",
    "protect_manual_entries",
})

# OWNER_BRIEF B17 — pre-TP fires a REAL partial close.  Hard floor 30% so no
# user can accidentally collapse to the pre-2026-05-17 SL-to-BE-only behaviour
# (which converted MFE-positive signals into fee-burning flat exits).  100%
# ceiling = fully bank the partial, leave nothing riding.
_PRETP_GRAB_FRACTION_MIN: float = 0.30
_PRETP_GRAB_FRACTION_MAX: float = 1.00

# Per-user pre-TP threshold (the raw-percent move at which the pre-TP LIMIT
# rests).  A user picks e.g. 0.30% ("bank fast") or 0.50% ("let it breathe").
# Bounds guard against a fat-fingered or stale value: below 0.05% the LIMIT
# would sit inside the spread and fill on noise; above 5% it stops being a
# scalp pre-TP.  Out-of-band values fall back to the engine default.
_PRETP_THRESHOLD_PCT_MIN: float = 0.05
_PRETP_THRESHOLD_PCT_MAX: float = 5.00

_INVALIDATION_KEYS = frozenset({
    "mode",
    "min_age_sec",
    "momentum_threshold_mult",
    "ema_crossover_enabled",
    "regime_shift_enabled",
    "trailing_kill_enabled",
    "trailing_mfe_r_threshold",
    "trailing_retrace_pct",
})

_VALID_INVALIDATION_MODES: FrozenSet[str] = frozenset({"loose", "standard", "tight"})

_REGIME_UI_TO_BACKEND: Dict[str, FrozenSet[str]] = {
    "TRENDING": frozenset({"TRENDING_UP", "TRENDING_DOWN"}),
    "RANGING": frozenset({"RANGING"}),
    "CHOPPY": frozenset({"VOLATILE", "QUIET"}),
}
_VALID_BACKEND_REGIMES: FrozenSet[str] = frozenset({
    "TRENDING_UP", "TRENDING_DOWN", "RANGING", "VOLATILE", "QUIET",
})

_AUTO_TRADE_KEYS = frozenset({
    "mode",
    "position_size_pct",
    "leverage_cap",
    "max_concurrent_positions",
    "symbol_preference",
    "path_preference",
    "regime_preference",
    "paper_symbol_preference",
    "paper_path_preference",
    "paper_regime_preference",
    "notional_usd",
    "exit_mechanism",
})

#: Per-user exit mechanism (2026-08-10).  ``default`` is the SL/TP FSM every
#: user has always run.  The other two hand the exit to the live trail
#: governor once the mechanism comes onside — the same mechanisms
#: ``trail_mechanisms`` measures, now placing real orders.
#:
#: Deliberately per-user rather than a global flag: the owner asked to test
#: this on his own capital only ("only for me not for us not for users"), and
#: B17's pre-TP / invalidation settings already establish that exit behaviour
#: is a per-user column.  A global switch could not express "one account".
EXIT_MECHANISM_DEFAULT = "default"
EXIT_MECHANISMS = frozenset({EXIT_MECHANISM_DEFAULT, "sar", "chandelier"})

# The three live eligibility columns and their PAPER counterparts.  Live
# is consumed by ``dispatch_signal_to_active_users`` (real orders); paper
# by the per-user paper book fan-out (simulated).  "individual paper +
# live selection" (owner, 2026-06-20) = these two independent triples.
_ELIGIBILITY_KEYS_BY_SCOPE: Dict[str, Tuple[str, str, str]] = {
    "live": ("symbol_preference", "path_preference", "regime_preference"),
    "paper": (
        "paper_symbol_preference",
        "paper_path_preference",
        "paper_regime_preference",
    ),
}

_LEVERAGE_HARD_CAP: float = 30.0  # B12

# Per-user notional override bounds (2026-05-20).
#
# Floor:   $5 — Binance USDT-M MIN_NOTIONAL is $5 for most pairs (a few
#          micro-cap pairs raise it to $10–20).  Anything below $5 is
#          guaranteed to fail Binance's filter on every symbol → setting
#          it that low is a foot-gun.
#
# Ceiling: $2000 — B18 per-user position cap.  Engine-side ``assert_
#          position_cap`` tripwire rejects any single position above
#          this; the override layer enforces it here so we never write
#          a value that would later be rejected at dispatch time.
#
# Default: $500 — preserves the prior hardcoded ``_DEFAULT_NOTIONAL_USD``
#          behaviour for users who don't set an override.
_NOTIONAL_USD_MIN: float = 5.0
_NOTIONAL_USD_MAX: float = 2000.0


_PRETP_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_pretp_settings (
    user_id                 INTEGER PRIMARY KEY,
    enabled                 INTEGER,
    regime_allowlist        TEXT,
    setup_allowlist         TEXT,
    threshold_pct           REAL,
    atr_multiplier          REAL,
    fee_floor_pct           REAL,
    min_age_sec             INTEGER,
    max_age_sec             INTEGER,
    grab_fraction           REAL,
    protect_manual_entries  INTEGER,
    updated_at              TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
"""

# OWNER_BRIEF B17 — per-user invalidation aggressiveness.  ``mode`` is the
# headline knob (loose / standard / tight); the remaining columns are
# advanced-section overrides for users who want fine control without
# committing to a preset.  All nullable: NULL → use engine default (which
# itself reads ``mode`` first, then falls back to ``INVALIDATION_*`` env
# vars from ``config/__init__.py``).
_INVALIDATION_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_invalidation_settings (
    user_id                   INTEGER PRIMARY KEY,
    mode                      TEXT,
    min_age_sec               INTEGER,
    momentum_threshold_mult   REAL,
    ema_crossover_enabled     INTEGER,
    regime_shift_enabled      INTEGER,
    trailing_kill_enabled     INTEGER,
    trailing_mfe_r_threshold  REAL,
    trailing_retrace_pct      REAL,
    updated_at                TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
"""

_AUTO_TRADE_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_auto_trade_settings (
    user_id                  INTEGER PRIMARY KEY,
    mode                     TEXT,
    position_size_pct        REAL,
    leverage_cap             REAL,
    max_concurrent_positions INTEGER,
    symbol_preference        TEXT,     -- JSON list[str] or NULL = all (LIVE)
    path_preference          TEXT,     -- JSON list[setup_class] or NULL = all paths; [] = block all (LIVE)
    regime_preference        TEXT,     -- JSON list[backend regime] or NULL = all regimes; [] = block all (LIVE)
    paper_symbol_preference  TEXT,     -- PAPER counterpart of symbol_preference
    paper_path_preference    TEXT,     -- PAPER counterpart of path_preference
    paper_regime_preference  TEXT,     -- PAPER counterpart of regime_preference
    notional_usd             REAL,     -- per-user notional cap; NULL = engine default ($500)
    exit_mechanism           TEXT,     -- NULL/"default" = SL/TP FSM; "sar"/"chandelier" = live trail governor
    updated_at               TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 2026-05-23 — per-user paper-mode subscription windows.
-- The engine runs a single PaperOrderManager; per-user visibility is
-- derived by filtering the engine ledger (paper_trades.sqlite,
-- pnl_history.json) to trades closed during ANY of the user's paper
-- subscription windows. A fresh user with no subscriptions sees no
-- trades — which is exactly the bug fix this table enables.
--
-- Invariant: at most one row per user has ended_at IS NULL (active
-- subscription). Enforced by open_paper_subscription closing any
-- prior active row before inserting the new one.
CREATE TABLE IF NOT EXISTS user_paper_subscriptions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    started_at TEXT    NOT NULL,
    ended_at   TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_user_paper_subs_user_started
ON user_paper_subscriptions(user_id, started_at DESC);
"""

# 2026-06-20 — per-(user, symbol) management mode for the Signals-tab
# "take full vs entry-only" choice.  ``full`` (default; absence of a row)
# = engine manages entry + SL + pre-TP + TP ladder + invalidation.
# ``entry`` = engine places entry + protective SL only, then hands the
# position to the user (no pre-TP, no TP ladder, engine invalidation
# does not force-close — honoured at dispatch via grab_fraction=0 +
# invalidation_mode='loose' + skip-TP-bracket).  The protective SL is
# always placed, so the naked-position invariant (B12/B18) holds.
_SYMBOL_MGMT_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_symbol_management (
    user_id    INTEGER NOT NULL,
    symbol     TEXT    NOT NULL,
    mode       TEXT    NOT NULL,   -- 'full' | 'entry'
    updated_at TEXT    NOT NULL,
    PRIMARY KEY (user_id, symbol),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
"""

_VALID_MANAGEMENT_MODES: FrozenSet[str] = frozenset({"full", "entry"})

# 2026-06-27 — referral tracking (Phase 1: free invite/share + attribution).
# One stable code per user, generated lazily on first read. A referee can
# redeem at most once ever — ``referee_id`` as the PK makes that a DB-level
# invariant, not just an application check.
#
# 2026-07-21 — Phase 2 (owner-approved): rewards on top of the same rows.
#   * ``user_reward_grants`` — durable ledger of time-boxed tier grants
#     (referral join → 7 days of Auto for the referrer, stacking).  A grant
#     must SURVIVE Play verify / RTDN overwrites of the user row, so the
#     entitlement write sites compose the user row from Play state + this
#     ledger (src/api/referral_rewards.py) instead of trusting either alone.
#     ``UNIQUE (user_id, source, ref_id)`` makes each reward one-shot per
#     originating event (e.g. one grant per referee ever).
#   * ``referral_commissions`` — accrual ledger: 50% (env-tunable) of each
#     verified paid billing period of a referred user, for that user's first
#     N periods, credited to the referrer.  ``UNIQUE (purchase_token,
#     period_expiry)`` makes RTDN redeliveries / re-verifies idempotent.
#     Payout is owner-manual: rows move accrued → paid via the owner admin
#     endpoint (ops Referrals panel).
#   * ``user_referral_redemptions.converted_at`` (ALTER, migration below) —
#     stamped on the referee's first verified paid purchase; while NULL the
#     referee is eligible for the one-time 50%-off first cycle.
_REFERRAL_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_referral_codes (
    user_id    INTEGER PRIMARY KEY,
    code       TEXT    NOT NULL UNIQUE,
    created_at TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS user_referral_redemptions (
    referee_id  INTEGER PRIMARY KEY,
    referrer_id INTEGER NOT NULL,
    code        TEXT    NOT NULL,
    redeemed_at TEXT    NOT NULL,
    FOREIGN KEY (referee_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (referrer_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_user_referral_redemptions_referrer
ON user_referral_redemptions(referrer_id);
CREATE TABLE IF NOT EXISTS user_reward_grants (
    grant_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    tier       TEXT    NOT NULL,
    source     TEXT    NOT NULL,
    ref_id     TEXT    NOT NULL,
    starts_at  TEXT    NOT NULL,
    expires_at TEXT    NOT NULL,
    created_at TEXT    NOT NULL,
    UNIQUE (user_id, source, ref_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_user_reward_grants_user
ON user_reward_grants(user_id, expires_at);
CREATE TABLE IF NOT EXISTS referral_commissions (
    commission_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id    INTEGER NOT NULL,
    referee_id     INTEGER NOT NULL,
    product_id     TEXT    NOT NULL,
    purchase_token TEXT    NOT NULL,
    period_expiry  TEXT    NOT NULL,
    amount         REAL    NOT NULL,
    currency       TEXT    NOT NULL,
    rate           REAL    NOT NULL,
    status         TEXT    NOT NULL DEFAULT 'accrued',
    created_at     TEXT    NOT NULL,
    paid_at        TEXT,
    UNIQUE (purchase_token, period_expiry)
);
CREATE INDEX IF NOT EXISTS idx_referral_commissions_referrer
ON referral_commissions(referrer_id, status);
CREATE INDEX IF NOT EXISTS idx_referral_commissions_referee
ON referral_commissions(referee_id);
"""

# 2026-07-25 — signup free trial (owner-approved: 7 days of Auto, no card,
# opt-in).  The GRANT itself lives in ``user_reward_grants`` above with
# ``source='signup_trial'`` so it shares one sequential entitlement timeline
# with referral rewards and is picked up unchanged by the composition in
# src/api/referral_rewards.py.  This table is the FUNNEL — the thing ops
# reads, and the reason the measurement flag can be ON while the
# user-visible flag is OFF:
#
#   eligible_at  — first time we saw this user as trial-eligible (stamped
#                  even while dark; that is the would-be cohort)
#   offered_at   — first time the app was actually told the offer is live
#   claimed_at   — the user tapped "Start my 7 free days" (opt-in, never
#                  auto-applied per owner decision)
#   expires_at   — claimed_at + days; mirrors the reward grant's expiry
#   converted_at — their first verified paid period after claiming, i.e. the
#                  trial paid for itself
#   shadow       — 1 when the row was created while SIGNUP_TRIAL_ENABLED was
#                  off, so the dark cohort is never mistaken for a live one
#
# ``user_id`` as the PK is the one-shot-ever invariant: a trial is offered,
# claimed and burned at most once per user, at DB level rather than by
# application check.
_TRIAL_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_trials (
    user_id      INTEGER PRIMARY KEY,
    tier         TEXT    NOT NULL,
    days         INTEGER NOT NULL,
    eligible_at  TEXT    NOT NULL,
    offered_at   TEXT,
    claimed_at   TEXT,
    expires_at   TEXT,
    converted_at TEXT,
    shadow       INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_user_trials_claimed
ON user_trials(claimed_at);
CREATE INDEX IF NOT EXISTS idx_user_trials_expires
ON user_trials(expires_at);
"""

# Unambiguous alphabet — excludes 0/O and 1/I so a code read aloud or typed
# by hand from a share-sheet message doesn't bounce on lookalike characters.
_REFERRAL_CODE_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
_REFERRAL_CODE_LENGTH = 7
_REFERRAL_CODE_MAX_ATTEMPTS = 10


def _generate_referral_code() -> str:
    return "".join(
        secrets.choice(_REFERRAL_CODE_ALPHABET)
        for _ in range(_REFERRAL_CODE_LENGTH)
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_reward_ts(raw: Any) -> Optional[datetime]:
    """Parse a stored reward-grant timestamp; None on absence/garbage."""
    if not raw:
        return None
    try:
        ts = datetime.fromisoformat(str(raw))
    except ValueError:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts


def _normalise_regime_input(items: Any) -> list[str]:
    if items is None:
        return []
    if isinstance(items, str):
        items = [items]
    out: set = set()
    for raw in items:
        if not isinstance(raw, str):
            continue
        tok = raw.strip().upper()
        if not tok:
            continue
        if tok in _REGIME_UI_TO_BACKEND:
            out.update(_REGIME_UI_TO_BACKEND[tok])
        elif tok in _VALID_BACKEND_REGIMES:
            out.add(tok)
    return sorted(out)


def _coerce_pretp(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Drop unknown keys, validate types, normalise regime/setup lists."""
    out: Dict[str, Any] = {}
    for key, value in raw.items():
        if key not in _PRETP_KEYS:
            continue
        if value is None:
            # Explicit null → clear the override (caller's choice).
            out[key] = None
            continue
        if key == "enabled":
            if isinstance(value, bool):
                out[key] = value
        elif key in ("threshold_pct", "atr_multiplier", "fee_floor_pct"):
            if isinstance(value, (int, float)) and value >= 0:
                out[key] = float(value)
        elif key in ("min_age_sec", "max_age_sec"):
            if isinstance(value, int) and value >= 0:
                out[key] = int(value)
        elif key == "grab_fraction":
            # Session 34 — 0 (or any non-positive) means pre-TP DISABLED (the
            # engine default exit is TP1-full + fixed SL); preserve it as 0.0.
            # Any positive value clamps into the B17 [0.30, 1.00] opt-in band so
            # no user lands in the dead 0<x<0.30 zone.  Mirrors the FSM/monitor
            # clamp.  Reject non-numeric silently to match drop-unknown.
            if isinstance(value, (int, float)):
                if float(value) <= 0.0:
                    out[key] = 0.0
                else:
                    out[key] = max(
                        _PRETP_GRAB_FRACTION_MIN,
                        min(_PRETP_GRAB_FRACTION_MAX, float(value)),
                    )
        elif key == "protect_manual_entries":
            # B17 (2026-05-17) — when ON, the app-side AutoTradeWatcher
            # keeps polling for pre-TP partials on manual entries even
            # when auto-trade ``mode == 'off'``.  Default ON delivers
            # capital preservation to the most engaged subscriber cohort
            # (hand-picked entries); OFF respects "off means off" for
            # users who want pure manual control.
            if isinstance(value, bool):
                out[key] = value
        elif key == "regime_allowlist":
            out[key] = _normalise_regime_input(value)
        elif key == "setup_allowlist":
            if isinstance(value, list):
                out[key] = sorted({
                    s.strip().upper() for s in value
                    if isinstance(s, str) and s.strip()
                })
    return out


def _coerce_invalidation(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Drop unknown keys, validate types, normalise the mode token."""
    out: Dict[str, Any] = {}
    for key, value in raw.items():
        if key not in _INVALIDATION_KEYS:
            continue
        if value is None:
            out[key] = None
            continue
        if key == "mode":
            if isinstance(value, str):
                token = value.strip().lower()
                if token in _VALID_INVALIDATION_MODES:
                    out[key] = token
        elif key == "min_age_sec":
            if isinstance(value, int) and value >= 0:
                out[key] = int(value)
        elif key in (
            "momentum_threshold_mult",
            "trailing_mfe_r_threshold",
            "trailing_retrace_pct",
        ):
            if isinstance(value, (int, float)) and float(value) >= 0:
                out[key] = float(value)
        elif key in (
            "ema_crossover_enabled",
            "regime_shift_enabled",
            "trailing_kill_enabled",
        ):
            if isinstance(value, bool):
                out[key] = value
    return out


def _coerce_auto_trade(raw: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in raw.items():
        if key not in _AUTO_TRADE_KEYS:
            continue
        if value is None:
            out[key] = None
            continue
        if key == "mode":
            if isinstance(value, str):
                token = value.strip().lower()
                if token in ("off", "paper", "live", "both"):
                    out[key] = token
        elif key == "exit_mechanism":
            # Reject an unknown mechanism outright rather than storing it and
            # letting the governor fall back at dispatch time.  A silent
            # fallback here would read as "SAR is on" in the API response
            # while the FSM ran the default exit — the money path must not
            # disagree with the surface that claims to control it.
            if isinstance(value, str):
                token = value.strip().lower()
                if token in EXIT_MECHANISMS:
                    out[key] = token
        elif key == "position_size_pct":
            if isinstance(value, (int, float)) and 0 < float(value) <= 100:
                out[key] = float(value)
        elif key == "leverage_cap":
            if isinstance(value, (int, float)) and float(value) > 0:
                out[key] = min(float(value), _LEVERAGE_HARD_CAP)
        elif key == "max_concurrent_positions":
            if isinstance(value, int) and value >= 1:
                out[key] = int(value)
        elif key in ("symbol_preference", "paper_symbol_preference"):
            # Accept list[str] only.  Empty list → store as ``[]`` to
            # mean "explicitly chose nothing" (which the FSM treats as
            # "block ALL orders for this user").  This is the doctrine-
            # strict opt-out path — distinct from ``None`` which means
            # "no preference set, fall through to engine-wide allowlist".
            # Paper counterpart coerces identically (independent column).
            if isinstance(value, list):
                cleaned = []
                for sym in value:
                    if isinstance(sym, str):
                        tok = sym.strip().upper()
                        # USDT-M futures symbol shape: alphanum + ends with USDT.
                        # Be permissive on character set (Binance lists like
                        # "1000BONKUSDT") but reject empty / wildly malformed.
                        if tok and tok.endswith("USDT") and tok.isalnum():
                            cleaned.append(tok)
                out[key] = sorted(set(cleaned))  # canonical form
        elif key in ("path_preference", "paper_path_preference"):
            # User-chosen subset of signal evaluator paths (setup classes)
            # eligible to auto-trade live for this user.  Mirrors
            # ``symbol_preference`` semantics exactly: ``None`` (handled
            # above) = no preference → all paths; a list (incl. empty) =
            # "only these paths may auto-trade for me" (empty = block all).
            # Stored uppercase + canonical-sorted; the dispatch gate
            # compares against ``setup_class.upper()``.  Permissive on the
            # token set (a value the engine never emits simply never
            # matches → no trades for it), matching ``setup_allowlist``.
            if isinstance(value, list):
                out[key] = sorted({
                    s.strip().upper() for s in value
                    if isinstance(s, str) and s.strip()
                })
        elif key in ("regime_preference", "paper_regime_preference"):
            # User-chosen subset of entry regimes eligible to auto-trade
            # live.  ``_normalise_regime_input`` maps the app's UI tokens
            # (TRENDING / RANGING / CHOPPY) onto the backend regime labels
            # (TRENDING_UP/DOWN, RANGING, VOLATILE, QUIET) the dispatcher
            # compares ``regime_label`` against.  A non-None list that
            # normalises to ``[]`` means "block all" (mirrors symbol []).
            out[key] = _normalise_regime_input(value)
        elif key == "notional_usd":
            # Per-user notional cap.  Clamp into the [_NOTIONAL_USD_MIN,
            # _NOTIONAL_USD_MAX] band — silently fixing rather than
            # rejecting is the same UX as ``leverage_cap`` (which also
            # min()s into the hard cap rather than 400'ing the request).
            if isinstance(value, (int, float)) and float(value) > 0:
                v = float(value)
                v = max(_NOTIONAL_USD_MIN, min(v, _NOTIONAL_USD_MAX))
                out[key] = v
    return out


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------


class UserOverridesStore:
    """SQLite-backed per-user override store.

    Opens its own connection to the same db file as ``UserStore`` — WAL
    mode lets the two connections share without deadlock.  Reads return
    a partial dict of fields the user has actually set (NULL columns
    omitted); the API layer composes this with engine defaults to
    produce the effective view sent back to the app.
    """

    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            str(self._path),
            check_same_thread=False,
            isolation_level=None,
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        # busy_timeout — shares lumin.sqlite with UserStore's separate
        # connection; wait for the file lock rather than fail instantly
        # on a cross-store write collision under the thread pool.
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(
            _PRETP_SCHEMA + _INVALIDATION_SCHEMA + _AUTO_TRADE_SCHEMA
            + _SYMBOL_MGMT_SCHEMA + _REFERRAL_SCHEMA + _TRIAL_SCHEMA
        )
        self._migrate_pretp_grab_fraction()
        self._migrate_pretp_protect_manual_entries()
        self._migrate_auto_trade_symbol_preference()
        self._migrate_auto_trade_path_regime_preference()
        self._migrate_auto_trade_notional_usd()
        self._migrate_auto_trade_exit_mechanism()
        self._migrate_auto_trade_pause_columns()
        self._migrate_referral_converted_at()
        log.info("UserOverridesStore opened at {}", self._path)

    def _migrate_referral_converted_at(self) -> None:
        """Idempotent ALTER for ``user_referral_redemptions.converted_at``
        (2026-07-21 referral Phase 2).

        NULL = the referee has never completed a verified paid purchase —
        they are still eligible for the one-time 50%-off first cycle.
        Stamped (ISO-8601 UTC) on the first verified paid period, which
        also starts the referrer's commission window.
        """
        cur = self._conn.execute("PRAGMA table_info(user_referral_redemptions)")
        cols = {row["name"] for row in cur.fetchall()}
        if "converted_at" not in cols:
            self._conn.execute(
                "ALTER TABLE user_referral_redemptions ADD COLUMN converted_at TEXT"
            )
            log.info("migrated user_referral_redemptions: added converted_at")

    def _migrate_auto_trade_path_regime_preference(self) -> None:
        """Idempotent ALTER for the ``path_preference`` / ``regime_preference``
        columns (2026-06-20 per-user path + regime picker).

        Mirrors ``symbol_preference``: NULL on existing rows means "no
        preference — all paths / all regimes eligible" (default-all UX).
        Stored as TEXT (JSON list of strings).  Consumed at LIVE dispatch
        as trade-eligibility filters (``dispatch_signal_to_active_users``).
        """
        cur = self._conn.execute("PRAGMA table_info(user_auto_trade_settings)")
        cols = {row["name"] for row in cur.fetchall()}
        for col in (
            "path_preference",
            "regime_preference",
            "paper_symbol_preference",
            "paper_path_preference",
            "paper_regime_preference",
        ):
            if col not in cols:
                self._conn.execute(
                    f"ALTER TABLE user_auto_trade_settings ADD COLUMN {col} TEXT"
                )
                log.info(
                    "UserOverridesStore: added user_auto_trade_settings.{} "
                    "column (2026-06-20 per-user path/regime + paper picker)", col,
                )

    def _migrate_auto_trade_notional_usd(self) -> None:
        """Idempotent ALTER for the ``notional_usd`` column.

        Added 2026-05-20 — per-user notional override.  Existing
        deploys carry the pre-override schema (no ``notional_usd``
        column).  ``CREATE TABLE IF NOT EXISTS`` doesn't update
        existing tables, so we detect the missing column via
        ``PRAGMA table_info`` and ``ALTER TABLE ... ADD COLUMN``
        it in if absent.  No-op on fresh DBs where the column is
        already present from the CREATE.  NULL on existing rows
        is interpreted by the dispatch layer as "use engine
        default ($500)".
        """
        cur = self._conn.execute("PRAGMA table_info(user_auto_trade_settings)")
        cols = {row["name"] for row in cur.fetchall()}
        if "notional_usd" not in cols:
            self._conn.execute(
                "ALTER TABLE user_auto_trade_settings ADD COLUMN "
                "notional_usd REAL"
            )
            log.info(
                "UserOverridesStore: added user_auto_trade_settings."
                "notional_usd column (2026-05-20 per-user notional override)"
            )

    def _migrate_auto_trade_exit_mechanism(self) -> None:
        """Idempotent ALTER for the ``exit_mechanism`` column.

        Added 2026-08-10 — per-user live trail governor.  NULL on existing
        rows means "default", i.e. the SL/TP FSM every account has always
        run, so an un-migrated row fails toward the *unchanged* exit rather
        than toward a mechanism nobody opted into.  That direction matters:
        this column decides whether a real stop order is cancelled and
        re-placed every bar on somebody's live capital.
        """
        cur = self._conn.execute("PRAGMA table_info(user_auto_trade_settings)")
        cols = {row["name"] for row in cur.fetchall()}
        if "exit_mechanism" not in cols:
            self._conn.execute(
                "ALTER TABLE user_auto_trade_settings ADD COLUMN "
                "exit_mechanism TEXT"
            )
            log.info(
                "UserOverridesStore: added user_auto_trade_settings."
                "exit_mechanism column (2026-08-10 per-user trail governor)"
            )

    def _migrate_auto_trade_symbol_preference(self) -> None:
        """Idempotent ALTER for the ``symbol_preference`` column.

        Added 2026-05-19 to support per-user symbol picker (PR E).
        NULL on existing rows is interpreted by the FSM gate as "no
        preference — fall through to engine-wide allowlist" (default-
        all UX path).  Stored as TEXT (JSON list of strings).
        """
        cur = self._conn.execute("PRAGMA table_info(user_auto_trade_settings)")
        cols = {row["name"] for row in cur.fetchall()}
        if "symbol_preference" not in cols:
            self._conn.execute(
                "ALTER TABLE user_auto_trade_settings ADD COLUMN "
                "symbol_preference TEXT"
            )
            log.info(
                "UserOverridesStore: added user_auto_trade_settings."
                "symbol_preference column (2026-05-19 per-user symbol picker)"
            )

    def _migrate_auto_trade_pause_columns(self) -> None:
        """Idempotent ALTER for the per-user auto-pause columns.

        Added 2026-05-24 to support self-healing dispatch behaviour:
        when the engine sees N consecutive Binance ``-2019`` (insufficient
        margin) rejects for a user, it auto-pauses that user's
        dispatcher with ``paused_reason='insufficient_margin'`` so we
        stop spamming their Recent Activity feed with the same rejection
        on every signal. ``paused_at`` is the ISO-8601 UTC stamp of the
        pause event — surfaced in the user-facing auto-mode status so
        the app can show a "wallet empty — top up + resume" banner.

        Both columns are NULL on existing rows; the dispatcher treats
        NULL as "not paused — keep dispatching".
        """
        cur = self._conn.execute("PRAGMA table_info(user_auto_trade_settings)")
        cols = {row["name"] for row in cur.fetchall()}
        if "paused_reason" not in cols:
            self._conn.execute(
                "ALTER TABLE user_auto_trade_settings ADD COLUMN "
                "paused_reason TEXT"
            )
            log.info(
                "UserOverridesStore: added user_auto_trade_settings."
                "paused_reason column (2026-05-24 auto-pause on -2019)"
            )
        if "paused_at" not in cols:
            self._conn.execute(
                "ALTER TABLE user_auto_trade_settings ADD COLUMN "
                "paused_at TEXT"
            )
            log.info(
                "UserOverridesStore: added user_auto_trade_settings."
                "paused_at column (2026-05-24 auto-pause on -2019)"
            )

    def _migrate_pretp_grab_fraction(self) -> None:
        """Idempotent ALTER for the B17 ``grab_fraction`` column.

        Existing deploys carry the pre-B17 schema (no ``grab_fraction``
        column).  ``CREATE TABLE IF NOT EXISTS`` doesn't update existing
        tables, so we detect the missing column via ``PRAGMA table_info``
        and ``ALTER TABLE ... ADD COLUMN`` it in if absent.  No-op on
        fresh DBs where the column is already present from the CREATE.
        """
        cur = self._conn.execute("PRAGMA table_info(user_pretp_settings)")
        cols = {row["name"] for row in cur.fetchall()}
        if "grab_fraction" not in cols:
            self._conn.execute(
                "ALTER TABLE user_pretp_settings ADD COLUMN grab_fraction REAL"
            )
            log.info(
                "UserOverridesStore: added user_pretp_settings.grab_fraction "
                "column (B17 migration)"
            )

    def _migrate_pretp_protect_manual_entries(self) -> None:
        """Idempotent ALTER for the ``protect_manual_entries`` column.

        Added 2026-05-17 to support extending pre-TP execution coverage
        to manual entries when auto-trade is off.  Same migration pattern
        as ``_migrate_pretp_grab_fraction``: detect via PRAGMA, ADD
        COLUMN only when missing.  NULL on existing rows is interpreted
        by the API layer as "use engine default (True)".
        """
        cur = self._conn.execute("PRAGMA table_info(user_pretp_settings)")
        cols = {row["name"] for row in cur.fetchall()}
        if "protect_manual_entries" not in cols:
            self._conn.execute(
                "ALTER TABLE user_pretp_settings ADD COLUMN "
                "protect_manual_entries INTEGER"
            )
            log.info(
                "UserOverridesStore: added user_pretp_settings."
                "protect_manual_entries column"
            )

    # ---- pretp -----------------------------------------------------------

    def get_pretp(self, user_id: int) -> Dict[str, Any]:
        """Return the user's pretp overrides as a partial dict.

        Fields the user hasn't set (NULL columns) are omitted from the
        result.  Empty dict means "no row" — user is on full defaults.
        """
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM user_pretp_settings WHERE user_id = ?",
                (int(user_id),),
            )
            row = cur.fetchone()
            return _row_to_partial(row, _PRETP_COL_TYPES) if row else {}

    def update_pretp(self, user_id: int, partial: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert: merge ``partial`` into the user's row.  Returns the
        full partial-dict after the update (same shape as ``get_pretp``).

        Validates + normalises via ``_coerce_pretp`` first.  Unknown keys
        and ill-typed values are silently dropped to mirror the engine's
        existing user_settings coercion behaviour.
        """
        cleaned = _coerce_pretp(partial)
        with self._lock:
            existing = self.get_pretp(user_id)
            merged = dict(existing)
            for k, v in cleaned.items():
                if v is None:
                    merged.pop(k, None)
                else:
                    merged[k] = v
            now = _now_iso()
            # Single upsert — INSERT OR REPLACE works because the table
            # has a clean PK and we always rewrite every column.
            self._conn.execute(
                """
                INSERT INTO user_pretp_settings (
                    user_id, enabled, regime_allowlist, setup_allowlist,
                    threshold_pct, atr_multiplier, fee_floor_pct,
                    min_age_sec, max_age_sec, grab_fraction,
                    protect_manual_entries, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    enabled = excluded.enabled,
                    regime_allowlist = excluded.regime_allowlist,
                    setup_allowlist = excluded.setup_allowlist,
                    threshold_pct = excluded.threshold_pct,
                    atr_multiplier = excluded.atr_multiplier,
                    fee_floor_pct = excluded.fee_floor_pct,
                    min_age_sec = excluded.min_age_sec,
                    max_age_sec = excluded.max_age_sec,
                    grab_fraction = excluded.grab_fraction,
                    protect_manual_entries = excluded.protect_manual_entries,
                    updated_at = excluded.updated_at
                """,
                (
                    int(user_id),
                    _bool_to_int(merged.get("enabled")),
                    _list_to_json(merged.get("regime_allowlist")),
                    _list_to_json(merged.get("setup_allowlist")),
                    merged.get("threshold_pct"),
                    merged.get("atr_multiplier"),
                    merged.get("fee_floor_pct"),
                    merged.get("min_age_sec"),
                    merged.get("max_age_sec"),
                    merged.get("grab_fraction"),
                    _bool_to_int(merged.get("protect_manual_entries")),
                    now,
                ),
            )
            return self.get_pretp(user_id)

    # ---- invalidation ----------------------------------------------------

    def get_invalidation(self, user_id: int) -> Dict[str, Any]:
        """Return the user's invalidation overrides as a partial dict.

        Realises OWNER_BRIEF B17 — empty dict means user is on engine default
        (which itself is ``mode="standard"`` per B17).  Fields the user hasn't
        set (NULL columns) are omitted from the result.
        """
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM user_invalidation_settings WHERE user_id = ?",
                (int(user_id),),
            )
            row = cur.fetchone()
            return _row_to_partial(row, _INVALIDATION_COL_TYPES) if row else {}

    def update_invalidation(self, user_id: int, partial: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = _coerce_invalidation(partial)
        with self._lock:
            existing = self.get_invalidation(user_id)
            merged = dict(existing)
            for k, v in cleaned.items():
                if v is None:
                    merged.pop(k, None)
                else:
                    merged[k] = v
            now = _now_iso()
            self._conn.execute(
                """
                INSERT INTO user_invalidation_settings (
                    user_id, mode, min_age_sec, momentum_threshold_mult,
                    ema_crossover_enabled, regime_shift_enabled,
                    trailing_kill_enabled, trailing_mfe_r_threshold,
                    trailing_retrace_pct, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    mode = excluded.mode,
                    min_age_sec = excluded.min_age_sec,
                    momentum_threshold_mult = excluded.momentum_threshold_mult,
                    ema_crossover_enabled = excluded.ema_crossover_enabled,
                    regime_shift_enabled = excluded.regime_shift_enabled,
                    trailing_kill_enabled = excluded.trailing_kill_enabled,
                    trailing_mfe_r_threshold = excluded.trailing_mfe_r_threshold,
                    trailing_retrace_pct = excluded.trailing_retrace_pct,
                    updated_at = excluded.updated_at
                """,
                (
                    int(user_id),
                    merged.get("mode"),
                    merged.get("min_age_sec"),
                    merged.get("momentum_threshold_mult"),
                    _bool_to_int(merged.get("ema_crossover_enabled")),
                    _bool_to_int(merged.get("regime_shift_enabled")),
                    _bool_to_int(merged.get("trailing_kill_enabled")),
                    merged.get("trailing_mfe_r_threshold"),
                    merged.get("trailing_retrace_pct"),
                    now,
                ),
            )
            return self.get_invalidation(user_id)

    def clear_pretp(self, user_id: int) -> Dict[str, Any]:
        """Delete the user's pretp override row, reverting them to engine
        defaults.  Returns ``{}`` (the same shape ``get_pretp`` returns for a
        user with no row) so the caller can rebuild a using_defaults view.
        Idempotent — deleting a non-existent row is a no-op.
        """
        with self._lock:
            self._conn.execute(
                "DELETE FROM user_pretp_settings WHERE user_id = ?",
                (int(user_id),),
            )
        return {}

    def clear_invalidation(self, user_id: int) -> Dict[str, Any]:
        """Delete the user's invalidation override row, reverting them to
        engine defaults.  Returns ``{}`` (matching ``get_invalidation`` for a
        user with no row).  Idempotent.
        """
        with self._lock:
            self._conn.execute(
                "DELETE FROM user_invalidation_settings WHERE user_id = ?",
                (int(user_id),),
            )
        return {}

    # ---- auto-trade ------------------------------------------------------

    def list_user_ids_with_mode(self, modes: Iterable[str]) -> List[int]:
        """Return the user_ids whose auto-trade ``mode`` is in ``modes``
        (case-insensitive).  Used by the per-user paper book fan-out to
        enumerate the paper/both cohort for a signal.  Empty ``modes`` →
        empty list."""
        modes_l = [str(m).lower() for m in modes if str(m).strip()]
        if not modes_l:
            return []
        placeholders = ",".join("?" for _ in modes_l)
        with self._lock:
            cur = self._conn.execute(
                "SELECT user_id FROM user_auto_trade_settings "
                f"WHERE LOWER(mode) IN ({placeholders})",
                tuple(modes_l),
            )
            return [int(r["user_id"]) for r in cur.fetchall()]

    def get_auto_trade(self, user_id: int) -> Dict[str, Any]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM user_auto_trade_settings WHERE user_id = ?",
                (int(user_id),),
            )
            row = cur.fetchone()
            return _row_to_partial(row, _AUTO_TRADE_COL_TYPES) if row else {}

    def update_auto_trade(self, user_id: int, partial: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = _coerce_auto_trade(partial)
        with self._lock:
            existing = self.get_auto_trade(user_id)
            merged = dict(existing)
            for k, v in cleaned.items():
                if v is None:
                    merged.pop(k, None)
                else:
                    merged[k] = v
            now = _now_iso()

            def _json_list(key: str) -> Optional[str]:
                v = merged.get(key)
                return json.dumps(v) if isinstance(v, list) else None

            self._conn.execute(
                """
                INSERT INTO user_auto_trade_settings (
                    user_id, mode, position_size_pct, leverage_cap,
                    max_concurrent_positions, symbol_preference,
                    path_preference, regime_preference,
                    paper_symbol_preference, paper_path_preference,
                    paper_regime_preference,
                    notional_usd, exit_mechanism, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    mode = excluded.mode,
                    position_size_pct = excluded.position_size_pct,
                    leverage_cap = excluded.leverage_cap,
                    max_concurrent_positions = excluded.max_concurrent_positions,
                    symbol_preference = excluded.symbol_preference,
                    path_preference = excluded.path_preference,
                    regime_preference = excluded.regime_preference,
                    paper_symbol_preference = excluded.paper_symbol_preference,
                    paper_path_preference = excluded.paper_path_preference,
                    paper_regime_preference = excluded.paper_regime_preference,
                    notional_usd = excluded.notional_usd,
                    exit_mechanism = excluded.exit_mechanism,
                    updated_at = excluded.updated_at
                """,
                (
                    int(user_id),
                    merged.get("mode"),
                    merged.get("position_size_pct"),
                    merged.get("leverage_cap"),
                    merged.get("max_concurrent_positions"),
                    _json_list("symbol_preference"),
                    _json_list("path_preference"),
                    _json_list("regime_preference"),
                    _json_list("paper_symbol_preference"),
                    _json_list("paper_path_preference"),
                    _json_list("paper_regime_preference"),
                    merged.get("notional_usd"),
                    merged.get("exit_mechanism"),
                    now,
                ),
            )
            # Per-user paper subscription bookkeeping (2026-05-23).
            # Bug fix: fresh accounts were seeing operator's prior paper
            # trades. Track each user's paper sessions as (started_at,
            # ended_at) windows so API readers can filter the shared
            # engine ledger to only trades closed within this user's
            # visibility windows.
            #
            # We compare normalised prior/new mode and toggle the
            # subscription accordingly. Mode-not-in-partial → no change.
            prior_mode = (existing.get("mode") or "").lower() or None
            new_mode = (merged.get("mode") or "").lower() or None
            #
            # Asked via the shared predicate, never ``== "paper"``. ``both``
            # runs the paper book too, and the literal comparison read it as
            # "not paper" — so a user switching paper → both had their paper
            # subscription CLOSED, silently truncating the trade history they
            # are allowed to read, because they enabled something additional
            # (#989). A window governs what a user may see about their own
            # money; it must never narrow on a mode change that widens what
            # they asked for.
            if "mode" in cleaned and prior_mode != new_mode:
                from src.execution import exec_mode as _em

                was_open = _em.paper_subscription_should_be_open(prior_mode)
                should_open = _em.paper_subscription_should_be_open(new_mode)
                if should_open and not was_open:
                    self._open_paper_subscription_locked(int(user_id), now)
                elif was_open and not should_open:
                    self._close_paper_subscription_locked(int(user_id), now)
                # paper → both (or both → paper) hits neither arm: the window
                # is already open and must stay exactly as it is. Re-opening
                # would stamp a new window and orphan the trades before it.
            return self.get_auto_trade(user_id)

    # ---- per-symbol management mode (Signals-tab full vs entry) ---------

    def get_symbol_management_map(self, user_id: int) -> Dict[str, str]:
        """Return ``{SYMBOL: mode}`` for every symbol the user has set to a
        non-default mode.  Absent symbols default to ``full`` — the caller
        treats a missing key as full management."""
        with self._lock:
            cur = self._conn.execute(
                "SELECT symbol, mode FROM user_symbol_management "
                "WHERE user_id = ?",
                (int(user_id),),
            )
            return {row["symbol"]: row["mode"] for row in cur.fetchall()}

    def set_symbol_management(
        self, user_id: int, symbol: str, mode: str,
    ) -> Dict[str, str]:
        """Upsert the management mode for one (user, symbol).  Setting
        ``full`` (the default) DELETES the row — absence == full, so we
        never store rows that just restate the default.  Invalid symbols
        / modes are dropped.  Returns the rebuilt map."""
        sym = (symbol or "").strip().upper()
        m = (mode or "").strip().lower()
        if not sym or m not in _VALID_MANAGEMENT_MODES:
            return self.get_symbol_management_map(user_id)
        with self._lock:
            if m == "full":
                self._conn.execute(
                    "DELETE FROM user_symbol_management "
                    "WHERE user_id = ? AND symbol = ?",
                    (int(user_id), sym),
                )
            else:
                self._conn.execute(
                    """
                    INSERT INTO user_symbol_management
                        (user_id, symbol, mode, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id, symbol) DO UPDATE SET
                        mode = excluded.mode,
                        updated_at = excluded.updated_at
                    """,
                    (int(user_id), sym, m, _now_iso()),
                )
            return self.get_symbol_management_map(user_id)

    # ---- referrals (Phase 1: free invite/share tracking, no reward) -----

    def get_or_create_referral_code(self, user_id: int) -> str:
        """Return the user's stable referral code, generating one on first
        call. Codes are immutable once issued — re-calling for the same
        user always returns the same code."""
        with self._lock:
            cur = self._conn.execute(
                "SELECT code FROM user_referral_codes WHERE user_id = ?",
                (int(user_id),),
            )
            row = cur.fetchone()
            if row is not None:
                return row["code"]
            now = _now_iso()
            for _ in range(_REFERRAL_CODE_MAX_ATTEMPTS):
                code = _generate_referral_code()
                try:
                    self._conn.execute(
                        "INSERT INTO user_referral_codes "
                        "(user_id, code, created_at) VALUES (?, ?, ?)",
                        (int(user_id), code, now),
                    )
                    return code
                except sqlite3.IntegrityError:
                    # Either the 7-char/33-symbol code collided (rare) or a
                    # concurrent call for this same user_id raced us — check
                    # for the latter before retrying with a fresh code.
                    cur = self._conn.execute(
                        "SELECT code FROM user_referral_codes WHERE user_id = ?",
                        (int(user_id),),
                    )
                    row = cur.fetchone()
                    if row is not None:
                        return row["code"]
                    continue
            raise RuntimeError(
                "failed to generate a unique referral code after "
                f"{_REFERRAL_CODE_MAX_ATTEMPTS} attempts"
            )

    def get_referral_stats(self, user_id: int) -> Dict[str, Any]:
        """Return this user's code plus how many friends have joined via it.
        Generates the code lazily if the user has never opened the invite
        screen before, so this is always safe to call."""
        code = self.get_or_create_referral_code(user_id)
        with self._lock:
            cur = self._conn.execute(
                "SELECT COUNT(*) AS n FROM user_referral_redemptions "
                "WHERE referrer_id = ?",
                (int(user_id),),
            )
            count = int(cur.fetchone()["n"])
        return {"code": code, "referred_count": count}

    def redeem_referral_code(self, user_id: int, code: str) -> Dict[str, Any]:
        """Record that ``user_id`` joined via ``code``. Phase 1 grants no
        reward — this only feeds the referrer's "X friends joined" counter
        (Phase 2 wires the 1-week-free-Auto grant on top of this same
        redemption record once Play Billing is live).

        Rejects an unknown code, a self-referral, and a referee who has
        already redeemed any code (first redemption is final — enforced
        at the DB layer by ``referee_id`` being the table's PK).
        """
        token = (code or "").strip().upper()
        if not token:
            return {"ok": False, "reason": "invalid_code"}
        with self._lock:
            cur = self._conn.execute(
                "SELECT user_id FROM user_referral_codes WHERE code = ?",
                (token,),
            )
            row = cur.fetchone()
            if row is None:
                return {"ok": False, "reason": "invalid_code"}
            referrer_id = int(row["user_id"])
            if referrer_id == int(user_id):
                return {"ok": False, "reason": "self_referral"}
            cur = self._conn.execute(
                "SELECT referrer_id FROM user_referral_redemptions "
                "WHERE referee_id = ?",
                (int(user_id),),
            )
            if cur.fetchone() is not None:
                return {"ok": False, "reason": "already_redeemed"}
            now = _now_iso()
            try:
                self._conn.execute(
                    "INSERT INTO user_referral_redemptions "
                    "(referee_id, referrer_id, code, redeemed_at) "
                    "VALUES (?, ?, ?, ?)",
                    (int(user_id), referrer_id, token, now),
                )
            except sqlite3.IntegrityError:
                return {"ok": False, "reason": "already_redeemed"}
            log.info(
                "user_overrides.redeem_referral_code referee_id={} "
                "referrer_id={} code={}", user_id, referrer_id, token,
            )
            return {"ok": True, "referrer_id": referrer_id}

    # ---- referral rewards (Phase 2, 2026-07-21) --------------------------
    # Ledger primitives only — reward policy (days, tier, caps, commission
    # rates/prices) and entitlement composition live in
    # ``src/api/referral_rewards.py``; these methods never read config.

    def grant_referral_reward(
        self,
        referrer_id: int,
        referee_id: int,
        *,
        days: int,
        tier: str,
        cap_days: int,
    ) -> Dict[str, Any]:
        """Bank ``days`` of ``tier`` for ``referrer_id``, keyed one-shot to
        ``referee_id``'s join.

        Grants stack SEQUENTIALLY: a new grant starts where the latest
        existing grant ends (or now, whichever is later), so five invites
        while a reward is running extend the window instead of overlapping
        into nothing.  ``cap_days`` bounds the total banked future window
        — a farm of fake joins can bank at most that far ahead.  Dedup is
        DB-level (``UNIQUE (user_id, source, ref_id)``): re-processing the
        same referee grants nothing.
        """
        with self._lock:
            result = self._grant_tier_window_locked(
                referrer_id,
                tier=tier,
                source="referral_join",
                ref_id=str(int(referee_id)),
                days=days,
                cap_days=cap_days,
            )
        if not result.get("granted"):
            log.info(
                "referral reward NOT granted ({}): referrer_id={} referee_id={}",
                result.get("reason"), referrer_id, referee_id,
            )
        else:
            log.info(
                "referral reward granted: referrer_id={} referee_id={} "
                "tier={} → {}",
                referrer_id, referee_id, tier, result["expires_at"],
            )
        return result

    def _grant_tier_window_locked(
        self,
        user_id: int,
        *,
        tier: str,
        source: str,
        ref_id: str,
        days: int,
        cap_days: int,
    ) -> Dict[str, Any]:
        """Insert one time-boxed tier grant on the user's single sequential
        entitlement timeline.  Caller holds ``self._lock``.

        Shared by every grant source (referral joins, the signup free
        trial) so they cannot overlap and silently waste each other's
        days: a new grant always starts at the later of *now* and the
        furthest existing expiry.  ``UNIQUE (user_id, source, ref_id)``
        makes each originating event one-shot.

        ``cap_days`` bounds the total banked window measured from *now* —
        the abuse bound on a source that can fire repeatedly (referral
        joins).  Pass ``0`` for no cap, which is right for a source the
        DB already limits to once per user ever: the signup trial promises
        7 days, so a trialist who happens to hold a referral window must
        get their 7 days appended, not clamped to nothing.

        Returns ``{"granted": True, "starts_at", "expires_at"}`` or
        ``{"granted": False, "reason": "cap_reached" | "duplicate"}``.
        """
        now = datetime.now(timezone.utc)
        row = self._conn.execute(
            "SELECT MAX(expires_at) AS latest FROM user_reward_grants "
            "WHERE user_id = ?",
            (int(user_id),),
        ).fetchone()
        latest = _parse_reward_ts(row["latest"]) if row is not None else None
        start = max(now, latest) if latest is not None else now
        end = start + timedelta(days=int(days))
        if int(cap_days) > 0:
            end = min(end, now + timedelta(days=int(cap_days)))
        # Sub-minute residues (clock drift between "now" here and the
        # previous grant's cap) are not a real grant — treat as capped.
        if end <= start + timedelta(minutes=1):
            return {"granted": False, "reason": "cap_reached"}
        try:
            self._conn.execute(
                "INSERT INTO user_reward_grants "
                "(user_id, tier, source, ref_id, starts_at, expires_at, "
                "created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    int(user_id),
                    str(tier),
                    str(source),
                    str(ref_id),
                    start.isoformat(),
                    end.isoformat(),
                    now.isoformat(),
                ),
            )
        except sqlite3.IntegrityError:
            return {"granted": False, "reason": "duplicate"}
        return {
            "granted": True,
            "starts_at": start.isoformat(),
            "expires_at": end.isoformat(),
        }

    def get_active_reward(
        self, user_id: int, *, now: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """The user's currently-running reward window, or None.

        Grants share one sequential timeline per user (see
        :meth:`grant_referral_reward`), so "active" is simply the row
        covering ``now`` with the furthest expiry.
        """
        ts = (now or datetime.now(timezone.utc)).isoformat()
        with self._lock:
            row = self._conn.execute(
                "SELECT tier, MAX(expires_at) AS expires_at "
                "FROM user_reward_grants "
                "WHERE user_id = ? AND starts_at <= ? AND expires_at > ?",
                (int(user_id), ts, ts),
            ).fetchone()
        if row is None or row["expires_at"] is None:
            return None
        return {"tier": str(row["tier"]), "expires_at": str(row["expires_at"])}

    def get_reward_summary(self, user_id: int) -> Dict[str, Any]:
        """Lifetime reward stats for the invite screen."""
        now = datetime.now(timezone.utc)
        with self._lock:
            rows = self._conn.execute(
                "SELECT starts_at, expires_at FROM user_reward_grants "
                "WHERE user_id = ?",
                (int(user_id),),
            ).fetchall()
        total_seconds = 0.0
        for row in rows:
            start = _parse_reward_ts(row["starts_at"])
            end = _parse_reward_ts(row["expires_at"])
            if start is not None and end is not None and end > start:
                total_seconds += (end - start).total_seconds()
        active = self.get_active_reward(user_id, now=now)
        return {
            "reward_days_earned": int(round(total_seconds / 86400.0)),
            "reward_active_tier": active["tier"] if active else None,
            "reward_active_until": active["expires_at"] if active else None,
        }

    def get_redemption_for_referee(
        self, referee_id: int
    ) -> Optional[Dict[str, Any]]:
        """The redemption row that made ``referee_id`` a referee, or None."""
        with self._lock:
            row = self._conn.execute(
                "SELECT referrer_id, code, redeemed_at, converted_at "
                "FROM user_referral_redemptions WHERE referee_id = ?",
                (int(referee_id),),
            ).fetchone()
        if row is None:
            return None
        return {
            "referrer_id": int(row["referrer_id"]),
            "code": str(row["code"]),
            "redeemed_at": str(row["redeemed_at"]),
            "converted_at": row["converted_at"],
        }

    def mark_referral_converted(self, referee_id: int) -> bool:
        """Stamp the referee's first verified paid purchase.  Returns True
        only on the first call (the conversion moment); later paid periods
        return False.  Consumes the referee's one-time discount."""
        with self._lock:
            cur = self._conn.execute(
                "UPDATE user_referral_redemptions SET converted_at = ? "
                "WHERE referee_id = ? AND converted_at IS NULL",
                (_now_iso(), int(referee_id)),
            )
            return cur.rowcount > 0

    def count_commission_periods(self, referee_id: int) -> int:
        """How many billing periods of this referee have already accrued
        commission (enforces the first-N-periods cap across channels)."""
        with self._lock:
            row = self._conn.execute(
                "SELECT COUNT(*) AS n FROM referral_commissions "
                "WHERE referee_id = ?",
                (int(referee_id),),
            ).fetchone()
        return int(row["n"])

    def accrue_referral_commission(
        self,
        *,
        referrer_id: int,
        referee_id: int,
        product_id: str,
        purchase_token: str,
        period_expiry: str,
        amount: float,
        currency: str,
        rate: float,
    ) -> bool:
        """Insert one accrual row; idempotent on (purchase_token,
        period_expiry) so RTDN redeliveries / re-verifies of the same
        billing period never double-credit.  Returns True when a new row
        was actually inserted."""
        with self._lock:
            cur = self._conn.execute(
                "INSERT OR IGNORE INTO referral_commissions "
                "(referrer_id, referee_id, product_id, purchase_token, "
                "period_expiry, amount, currency, rate, status, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'accrued', ?)",
                (
                    int(referrer_id),
                    int(referee_id),
                    str(product_id),
                    str(purchase_token),
                    str(period_expiry),
                    float(amount),
                    str(currency).upper(),
                    float(rate),
                    _now_iso(),
                ),
            )
            inserted = cur.rowcount > 0
        if inserted:
            log.info(
                "referral commission accrued: referrer_id={} referee_id={} "
                "product={} amount={} {}",
                referrer_id, referee_id, product_id, amount, currency,
            )
        return inserted

    def get_commission_summary(self, referrer_id: int) -> Dict[str, Any]:
        """Per-currency accrued/paid totals + paid-referral count for the
        invite screen.  Currencies can mix (Play accrues in INR from the
        configured prices; the web rail accrues in USD from the actual
        payment), so totals are grouped, never summed across currencies."""
        with self._lock:
            rows = self._conn.execute(
                "SELECT currency, status, SUM(amount) AS total "
                "FROM referral_commissions WHERE referrer_id = ? "
                "GROUP BY currency, status",
                (int(referrer_id),),
            ).fetchall()
            converted = self._conn.execute(
                "SELECT COUNT(*) AS n FROM user_referral_redemptions "
                "WHERE referrer_id = ? AND converted_at IS NOT NULL",
                (int(referrer_id),),
            ).fetchone()
        totals: Dict[str, Dict[str, float]] = {}
        for row in rows:
            cur_totals = totals.setdefault(
                str(row["currency"]), {"accrued": 0.0, "paid": 0.0}
            )
            key = "paid" if str(row["status"]) == "paid" else "accrued"
            cur_totals[key] += float(row["total"] or 0.0)
        return {
            "commission_totals": [
                {"currency": currency, **amounts}
                for currency, amounts in sorted(totals.items())
            ],
            "paid_referred_count": int(converted["n"]),
        }

    def list_referral_commissions(
        self, *, status: Optional[str] = None, limit: int = 500
    ) -> List[Dict[str, Any]]:
        """Owner admin listing (ops Referrals panel).  Joins ``users`` for
        the referrer's phone — same SQLite file, so no cross-store hop —
        because the owner pays out manually and needs to know who to pay."""
        query = (
            "SELECT c.commission_id, c.referrer_id, c.referee_id, "
            "c.product_id, c.period_expiry, c.amount, c.currency, c.rate, "
            "c.status, c.created_at, c.paid_at, u.phone_e164 AS referrer_phone "
            "FROM referral_commissions c "
            "LEFT JOIN users u ON u.user_id = c.referrer_id "
        )
        params: List[Any] = []
        if status:
            query += "WHERE c.status = ? "
            params.append(str(status))
        query += "ORDER BY c.created_at DESC LIMIT ?"
        params.append(int(limit))
        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def mark_referral_commissions_paid(self, ids: Iterable[int]) -> int:
        """Flip accrued rows to paid (owner has settled them).  Returns the
        number of rows actually transitioned."""
        id_list = [int(i) for i in ids]
        if not id_list:
            return 0
        placeholders = ",".join("?" for _ in id_list)
        with self._lock:
            cur = self._conn.execute(
                "UPDATE referral_commissions SET status = 'paid', paid_at = ? "
                f"WHERE commission_id IN ({placeholders}) "
                "AND status = 'accrued'",
                [_now_iso(), *id_list],
            )
            return int(cur.rowcount)

    # ---- signup free trial (2026-07-25) ---------------------------------
    # Ledger primitives only — eligibility policy, the two dark-first flags
    # and entitlement composition live in ``src/api/signup_trial.py``; these
    # methods never read config.

    def observe_trial_eligibility(
        self, user_id: int, *, tier: str, days: int, shadow: bool
    ) -> Dict[str, Any]:
        """Record that ``user_id`` is trial-eligible, and return the row.

        Idempotent and one-shot: the first observation creates the funnel
        row (``eligible_at`` = now), every later call returns it unchanged.
        This is what makes the measurement flag independent of the
        user-visible one — the would-be cohort accumulates from ship day
        with ``shadow=1``, so the owner reads a real number before deciding
        whether to switch grants on.

        ``shadow`` is recorded only on creation: a row first seen while the
        offer was dark keeps ``shadow=1`` forever, which is the honest
        reading (we never actually offered that user anything on that day).
        """
        with self._lock:
            existing = self._get_trial_locked(user_id)
            if existing is not None:
                return existing
            self._conn.execute(
                "INSERT INTO user_trials "
                "(user_id, tier, days, eligible_at, shadow) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    int(user_id), str(tier), int(days), _now_iso(),
                    1 if shadow else 0,
                ),
            )
            row = self._get_trial_locked(user_id)
            assert row is not None  # just inserted
            log.info(
                "trial cohort: user_id={} tier={} days={} shadow={}",
                user_id, tier, days, shadow,
            )
            return row

    def mark_trial_offered(self, user_id: int) -> bool:
        """Stamp ``offered_at`` the first time the app is told the offer is
        genuinely live for this user.  Returns True on the transition.

        Deliberately separate from ``eligible_at``: the gap between the two
        is the dark window, and the gap between ``offered_at`` and
        ``claimed_at`` is what tells us whether the welcome copy works.
        """
        with self._lock:
            cur = self._conn.execute(
                "UPDATE user_trials SET offered_at = ? "
                "WHERE user_id = ? AND offered_at IS NULL",
                (_now_iso(), int(user_id)),
            )
            return int(cur.rowcount) > 0

    def claim_trial(
        self, user_id: int, *, tier: str, days: int
    ) -> Dict[str, Any]:
        """Burn the user's one trial and bank the entitlement grant.

        Atomic under one lock across BOTH tables: the ``user_trials`` row is
        stamped ``claimed_at``/``expires_at`` and the matching
        ``user_reward_grants`` window is inserted in the same critical
        section, so a crash or a double-tap can never leave a claimed trial
        with no entitlement (or an entitlement with no claim record).

        The ``claimed_at IS NULL`` guard plus ``UNIQUE (user_id, source,
        ref_id)`` on the grant make this idempotent at DB level — a
        double-tap gets ``already_claimed``, never a second 7 days.

        Returns ``{"claimed": bool, "reason"?, "tier", "expires_at"?}``.
        """
        with self._lock:
            row = self._get_trial_locked(user_id)
            if row is None:
                return {"claimed": False, "reason": "not_eligible"}
            if row["claimed_at"] is not None:
                return {
                    "claimed": False,
                    "reason": "already_claimed",
                    "expires_at": row["expires_at"],
                }
            grant = self._grant_tier_window_locked(
                user_id,
                tier=tier,
                source="signup_trial",
                ref_id="1",  # one trial per user ever — a constant ref_id
                days=days,
                # No cap: the PK above already limits this to once per user
                # ever, and capping from *now* would silently shrink the
                # promised window for a user who holds a referral reward.
                cap_days=0,
            )
            if not grant.get("granted"):
                # Do NOT stamp the claim, or the user would burn their one
                # trial for zero days.
                return {"claimed": False, "reason": str(grant.get("reason"))}
            now = _now_iso()
            self._conn.execute(
                "UPDATE user_trials SET claimed_at = ?, expires_at = ?, "
                # You cannot claim what you were never offered: backfill
                # offered_at so the funnel stays monotone (offered >=
                # claimed) even when a client claims without reading state
                # first, which would otherwise push claim_rate above 1.
                "offered_at = COALESCE(offered_at, ?), "
                "tier = ?, days = ? WHERE user_id = ?",
                (
                    now, grant["expires_at"], now, str(tier), int(days),
                    int(user_id),
                ),
            )
            log.info(
                "trial claimed: user_id={} tier={} days={} → {}",
                user_id, tier, days, grant["expires_at"],
            )
            return {
                "claimed": True,
                "tier": str(tier),
                "expires_at": grant["expires_at"],
            }

    def mark_trial_converted(self, user_id: int) -> bool:
        """Stamp ``converted_at`` on the user's first verified paid period
        after claiming a trial.  Returns True on the transition.

        Only claimed trials convert — an unclaimed cohort row staying NULL
        forever is the correct reading, so the trial→paid rate in ops is
        computed on people who actually trialled.
        """
        with self._lock:
            cur = self._conn.execute(
                "UPDATE user_trials SET converted_at = ? "
                "WHERE user_id = ? AND claimed_at IS NOT NULL "
                "AND converted_at IS NULL",
                (_now_iso(), int(user_id)),
            )
            converted = int(cur.rowcount) > 0
        if converted:
            log.info("trial converted to paid: user_id={}", user_id)
        return converted

    def _get_trial_locked(self, user_id: int) -> Optional[Dict[str, Any]]:
        row = self._conn.execute(
            "SELECT user_id, tier, days, eligible_at, offered_at, claimed_at, "
            "expires_at, converted_at, shadow FROM user_trials "
            "WHERE user_id = ?",
            (int(user_id),),
        ).fetchone()
        return dict(row) if row is not None else None

    def get_trial(self, user_id: int) -> Optional[Dict[str, Any]]:
        """The user's trial funnel row, or None if never observed."""
        with self._lock:
            return self._get_trial_locked(user_id)

    def trial_funnel_summary(self) -> Dict[str, Any]:
        """Aggregate trial funnel for ops → Trials (one grouped scan of a
        table with one row per eligible user; owner-only endpoint, never a
        hot path).

        ``cohort_dark`` vs ``cohort_live`` keeps the dark-window
        observations visibly separate from users who were really offered
        the trial, so the panel can't imply we shipped something we
        hadn't.
        """
        now = _now_iso()
        with self._lock:
            row = self._conn.execute(
                """
                SELECT
                    COUNT(*)                                      AS cohort,
                    SUM(CASE WHEN shadow = 1 THEN 1 ELSE 0 END)   AS cohort_dark,
                    SUM(CASE WHEN offered_at IS NOT NULL THEN 1 ELSE 0 END)
                                                                  AS offered,
                    SUM(CASE WHEN claimed_at IS NOT NULL THEN 1 ELSE 0 END)
                                                                  AS claimed,
                    SUM(CASE WHEN claimed_at IS NOT NULL
                              AND expires_at > ? THEN 1 ELSE 0 END)
                                                                  AS active,
                    SUM(CASE WHEN claimed_at IS NOT NULL
                              AND expires_at <= ? THEN 1 ELSE 0 END)
                                                                  AS lapsed,
                    SUM(CASE WHEN converted_at IS NOT NULL THEN 1 ELSE 0 END)
                                                                  AS converted
                FROM user_trials
                """,
                (now, now),
            ).fetchone()
        cohort = int(row["cohort"] or 0)
        claimed = int(row["claimed"] or 0)
        offered = int(row["offered"] or 0)
        converted = int(row["converted"] or 0)
        return {
            "cohort": cohort,
            "cohort_dark": int(row["cohort_dark"] or 0),
            "cohort_live": cohort - int(row["cohort_dark"] or 0),
            "offered": offered,
            "claimed": claimed,
            "active": int(row["active"] or 0),
            "lapsed": int(row["lapsed"] or 0),
            "converted": converted,
            # Rates are None (not 0.0) when the denominator is empty — an
            # unmeasured rate must not render as a real 0%.
            "claim_rate": (claimed / offered) if offered else None,
            "conversion_rate": (converted / claimed) if claimed else None,
        }

    def list_trials(
        self, *, limit: int = 200, claimed_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Most-recent trial rows for the ops table (bounded)."""
        clause = "WHERE claimed_at IS NOT NULL " if claimed_only else ""
        with self._lock:
            rows = self._conn.execute(
                "SELECT user_id, tier, days, eligible_at, offered_at, "
                "claimed_at, expires_at, converted_at, shadow "
                f"FROM user_trials {clause}"
                "ORDER BY COALESCE(claimed_at, eligible_at) DESC LIMIT ?",
                (int(limit),),
            ).fetchall()
        return [dict(r) for r in rows]

    # ---- paper subscription windows -------------------------------------

    def _open_paper_subscription_locked(self, user_id: int, now: str) -> str:
        """Insert a fresh active subscription, closing any prior active row
        first to preserve the at-most-one-active invariant. Must be called
        with self._lock held.

        Returns the new row's started_at (always equal to ``now``).
        """
        self._conn.execute(
            "UPDATE user_paper_subscriptions SET ended_at = ? "
            "WHERE user_id = ? AND ended_at IS NULL",
            (now, int(user_id)),
        )
        self._conn.execute(
            "INSERT INTO user_paper_subscriptions (user_id, started_at, ended_at) "
            "VALUES (?, ?, NULL)",
            (int(user_id), now),
        )
        return now

    def _close_paper_subscription_locked(
        self, user_id: int, now: str,
    ) -> Optional[str]:
        """Stamp ended_at on the user's currently-active subscription, if any.
        Idempotent — no-op when nothing is active. Returns ended_at when a
        row was closed, None otherwise. Must hold self._lock.
        """
        cur = self._conn.execute(
            "UPDATE user_paper_subscriptions SET ended_at = ? "
            "WHERE user_id = ? AND ended_at IS NULL",
            (now, int(user_id)),
        )
        return now if cur.rowcount > 0 else None

    def open_paper_subscription(self, user_id: int) -> str:
        """Public form of :meth:`_open_paper_subscription_locked` — wraps
        with the store lock. Used by the user-callable reset endpoint.
        """
        now = _now_iso()
        with self._lock:
            return self._open_paper_subscription_locked(int(user_id), now)

    def close_paper_subscription(self, user_id: int) -> Optional[str]:
        """Public form of :meth:`_close_paper_subscription_locked`."""
        now = _now_iso()
        with self._lock:
            return self._close_paper_subscription_locked(int(user_id), now)

    def reset_paper_subscription(self, user_id: int) -> str:
        """Atomically discard all prior subscription windows and open a
        single fresh one. Used by ``POST /api/auto-mode/paper/reset-mine``
        so the user can start truly clean — every pre-reset trade
        disappears from their view.

        Note we DELETE rather than close-and-mark: a closed (start, end)
        window would still admit any trade that closed inside it, which
        would defeat the "start fresh" semantics the bug-fix endpoint
        promises.

        Returns the new started_at ISO timestamp.
        """
        now = _now_iso()
        with self._lock:
            self._conn.execute(
                "DELETE FROM user_paper_subscriptions WHERE user_id = ?",
                (int(user_id),),
            )
            return self._open_paper_subscription_locked(int(user_id), now)

    def get_paper_subscriptions(
        self, user_id: int,
    ) -> List[Tuple[str, Optional[str]]]:
        """Return all subscription windows for the user, oldest-first.

        Each tuple is ``(started_at, ended_at_or_None)``. A None ended_at
        means the subscription is currently active — callers filtering
        trade rows should treat it as "open-ended through now".

        Empty list = user has never enabled paper. By design, the trade-
        filter helpers treat this as "show nothing", which is the bug fix.
        """
        with self._lock:
            cur = self._conn.execute(
                "SELECT started_at, ended_at FROM user_paper_subscriptions "
                "WHERE user_id = ? ORDER BY started_at ASC",
                (int(user_id),),
            )
            return [(row["started_at"], row["ended_at"]) for row in cur.fetchall()]

    # ---- auto-pause -----------------------------------------------------

    def pause_user_auto_trade(self, user_id: int, reason: str) -> Optional[str]:
        """Stamp the user as auto-paused with a typed reason. Idempotent:
        re-pausing a user already paused for the same reason is a no-op
        that returns the original ``paused_at`` (so the engine can detect
        "this was already paused" if it cares).

        Returns the ``paused_at`` timestamp on the row after the call,
        or None if no user row exists (paused state requires the
        auto-trade row to exist — the engine only dispatches to users
        who have already opted in).

        Used by :mod:`src.execution.signal_dispatch` after N consecutive
        Binance ``-2019`` rejects so the dispatcher stops sending new
        orders to a user whose Futures wallet is empty.
        """
        if not isinstance(reason, str) or not reason:
            return None
        now = _now_iso()
        with self._lock:
            cur = self._conn.execute(
                "SELECT paused_reason, paused_at FROM user_auto_trade_settings "
                "WHERE user_id = ?",
                (int(user_id),),
            )
            row = cur.fetchone()
            if row is None:
                return None
            existing_reason = row["paused_reason"]
            existing_at = row["paused_at"]
            if existing_reason == reason and existing_at:
                return existing_at  # already paused for this reason
            self._conn.execute(
                "UPDATE user_auto_trade_settings "
                "SET paused_reason = ?, paused_at = ?, updated_at = ? "
                "WHERE user_id = ?",
                (reason, now, now, int(user_id)),
            )
            log.info(
                "user_overrides.pause_user_auto_trade user_id={} reason={}",
                user_id, reason,
            )
            return now

    def resume_user_auto_trade(self, user_id: int) -> bool:
        """Clear ``paused_reason`` + ``paused_at`` so the dispatcher
        resumes sending orders to this user. Returns True if a paused
        row was cleared, False if the user wasn't paused.

        Called from the user-facing ``POST /api/auto-mode/resume-mine``
        endpoint after the user has topped up their Futures wallet (or
        otherwise resolved the original pause condition).
        """
        with self._lock:
            cur = self._conn.execute(
                "SELECT paused_reason FROM user_auto_trade_settings "
                "WHERE user_id = ? AND paused_reason IS NOT NULL",
                (int(user_id),),
            )
            row = cur.fetchone()
            if row is None:
                return False
            now = _now_iso()
            self._conn.execute(
                "UPDATE user_auto_trade_settings "
                "SET paused_reason = NULL, paused_at = NULL, updated_at = ? "
                "WHERE user_id = ?",
                (now, int(user_id)),
            )
            log.info(
                "user_overrides.resume_user_auto_trade user_id={}", user_id,
            )
            return True

    def is_user_auto_paused(self, user_id: int) -> bool:
        """Cheap check used by the dispatcher's per-signal skip-filter.

        Returns False on missing user row (no row → user never opted in;
        nothing to skip), False when paused_reason is NULL, True when
        paused_reason has a value.
        """
        with self._lock:
            cur = self._conn.execute(
                "SELECT paused_reason FROM user_auto_trade_settings "
                "WHERE user_id = ?",
                (int(user_id),),
            )
            row = cur.fetchone()
            if row is None:
                return False
            return bool(row["paused_reason"])

    def get_operator_auto_trade(self) -> Dict[str, Any]:
        """Return the operator's effective per-user auto-trade override.

        Single-operator MVP convenience: the engine's PaperOrderManager
        (and any other engine-side consumer that needs to know "what is
        the operator's configured leverage / position size") doesn't know
        which user_id to look up — the per-user overrides table is keyed
        on user_id, but the paper trader is engine-wide.  Until multi-user
        execution (Phase 3) attaches a user_id to each signal, we treat
        the most-recently-updated row as the operator's view.

        Returns an empty dict when no row exists yet — caller should fall
        back to ``src.user_settings`` engine-global defaults.

        Why this exists (2026-05-19): user reported paper-mode trades
        opening at 30× margin even though the Auto-trade page leverage
        slider was 10×.  Root cause was a two-store split — the app
        writes to ``user_auto_trade_settings`` (per-user, here), the
        paper trader reads from ``user_settings.json`` (engine-global).
        This accessor bridges them so paper-mode reflects the app slider.
        """
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM user_auto_trade_settings "
                "ORDER BY updated_at DESC LIMIT 1"
            )
            row = cur.fetchone()
            return _row_to_partial(row, _AUTO_TRADE_COL_TYPES) if row else {}

    # --- async variants ---

    async def aget_pretp(self, user_id: int) -> Dict[str, Any]:
        return await asyncio.to_thread(self.get_pretp, user_id)

    async def aupdate_pretp(
        self, user_id: int, partial: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await asyncio.to_thread(self.update_pretp, user_id, partial)

    async def aclear_pretp(self, user_id: int) -> Dict[str, Any]:
        return await asyncio.to_thread(self.clear_pretp, user_id)

    async def aget_invalidation(self, user_id: int) -> Dict[str, Any]:
        return await asyncio.to_thread(self.get_invalidation, user_id)

    async def aupdate_invalidation(
        self, user_id: int, partial: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await asyncio.to_thread(self.update_invalidation, user_id, partial)

    async def aclear_invalidation(self, user_id: int) -> Dict[str, Any]:
        return await asyncio.to_thread(self.clear_invalidation, user_id)

    async def aget_auto_trade(self, user_id: int) -> Dict[str, Any]:
        return await asyncio.to_thread(self.get_auto_trade, user_id)

    async def aget_paper_subscriptions(
        self, user_id: int
    ) -> List[Tuple[str, Optional[str]]]:
        return await asyncio.to_thread(self.get_paper_subscriptions, user_id)

    async def aupdate_auto_trade(
        self, user_id: int, partial: Dict[str, Any]
    ) -> Dict[str, Any]:
        return await asyncio.to_thread(self.update_auto_trade, user_id, partial)

    async def aresume_user_auto_trade(self, user_id: int) -> bool:
        return await asyncio.to_thread(self.resume_user_auto_trade, user_id)

    async def aget_symbol_management_map(self, user_id: int) -> Dict[str, str]:
        return await asyncio.to_thread(self.get_symbol_management_map, user_id)

    async def aset_symbol_management(
        self, user_id: int, symbol: str, mode: str,
    ) -> Dict[str, str]:
        return await asyncio.to_thread(
            self.set_symbol_management, user_id, symbol, mode
        )

    async def aget_referral_stats(self, user_id: int) -> Dict[str, Any]:
        return await asyncio.to_thread(self.get_referral_stats, user_id)

    async def agrant_referral_reward(
        self,
        referrer_id: int,
        referee_id: int,
        *,
        days: int,
        tier: str,
        cap_days: int,
    ) -> Dict[str, Any]:
        return await asyncio.to_thread(
            lambda: self.grant_referral_reward(
                referrer_id, referee_id, days=days, tier=tier, cap_days=cap_days,
            )
        )

    async def aget_active_reward(
        self, user_id: int
    ) -> Optional[Dict[str, Any]]:
        return await asyncio.to_thread(self.get_active_reward, user_id)

    async def aget_reward_summary(self, user_id: int) -> Dict[str, Any]:
        return await asyncio.to_thread(self.get_reward_summary, user_id)

    async def aget_redemption_for_referee(
        self, referee_id: int
    ) -> Optional[Dict[str, Any]]:
        return await asyncio.to_thread(self.get_redemption_for_referee, referee_id)

    async def amark_referral_converted(self, referee_id: int) -> bool:
        return await asyncio.to_thread(self.mark_referral_converted, referee_id)

    async def acount_commission_periods(self, referee_id: int) -> int:
        return await asyncio.to_thread(self.count_commission_periods, referee_id)

    async def aaccrue_referral_commission(self, **kwargs: Any) -> bool:
        return await asyncio.to_thread(
            lambda: self.accrue_referral_commission(**kwargs)
        )

    async def aget_commission_summary(self, referrer_id: int) -> Dict[str, Any]:
        return await asyncio.to_thread(self.get_commission_summary, referrer_id)

    async def alist_referral_commissions(
        self, *, status: Optional[str] = None, limit: int = 500
    ) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(
            lambda: self.list_referral_commissions(status=status, limit=limit)
        )

    async def aobserve_trial_eligibility(
        self, user_id: int, *, tier: str, days: int, shadow: bool
    ) -> Dict[str, Any]:
        return await asyncio.to_thread(
            lambda: self.observe_trial_eligibility(
                user_id, tier=tier, days=days, shadow=shadow,
            )
        )

    async def amark_trial_offered(self, user_id: int) -> bool:
        return await asyncio.to_thread(self.mark_trial_offered, user_id)

    async def aclaim_trial(
        self, user_id: int, *, tier: str, days: int
    ) -> Dict[str, Any]:
        return await asyncio.to_thread(
            lambda: self.claim_trial(user_id, tier=tier, days=days)
        )

    async def amark_trial_converted(self, user_id: int) -> bool:
        return await asyncio.to_thread(self.mark_trial_converted, user_id)

    async def aget_trial(self, user_id: int) -> Optional[Dict[str, Any]]:
        return await asyncio.to_thread(self.get_trial, user_id)

    async def atrial_funnel_summary(self) -> Dict[str, Any]:
        return await asyncio.to_thread(self.trial_funnel_summary)

    async def alist_trials(
        self, *, limit: int = 200, claimed_only: bool = False
    ) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(
            lambda: self.list_trials(limit=limit, claimed_only=claimed_only)
        )

    async def amark_referral_commissions_paid(self, ids: Iterable[int]) -> int:
        ids_list = list(ids)
        return await asyncio.to_thread(
            self.mark_referral_commissions_paid, ids_list
        )

    async def aredeem_referral_code(
        self, user_id: int, code: str
    ) -> Dict[str, Any]:
        return await asyncio.to_thread(self.redeem_referral_code, user_id, code)

    def close(self) -> None:
        with self._lock:
            self._conn.close()


# ---------------------------------------------------------------------------
# Module-level singleton accessor.
#
# Mirrors the ``user_settings`` module-level ``_STORE`` pattern so engine-
# side modules (paper_order_manager, etc.) can look up operator overrides
# without a constructor-time dependency injection.  ``bootstrap`` registers
# the store once via ``set_singleton`` after construction.  Tests can
# register a fresh in-memory store and tear it down via ``clear_singleton``.
# ---------------------------------------------------------------------------


_SINGLETON: Optional["UserOverridesStore"] = None


def set_singleton(store: "UserOverridesStore") -> None:
    global _SINGLETON
    _SINGLETON = store


def clear_singleton() -> None:
    global _SINGLETON
    _SINGLETON = None


def get_singleton() -> Optional["UserOverridesStore"]:
    return _SINGLETON


def resolve_notional_usd(firebase_uid: str, default: float) -> float:
    """Return the per-user notional override for ``firebase_uid``, or
    ``default`` if no override is set / store is offline / lookup fails.

    Called per-user by :func:`signal_dispatch.dispatch_signal_to_active_users`
    so each user's qty is computed from their own override.  Three
    lookup steps:

    1. ``user_overrides`` singleton → ``user_store`` singleton →
       ``get_by_firebase_uid(firebase_uid)`` → ``user_id``
    2. ``get_auto_trade(user_id)`` → ``notional_usd`` field
    3. Fall back to ``default`` (which the caller sets to
       ``_DEFAULT_NOTIONAL_USD`` in dispatch — $500).

    Soft-fail: any exception in steps 1–2 returns ``default``.  We
    must NEVER block a dispatch on an override lookup; the worst
    case is that a user's intended smaller notional falls back to
    $500 and Binance returns -2019 (which the dispatch event log
    surfaces in the Recent Activity card).
    """
    if _SINGLETON is None:
        return default
    try:
        from src.api import users as _users
        user_store = _users.get_singleton()
        if user_store is None:
            return default
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return default
        row = _SINGLETON.get_auto_trade(int(user.user_id))
        v = row.get("notional_usd")
        if isinstance(v, (int, float)) and float(v) > 0:
            return float(v)
        return default
    except Exception as exc:
        log.debug(
            "resolve_notional_usd: lookup failed for firebase_uid={} ({}); "
            "falling back to default ${}",
            firebase_uid, type(exc).__name__, default,
        )
        return default


def resolve_grab_fraction_uid(firebase_uid: str, default: float) -> float:
    """Return the per-user pre-TP grab fraction for ``firebase_uid``, or
    ``default`` (engine config ``PRE_TP_GRAB_FRACTION``) when unset.

    Same lookup pattern as :func:`resolve_notional_usd`.  Soft-fail:
    any exception returns ``default`` so a store blip never blocks dispatch.
    Result is clamped to B17 bounds [0.30, 1.00].
    """
    if _SINGLETON is None:
        return default
    try:
        from src.api import users as _users
        user_store = _users.get_singleton()
        if user_store is None:
            return default
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return default
        row = _SINGLETON.get_pretp(int(user.user_id))
        v = row.get("grab_fraction")
        if isinstance(v, (int, float)) and 0 < float(v) <= 1.0:
            return max(0.30, min(1.00, float(v)))
        return default
    except Exception as exc:
        log.debug(
            "resolve_grab_fraction_uid: lookup failed for firebase_uid={} ({}); "
            "falling back to default {}",
            firebase_uid, type(exc).__name__, default,
        )
        return default


def resolve_pretp_threshold_uid(firebase_uid: str, default: float) -> float:
    """Return the per-user pre-TP threshold percent for ``firebase_uid``,
    or ``default`` (engine config ``PRE_TP_THRESHOLD_PCT``) when unset.

    This is the move (in raw percent — 0.30 = 0.30%, not 30%) at which the
    pre-TP reduce-only LIMIT rests on Binance's book.  It realises the
    per-user "close at 0.3% vs 0.5%" dial: the app writes
    ``user_pretp_settings.threshold_pct`` and this resolver feeds it into
    ``place_signal`` so the LIMIT price is computed from the user's choice
    rather than the engine-wide default.

    Until 2026-06-01 the column was stored and surfaced but never read by
    the execution path — every user's pre-TP rested at the hard-coded
    ``place_signal`` default regardless of their setting.  This closes that
    gap, mirroring :func:`resolve_grab_fraction_uid`.

    Soft-fail: any lookup error returns ``default`` so a store blip never
    blocks dispatch.  Result is clamped to the sane scalp band
    [``_PRETP_THRESHOLD_PCT_MIN``, ``_PRETP_THRESHOLD_PCT_MAX``]; a stored
    value outside that band falls back to ``default``.
    """
    if _SINGLETON is None:
        return default
    try:
        from src.api import users as _users
        user_store = _users.get_singleton()
        if user_store is None:
            return default
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return default
        row = _SINGLETON.get_pretp(int(user.user_id))
        v = row.get("threshold_pct")
        if isinstance(v, (int, float)) and (
            _PRETP_THRESHOLD_PCT_MIN <= float(v) <= _PRETP_THRESHOLD_PCT_MAX
        ):
            return float(v)
        return default
    except Exception as exc:
        log.debug(
            "resolve_pretp_threshold_uid: lookup failed for firebase_uid={} "
            "({}); falling back to default {}",
            firebase_uid, type(exc).__name__, default,
        )
        return default


def resolve_pretp_enabled_uid(firebase_uid: str, default: bool = True) -> bool:
    """Return the per-user pre-TP master enable flag for ``firebase_uid``.

    The Lumin app exposes a master "Pre-TP grab" ON/OFF toggle that writes
    ``user_pretp_settings.enabled``.  Until 2026-05-29 this column was stored
    and surfaced but never consulted by the execution path, so a user who
    switched pre-TP OFF still had it fire on their account (the only thing
    that suppressed pre-TP was a non-empty exclusionary allowlist).  This
    resolver closes that gap: dispatch zeroes the grab fraction when this
    returns ``False`` so neither the FSM tick path nor the TradeMonitor
    backstop fires a partial close.

    Semantics: honour the stored boolean when the user has set it
    explicitly (True or False); when unset (no row / NULL column) fall back
    to ``default`` — ``True`` for the per-user FSM path, matching the app's
    default-ON master toggle and the §3.2a doctrine that pre-TP is the
    primary exit.  (This is distinct from the engine-wide ``PRE_TP_ENABLED``
    config flag, which gates the owner-account TradeMonitor backstop.)

    Soft-fail: any lookup error returns ``default`` so a store blip never
    blocks dispatch.
    """
    if _SINGLETON is None:
        return default
    try:
        from src.api import users as _users
        user_store = _users.get_singleton()
        if user_store is None:
            return default
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return default
        row = _SINGLETON.get_pretp(int(user.user_id))
        v = row.get("enabled")
        if isinstance(v, bool):
            return v
        return default
    except Exception as exc:
        log.debug(
            "resolve_pretp_enabled_uid: lookup failed for firebase_uid={} ({}); "
            "falling back to default {}",
            firebase_uid, type(exc).__name__, default,
        )
        return default


def resolve_pretp_allowlists_uid(
    firebase_uid: str,
) -> Tuple[Optional[FrozenSet[str]], Optional[FrozenSet[str]]]:
    """Return ``(regime_allowlist, setup_allowlist)`` for the user.

    Each element is either a non-empty frozenset of allowed values
    (restricting pre-TP to those regimes/setups) or ``None`` meaning
    "no restriction — allow all."

    Same soft-fail pattern as :func:`resolve_grab_fraction_uid`:
    any lookup error returns ``(None, None)`` so a store blip never
    blocks dispatch.  Callers treat ``None`` as "allow all".
    """
    if _SINGLETON is None:
        return None, None
    try:
        from src.api import users as _users
        user_store = _users.get_singleton()
        if user_store is None:
            return None, None
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return None, None
        row = _SINGLETON.get_pretp(int(user.user_id))
        regime_raw = row.get("regime_allowlist")
        setup_raw = row.get("setup_allowlist")
        regime_fs = (
            frozenset(str(r).upper() for r in regime_raw if r)
            if isinstance(regime_raw, list) and regime_raw
            else None
        )
        setup_fs = (
            frozenset(str(s).upper() for s in setup_raw if s)
            if isinstance(setup_raw, list) and setup_raw
            else None
        )
        return regime_fs, setup_fs
    except Exception as exc:
        log.debug(
            "resolve_pretp_allowlists_uid: lookup failed uid={} ({}); "
            "defaulting to allow-all",
            firebase_uid, type(exc).__name__,
        )
        return None, None


def resolve_invalidation_mode_uid(firebase_uid: str, default: str) -> str:
    """Return the per-user invalidation mode for ``firebase_uid``, or
    ``default`` (typically ``INVALIDATION_MODE_DEFAULT`` from config) when
    the user has no override, the store is offline, or the lookup fails.

    Same lookup pattern as :func:`resolve_grab_fraction_uid`.  Soft-fail:
    any exception returns ``default`` so a store blip never blocks dispatch.
    Stored values are validated against ``_VALID_INVALIDATION_MODES``; an
    invalid stored token (shouldn't happen after ``_coerce_invalidation``,
    but defensive) falls back to ``default``.
    """
    if _SINGLETON is None:
        return default
    try:
        from src.api import users as _users
        user_store = _users.get_singleton()
        if user_store is None:
            return default
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return default
        row = _SINGLETON.get_invalidation(int(user.user_id))
        mode = row.get("mode")
        if isinstance(mode, str) and mode.lower() in _VALID_INVALIDATION_MODES:
            return mode.lower()
        return default
    except Exception as exc:
        log.debug(
            "resolve_invalidation_mode_uid: lookup failed uid={} ({}); "
            "defaulting to {}",
            firebase_uid, type(exc).__name__, default,
        )
        return default


def resolve_exit_mechanism_uid(firebase_uid: str) -> str:
    """Per-user live exit mechanism, or ``"default"`` (the SL/TP FSM).

    Same soft-fail shape as :func:`resolve_invalidation_mode_uid`, and the
    direction of the failure matters more here than anywhere else in this
    module: every error path returns ``default``, so a store blip, a missing
    user row or an unrecognised stored token all leave the position on the
    exit it has always had.  The governor can only ever be reached by an
    explicit, valid, stored opt-in.
    """
    if _SINGLETON is None:
        return EXIT_MECHANISM_DEFAULT
    try:
        from src.api import users as _users

        user_store = _users.get_singleton()
        if user_store is None:
            return EXIT_MECHANISM_DEFAULT
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return EXIT_MECHANISM_DEFAULT
        row = _SINGLETON.get_auto_trade(int(user.user_id))
        mech = row.get("exit_mechanism")
        if isinstance(mech, str) and mech.lower() in EXIT_MECHANISMS:
            return mech.lower()
        return EXIT_MECHANISM_DEFAULT
    except Exception as exc:
        log.debug(
            "resolve_exit_mechanism_uid: lookup failed uid={} ({}); "
            "defaulting to {}",
            firebase_uid, type(exc).__name__, EXIT_MECHANISM_DEFAULT,
        )
        return EXIT_MECHANISM_DEFAULT


def resolve_user_mode_uid(firebase_uid: str) -> Optional[str]:
    """Return the per-user auto-trade ``mode`` for ``firebase_uid``, or
    None when the user has no row / store is offline / lookup fails.

    The dispatcher uses this to decide whether to fire a real Binance
    order: ``mode == 'live'`` → dispatch; anything else (``'paper'``,
    ``'off'``, ``None``) → skip silently. This makes the in-app "Mode =
    live" gate the actual authority, instead of "user has connected a
    Binance key" which had been the implicit gate pre-2026-05-24.

    Soft-fail semantics: a lookup failure returns None, which the
    dispatcher treats as "user hasn't opted into live" and skips. The
    safe-by-default direction here matches B12 — capital preservation
    over signal volume — so a transient Firestore/SQLite outage can't
    accidentally fire live orders.
    """
    if _SINGLETON is None:
        return None
    try:
        from src.api import users as _users
        user_store = _users.get_singleton()
        if user_store is None:
            return None
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return None
        row = _SINGLETON.get_auto_trade(int(user.user_id))
        mode = row.get("mode")
        if isinstance(mode, str) and mode:
            return mode.lower()
        return None
    except Exception as exc:
        log.debug(
            "resolve_user_mode_uid: lookup failed for firebase_uid={} "
            "({}); treating as 'not live'",
            firebase_uid, type(exc).__name__,
        )
        return None


def resolve_auto_trade_preferences_uid(
    firebase_uid: str,
) -> Tuple[Optional[FrozenSet[str]], Optional[FrozenSet[str]]]:
    """Return ``(path_preference, regime_preference)`` for the user as
    LIVE trade-eligibility filters.

    Each element is either ``None`` ("no preference set — every path /
    regime is eligible", the default-all path) or a frozenset of the
    allowed values.  An **empty** frozenset is meaningful and distinct
    from ``None``: it means the user explicitly chose nothing, so *no*
    signal matches → block-all (mirrors ``symbol_preference == []``).

    Soft-fail pattern matches the other ``*_uid`` resolvers: any lookup
    error returns ``(None, None)`` so a store blip never silently blocks
    a user's live dispatch.  ``regime`` values are stored already
    normalised to backend labels (``TRENDING_UP`` …) by
    ``_normalise_regime_input`` at write time, so the dispatcher can
    compare ``regime_label.upper()`` directly.
    """
    if _SINGLETON is None:
        return None, None
    try:
        from src.api import users as _users
        user_store = _users.get_singleton()
        if user_store is None:
            return None, None
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return None, None
        row = _SINGLETON.get_auto_trade(int(user.user_id))
        path_raw = row.get("path_preference")
        regime_raw = row.get("regime_preference")
        path_fs = (
            frozenset(str(s).upper() for s in path_raw)
            if isinstance(path_raw, list)
            else None
        )
        regime_fs = (
            frozenset(str(r).upper() for r in regime_raw)
            if isinstance(regime_raw, list)
            else None
        )
        return path_fs, regime_fs
    except Exception as exc:
        log.debug(
            "resolve_auto_trade_preferences_uid: lookup failed uid={} ({}); "
            "defaulting to allow-all",
            firebase_uid, type(exc).__name__,
        )
        return None, None


def resolve_paper_preferences_uid(
    firebase_uid: str,
) -> Tuple[
    Optional[FrozenSet[str]], Optional[FrozenSet[str]], Optional[FrozenSet[str]]
]:
    """Return ``(symbol, path, regime)`` PAPER eligibility filters for the
    user — the per-user-paper analogue of the live filters, consumed by the
    per-user paper book fan-out.

    Each element is ``None`` (no preference — all eligible) or a frozenset
    of allowed values (an **empty** frozenset = block-all, distinct from
    ``None``).  Same soft-fail contract as the live resolver: any lookup
    error returns ``(None, None, None)`` so a store blip never silently
    blocks a user's paper simulation.
    """
    if _SINGLETON is None:
        return None, None, None
    try:
        from src.api import users as _users
        user_store = _users.get_singleton()
        if user_store is None:
            return None, None, None
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return None, None, None
        row = _SINGLETON.get_auto_trade(int(user.user_id))

        def _fs(key: str) -> Optional[FrozenSet[str]]:
            raw = row.get(key)
            return (
                frozenset(str(x).upper() for x in raw)
                if isinstance(raw, list)
                else None
            )

        return (
            _fs("paper_symbol_preference"),
            _fs("paper_path_preference"),
            _fs("paper_regime_preference"),
        )
    except Exception as exc:
        log.debug(
            "resolve_paper_preferences_uid: lookup failed uid={} ({}); "
            "defaulting to allow-all",
            firebase_uid, type(exc).__name__,
        )
        return None, None, None


def resolve_symbol_management_uid(firebase_uid: str, symbol: str) -> str:
    """Return the per-(user, symbol) management mode — ``'full'`` (engine
    manages entry+SL+pre-TP+TP+invalidation) or ``'entry'`` (engine places
    entry + protective SL only, user manages the rest).

    Default ``'full'`` whenever the user hasn't set the symbol, the store
    is offline, or any lookup error occurs — the soft-fail direction is
    toward FULL engine management (the protective, capital-preserving
    default), never silently toward hands-off.
    """
    if _SINGLETON is None:
        return "full"
    try:
        from src.api import users as _users
        user_store = _users.get_singleton()
        if user_store is None:
            return "full"
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return "full"
        mode = _SINGLETON.get_symbol_management_map(
            int(user.user_id)
        ).get((symbol or "").upper())
        return mode if mode in _VALID_MANAGEMENT_MODES else "full"
    except Exception as exc:
        log.debug(
            "resolve_symbol_management_uid: lookup failed uid={} symbol={} "
            "({}); defaulting to full",
            firebase_uid, symbol, type(exc).__name__,
        )
        return "full"


def is_user_auto_paused_uid(firebase_uid: str) -> bool:
    """Firebase-UID-keyed wrapper around :meth:`UserOverridesStore.
    is_user_auto_paused`. Mirrors :func:`resolve_notional_usd` — same
    lookup path (firebase_uid → user_id via the UserStore singleton →
    pause-state check via the UserOverridesStore singleton).

    Soft-fail: any exception returns False so a lookup failure NEVER
    silently suppresses dispatch (the dispatcher can still log the
    rejection and the operator gets visibility). Worst case is the
    pre-2026-05-24 behaviour: keep dispatching to a paused user.
    """
    if _SINGLETON is None:
        return False
    try:
        from src.api import users as _users
        user_store = _users.get_singleton()
        if user_store is None:
            return False
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return False
        return _SINGLETON.is_user_auto_paused(int(user.user_id))
    except Exception as exc:
        log.debug(
            "is_user_auto_paused_uid: lookup failed for firebase_uid={} "
            "({}); treating as not-paused",
            firebase_uid, type(exc).__name__,
        )
        return False


def pause_user_auto_trade_uid(firebase_uid: str, reason: str) -> Optional[str]:
    """Firebase-UID-keyed wrapper around :meth:`UserOverridesStore.
    pause_user_auto_trade`. Same lookup pattern as
    :func:`is_user_auto_paused_uid`.

    Soft-fail: returns None on any lookup or store error. The dispatcher
    treats None as "couldn't persist the pause" and logs at WARNING so
    the operator notices — the next signal will retry the pause attempt.
    """
    if _SINGLETON is None:
        return None
    try:
        from src.api import users as _users
        user_store = _users.get_singleton()
        if user_store is None:
            return None
        user = user_store.get_by_firebase_uid(firebase_uid)
        if user is None:
            return None
        return _SINGLETON.pause_user_auto_trade(int(user.user_id), reason)
    except Exception as exc:
        log.warning(
            "pause_user_auto_trade_uid: persist failed for "
            "firebase_uid={} reason={} ({})",
            firebase_uid, reason, type(exc).__name__,
        )
        return None


def operator_auto_trade_override() -> Dict[str, Any]:
    """Convenience: ``get_singleton().get_operator_auto_trade()`` with
    fallback to ``{}`` when the singleton is unset (tests, boot order)."""
    store = _SINGLETON
    if store is None:
        return {}
    try:
        return store.get_operator_auto_trade()
    except Exception:
        log.exception("operator_auto_trade_override: store read failed")
        return {}


# Column-name → coerce-type tables, used by ``_row_to_partial`` so a
# stored ``1`` for boolean ``enabled`` round-trips as Python ``True``.
_PRETP_COL_TYPES: Dict[str, str] = {
    "enabled": "bool",
    "regime_allowlist": "json_list",
    "setup_allowlist": "json_list",
    "threshold_pct": "float",
    "atr_multiplier": "float",
    "fee_floor_pct": "float",
    "min_age_sec": "int",
    "max_age_sec": "int",
    "grab_fraction": "float",
    "protect_manual_entries": "bool",
}

_INVALIDATION_COL_TYPES: Dict[str, str] = {
    "mode": "str",
    "min_age_sec": "int",
    "momentum_threshold_mult": "float",
    "ema_crossover_enabled": "bool",
    "regime_shift_enabled": "bool",
    "trailing_kill_enabled": "bool",
    "trailing_mfe_r_threshold": "float",
    "trailing_retrace_pct": "float",
}

_AUTO_TRADE_COL_TYPES: Dict[str, str] = {
    "mode": "str",
    "position_size_pct": "float",
    "leverage_cap": "float",
    "max_concurrent_positions": "int",
    "symbol_preference": "json_list",
    "path_preference": "json_list",
    "regime_preference": "json_list",
    "paper_symbol_preference": "json_list",
    "paper_path_preference": "json_list",
    "paper_regime_preference": "json_list",
    "notional_usd": "float",
    "exit_mechanism": "str",
    "paused_reason": "str",
    "paused_at": "str",
}


def _row_to_partial(row: sqlite3.Row, col_types: Dict[str, str]) -> Dict[str, Any]:
    """Convert a SQLite row → partial dict, skipping NULL columns."""
    out: Dict[str, Any] = {}
    for col, kind in col_types.items():
        val = row[col]
        if val is None:
            continue
        if kind == "bool":
            out[col] = bool(val)
        elif kind == "json_list":
            try:
                parsed = json.loads(val)
            except (TypeError, ValueError):
                continue
            if isinstance(parsed, list):
                out[col] = parsed
        elif kind == "float":
            out[col] = float(val)
        elif kind == "int":
            out[col] = int(val)
        else:  # str
            out[col] = val
    return out


def _bool_to_int(v: Any) -> Optional[int]:
    if v is None:
        return None
    return 1 if bool(v) else 0


def _list_to_json(v: Any) -> Optional[str]:
    if v is None:
        return None
    return json.dumps(v, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Module-level singleton (mirrors UserStore.get_default_store pattern)
# ---------------------------------------------------------------------------


_store: Optional[UserOverridesStore] = None
_store_lock = threading.Lock()


def get_default_store(path: Path | str) -> UserOverridesStore:
    global _store
    with _store_lock:
        if _store is None:
            _store = UserOverridesStore(path)
        return _store


def reset_for_test(path: Optional[Path | str] = None) -> Optional[UserOverridesStore]:
    global _store
    with _store_lock:
        if _store is not None:
            try:
                _store.close()
            except Exception:  # pragma: no cover
                pass
            _store = None
        if path is not None:
            _store = UserOverridesStore(path)
        return _store
