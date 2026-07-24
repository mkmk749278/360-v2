"""Healthcheck scanner-heartbeat logic, incl. the autoheal restart-loop guard.

The docker HEALTHCHECK drives an ``autoheal`` sidecar, so what this returns
decides whether the engine gets force-restarted. These pin the 2026-07-24
incident fix: a restart is allowed once for a genuine mid-run hang, but the
check must NOT keep going unhealthy (→ endless autoheal restarts) when a restart
cannot cure the condition (a persistent external outage where the scanner never
beats since boot).

Pure/file-based: we write a heartbeat file with a controlled mtime and stub the
engine uptime, so no engine process or network is needed.
"""
from __future__ import annotations

import os
import time

import healthcheck


def _write_beat(path: str, age_s: float) -> None:
    with open(path, "w") as fh:
        fh.write("beat")
    mt = time.time() - age_s
    os.utime(path, (mt, mt))


def test_fresh_beat_passes(tmp_path, monkeypatch) -> None:
    p = str(tmp_path / "scanner_heartbeat")
    _write_beat(p, 5)
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 1000.0)
    assert healthcheck._scanner_heartbeat_fresh(123) is True


def test_stale_never_beat_within_grace_is_warming_up(tmp_path, monkeypatch) -> None:
    # Stale (>120s) but the beat predates a young process (uptime<grace) → warmup.
    p = str(tmp_path / "scanner_heartbeat")
    _write_beat(p, 200)
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 100.0)
    assert healthcheck._scanner_heartbeat_fresh(123) is True


def test_stale_never_beat_past_grace_breaks_the_loop(tmp_path, monkeypatch, capsys) -> None:
    # Past grace, and the scanner has STILL not beaten since boot (age>uptime).
    # A restart isn't curing it → report healthy-degraded to stop autoheal.
    p = str(tmp_path / "scanner_heartbeat")
    _write_beat(p, 700)
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 600.0)
    monkeypatch.delenv("HEALTHCHECK_RESTART_LOOP_GUARD", raising=False)  # default ON
    assert healthcheck._scanner_heartbeat_fresh(123) is True
    assert "DEGRADED" in capsys.readouterr().err


def test_guard_can_be_disabled_for_strict_legacy(tmp_path, monkeypatch) -> None:
    p = str(tmp_path / "scanner_heartbeat")
    _write_beat(p, 700)
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 600.0)
    monkeypatch.setenv("HEALTHCHECK_RESTART_LOOP_GUARD", "false")
    assert healthcheck._scanner_heartbeat_fresh(123) is False


def test_stale_after_beating_this_boot_fails(tmp_path, monkeypatch) -> None:
    # Beat this boot (age<uptime) then went stale → genuine mid-run hang → fail,
    # so autoheal restarts once to try to clear it.
    p = str(tmp_path / "scanner_heartbeat")
    _write_beat(p, 200)
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 5000.0)
    assert healthcheck._scanner_heartbeat_fresh(123) is False


def test_missing_file_within_grace_passes(tmp_path, monkeypatch) -> None:
    p = str(tmp_path / "does_not_exist")
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 60.0)
    assert healthcheck._scanner_heartbeat_fresh(123) is True


def test_missing_file_past_grace_fails(tmp_path, monkeypatch) -> None:
    p = str(tmp_path / "does_not_exist")
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 9999.0)
    assert healthcheck._scanner_heartbeat_fresh(123) is False


def test_restart_loop_guard_env_parsing(monkeypatch) -> None:
    monkeypatch.delenv("HEALTHCHECK_RESTART_LOOP_GUARD", raising=False)
    assert healthcheck._restart_loop_guard_enabled() is True
    monkeypatch.setenv("HEALTHCHECK_RESTART_LOOP_GUARD", "off")
    assert healthcheck._restart_loop_guard_enabled() is False
    monkeypatch.setenv("HEALTHCHECK_RESTART_LOOP_GUARD", "true")
    assert healthcheck._restart_loop_guard_enabled() is True
