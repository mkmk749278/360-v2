"""What the box is actually giving this process — read from inside it.

Built 2026-08-19, for the owner's first question of the stability session:
*"engine cpu 221% used is our vps not enough or what"*. That question had no
answer on any ops surface. It was answerable only over SSH, and the answer
matters: 221% of a 250% quota is a process at its ceiling and a scan loop that
will keep tripping the healthcheck, while 221% of a 400% host with no quota is
a busy box with room.

Three design decisions, each one a rule this system has already paid for:

**Measured in the ENGINE container, published, then read.** CPU and memory are
facts about the cgroup the reader is standing in. In isolated mode the API
container serves the diag, and it would have measured *itself* — reporting a
near-idle HTTP process as the engine's load. That is the trail-governor
``INDEX COLD`` defect exactly: which process holds the state is not a
deployment detail. The engine samples, the snapshot writer publishes, the API
container reads what was published and measures nothing of its own.

**Effective config comes from the running process, never from a side
process.** ``docker exec ... python -c "from config import X; print(X)"``
prints what the image was BUILT with; this repo has already believed such a
reading once and been wrong about which gate was live. These values are read
out of the module the scanner is actually using.

**Absent is not zero.** Every reading that cannot be taken returns ``None``
with a named reason. A cgroup file missing on a bare-metal run and a quota of
zero are different facts, and a 0.0% CPU reading over a pinned engine is worse
than a blank because it looks like an answer.
"""
from __future__ import annotations

import os
import shutil
import time
from typing import Any, Dict, Optional, Tuple

_CG2_CPU_MAX = "/sys/fs/cgroup/cpu.max"
_CG2_CPU_STAT = "/sys/fs/cgroup/cpu.stat"
_CG2_MEM_CURRENT = "/sys/fs/cgroup/memory.current"
_CG2_MEM_MAX = "/sys/fs/cgroup/memory.max"
_CG1_CPU_USAGE = "/sys/fs/cgroup/cpuacct/cpuacct.usage"
_CG1_MEM_USAGE = "/sys/fs/cgroup/memory/memory.usage_in_bytes"
_CG1_MEM_LIMIT = "/sys/fs/cgroup/memory/memory.limit_in_bytes"

#: A cgroup v1 "no limit" is a sentinel close to 2^63, not an absent file.
_CG1_UNLIMITED = 1 << 62

#: Previous CPU sample, so a rate can be computed without ever sleeping.
#: A blocking sample inside the snapshot-writer loop would add its own delay to
#: the very loop this module exists to explain the delay in.
_last_cpu: Optional[Tuple[float, float]] = None  # (monotonic_sec, cpu_seconds)


def _read(path: str) -> Optional[str]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read().strip()
    except OSError:
        return None


def _cpu_seconds_used() -> Tuple[Optional[float], str]:
    """Cumulative CPU seconds this cgroup has burned, v2 then v1."""
    stat = _read(_CG2_CPU_STAT)
    if stat:
        for line in stat.splitlines():
            if line.startswith("usage_usec "):
                try:
                    return float(line.split()[1]) / 1e6, "cgroup_v2"
                except (ValueError, IndexError):
                    break
    raw = _read(_CG1_CPU_USAGE)
    if raw:
        try:
            return float(raw) / 1e9, "cgroup_v1"
        except ValueError:
            pass
    return None, "no_cgroup_cpu_accounting"


def _memory() -> Dict[str, Any]:
    used = _read(_CG2_MEM_CURRENT)
    limit = _read(_CG2_MEM_MAX)
    source = "cgroup_v2"
    if used is None:
        used, limit, source = _read(_CG1_MEM_USAGE), _read(_CG1_MEM_LIMIT), "cgroup_v1"
    out: Dict[str, Any] = {"source": source, "used_mb": None, "limit_mb": None,
                           "used_pct": None, "reason": ""}
    if used is None:
        out["source"] = "unavailable"
        out["reason"] = "no cgroup memory accounting readable from this process"
        return out
    try:
        used_b = float(used)
    except ValueError:
        out["source"] = "unavailable"
        out["reason"] = f"unparseable memory reading: {used!r}"
        return out
    out["used_mb"] = round(used_b / 1024 / 1024, 1)
    # "max" (v2) and a near-2^63 sentinel (v1) both mean *no limit set* — which
    # is a real and different state from a limit we could not read.
    if limit and limit != "max":
        try:
            limit_b = float(limit)
        except ValueError:
            limit_b = 0.0
        if 0 < limit_b < _CG1_UNLIMITED:
            out["limit_mb"] = round(limit_b / 1024 / 1024, 1)
            out["used_pct"] = round(100.0 * used_b / limit_b, 1)
            return out
    out["reason"] = "no memory limit set on this container — bounded by the host"
    return out


def sample(data_dir: str = "data") -> Dict[str, Any]:
    """One reading of what this container is getting from the box.

    Cheap by construction: a handful of small ``/sys`` and ``/proc`` reads and
    one ``statvfs``. No network, no lock, nothing that can block the loop it is
    called from — this runs on the snapshot-writer's cadence and the whole
    point of it is explaining that loop's delays, so it must not add any.
    """
    global _last_cpu

    from config import (
        INDICATOR_CACHE_CONTENT_KEY,
        SCAN_CYCLE_KILL_SEC,
        SCAN_CYCLE_WARN_SEC,
        SCAN_EXECUTOR_WORKERS,
        STRATEGY_EDGE_FLUSH_SEC,
        cpu_budget,
    )

    now = time.monotonic()
    cpu_now, cpu_source = _cpu_seconds_used()

    quota = cpu_budget()
    host_cores = os.cpu_count()

    cpu: Dict[str, Any] = {
        "source": cpu_source,
        "quota_cores": round(quota, 2),
        "host_cores": host_cores,
        "quota_is_host": host_cores is not None and abs(quota - float(host_cores)) < 0.01,
        "cores_used": None,
        "pct_of_quota": None,
        "window_sec": None,
        "reason": "",
    }

    if cpu_now is None:
        cpu["reason"] = (
            "no cgroup CPU accounting is readable from this process — this is a "
            "statement about the container, not a measurement of idleness"
        )
    elif _last_cpu is None:
        cpu["reason"] = (
            "first sample since boot — a rate needs two readings, and the next "
            "call has one"
        )
        _last_cpu = (now, cpu_now)
    else:
        prev_t, prev_cpu = _last_cpu
        elapsed = now - prev_t
        burned = cpu_now - prev_cpu
        # A counter that went backwards means the container was replaced under
        # us. Refuse the reading and re-seed rather than publishing a negative
        # or a wildly large one: a wrong number here reads as a load spike.
        if elapsed <= 0 or burned < 0:
            cpu["reason"] = "CPU counter reset — re-seeding, next sample measures"
        else:
            cores = burned / elapsed
            cpu["cores_used"] = round(cores, 2)
            cpu["window_sec"] = round(elapsed, 1)
            if quota > 0:
                cpu["pct_of_quota"] = round(100.0 * cores / quota, 1)
        _last_cpu = (now, cpu_now)

    load: Dict[str, Any] = {"one": None, "five": None, "fifteen": None, "reason": ""}
    try:
        one, five, fifteen = os.getloadavg()
        load.update(one=round(one, 2), five=round(five, 2), fifteen=round(fifteen, 2))
    except (OSError, AttributeError):
        load["reason"] = "load average unavailable on this platform"

    disk: Dict[str, Any] = {"path": data_dir, "used_pct": None, "free_gb": None,
                            "total_gb": None, "reason": ""}
    try:
        usage = shutil.disk_usage(data_dir)
        disk["total_gb"] = round(usage.total / 1024**3, 1)
        disk["free_gb"] = round(usage.free / 1024**3, 1)
        disk["used_pct"] = round(100.0 * usage.used / usage.total, 1) if usage.total else None
    except OSError as exc:
        disk["reason"] = f"{type(exc).__name__}: {exc}"

    return {
        "cpu": cpu,
        "memory": _memory(),
        "load": load,
        "disk": disk,
        # The values the RUNNING process is using. A deploy that did not take
        # is otherwise indistinguishable from a fix that did not work, and the
        # owner has no way to tell them apart from a dashboard.
        "effective_config": {
            "cpu_budget": round(quota, 2),
            "scan_executor_workers": SCAN_EXECUTOR_WORKERS,
            "indicator_cache_content_key": bool(INDICATOR_CACHE_CONTENT_KEY),
            "scan_cycle_warn_sec": SCAN_CYCLE_WARN_SEC,
            "scan_cycle_kill_sec": SCAN_CYCLE_KILL_SEC,
            "strategy_edge_flush_sec": STRATEGY_EDGE_FLUSH_SEC,
        },
        "sampled_at": time.time(),
    }
