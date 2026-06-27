"""Reconcile the paper-book DOLLAR P&L (Lumin) against the signal-% feed (ops).

Why this exists (owner question, 2026-06-27): since the last full reset the
Lumin Pulse "Paper P&L" reads **green** (e.g. +$9.42) while the ops profit page
reads **red** (e.g. −18.6% total). Both are computed correctly — they are two
*different ledgers*:

* **ops profit page** = the signal-performance feed: every signal's *percentage*
  outcome (`real_pnl_pct` / TP1-full `strategy_pct`), equal-weighted, over the
  whole engine firehose. Source: ``data/signal_history.json``.
* **Lumin Pulse** = the paper-trade book: ``net_pnl_usd`` summed over the paper
  positions the engine actually *opened and closed*, sized as a % of a $1000
  paper-equity book with partial-TP banking + fees, filtered to the user's
  subscription window. Source: ``data/paper_trades.sqlite`` (``trade_records``).

They diverge for three structural reasons, which this diagnostic quantifies:

1. **Population** — the paper book only enters a *subset* of signals (routing,
   concurrency, one-position-per-symbol). Signals with no paper trade never
   touch the dollar number.
2. **Unit & sizing** — dollars on an equity-% book vs equal-weight percentages.
3. **Partial-TP banking** — a paper trade can bank a TP1 partial then stop the
   residual at break-even, closing **net-positive in dollars** even though the
   signal feed records the same name as a stop/expiry.

A green dollar number on a red percentage universe is therefore expected when
the banking + population effects are large enough — it is *not* proof of edge.
This script makes the bridge explicit so the two surfaces never look like a
contradiction (or hide a real accounting bug) again.

Reads the on-disk stores directly — no Redis, no running engine. Safe on the
VPS via::

    docker compose exec engine python /app/scripts/diag_paper_reconciliation.py
        [--since 2026-06-25] [--paper-db PATH] [--history PATH] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Allow ``python scripts/diag_paper_reconciliation.py`` to import ``src`` when
# run from the repo root (mirrors how the engine container invokes it).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


_DEFAULT_HISTORY_PATH = os.environ.get("SIGNAL_HISTORY_PATH", "data/signal_history.json")

# Closed-lifecycle statuses in the signal feed (mirror of the geometry diag).
_TERMINAL_STATUSES = frozenset({
    "SL_HIT", "BREAKEVEN_EXIT", "PROFIT_LOCKED", "INVALIDATED",
    "EXPIRED", "CANCELLED", "FULL_TP_HIT", "TP3_HIT",
})
# Paper close reasons that are nominal "losers" — a net-positive close under one
# of these is the partial-TP-banking signature (banked TP1, residual to BE/SL).
_LOSER_CLOSE_REASONS = frozenset({"sl_hit", "expired", "invalidated", "cancelled"})


def _f(v: Any) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _signal_pct(rec: Dict[str, Any]) -> float:
    """Realised % for a signal-feed record, tolerant of field-name drift."""
    for key in ("real_pnl_pct", "pnl_pct", "result_pct"):
        if rec.get(key) is not None:
            return _f(rec.get(key))
    return 0.0


@dataclass
class Reconciliation:
    paper_n: int = 0
    paper_net_usd: float = 0.0
    paper_gross_usd: float = 0.0
    paper_fees_usd: float = 0.0
    paper_wins: int = 0
    signal_n: int = 0
    signal_pct_sum: float = 0.0
    signal_wins: int = 0
    # Population bridge
    signals_not_papered: int = 0          # engine signal, paper never entered
    paper_not_in_feed: int = 0            # paper trade with no matching signal
    matched: int = 0
    matched_pct_sum: float = 0.0          # Σ signal-% over the matched subset
    # Banking bridge
    banked_savers: int = 0                # net-positive paper close on a "loser" reason
    banked_savers_usd: float = 0.0
    examples: List[str] = field(default_factory=list)


def reconcile(
    paper_rows: List[Dict[str, Any]],
    signal_rows: List[Dict[str, Any]],
) -> Reconciliation:
    """Pure bridge between the paper $ ledger and the signal % feed.

    ``paper_rows`` = ``trade_records.list_trades`` dicts (closed paper trades).
    ``signal_rows`` = ``signal_history.json`` records. Joined on ``signal_id``.
    """
    r = Reconciliation()

    closed_signals = {
        str(s.get("signal_id")): s
        for s in signal_rows
        if str(s.get("status") or "").upper() in _TERMINAL_STATUSES and s.get("signal_id")
    }
    paper_by_id: Dict[str, Dict[str, Any]] = {}
    for p in paper_rows:
        sid = str(p.get("signal_id") or "")
        if not sid or p.get("closed_at") in (None, ""):
            continue
        paper_by_id[sid] = p

    # Paper book aggregates (the dollar number Lumin sums).
    for sid, p in paper_by_id.items():
        net = _f(p.get("net_pnl_usd"))
        r.paper_n += 1
        r.paper_net_usd += net
        r.paper_gross_usd += _f(p.get("gross_pnl_usd"))
        r.paper_fees_usd += _f(p.get("fees_usd"))
        if net > 0:
            r.paper_wins += 1
        reason = str(p.get("close_reason") or "").lower()
        if net > 0 and reason in _LOSER_CLOSE_REASONS:
            r.banked_savers += 1
            r.banked_savers_usd += net
            if len(r.examples) < 8:
                r.examples.append(
                    f"{p.get('symbol')} {reason} → net +${net:.2f} (banked partial, residual to BE)"
                )

    # Signal feed aggregates (the percentage number ops sums).
    for sid, s in closed_signals.items():
        pct = _signal_pct(s)
        r.signal_n += 1
        r.signal_pct_sum += pct
        if pct > 0:
            r.signal_wins += 1
        if sid in paper_by_id:
            r.matched += 1
            r.matched_pct_sum += pct
        else:
            r.signals_not_papered += 1

    r.paper_not_in_feed = sum(1 for sid in paper_by_id if sid not in closed_signals)
    return r


def render(r: Reconciliation) -> str:
    def wr(w: int, n: int) -> str:
        return f"{(w / n * 100):.0f}%" if n else "—"

    lines: List[str] = []
    lines.append("=" * 68)
    lines.append("PAPER-BOOK ($, Lumin)  vs  SIGNAL-FEED (%, ops)  reconciliation")
    lines.append("=" * 68)
    lines.append("")
    lines.append("Paper book — closed paper trades (what Lumin Pulse sums):")
    lines.append(f"  trades         : {r.paper_n}")
    lines.append(f"  net P&L        : ${r.paper_net_usd:+.2f}   (gross ${r.paper_gross_usd:+.2f}, fees ${r.paper_fees_usd:.2f})")
    lines.append(f"  win rate       : {wr(r.paper_wins, r.paper_n)}  ({r.paper_wins}/{r.paper_n})")
    lines.append("")
    lines.append("Signal feed — closed signals (what ops profit sums):")
    lines.append(f"  signals        : {r.signal_n}")
    lines.append(f"  Σ realised %   : {r.signal_pct_sum:+.2f}%")
    lines.append(f"  win rate       : {wr(r.signal_wins, r.signal_n)}  ({r.signal_wins}/{r.signal_n})")
    lines.append("")
    lines.append("Bridge 1 — POPULATION (why the $ book ≠ the % universe):")
    lines.append(f"  signals the paper book NEVER entered : {r.signals_not_papered}")
    lines.append(f"  matched (signal + paper trade)       : {r.matched}")
    lines.append(f"  paper trades with no signal record   : {r.paper_not_in_feed}")
    lines.append(f"  Σ % over the matched subset only     : {r.matched_pct_sum:+.2f}%")
    lines.append("")
    lines.append("Bridge 2 — PARTIAL-TP BANKING (why $ can be green on red %):")
    lines.append(f"  paper trades net-positive on a 'loser' close : {r.banked_savers}")
    lines.append(f"  dollars that came from banked partials        : ${r.banked_savers_usd:+.2f}")
    for ex in r.examples:
        lines.append(f"    · {ex}")
    lines.append("")
    lines.append("Read: a green paper $ on a red % universe is the banking +")
    lines.append("population effect, NOT broad edge. Trust the % feed for edge.")
    lines.append("=" * 68)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# I/O wrappers (thin — the testable logic is in reconcile()).
# ---------------------------------------------------------------------------


def _load_signal_history(path: str) -> List[Dict[str, Any]]:
    try:
        with open(path, encoding="utf-8") as fp:
            data = json.load(fp)
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(data, dict):
        data = data.get("signals") or data.get("history") or []
    return data if isinstance(data, list) else []


def _load_paper_trades(db_path: Optional[str], since_ts: Optional[str], limit: int) -> List[Dict[str, Any]]:
    from src.auto_trade import trade_records

    rows: List[Dict[str, Any]] = []
    offset = 0
    page = 500
    while len(rows) < limit:
        batch = trade_records.list_trades(
            limit=min(page, limit - len(rows)),
            offset=offset,
            since_ts=since_ts,
            include_open=False,
            db_path=db_path,
        )
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < page:
            break
        offset += len(batch)
    return rows


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Reconcile paper $ P&L vs signal % feed.")
    ap.add_argument("--since", default=None, help="ISO date/timestamp; only paper trades closed at-or-after.")
    ap.add_argument("--paper-db", default=None, help="Override paper_trades.sqlite path.")
    ap.add_argument("--history", default=_DEFAULT_HISTORY_PATH, help="signal_history.json path.")
    ap.add_argument("--limit", type=int, default=2000, help="Max paper trades to read.")
    args = ap.parse_args(argv)

    paper_rows = _load_paper_trades(args.paper_db, args.since, args.limit)
    signal_rows = _load_signal_history(args.history)
    print(render(reconcile(paper_rows, signal_rows)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
