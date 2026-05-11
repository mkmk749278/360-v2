#!/usr/bin/env python3
"""VPS Health Agent — 360-Crypto-Scalping V2.

Runs on the VPS HOST (not inside Docker) to diagnose system resources,
Docker container health, engine heartbeat, and network reachability.
Reports results to the Telegram admin chat.

No host-side pip installs required — uses only Python stdlib + /proc + docker CLI.

Schedule via cron (see scripts/install_health_agent.sh):
    */15 * * * *   cd /opt/360-v2 && python3 scripts/vps_health_agent.py
    0 0,6,12,18 * * *  cd /opt/360-v2 && python3 scripts/vps_health_agent.py --full

Usage:
    vps_health_agent.py              — alert-only: Telegram only if issues found
    vps_health_agent.py --full       — always send full report to Telegram
    vps_health_agent.py --stdout     — print to stdout, no Telegram
    vps_health_agent.py --full --stdout  — full report to stdout
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Container names (match docker-compose.yml) ─────────────────────────────────
ENGINE_CONTAINER = "360scalp-v2-engine"
REDIS_CONTAINER  = "360scalp-v2-redis"

# ── Thresholds (all overridable via env vars) ───────────────────────────────
CPU_WARN_PCT    = float(os.getenv("HEALTH_CPU_WARN",          "80"))
CPU_CRIT_PCT    = float(os.getenv("HEALTH_CPU_CRIT",          "92"))
RAM_WARN_PCT    = float(os.getenv("HEALTH_RAM_WARN",          "80"))
RAM_CRIT_PCT    = float(os.getenv("HEALTH_RAM_CRIT",          "92"))
DISK_WARN_PCT   = float(os.getenv("HEALTH_DISK_WARN",         "80"))
DISK_CRIT_PCT   = float(os.getenv("HEALTH_DISK_CRIT",         "90"))
SWAP_WARN_PCT   = float(os.getenv("HEALTH_SWAP_WARN",         "50"))
HB_MAX_AGE_S    = int(os.getenv("HEALTH_HEARTBEAT_MAX_AGE",   "150"))
NET_TIMEOUT_S   = int(os.getenv("HEALTH_NET_TIMEOUT",         "8"))
LOG_ERROR_WARN  = int(os.getenv("HEALTH_LOG_ERROR_WARN",      "5"))   # errors in last 15m = WARN
LOG_ERROR_CRIT  = int(os.getenv("HEALTH_LOG_ERROR_CRIT",      "20"))  # errors in last 15m = CRIT

# ── Network reachability targets ────────────────────────────────────────────
NETWORK_TARGETS = [
    ("Binance REST",    "https://api.binance.com/api/v3/ping"),
    ("Binance Futures", "https://fapi.binance.com/fapi/v1/ping"),
    ("Telegram API",    "https://api.telegram.org"),
]

# ── Status levels ────────────────────────────────────────────────────────────────
OK   = "OK"
WARN = "WARN"
CRIT = "CRIT"
INFO = "INFO"
ICON = {OK: "✅", WARN: "⚠️", CRIT: "❌", INFO: "ℹ️"}


# ────────────────────────────────────────────────────────────────────────────────
# Data model
# ────────────────────────────────────────────────────────────────────────────────

@dataclass
class Check:
    label: str
    status: str
    detail: str


@dataclass
class Report:
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    )
    sections: dict[str, list[Check]] = field(default_factory=dict)

    def add(self, section: str, check: Check) -> None:
        self.sections.setdefault(section, []).append(check)

    @property
    def worst(self) -> str:
        all_checks = [c for checks in self.sections.values() for c in checks]
        for level in (CRIT, WARN):
            if any(c.status == level for c in all_checks):
                return level
        return OK

    @property
    def has_issues(self) -> bool:
        return self.worst in (CRIT, WARN)

    def format_telegram(self, full: bool = False) -> str:
        overall = self.worst
        header = f"{ICON[overall]} *VPS Health — 360 Scalping V2*\n`{self.generated_at}`"

        if not full and not self.has_issues:
            return f"{header}\n\nAll systems nominal ✓"

        lines = [header, ""]
        for section, checks in self.sections.items():
            visible = [
                c for c in checks
                if full or c.status in (CRIT, WARN)
            ]
            if not visible:
                continue
            lines.append(f"*{section}*")
            for c in visible:
                lines.append(f"  {ICON[c.status]} {c.label}: {c.detail}")
            lines.append("")

        return "\n".join(lines).rstrip()

    def format_stdout(self, full: bool = False) -> str:
        lines = [f"VPS Health Report — {self.generated_at}", "=" * 52]
        for section, checks in self.sections.items():
            visible = [c for c in checks if full or c.status in (CRIT, WARN, INFO)]
            if not visible:
                if full:
                    lines.append(f"\n[{section}] (all OK)")
                continue
            lines.append(f"\n[{section}]")
            for c in visible:
                tag = {OK: "OK  ", WARN: "WARN", CRIT: "CRIT", INFO: "INFO"}.get(c.status, c.status)
                lines.append(f"  [{tag}] {c.label}: {c.detail}")
        return "\n".join(lines)


# ────────────────────────────────────────────────────────────────────────────────
# .env parser (stdlib only — no python-dotenv needed on the host)
# ────────────────────────────────────────────────────────────────────────────────

def _load_env(env_path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not env_path.is_file():
        return result
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key   = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value:
            result[key] = value
    return result


# ────────────────────────────────────────────────────────────────────────────────
# System checks  (/proc — works on any Linux VPS, zero dependencies)
# ────────────────────────────────────────────────────────────────────────────────

def _read_proc(path: str) -> str:
    try:
        return Path(path).read_text()
    except OSError:
        return ""


def check_cpu(report: Report) -> None:
    """Sample CPU usage over 1 second from /proc/stat."""
    def _snapshot() -> tuple[int, int]:
        line = _read_proc("/proc/stat").splitlines()[0]
        vals = list(map(int, line.split()[1:]))
        # iowait is vals[4] when present; idle is vals[3]
        idle  = vals[3] + (vals[4] if len(vals) > 4 else 0)
        total = sum(vals)
        return idle, total

    idle1, total1 = _snapshot()
    time.sleep(1)
    idle2, total2 = _snapshot()

    d_total = total2 - total1
    d_idle  = idle2  - idle1
    pct = 100.0 * (1 - d_idle / d_total) if d_total > 0 else 0.0

    load_parts = _read_proc("/proc/loadavg").split()
    load_str   = "/".join(load_parts[:3]) if len(load_parts) >= 3 else "?"

    status = CRIT if pct >= CPU_CRIT_PCT else WARN if pct >= CPU_WARN_PCT else OK
    report.add("System", Check("CPU usage", status,
        f"{pct:.1f}%  |  load avg {load_str}"))


def check_memory(report: Report) -> None:
    """Parse /proc/meminfo for RAM and swap metrics."""
    raw = _read_proc("/proc/meminfo")
    mem: dict[str, int] = {}
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            try:
                mem[parts[0].rstrip(":")] = int(parts[1])
            except ValueError:
                pass

    def _mb(kb: int) -> str:
        return f"{kb // 1024} MB"

    total = mem.get("MemTotal", 0)
    avail = mem.get("MemAvailable", 0)
    used  = total - avail
    pct   = 100.0 * used / total if total > 0 else 0.0

    status = CRIT if pct >= RAM_CRIT_PCT else WARN if pct >= RAM_WARN_PCT else OK
    report.add("System", Check("RAM", status,
        f"{pct:.1f}%  ({_mb(used)} / {_mb(total)})"))

    swap_total = mem.get("SwapTotal", 0)
    if swap_total > 0:
        swap_used = swap_total - mem.get("SwapFree", 0)
        swap_pct  = 100.0 * swap_used / swap_total
        swap_status = WARN if swap_pct >= SWAP_WARN_PCT else OK
        report.add("System", Check("Swap", swap_status,
            f"{swap_pct:.1f}%  ({_mb(swap_used)} / {_mb(swap_total)})"))


def check_disk(report: Report) -> None:
    """Check disk usage on all non-virtual mounts via df."""
    try:
        out = subprocess.check_output(
            ["df", "-h", "--output=target,pcent,used,size",
             "-x", "tmpfs", "-x", "devtmpfs", "-x", "overlay"],
            text=True, timeout=5
        )
    except Exception as exc:
        report.add("System", Check("Disk", WARN, f"df failed: {exc}"))
        return

    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 4 or not parts[1].endswith("%"):
            continue
        mount, pct_str, used, size = parts[0], parts[1], parts[2], parts[3]
        pct    = float(pct_str.rstrip("%"))
        status = CRIT if pct >= DISK_CRIT_PCT else WARN if pct >= DISK_WARN_PCT else OK
        report.add("System", Check(f"Disk {mount}", status,
            f"{pct:.0f}%  ({used} / {size})"))


def check_uptime(report: Report) -> None:
    raw = _read_proc("/proc/uptime").split()
    if raw:
        secs  = float(raw[0])
        days  = int(secs // 86400)
        hours = int((secs % 86400) // 3600)
        mins  = int((secs % 3600) // 60)
        report.add("System", Check("Uptime", INFO, f"{days}d {hours}h {mins}m"))


# ────────────────────────────────────────────────────────────────────────────────
# Docker checks
# ────────────────────────────────────────────────────────────────────────────────

def _docker_ok() -> bool:
    try:
        subprocess.check_output(["docker", "info"], timeout=6, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def _docker_inspect(container: str) -> Optional[dict]:
    try:
        raw = subprocess.check_output(
            ["docker", "inspect", container],
            text=True, timeout=10, stderr=subprocess.DEVNULL
        )
        data = json.loads(raw)
        return data[0] if data else None
    except Exception:
        return None


def check_container(report: Report, container: str) -> bool:
    """Inspect a container and add its status to the Docker section. Returns True if running."""
    info = _docker_inspect(container)
    if info is None:
        report.add("Docker", Check(container, CRIT, "not found / Docker unreachable"))
        return False

    state        = info.get("State", {})
    running      = state.get("Running", False)
    status_str   = state.get("Status", "unknown")
    restart_cnt  = state.get("RestartCount", 0)
    health_info  = state.get("Health", {})
    health_st    = health_info.get("Status", "") if health_info else ""

    if not running:
        report.add("Docker", Check(container, CRIT,
            f"not running  (status={status_str}, restarts={restart_cnt})"))
        return False

    parts = ["running"]
    if health_st:
        parts.append(f"health={health_st}")
    if restart_cnt > 0:
        parts.append(f"restarts={restart_cnt}")

    status = (
        CRIT if health_st == "unhealthy" else
        WARN if health_st == "starting" or restart_cnt >= 3 else
        OK
    )
    report.add("Docker", Check(container, status, "  |  ".join(parts)))
    return running


def check_engine_heartbeat(report: Report) -> None:
    """Read scanner heartbeat age via docker exec (no volume mount needed)."""
    try:
        raw = subprocess.check_output(
            ["docker", "exec", ENGINE_CONTAINER, "python3", "-c",
             "import os,time; p='/app/data/scanner_heartbeat';"
             "a=int(time.time()-os.path.getmtime(p)) if os.path.isfile(p) else -1;"
             "print(a)"],
            text=True, timeout=10, stderr=subprocess.DEVNULL
        ).strip()
        age = int(raw)
    except Exception as exc:
        report.add("Engine", Check("Heartbeat", WARN, f"read failed: {exc}"))
        return

    if age < 0:
        report.add("Engine", Check("Heartbeat", WARN,
            "file missing — engine may still be seeding pairs"))
    elif age > HB_MAX_AGE_S:
        report.add("Engine", Check("Heartbeat", CRIT,
            f"STALE — {age}s old  (max {HB_MAX_AGE_S}s)"))
    else:
        report.add("Engine", Check("Heartbeat", OK,
            f"{age}s old — scanner loop alive"))


def check_engine_logs(report: Report) -> None:
    """Tail last 15 minutes of engine logs and count error lines."""
    try:
        # stderr=STDOUT because the engine writes to stderr inside the container
        out = subprocess.check_output(
            ["docker", "logs", "--since", "15m", ENGINE_CONTAINER],
            text=True, timeout=15, stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as exc:
        out = exc.output or ""
    except Exception as exc:
        report.add("Engine", Check("Logs (15m)", WARN, f"could not read: {exc}"))
        return

    lines    = out.splitlines()
    errors   = [l for l in lines if " ERROR "    in l or " CRITICAL " in l]
    warnings = [l for l in lines if " WARNING "   in l]

    if len(errors) >= LOG_ERROR_CRIT:
        snippet = errors[-1][-100:] if errors else ""
        report.add("Engine", Check("Logs (15m)", CRIT,
            f"{len(errors)} errors, {len(warnings)} warnings — last: {snippet}"))
    elif len(errors) >= LOG_ERROR_WARN:
        report.add("Engine", Check("Logs (15m)", WARN,
            f"{len(errors)} errors, {len(warnings)} warnings"))
    else:
        report.add("Engine", Check("Logs (15m)", OK,
            f"clean — {len(errors)} errors, {len(warnings)} warnings in {len(lines)} lines"))


def check_engine_memory(report: Report) -> None:
    """Pull engine container memory via docker stats (single snapshot)."""
    try:
        raw = subprocess.check_output(
            ["docker", "stats", "--no-stream", "--format",
             "{{.MemUsage}}|{{.MemPerc}}", ENGINE_CONTAINER],
            text=True, timeout=12, stderr=subprocess.DEVNULL
        ).strip()
        usage, perc_str = raw.split("|")
        pct    = float(perc_str.strip().rstrip("%"))
        status = WARN if pct > 80 else OK
        report.add("Engine", Check("Container RAM", status,
            f"{usage.strip()}  ({perc_str.strip()})"))
    except Exception as exc:
        report.add("Engine", Check("Container RAM", INFO, f"unavailable: {exc}"))


# ────────────────────────────────────────────────────────────────────────────────
# Network reachability
# ────────────────────────────────────────────────────────────────────────────────

def check_network(report: Report) -> None:
    for name, url in NETWORK_TARGETS:
        try:
            t0  = time.monotonic()
            req = urllib.request.Request(url, headers={"User-Agent": "360-health-agent/1.0"})
            with urllib.request.urlopen(req, timeout=NET_TIMEOUT_S) as resp:
                resp.read()
            ms     = int((time.monotonic() - t0) * 1000)
            status = WARN if ms > 3000 else OK
            report.add("Network", Check(name, status, f"{ms} ms"))
        except urllib.error.URLError as exc:
            report.add("Network", Check(name, CRIT, f"unreachable — {exc.reason}"))
        except Exception as exc:
            report.add("Network", Check(name, CRIT, f"error: {exc}"))


# ────────────────────────────────────────────────────────────────────────────────
# Telegram sender
# ────────────────────────────────────────────────────────────────────────────────

def _send_telegram(token: str, chat_id: str, text: str) -> bool:
    url     = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id":                  chat_id,
        "text":                     text,
        "parse_mode":               "Markdown",
        "disable_web_page_preview": True,
    }).encode()
    try:
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
        return True
    except Exception as exc:
        print(f"[ERROR] Telegram send failed: {exc}", file=sys.stderr)
        return False


# ────────────────────────────────────────────────────────────────────────────────
# Entry point
# ────────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="VPS Health Agent — 360-Crypto-Scalping V2"
    )
    parser.add_argument("--full",   action="store_true",
        help="Always send a full report (default: alert-only)")
    parser.add_argument("--stdout", action="store_true",
        help="Print report to stdout instead of sending to Telegram")
    args = parser.parse_args()

    # Resolve .env relative to this script's parent directory
    env      = _load_env(Path(__file__).resolve().parent.parent / ".env")
    tg_token = env.get("TELEGRAM_BOT_TOKEN")    or os.getenv("TELEGRAM_BOT_TOKEN",    "")
    tg_chat  = env.get("TELEGRAM_ADMIN_CHAT_ID") or os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")

    # ── Run all checks ─────────────────────────────────────────────────────────
    report = Report()

    check_cpu(report)
    check_memory(report)
    check_disk(report)
    check_uptime(report)

    if _docker_ok():
        engine_up = check_container(report, ENGINE_CONTAINER)
        check_container(report, REDIS_CONTAINER)
        if engine_up:
            check_engine_heartbeat(report)
            check_engine_logs(report)
            check_engine_memory(report)
    else:
        report.add("Docker", Check("Docker daemon", CRIT, "not reachable from this user"))

    check_network(report)

    # ── Output ──────────────────────────────────────────────────────────────
    if args.stdout:
        if args.full or report.has_issues:
            print(report.format_stdout(full=args.full))
        else:
            print(f"[{report.generated_at}] All systems nominal.")
        return 1 if report.has_issues else 0

    # Telegram mode
    if not tg_token or not tg_chat:
        # Graceful fallback: print to stdout if no Telegram config found
        print(report.format_stdout(full=args.full))
        if not tg_token:
            print("[WARN] TELEGRAM_BOT_TOKEN not set — printing to stdout", file=sys.stderr)
        return 1 if report.has_issues else 0

    if args.full or report.has_issues:
        msg = report.format_telegram(full=args.full)
        if not _send_telegram(tg_token, tg_chat, msg):
            # Telegram failed — print locally so the cron log captures it
            print(report.format_stdout(full=args.full))
            return 1

    return 1 if report.has_issues else 0


if __name__ == "__main__":
    sys.exit(main())
