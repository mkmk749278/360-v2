#!/usr/bin/env python3
"""Healthcheck — verifies the 360-Crypto-scalping-V2 engine is running and healthy.

Restart-loop guard (2026-07-24 incident): this healthcheck gates the docker
HEALTHCHECK, and an ``autoheal`` sidecar restarts the container whenever it goes
unhealthy. That is the right medicine for a *transient* scanner hang (a deadlock
a restart clears) but the wrong medicine for a *persistent* condition a restart
can't fix — e.g. a Binance **REST IP-ban** that blocks the boot-time historical
seed. In that case every restart re-runs the seed (still banned), the scanner
never produces a heartbeat, we go unhealthy again ~10 min later, and autoheal
loops forever — each loop re-restoring signals as entry-0 shells and re-extending
the ban with fresh banned REST calls. So autoheal gets a BOUNDED number of
restarts, and past that we stop reporting unhealthy when a restart is
demonstrably not curing it. The process stays up and serving on the WebSocket
feed; vps-liveness + the feature-liveness watchdog still page a human for the
underlying outage.

That sentence used to read "we let autoheal restart a genuine mid-run hang
**once**", and the code did not do it: the bound covered only the
never-beat-since-boot branch, while a scanner that beat during warm-up and then
went stale fell through to an UNBOUNDED fail. Both branches are bounded now, on
one shared counter — a boot that never reaches a healthy steady state is the
same condition whichever way it fails, and only a genuinely fresh beat clears
it (2026-08-19, the day that loop ran).
"""
import json
import os
import sys
import time
from typing import Optional, Tuple

# Maximum age (seconds) of the heartbeat file before the scanner is considered
# stale — i.e. how long the scan loop may go without FINISHING A SYMBOL.
#
# This comment used to read "must be longer than a worst-case scan cycle", and
# the value did not satisfy it: the heartbeat was written once per completed
# cycle, and cycles were measured at 82.4s median / 402.5s worst against this
# 120s bound (2026-08-19). A constant asserting a property it does not have is
# the defect this repo has now paid for under several names — and here it cost a
# day of restart loop, because every slow cycle read as a wedge.
#
# The scanner now beats on PROGRESS (`Scanner._touch_heartbeat_progress`,
# throttled to ~1/5s), so this bound is once again what it claims to be: a
# wedge detector. A cycle slower than 120s keeps beating; a loop that has
# stopped advancing does not. Raising this number is therefore no longer the
# lever for a slow cycle — it would only make a real wedge take longer to catch.
_HEARTBEAT_MAX_AGE_SECONDS = 120.0
_HEARTBEAT_PATH = os.path.join(os.path.dirname(__file__), "data", "scanner_heartbeat")
# Grace period: give the engine time to complete its first scan cycle before
# treating a missing OR pre-restart heartbeat as a failure.  Boot re-seeds
# 75 pairs x multiple timeframes over REST — on a loaded box that takes
# several minutes, and 180s had autoheal killing warmups mid-boot during the
# 2026-07-13 restart storm.
_HEARTBEAT_GRACE_PERIOD_SECONDS = 480
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


def _restart_loop_guard_enabled() -> bool:
    """Whether to break an autoheal restart loop on a persistent stale beat.

    On by default; ``HEALTHCHECK_RESTART_LOOP_GUARD=false`` restores the strict
    legacy behaviour (always fail on a post-grace stale heartbeat).
    """
    return os.getenv("HEALTHCHECK_RESTART_LOOP_GUARD", "true").strip().lower() not in {
        "0", "false", "no", "off",
    }


# How many autoheal restarts to allow before concluding a never-beats-since-boot
# condition is persistent (external outage / boot failure a restart can't fix)
# and breaking the loop. Small enough that the loop self-limits within ~30 min,
# large enough that a genuinely transient boot hiccup still gets restart attempts.
_RESTART_GUARD_STATE_PATH = os.path.join(
    os.path.dirname(__file__), "data", "healthcheck_restart_guard"
)


def _max_restart_attempts() -> int:
    try:
        return max(1, int(os.getenv("HEALTHCHECK_MAX_RESTART_ATTEMPTS", "3")))
    except ValueError:
        return 3


def _read_restart_guard() -> Tuple[int, int]:
    """Persisted ``(boot_marker, consecutive_never_beat_boots)``; (0, 0) on failure."""
    try:
        with open(_RESTART_GUARD_STATE_PATH) as fh:
            data = json.load(fh)
        return int(data.get("boot", 0)), int(data.get("count", 0))
    except Exception:
        return 0, 0


def _write_restart_guard(boot_marker: int, count: int) -> bool:
    try:
        os.makedirs(os.path.dirname(_RESTART_GUARD_STATE_PATH), exist_ok=True)
        with open(_RESTART_GUARD_STATE_PATH, "w") as fh:
            json.dump({"boot": boot_marker, "count": count}, fh)
        return True
    except Exception:
        return False


def _reset_restart_guard() -> None:
    """Clear the restart counter — called on a genuinely fresh heartbeat."""
    boot_marker, count = _read_restart_guard()
    if count != 0:
        _write_restart_guard(boot_marker, 0)


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
            # The heartbeat file lives on the data volume, so its mtime
            # survives a container restart.  A "stale" heartbeat that
            # predates the engine process itself is a WARMING-UP engine,
            # not a wedged one — failing here made autoheal kill every
            # boot mid-warmup (2026-07-13).  After the grace period a
            # still-untouched heartbeat is a real failure.
            uptime = (
                _engine_uptime_seconds(engine_pid)
                if engine_pid is not None
                else _UNKNOWN_UPTIME_SECONDS
            )
            # "Never beat this boot": the heartbeat mtime predates the current
            # engine process (age older than uptime), so the scanner has not
            # written a single fresh beat since this (re)start.
            never_beat_this_boot = age > uptime
            if never_beat_this_boot and uptime < _HEARTBEAT_GRACE_PERIOD_SECONDS:
                return True  # pre-restart mtime; engine still warming up
            if never_beat_this_boot and _restart_loop_guard_enabled():
                # Past the grace period and STILL no fresh beat since boot. Let
                # autoheal restart a BOUNDED number of times — a transient
                # boot-time failure can be cured by a restart — but once the
                # condition survives that many restarts it is persistent (a
                # Binance REST IP-ban blocking the boot seed, a boot-time crash;
                # neither cured by more restarts, and each loop re-restores
                # signals as entry-0 shells and re-extends the ban). Then report
                # healthy-but-DEGRADED so autoheal stops thrashing: the process
                # is alive and serving on the WS feed, and vps-liveness +
                # feature-liveness still page a human.
                #
                # The counter is keyed on the engine process start (uptime), so
                # it increments once per restarted boot and resets on a genuine
                # fresh beat. Unknown uptime keeps the strict (fail) path.
                if uptime != _UNKNOWN_UPTIME_SECONDS:
                    boot_marker = int(time.time() - uptime)
                    prev_boot, count = _read_restart_guard()
                    if boot_marker != prev_boot:
                        count += 1
                        _write_restart_guard(boot_marker, count)
                    if count >= _max_restart_attempts():
                        print(
                            f"Heartbeat unrefreshed across {count} restart(s) "
                            f"(age={age:.0f}s, uptime ~{uptime:.0f}s) — a restart is "
                            f"not curing it; reporting DEGRADED (not unhealthy) to "
                            f"break the autoheal loop. Process alive on WS; external "
                            f"outage suspected. Path: {_HEARTBEAT_PATH}",
                            file=sys.stderr,
                        )
                        return True
                    print(
                        f"Heartbeat unrefreshed since boot (age={age:.0f}s, uptime "
                        f"~{uptime:.0f}s) — failing so autoheal restarts "
                        f"(attempt {count}/{_max_restart_attempts()}).",
                        file=sys.stderr,
                    )
                    return False
            # Beat this boot then went stale (mid-run hang), or the guard is
            # disabled / uptime unknown → fail so autoheal restarts.
            #
            # Bounded the same way as the never-beat case, and for the same
            # reason (2026-08-19): the bound above covered only "never beat
            # since boot", so a scanner that beat during warm-up and then went
            # stale could be restarted forever. That is exactly what ran all of
            # 2026-08-19 — restart -> cold indicator caches + a full REST
            # re-seed -> the next cycle slower than the one that tripped the
            # deadline -> restart, every ~15 minutes, each loop expiring every
            # `snapshot:*` key and emptying the dashboard and the app feed.
            # A restart that has demonstrably not cured the condition across
            # this many boots is not medicine, and the argument for stopping is
            # the one the never-beat branch already makes: the process is alive
            # and serving on the WS feed, every open position's SL/TP rests on
            # Binance, and vps-liveness + feature-liveness still page a human.
            #
            # The counter is shared with the never-beat path on purpose — it
            # counts boots that failed to reach a healthy steady state, however
            # they failed — and `_reset_restart_guard` clears it on the first
            # genuinely fresh beat, so a one-off hang still gets its restart.
            if _restart_loop_guard_enabled() and uptime != _UNKNOWN_UPTIME_SECONDS:
                boot_marker = int(time.time() - uptime)
                prev_boot, count = _read_restart_guard()
                if boot_marker != prev_boot:
                    count += 1
                    _write_restart_guard(boot_marker, count)
                if count >= _max_restart_attempts():
                    print(
                        f"Heartbeat stale on {count} consecutive boot(s) "
                        f"(age={age:.1f}s > max={_HEARTBEAT_MAX_AGE_SECONDS:.0f}s, "
                        f"uptime ~{uptime:.0f}s) — restarting is not curing it and "
                        f"each restart re-seeds every pair cold; reporting DEGRADED "
                        f"(not unhealthy) to break the autoheal loop. Process alive "
                        f"on WS. Path: {_HEARTBEAT_PATH}",
                        file=sys.stderr,
                    )
                    return True
                print(
                    f"Heartbeat is stale: age={age:.1f}s > max={_HEARTBEAT_MAX_AGE_SECONDS:.0f}s "
                    f"(engine uptime ~{uptime:.0f}s) — failing so autoheal restarts "
                    f"(attempt {count}/{_max_restart_attempts()}). Path: {_HEARTBEAT_PATH}",
                    file=sys.stderr,
                )
                return False
            print(
                f"Heartbeat is stale: age={age:.1f}s > max={_HEARTBEAT_MAX_AGE_SECONDS:.0f}s "
                f"(engine uptime ~{uptime:.0f}s). Path: {_HEARTBEAT_PATH}",
                file=sys.stderr,
            )
            return False
        _reset_restart_guard()  # genuine fresh beat — clear any restart counter
        return True
    except OSError:
        return True  # Cannot stat — treat as fresh to avoid false negatives


def main() -> int:
    engine_pid = _find_engine_pid()
    if engine_pid is None:
        print("Engine process (src.main) not found.", file=sys.stderr)
        return 1

    if not _config_importable():
        print("Config module could not be imported — dependency issue.", file=sys.stderr)
        return 1

    if not _logs_dir_exists():
        print("logs/ directory does not exist.", file=sys.stderr)
        return 1

    if not _scanner_heartbeat_fresh(engine_pid):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
