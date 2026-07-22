"""W1 cost-aware R — unit tests.

Covers the pure cost model, the dark-flag no-op guarantee (default-OFF == gross
byte-for-byte), and the two measurement seams (counterfactual `candidate_outcome`
+ gate EV `suppression_value_delta_r`) netting by *exactly* the modelled cost.
"""
from __future__ import annotations

import config
import pytest
from src import suppression_audit as sa
from src import trade_costs


def _pin_costs(monkeypatch, *, enabled: bool) -> None:
    """Deterministic cost model: 0.10 + 2*0.02 + 0.01 = 0.15% round-trip."""
    monkeypatch.setattr(config, "EDGE_COST_MODEL_ENABLED", enabled, raising=False)
    monkeypatch.setattr(config, "EDGE_TAKER_FEE_PCT_ROUND_TRIP", 0.10, raising=False)
    monkeypatch.setattr(config, "EDGE_SLIPPAGE_PCT_PER_SIDE", 0.02, raising=False)
    monkeypatch.setattr(config, "EDGE_FUNDING_PCT_ESTIMATE", 0.01, raising=False)


# ── pure model ─────────────────────────────────────────────────────────────

def test_round_trip_cost_pct_sums_terms():
    assert trade_costs.round_trip_cost_pct(
        taker_fee_round_trip_pct=0.10,
        slippage_pct_per_side=0.02,
        funding_pct_estimate=0.01,
    ) == pytest.approx(0.15)


def test_cost_in_r_is_cost_over_stop_distance():
    # entry=100, stop 1.0 away → 1% stop → 0.15% cost = 0.15R.
    assert trade_costs.cost_in_r(100.0, 1.0, cost_pct=0.15) == 0.15
    # a tighter stop is more cost-dominated.
    assert trade_costs.cost_in_r(100.0, 0.5, cost_pct=0.15) == 0.30


def test_cost_in_r_fails_toward_zero_on_bad_geometry():
    assert trade_costs.cost_in_r(0.0, 1.0, cost_pct=0.15) == 0.0
    assert trade_costs.cost_in_r(100.0, 0.0, cost_pct=0.15) == 0.0


def test_net_r_disabled_is_gross(monkeypatch):
    _pin_costs(monkeypatch, enabled=False)
    assert trade_costs.net_r(2.0, entry=100.0, sl_distance=1.0) == 2.0
    assert trade_costs.net_r(-1.0, entry=100.0, sl_distance=1.0) == -1.0


def test_net_r_enabled_subtracts_cost(monkeypatch):
    _pin_costs(monkeypatch, enabled=True)
    assert trade_costs.net_r(2.0, entry=100.0, sl_distance=1.0) == pytest.approx(1.85)
    assert trade_costs.net_r(-1.0, entry=100.0, sl_distance=1.0) == pytest.approx(-1.15)


def test_net_r_enabled_but_ungeometried_is_gross(monkeypatch):
    _pin_costs(monkeypatch, enabled=True)
    # No stop distance → can't cost it → fail toward gross, never fabricate drag.
    assert trade_costs.net_r(2.0, entry=100.0, sl_distance=0.0) == 2.0


# ── counterfactual seam: candidate_outcome ──────────────────────────────────

def _win_record():
    return {
        "classification": "WOULD_WIN",
        "side": "LONG",
        "entry": 100.0,
        "tp1": 102.0,
        "stop_loss": 99.0,
        "sl_distance": 1.0,
    }


def test_candidate_outcome_off_net_equals_gross(monkeypatch):
    _pin_costs(monkeypatch, enabled=False)
    out = sa.candidate_outcome(_win_record())
    assert out["r_multiple"] == 2.0
    assert out["gross_r_multiple"] == 2.0
    assert out["pnl_pct"] == 2.0


def test_candidate_outcome_on_nets_by_exact_cost(monkeypatch):
    _pin_costs(monkeypatch, enabled=True)
    out = sa.candidate_outcome(_win_record())
    assert out["gross_r_multiple"] == 2.0          # gross preserved
    assert out["r_multiple"] == pytest.approx(1.85)         # net = gross − cost_in_r
    assert out["pnl_pct"] == pytest.approx(1.85)            # pnl netted by round-trip %
    assert out["won"] is True                      # outcome flag unchanged


def test_candidate_outcome_loss_nets_worse_than_minus_one(monkeypatch):
    _pin_costs(monkeypatch, enabled=True)
    rec = {**_win_record(), "classification": "WOULD_LOSE"}
    out = sa.candidate_outcome(rec)
    assert out["gross_r_multiple"] == -1.0
    assert out["r_multiple"] == pytest.approx(-1.15)


# ── gate-EV seam: suppression_value_delta_r ─────────────────────────────────

def test_suppression_ev_off_is_gross(monkeypatch):
    _pin_costs(monkeypatch, enabled=False)
    assert sa.suppression_value_delta_r({**_win_record(), "classification": "WOULD_LOSE"}) == 1.0
    assert sa.suppression_value_delta_r(_win_record()) == -2.0  # forgone win
    assert sa.suppression_value_delta_r({**_win_record(), "classification": "WOULD_EXPIRE"}) == 0.0


def test_suppression_ev_on_credits_saved_cost(monkeypatch):
    _pin_costs(monkeypatch, enabled=True)
    # Suppressing a loser saves the 1R loss AND the round-trip cost.
    assert sa.suppression_value_delta_r({**_win_record(), "classification": "WOULD_LOSE"}) == pytest.approx(1.15)
    # Suppressing a winner forgoes the win but also dodges the cost.
    assert sa.suppression_value_delta_r(_win_record()) == pytest.approx(-1.85)
    # A would-expire trade would have paid the cost for nothing → suppression saves it.
    assert sa.suppression_value_delta_r({**_win_record(), "classification": "WOULD_EXPIRE"}) == pytest.approx(0.15)
