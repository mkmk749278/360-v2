"""Scanner wiring for the dispatch-gate shadow arms (2026-07-23).

Covers the two dark-first attacks on the audited-negative dispatch gates:

* **@DSV2** — staleness V2 disagreement arms: V1 blocks, V2 would pass →
  rescue stamped into the geometry variants ledger with entry re-anchored at
  the dispatch-time price; V1 keeps deciding while ``DISPATCH_STALENESS_V2_LIVE``
  is dark, and decides no longer once it is live.
* **@GOV** — STRONG-cell gate override (W5): a measured-STRONG candidate
  blocked by ``dispatch_staleness`` / ``level_still_in_play`` is shadow-stamped
  (dark) or actually emitted (``gate_override_live``).
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import config
from src import staleness_v2 as _sv2
from src.channels.base import Direction, Signal
from src.context_emission_policy import GateOverrideDecision
from src.scanner import Scanner
from src.suppression_audit import SuppressedCandidateStore

# Captured at import time — the autouse conftest fixture replaces these per-test
# (Scanner._is_entry_fresh -> always-fresh V1, staleness_v2.evaluate ->
# always-fresh V2 stub), so these are the only handles on the real
# implementations. gate_env restores both to exercise the real gates.
_REAL_IS_ENTRY_FRESH = Scanner._is_entry_fresh
_REAL_STALENESS_V2_EVALUATE = _sv2.evaluate


def _make_scanner() -> Scanner:
    queue = MagicMock()

    async def _put(sig):
        return True

    queue.put = _put

    data_store = MagicMock()
    data_store.candles = {}

    return Scanner(
        pair_mgr=MagicMock(),
        data_store=data_store,
        channels=[],
        smc_detector=MagicMock(),
        regime_detector=MagicMock(),
        predictive=MagicMock(),
        exchange_mgr=MagicMock(),
        spot_client=None,
        telemetry=MagicMock(),
        signal_queue=queue,
        router=MagicMock(active_signals={}),
    )


def _make_signal(*, entry=100.0, stop_loss=98.0, tp1=103.0) -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol="BTCUSDT",
        direction=Direction.LONG,
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=tp1 + 1.0,
        confidence=70.0,
        setup_class="MEAN_REVERT",
    )
    sig.mc_context_key = "OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL"
    return sig


@pytest.fixture()
def gate_env(monkeypatch):
    """Real staleness gate + isolated geometry store, both rescue flags dark.

    These tests exercise the shadow path (measurement ON, live application
    OFF: V1 keeps deciding while X@DSV2 / X@GOV disagreements get stamped).
    The shipped config default is now LIVE, and the runtime-tunables registry
    snapshots its bool defaults from ``config`` at build time — so a config
    monkeypatch alone never reaches the read site (StalenessV2Params /
    PolicyParams resolve the flag via ``runtime_tunables.get`` → registry
    default, exactly what the ``_v2_live`` helper below documents). Patch
    ``config`` *and* rebuild the registry so the dark values actually take
    effect; reset again on teardown so later tests see the shipped defaults.
    """
    from src import geometry_ab as gab
    from src import runtime_tunables as rt

    monkeypatch.setattr(Scanner, "_is_entry_fresh", _REAL_IS_ENTRY_FRESH)
    monkeypatch.setattr(_sv2, "evaluate", _REAL_STALENESS_V2_EVALUATE)
    store = SuppressedCandidateStore(persist_path="")
    monkeypatch.setattr(gab, "get_geometry_store", lambda: store)
    monkeypatch.setattr(config, "DISPATCH_STALENESS_V2_ENABLED", True, raising=False)
    monkeypatch.setattr(config, "DISPATCH_STALENESS_V2_LIVE", False, raising=False)
    monkeypatch.setattr(config, "CONTEXT_EMISSION_GATE_OVERRIDE_ENABLED", True, raising=False)
    monkeypatch.setattr(config, "CONTEXT_EMISSION_GATE_OVERRIDE_LIVE", False, raising=False)
    rt.reset_for_test()  # rebuild the registry against the dark config above
    yield store
    rt.reset_for_test()  # restore the shipped (live) defaults for later tests


def _seed_price(scanner: Scanner, price: float) -> None:
    scanner.data_store.candles = {"BTCUSDT": {"1m": {"close": [price]}}}


def _block_gate_override(monkeypatch) -> None:
    """Make the W5 override ineligible so DSV2 tests see only the V1/V2 path."""
    from src import context_emission_policy as cep

    monkeypatch.setattr(
        cep, "gate_override",
        lambda *a, **k: GateOverrideDecision(False, "FLAT", None, 0, "", "not_strong"),
    )


class TestStalenessV2Shadow:
    @pytest.mark.asyncio
    async def test_v1_block_v2_pass_stamps_dsv2_rescue(self, monkeypatch, gate_env):
        _block_gate_override(monkeypatch)
        scanner = _make_scanner()
        # Drift 0.6% (V1 kills at 0.5%) but only 30% of the 2.0 stop distance
        # (V2 budget 40%): the exact disagreement class the audit measured.
        _seed_price(scanner, 99.4)
        ok = await scanner._enqueue_signal(_make_signal())
        assert ok is False  # V1 still decides while V2 is dark
        recs = gate_env.records()
        assert len(recs) == 1
        rec = recs[0]
        assert rec["setup_class"] == "MEAN_REVERT@DSV2"
        assert rec["gate_name"] == "dsv2_rescue"
        # Entry re-anchored at dispatch-time price, original SL/TP1 kept.
        assert rec["entry"] == pytest.approx(99.4)
        assert rec["stop_loss"] == pytest.approx(98.0)
        assert rec["tp1"] == pytest.approx(103.0)
        assert scanner._suppression_counters["dsv2:rescue:MEAN_REVERT"] == 1
        assert scanner._suppression_counters["dsv2:evaluated"] == 1

    @pytest.mark.asyncio
    async def test_v1_and_v2_agree_block_no_rescue_arm(self, monkeypatch, gate_env):
        _block_gate_override(monkeypatch)
        scanner = _make_scanner()
        # Price at 99.0 = 50% of stop room consumed: both V1 and V2 block.
        _seed_price(scanner, 99.0)
        ok = await scanner._enqueue_signal(_make_signal())
        assert ok is False
        assert gate_env.records() == []
        assert scanner._suppression_counters["dsv2:rescue:MEAN_REVERT"] == 0

    @pytest.mark.asyncio
    async def test_fresh_price_passes_both(self, monkeypatch, gate_env):
        _block_gate_override(monkeypatch)
        scanner = _make_scanner()
        _seed_price(scanner, 100.1)
        ok = await scanner._enqueue_signal(_make_signal())
        assert ok is True
        assert gate_env.records() == []

    @staticmethod
    def _v2_live(monkeypatch) -> None:
        # The tunables registry (built at import in the test env) outranks a
        # config monkeypatch — pin the params object itself.
        from src import staleness_v2 as sv2

        live = sv2.StalenessV2Params(
            enabled=True, live=True, toward_sl_max_frac=0.40, toward_tp_max_frac=0.35
        )
        monkeypatch.setattr(
            sv2.StalenessV2Params, "from_config", staticmethod(lambda: live)
        )

    @pytest.mark.asyncio
    async def test_v2_live_lets_the_rescue_class_emit(self, monkeypatch, gate_env):
        _block_gate_override(monkeypatch)
        self._v2_live(monkeypatch)
        scanner = _make_scanner()
        _seed_price(scanner, 99.4)  # V1 would kill; V2 passes
        ok = await scanner._enqueue_signal(_make_signal())
        assert ok is True
        assert gate_env.records() == []  # emitted live — nothing to shadow

    @pytest.mark.asyncio
    async def test_v2_live_still_blocks_true_staleness(self, monkeypatch, gate_env):
        _block_gate_override(monkeypatch)
        self._v2_live(monkeypatch)
        scanner = _make_scanner()
        _seed_price(scanner, 98.2)  # 90% of stop room consumed — stale by any honest gate
        ok = await scanner._enqueue_signal(_make_signal())
        assert ok is False
        assert scanner._suppression_counters["dispatch_staleness_v2:MEAN_REVERT"] == 1


class TestGateOverrideShadow:
    def _force_strong_cell(self, monkeypatch) -> None:
        from src import context_emission_policy as cep

        monkeypatch.setattr(
            cep, "gate_override",
            lambda *a, **k: GateOverrideDecision(
                True, "STRONG", 0.8, 40, "MEAN_REVERT", "strong_override"
            ),
        )

    @pytest.mark.asyncio
    async def test_level_block_strong_cell_stamps_gov_dark(self, monkeypatch, gate_env):
        self._force_strong_cell(monkeypatch)
        monkeypatch.setattr(Scanner, "_is_level_in_play", lambda self, sig: True)
        scanner = _make_scanner()
        _seed_price(scanner, 100.1)  # staleness gates pass
        ok = await scanner._enqueue_signal(_make_signal())
        assert ok is False  # dark: the gate still blocks
        recs = gate_env.records()
        assert len(recs) == 1
        assert recs[0]["setup_class"] == "MEAN_REVERT@GOV"
        assert recs[0]["gate_name"] == "gov_rescue:level_still_in_play"
        assert scanner._suppression_counters[
            "gov:rescue:level_still_in_play:MEAN_REVERT"
        ] == 1

    @pytest.mark.asyncio
    async def test_gate_override_live_emits_through_level_block(self, monkeypatch, gate_env):
        self._force_strong_cell(monkeypatch)
        from src import context_emission_policy as cep

        live = cep.PolicyParams(
            enabled=True, live=True, quality_anchor=60.0, strong_relax=5.0,
            positive_relax=3.0, min_samples=30, suppress_negative=True,
            gate_override_enabled=True, gate_override_live=True,
        )
        monkeypatch.setattr(cep.PolicyParams, "from_config", staticmethod(lambda: live))
        monkeypatch.setattr(Scanner, "_is_level_in_play", lambda self, sig: True)
        scanner = _make_scanner()
        _seed_price(scanner, 100.1)
        ok = await scanner._enqueue_signal(_make_signal())
        assert ok is True
        assert scanner._suppression_counters[
            "gov:applied:level_still_in_play:MEAN_REVERT"
        ] == 1

    @pytest.mark.asyncio
    async def test_staleness_block_strong_cell_stamps_gov_dark(self, monkeypatch, gate_env):
        self._force_strong_cell(monkeypatch)
        scanner = _make_scanner()
        _seed_price(scanner, 99.0)  # both V1 and V2 block
        ok = await scanner._enqueue_signal(_make_signal())
        assert ok is False
        gates = [r["gate_name"] for r in gate_env.records()]
        assert "gov_rescue:dispatch_staleness" in gates

    @pytest.mark.asyncio
    async def test_non_strong_cell_never_rescued(self, monkeypatch, gate_env):
        _block_gate_override(monkeypatch)
        monkeypatch.setattr(Scanner, "_is_level_in_play", lambda self, sig: True)
        scanner = _make_scanner()
        _seed_price(scanner, 100.1)
        ok = await scanner._enqueue_signal(_make_signal())
        assert ok is False
        assert gate_env.records() == []
