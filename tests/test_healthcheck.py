"""Healthcheck scanner-heartbeat logic, incl. the autoheal restart-loop guard.

The docker HEALTHCHECK drives an ``autoheal`` sidecar, so what this returns
decides whether the engine gets force-restarted. These pin the 2026-07-24
incident fix: autoheal is allowed a BOUNDED number of restarts for a genuine
transient hang, but the check must stop going unhealthy (→ endless restarts)
once a never-beats-since-boot condition is clearly persistent (an external
Binance-REST outage a restart cannot fix).

Pure/file-based: we write a heartbeat file with a controlled mtime and stub the
engine uptime, so no engine process or network is needed. The restart-guard
state file is isolated to tmp per test.
"""
from __future__ import annotations

import os
import time

import pytest

import healthcheck


@pytest.fixture(autouse=True)
def _isolate_guard_state(tmp_path, monkeypatch):
    """Keep the restart counter out of the real data/ dir and off other tests."""
    monkeypatch.setattr(
        healthcheck, "_RESTART_GUARD_STATE_PATH", str(tmp_path / "restart_guard")
    )


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


def test_never_beat_first_occurrence_fails(tmp_path, monkeypatch) -> None:
    # Past grace, never beat this boot, counter at 0 (< default max 3): still
    # FAIL so autoheal gets its bounded restart attempt.
    p = str(tmp_path / "scanner_heartbeat")
    _write_beat(p, 700)
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 600.0)
    assert healthcheck._scanner_heartbeat_fresh(123) is False


def test_never_beat_breaks_loop_after_threshold(tmp_path, monkeypatch, capsys) -> None:
    # With max=2: first boot fails (autoheal restart), a second distinct boot
    # that still never beats hits the cap → healthy-DEGRADED, breaking the loop.
    monkeypatch.setenv("HEALTHCHECK_MAX_RESTART_ATTEMPTS", "2")
    p = str(tmp_path / "scanner_heartbeat")
    _write_beat(p, 5000)  # heartbeat older than either uptime → never beat since boot
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)

    # Boot 1 (uptime 600, past grace): counter → 1/2 → fail (autoheal restart).
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 600.0)
    assert healthcheck._scanner_heartbeat_fresh(123) is False

    # Boot 2 (distinct uptime 650 → distinct boot marker): counter → 2/2 → cap
    # reached → healthy-DEGRADED, breaking the loop.
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 650.0)
    assert healthcheck._scanner_heartbeat_fresh(123) is True
    assert "break the autoheal loop" in capsys.readouterr().err


def test_guard_can_be_disabled_for_strict_legacy(tmp_path, monkeypatch) -> None:
    p = str(tmp_path / "scanner_heartbeat")
    _write_beat(p, 700)
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 600.0)
    monkeypatch.setenv("HEALTHCHECK_RESTART_LOOP_GUARD", "false")
    assert healthcheck._scanner_heartbeat_fresh(123) is False


def test_stale_after_beating_this_boot_fails(tmp_path, monkeypatch) -> None:
    # Beat this boot (age<uptime) then went stale → mid-run hang → fail, so
    # autoheal gets its restart attempt. Passes on the FIRST attempt only: this
    # branch is bounded by the same counter as the never-beat one (2026-08-19),
    # which is what `test_stale_after_beating_breaks_loop_after_threshold`
    # below pins. Before that it failed forever, which is the loop it caused.
    p = str(tmp_path / "scanner_heartbeat")
    _write_beat(p, 200)
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 5000.0)
    assert healthcheck._scanner_heartbeat_fresh(123) is False


def test_fresh_beat_resets_guard(tmp_path, monkeypatch) -> None:
    # A stuck counter is cleared the moment the scanner beats fresh again.
    healthcheck._write_restart_guard(12345, 2)
    p = str(tmp_path / "scanner_heartbeat")
    _write_beat(p, 5)
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 1000.0)
    assert healthcheck._scanner_heartbeat_fresh(123) is True
    assert healthcheck._read_restart_guard()[1] == 0


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


def test_stale_after_beating_breaks_loop_after_threshold(
    tmp_path, monkeypatch, capsys,
) -> None:
    """A mid-run hang that survives N restarts stops reporting unhealthy.

    The 2026-08-19 loop: the scanner beat during warm-up, went stale when a scan
    cycle ran past 120s, autoheal restarted, the restart re-seeded every pair
    over REST and rebuilt the indicator caches cold, and the next cycle was
    slower still — every ~15 minutes, each restart expiring every `snapshot:*`
    key and emptying the dashboard and the app feed. The bound existed and
    covered only the never-beat-since-boot branch.

    Fails against the pre-fix tree, where this branch returned False forever.
    """
    p = str(tmp_path / "scanner_heartbeat")
    _write_beat(p, 200)
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 5000.0)

    # Each boot is a distinct process start, so the counter advances once per boot.
    seen = []
    for boot in range(1, 5):
        monkeypatch.setattr(
            healthcheck, "_engine_uptime_seconds", lambda pid, b=boot: 5000.0 + b,
        )
        seen.append(healthcheck._scanner_heartbeat_fresh(123))

    # Default max attempts is 3: fail, fail, then DEGRADED-but-healthy.
    assert seen[:2] == [False, False]
    assert seen[2] is True and seen[3] is True
    assert "not curing it" in capsys.readouterr().err


def test_stale_after_beating_resets_on_a_fresh_beat(tmp_path, monkeypatch) -> None:
    """A one-off hang still gets its restarts once the scanner recovers.

    The bound must not be a one-way door: without this, three unrelated hangs
    over the container's whole life would permanently disarm autoheal for a
    genuine wedge later.
    """
    p = str(tmp_path / "scanner_heartbeat")
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)

    _write_beat(p, 200)
    monkeypatch.setattr(healthcheck, "_engine_uptime_seconds", lambda pid: 5000.0)
    assert healthcheck._scanner_heartbeat_fresh(123) is False
    assert healthcheck._read_restart_guard()[1] == 1

    _write_beat(p, 5)
    assert healthcheck._scanner_heartbeat_fresh(123) is True
    assert healthcheck._read_restart_guard()[1] == 0


def test_stale_after_beating_respects_the_strict_legacy_switch(
    tmp_path, monkeypatch,
) -> None:
    """`HEALTHCHECK_RESTART_LOOP_GUARD=false` restores unbounded restarts.

    The off-switch is the whole reversibility argument for bounding this branch,
    so it is asserted on the branch that was just bounded, not only on the one
    that already was.
    """
    p = str(tmp_path / "scanner_heartbeat")
    _write_beat(p, 200)
    monkeypatch.setattr(healthcheck, "_HEARTBEAT_PATH", p)
    monkeypatch.setenv("HEALTHCHECK_RESTART_LOOP_GUARD", "false")
    for boot in range(1, 6):
        monkeypatch.setattr(
            healthcheck, "_engine_uptime_seconds", lambda pid, b=boot: 5000.0 + b,
        )
        assert healthcheck._scanner_heartbeat_fresh(123) is False
