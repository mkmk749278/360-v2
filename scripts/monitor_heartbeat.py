"""Engine liveness probe — piped into the engine container by the hourly
``vps-liveness.yml`` watch (and runnable ad hoc via ``docker exec``).

Prints human-readable status lines; the workflow greps them. Machine-
significant problems are ALSO emitted as ``INVARIANT_WARN: ...`` lines —
the workflow pages the owner (auto-detected issue) on ANY such line, so a
new check added here is automatically a new page with no workflow change.

Checks:
1. Scanner heartbeat freshness (hung/halted scan loop).
2. Loss circuit-breaker state (protective halt vs hang disambiguation).
3. Paper-book silence (audit F-09; the Session-46 incident class): the
   engine book is closing signals but NO paper ledger has been touched for
   over a day → the measurement system froze silently. mtime-based on
   purpose — ledgers are written on every paper event regardless of the
   Redis/JSON persistence mode, and reading file times can never disturb
   the engine.

``ENGINE_DATA_DIR`` overrides ``/app/data`` so tests can point at a tmpdir.
"""

import glob
import json
import os
import time

DATA_DIR = os.environ.get("ENGINE_DATA_DIR", "/app/data")

# Paper silence tuning (env-overridable, seconds).
PAPER_SILENCE_SEC = int(os.environ.get("PAPER_SILENCE_SEC", str(24 * 3600)))
ENGINE_ACTIVITY_WINDOW_SEC = int(
    os.environ.get("ENGINE_ACTIVITY_WINDOW_SEC", str(6 * 3600))
)


def check_heartbeat() -> None:
    p = os.path.join(DATA_DIR, "scanner_heartbeat")
    if os.path.exists(p):
        age = int(time.time() - os.path.getmtime(p))
        print(f"Heartbeat age: {age}s")
        if age > 120:
            print(f"WARNING: Heartbeat is STALE ({age}s > 120s) — scanner loop may be hung")
        else:
            print("OK: Heartbeat fresh — scanner loop is alive")
    else:
        print(f"NOT FOUND: {p} does not exist inside container")
        print("Scanner has not completed its first cycle yet, or _touch_heartbeat() is failing silently")


def check_circuit_breaker() -> None:
    # Circuit-breaker state — lets the report tell a *protective halt* apart
    # from a *hung loop* (both otherwise show a stale heartbeat). Published by
    # the scanner every cycle, including while halted.
    bp = os.path.join(DATA_DIR, "circuit_breaker_status.json")
    if not os.path.exists(bp):
        print("Circuit breaker: status file not found (pre-first-cycle or pre-observability build)")
        return
    try:
        with open(bp) as fh:
            cb = json.load(fh)
        status_age = int(time.time() - cb.get("updated_at", 0))
        if cb.get("tripped"):
            print(
                "Circuit breaker: TRIPPED "
                f'mode={cb.get("status_mode")} '
                f'reason="{cb.get("trip_reason")}" '
                f'cooldown_remaining={cb.get("cooldown_remaining_s")}s '
                f'daily_drawdown={cb.get("daily_drawdown_pct")}%/{cb.get("max_daily_drawdown_pct")}% '
                f"(status_age={status_age}s)"
            )
        else:
            print(f"Circuit breaker: healthy (status_age={status_age}s)")
    except Exception as exc:  # noqa: BLE001 — diagnostic script, report and move on
        print(f"Circuit breaker: status unreadable ({exc})")


def check_paper_silence() -> None:
    """Page when the engine book is active but every paper ledger is frozen.

    Signature of the Session-46 incident: signals kept dispatching/closing
    for ~24h with ZERO paper counterparts, discovered only by the owner
    eyeballing the ops page. Detection:

    * engine recently active  = ``signal_performance.json`` mtime within
      ``ENGINE_ACTIVITY_WINDOW_SEC`` (that file is appended on every
      signal close, in every persistence mode), AND
    * paper books exist but the NEWEST ledger mtime is older than
      ``PAPER_SILENCE_SEC``.

    No paper books at all → paper trading isn't configured on this deploy;
    stay silent (this probe must not nag a topology that never had paper).
    """
    try:
        perf = os.path.join(DATA_DIR, "signal_performance.json")
        books = sorted(glob.glob(os.path.join(DATA_DIR, "paper_books", "paper_pnl_user_*.json")))
        legacy = os.path.join(DATA_DIR, "paper_pnl_state.json")
        if os.path.exists(legacy):
            books.append(legacy)

        if not books:
            print("Paper books: none found — paper trading not configured; check skipped")
            return
        if not os.path.exists(perf):
            print("Paper books: engine perf record missing — activity unknown; check skipped")
            return

        now = time.time()
        engine_idle_sec = int(now - os.path.getmtime(perf))
        newest_paper_sec = int(now - max(os.path.getmtime(b) for b in books))
        print(
            f"Paper books: {len(books)} ledger(s), newest write {newest_paper_sec}s ago; "
            f"engine book last close {engine_idle_sec}s ago"
        )
        if engine_idle_sec <= ENGINE_ACTIVITY_WINDOW_SEC and newest_paper_sec > PAPER_SILENCE_SEC:
            print(
                "INVARIANT_WARN: paper books silent "
                f"({newest_paper_sec}s since last paper write, > {PAPER_SILENCE_SEC}s) "
                f"while the engine book closed signals {engine_idle_sec}s ago — "
                "the measurement layer may have frozen (Session-46 class). "
                "Run scripts/diag_paper_health.py via the ops Diag page."
            )
        else:
            print("OK: paper books consistent with engine activity")
    except Exception as exc:  # noqa: BLE001 — diagnostic script, report and move on
        print(f"Paper books: check unreadable ({exc})")


check_heartbeat()
check_circuit_breaker()
check_paper_silence()
