"""scripts/watchdog.py — the on-box autonomous supervisor.

Checks are pure functions over snapshots/tmpdirs, so no Docker daemon or
network is needed. Action paths (restart / kill switch) are exercised with
the actuators monkeypatched — the assertions are about the *decision
ladder*: budgets, escalation, dedupe, and the risk-reducing-only doctrine.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

import watchdog  # noqa: E402


def _redirect_state_files(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(watchdog, "STATE_PATH", str(tmp_path / "watchdog_state.json"))
    monkeypatch.setattr(watchdog, "AUDIT_PATH", str(tmp_path / "watchdog_audit.jsonl"))


class TestContainerChecks:
    def test_all_healthy_is_quiet(self):
        states = {
            "engine": {"running": True, "status": "running", "health": "healthy", "restart_count": 0},
        }
        assert watchdog.check_containers(states) == []

    def test_down_container_is_critical(self):
        states = {
            "engine": {"running": False, "status": "exited", "health": "unknown", "restart_count": 4},
        }
        findings = watchdog.check_containers(states)
        assert len(findings) == 1
        assert findings[0].severity == "critical"
        assert findings[0].key == "container_down:engine"

    def test_unhealthy_container_warns(self):
        states = {
            "redis": {"running": True, "status": "running", "health": "unhealthy", "restart_count": 0},
        }
        findings = watchdog.check_containers(states)
        assert findings[0].key == "container_unhealthy:redis"


class TestHeartbeatCheck:
    def test_fresh_heartbeat_quiet(self, tmp_path):
        (tmp_path / "scanner_heartbeat").write_text(str(time.time()))
        assert watchdog.check_scanner_heartbeat(data_dir=str(tmp_path)) == []

    def test_missing_heartbeat_quiet(self, tmp_path):
        # Pre-first-cycle window belongs to the container healthcheck.
        assert watchdog.check_scanner_heartbeat(data_dir=str(tmp_path)) == []

    def test_stale_heartbeat_pages(self, tmp_path):
        import os

        p = tmp_path / "scanner_heartbeat"
        p.write_text("x")
        old = time.time() - 2000
        os.utime(p, (old, old))
        findings = watchdog.check_scanner_heartbeat(data_dir=str(tmp_path), stale_sec=900)
        assert [f.key for f in findings] == ["scanner_heartbeat_stale"]
        assert findings[0].severity == "critical"


class TestPricingFreshnessCheck:
    @staticmethod
    def _snap(tmp_path: Path, positions, age=5.0):
        (tmp_path / "pricing_freshness.json").write_text(
            json.dumps({"updated_at": time.time() - age, "positions": positions})
        )

    def test_missing_file_quiet(self, tmp_path):
        assert watchdog.check_pricing_freshness(data_dir=str(tmp_path)) == []

    def test_blind_position_critical(self, tmp_path):
        self._snap(
            tmp_path,
            [{"signal_id": "s1", "symbol": "MVLLUSDT", "status": "TP1_HIT",
              "kline_age_sec": 40000, "blind": True}],
        )
        findings = watchdog.check_pricing_freshness(data_dir=str(tmp_path))
        assert [f.key for f in findings] == ["blind_position:s1"]
        assert findings[0].severity == "critical"

    def test_healthy_positions_quiet(self, tmp_path):
        self._snap(tmp_path, [{"signal_id": "s1", "symbol": "BTCUSDT", "blind": False}])
        assert watchdog.check_pricing_freshness(data_dir=str(tmp_path)) == []

    def test_frozen_publisher_is_its_own_page(self, tmp_path):
        self._snap(tmp_path, [], age=4000)
        findings = watchdog.check_pricing_freshness(data_dir=str(tmp_path), file_max_age_sec=600)
        assert [f.key for f in findings] == ["pricing_freshness_stale_file"]


class TestBreakerCheck:
    def test_tripped_pages_with_reason_scoped_key(self, tmp_path):
        (tmp_path / "circuit_breaker_status.json").write_text(
            json.dumps({"tripped": True, "trip_reason": "daily loss 5%",
                        "cooldown_remaining_s": 900, "daily_drawdown_pct": 5.0})
        )
        findings = watchdog.check_circuit_breaker(data_dir=str(tmp_path))
        assert findings[0].key == "breaker_tripped:daily loss 5%"
        # The message must promise NOT to reset it — doctrine, asserted.
        assert "will NOT reset" in findings[0].message

    def test_untripped_quiet(self, tmp_path):
        (tmp_path / "circuit_breaker_status.json").write_text(json.dumps({"tripped": False}))
        assert watchdog.check_circuit_breaker(data_dir=str(tmp_path)) == []


class TestResourceChecks:
    def test_disk_thresholds(self, tmp_path):
        assert watchdog.check_disk(paths=[str(tmp_path)], warn_pct=0.0)
        assert watchdog.check_disk(paths=[str(tmp_path)], warn_pct=100.1) == []

    def test_memory_check_parses_meminfo(self, tmp_path):
        mi = tmp_path / "meminfo"
        mi.write_text("MemTotal: 1000000 kB\nMemAvailable: 50000 kB\n")
        findings = watchdog.check_memory(warn_pct=10.0, meminfo_path=str(mi))
        assert [f.key for f in findings] == ["memory_pressure"]
        mi.write_text("MemTotal: 1000000 kB\nMemAvailable: 500000 kB\n")
        assert watchdog.check_memory(warn_pct=10.0, meminfo_path=str(mi)) == []


class TestPagingDedupe:
    def _capture_pages(self, monkeypatch, tmp_path):
        _redirect_state_files(monkeypatch, tmp_path)
        sent: list[str] = []
        monkeypatch.setattr(watchdog.notify_telegram, "send_telegram", lambda t: sent.append(t) or True)
        return sent

    def test_page_once_per_cooldown_then_recovery_notice(self, monkeypatch, tmp_path):
        sent = self._capture_pages(monkeypatch, tmp_path)
        state = watchdog.WatchdogState()
        finding = watchdog.Finding(key="k1", severity="critical", message="broken")

        watchdog.dispatch_pages([finding], state, now=1000.0)
        assert len(sent) == 1

        # Same finding inside the cooldown → no second page.
        watchdog.dispatch_pages([finding], state, now=1000.0 + 60)
        assert len(sent) == 1

        # Past the cooldown and still broken → re-page.
        watchdog.dispatch_pages([finding], state, now=1000.0 + watchdog.PAGE_COOLDOWN_SEC + 1)
        assert len(sent) == 2

        # Cleared → exactly one recovery notice, then silence.
        watchdog.dispatch_pages([], state, now=1000.0 + watchdog.PAGE_COOLDOWN_SEC + 2)
        assert len(sent) == 3
        assert "recovered" in sent[-1]
        watchdog.dispatch_pages([], state, now=1000.0 + watchdog.PAGE_COOLDOWN_SEC + 3)
        assert len(sent) == 3

    def test_state_roundtrip(self, tmp_path):
        path = str(tmp_path / "state.json")
        state = watchdog.WatchdogState(
            last_paged_at={"k": 1.0},
            active_keys=["k"],
            engine_restarts=[2.0],
            blind_since={"b": 3.0},
            kill_switch_engaged_by_watchdog=True,
        )
        state.save(path)
        loaded = watchdog.WatchdogState.load(path)
        assert loaded == state

    def test_corrupt_state_file_starts_fresh(self, tmp_path):
        path = tmp_path / "state.json"
        path.write_text("{not json")
        assert watchdog.WatchdogState.load(str(path)) == watchdog.WatchdogState()


class TestRestartLadder:
    def _arm(self, monkeypatch, tmp_path):
        _redirect_state_files(monkeypatch, tmp_path)
        pages: list[str] = []
        restarts: list[str] = []
        engages: list[str] = []
        monkeypatch.setattr(watchdog.notify_telegram, "send_telegram", lambda t: pages.append(t) or True)
        monkeypatch.setattr(watchdog, "restart_container", lambda name: restarts.append(name) or True)
        monkeypatch.setattr(watchdog, "engage_kill_switch", lambda reason: engages.append(reason) or True)
        monkeypatch.setattr(watchdog, "RESTART_ENABLED", True)
        monkeypatch.setattr(watchdog, "KILLSWITCH_ENABLED", True)
        return pages, restarts, engages

    def test_restart_within_budget(self, monkeypatch, tmp_path):
        pages, restarts, engages = self._arm(monkeypatch, tmp_path)
        state = watchdog.WatchdogState()
        assert watchdog.restart_engine(state, "wedged", now=1000.0)
        assert restarts == [watchdog.ENGINE_CONTAINER]
        assert engages == []
        assert len(state.engine_restarts) == 1

    def test_budget_exhaustion_escalates_to_kill_switch(self, monkeypatch, tmp_path):
        pages, restarts, engages = self._arm(monkeypatch, tmp_path)
        state = watchdog.WatchdogState(
            engine_restarts=[1000.0, 1100.0, 1200.0]  # budget of 3/h consumed
        )
        assert not watchdog.restart_engine(state, "still wedged", now=1300.0)
        assert restarts == []  # no fourth restart
        assert engages == ["engine unrecoverable: still wedged"]
        assert state.kill_switch_engaged_by_watchdog

    def test_kill_switch_not_re_engaged_in_same_episode(self, monkeypatch, tmp_path):
        pages, restarts, engages = self._arm(monkeypatch, tmp_path)
        state = watchdog.WatchdogState(
            engine_restarts=[1000.0, 1100.0, 1200.0],
            kill_switch_engaged_by_watchdog=True,
        )
        watchdog.restart_engine(state, "still wedged", now=1300.0)
        assert engages == []

    def test_budget_window_slides(self, monkeypatch, tmp_path):
        pages, restarts, engages = self._arm(monkeypatch, tmp_path)
        state = watchdog.WatchdogState(engine_restarts=[1000.0, 1100.0, 1200.0])
        # 61 minutes later the hour window has slid — restart, don't escalate.
        assert watchdog.restart_engine(state, "wedged again", now=1200.0 + 3661)
        assert restarts == [watchdog.ENGINE_CONTAINER]
        assert engages == []

    def test_restart_disabled_pages_instead(self, monkeypatch, tmp_path):
        pages, restarts, engages = self._arm(monkeypatch, tmp_path)
        monkeypatch.setattr(watchdog, "RESTART_ENABLED", False)
        state = watchdog.WatchdogState()
        assert not watchdog.restart_engine(state, "wedged", now=1000.0)
        assert restarts == []
        assert any("manual action required" in p for p in pages)


class TestKillSwitchActuator:
    def test_no_token_means_no_engage(self, monkeypatch, tmp_path):
        _redirect_state_files(monkeypatch, tmp_path)
        monkeypatch.delenv("API_AUTH_TOKEN", raising=False)
        assert watchdog.engage_kill_switch("test") is False

    def test_engage_posts_owner_bearer_and_reason(self, monkeypatch, tmp_path):
        _redirect_state_files(monkeypatch, tmp_path)
        monkeypatch.setenv("API_AUTH_TOKEN", "owner-token")
        seen = {}

        class _Resp:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def _urlopen(req, timeout=0):
            seen["url"] = req.full_url
            seen["auth"] = req.get_header("Authorization")
            seen["body"] = json.loads(req.data)
            return _Resp()

        monkeypatch.setattr(watchdog.urllib.request, "urlopen", _urlopen)
        assert watchdog.engage_kill_switch("engine unrecoverable") is True
        assert seen["auth"] == "Bearer owner-token"
        assert seen["body"]["engaged"] is True
        assert seen["body"]["reason"] == "watchdog: engine unrecoverable"
        assert seen["url"].endswith("/api/kill-switch")

    def test_watchdog_has_no_disengage_code_path(self):
        # Doctrine test: the module must never POST engaged=false. Assert
        # at the source level so a future edit trips this immediately.
        src = (Path(watchdog.__file__)).read_text()
        assert '"engaged": True' in src
        assert '"engaged": False' not in src
        assert "'engaged': False" not in src
