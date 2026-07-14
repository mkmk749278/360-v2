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

# Stale-pricing invariant tuning (audit F-07, seconds). The freshness file is
# published every ~30s by the trade monitor; treat it as expired well past
# that so a wedged monitor loop is caught here instead of silently passing a
# frozen snapshot.
PRICING_FILE_MAX_AGE_SEC = int(os.environ.get("PRICING_FILE_MAX_AGE_SEC", "600"))

# Feature-liveness manifest is published every ~5 min by the audit loop;
# treat it as dead well past that (2026-07-14 incident class).
FEATURE_LIVENESS_MAX_AGE_SEC = int(
    os.environ.get("FEATURE_LIVENESS_MAX_AGE_SEC", "1800")
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


def check_pricing_freshness() -> None:
    """Page when an OPEN position's every pricing source has gone stale.

    Audit F-07 / the Session 44-45-46 incident class (MVLLUSDT: 11h of
    frozen close on an open runner — SL/TP backstop blind, discovered by
    owner screenshot). The trade monitor publishes per-open-signal source
    freshness to ``pricing_freshness.json`` (~30s cadence); an entry with
    ``blind: true`` means the 1m candle is stale AND the mark-price feed has
    nothing — the fallback chain shipped in #706/Session 46 is exhausted and
    the position is unprotected. That is a page, not a log line.

    File missing → pre-rollout build or the engine hasn't opened a monitor
    cycle yet; stay quiet. File present but old → the publisher itself froze;
    that is also a page (a freshness monitor that can silently stop measuring
    is F-09 all over again).
    """
    fp = os.path.join(DATA_DIR, "pricing_freshness.json")
    if not os.path.exists(fp):
        print("Pricing freshness: file not found (pre-rollout build); check skipped")
        return
    try:
        with open(fp) as fh:
            snap = json.load(fh)
        age = int(time.time() - float(snap.get("updated_at", 0)))
        positions = snap.get("positions", [])
        blind = [p for p in positions if p.get("blind")]
        print(
            f"Pricing freshness: {len(positions)} open signal(s), "
            f"{len(blind)} blind, snapshot age {age}s"
        )
        if age > PRICING_FILE_MAX_AGE_SEC:
            print(
                "INVARIANT_WARN: pricing-freshness snapshot itself is stale "
                f"({age}s > {PRICING_FILE_MAX_AGE_SEC}s) — the trade monitor "
                "stopped publishing; its SL/TP backstop loop may be wedged."
            )
            return
        for p in blind:
            print(
                "INVARIANT_WARN: open position on "
                f"{p.get('symbol')} ({p.get('status')}, {p.get('signal_id')}) "
                "is priced off a fully stale source "
                f"(1m kline age {p.get('kline_age_sec')}s, mark feed has no price) — "
                "SL/TP/trailing protection is BLIND (F-07 / MVLLUSDT class)."
            )
        if not blind:
            print("OK: every open position has a fresh pricing source")
    except Exception as exc:  # noqa: BLE001 — diagnostic script, report and move on
        print(f"Pricing freshness: check unreadable ({exc})")


def check_feature_liveness() -> None:
    """Page when a measurement feature has silently flat-lined (2026-07-14).

    The engine's feature-liveness watchdog compares every measurement
    pipeline's output counter against its upstream driver each 5-min audit
    cycle and publishes ``feature_liveness.json``; entries in ``alerts``
    have already cleared their sustained-streak thresholds engine-side, so
    this check stays dumb: one INVARIANT_WARN per alert.  The 8-features-
    dead-silently incident (PRs #726/#727) is the class this pages on —
    e.g. suppression events flowing while stop-geometry pairs stamp zero,
    or a fail-open exception counter growing every cycle.

    File missing → pre-rollout build; stay quiet.  File present but old
    while the engine heartbeat is fresh → the liveness system itself died,
    which is exactly the recursion F-09 warns about — page.
    """
    fp = os.path.join(DATA_DIR, "feature_liveness.json")
    if not os.path.exists(fp):
        print("Feature liveness: file not found (pre-rollout build); check skipped")
        return
    try:
        with open(fp) as fh:
            snap = json.load(fh)
        age = int(time.time() - float(snap.get("generated_at", 0)))
        features = snap.get("features", {})
        alerts = snap.get("alerts", [])
        print(
            f"Feature liveness: {len(features)} feature(s) probed, "
            f"{len(alerts)} alerting, manifest age {age}s"
        )
        if age > FEATURE_LIVENESS_MAX_AGE_SEC:
            hb = os.path.join(DATA_DIR, "scanner_heartbeat")
            hb_fresh = os.path.exists(hb) and (time.time() - os.path.getmtime(hb)) < 300
            if hb_fresh:
                print(
                    "INVARIANT_WARN: feature-liveness manifest is stale "
                    f"({age}s > {FEATURE_LIVENESS_MAX_AGE_SEC}s) while the engine "
                    "heartbeat is fresh — the liveness watchdog itself stopped "
                    "publishing (a monitor that can die silently is the incident "
                    "class it exists to catch)."
                )
            else:
                print(
                    f"Feature liveness: manifest stale ({age}s) alongside a stale "
                    "engine heartbeat — engine-down is the primary finding, skipping"
                )
            return
        for a in alerts:
            print(
                "INVARIANT_WARN: feature_liveness "
                f"{a.get('feature')} — {a.get('detail')} "
                f"(sustained {a.get('streak')} audit cycles)"
            )
        if not alerts:
            print("OK: every probed feature is producing data at its expected rate")
    except Exception as exc:  # noqa: BLE001 — diagnostic script, report and move on
        print(f"Feature liveness: check unreadable ({exc})")


check_heartbeat()
check_circuit_breaker()
check_paper_silence()
check_pricing_freshness()
check_feature_liveness()
