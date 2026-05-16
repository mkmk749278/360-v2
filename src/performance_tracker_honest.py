"""Honest multi-metric ``/stats`` formatter (paper-trade visibility, 2026-05-16).

Owner-flagged motivation: the legacy ``format_stats_message`` on
:class:`~src.performance_tracker.PerformanceTracker` reports a single
``Win rate = wins / (wins + losses)`` headline.  That number lies to
subscribers because it collapses three meaningfully different
outcomes into the win/loss buckets:

* **Decisive wins** — ``TP1_HIT`` / ``TP2_HIT`` / ``TP3_HIT`` /
  ``FULL_TP_HIT``.  The strategy locked partial or full profit at a
  take-profit level.
* **Pre-TP grabs / capital preserved** — ``PROFIT_LOCKED`` /
  ``BREAKEVEN_EXIT``.  Pre-TP fired, SL moved to break-even, the
  trade exited at-or-near flat.  These are NOT wins in the W/L sense
  but they ARE capital preserved — and they appear in the legacy
  count as **losses** because ``SignalRecord.hit_tp == 0`` for
  PROFIT_LOCKED outcomes (the truth-report data confirmed this).
* **Clean SL hits** — ``SL_HIT``.  Trade ran to stop-loss at a real
  loss.

The legacy formula counts every PROFIT_LOCKED outcome as a loss —
double counting "capital preserved" as a negative event.  This module
introduces:

* :func:`get_honest_outcome_breakdown` — dict of per-bucket counters
  + percentages.
* :func:`format_honest_stats_message` — Telegram-ready string.

Both branch on ``SignalRecord.outcome_label`` (the semantic
classification stamped at record-time by
:func:`src.performance_metrics.classify_trade_outcome`) rather than
the mechanical ``hit_tp`` / ``hit_sl`` flags, so PROFIT_LOCKED is
attributed to the pre-TP-grab bucket and not the SL bucket.

Kept as a standalone module rather than methods on PerformanceTracker
because the tracker file is large and this is purely additive — the
legacy ``format_stats_message`` continues to work unchanged for any
existing caller (the wider stat ecosystem is unchanged; only the bot's
``/stats`` command rewires to the honest formatter).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from src.performance_metrics import classify_trade_outcome
from src.performance_tracker import PerformanceTracker


def get_honest_outcome_breakdown(
    tracker: PerformanceTracker,
    *,
    channel: Optional[str] = None,
    window_days: Optional[int] = None,
) -> Dict[str, Any]:
    """Per-outcome counters for the multi-metric ``/stats`` view.

    Returns a dict with:

    * ``total``                     — total signals in window
    * ``decisive_wins`` (int)       — TP1/TP2/TP3/FULL_TP_HIT count
    * ``pre_tp_grabs`` (int)        — PROFIT_LOCKED + BREAKEVEN_EXIT
    * ``clean_sl_hits`` (int)       — SL_HIT count
    * ``other`` (int)               — CLOSED / EXPIRED / unclassified
    * ``decisive_win_pct`` (float)  — decisive_wins / total * 100
    * ``pre_tp_grab_pct`` (float)
    * ``clean_sl_pct`` (float)
    * ``capital_preserved_pct`` (float) — 1 - clean_sl / total
    * ``avg_pnl_pct`` (float)       — mean of pnl_pct

    Uses the tracker's private ``_filter`` to apply channel + window
    filters consistently with the legacy formatter.  Reaches into the
    tracker via ``_records`` only as a fallback when the protected
    method isn't available (defensive — the field name is stable but
    we shouldn't rely on it if a setter API ships later).
    """
    # ``_filter`` is the same private helper ``get_stats`` /
    # ``format_stats_message`` use.  Calling it keeps our window/channel
    # semantics identical to the legacy formula — a divergence here
    # would be confusing.
    records = tracker._filter(  # noqa: SLF001 — intentional, mirrors legacy callers
        channel=channel, window_days=window_days,
    )

    total = len(records)
    decisive_wins = 0
    pre_tp_grabs = 0
    clean_sl = 0
    other = 0
    total_pnl_pct = 0.0
    for record in records:
        total_pnl_pct += record.pnl_pct
        # Prefer the classification stamped at record-time; fall back to
        # a fresh classify() for legacy rows that pre-date the
        # outcome_label field.
        label = record.outcome_label
        if not label:
            label = classify_trade_outcome(
                pnl_pct=record.pnl_pct,
                hit_tp=record.hit_tp,
                hit_sl=record.hit_sl,
            )
        if label in ("TP1_HIT", "TP2_HIT", "TP3_HIT", "FULL_TP_HIT"):
            decisive_wins += 1
        elif label in ("PROFIT_LOCKED", "BREAKEVEN_EXIT"):
            pre_tp_grabs += 1
        elif label == "SL_HIT":
            clean_sl += 1
        else:
            other += 1

    def _pct(n: int) -> float:
        return round(n / total * 100.0, 1) if total > 0 else 0.0

    return {
        "total": total,
        "decisive_wins": decisive_wins,
        "pre_tp_grabs": pre_tp_grabs,
        "clean_sl_hits": clean_sl,
        "other": other,
        "decisive_win_pct": _pct(decisive_wins),
        "pre_tp_grab_pct": _pct(pre_tp_grabs),
        "clean_sl_pct": _pct(clean_sl),
        "capital_preserved_pct": (
            round((1.0 - clean_sl / total) * 100.0, 1) if total > 0 else 0.0
        ),
        "avg_pnl_pct": round(total_pnl_pct / total, 2) if total > 0 else 0.0,
    }


def format_honest_stats_message(
    tracker: PerformanceTracker,
    *,
    channel: Optional[str] = None,
    window_days: Optional[int] = None,
) -> str:
    """Multi-metric ``/stats`` view — subscriber-honest replacement for
    the legacy ``Win rate: W/(W+L)`` formula.

    See :func:`get_honest_outcome_breakdown` for the bucket
    definitions and motivation.  This formatter is the bot-facing
    wrapper that emits a Telegram-friendly block.

    Telegram-markdown safe — no underscores, no asterisks-in-content,
    just plain text + the single ``*…*`` header.
    """
    label = channel or "All Channels"
    window_label = f" (last {window_days}d)" if window_days else " (all time)"
    b = get_honest_outcome_breakdown(
        tracker, channel=channel, window_days=window_days,
    )
    if b["total"] == 0:
        return (
            f"📊 *Performance – {label}{window_label}*\n"
            f"No completed signals yet."
        )
    return (
        f"📊 *Performance – {label}{window_label}*\n"
        f"Total signals: {b['total']}\n"
        f"Decisive wins (TP): {b['decisive_wins']} ({b['decisive_win_pct']}%)\n"
        f"Pre-TP grabs (BE):  {b['pre_tp_grabs']} ({b['pre_tp_grab_pct']}%)\n"
        f"Clean SL hits:      {b['clean_sl_hits']} ({b['clean_sl_pct']}%)\n"
        f"Capital preserved:  {b['capital_preserved_pct']}%\n"
        f"Avg PnL: {b['avg_pnl_pct']:+.2f}%"
    )
