"""CoinDCX position records — SQLite on the shared data volume.

The engine writes, the api reads (WAL), exactly as per-user settings flow the
other way.  Zero Firestore reads or writes: at the 1,000-member target a
per-transition Firestore write per user is avoidable cost, and nothing here
needs Firestore's properties.

This is **our record** of a position we opened.  The exchange is the source of
truth about whether the position exists; the reconciler compares the two
every cycle and this store follows the exchange.

States (a small set on purpose — the venue supports one exit shape):

* ``PENDING``          — row written, entry order about to be sent.  Written
  *before* the order so a crash between the two leaves something the
  reconciler can resolve against the exchange.
* ``ENTRY_UNCERTAIN``  — the entry call timed out or its fill never appeared;
  the reconciler adopts or retires it from what the exchange holds.
* ``OPEN``             — filled, with the position-level stop resting.
* ``CLOSING``          — we asked the exchange to exit.
* ``CLOSED``           — flat.  ``close_reason`` says why.
* ``REJECTED``         — no position was ever opened.
"""

from __future__ import annotations

import sqlite3
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils import get_logger

log = get_logger("venues.coindcx.positions")

PENDING = "PENDING"
ENTRY_UNCERTAIN = "ENTRY_UNCERTAIN"
OPEN = "OPEN"
CLOSING = "CLOSING"
CLOSED = "CLOSED"
REJECTED = "REJECTED"

STATES = (PENDING, ENTRY_UNCERTAIN, OPEN, CLOSING, CLOSED, REJECTED)
LIVE_STATES = (PENDING, ENTRY_UNCERTAIN, OPEN, CLOSING)
TERMINAL_STATES = (CLOSED, REJECTED)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS coindcx_positions (
    uid                 TEXT    NOT NULL,
    signal_id           TEXT    NOT NULL,
    symbol              TEXT    NOT NULL,
    pair                TEXT    NOT NULL,
    side                TEXT    NOT NULL,
    state               TEXT    NOT NULL,
    margin_currency     TEXT    NOT NULL,
    leverage            REAL    NOT NULL,
    qty                 REAL    NOT NULL,
    notional_usdt       REAL    NOT NULL DEFAULT 0,
    entry_target        REAL    NOT NULL,
    entry_filled        REAL    NOT NULL DEFAULT 0,
    sl_price            REAL    NOT NULL,
    tp_price            REAL    NOT NULL,
    position_id         TEXT    NOT NULL DEFAULT '',
    entry_order_id      TEXT    NOT NULL DEFAULT '',
    sl_order_id         TEXT    NOT NULL DEFAULT '',
    tp_order_id         TEXT    NOT NULL DEFAULT '',
    sl_resting          INTEGER NOT NULL DEFAULT 0,
    tp_resting          INTEGER NOT NULL DEFAULT 0,
    liquidation_price   REAL    NOT NULL DEFAULT 0,
    conversion_price    REAL    NOT NULL DEFAULT 0,
    exit_price          REAL    NOT NULL DEFAULT 0,
    realized_pnl_usdt   REAL,
    fees_usdt           REAL,
    close_reason        TEXT    NOT NULL DEFAULT '',
    last_error          TEXT    NOT NULL DEFAULT '',
    source              TEXT    NOT NULL DEFAULT 'auto',
    created_at          REAL    NOT NULL,
    opened_at           REAL,
    closed_at           REAL,
    updated_at          REAL    NOT NULL,
    PRIMARY KEY (uid, signal_id)
);
CREATE INDEX IF NOT EXISTS coindcx_positions_live
    ON coindcx_positions (state) WHERE state IN ('PENDING','ENTRY_UNCERTAIN','OPEN','CLOSING');
CREATE INDEX IF NOT EXISTS coindcx_positions_uid_created
    ON coindcx_positions (uid, created_at);
"""


@dataclass
class CoinDCXPosition:
    uid: str
    signal_id: str
    symbol: str
    pair: str
    side: str                   # "LONG" | "SHORT"
    state: str
    margin_currency: str        # "INR" | "USDT"
    leverage: float
    qty: float
    entry_target: float
    sl_price: float
    tp_price: float
    notional_usdt: float = 0.0
    entry_filled: float = 0.0
    position_id: str = ""
    entry_order_id: str = ""
    sl_order_id: str = ""
    tp_order_id: str = ""
    sl_resting: bool = False
    tp_resting: bool = False
    liquidation_price: float = 0.0
    conversion_price: float = 0.0
    exit_price: float = 0.0
    realized_pnl_usdt: Optional[float] = None
    fees_usdt: Optional[float] = None
    close_reason: str = ""
    last_error: str = ""
    source: str = "auto"
    created_at: float = field(default_factory=time.time)
    opened_at: Optional[float] = None
    closed_at: Optional[float] = None
    updated_at: float = field(default_factory=time.time)

    @property
    def live(self) -> bool:
        return self.state in LIVE_STATES

    @property
    def direction_sign(self) -> int:
        return 1 if self.side == "LONG" else -1

    def to_api(self) -> Dict[str, Any]:
        """The app's view.  ₹ figures only where CoinDCX published the
        conversion price used — never a rate we chose."""
        out = asdict(self)
        out["venue"] = "coindcx"
        rate = self.conversion_price if self.margin_currency == "INR" else 0.0
        out["realized_pnl_inr"] = (
            round(self.realized_pnl_usdt * rate, 2)
            if (rate > 0 and self.realized_pnl_usdt is not None) else None
        )
        out["notional_inr"] = round(self.notional_usdt * rate, 2) if rate > 0 else None
        return out


_COLUMNS = tuple(CoinDCXPosition.__dataclass_fields__.keys())


class CoinDCXPositionStore:
    """Thread-safe SQLite store.  One connection per process."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        if str(path) != ":memory:":
            self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(
            str(path), check_same_thread=False, isolation_level=None,
        )
        self._conn.row_factory = sqlite3.Row
        if str(path) != ":memory:":
            self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._conn.executescript(_SCHEMA)

    def put(self, pos: CoinDCXPosition) -> None:
        """Insert or replace one record (the whole row is the unit)."""
        pos.updated_at = time.time()
        row = asdict(pos)
        row["sl_resting"] = int(bool(pos.sl_resting))
        row["tp_resting"] = int(bool(pos.tp_resting))
        cols = ",".join(_COLUMNS)
        marks = ",".join("?" for _ in _COLUMNS)
        with self._lock:
            self._conn.execute(
                f"INSERT OR REPLACE INTO coindcx_positions ({cols}) VALUES ({marks})",
                tuple(row[c] for c in _COLUMNS),
            )

    def insert_new(self, pos: CoinDCXPosition) -> bool:
        """Insert only if no row exists for (uid, signal_id).

        The duplicate guard for a signal: a second dispatch of one signal to
        one user (a retry, a manual take racing the auto fan-out) must never
        send a second entry.  Returns ``False`` when a row already exists.
        """
        pos.updated_at = time.time()
        row = asdict(pos)
        row["sl_resting"] = int(bool(pos.sl_resting))
        row["tp_resting"] = int(bool(pos.tp_resting))
        cols = ",".join(_COLUMNS)
        marks = ",".join("?" for _ in _COLUMNS)
        with self._lock:
            cur = self._conn.execute(
                f"INSERT OR IGNORE INTO coindcx_positions ({cols}) VALUES ({marks})",
                tuple(row[c] for c in _COLUMNS),
            )
            return cur.rowcount == 1

    def get(self, uid: str, signal_id: str) -> Optional[CoinDCXPosition]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM coindcx_positions WHERE uid = ? AND signal_id = ?",
                (uid, signal_id),
            )
            row = cur.fetchone()
        return _from_row(row) if row else None

    def live_positions(self) -> List[CoinDCXPosition]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM coindcx_positions WHERE state IN (?,?,?,?) "
                "ORDER BY created_at",
                LIVE_STATES,
            )
            rows = cur.fetchall()
        return [_from_row(r) for r in rows]

    def live_for_signal(self, signal_id: str) -> List[CoinDCXPosition]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM coindcx_positions WHERE signal_id = ? "
                "AND state IN (?,?,?,?)",
                (signal_id, *LIVE_STATES),
            )
            rows = cur.fetchall()
        return [_from_row(r) for r in rows]

    def for_user(self, uid: str, *, limit: int = 50) -> List[CoinDCXPosition]:
        """Live rows first, then the most recent terminal ones."""
        with self._lock:
            cur = self._conn.execute(
                "SELECT * FROM coindcx_positions WHERE uid = ? "
                "ORDER BY CASE WHEN state IN (?,?,?,?) THEN 0 ELSE 1 END, "
                "created_at DESC LIMIT ?",
                (uid, *LIVE_STATES, int(max(1, min(limit, 500)))),
            )
            rows = cur.fetchall()
        return [_from_row(r) for r in rows]

    def summary(self) -> Dict[str, Any]:
        """Counts for ops — per state, plus users with a live position."""
        with self._lock:
            by_state = {
                r["state"]: r["n"]
                for r in self._conn.execute(
                    "SELECT state, COUNT(*) AS n FROM coindcx_positions GROUP BY state"
                ).fetchall()
            }
            users_live = self._conn.execute(
                "SELECT COUNT(DISTINCT uid) FROM coindcx_positions WHERE state IN (?,?,?,?)",
                LIVE_STATES,
            ).fetchone()[0]
            reasons = {
                r["close_reason"] or "": r["n"]
                for r in self._conn.execute(
                    "SELECT close_reason, COUNT(*) AS n FROM coindcx_positions "
                    "WHERE state = 'CLOSED' GROUP BY close_reason"
                ).fetchall()
            }
        return {"by_state": by_state, "users_live": users_live, "close_reasons": reasons}


def _from_row(row: sqlite3.Row) -> CoinDCXPosition:
    data = {k: row[k] for k in row.keys() if k in _COLUMNS}
    data["sl_resting"] = bool(data.get("sl_resting"))
    data["tp_resting"] = bool(data.get("tp_resting"))
    return CoinDCXPosition(**data)


_STORE: Optional[CoinDCXPositionStore] = None
_STORE_LOCK = threading.Lock()


def get_store() -> CoinDCXPositionStore:
    """Process-wide store at ``COINDCX_POSITIONS_DB`` (opened on first use)."""
    global _STORE
    with _STORE_LOCK:
        if _STORE is None:
            from config import COINDCX_POSITIONS_DB

            _STORE = CoinDCXPositionStore(COINDCX_POSITIONS_DB)
        return _STORE


def set_store_for_test(store: Optional[CoinDCXPositionStore]) -> None:
    global _STORE
    with _STORE_LOCK:
        _STORE = store
