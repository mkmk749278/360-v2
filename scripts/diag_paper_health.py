"""Why has the paper book stopped opening trades? — one-shot evidence dump.

Owner-reported 2026-07-10: the app's Paper tab froze right at the #707
deploy — no new paper positions or history rows while the engine book kept
dispatching and closing signals (POWERUSDT / TIAUSDT / EIGENUSDT / CLOUSDT /
OPUSDT all resolved with no paper counterpart).

The paper open path has many silent-skip exits (fan-out finds no paper-mode
users, per-user eligibility filters, risk-gate refusals, qty/notional
floors), each observable only in engine logs or on-disk state.  This script
joins every on-disk source so one run answers which gate is eating the
opens:

1. Engine boot config — AUTO_EXECUTION_MODE / PAPER_PER_USER_BOOKS.
2. ``user_auto_trade_settings`` — who is in paper/both mode (the fan-out
   cohort), plus their PAPER eligibility preferences.
3. Per-user paper books (``data/paper_books/``) — persisted equity and the
   per-user trades ledger's last open/close timestamps.
4. ``data/signal_history.json`` — engine-book signals in the window.
5. The join: per paper user × per recent signal, would the eligibility
   filter have admitted it, and does a ledger row exist?

Read-only; safe on the VPS::

    docker exec 360scalp-v2-engine python /app/scripts/diag_paper_health.py [--hours 30]

For gates that leave no disk trace (risk-gate refusal, qty_zero,
notional_floor, fan-out exceptions) finish with::

    docker logs 360scalp-v2-engine --since 30h 2>&1 | \
      grep -E "paper_trade_skip|paper fanout|Auto-execution|risk_gate"
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _connect_ro(path: str) -> Optional[sqlite3.Connection]:
    if not os.path.exists(path):
        return None
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as exc:
        print(f"  !! cannot open {path}: {exc}")
        return None


def _load_json(path: str) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def _parse_ts(v: Any) -> Optional[datetime]:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(float(v), tz=timezone.utc)
    if isinstance(v, str):
        try:
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _pref_set(raw: Any) -> Optional[set]:
    """None = all allowed; [] = block all; list = allowlist (uppercased)."""
    if raw is None:
        return None
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None
    if isinstance(raw, list):
        return {str(x).upper() for x in raw}
    return None


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=30.0)
    ap.add_argument("--lumin-db", default=os.getenv("LUMIN_DB_PATH", "data/lumin.sqlite"))
    ap.add_argument("--books-dir", default=os.getenv("PAPER_BOOKS_DIR", "data/paper_books"))
    ap.add_argument("--history", default=os.getenv("SIGNAL_HISTORY_PATH", "data/signal_history.json"))
    ap.add_argument("--shared-trades-db", default="data/paper_trades.sqlite")
    args = ap.parse_args(argv)
    since = datetime.now(timezone.utc) - timedelta(hours=args.hours)

    print("=" * 72)
    print(f"PAPER HEALTH — window: last {args.hours:.0f}h (since {since:%Y-%m-%d %H:%M} UTC)")
    print("=" * 72)

    # 1. Boot config ------------------------------------------------------
    print("\n[1] Engine boot config (env at container start)")
    print(f"    AUTO_EXECUTION_MODE   = {os.getenv('AUTO_EXECUTION_MODE', '(unset → default paper)')}")
    print(f"    PAPER_PER_USER_BOOKS  = {os.getenv('PAPER_PER_USER_BOOKS', '(unset → false = shared book)')}")
    print("    NOTE: a runtime auto-mode flip from ops is ephemeral and NOT visible")
    print("    here — check ops Control for the live mode if this looks right.")

    # 2. Paper cohort -----------------------------------------------------
    print("\n[2] Paper/both users (the fan-out cohort) + PAPER eligibility prefs")
    users: List[Dict[str, Any]] = []
    conn = _connect_ro(args.lumin_db)
    if conn is None:
        print(f"    !! {args.lumin_db} missing — the fan-out would see ZERO paper users")
    else:
        try:
            rows = conn.execute(
                "SELECT user_id, mode, paper_symbol_preference, "
                "paper_path_preference, paper_regime_preference, updated_at "
                "FROM user_auto_trade_settings"
            ).fetchall()
        except sqlite3.Error as exc:
            rows = []
            print(f"    !! query failed: {exc}")
        for r in rows:
            mode = (r["mode"] or "").lower()
            marker = " <-- PAPER COHORT" if mode in ("paper", "both") else ""
            print(
                f"    user_id={r['user_id']} mode={mode or '(null)'}"
                f" updated_at={r['updated_at']}{marker}"
            )
            if mode in ("paper", "both"):
                users.append(dict(r))
                for label, col in (
                    ("symbols", "paper_symbol_preference"),
                    ("paths", "paper_path_preference"),
                    ("regimes", "paper_regime_preference"),
                ):
                    pref = _pref_set(r[col])
                    if pref is not None:
                        note = "BLOCKS EVERYTHING" if not pref else f"allowlist={sorted(pref)}"
                        print(f"        paper {label}: {note}")
        if not users:
            print("    ** ZERO paper/both users — this alone freezes the paper book. **")
        conn.close()

    # 3. Per-user books ---------------------------------------------------
    print("\n[3] Per-user paper books on disk")
    book_files = sorted(glob.glob(os.path.join(args.books_dir, "paper_pnl_user_*.json")))
    if not book_files:
        print(f"    (none under {args.books_dir} — per-user books never created here)")
    for bf in book_files:
        uid = bf.rsplit("_", 1)[-1].split(".")[0]
        state = _load_json(bf) or {}
        pnl = state.get("realised_pnl_total", state)
        db = os.path.join(args.books_dir, f"paper_trades_user_{uid}.sqlite")
        last_open = last_close = opens_in_window = None
        tconn = _connect_ro(db)
        if tconn is not None:
            try:
                last_open = tconn.execute(
                    "SELECT MAX(created_at) FROM paper_trades").fetchone()[0]
                last_close = tconn.execute(
                    "SELECT MAX(closed_at) FROM paper_trades").fetchone()[0]
                opens_in_window = tconn.execute(
                    "SELECT COUNT(*) FROM paper_trades WHERE created_at >= ?",
                    (since.isoformat(),),
                ).fetchone()[0]
            except sqlite3.Error as exc:
                print(f"    !! {db}: {exc}")
            tconn.close()
        print(
            f"    user {uid}: persisted_pnl={pnl} "
            f"last_open={last_open} last_close={last_close} "
            f"opens_in_window={opens_in_window}"
        )

    # Legacy shared book (PAPER_PER_USER_BOOKS=false)
    sconn = _connect_ro(args.shared_trades_db)
    if sconn is not None:
        try:
            lo = sconn.execute("SELECT MAX(created_at) FROM paper_trades").fetchone()[0]
            n = sconn.execute(
                "SELECT COUNT(*) FROM paper_trades WHERE created_at >= ?",
                (since.isoformat(),),
            ).fetchone()[0]
            print(f"    shared book: last_open={lo} opens_in_window={n}")
        except sqlite3.Error:
            pass
        sconn.close()

    # 4. Engine-book signals in window -------------------------------------
    print("\n[4] Engine-book signals in the window (what paper SHOULD have taken)")
    history = _load_json(args.history) or []
    if isinstance(history, dict):
        history = list(history.values())
    recent: List[Dict[str, Any]] = []
    for rec in history:
        ts = _parse_ts(
            rec.get("dispatch_timestamp") or rec.get("create_timestamp")
            or rec.get("timestamp")
        )
        if ts is not None and ts >= since:
            recent.append(rec)
    print(f"    {len(recent)} signals since window start")

    # 5. The join ----------------------------------------------------------
    print("\n[5] Signal × paper-user verdicts")
    if not recent:
        print("    (no signals in window — the freeze is upstream: dispatch, not paper)")
    ledger_ids: Dict[str, set] = {}
    for bf in book_files:
        uid = bf.rsplit("_", 1)[-1].split(".")[0]
        db = os.path.join(args.books_dir, f"paper_trades_user_{uid}.sqlite")
        tconn = _connect_ro(db)
        ids: set = set()
        if tconn is not None:
            try:
                ids = {r[0] for r in tconn.execute("SELECT signal_id FROM paper_trades")}
            except sqlite3.Error:
                pass
            tconn.close()
        ledger_ids[uid] = ids

    for rec in recent:
        sid = str(rec.get("signal_id", "?"))
        sym = str(rec.get("symbol", "?")).upper()
        setup = str(rec.get("setup_class", "") or "").upper()
        regime = str(
            rec.get("entry_regime") or rec.get("market_phase") or ""
        ).split("|")[0].strip().upper()
        verdicts = []
        for u in users:
            uid = str(u["user_id"])
            sym_fs = _pref_set(u.get("paper_symbol_preference"))
            path_fs = _pref_set(u.get("paper_path_preference"))
            reg_fs = _pref_set(u.get("paper_regime_preference"))
            if sym_fs is not None and sym not in sym_fs:
                verdict = "excluded:symbol"
            elif path_fs is not None and setup not in path_fs:
                verdict = "excluded:path"
            elif reg_fs is not None and regime not in reg_fs:
                verdict = "excluded:regime"
            elif sid in ledger_ids.get(uid, set()):
                verdict = "opened"
            else:
                verdict = "ELIGIBLE-BUT-NO-LEDGER-ROW"
            verdicts.append(f"u{uid}:{verdict}")
        print(f"    {sid:<22} {sym:<14} {setup:<26} {' '.join(verdicts) or '(no paper users)'}")

    print(
        "\nIf rows read ELIGIBLE-BUT-NO-LEDGER-ROW, the skip happened inside the"
        "\nopen path (risk gate / qty_zero / notional_floor / fan-out exception)."
        "\nThose emit parseable markers — run:"
        "\n  docker logs 360scalp-v2-engine --since 30h 2>&1 | "
        "grep -E 'paper_trade_skip|paper fanout|Auto-execution|risk_gate'"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
