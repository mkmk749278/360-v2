"""Tests for the paper-$ vs signal-% reconciliation diag's pure core."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

# The diag lives under scripts/ (not a package) — load it by path. Register in
# sys.modules before exec so its @dataclass can resolve its own module.
_SPEC = importlib.util.spec_from_file_location(
    "diag_paper_reconciliation",
    Path(__file__).resolve().parent.parent / "scripts" / "diag_paper_reconciliation.py",
)
assert _SPEC and _SPEC.loader
_mod = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _mod
_SPEC.loader.exec_module(_mod)
reconcile = _mod.reconcile


def _sig(sid, status, pct):
    return {"signal_id": sid, "status": status, "real_pnl_pct": pct}


def _paper(sid, net, reason="tp1_hit", **kw):
    row = {"signal_id": sid, "symbol": kw.get("symbol", "ABCUSDT"),
           "net_pnl_usd": net, "gross_pnl_usd": kw.get("gross", net),
           "fees_usd": kw.get("fees", 0.0), "close_reason": reason,
           "closed_at": "2026-06-26T00:00:00+00:00"}
    return row


def test_population_bridge_counts_unpapered_signals():
    # 3 closed signals, but the paper book only entered 1 of them.
    signals = [_sig("A", "SL_HIT", -0.8), _sig("B", "EXPIRED", -0.5), _sig("C", "TP3_HIT", 2.0)]
    paper = [_paper("C", net=5.0, reason="tp3_hit")]
    r = reconcile(paper, signals)
    assert r.signal_n == 3
    assert r.matched == 1
    assert r.signals_not_papered == 2
    assert r.paper_not_in_feed == 0


def test_dollar_green_while_percent_red():
    # The headline case: % universe is net-negative, paper $ is net-positive
    # because the book only entered the winner.
    signals = [_sig("A", "SL_HIT", -0.8), _sig("B", "SL_HIT", -0.9), _sig("C", "TP3_HIT", 1.5)]
    paper = [_paper("C", net=9.42, reason="tp3_hit")]
    r = reconcile(paper, signals)
    assert r.signal_pct_sum < 0          # ops: red
    assert r.paper_net_usd > 0           # Lumin: green
    assert round(r.paper_net_usd, 2) == 9.42


def test_partial_tp_banking_saver_detected():
    # A trade that closed on a 'loser' reason but net-positive = banked partial.
    signals = [_sig("A", "SL_HIT", -0.2)]
    paper = [_paper("A", net=0.7, reason="sl_hit")]
    r = reconcile(paper, signals)
    assert r.banked_savers == 1
    assert round(r.banked_savers_usd, 2) == 0.70
    assert any("banked partial" in e for e in r.examples)


def test_loser_close_with_loss_is_not_a_banking_saver():
    signals = [_sig("A", "SL_HIT", -0.8)]
    paper = [_paper("A", net=-0.8, reason="sl_hit")]
    r = reconcile(paper, signals)
    assert r.banked_savers == 0
    assert r.paper_wins == 0


def test_open_paper_trades_and_non_terminal_signals_excluded():
    signals = [_sig("A", "ACTIVE", 0.0), _sig("B", "TP3_HIT", 1.0)]
    paper = [
        _paper("B", net=3.0, reason="tp3_hit"),
        {"signal_id": "C", "symbol": "XUSDT", "net_pnl_usd": 99.0, "closed_at": None},  # still open
    ]
    r = reconcile(paper, signals)
    assert r.signal_n == 1                # ACTIVE excluded
    assert r.paper_n == 1                 # open trade excluded
    assert r.paper_net_usd == 3.0


def test_aggregates_and_winrate():
    signals = [_sig("A", "SL_HIT", -0.8), _sig("B", "TP3_HIT", 1.2), _sig("C", "PROFIT_LOCKED", 0.5)]
    paper = [_paper("A", net=-0.8, reason="sl_hit"),
             _paper("B", net=2.0, reason="tp3_hit"),
             _paper("C", net=0.3, reason="profit_locked")]
    r = reconcile(paper, signals)
    assert r.paper_n == 3
    assert round(r.paper_net_usd, 2) == 1.50
    assert r.paper_wins == 2
    assert r.signal_wins == 2
    assert round(r.signal_pct_sum, 2) == 0.90
