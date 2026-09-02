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


def reset_for_test() -> None:
    """Test-only — drop every counter and restart the clock."""
    global _started_at
    with _lock:
        _sites.clear()
        _started_at = time.time()
