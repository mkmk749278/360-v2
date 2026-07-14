"""Feature-liveness watchdog + fail-open telemetry (2026-07-14 incident response).

Covers the three layers shipped in response to "8 features dead silently":

1. ``src.fail_open`` — counting, rate-limited WARNs, snapshot contract.
2. ``src.feature_liveness`` — rate/predicate probe math (upstream gating,
   streak discipline, boot grace, tunable-off → unknown), manifest write.
3. ``scripts/monitor_heartbeat.check_feature_liveness`` — manifest →
   INVARIANT_WARN lines (the F-09 pager wiring).

Plus the INCIDENT REPLAY: suppression stamps flowing while geometry stamping
is broken (the exact pre-#726 production state) must produce a geometry_ab
alert after the sustained-streak window and an INVARIANT_WARN from the
monitor — end-to-end proof this incident would have paged.
"""
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

import pytest

from src import fail_open
from src.feature_liveness import FeatureLiveness, PredicateProbe, RateProbe


@pytest.fixture(autouse=True)
def _clean_fail_open():
    fail_open.reset()
    yield
    fail_open.reset()


# ---------------------------------------------------------------------------
# Layer 1 — fail_open
# ---------------------------------------------------------------------------


class TestFailOpen:
    def test_counts_and_snapshot(self):
        fail_open.record("site.a", ValueError("boom"))
        fail_open.record("site.a", ValueError("boom2"))
        fail_open.record("site.b", KeyError("x"))
        snap = fail_open.snapshot()
        assert snap["site.a"]["count"] == 2
        assert "boom2" in str(snap["site.a"]["last_error"])
        assert snap["site.b"]["count"] == 1

    def test_never_raises_even_on_weird_input(self):
        class _Evil(Exception):
            def __str__(self):  # noqa: D105
                raise RuntimeError("str() bomb")

        fail_open.record("site.evil", _Evil())  # must not propagate
        assert fail_open.snapshot()["site.evil"]["count"] == 1

    def test_log_rate_limited_but_every_occurrence_counted(self):
        t0 = 1_000_000.0
        for i in range(50):
            fail_open.record("site.hot", ValueError(str(i)), now=t0 + i)
        assert fail_open.snapshot()["site.hot"]["count"] == 50


# ---------------------------------------------------------------------------
# Layer 2 — probe math
# ---------------------------------------------------------------------------


class _Counter:
    def __init__(self, v: float = 0.0):
        self.v = v

    def __call__(self):
        return self.v


def _fl(tmp_path, boot_grace=0.0, clock=None):
    return FeatureLiveness(
        path=str(tmp_path / "feature_liveness.json"),
        boot_grace_sec=boot_grace,
        now=clock,
    )


class TestRateProbe:
    def test_violates_only_when_upstream_flows_and_output_flat(self, tmp_path):
        out, up = _Counter(0.0), _Counter(0.0)
        fl = _fl(tmp_path)
        probe = RateProbe(
            name="geometry_ab", counter=out, upstream=up,
            min_upstream_delta=10.0, min_streak=2,
        )
        fl.add_rate(probe)

        fl.run_cycle()                       # first cycle: baseline only
        up.v += 5                            # below min_upstream_delta
        payload = fl.run_cycle()
        assert payload["features"]["geometry_ab"]["status"] == "ok"

        up.v += 50                           # upstream flows, output flat
        payload = fl.run_cycle()
        assert payload["features"]["geometry_ab"]["status"] == "violating"
        assert payload["alerts"] == []       # streak 1 < min_streak 2

        up.v += 50
        payload = fl.run_cycle()
        assert [a["feature"] for a in payload["alerts"]] == ["geometry_ab"]

        up.v += 50
        out.v += 1                           # output resumes → recovery
        payload = fl.run_cycle()
        assert payload["features"]["geometry_ab"]["status"] == "ok"
        assert payload["alerts"] == []

    def test_quiet_market_never_alerts(self, tmp_path):
        out, up = _Counter(0.0), _Counter(0.0)
        fl = _fl(tmp_path)
        fl.add_rate(RateProbe(
            name="x", counter=out, upstream=up,
            min_upstream_delta=10.0, min_streak=1,
        ))
        fl.run_cycle()
        for _ in range(10):                  # nothing flows anywhere
            payload = fl.run_cycle()
            assert payload["alerts"] == []

    def test_tunable_off_reports_unknown_not_violation(self, tmp_path):
        up = _Counter(0.0)
        fl = _fl(tmp_path)
        fl.add_rate(RateProbe(
            name="x", counter=lambda: None, upstream=up,
            min_upstream_delta=1.0, min_streak=1,
        ))
        fl.run_cycle()
        up.v += 100
        payload = fl.run_cycle()
        assert payload["features"]["x"]["status"] == "unknown"
        assert payload["alerts"] == []

    def test_counter_reset_clears_streak(self, tmp_path):
        out, up = _Counter(0.0), _Counter(0.0)
        fl = _fl(tmp_path)
        probe = RateProbe(
            name="x", counter=out, upstream=up,
            min_upstream_delta=1.0, min_streak=1,
        )
        fl.add_rate(probe)
        fl.run_cycle()
        up.v += 10
        fl.run_cycle()
        assert probe.streak == 1
        up.v = 0.0                           # engine-side restart of upstream
        payload = fl.run_cycle()
        assert payload["features"]["x"]["status"] == "ok"
        assert probe.streak == 0


class TestPredicateAndGrace:
    def test_predicate_streak_and_recovery(self, tmp_path):
        ok = {"v": False}
        fl = _fl(tmp_path)
        fl.add_predicate(PredicateProbe(
            name="market_context",
            fn=lambda: (ok["v"], "atr_percentile None"),
            min_streak=2,
        ))
        assert fl.run_cycle()["alerts"] == []
        payload = fl.run_cycle()
        assert [a["feature"] for a in payload["alerts"]] == ["market_context"]
        ok["v"] = True
        assert fl.run_cycle()["alerts"] == []

    def test_boot_grace_suppresses_everything(self, tmp_path):
        clock = {"t": 1000.0}
        fl = _fl(tmp_path, boot_grace=3600.0, clock=lambda: clock["t"])
        fl.add_predicate(PredicateProbe(
            name="x", fn=lambda: (False, "broken"), min_streak=1,
        ))
        for _ in range(5):
            clock["t"] += 300
            payload = fl.run_cycle()
            assert payload["alerts"] == []
            assert payload["boot_grace_active"] is True
        clock["t"] += 3600                   # grace over → alerts arm
        payload = fl.run_cycle()
        assert payload["boot_grace_active"] is False
        assert [a["feature"] for a in payload["alerts"]] == ["x"]

    def test_probe_exception_is_unknown_and_counted(self, tmp_path):
        fl = _fl(tmp_path)
        fl.add_predicate(PredicateProbe(
            name="x", fn=lambda: (_ for _ in ()).throw(RuntimeError("dead")),
            min_streak=1,
        ))
        payload = fl.run_cycle()
        assert payload["features"]["x"]["status"] == "unknown"
        assert fail_open.snapshot()["feature_liveness.probe.x"]["count"] == 1


class TestFailOpenAlerting:
    def test_burst_alerts_immediately(self, tmp_path):
        fl = _fl(tmp_path)
        fl.run_cycle()
        for i in range(25):                  # geometry-A/B signature: hot loop
            fail_open.record("scanner.stamp_geometry_ab", ValueError(str(i)))
        payload = fl.run_cycle()
        assert any(
            a["feature"] == "fail_open:scanner.stamp_geometry_ab"
            for a in payload["alerts"]
        )

    def test_slow_drip_alerts_on_streak(self, tmp_path):
        fl = _fl(tmp_path)
        fl.run_cycle()
        alerted = False
        for cycle in range(4):
            fail_open.record("site.drip", ValueError("x"))
            payload = fl.run_cycle()
            names = [a["feature"] for a in payload["alerts"]]
            if cycle < 2:
                assert "fail_open:site.drip" not in names
            alerted = alerted or "fail_open:site.drip" in names
        assert alerted

    def test_single_transient_never_alerts(self, tmp_path):
        fl = _fl(tmp_path)
        fl.run_cycle()
        fail_open.record("site.once", ValueError("x"))
        assert fl.run_cycle()["alerts"] == []
        assert fl.run_cycle()["alerts"] == []


class TestManifest:
    def test_atomic_write_round_trip(self, tmp_path):
        fl = _fl(tmp_path)
        fl.add_predicate(PredicateProbe(name="x", fn=lambda: (True, "fine")))
        fl.run_cycle()
        data = json.loads((tmp_path / "feature_liveness.json").read_text())
        assert data["features"]["x"]["status"] == "ok"
        assert "generated_at" in data and "fail_open" in data


# ---------------------------------------------------------------------------
# Layer 3 — monitor_heartbeat wiring
# ---------------------------------------------------------------------------


def _run_heartbeat_check(tmp_path, capsys, manifest: dict | None, mtime_ago: float = 0.0):
    if manifest is not None:
        p = tmp_path / "feature_liveness.json"
        p.write_text(json.dumps(manifest))
    # Keep the heartbeat file fresh so manifest-staleness attributes correctly.
    hb = tmp_path / "scanner_heartbeat"
    hb.write_text("x")
    os.environ["ENGINE_DATA_DIR"] = str(tmp_path)
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
    try:
        import monitor_heartbeat  # noqa: PLC0415 — module runs checks on import
        importlib.reload(monitor_heartbeat)
        capsys.readouterr()                  # drop import-time output
        monitor_heartbeat.DATA_DIR = str(tmp_path)
        monitor_heartbeat.check_feature_liveness()
        return capsys.readouterr().out
    finally:
        os.environ.pop("ENGINE_DATA_DIR", None)


class TestMonitorHeartbeatCheck:
    def test_alert_becomes_invariant_warn(self, tmp_path, capsys):
        import time as _t
        out = _run_heartbeat_check(tmp_path, capsys, {
            "generated_at": _t.time(),
            "features": {"geometry_ab": {"status": "violating", "detail": "d", "streak": 6}},
            "alerts": [{"feature": "geometry_ab", "detail": "upstream +120 but output +0", "streak": 6}],
            "fail_open": {},
        })
        assert "INVARIANT_WARN: feature_liveness geometry_ab" in out

    def test_healthy_manifest_is_quiet(self, tmp_path, capsys):
        import time as _t
        out = _run_heartbeat_check(tmp_path, capsys, {
            "generated_at": _t.time(),
            "features": {"geometry_ab": {"status": "ok", "detail": "", "streak": 0}},
            "alerts": [],
            "fail_open": {},
        })
        assert "INVARIANT_WARN" not in out
        assert "OK:" in out

    def test_stale_manifest_with_fresh_engine_pages(self, tmp_path, capsys):
        out = _run_heartbeat_check(tmp_path, capsys, {
            "generated_at": 1000.0,          # ancient
            "features": {}, "alerts": [], "fail_open": {},
        })
        assert "INVARIANT_WARN: feature-liveness manifest is stale" in out

    def test_missing_file_skips_quietly(self, tmp_path, capsys):
        out = _run_heartbeat_check(tmp_path, capsys, None)
        assert "INVARIANT_WARN" not in out
        assert "check skipped" in out


# ---------------------------------------------------------------------------
# THE INCIDENT REPLAY — would 2026-07-14 have paged?
# ---------------------------------------------------------------------------


class TestIncidentReplay:
    def test_dead_geometry_stamping_pages_end_to_end(self, tmp_path, capsys):
        """Pre-#726 production state: every suppression stamps the audit
        ledger, geometry stamping raises numpy-truthiness and fail-opens.
        The watchdog must (a) alert on the geometry_ab flat-line, (b) alert
        on the fail-open burst, and (c) the monitor must page on both."""
        from src import suppression_audit as sa
        from src.suppression_audit import SuppressedCandidateStore

        store = SuppressedCandidateStore(persist_path="")
        fl = _fl(tmp_path)
        geometry = _Counter(0.0)             # stamping is broken: stays 0
        fl.add_rate(RateProbe(
            name="geometry_ab",
            counter=geometry,
            upstream=lambda: float(store.stamped_total),
            min_upstream_delta=10.0,
            min_streak=6,
        ))

        def _one_cycle():
            # ~15 suppressions land per 5-min window (the real 2026-07-13
            # rate), and each one's geometry stamp raises like production did.
            for i in range(15):
                sa.stamp_candidate(
                    gate_name="dispatch_staleness", symbol=f"S{i}USDT",
                    channel="360_SCALP", setup_class="SR_FLIP_RETEST",
                    side="LONG", entry=100.0, stop_loss=99.0, tp1=101.5,
                    store=store,
                )
                fail_open.record(
                    "scanner.stamp_geometry_ab",
                    ValueError("The truth value of an array with more than "
                               "one element is ambiguous."),
                )
            return fl.run_cycle()

        payload = _one_cycle()               # baseline cycle
        for _ in range(6):                   # 30 minutes of production
            payload = _one_cycle()

        alert_names = [a["feature"] for a in payload["alerts"]]
        assert "geometry_ab" in alert_names, "flat-line probe must fire"
        assert "fail_open:scanner.stamp_geometry_ab" in alert_names, (
            "the swallowed ValueError itself must alert"
        )

        # And the monitor turns the manifest into pages:
        out = _run_heartbeat_check(
            tmp_path, capsys, json.loads(
                (tmp_path / "feature_liveness.json").read_text()
            ) | {"generated_at": __import__("time").time()},
        )
        assert "INVARIANT_WARN: feature_liveness geometry_ab" in out
        assert "INVARIANT_WARN: feature_liveness fail_open:scanner.stamp_geometry_ab" in out


# ---------------------------------------------------------------------------
# Engine wiring + truth-report section
# ---------------------------------------------------------------------------


class TestEngineWiring:
    def test_build_feature_liveness_probes_run_on_real_stores(
        self, tmp_path, monkeypatch, numpy_seeded_store
    ):
        """The engine's probe registration must produce a runnable registry
        against real store objects (numpy shape) without any exceptions."""
        from types import SimpleNamespace

        from src import feature_liveness as fl_mod
        from src import runtime_tunables
        from src.main import CryptoSignalEngine

        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        monkeypatch.setattr(
            fl_mod, "_DEFAULT_PATH", str(tmp_path / "feature_liveness.json")
        )
        store = numpy_seeded_store("BTCUSDT", ("5m", "15m"), n=40)
        stub = SimpleNamespace(
            _scanner=SimpleNamespace(_scan_cycle_count=10, _shadow_last_stamp={}),
            pair_mgr=SimpleNamespace(pairs={"BTCUSDT": object()}),
            data_store=store,
            _last_market_context_publish_ts=__import__("time").time(),
            _last_atr_percentile=55.0,
        )
        fl = CryptoSignalEngine._build_feature_liveness(stub)
        payload = fl.run_cycle()
        # Every registered probe must resolve — no "probe read failed".
        for name, f in payload["features"].items():
            assert "probe read failed" not in str(f.get("detail")), (name, f)
        assert {"geometry_ab", "suppression_audit", "strategy_edge",
                "market_context", "shadow_units", "candle_coverage",
                "btc_reference"} <= set(payload["features"])
        # Healthy stub state on cycle one → nothing alerting.
        assert payload["alerts"] == []


class TestTruthReportSection:
    def test_markdown_renders_manifest_and_alerts(self):
        from src.runtime_truth_report import format_truth_report_markdown

        snapshot = {
            "feature_liveness": {
                "boot_grace_active": False,
                "features": {
                    "geometry_ab": {"status": "violating", "detail": "upstream +120 but output +0", "streak": 6},
                    "btc_reference": {"status": "ok", "detail": "BTC ref 100.00", "streak": 0},
                },
                "alerts": [{"feature": "geometry_ab", "detail": "upstream +120 but output +0", "streak": 6}],
                "fail_open": {
                    "scanner.stamp_geometry_ab": {"count": 90, "last_error": "ValueError: truth value", "last_ts": 0.0},
                },
            },
        }
        md = format_truth_report_markdown(snapshot, {})
        assert "## Feature Liveness & Fail-Open Telemetry" in md
        assert "**ALERT** `geometry_ab`" in md
        assert "scanner.stamp_geometry_ab" in md

    def test_markdown_renders_cold(self):
        from src.runtime_truth_report import format_truth_report_markdown

        md = format_truth_report_markdown({}, {})
        assert "## Feature Liveness & Fail-Open Telemetry" in md
        assert "no liveness manifest" in md
