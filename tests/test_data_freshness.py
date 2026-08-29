"""Known-stale timeframe guard — follow-up to #811.

#811 restored the 15m feed.  This covers the guard that makes the *next* freeze
impossible to score on unnoticed, and its two-flag shape: measurement always on,
withholding dark until owner sign-off.

Every store here is a real ``HistoricalDataStore`` written through
``update_candle`` (the same path the WS handler uses), so the freshness stamp
under test is the production one and not a shape invented by the test.
"""
from __future__ import annotations

import time

import pytest

from src import data_freshness as df


@pytest.fixture(autouse=True)
def _clean():
    df.reset()
    yield
    df.reset()


def _age(store, symbol, tf, seconds):
    """Backdate the store's own freshness stamp, leaving the candles alone."""
    store._last_kline_update_ts[symbol][tf] = time.time() - seconds


class TestKnownStale:
    def test_fresh_series_is_not_stale(self, numpy_seeded_store):
        store = numpy_seeded_store("BTCUSDT", ("15m",), n=60)
        assert df.known_stale_age(store, "BTCUSDT", "15m") is None

    def test_old_series_reports_its_age(self, numpy_seeded_store):
        store = numpy_seeded_store("BTCUSDT", ("15m",), n=60)
        _age(store, "BTCUSDT", "15m", 6 * 3600)
        age = df.known_stale_age(store, "BTCUSDT", "15m")
        assert age is not None and age > 5 * 3600

    def test_unknown_age_is_never_treated_as_stale(self, numpy_seeded_store):
        """A missing stamp (snapshot restore, fresh bucket) must not degrade
        geometry — that is a worse failure than the one being guarded."""
        store = numpy_seeded_store("BTCUSDT", ("15m",), n=60)
        store._last_kline_update_ts.pop("BTCUSDT", None)
        assert df.timeframe_age_seconds(store, "BTCUSDT", "15m") is None
        assert df.known_stale_age(store, "BTCUSDT", "15m") is None

    def test_a_store_that_cannot_answer_is_not_stale(self):
        class _Stub:
            pass

        assert df.known_stale_age(_Stub(), "BTCUSDT", "15m") is None


class TestDarkFirstShape:
    def test_measurement_runs_while_the_effect_is_off(
        self, numpy_seeded_store, monkeypatch
    ):
        """Default config: counters move, indicators are handed through
        untouched.  This is the state the change ships in."""
        import config as _cfg

        monkeypatch.setattr(_cfg, "STALE_TF_REFUSE_ENABLED", False)
        monkeypatch.setattr("src.runtime_tunables.get", lambda key: None)
        store = numpy_seeded_store("BTCUSDT", ("5m", "15m"), n=60)
        _age(store, "BTCUSDT", "15m", 6 * 3600)

        ind = {"5m": {"atr_last": 1.0}, "15m": {"atr_last": 2.0}}
        out = df.audit_indicators(store=store, symbol="BTCUSDT", indicators=ind)

        assert out == ind, "dark means measured, not applied"
        counts = df.snapshot()["counts"]
        assert counts["scoring:15m"] == 1
        assert "withheld:15m" not in counts

    def test_armed_withholds_only_the_stale_timeframe(
        self, numpy_seeded_store, monkeypatch
    ):
        import config as _cfg

        monkeypatch.setattr(_cfg, "STALE_TF_REFUSE_ENABLED", True)
        monkeypatch.setattr("src.runtime_tunables.get", lambda key: None)
        store = numpy_seeded_store("BTCUSDT", ("5m", "15m"), n=60)
        _age(store, "BTCUSDT", "15m", 6 * 3600)

        ind = {"5m": {"atr_last": 1.0}, "15m": {"atr_last": 2.0}}
        out = df.audit_indicators(store=store, symbol="BTCUSDT", indicators=ind)

        assert "15m" not in out
        assert out["5m"] == {"atr_last": 1.0}, "a fresh timeframe must survive"
        assert df.snapshot()["counts"]["withheld:15m"] == 1

    def test_fresh_data_is_never_touched_even_when_armed(
        self, numpy_seeded_store, monkeypatch
    ):
        import config as _cfg

        monkeypatch.setattr(_cfg, "STALE_TF_REFUSE_ENABLED", True)
        monkeypatch.setattr("src.runtime_tunables.get", lambda key: None)
        store = numpy_seeded_store("BTCUSDT", ("5m", "15m"), n=60)

        ind = {"5m": {"atr_last": 1.0}, "15m": {"atr_last": 2.0}}
        out = df.audit_indicators(store=store, symbol="BTCUSDT", indicators=ind)
        assert out == ind
        assert df.snapshot()["counts"] == {}

    def test_gate_counts_dark_and_skips_only_when_armed(
        self, numpy_seeded_store, monkeypatch
    ):
        import config as _cfg

        monkeypatch.setattr("src.runtime_tunables.get", lambda key: None)
        store = numpy_seeded_store("BTCUSDT", ("15m",), n=60)
        _age(store, "BTCUSDT", "15m", 6 * 3600)

        monkeypatch.setattr(_cfg, "STALE_TF_REFUSE_ENABLED", False)
        assert df.gate_should_skip(store, "BTCUSDT", "15m", "regime_kill") is False
        monkeypatch.setattr(_cfg, "STALE_TF_REFUSE_ENABLED", True)
        assert df.gate_should_skip(store, "BTCUSDT", "15m", "regime_kill") is True
        assert df.snapshot()["counts"]["gate:regime_kill"] == 2, "both are measured"


class TestConsumerFallbacksExist:
    """Withholding is only honest because every consumer already has a written
    fallback for *absent* 15m.  These pin the ones the guard relies on, driven
    through the real functions rather than asserted in prose."""

    def test_pre_tp_threshold_falls_back_to_static_without_atr(self):
        from src.pre_tp_stamping import resolve_pre_tp_threshold

        _, source = resolve_pre_tp_threshold(100.0, None)
        assert source == "static"
        _, source_zero = resolve_pre_tp_threshold(100.0, 0.0)
        assert source_zero == "static"


class TestScannerWiring:
    """The module must actually be called from the scan path.

    A guard nobody invokes is a scaffold, and unit tests over the module alone
    cannot tell the two apart — so this drives the real ``_build_scan_context``
    and asserts against the real counters.  Deleting the hook fails this.
    """

    async def test_scan_context_measures_a_stale_timeframe(self, monkeypatch):
        from types import SimpleNamespace
        from unittest.mock import MagicMock

        import config as _cfg
        from tests.test_scanner import _make_candles_dict, _make_scanner

        monkeypatch.setattr(_cfg, "STALE_TF_REFUSE_ENABLED", False)
        monkeypatch.setattr("src.runtime_tunables.get", lambda key: None)

        scanner = _make_scanner()
        candles = _make_candles_dict()
        scanner.data_store.get_candles.side_effect = lambda sym, tf: candles.get(tf)
        scanner.data_store.ticks = {"BTCUSDT": []}
        # Same contract as HistoricalDataStore.last_kline_age_seconds
        # (float | None) — pinned against the real store in TestKnownStale.
        scanner.data_store.last_kline_age_seconds = lambda sym, tf: (
            6 * 3600.0 if tf == "15m" else 30.0
        )
        scanner.order_flow_store = MagicMock()
        scanner._compute_indicators = lambda cd: {tf: {"rsi_last": 50.0} for tf in cd}
        scanner.smc_detector = MagicMock()
        scanner.smc_detector.detect.return_value = SimpleNamespace(
            as_dict=lambda: {"sweeps": [], "fvg": [], "orderblocks": [], "recent_ticks": []},
            sweeps=[], fvg=[], orderblocks=[], recent_ticks=[], whale_alert=None,
            volume_delta_spike=None, mss=None, oi_invalidated=False,
            cvd_divergence=False, cvd_divergence_age=None, cvd_divergence_strength=None,
        )

        ctx = await scanner._build_scan_context("BTCUSDT", 1e9)

        assert ctx is not None, "measurement must never break the scan path"
        counts = df.snapshot()["counts"]
        assert counts.get("scoring:15m") == 1, (
            "the scan path did not consult the staleness guard"
        )
        # Dark: the stale timeframe still reached the evaluators this cycle.
        assert "15m" in ctx.indicators
        assert "withheld:15m" not in counts


class TestLivenessProbe:
    def test_probe_is_quiet_when_idle_and_speaks_when_stale(
        self, tmp_path, monkeypatch, numpy_seeded_store
    ):
        """The probe must report idle as OK — never raise to mean 'nothing
        happened', which would fill the fail_open counter with non-failures."""
        import time as _time
        from types import SimpleNamespace

        import config as _cfg
        from src import feature_liveness as fl_mod
        from src import runtime_tunables
        from src.main import CryptoSignalEngine

        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        monkeypatch.setattr(
            fl_mod, "_DEFAULT_PATH", str(tmp_path / "feature_liveness.json")
        )
        monkeypatch.setattr(_cfg, "FEATURE_LIVENESS_BOOT_GRACE_SEC", 0.0)
        store = numpy_seeded_store("BTCUSDT", ("5m", "15m"), n=120)
        stub = SimpleNamespace(
            _scanner=SimpleNamespace(_scan_cycle_count=10, _shadow_last_stamp={}),
            pair_mgr=SimpleNamespace(pairs={"BTCUSDT": object()}),
            data_store=store,
            _last_market_context_publish_ts=_time.time(),
            _last_atr_percentile=55.0,
        )
        fl = CryptoSignalEngine._build_feature_liveness(stub)
        payload = fl.run_cycle()
        assert payload["features"]["stale_tf_scoring"]["status"] == "ok"

        # A sustained condition means NEW stale scoring on each probe interval;
        # one historical event must not latch the process red forever.
        _age(store, "BTCUSDT", "15m", 6 * 3600)
        for _ in range(7):
            df.audit_indicators(
                store=store,
                symbol="BTCUSDT",
                indicators={"15m": {"atr_last": 2.0}},
            )
            payload = fl.run_cycle()
        feature = payload["features"]["stale_tf_scoring"]
        assert feature["status"] == "violating"
        assert "new stale-TF events: scored 1x" in feature["detail"]
        assert "stale_tf_scoring" in [a["feature"] for a in payload["alerts"]]

        # Once no new event arrives, the current condition has recovered. The
        # lifetime total remains in detail for incident history.
        payload = fl.run_cycle()
        feature = payload["features"]["stale_tf_scoring"]
        assert feature["status"] == "ok"
        assert "lifetime scored=7" in feature["detail"]
