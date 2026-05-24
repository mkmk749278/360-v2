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

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Tuple

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
    "notional_usd",
})

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
    symbol_preference        TEXT,     -- JSON list[str] or NULL = all
    notional_usd             REAL,     -- per-user notional cap; NULL = engine default ($500)
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


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
            # B17 — clamp into [0.30, 1.00].  Reject non-numeric silently to
            # match the existing drop-unknown behaviour; the API layer can
            # surface a 422 if it wants stricter feedback.
            if isinstance(value, (int, float)):
                clamped = max(
                    _PRETP_GRAB_FRACTION_MIN,
                    min(_PRETP_GRAB_FRACTION_MAX, float(value)),
                )
                out[key] = clamped
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
                if token in ("off", "paper", "live"):
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
        elif key == "symbol_preference":
            # Accept list[str] only.  Empty list → store as ``[]`` to
            # mean "explicitly chose nothing" (which the FSM treats as
            # "block ALL orders for this user").  This is the doctrine-
            # strict opt-out path — distinct from ``None`` which means
            # "no preference set, fall through to engine-wide allowlist".
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
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(_PRETP_SCHEMA + _INVALIDATION_SCHEMA + _AUTO_TRADE_SCHEMA)
        self._migrate_pretp_grab_fraction()
        self._migrate_pretp_protect_manual_entries()
        self._migrate_auto_trade_symbol_preference()
        self._migrate_auto_trade_notional_usd()
        self._migrate_auto_trade_pause_columns()
        log.info("UserOverridesStore opened at {}", self._path)

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

    # ---- auto-trade ------------------------------------------------------

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
            sym_pref = merged.get("symbol_preference")
            sym_pref_json = (
                json.dumps(sym_pref) if isinstance(sym_pref, list) else None
            )
            self._conn.execute(
                """
                INSERT INTO user_auto_trade_settings (
                    user_id, mode, position_size_pct, leverage_cap,
                    max_concurrent_positions, symbol_preference,
                    notional_usd, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    mode = excluded.mode,
                    position_size_pct = excluded.position_size_pct,
                    leverage_cap = excluded.leverage_cap,
                    max_concurrent_positions = excluded.max_concurrent_positions,
                    symbol_preference = excluded.symbol_preference,
                    notional_usd = excluded.notional_usd,
                    updated_at = excluded.updated_at
                """,
                (
                    int(user_id),
                    merged.get("mode"),
                    merged.get("position_size_pct"),
                    merged.get("leverage_cap"),
                    merged.get("max_concurrent_positions"),
                    sym_pref_json,
                    merged.get("notional_usd"),
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
            if "mode" in cleaned and prior_mode != new_mode:
                if new_mode == "paper":
                    self._open_paper_subscription_locked(int(user_id), now)
                elif prior_mode == "paper":
                    self._close_paper_subscription_locked(int(user_id), now)
            return self.get_auto_trade(user_id)

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
    "notional_usd": "float",
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
