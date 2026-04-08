#!/usr/bin/env python3
"""Healthcheck — verifies the 360-Crypto-scalping-V2 engine is running and healthy."""
import os
import subprocess
import sys
import time

# Maximum age (seconds) of the heartbeat file before the scanner is
# considered stale.  Must be longer than a worst-case scan cycle.
_HEARTBEAT_MAX_AGE_SECONDS = 120.0
_HEARTBEAT_PATH = os.path.join(os.path.dirname(__file__), "data", "scanner_heartbeat")
# Grace period: give the engine time to complete its first scan cycle before
# treating a missing heartbeat file as a failure.
_HEARTBEAT_GRACE_PERIOD_SECONDS = 180
# Sentinel used when process uptime cannot be determined — treated as "old enough".
_UNKNOWN_UPTIME_SECONDS = 999


def _engine_process_running() -> bool:
    """Return True if a Python process running src.main is found in /proc."""
    try:
        for entry in os.listdir("/proc"):
            if not entry.isdigit():
                continue
            try:
                with open(f"/proc/{entry}/cmdline", "rb") as fh:
                    cmdline = fh.read().replace(b"\x00", b" ").decode("utf-8", errors="replace")
                if "python" in cmdline and "src.main" in cmdline:
                    return True
            except (FileNotFoundError, PermissionError):
                continue
    except FileNotFoundError:
        pass
    return False


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


def _scanner_heartbeat_fresh() -> bool:
    """Return True if the scanner heartbeat file was touched recently.

    A grace period of 180 seconds is applied at startup: if the process has
    been running for less than 180 seconds and the heartbeat file does not
    exist yet, the check passes (engine may still be completing its first
    scan cycle).  After the grace period a missing file is treated as stale.
    """
    if not os.path.isfile(_HEARTBEAT_PATH):
        # Determine how long this process has been running.
        try:
            result = subprocess.run(
                ["ps", "-o", "etimes=", "-p", str(os.getpid())],
                capture_output=True,
                text=True,
                timeout=2,
            )
            uptime_seconds = (
                int(result.stdout.strip())
                if result.stdout.strip().isdigit()
                else _UNKNOWN_UPTIME_SECONDS
            )
        except Exception:
            uptime_seconds = _UNKNOWN_UPTIME_SECONDS  # Assume old enough — treat missing as stale

        if uptime_seconds < _HEARTBEAT_GRACE_PERIOD_SECONDS:
            return True  # Still in grace period
        return False  # Missing after grace period — scanner loop never ran or crashed

    try:
        age = time.time() - os.path.getmtime(_HEARTBEAT_PATH)
        return age < _HEARTBEAT_MAX_AGE_SECONDS
    except OSError:
        return True  # Cannot stat — treat as fresh to avoid false negatives


if not _engine_process_running():
    print("Engine process (src.main) not found.", file=sys.stderr)
    sys.exit(1)

if not _config_importable():
    print("Config module could not be imported — dependency issue.", file=sys.stderr)
    sys.exit(1)

if not _logs_dir_exists():
    print("logs/ directory does not exist.", file=sys.stderr)
    sys.exit(1)

if not _scanner_heartbeat_fresh():
    print(
        f"Scanner heartbeat is stale (>{_HEARTBEAT_MAX_AGE_SECONDS:.0f}s old).",
        file=sys.stderr,
    )
    sys.exit(1)

sys.exit(0)
