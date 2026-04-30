"""Tests for scripts/extract_engine_logs.sh.

Validates the date-range filter and the rc=2 missing-sink contract that the
vps-monitor workflow relies on for fallback logic.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR = REPO_ROOT / "scripts" / "extract_engine_logs.sh"


def _run(script_path: Path, log_dir: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run extract_engine_logs.sh against a synthesised /app/logs directory.

    The script hardcodes /app/logs, so we invoke it through a wrapper that
    bind-mounts the test directory to /app/logs via a temp symlink path.
    Implementation: copy the script to a temp file, sed the path, run it.
    """
    tmp_script = log_dir.parent / "extract_under_test.sh"
    original = script_path.read_text(encoding="utf-8")
    tmp_script.write_text(original.replace("/app/logs", str(log_dir)), encoding="utf-8")
    tmp_script.chmod(0o755)
    return subprocess.run(
        [str(tmp_script), *args],
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
    )


@pytest.fixture
def log_root(tmp_path):
    log_dir = tmp_path / "applogs"
    log_dir.mkdir()
    return log_dir


def test_extractor_returns_rc2_when_no_log_files(log_root):
    """Workflow uses rc=2 to detect missing sink and fall back to docker logs."""
    result = _run(EXTRACTOR, log_root, "2026-04-30 00:00:00")
    assert result.returncode == 2, (
        f"Empty /app/logs must exit 2, got rc={result.returncode} stderr={result.stderr}"
    )


def test_extractor_filters_by_start_only(log_root):
    """Open-ended window: emit every line with timestamp >= start."""
    log_file = log_root / "engine_2026-04-30.log"
    log_file.write_text(
        "\n".join([
            "2026-04-30 09:00:00 | scanner | INFO    | early line, before window",
            "2026-04-30 10:00:00 | scanner | INFO    | first in-window line",
            "2026-04-30 10:30:00 | scanner | INFO    | Path funnel (last 100 cycles): path={} channel={}",
            "2026-04-30 11:00:00 | scanner | INFO    | Regime distribution (last 100 cycles): {'QUIET': 100}",
            # Continuation line (no leading date) — must be filtered out by the
            # `^[0-9]{4}-` anchor regardless of position.
            "    traceback continuation should be dropped",
        ]),
        encoding="utf-8",
    )
    result = _run(EXTRACTOR, log_root, "2026-04-30 10:00:00")
    assert result.returncode == 0
    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    assert len(lines) == 3
    assert "first in-window line" in lines[0]
    assert "Path funnel" in lines[1]
    assert "Regime distribution" in lines[2]


def test_extractor_filters_by_start_and_stop(log_root):
    """Two-arg invocation: emit lines in [start, stop) — exclusive upper bound."""
    log_file = log_root / "engine_2026-04-30.log"
    log_file.write_text(
        "\n".join([
            "2026-04-30 08:00:00 | scanner | INFO    | before window",
            "2026-04-30 10:00:00 | scanner | INFO    | at start (inclusive)",
            "2026-04-30 11:30:00 | scanner | INFO    | inside window",
            "2026-04-30 12:00:00 | scanner | INFO    | at stop (exclusive — must be excluded)",
            "2026-04-30 13:00:00 | scanner | INFO    | after window",
        ]),
        encoding="utf-8",
    )
    result = _run(EXTRACTOR, log_root, "2026-04-30 10:00:00", "2026-04-30 12:00:00")
    assert result.returncode == 0
    out_text = result.stdout
    assert "at start (inclusive)" in out_text
    assert "inside window" in out_text
    assert "at stop (exclusive" not in out_text
    assert "before window" not in out_text
    assert "after window" not in out_text


def test_extractor_concatenates_multiple_log_files(log_root):
    """Loguru rotates by 50MB → multiple engine_*.log files in production."""
    (log_root / "engine_2026-04-29.log").write_text(
        "2026-04-29 23:30:00 | scanner | INFO    | rolled-file line\n",
        encoding="utf-8",
    )
    (log_root / "engine_2026-04-30.log").write_text(
        "2026-04-30 00:30:00 | scanner | INFO    | current-file line\n",
        encoding="utf-8",
    )
    result = _run(EXTRACTOR, log_root, "2026-04-29 00:00:00")
    assert result.returncode == 0
    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    assert len(lines) == 2
    assert any("rolled-file line" in ln for ln in lines)
    assert any("current-file line" in ln for ln in lines)


def test_extractor_emits_zero_lines_inside_empty_window_succeeds(log_root):
    """A window with no matching lines exits 0 (success) — only missing sink is rc=2."""
    log_file = log_root / "engine_2026-04-30.log"
    log_file.write_text(
        "2026-04-30 09:00:00 | scanner | INFO    | only line, before window\n",
        encoding="utf-8",
    )
    result = _run(EXTRACTOR, log_root, "2026-04-30 10:00:00")
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_extractor_works_via_sh_s_stdin_invocation(log_root):
    """The workflow invokes the extractor via `sh -s "$ARG"` reading from
    stdin (matches the monitor_heartbeat.py pattern at line 99 of
    vps-monitor.yml).  This avoids the docker-cp + chmod path that fails
    "Operation not permitted" when the engine container runs as a non-root
    user.  Verify the script behaves identically when piped vs invoked.
    """
    log_file = log_root / "engine_2026-04-30.log"
    log_file.write_text(
        "\n".join([
            "2026-04-30 08:00:00 | scanner | INFO | before window",
            "2026-04-30 10:00:00 | scanner | INFO | in window",
        ]),
        encoding="utf-8",
    )
    # Rewrite the hardcoded /app/logs path to point at the test fixture, then
    # pipe through `sh -s` exactly as the workflow does.
    script_text = EXTRACTOR.read_text(encoding="utf-8").replace("/app/logs", str(log_root))
    result = subprocess.run(
        ["sh", "-s", "2026-04-30 09:30:00"],
        input=script_text,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "in window" in result.stdout
    assert "before window" not in result.stdout

    # rc=2 contract still holds via stdin invocation when the sink is missing.
    empty_dir = log_root.parent / "empty_logs"
    empty_dir.mkdir()
    script_empty = EXTRACTOR.read_text(encoding="utf-8").replace("/app/logs", str(empty_dir))
    result2 = subprocess.run(
        ["sh", "-s", "2026-04-30 09:30:00"],
        input=script_empty,
        capture_output=True,
        text=True,
    )
    assert result2.returncode == 2
