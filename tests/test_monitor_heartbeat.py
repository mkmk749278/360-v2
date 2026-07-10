"""scripts/monitor_heartbeat.py — the hourly liveness probe (audit F-09).

The script is executed standalone (piped into the engine container), so
these tests run it as a subprocess against a tmpdir ``ENGINE_DATA_DIR``
and assert on its printed contract — in particular the ``INVARIANT_WARN``
lines the vps-liveness workflow pages on.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "monitor_heartbeat.py"


def _run(data_dir: Path, **extra_env: str) -> str:
    env = dict(os.environ)
    env["ENGINE_DATA_DIR"] = str(data_dir)
    env.update(extra_env)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


def _touch(path: Path, age_sec: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}")
    ts = time.time() - age_sec
    os.utime(path, (ts, ts))


class TestHeartbeatAndBreaker:
    def test_missing_everything_reports_not_found(self, tmp_path):
        out = _run(tmp_path)
        assert "NOT FOUND" in out
        assert "Circuit breaker: status file not found" in out
        assert "INVARIANT_WARN" not in out

    def test_fresh_heartbeat_ok(self, tmp_path):
        _touch(tmp_path / "scanner_heartbeat", age_sec=5)
        out = _run(tmp_path)
        assert "OK: Heartbeat fresh" in out

    def test_stale_heartbeat_warns(self, tmp_path):
        _touch(tmp_path / "scanner_heartbeat", age_sec=600)
        out = _run(tmp_path)
        assert "WARNING: Heartbeat is STALE" in out


class TestPaperSilence:
    def test_no_paper_books_skips_silently(self, tmp_path):
        _touch(tmp_path / "signal_performance.json", age_sec=60)
        out = _run(tmp_path)
        assert "paper trading not configured" in out
        assert "INVARIANT_WARN" not in out

    def test_active_engine_frozen_paper_pages(self, tmp_path):
        _touch(tmp_path / "signal_performance.json", age_sec=3600)  # engine active
        _touch(tmp_path / "paper_books" / "paper_pnl_user_1.json", age_sec=100_000)
        out = _run(tmp_path)
        assert "INVARIANT_WARN: paper books silent" in out

    def test_fresh_paper_book_is_ok(self, tmp_path):
        _touch(tmp_path / "signal_performance.json", age_sec=3600)
        _touch(tmp_path / "paper_books" / "paper_pnl_user_1.json", age_sec=300)
        out = _run(tmp_path)
        assert "OK: paper books consistent" in out
        assert "INVARIANT_WARN" not in out

    def test_idle_engine_does_not_page(self, tmp_path):
        # Engine itself quiet for 2 days → stale paper books are expected,
        # not an invariant breach (the heartbeat checks catch a dead engine).
        _touch(tmp_path / "signal_performance.json", age_sec=2 * 86400)
        _touch(tmp_path / "paper_books" / "paper_pnl_user_1.json", age_sec=3 * 86400)
        out = _run(tmp_path)
        assert "INVARIANT_WARN" not in out

    def test_newest_ledger_counts_across_users(self, tmp_path):
        # One frozen user ledger must not page while another is fresh — the
        # invariant is "the paper LAYER froze", not one idle user.
        _touch(tmp_path / "signal_performance.json", age_sec=3600)
        _touch(tmp_path / "paper_books" / "paper_pnl_user_1.json", age_sec=200_000)
        _touch(tmp_path / "paper_books" / "paper_pnl_user_2.json", age_sec=60)
        out = _run(tmp_path)
        assert "INVARIANT_WARN" not in out

    def test_thresholds_env_overridable(self, tmp_path):
        _touch(tmp_path / "signal_performance.json", age_sec=60)
        _touch(tmp_path / "paper_books" / "paper_pnl_user_1.json", age_sec=600)
        out = _run(tmp_path, PAPER_SILENCE_SEC="300")
        assert "INVARIANT_WARN: paper books silent" in out

    def test_legacy_shared_ledger_recognised(self, tmp_path):
        _touch(tmp_path / "signal_performance.json", age_sec=3600)
        _touch(tmp_path / "paper_pnl_state.json", age_sec=60)
        out = _run(tmp_path)
        assert "OK: paper books consistent" in out
