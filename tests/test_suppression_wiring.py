"""End-to-end wiring tests for the shadow ledger (Layer C).

Covers the pieces added around the already-tested modules:
scanner stamp helper (tunable-gated, fail-open) → classify loop feed →
StrategyEdgeStore, and the shadow-strategy scanner pass (no emit path).
"""
from __future__ import annotations

import time
from types import SimpleNamespace

import pytest

from src import suppression_audit as sa
from src.scanner import Scanner
from src.smc import Direction
from src.strategy_edge import (
    SOURCE_SHADOW,
    SOURCE_SUPPRESSED,
    StrategyEdgeStore,
    StrategyOutcome,
)
from src.suppression_audit import SuppressedCandidateStore


@pytest.fixture()
def fresh_store(monkeypatch):
    store = SuppressedCandidateStore(persist_path="")
    monkeypatch.setattr(sa, "_store", store)
    return store


def _sig(**over):
    base = dict(
        symbol="ETHUSDT",
        channel="360_SCALP",
        setup_class="BREAKOUT_RETEST",
        direction=Direction.LONG,
        entry=100.0,
        stop_loss=99.0,
        tp1=101.5,
        confidence=70.0,
        mc_context_key="OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL",
        entry_regime="TRENDING_UP",
        valid_for_minutes=45.0,
    )
    base.update(over)
    return SimpleNamespace(**base)


class TestStampSuppressed:
    def test_stamps_when_enabled(self, fresh_store, monkeypatch):
        from src import runtime_tunables
        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        Scanner._stamp_suppressed(object(), _sig(), "quiet_scalp_block")
        assert fresh_store.pending_count() == 1
        rec = fresh_store.records()[0]
        assert rec["gate_name"] == "quiet_scalp_block"
        assert rec["context_key"] == "OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL"
        assert rec["side"] == "LONG"

    def test_no_stamp_when_tunable_off(self, fresh_store, monkeypatch):
        from src import runtime_tunables
        monkeypatch.setattr(runtime_tunables, "get", lambda key: False)
        Scanner._stamp_suppressed(object(), _sig(), "dispatch_cooldown")
        assert fresh_store.pending_count() == 0

    def test_fail_open_on_garbage_signal(self, fresh_store, monkeypatch):
        from src import runtime_tunables
        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        # Must never raise, whatever the sig looks like.
        Scanner._stamp_suppressed(object(), object(), "regime_kill")
        Scanner._stamp_suppressed(object(), _sig(entry=None), "regime_kill")

    def test_untradeable_geometry_not_recorded(self, fresh_store, monkeypatch):
        from src import runtime_tunables
        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        Scanner._stamp_suppressed(object(), _sig(tp1=0.0), "data_stale")
        assert fresh_store.pending_count() == 0


class TestClassifyToEdgeFeed:
    def test_suppressed_candidate_flows_into_edge_matrix(self, fresh_store, monkeypatch):
        from src import runtime_tunables
        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        Scanner._stamp_suppressed(object(), _sig(), "quiet_scalp_block")
        # Backdate the stamp so the classify window has elapsed.
        fresh_store.records()[0]["suppress_timestamp"] = time.time() - 7200
        edge_store = StrategyEdgeStore(min_samples=1, persist_path="")

        def fetch_ohlc_since(symbol, since_ts, _rec=None):
            # Price runs straight to TP1 without touching SL → WOULD_WIN.
            return {"high": [100.5, 102.0], "low": [99.8, 100.2], "close": [100.4, 101.9]}

        def _feed_edge(rec):
            outcome = sa.candidate_outcome(rec)
            if not outcome:
                return
            is_shadow = str(rec.get("gate_name", "")).startswith("shadow_unit")
            edge_store.record(StrategyOutcome(
                strategy=str(rec.get("setup_class", "")),
                context_key=str(rec.get("context_key", "")),
                side=str(rec.get("side", "")),
                won=bool(outcome.get("won")),
                pnl_pct=float(outcome.get("pnl_pct", 0.0)),
                r_multiple=float(outcome.get("r_multiple", 0.0)),
                mfe_pct=float(outcome.get("mfe_pct", 0.0)),
                source=SOURCE_SHADOW if is_shadow else SOURCE_SUPPRESSED,
            ))

        counters = fresh_store.classify_pending(
            fetch_ohlc_since=fetch_ohlc_since, on_classified=_feed_edge
        )
        assert counters.get("WOULD_WIN", 0) == 1
        cell = edge_store.matrix()[
            "BREAKOUT_RETEST|OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL"
        ]
        assert cell["n"] == 1
        assert cell["n_suppressed"] == 1
        assert cell["n_emitted"] == 0
        assert cell["win_rate"] == 1.0


class TestShadowStrategyScannerPass:
    def _fake_scanner(self, candles_15m, funding=0.002):
        return SimpleNamespace(
            _resolve_candles=lambda candles, tf: candles.get(tf, {}),
            order_flow_store=SimpleNamespace(get_funding_rate=lambda s: funding),
            _shadow_last_stamp={},
            _get_btc_state_cached=lambda: {"b": 0.0},
        )

    def _ctx(self, candles_15m):
        return SimpleNamespace(
            candles={"15m": candles_15m},
            regime_result=SimpleNamespace(regime=SimpleNamespace(value="RANGING")),
            regime_context=SimpleNamespace(atr_percentile=50.0),
        )

    def _candles(self):
        n = 100
        closes = [100 + 0.1 * ((-1) ** i) for i in range(n)]
        return {
            "high": [c + 0.1 for c in closes],
            "low": [c - 0.1 for c in closes],
            "close": closes,
        }

    def test_stamps_shadow_unit_and_never_queues(self, fresh_store, monkeypatch):
        from src import runtime_tunables
        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        c15 = self._candles()
        fake = self._fake_scanner(c15)
        Scanner._evaluate_shadow_strategies(fake, "ETHUSDT", self._ctx(c15))
        recs = fresh_store.records()
        assert len(recs) >= 1  # funding-fade fires on the 0.002 extreme
        assert all(r["gate_name"].startswith("shadow_unit:") for r in recs)
        assert all(r["channel"] == "SHADOW" for r in recs)
        # No signal queue on the fake scanner — nothing to enqueue into, and
        # the pass must not have tried (no AttributeError raised = no path).

    def test_cooldown_bounds_ledger_growth(self, fresh_store, monkeypatch):
        from src import runtime_tunables
        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        c15 = self._candles()
        fake = self._fake_scanner(c15)
        ctx = self._ctx(c15)
        Scanner._evaluate_shadow_strategies(fake, "ETHUSDT", ctx)
        first = fresh_store.pending_count()
        Scanner._evaluate_shadow_strategies(fake, "ETHUSDT", ctx)
        assert fresh_store.pending_count() == first  # second pass cooled down

    def test_disabled_tunable_stamps_nothing(self, fresh_store, monkeypatch):
        from src import runtime_tunables
        monkeypatch.setattr(runtime_tunables, "get", lambda key: False)
        c15 = self._candles()
        fake = self._fake_scanner(c15)
        Scanner._evaluate_shadow_strategies(fake, "ETHUSDT", self._ctx(c15))
        assert fresh_store.pending_count() == 0
