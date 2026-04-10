#!/usr/bin/env python3
"""Healthcheck — verifies the 360-Crypto-scalping-V2 engine is running and healthy."""
import os
import sys
import time
from typing import Optional

# Maximum age (seconds) of the heartbeat file before the scanner is
# considered stale.  Must be longer than a worst-case scan cycle.
_HEARTBEAT_MAX_AGE_SECONDS = 120.0
_HEARTBEAT_PATH = os.path.join(os.path.dirname(__file__), "data", "scanner_heartbeat")
# Grace period: give the engine time to complete its first scan cycle before
# treating a missing heartbeat file as a failure.
_HEARTBEAT_GRACE_PERIOD_SECONDS = 180
# Index of the starttime field in /proc/pid/stat after stripping "pid (comm) ".
# Corresponds to field 22 in the kernel ABI (1-based).  We need at least this
# many fields to be present before indexing.
_STAT_STARTTIME_IDX = 19
_STAT_MIN_FIELDS = 20
# Byte offset past ") " that separates the comm field from the remaining fields.
_STAT_AFTER_COMM_OFFSET = 2
# Sentinel used when engine uptime cannot be determined — treated as "old
# enough to have produced a heartbeat" so that a missing file is treated as a
# real failure rather than hiding bugs.
_UNKNOWN_UPTIME_SECONDS = 999


def _find_engine_pid() -> Optional[int]:
    """Return the PID of the running src.main engine process, or None if not found."""
    try:
        for entry in os.listdir("/proc"):
            if not entry.isdigit():
                continue
            try:
                with open(f"/proc/{entry}/cmdline", "rb") as fh:
                    cmdline = fh.read().replace(b"\x00", b" ").decode("utf-8", errors="replace")
                if "python" in cmdline and "src.main" in cmdline:
                    return int(entry)
            except (FileNotFoundError, PermissionError):
                continue
    except FileNotFoundError:
        pass
    return None


def _engine_process_running() -> bool:
    """Return True if a Python process running src.main is found in /proc."""
    return _find_engine_pid() is not None


def _engine_uptime_seconds(pid: int) -> float:
    """Return how long the engine process (pid) has been running, in seconds.

    Reads directly from the Linux /proc filesystem — no external commands
    required, so this works in minimal containers (python:slim) that do not
    include procps/ps.

    Returns _UNKNOWN_UPTIME_SECONDS on any failure so callers treat the engine
    as old enough to have written a heartbeat (i.e., a missing heartbeat is a
    real failure, not a startup-grace pass).
    """
    try:
        with open(f"/proc/{pid}/stat") as fh:
            stat = fh.read()
        # The comm field (2nd token) is wrapped in parentheses and may contain
        # spaces.  Skip everything up to and including the last ')'.
        rpar = stat.rfind(")")
        if rpar < 0:
            return _UNKNOWN_UPTIME_SECONDS
        # Fields after ')': state ppid pgrp session tty_nr tpgid flags
        #   minflt cminflt majflt cmajflt utime stime cutime cstime
        #   priority nice num_threads itrealvalue starttime …
        # starttime is at index _STAT_STARTTIME_IDX (0-based) in this slice.
        fields = stat[rpar + _STAT_AFTER_COMM_OFFSET:].split()
        if len(fields) < _STAT_MIN_FIELDS:
            return _UNKNOWN_UPTIME_SECONDS
        starttime_ticks = int(fields[_STAT_STARTTIME_IDX])
        clk_tck = os.sysconf("SC_CLK_TCK")
        with open("/proc/uptime") as fh:
            system_uptime = float(fh.read().split()[0])
        return system_uptime - (starttime_ticks / clk_tck)
    except Exception:
        return _UNKNOWN_UPTIME_SECONDS


def _config_importable() -> bool:
    """Return True if the engine config module can be imported (proves deps are installed)."""
    try:
        import config
        # Access a known attribute to confirm the module loaded correctly
        _ = config.BINANCE_REST_BASE
        return True
    except Exception:
        return False


def _logs_dir_exists() -> bool:
    """Return True if the logs directory exists."""
    return os.path.isdir(os.path.join(os.path.dirname(__file__), "logs"))


def _scanner_heartbeat_fresh(engine_pid: Optional[int]) -> bool:
    """Return True if the scanner heartbeat file was touched recently.

    A grace period of _HEARTBEAT_GRACE_PERIOD_SECONDS is applied at startup:
    if the *engine process* has been running for less than that time and the
    heartbeat file does not exist yet, the check passes (engine may still be
    completing its first scan cycle).  After the grace period a missing file
    is treated as a failure.

    The grace period is based on the engine process uptime — read from
    /proc/<engine_pid>/stat — not the short-lived healthcheck subprocess PID.
    """
    if not os.path.isfile(_HEARTBEAT_PATH):
        uptime = (
            _engine_uptime_seconds(engine_pid)
            if engine_pid is not None
            else _UNKNOWN_UPTIME_SECONDS
        )
        if uptime < _HEARTBEAT_GRACE_PERIOD_SECONDS:
            return True  # Engine still within startup grace period
        uptime_str = f"~{uptime:.0f}s" if uptime != _UNKNOWN_UPTIME_SECONDS else "unknown"
        print(
            f"Heartbeat file missing after grace period "
            f"(engine uptime {uptime_str}, grace={_HEARTBEAT_GRACE_PERIOD_SECONDS}s). "
            f"Expected at: {_HEARTBEAT_PATH}",
            file=sys.stderr,
        )
        return False  # Missing after grace — scanner loop never ran or crashed

    try:
        age = time.time() - os.path.getmtime(_HEARTBEAT_PATH)
        if age >= _HEARTBEAT_MAX_AGE_SECONDS:
            print(
                f"Heartbeat is stale: age={age:.1f}s > max={_HEARTBEAT_MAX_AGE_SECONDS:.0f}s. "
                f"Path: {_HEARTBEAT_PATH}",
                file=sys.stderr,
            )
            return False
        return True
    except OSError:
        return True  # Cannot stat — treat as fresh to avoid false negatives


engine_pid = _find_engine_pid()
if engine_pid is None:
    print("Engine process (src.main) not found.", file=sys.stderr)
    sys.exit(1)

if not _config_importable():
    print("Config module could not be imported — dependency issue.", file=sys.stderr)
    sys.exit(1)

if not _logs_dir_exists():
    print("logs/ directory does not exist.", file=sys.stderr)
    sys.exit(1)

if not _scanner_heartbeat_fresh(engine_pid):
    sys.exit(1)

sys.exit(0)
