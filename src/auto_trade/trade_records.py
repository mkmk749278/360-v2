"""SQLite-backed structured per-trade ledger for paper-mode visibility.

Phase: paper-trade visibility (2026-05-16).

Why this exists
---------------
Pre-fix, Lumin subscribers could only see aggregate daily / weekly /
monthly P&L from ``data/pnl_history.json``.  They could not answer the
two questions every paper-trader asks:

* *Which* trade just closed, on what symbol, in what direction?
* What was the **ROI on my margin** — not the engine's pseudo-equity?

The dashboard total isn't useful when the user is mentally trading at
10x with $100 per position: they need the per-trade row showing
``net_pnl_usd / margin_usd * 100`` to understand the strategy.

Design
------
* Single SQLite database at ``data/paper_trades.sqlite``, WAL journaling
  so a TradeMonitor write doesn't block an API reader.
* One row per signal lifecycle.  Open → partial fills accumulate inside
  the row as a JSON column (no row-explosion for monitoring loops).
  Closed at terminal status (TP3 / SL / invalidated / expired).
* All public helpers are sync.  PaperOrderManager calls them from inside
  its `async` methods — the SQLite I/O is fast (~ms) and lives behind
  an RLock, matching the threading pattern of ``src.api.users.UserStore``.
* Atomic writes via the sqlite WAL — no tmp/rename dance needed for the
  db file itself.  Archive operations (``archive_all``) use a single
  transaction.
* Backward-compatible additive store: existing ``paper_pnl_state.json``
  and ``pnl_history.json`` write paths are NOT touched.  This module is
  the new structured ledger that runs alongside them.

Per-user ledgers (2026-06-20)
-----------------------------
Each public helper takes an optional ``db_path`` so a per-user paper book
(``PaperBookRegistry``) writes to its own isolated SQLite file
(``data/paper_books/paper_trades_user_<id>.sqlite``).  ``db_path=None`` keeps
the legacy shared ``paper_trades.sqlite`` path.  The engine-wide "one source"
view is the SUM across per-user books via ``list_trades_all_users`` /
``count_trades_all_users``.

Out of scope
------------
* Live-mode trade records (reconcile-via-exchange is a separate concern)
* Backfill from existing ``pnl_history.json`` (those entries lack the
  per-trade fields by design)
"""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils import get_logger

log = get_logger("trade_records")


# ---------------------------------------------------------------------------
# Path resolution — env-var override per CLAUDE.md B8 so tests can isolate
# per-tmp_path stores via the autouse conftest fixture without monkeypatching
# the module constant.
# ---------------------------------------------------------------------------

_DEFAULT_PATH: str = "data/paper_trades.sqlite"


def _resolve_db_path() -> Path:
    """Lazy env lookup matches ``pnl_history._resolve_history_path`` so the
    test fixture's ``monkeypatch.setenv`` takes effect on the next call.
    """
    return Path(os.getenv("PAPER_TRADES_DB_PATH", _DEFAULT_PATH))


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS paper_trades (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id         TEXT NOT NULL UNIQUE,
    symbol            TEXT NOT NULL,
    side              TEXT NOT NULL,
    entry             REAL NOT NULL,
    qty               REAL NOT NULL,
    leverage          REAL NOT NULL,
    position_size_pct REAL NOT NULL,
    notional_usd      REAL NOT NULL,
    margin_usd        REAL NOT NULL,
    partial_fills     TEXT NOT NULL DEFAULT '[]',
    close_reason      TEXT,
    close_price       REAL,
    gross_pnl_usd     REAL,
    fees_usd          REAL,
    net_pnl_usd       REAL,
    roi_pct_on_margin REAL,
    created_at        TEXT NOT NULL,
    closed_at         TEXT
);

CREATE INDEX IF NOT EXISTS idx_paper_trades_closed_at ON paper_trades(closed_at);
CREATE INDEX IF NOT EXISTS idx_paper_trades_symbol ON paper_trades(symbol);
"""


# ---------------------------------------------------------------------------
# Connection management — singleton per-path connection with WAL + RLock
# ---------------------------------------------------------------------------


_conn_lock = threading.RLock()
_conn_cache: Dict[str, sqlite3.Connection] = {}


def _get_conn(db_path: Optional[Any] = None) -> sqlite3.Connection:
    """Return the cached connection for ``db_path`` (or the resolved default).

    The cache key is the absolute path string — when the env var changes
    between tests, the per-test ``tmp_path`` produces a different key
    and we open a fresh connection.  Same threading discipline as
    ``UserStore``: ``check_same_thread=False`` + an RLock.

    Per-user paper books (2026-06-20) pass their own ``db_path`` so each
    user's paper trade ledger is an isolated SQLite file; the per-path
    connection cache already supports any number of them.
    """
    resolved = Path(db_path) if db_path is not None else _resolve_db_path()
    path = str(resolved.resolve())
    with _conn_lock:
        conn = _conn_cache.get(path)
        if conn is not None:
            return conn
        # Ensure parent dir exists before opening so a fresh install on
        # a clean VPS doesn't OperationalError.
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(
            path,
            check_same_thread=False,
            isolation_level=None,  # autocommit; we manage transactions
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.executescript(_SCHEMA_SQL)
        _conn_cache[path] = conn
        log.info("trade_records: opened SQLite store at {}", path)
        return conn


def reset_for_test() -> None:
    """Close all cached connections — used by tests that swap PAPER_TRADES_DB_PATH.

    Safe to call multiple times.  Re-opens lazily on the next API call.
    """
    with _conn_lock:
        for conn in _conn_cache.values():
            try:
                conn.close()
            except Exception:  # pragma: no cover — best effort
                pass
        _conn_cache.clear()


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    """ISO-8601 UTC stamp — matches ``UserStore`` and the API schemas."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Row materialisation
# ---------------------------------------------------------------------------


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert a sqlite3.Row to a plain dict with parsed ``partial_fills``.

    The API layer serialises this back to JSON via Pydantic; an
    intermediate dict step keeps the per-row materialisation symmetric
    with ``list_trades`` (single row from ``get_trade`` shouldn't differ
    in shape from a list entry).
    """
    raw = dict(row)
    fills_raw = raw.get("partial_fills") or "[]"
    try:
        raw["partial_fills"] = json.loads(fills_raw)
    except (TypeError, ValueError):
        log.warning(
            "trade_records: malformed partial_fills for signal_id={} — "
            "returning []", raw.get("signal_id"),
        )
        raw["partial_fills"] = []
    return raw


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def open_trade(
    *,
    signal_id: str,
    symbol: str,
    side: str,
    entry: float,
    qty: float,
    leverage: float,
    position_size_pct: float,
    db_path: Optional[Any] = None,
) -> Optional[int]:
    """Insert a new row at signal open and return its primary key.

    Idempotent on ``signal_id`` — if the row already exists (re-open
    race or restart-replay), returns the existing row's id without
    overwriting state.  This matches ``PaperOrderManager.place_market_order``
    which is itself idempotent.

    Returns ``None`` if any precondition fails (zero qty, non-positive
    entry, missing signal_id) — the caller logs a ``paper_trade_skip``
    marker and continues without a broker-side position.
    """
    if not signal_id:
        log.debug("trade_records.open_trade: empty signal_id, skipping")
        return None
    if entry <= 0 or qty <= 0 or leverage <= 0:
        log.warning(
            "trade_records.open_trade: degenerate inputs "
            "signal_id={} entry={} qty={} leverage={} — skipping",
            signal_id, entry, qty, leverage,
        )
        return None
    notional = entry * qty
    margin = notional / leverage if leverage > 0 else notional
    created_at = _now_iso()
    conn = _get_conn(db_path)
    with _conn_lock:
        existing = conn.execute(
            "SELECT id FROM paper_trades WHERE signal_id = ?", (signal_id,),
        ).fetchone()
        if existing is not None:
            return int(existing["id"])
        cur = conn.execute(
            """
            INSERT INTO paper_trades (
                signal_id, symbol, side, entry, qty, leverage,
                position_size_pct, notional_usd, margin_usd,
                partial_fills, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '[]', ?)
            """,
            (
                signal_id, symbol, side, float(entry), float(qty),
                float(leverage), float(position_size_pct), float(notional),
                float(margin), created_at,
            ),
        )
        log.info(
            "trade_records.open_trade signal_id={} symbol={} side={} "
            "entry={:.6f} qty={:.6f} leverage={:.1f}x notional=${:.2f} "
            "margin=${:.2f}",
            signal_id, symbol, side, entry, qty, leverage, notional, margin,
        )
        return int(cur.lastrowid)


def record_partial_fill(
    *,
    signal_id: str,
    tp_level: int,
    fraction: float,
    fill_price: float,
    pnl_usd: float,
    fee_usd: float,
    db_path: Optional[Any] = None,
) -> None:
    """Append a partial-fill event to the row's ``partial_fills`` JSON array.

    No-op when the signal doesn't have a row yet (e.g. paper-mode flipped
    on after a signal opened, so we have no record of its open) — logs a
    warning so the operator notices the asymmetry.

    Concurrency note: the read-modify-write of the JSON column happens
    under ``_conn_lock`` so two concurrent close events on the same
    signal can't lose a fill.  This is rare in practice (TradeMonitor
    serialises lifecycle events per signal) but the lock costs nothing.
    """
    if not signal_id:
        return
    fill_event = {
        "tp_level": int(tp_level),
        "fraction": float(fraction),
        "fill_price": float(fill_price),
        "pnl_usd": float(pnl_usd),
        "fee_usd": float(fee_usd),
        "ts": _now_iso(),
    }
    conn = _get_conn(db_path)
    with _conn_lock:
        row = conn.execute(
            "SELECT partial_fills FROM paper_trades WHERE signal_id = ?",
            (signal_id,),
        ).fetchone()
        if row is None:
            log.warning(
                "trade_records.record_partial_fill: no row for signal_id={} "
                "— partial-fill telemetry will be missing for this trade",
                signal_id,
            )
            return
        try:
            current = json.loads(row["partial_fills"] or "[]")
            if not isinstance(current, list):
                current = []
        except (TypeError, ValueError):
            current = []
        current.append(fill_event)
        conn.execute(
            "UPDATE paper_trades SET partial_fills = ? WHERE signal_id = ?",
            (json.dumps(current), signal_id),
        )


def close_trade(
    *,
    signal_id: str,
    close_reason: str,
    close_price: float,
    gross_pnl_usd: float,
    fees_usd: float,
    net_pnl_usd: float,
    db_path: Optional[Any] = None,
) -> Optional[Dict[str, Any]]:
    """Stamp the row as closed and compute ROI% on margin.

    ``roi_pct_on_margin`` is the headline metric subscribers see: how
    much of the user's locked margin (notional / leverage) was returned
    as net PnL.  At 10x leverage a +1% price move on the underlying
    becomes a +10% ROI on margin — that's the number that actually
    matters when sizing risk.

    Idempotent — re-calling on a row that is already closed (e.g. a
    redundant ``close_full`` after ``close_partial`` already took the
    last fraction) is a no-op that returns the existing row dict so
    the caller can still inspect state.

    Returns ``None`` when no row exists for ``signal_id``.
    """
    if not signal_id:
        return None
    closed_at = _now_iso()
    conn = _get_conn(db_path)
    with _conn_lock:
        row = conn.execute(
            "SELECT * FROM paper_trades WHERE signal_id = ?", (signal_id,),
        ).fetchone()
        if row is None:
            log.warning(
                "trade_records.close_trade: no row for signal_id={} — "
                "engine has no record of this paper trade's open", signal_id,
            )
            return None
        if row["closed_at"] is not None:
            # Idempotent re-close — return the already-closed view.
            return _row_to_dict(row)
        margin = float(row["margin_usd"]) if row["margin_usd"] else 0.0
        roi = (float(net_pnl_usd) / margin * 100.0) if margin > 0 else 0.0
        conn.execute(
            """
            UPDATE paper_trades
               SET close_reason      = ?,
                   close_price       = ?,
                   gross_pnl_usd     = ?,
                   fees_usd          = ?,
                   net_pnl_usd       = ?,
                   roi_pct_on_margin = ?,
                   closed_at         = ?
             WHERE signal_id = ?
            """,
            (
                close_reason, float(close_price), float(gross_pnl_usd),
                float(fees_usd), float(net_pnl_usd), float(roi),
                closed_at, signal_id,
            ),
        )
        log.info(
            "trade_records.close_trade signal_id={} reason={} "
            "close_price={:.6f} net_pnl=${:.4f} roi_on_margin={:+.2f}%",
            signal_id, close_reason, close_price, net_pnl_usd, roi,
        )
        updated = conn.execute(
            "SELECT * FROM paper_trades WHERE signal_id = ?", (signal_id,),
        ).fetchone()
        return _row_to_dict(updated) if updated is not None else None


def get_trade(
    signal_id: str, *, db_path: Optional[Any] = None
) -> Optional[Dict[str, Any]]:
    """Fetch one row by signal_id.  Returns None when missing."""
    if not signal_id:
        return None
    conn = _get_conn(db_path)
    with _conn_lock:
        row = conn.execute(
            "SELECT * FROM paper_trades WHERE signal_id = ?", (signal_id,),
        ).fetchone()
        return _row_to_dict(row) if row is not None else None


def list_trades(
    *,
    limit: int = 50,
    offset: int = 0,
    since_ts: Optional[str] = None,
    symbol: Optional[str] = None,
    include_open: bool = False,
    db_path: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Return paginated rows, newest closed-first.

    Default surface is "closed trades for the history tab".  Setting
    ``include_open=True`` lets dashboards mix in still-open positions
    when they want to render the live state alongside history.

    Filters:
    * ``since_ts`` (ISO-8601 UTC) — only rows closed at-or-after this
      timestamp.  Used by the app's incremental-fetch loop so it doesn't
      re-pull the full ledger on every refresh.
    * ``symbol`` — exact match on the symbol column.

    Sort: newest-first by ``closed_at`` (NULLs last) → newest open trades
    sort below the newest closed trades in mixed views, which is the
    right default for the history tab.
    """
    limit = max(1, min(int(limit), 500))
    offset = max(0, int(offset))
    where: List[str] = []
    params: List[Any] = []
    if not include_open:
        where.append("closed_at IS NOT NULL")
    if since_ts:
        where.append("closed_at >= ?")
        params.append(since_ts)
    if symbol:
        where.append("symbol = ?")
        params.append(symbol)
    where_sql = (" WHERE " + " AND ".join(where)) if where else ""
    params.extend([limit, offset])
    sql = (
        "SELECT * FROM paper_trades"
        f"{where_sql}"
        " ORDER BY (closed_at IS NULL), closed_at DESC, created_at DESC"
        " LIMIT ? OFFSET ?"
    )
    conn = _get_conn(db_path)
    with _conn_lock:
        rows = conn.execute(sql, params).fetchall()
        return [_row_to_dict(r) for r in rows]


def count_trades(
    *,
    since_ts: Optional[str] = None,
    symbol: Optional[str] = None,
    include_open: bool = False,
    db_path: Optional[Any] = None,
) -> int:
    """Return total matching rows — for ``TradeListResponse.total``.

    Filters mirror :func:`list_trades` so pagination math works.
    """
    where: List[str] = []
    params: List[Any] = []
    if not include_open:
        where.append("closed_at IS NOT NULL")
    if since_ts:
        where.append("closed_at >= ?")
        params.append(since_ts)
    if symbol:
        where.append("symbol = ?")
        params.append(symbol)
    where_sql = (" WHERE " + " AND ".join(where)) if where else ""
    conn = _get_conn(db_path)
    with _conn_lock:
        cur = conn.execute(
            f"SELECT COUNT(*) AS n FROM paper_trades{where_sql}", params,
        )
        return int(cur.fetchone()["n"])


# ---------------------------------------------------------------------------
# Per-user aggregate readers (2026-06-20) — "one source" for the engine-wide
# paper view is the SUM across every per-user book.  The app reads a single
# user's db via the ``db_path`` params above; the truth report + ops
# dashboard read the aggregate here.
# ---------------------------------------------------------------------------


_BOOKS_DIR_DEFAULT: str = "data/paper_books"


def _resolve_books_dir(books_dir: Optional[Any] = None) -> Path:
    if books_dir is not None:
        return Path(books_dir)
    return Path(os.getenv("PAPER_BOOKS_DIR", _BOOKS_DIR_DEFAULT))


def iter_user_db_paths(books_dir: Optional[Any] = None) -> List[Path]:
    """Discover every per-user paper-trade SQLite file in the books dir."""
    d = _resolve_books_dir(books_dir)
    if not d.exists():
        return []
    return sorted(d.glob("paper_trades_user_*.sqlite"))


def _sort_trades_newest_first(rows: List[Dict[str, Any]]) -> None:
    """In-place sort matching the SQL ORDER BY: open trades (closed_at NULL)
    last, then closed_at DESC, then created_at DESC.  Composed stable sorts,
    least-significant key first."""
    rows.sort(key=lambda r: (r.get("created_at") or ""), reverse=True)
    rows.sort(key=lambda r: (r.get("closed_at") or ""), reverse=True)
    rows.sort(key=lambda r: r.get("closed_at") is None)  # NULLs last (stable)


def list_trades_all_users(
    *,
    limit: int = 50,
    offset: int = 0,
    since_ts: Optional[str] = None,
    symbol: Optional[str] = None,
    include_open: bool = False,
    books_dir: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Merge ``list_trades`` across every per-user book, newest-first.

    Each returned row carries a ``user_id`` parsed from its source db file so
    diagnostic consumers can attribute the trade.  Pagination is applied to
    the merged stream.
    """
    limit = max(1, min(int(limit), 500))
    offset = max(0, int(offset))
    merged: List[Dict[str, Any]] = []
    for p in iter_user_db_paths(books_dir):
        uid = _user_id_from_db_path(p)
        rows = list_trades(
            limit=500, offset=0, since_ts=since_ts, symbol=symbol,
            include_open=include_open, db_path=p,
        )
        for r in rows:
            r["user_id"] = uid
        merged.extend(rows)
    _sort_trades_newest_first(merged)
    return merged[offset:offset + limit]


def count_trades_all_users(
    *,
    since_ts: Optional[str] = None,
    symbol: Optional[str] = None,
    include_open: bool = False,
    books_dir: Optional[Any] = None,
) -> int:
    """Total matching rows summed across every per-user book."""
    return sum(
        count_trades(
            since_ts=since_ts, symbol=symbol, include_open=include_open,
            db_path=p,
        )
        for p in iter_user_db_paths(books_dir)
    )


def _user_id_from_db_path(path: Path) -> Optional[int]:
    """``paper_trades_user_42.sqlite`` → 42 (None if unparseable)."""
    stem = path.stem  # paper_trades_user_42
    try:
        return int(stem.rsplit("_", 1)[1])
    except (IndexError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Reset / archive support (for the /api/auto-mode/paper/reset endpoint)
# ---------------------------------------------------------------------------


def archive_all(db_path: Optional[Any] = None) -> int:
    """Rename the live ``paper_trades`` table to a timestamped archive and
    re-create an empty live table.

    Preferred over a destructive ``DELETE FROM paper_trades`` because the
    owner sometimes wants to compare a fresh paper-equity session to the
    prior one — the archived rows remain queryable via ad-hoc SQLite
    until the operator opts to drop them.

    Returns the number of rows that were archived.

    Naming: ``paper_trades_archive_YYYYMMDDTHHMMSSZ`` (single-second
    granularity is fine — manual reset isn't going to fire twice in
    the same second).
    """
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive_name = f"paper_trades_archive_{stamp}"
    conn = _get_conn(db_path)
    with _conn_lock:
        count = int(
            conn.execute("SELECT COUNT(*) AS n FROM paper_trades")
            .fetchone()["n"]
        )
        if count == 0:
            # Nothing to archive — short-circuit so we don't create empty
            # archive tables polluting the schema.
            return 0
        # SQLite DDL (ALTER TABLE, CREATE TABLE) implicitly commits any
        # open transaction before executing, so the original "BEGIN +
        # ALTER + executescript + COMMIT" framing here always tripped
        # "cannot commit - no transaction is active" on the explicit
        # COMMIT (the ALTER had already auto-committed).  The except
        # branch then re-failed on the matching ROLLBACK.  Simplification:
        # drop the explicit transaction framing.  DDL is auto-committed
        # by SQLite per-statement; ``executescript`` also runs in its
        # own commit boundary; the rename + re-create sequence is
        # effectively atomic from any reader's perspective because
        # ``paper_trades`` either exists as the original or as the
        # newly-empty version — never both, never neither.
        try:
            conn.execute(
                f"ALTER TABLE paper_trades RENAME TO {archive_name}"
            )
            conn.executescript(_SCHEMA_SQL)
        except sqlite3.Error:
            log.exception(
                "trade_records.archive_all: rename+recreate failed; "
                "the paper_trades table may be in an inconsistent state — "
                "operator should inspect SQLite directly"
            )
            raise
        log.info(
            "trade_records.archive_all: archived {} rows to table {}",
            count, archive_name,
        )
        return count
