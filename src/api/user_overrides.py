"""Per-user settings overrides (Phase 2 of per-user expansion).

Stores per-user pre-TP + auto-trade preferences in SQLite tables that
sit alongside the ``users`` table in the same ``lumin.sqlite`` file.
Two tables, one row per user per surface:

    user_pretp_settings(user_id PK, enabled, regime_allowlist (JSON),
                        setup_allowlist (JSON), threshold_pct,
                        atr_multiplier, fee_floor_pct, min_age_sec,
                        max_age_sec, updated_at)

    user_auto_trade_settings(user_id PK, mode, position_size_pct,
                             leverage_cap, max_concurrent_positions,
                             updated_at)

NULL semantics: every column except the PK is nullable.  NULL =
"use the engine default" (which the API layer resolves from
``config/__init__.py`` and ``src.user_settings`` — the engine-wide
store).  A row exists for a user as soon as they PUT one setting;
fields they haven't set stay NULL.

The engine signal-evaluation path does NOT consume per-user values
in Phase 2.  It still reads from ``src.user_settings`` (engine-wide
defaults set by the operator) — same behaviour as today.  Phase 3
wires per-user execution: a paid user's app fires their own Binance
order using their per-user position_size_pct / leverage_cap; the
engine remains the single signal source.

This store deliberately mirrors the API of ``src.user_settings`` so
the app's existing GET/PUT round-trip pattern works without changes
on the wire — only the endpoint path differs.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, FrozenSet, Optional

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
})

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
})

_LEVERAGE_HARD_CAP: float = 30.0  # B12


_PRETP_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_pretp_settings (
    user_id           INTEGER PRIMARY KEY,
    enabled           INTEGER,
    regime_allowlist  TEXT,
    setup_allowlist   TEXT,
    threshold_pct     REAL,
    atr_multiplier    REAL,
    fee_floor_pct     REAL,
    min_age_sec       INTEGER,
    max_age_sec       INTEGER,
    updated_at        TEXT    NOT NULL,
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
    updated_at               TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
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
        elif key == "regime_allowlist":
            out[key] = _normalise_regime_input(value)
        elif key == "setup_allowlist":
            if isinstance(value, list):
                out[key] = sorted({
                    s.strip().upper() for s in value
                    if isinstance(s, str) and s.strip()
                })
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
        self._conn.executescript(_PRETP_SCHEMA + _AUTO_TRADE_SCHEMA)
        log.info("UserOverridesStore opened at {}", self._path)

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
                    min_age_sec, max_age_sec, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    enabled = excluded.enabled,
                    regime_allowlist = excluded.regime_allowlist,
                    setup_allowlist = excluded.setup_allowlist,
                    threshold_pct = excluded.threshold_pct,
                    atr_multiplier = excluded.atr_multiplier,
                    fee_floor_pct = excluded.fee_floor_pct,
                    min_age_sec = excluded.min_age_sec,
                    max_age_sec = excluded.max_age_sec,
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
                    now,
                ),
            )
            return self.get_pretp(user_id)

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
            self._conn.execute(
                """
                INSERT INTO user_auto_trade_settings (
                    user_id, mode, position_size_pct, leverage_cap,
                    max_concurrent_positions, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    mode = excluded.mode,
                    position_size_pct = excluded.position_size_pct,
                    leverage_cap = excluded.leverage_cap,
                    max_concurrent_positions = excluded.max_concurrent_positions,
                    updated_at = excluded.updated_at
                """,
                (
                    int(user_id),
                    merged.get("mode"),
                    merged.get("position_size_pct"),
                    merged.get("leverage_cap"),
                    merged.get("max_concurrent_positions"),
                    now,
                ),
            )
            return self.get_auto_trade(user_id)

    def close(self) -> None:
        with self._lock:
            self._conn.close()


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
}

_AUTO_TRADE_COL_TYPES: Dict[str, str] = {
    "mode": "str",
    "position_size_pct": "float",
    "leverage_cap": "float",
    "max_concurrent_positions": "int",
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
