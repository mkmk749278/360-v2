#!/usr/bin/env python3
"""On-box autonomous supervisor — the minutes-level layer of the ops pyramid.

Runs as its own container (see ``watchdog`` service in docker-compose.yml)
and closes the gap between the container healthcheck (seconds, shallow) and
the hourly GitHub-Actions liveness watch (slow, needs GitHub to be up):
every ``WATCHDOG_INTERVAL_SEC`` it reads the engine's own status files on
the shared data volume plus the Docker API over ``/var/run/docker.sock``,
pages the owner's phone via Telegram (scripts/notify_telegram.py), and takes
**risk-reducing remediation** on a graduated ladder.

Authority doctrine (docs/AUTONOMOUS_OPS.md — non-negotiable):

* The watchdog may only take actions that REDUCE risk: page, restart a
  wedged container, prune disk, ENGAGE the kill switch.
* It must never take an action that increases exposure — it never
  disengages the kill switch, never resets a circuit breaker, never
  re-enables auto-trade.  Recovery of trading is always the owner.

Checks → actions:

1.  Container states (engine/api/signing/redis): not-running or unhealthy
    → page.  First-line restart of *unhealthy* containers belongs to the
    autoheal sidecar; the watchdog is the escalation path.
2.  Scanner heartbeat: stale beyond ``WATCHDOG_HEARTBEAT_STALE_SEC`` while
    the container still reports running → restart the engine (the wedge
    class Docker's own healthcheck missed), bounded by a restart budget.
3.  Pricing freshness (audit F-07): an OPEN position whose 1m candle is
    stale AND absent from the mark feed is BLIND — page immediately; if
    still blind after ``WATCHDOG_BLIND_ESCALATION_SEC``, restart the engine
    (a boot re-seeds every active symbol's candles — the manual fix for
    MVLLUSDT, automated).
4.  Circuit-breaker trips: page on the trip transition (redundant with the
    engine's own Telegram alert BY DESIGN — the watchdog's page survives an
    engine whose alert path is down).
5.  Disk: page at ``WATCHDOG_DISK_WARN_PCT``; at ``WATCHDOG_DISK_CRIT_PCT``
    prune dangling images + stopped containers + build cache, then page
    with the space recovered.
6.  Memory: page when MemAvailable falls under ``WATCHDOG_MEM_WARN_PCT``.
7.  Escalation: engine restart budget exhausted and still broken → ENGAGE
    the global kill switch via the API (owner-tier static token) and page
    CRITICAL.  Resting SL/TP orders on Binance keep protecting open
    positions; the switch only halts NEW dispatch — strictly risk-reducing.
8.  Dead-man ping: hit ``HEALTHCHECKS_PING_URL`` at the end of every loop
    so an external service (healthchecks.io) pages when this box — or this
    watchdog — goes dark.  The one failure mode an on-box supervisor cannot
    see is its own host dying.

Every page and every action is appended to ``data/watchdog_audit.jsonl``.
Page dedupe: one page per finding key per ``WATCHDOG_PAGE_COOLDOWN_SEC``,
plus a one-shot recovery page when a previously-paged key clears.

Cost discipline: local files + the local Docker socket only; the only
network egress is Telegram/healthchecks pings and (rare) the kill-switch
POST to the API container.  No Firestore, no Binance, no per-tick anything.
"""

from __future__ import annotations

import http.client
import json
import os
import shutil
import socket
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import notify_telegram  # noqa: E402  — sibling module, stdlib-only


# ---------------------------------------------------------------------------
# Env-tunable configuration (read at import; the container restarts on
# .env changes via deploy.sh, same as every other service).
# ---------------------------------------------------------------------------

def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, "") or default)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, "") or default)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


DATA_DIR = os.environ.get("ENGINE_DATA_DIR", "/app/data")
DOCKER_SOCK = os.environ.get("WATCHDOG_DOCKER_SOCK", "/var/run/docker.sock")
INTERVAL_SEC = _env_int("WATCHDOG_INTERVAL_SEC", 60)
PAGE_COOLDOWN_SEC = _env_int("WATCHDOG_PAGE_COOLDOWN_SEC", 1800)

HEARTBEAT_STALE_SEC = _env_int("WATCHDOG_HEARTBEAT_STALE_SEC", 900)
BLIND_ESCALATION_SEC = _env_int("WATCHDOG_BLIND_ESCALATION_SEC", 600)
PRICING_FILE_MAX_AGE_SEC = _env_int("PRICING_FILE_MAX_AGE_SEC", 600)

DISK_WARN_PCT = _env_float("WATCHDOG_DISK_WARN_PCT", 85.0)
DISK_CRIT_PCT = _env_float("WATCHDOG_DISK_CRIT_PCT", 92.0)
MEM_WARN_PCT = _env_float("WATCHDOG_MEM_WARN_PCT", 10.0)

RESTART_ENABLED = _env_bool("WATCHDOG_RESTART_ENABLED", True)
MAX_ENGINE_RESTARTS_PER_HOUR = _env_int("WATCHDOG_MAX_ENGINE_RESTARTS_PER_HOUR", 3)
KILLSWITCH_ENABLED = _env_bool("WATCHDOG_KILLSWITCH_ENABLED", True)
# Post-(re)start warmup window: the heartbeat/pricing files keep their OLD
# mtime on the data volume across restarts, and a boot (REST-seeding 75 pairs)
# takes minutes.  Judging staleness during this window is what turned one
# wedge into a 3-restarts-in-3-minutes budget burn + kill switch on
# 2026-07-13.  While engine uptime < grace, staleness ages are floored at the
# container start and the heartbeat-restart action is disabled.
BOOT_GRACE_SEC = _env_int("WATCHDOG_BOOT_GRACE_SEC", 600)

HEALTHCHECKS_PING_URL = os.environ.get("HEALTHCHECKS_PING_URL", "").strip()

ENGINE_CONTAINER = "360scalp-v2-engine"
WATCHED_CONTAINERS = ["360scalp-v2-engine", "360scalp-v2-redis", "360scalp-v2-signing"]
if _env_bool("API_PROCESS_ISOLATED", False):
    WATCHED_CONTAINERS.append("360scalp-v2-api")

STATE_PATH = os.path.join(DATA_DIR, "watchdog_state.json")
AUDIT_PATH = os.path.join(DATA_DIR, "watchdog_audit.jsonl")
WATCHDOG_HEARTBEAT_PATH = os.environ.get(
    "WATCHDOG_HEARTBEAT_PATH", "/tmp/watchdog_heartbeat"
)


def _kill_switch_url() -> str:
    override = os.environ.get("WATCHDOG_KILL_SWITCH_URL", "").strip()
    if override:
        return override
    host = "api" if _env_bool("API_PROCESS_ISOLATED", False) else "engine"
    port = os.environ.get("API_PORT", "8000").strip() or "8000"
    return f"http://{host}:{port}/api/kill-switch"


# ---------------------------------------------------------------------------
# Findings — pure data so check logic is unit-testable without Docker.
# ---------------------------------------------------------------------------

@dataclass
class Finding:
    """One detected problem. ``key`` dedupes pages across loops."""

    key: str
    severity: str  # "warn" | "critical"
    message: str


@dataclass
class WatchdogState:
    """Cross-loop memory, persisted to the data volume so restarts of the
    watchdog itself don't re-page every open episode or reset the engine
    restart budget."""

    last_paged_at: Dict[str, float] = field(default_factory=dict)
    active_keys: List[str] = field(default_factory=list)
    engine_restarts: List[float] = field(default_factory=list)
    blind_since: Dict[str, float] = field(default_factory=dict)
    kill_switch_engaged_by_watchdog: bool = False

    @classmethod
    def load(cls, path: str = STATE_PATH) -> "WatchdogState":
        try:
            with open(path) as fh:
                raw = json.load(fh)
            return cls(
                last_paged_at=dict(raw.get("last_paged_at", {})),
                active_keys=list(raw.get("active_keys", [])),
                engine_restarts=list(raw.get("engine_restarts", [])),
                blind_since=dict(raw.get("blind_since", {})),
                kill_switch_engaged_by_watchdog=bool(
                    raw.get("kill_switch_engaged_by_watchdog", False)
                ),
            )
        except Exception:
            return cls()

    def save(self, path: str = STATE_PATH) -> None:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            tmp = path + ".tmp"
            with open(tmp, "w") as fh:
                json.dump(
                    {
                        "last_paged_at": self.last_paged_at,
                        "active_keys": self.active_keys,
                        "engine_restarts": self.engine_restarts,
                        "blind_since": self.blind_since,
                        "kill_switch_engaged_by_watchdog": self.kill_switch_engaged_by_watchdog,
                    },
                    fh,
                )
            os.replace(tmp, path)
        except Exception:
            pass  # state is an optimisation; losing it re-pages, never hides


def audit(event: str, detail: Dict[str, Any]) -> None:
    """Append one audit record. Best-effort — auditing never blocks acting."""
    try:
        os.makedirs(os.path.dirname(AUDIT_PATH), exist_ok=True)
        with open(AUDIT_PATH, "a") as fh:
            fh.write(json.dumps({"ts": time.time(), "event": event, **detail}) + "\n")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Docker API over the Unix socket — stdlib only.
# ---------------------------------------------------------------------------

class _UnixHTTPConnection(http.client.HTTPConnection):
    def __init__(self, sock_path: str, timeout: float = 10.0) -> None:
        super().__init__("localhost", timeout=timeout)
        self._sock_path = sock_path

    def connect(self) -> None:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(self.timeout)
        s.connect(self._sock_path)
        self.sock = s


def docker_request(
    method: str, path: str, sock_path: str = DOCKER_SOCK, timeout: float = 35.0
) -> Optional[Dict[str, Any]]:
    """One Docker-API call. Returns parsed JSON (or {} for empty bodies),
    None on any failure — callers treat None as 'Docker unreachable'."""
    conn = _UnixHTTPConnection(sock_path, timeout=timeout)
    try:
        conn.request(method, path, headers={"Host": "docker"})
        resp = conn.getresponse()
        body = resp.read()
        if resp.status >= 400:
            return None
        if not body:
            return {}
        return json.loads(body)
    except Exception:
        return None
    finally:
        try:
            conn.close()
        except Exception:
            pass


def _parse_docker_time(value: Any) -> float:
    """Docker RFC3339 timestamp (nanosecond precision) → epoch seconds.

    Returns 0.0 for missing/zero ("0001-01-01...") /unparseable values so
    callers can treat 0.0 as "unknown — apply no floor".
    """
    try:
        s = str(value or "").strip()
        if not s or s.startswith("0001-"):
            return 0.0
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        if "." in s:
            head, rest = s.split(".", 1)
            frac = ""
            tz = ""
            for i, ch in enumerate(rest):
                if ch.isdigit():
                    frac += ch
                else:
                    tz = rest[i:]
                    break
            s = head + "." + (frac[:6] or "0") + (tz or "+00:00")
        from datetime import datetime

        return datetime.fromisoformat(s).timestamp()
    except Exception:
        return 0.0


def container_state(name: str) -> Dict[str, Any]:
    """{'running', 'status', 'health', 'restart_count', 'started_at'}"""
    info = docker_request("GET", f"/containers/{name}/json")
    if not info:
        return {
            "running": False,
            "status": "unreachable",
            "health": "unknown",
            "restart_count": 0,
            "started_at": 0.0,
        }
    state = info.get("State", {})
    health = (state.get("Health") or {}).get("Status", "none")
    return {
        "running": bool(state.get("Running", False)),
        "status": state.get("Status", "unknown"),
        "health": health,
        "restart_count": int(info.get("RestartCount", 0)),
        "started_at": _parse_docker_time(state.get("StartedAt")),
    }


def restart_container(name: str) -> bool:
    # 30s stop grace — the engine flushes state files + closes WS cleanly.
    return docker_request("POST", f"/containers/{name}/restart?t=30", timeout=60.0) is not None


def prune_disk() -> Dict[str, Any]:
    """Reclaim space: dangling images, stopped containers, build cache.
    Never touches running containers or named volumes."""
    reclaimed = 0
    for path in ("/images/prune", "/containers/prune", "/build/prune"):
        res = docker_request("POST", path, timeout=120.0)
        if res:
            reclaimed += int(res.get("SpaceReclaimed", 0) or 0)
    return {"space_reclaimed_bytes": reclaimed}


# ---------------------------------------------------------------------------
# Checks — pure functions over snapshots, unit-testable.
# ---------------------------------------------------------------------------

def check_containers(states: Dict[str, Dict[str, Any]]) -> List[Finding]:
    findings: List[Finding] = []
    for name, st in states.items():
        if not st["running"]:
            findings.append(
                Finding(
                    key=f"container_down:{name}",
                    severity="critical",
                    message=(
                        f"container {name} is NOT RUNNING (status={st['status']}) — "
                        "restart:always should recover it; if this persists the "
                        "process is crash-looping."
                    ),
                )
            )
        elif st["health"] == "unhealthy":
            findings.append(
                Finding(
                    key=f"container_unhealthy:{name}",
                    severity="warn",
                    message=(
                        f"container {name} reports UNHEALTHY — autoheal will "
                        "restart it; escalating page in case it flaps."
                    ),
                )
            )
    return findings


def check_scanner_heartbeat(
    data_dir: str = DATA_DIR,
    stale_sec: int = HEARTBEAT_STALE_SEC,
    now: Optional[float] = None,
    min_ts: float = 0.0,
) -> List[Finding]:
    """Wedge the container healthcheck missed: heartbeat old but container up.

    The scanner publishes its heartbeat every cycle *including breaker
    halts*, so a protective halt never trips this (that disambiguation is
    check_circuit_breaker's job).

    ``min_ts`` (the engine container's StartedAt) floors the age: the file's
    mtime persists on the data volume across restarts, and an engine cannot
    have been wedged for longer than it has been alive.
    """
    now = now or time.time()
    p = os.path.join(data_dir, "scanner_heartbeat")
    if not os.path.exists(p):
        return []  # pre-first-cycle; the container healthcheck owns this window
    age = int(now - max(os.path.getmtime(p), min_ts))
    if age > stale_sec:
        return [
            Finding(
                key="scanner_heartbeat_stale",
                severity="critical",
                message=(
                    f"scanner heartbeat is {age}s old (> {stale_sec}s) — the scan "
                    "loop is wedged (not crashed, not a breaker halt)."
                ),
            )
        ]
    return []


def check_pricing_freshness(
    data_dir: str = DATA_DIR,
    file_max_age_sec: int = PRICING_FILE_MAX_AGE_SEC,
    now: Optional[float] = None,
    min_ts: float = 0.0,
) -> List[Finding]:
    """Audit F-07 at minutes cadence — see monitor_heartbeat.py for the class.

    ``min_ts`` floors the snapshot age at the engine's StartedAt (same
    persisted-mtime-across-restart honesty as the heartbeat check).
    """
    now = now or time.time()
    fp = os.path.join(data_dir, "pricing_freshness.json")
    if not os.path.exists(fp):
        return []
    try:
        with open(fp) as fh:
            snap = json.load(fh)
    except Exception:
        return [
            Finding(
                key="pricing_freshness_unreadable",
                severity="warn",
                message="pricing_freshness.json is unreadable/corrupt.",
            )
        ]
    findings: List[Finding] = []
    age = int(now - max(float(snap.get("updated_at", 0)), min_ts))
    if age > file_max_age_sec:
        findings.append(
            Finding(
                key="pricing_freshness_stale_file",
                severity="critical",
                message=(
                    f"pricing-freshness snapshot is {age}s old (> {file_max_age_sec}s) "
                    "— the trade monitor stopped publishing; its SL/TP backstop "
                    "loop may be wedged."
                ),
            )
        )
        return findings
    for p in snap.get("positions", []):
        if p.get("blind"):
            findings.append(
                Finding(
                    key=f"blind_position:{p.get('signal_id')}",
                    severity="critical",
                    message=(
                        f"open position {p.get('symbol')} ({p.get('status')}, "
                        f"{p.get('signal_id')}) is priced off a fully stale source "
                        f"(1m kline age {p.get('kline_age_sec')}s, no mark price) — "
                        "SL/TP/trailing protection is BLIND (F-07)."
                    ),
                )
            )
    return findings


def check_circuit_breaker(
    data_dir: str = DATA_DIR, now: Optional[float] = None
) -> List[Finding]:
    now = now or time.time()
    bp = os.path.join(data_dir, "circuit_breaker_status.json")
    if not os.path.exists(bp):
        return []
    try:
        with open(bp) as fh:
            cb = json.load(fh)
    except Exception:
        return []
    if cb.get("tripped"):
        # Key includes the trip reason so a NEW trip after recovery re-pages
        # even inside the cooldown window of the previous one.
        reason = str(cb.get("trip_reason", ""))[:80]
        return [
            Finding(
                key=f"breaker_tripped:{reason}",
                severity="critical",
                message=(
                    "loss circuit breaker TRIPPED — "
                    f"reason=\"{cb.get('trip_reason')}\" "
                    f"cooldown_remaining={cb.get('cooldown_remaining_s')}s "
                    f"daily_drawdown={cb.get('daily_drawdown_pct')}%. "
                    "Protective halt — the watchdog will NOT reset it; "
                    "review and reset via ops when appropriate."
                ),
            )
        ]
    return []


def check_disk(
    paths: Optional[List[str]] = None,
    warn_pct: float = DISK_WARN_PCT,
) -> List[Finding]:
    findings: List[Finding] = []
    for path in paths or [DATA_DIR, "/"]:
        try:
            usage = shutil.disk_usage(path)
        except OSError:
            continue
        used_pct = 100.0 * (usage.total - usage.free) / usage.total if usage.total else 0.0
        if used_pct >= warn_pct:
            findings.append(
                Finding(
                    key=f"disk_pressure:{path}",
                    severity="warn" if used_pct < DISK_CRIT_PCT else "critical",
                    message=(
                        f"disk at {path} is {used_pct:.1f}% full "
                        f"(warn {warn_pct:.0f}%, auto-prune {DISK_CRIT_PCT:.0f}%)."
                    ),
                )
            )
    return findings


def _mem_available_pct(meminfo_path: str = "/proc/meminfo") -> Optional[float]:
    try:
        total = avail = None
        with open(meminfo_path) as fh:
            for line in fh:
                if line.startswith("MemTotal:"):
                    total = float(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    avail = float(line.split()[1])
                if total is not None and avail is not None:
                    return 100.0 * avail / total
    except Exception:
        pass
    return None


def check_memory(
    warn_pct: float = MEM_WARN_PCT, meminfo_path: str = "/proc/meminfo"
) -> List[Finding]:
    pct = _mem_available_pct(meminfo_path)
    if pct is not None and pct < warn_pct:
        return [
            Finding(
                key="memory_pressure",
                severity="warn",
                message=(
                    f"host memory available is {pct:.1f}% (< {warn_pct:.0f}%) — "
                    "OOM-kill risk; earlyoom (host layer) is the backstop."
                ),
            )
        ]
    return []


# ---------------------------------------------------------------------------
# Actions — every one audited + paged.
# ---------------------------------------------------------------------------

def _page(text: str) -> None:
    sent = notify_telegram.send_telegram(f"🤖 WATCHDOG\n{text}")
    audit("page", {"text": text, "sent": bool(sent)})
    print(f"PAGE: {text}")


def engage_kill_switch(reason: str) -> bool:
    """ENGAGE only — the watchdog has no disengage path by design."""
    token = os.environ.get("API_AUTH_TOKEN", "").strip()
    if not token:
        audit("kill_switch_skipped", {"why": "no API_AUTH_TOKEN"})
        return False
    req = urllib.request.Request(
        _kill_switch_url(),
        data=json.dumps({"engaged": True, "reason": f"watchdog: {reason}"}).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            ok = 200 <= resp.status < 300
    except Exception as exc:  # noqa: BLE001 — page the failure, never raise
        audit("kill_switch_failed", {"error": type(exc).__name__, "reason": reason})
        return False
    audit("kill_switch_engaged", {"ok": ok, "reason": reason})
    return ok


def _restart_budget_left(state: WatchdogState, now: float) -> int:
    state.engine_restarts = [t for t in state.engine_restarts if now - t < 3600]
    return MAX_ENGINE_RESTARTS_PER_HOUR - len(state.engine_restarts)


def restart_engine(state: WatchdogState, why: str, now: Optional[float] = None) -> bool:
    """Bounded engine restart. Over budget → kill-switch escalation."""
    now = now or time.time()
    if not RESTART_ENABLED:
        _page(f"⛔ engine needs a restart ({why}) but WATCHDOG_RESTART_ENABLED=false — manual action required.")
        return False
    if _restart_budget_left(state, now) <= 0:
        # Cooldown-gated page: this branch runs on EVERY loop while the
        # engine stays broken — unthrottled it paged the owner once per
        # minute for 20+ minutes on 2026-07-13.  Once the watchdog has
        # engaged the kill switch the episode is already escalated; stay
        # quiet until it clears or the cooldown re-arms.
        key = "engine_restart_budget_exhausted"
        last = state.last_paged_at.get(key)
        page_due = last is None or now - last >= PAGE_COOLDOWN_SEC
        if page_due and not state.kill_switch_engaged_by_watchdog:
            _page(
                f"🆘 CRITICAL: engine restart budget exhausted "
                f"({MAX_ENGINE_RESTARTS_PER_HOUR}/h) and still broken ({why}). "
                "Escalating to kill switch — auto-trade HALTS; resting SL/TP on "
                "Binance keep protecting open positions. Re-enable is owner-only."
            )
            state.last_paged_at[key] = now
        if KILLSWITCH_ENABLED and not state.kill_switch_engaged_by_watchdog:
            # Retry the engage every loop until it lands — the attempt is
            # cheap and idempotent; only the paging is throttled.
            ok = engage_kill_switch(f"engine unrecoverable: {why}")
            state.kill_switch_engaged_by_watchdog = ok
            if ok:
                _page("kill switch ENGAGED by watchdog.")
            elif page_due:
                _page(
                    "🆘 kill-switch engage FAILED — engine AND control "
                    "surface degraded; intervene NOW."
                )
        return False
    state.engine_restarts.append(now)
    ok = restart_container(ENGINE_CONTAINER)
    audit("engine_restart", {"ok": ok, "why": why})
    _page(
        f"🔄 engine restarted ({why}) — budget "
        f"{_restart_budget_left(state, now)}/{MAX_ENGINE_RESTARTS_PER_HOUR} left this hour."
        if ok
        else f"🆘 engine restart FAILED ({why}) — Docker API not responding; intervene."
    )
    return ok


def deadman_ping() -> None:
    if not HEALTHCHECKS_PING_URL:
        return
    try:
        with urllib.request.urlopen(HEALTHCHECKS_PING_URL, timeout=10):
            pass
    except Exception:
        print("deadman ping failed (non-blocking)")


# ---------------------------------------------------------------------------
# Paging with dedupe + recovery notices.
# ---------------------------------------------------------------------------

def dispatch_pages(
    findings: List[Finding], state: WatchdogState, now: Optional[float] = None
) -> None:
    now = now or time.time()
    current_keys = [f.key for f in findings]
    for f in findings:
        last = state.last_paged_at.get(f.key)
        if last is None or now - last >= PAGE_COOLDOWN_SEC:
            icon = "🆘" if f.severity == "critical" else "⚠️"
            _page(f"{icon} {f.message}")
            state.last_paged_at[f.key] = now
    # Recovery notices: a key that was active last loop and paged at least
    # once, now gone → tell the owner it cleared (once).
    for key in state.active_keys:
        if key not in current_keys and key in state.last_paged_at:
            _page(f"✅ recovered: {key}")
            del state.last_paged_at[key]
    state.active_keys = current_keys


# ---------------------------------------------------------------------------
# Main loop.
# ---------------------------------------------------------------------------

def run_once(state: WatchdogState, now: Optional[float] = None) -> List[Finding]:
    now = now or time.time()
    states = {name: container_state(name) for name in WATCHED_CONTAINERS}

    # Staleness ages are floored at the engine's StartedAt — the status
    # files' mtimes persist on the data volume across restarts, so without
    # the floor every restart re-reads the PRE-restart age and a booting
    # engine looks permanently wedged (2026-07-13 restart storm).
    engine_started_at = float(states.get(ENGINE_CONTAINER, {}).get("started_at", 0.0))

    findings: List[Finding] = []
    findings += check_containers(states)
    # data_dir passed explicitly: module attribute resolved at call time
    # (defaults bind at def time, which pins the pre-monkeypatch path).
    findings += check_scanner_heartbeat(data_dir=DATA_DIR, now=now, min_ts=engine_started_at)
    findings += check_pricing_freshness(data_dir=DATA_DIR, now=now, min_ts=engine_started_at)
    findings += check_circuit_breaker(data_dir=DATA_DIR, now=now)
    findings += check_disk()
    findings += check_memory()

    # --- Graduated remediation -------------------------------------------
    engine_running = states.get(ENGINE_CONTAINER, {}).get("running", False)
    engine_uptime = (now - engine_started_at) if engine_started_at > 0 else None
    in_boot_grace = engine_uptime is not None and engine_uptime < BOOT_GRACE_SEC

    # Wedged scan loop with a running container → the restart Docker's own
    # healthcheck + autoheal should have done but didn't.  Never inside the
    # boot grace: a restart here kills the warmup the previous restart
    # started and burns the budget straight into the kill switch.
    if (
        engine_running
        and not in_boot_grace
        and any(f.key == "scanner_heartbeat_stale" for f in findings)
    ):
        restart_engine(state, "scanner heartbeat stale beyond watchdog bound", now=now)

    # Blind-position escalation: page immediately (dispatch_pages), restart
    # once blindness has persisted — a boot re-seeds all active symbols.
    blind_now = {f.key for f in findings if f.key.startswith("blind_position:")}
    for key in blind_now:
        state.blind_since.setdefault(key, now)
    for key in list(state.blind_since):
        if key not in blind_now:
            del state.blind_since[key]
    persistent = [k for k, since in state.blind_since.items() if now - since >= BLIND_ESCALATION_SEC]
    if persistent and engine_running and not in_boot_grace:
        restart_engine(
            state,
            f"open position blind for >{BLIND_ESCALATION_SEC}s ({', '.join(persistent)})",
            now=now,
        )
        state.blind_since = {}

    # Disk auto-remediation at the critical bound.
    for f in findings:
        if f.key.startswith("disk_pressure:") and f.severity == "critical":
            result = prune_disk()
            audit("disk_prune", result)
            _page(
                f"🧹 disk critical — pruned dangling images/stopped containers/"
                f"build cache, reclaimed {result['space_reclaimed_bytes'] / 1e6:.0f} MB."
            )
            break

    # Engine recovered → clear the watchdog-engaged marker so a FUTURE
    # unrecoverable episode can engage again. (The switch itself stays
    # engaged until the owner disengages it — this only resets our memory.)
    if state.kill_switch_engaged_by_watchdog and engine_running and not findings:
        state.kill_switch_engaged_by_watchdog = False
        # Re-arm the escalation page too, so the next episode pages
        # immediately instead of waiting out a stale cooldown stamp.
        state.last_paged_at.pop("engine_restart_budget_exhausted", None)

    dispatch_pages(findings, state, now=now)
    state.save()
    deadman_ping()
    return findings


def _touch_own_heartbeat() -> None:
    try:
        with open(WATCHDOG_HEARTBEAT_PATH, "w") as fh:
            fh.write(str(time.time()))
    except OSError:
        pass


def main() -> None:
    print(
        f"watchdog: starting — interval={INTERVAL_SEC}s "
        f"restart_enabled={RESTART_ENABLED} killswitch_enabled={KILLSWITCH_ENABLED} "
        f"containers={WATCHED_CONTAINERS} telegram={'yes' if notify_telegram.is_configured() else 'NO'}"
    )
    audit("watchdog_start", {"interval": INTERVAL_SEC})
    state = WatchdogState.load()
    while True:
        started = time.time()
        try:
            findings = run_once(state)
            print(
                f"watchdog: loop done — {len(findings)} finding(s)"
                + (": " + "; ".join(f.key for f in findings) if findings else "")
            )
        except Exception as exc:  # noqa: BLE001 — the supervisor must survive its own bugs
            print(f"watchdog: loop error ({type(exc).__name__}: {exc})")
            audit("loop_error", {"error": f"{type(exc).__name__}: {exc}"})
        _touch_own_heartbeat()
        time.sleep(max(1.0, INTERVAL_SEC - (time.time() - started)))


if __name__ == "__main__":
    main()
