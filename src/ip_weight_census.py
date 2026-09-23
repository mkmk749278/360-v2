"""Binance IP request-weight census — how close the box is to its ban line.

Why this exists (2026-09-23)
----------------------------
The engine reaches Binance from ONE whitelisted IP, and USDⓈ-M futures allows
**2,400 request-weight per minute per IP**. On 2026-09-01 a sweep spent that
budget on ``algoOpenOrders`` GETs and every paid user's orders then failed for
roughly four hours. The same budget is shared by everything that talks to
``fapi.binance.com`` from this box: the scanner's public REST, and every signed
per-user call the signing service makes — ``positionRisk`` from the reconciler
every 60s per user with an open position, ``algoOpenOrders`` per symbol, and
the order path.

Two instruments existed and neither answered *"how close have we come"*:

* ``rate_limiter.futures_rate_limiter`` syncs the header on **public** calls.
  It is a live throttle state, not a history — the ops data-intake page shows
  whatever it held at the instant of the request.
* The **signed** calls discarded the header inside the signing container, so
  the per-user traffic that grows with the subscriber count was never
  attributed to anything.

What it records
---------------
Binance's ``X-MBX-USED-WEIGHT-1M`` header reports the WHOLE IP's weight over the
trailing minute, not the cost of the request that carried it. So any one
response is a reading of the fleet total, and the maximum over a minute is the
number to compare against 2,400. This module keeps:

* per-minute peaks of that header (last :data:`_MINUTES_KEPT` minutes), split by
  the channel it arrived on — ``public`` (engine REST) or ``signed`` (signing
  service) — because they are the same quantity read by two processes and a
  disagreement between them is information;
* the all-time peak since boot, with its timestamp;
* signed call counts per Binance path, and the number of distinct users those
  calls were made for in the current hour — the input to *"what does one more
  live user cost"*;
* throttle responses (HTTP 418 / 429) by status, because those are the ban
  itself arriving;
* signed responses that carried **no** header, counted apart: an older signing
  service, a network failure, or a response that genuinely had none — "we could
  not read it" is never folded into "it read low".

Measurement only
----------------
Nothing here throttles, delays or refuses a request. It feeds no gate and the
rate limiter never reads it. Recording is O(1), in memory, with a bounded
footprint, and never raises into its caller.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import Any, Dict, Optional

from src.utils import get_logger

log = get_logger("ip_weight_census")

#: USDⓈ-M futures REQUEST_WEIGHT per IP per minute (documented 2026-08-05,
#: mirrored in :mod:`src.binance_weights`).
FUTURES_IP_WEIGHT_LIMIT_1M = 2_400

#: The probe violates when a recent minute peaked above this fraction.
ALERT_FRACTION = 0.80

#: Minutes of per-minute peaks retained.
_MINUTES_KEPT = 60

#: Bound on distinct paths tracked, so an unexpected path cannot grow the map.
_MAX_PATHS = 64

#: Bound on distinct uids tracked per hour bucket.
_MAX_UIDS_PER_HOUR = 5_000

_SOURCES = ("public", "signed")

_lock = threading.Lock()
_boot_ts = time.time()
# minute_epoch -> {"public": peak, "signed": peak}
_minutes: "OrderedDict[int, Dict[str, int]]" = OrderedDict()
_peak = {"value": 0, "ts": 0.0, "source": ""}
_last = {s: {"value": None, "ts": 0.0} for s in _SOURCES}
_signed_calls: Dict[str, int] = {}
_signed_no_header = 0
_throttled: Dict[int, int] = {}
_last_throttle = {"ts": 0.0, "status": 0}
_uid_hour = {"hour": 0, "uids": set()}


def parse_header(raw: Any) -> Optional[int]:
    """``X-MBX-USED-WEIGHT-1M`` as an int, or ``None`` when absent/unparseable."""
    if raw is None:
        return None
    try:
        value = int(str(raw).strip())
    except (TypeError, ValueError):
        return None
    return value if value >= 0 else None


def _note_value(source: str, value: int, now: float) -> None:
    minute = int(now // 60)
    bucket = _minutes.get(minute)
    if bucket is None:
        bucket = {s: 0 for s in _SOURCES}
        _minutes[minute] = bucket
        while len(_minutes) > _MINUTES_KEPT:
            _minutes.popitem(last=False)
    if value > bucket[source]:
        bucket[source] = value
    _last[source] = {"value": value, "ts": now}
    if value > _peak["value"]:
        _peak.update(value=value, ts=now, source=source)


def record_public(raw_header: Any, *, now: Optional[float] = None) -> None:
    """A public engine REST response from the futures host arrived."""
    try:
        value = parse_header(raw_header)
        if value is None:
            return
        with _lock:
            _note_value("public", value, now if now is not None else time.time())
    except Exception as exc:  # noqa: BLE001 — a census must never break a request
        log.debug("ip_weight_census.record_public failed: {}", exc)


def record_signed(
    *,
    path: str,
    firebase_uid: str,
    base: str,
    used_weight_1m: Optional[int],
    binance_status: int = 0,
    now: Optional[float] = None,
) -> None:
    """A signed call returned from the signing service.

    Only ``futures`` calls are counted against the futures IP budget; spot has
    its own pool and is not what this census is for.
    """
    try:
        if base != "futures":
            return
        ts = now if now is not None else time.time()
        global _signed_no_header
        with _lock:
            key = path or "(none)"
            if key in _signed_calls or len(_signed_calls) < _MAX_PATHS:
                _signed_calls[key] = _signed_calls.get(key, 0) + 1
            else:
                _signed_calls["(other)"] = _signed_calls.get("(other)", 0) + 1
            hour = int(ts // 3600)
            if _uid_hour["hour"] != hour:
                _uid_hour["hour"] = hour
                _uid_hour["uids"] = set()
            if firebase_uid and len(_uid_hour["uids"]) < _MAX_UIDS_PER_HOUR:
                _uid_hour["uids"].add(firebase_uid)
            if binance_status in (418, 429):
                _throttled[binance_status] = _throttled.get(binance_status, 0) + 1
                _last_throttle.update(ts=ts, status=binance_status)
            if used_weight_1m is None:
                _signed_no_header += 1
            else:
                _note_value("signed", int(used_weight_1m), ts)
    except Exception as exc:  # noqa: BLE001
        log.debug("ip_weight_census.record_signed failed: {}", exc)


def snapshot(*, now: Optional[float] = None) -> Dict[str, Any]:
    """Everything the census holds, for the diagnostic catalog."""
    ts = now if now is not None else time.time()
    with _lock:
        cur = int(ts // 60)
        minutes = [
            {
                "minute": m,
                "minute_utc": time.strftime("%H:%M", time.gmtime(m * 60)),
                "peak": max(b.values()),
                "public": b["public"],
                "signed": b["signed"],
            }
            for m, b in _minutes.items()
        ]
        peak = dict(_peak)
        last = {s: dict(v) for s, v in _last.items()}
        signed_calls = dict(sorted(_signed_calls.items(), key=lambda kv: -kv[1]))
        no_header = _signed_no_header
        throttled = dict(_throttled)
        last_throttle = dict(_last_throttle)
        uids_this_hour = len(_uid_hour["uids"]) if _uid_hour["hour"] == int(ts // 3600) else 0
    # Wall-clock windows, not "the last N buckets that exist": after an idle
    # hour the newest buckets are old, and reading them as recent would page on
    # a peak that has long since passed.
    recent = [row["peak"] for row in minutes if row["minute"] > cur - 5]
    peak_1h = max(
        (row["peak"] for row in minutes if row["minute"] > cur - 60), default=None
    )
    return {
        "limit_1m": FUTURES_IP_WEIGHT_LIMIT_1M,
        "alert_at": int(FUTURES_IP_WEIGHT_LIMIT_1M * ALERT_FRACTION),
        "uptime_sec": int(ts - _boot_ts),
        "peak_last_5m": max(recent) if recent else None,
        "peak_last_1h": peak_1h,
        "peak_since_boot": peak["value"] if peak["ts"] else None,
        "peak_since_boot_at": (
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(peak["ts"]))
            if peak["ts"] else None
        ),
        "peak_since_boot_source": peak["source"] or None,
        "last": {
            s: {
                "value": v["value"],
                "age_sec": int(ts - v["ts"]) if v["ts"] else None,
            }
            for s, v in last.items()
        },
        "signed_calls_since_boot": signed_calls,
        "signed_calls_without_header": no_header,
        "throttled_responses": throttled,
        "last_throttle_age_sec": (
            int(ts - last_throttle["ts"]) if last_throttle["ts"] else None
        ),
        "distinct_uids_signed_this_hour": uids_this_hour,
        "minutes": minutes,
        "note": (
            "X-MBX-USED-WEIGHT-1M is the WHOLE IP's trailing-minute weight, so "
            "each minute's peak is a reading of the fleet total against the "
            "2,400/min futures ban line. 'public' is read on engine REST, "
            "'signed' on the signing service's per-user calls — the same "
            "quantity seen by two processes. Calls without a header are counted "
            "apart and never read as low usage. Measurement only: nothing "
            "throttles on this."
        ),
    }


def budget_health(*, now: Optional[float] = None) -> tuple:
    """Predicate for the ``binance_ip_weight`` liveness probe.

    Violates when a minute in the last five peaked above
    :data:`ALERT_FRACTION` of the limit, or when Binance answered a signed
    call with 418/429 within the last hour. The hour bound is deliberate: a
    since-boot condition would latch red until the next restart, and a red that
    cannot clear is a dead instrument. No reading yet is not a fault — the box
    may simply not have made a futures call — so it passes and says so.
    """
    snap = snapshot(now=now)
    age = snap["last_throttle_age_sec"]
    if age is not None and age < 3600:
        return False, (
            f"Binance throttled a signed call {age}s ago "
            f"(since boot: {snap['throttled_responses']}; "
            f"peak {snap['peak_since_boot']}/{snap['limit_1m']})"
        )
    recent = snap["peak_last_5m"]
    if recent is None:
        return True, "no futures weight reading in the last 5 minutes"
    if recent > snap["alert_at"]:
        return False, (
            f"IP weight peaked at {recent}/{snap['limit_1m']} in the last 5 "
            f"minutes (alert at {snap['alert_at']}); top signed paths: "
            f"{list(snap['signed_calls_since_boot'].items())[:3]}"
        )
    return True, f"peak {recent}/{snap['limit_1m']} over the last 5 minutes"


def _reset_for_tests() -> None:
    global _signed_no_header, _boot_ts
    with _lock:
        _minutes.clear()
        _peak.update(value=0, ts=0.0, source="")
        for s in _SOURCES:
            _last[s] = {"value": None, "ts": 0.0}
        _signed_calls.clear()
        _signed_no_header = 0
        _throttled.clear()
        _last_throttle.update(ts=0.0, status=0)
        _uid_hour["hour"] = 0
        _uid_hour["uids"] = set()
        _boot_ts = time.time()
