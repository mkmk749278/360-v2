"""Firestore read census — what actually spends the daily quota (2026-09-02).

Written the morning auto-trade went down for every user because Firestore
answered ``RESOURCE_EXHAUSTED: Quota exceeded.``  The project had spent
**53,000 document reads against a 50,000/day allowance — on 25 writes.**  A
2,000:1 read-to-write ratio on data that barely changes, against a
``CLAUDE.md`` budget of ~12k/day, and nobody could say where the reads went:
the only instrument was the GCP billing console, one day late and aggregated
across every call site in both containers.

**Count documents, never calls.**  Firestore bills per document returned, so a
``collection_group`` query that matches forty users costs forty reads, and one
that matches none still costs one.  A call counter would have made
``list_active_uids`` — the read that grows linearly with subscribers — look
identical to a single-document get.  Every site therefore reports the number of
documents it actually consumed.

**Per process, and it says which.**  In isolated mode the engine and the api
container hold separate counters for the same modules, and the surfaces the
owner reads are served by the api one.  A census that could not say which
process it described would repeat the ``INDEX COLD`` defect at the one moment
somebody is trying to find a hot loop — so every snapshot carries its role.

Hot-path safe: no I/O, one dict update under a lock.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Any, Dict

_lock = threading.Lock()
_sites: Dict[str, Dict[str, Any]] = {}
_started_at: float = time.time()


def _process_role() -> str:
    """``api`` or ``engine`` — which container these counts describe.

    Derived from the same env var that decides the split so it cannot drift
    from the deployment it is reporting on.  ``single`` when the engine serves
    its own HTTP and the distinction does not exist.
    """
    isolated = os.environ.get("API_PROCESS_ISOLATED", "").strip().lower()
    if isolated not in ("1", "true", "yes"):
        return "single"
    return os.environ.get("PROCESS_ROLE", "engine").strip().lower() or "engine"


def record(site: str, docs: int = 1) -> None:
    """Count *docs* documents read at *site* (never raises).

    ``site`` is a stable dotted name — ``keystore.get_key_blob``,
    ``keystore.list_active_uids`` — because it is the key the diag console and
    any future pager display.  Keep it greppable.

    A query that returned nothing still costs one read; pass ``docs=1`` for it
    rather than 0, or the census will under-report exactly the empty-result
    loops that are cheapest to leave running and easiest to forget.
    """
    try:
        n = int(docs)
        if n < 0:
            n = 0
        ts = time.time()
        with _lock:
            entry = _sites.setdefault(
                site, {"docs": 0, "calls": 0, "last_ts": 0.0}
            )
            entry["docs"] = int(entry["docs"]) + n
            entry["calls"] = int(entry["calls"]) + 1
            entry["last_ts"] = ts
    except Exception:  # pragma: no cover - a census must never break a read
        pass


def snapshot() -> Dict[str, Any]:
    """Per-site document counts plus the observed rate.

    ``per_day`` extrapolates from this process's uptime and is the number to
    compare against the 50,000/day allowance — but it is an extrapolation, not
    a measurement, so it is named apart from ``docs`` and a short uptime is
    reported beside it rather than silently producing a confident daily figure
    from ninety seconds of data.
    """
    with _lock:
        sites = {k: dict(v) for k, v in _sites.items()}
        started = _started_at
    uptime = max(time.time() - started, 1.0)
    day = 86400.0
    rows = []
    total = 0
    for site, entry in sites.items():
        docs = int(entry["docs"])
        total += docs
        rows.append(
            {
                "site": site,
                "docs": docs,
                "calls": int(entry["calls"]),
                "docs_per_call": round(docs / max(int(entry["calls"]), 1), 2),
                "per_day": int(docs * day / uptime),
                "last_ts": entry["last_ts"],
            }
        )
    rows.sort(key=lambda r: r["docs"], reverse=True)
    return {
        "process_role": _process_role(),
        "uptime_sec": int(uptime),
        "uptime_is_short": uptime < 900.0,
        "total_docs": total,
        "total_per_day": int(total * day / uptime),
        "free_tier_reads_per_day": 50000,
        "sites": rows,
    }


#: Firestore's no-cost allowance, per project per day, resetting midnight
#: Pacific.  Past it a project whose billing account is not in good standing is
#: refused with ``RESOURCE_EXHAUSTED``, which is what happened at 00:41 UTC on
#: 2026-09-02: not a charge, an outage.
FREE_TIER_READS_PER_DAY = 50_000

#: Price per 100,000 document reads, in USD.  Firestore's location pricing
#: differs by roughly 2x between a multi-region (nam5, eur3) and a single
#: region, and this project's location is a fact about the console rather than
#: about the code — so BOTH are published and neither is called "the" price.
#: A surface quoting one of them silently would be choosing the flattering
#: half of a number the reader cannot check.
PRICE_PER_100K_READS_MULTI_REGION = 0.06
PRICE_PER_100K_READS_REGIONAL = 0.03

#: The owner's stated auto-trade target (2026-09-02): 1,000 members.  Named
#: here so the projection below is measured against the business goal rather
#: than against today's handful of users, where every per-user read looks free.
TARGET_MEMBERS = 1000


def project(members: int = TARGET_MEMBERS, current_members: int = 1) -> Dict[str, Any]:
    """What today's measured reads become at *members* subscribers.

    **This is arithmetic on a measurement, not a measurement.**  It takes each
    call site's observed daily rate and scales the ones whose cost grows with
    the roster, leaving the ones that do not.  Which sites scale is a fact
    about the code — a ``collection_group`` scan bills per document returned,
    a flag document does not — so it is declared here rather than guessed from
    the numbers, and the split is on screen so a reader can disagree with it.

    Why it exists: every per-user read is invisible at one user.  The
    ``worker_manager`` roster scan cost 1,440 reads a day on this account and
    1.44 MILLION at the target, and nothing in the console, the bill or the
    census would have said so until the subscribers arrived.  A cost model
    that only describes today cannot stop the bill it is there to stop.
    """
    snap = snapshot()
    members = max(int(members), 1)
    current = max(int(current_members), 1)
    factor = members / current
    rows = []
    flat_total = 0
    scaled_total = 0
    for row in snap["sites"]:
        scales = _scales_with_members(row["site"])
        per_day = int(row["per_day"])
        projected = int(per_day * factor) if scales else per_day
        flat_total += per_day
        scaled_total += projected
        rows.append({**row, "scales_with_members": scales,
                     "projected_per_day": projected})
    over = max(scaled_total - FREE_TIER_READS_PER_DAY, 0)
    return {
        "process_role": snap["process_role"],
        "uptime_sec": snap["uptime_sec"],
        "uptime_is_short": snap["uptime_is_short"],
        "measured_members": current,
        "target_members": members,
        "measured_per_day": flat_total,
        "projected_per_day": scaled_total,
        "free_tier_reads_per_day": FREE_TIER_READS_PER_DAY,
        "projected_over_free_tier": over,
        # Cost is on the BILLABLE excess, not on the whole figure — the first
        # 50,000 are free every day, and a projection that charges for them
        # overstates a small overage by the entire allowance.
        "projected_usd_per_month_multi_region": round(
            over / 100_000.0 * PRICE_PER_100K_READS_MULTI_REGION * 30, 2
        ),
        "projected_usd_per_month_regional": round(
            over / 100_000.0 * PRICE_PER_100K_READS_REGIONAL * 30, 2
        ),
        "sites": sorted(
            rows, key=lambda r: r["projected_per_day"], reverse=True
        ),
        "note": (
            "Projection, not measurement. Sites marked scales_with_members "
            "are the ones whose Firestore cost is per-user by construction; "
            "the rest are per-process and flat. Price is charged on the "
            "excess over the free allowance only, and both Firestore "
            "location tiers are shown because the project's region is a "
            "console fact, not a code fact."
        ),
    }


#: Call sites whose read count grows with the number of subscribers.
#:
#: Declared, not inferred.  A site is here because of what it DOES — one read
#: per user, or a query billed per document returned over a per-user
#: collection — and that is checkable by reading it, while inferring the split
#: from observed numbers at one user would classify everything as flat.
_PER_MEMBER_SITES = frozenset({
    "keystore.list_active_uids",
    "keystore.has_key",
    "keystore.get_key_blob",
    "kill_switch.user_disabled",
    "kill_switch.self_reenable",
    "kill_switch.disabled_rebuild",
    "position_state.get_position",
    "position_state.list_for_user",
    "position_state.list_recent_closed",
    "position_state.index_hydrate",
    "position_state.index_resync",
    "pretp.positions_for_symbol",
    "dispatch_log.recent_events",
})


def _scales_with_members(site: str) -> bool:
    """True when this site's read count is per-user.

    An UNKNOWN site is treated as scaling.  That is the safe direction for a
    cost projection: a flat site wrongly scaled overstates a bill somebody
    then checks, while a per-user site wrongly called flat is invisible until
    the subscribers arrive — which is the entire failure this function exists
    to prevent.
    """
    if site in _PER_MEMBER_SITES:
        return True
    known_flat = (
        "kill_switch.global_doc",
        "kill_switch.signal_expiry",
        "kill_switch.play_billing",
        "kill_switch.disabled_mirror",
        "runtime_tunables.doc",
        "keystore.roster_doc",
    )
    return site not in known_flat


def reset_for_test() -> None:
    """Test-only — drop every counter and restart the clock."""
    global _started_at
    with _lock:
        _sites.clear()
        _started_at = time.time()
