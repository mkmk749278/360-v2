"""Feature-liveness probes — "is this feature producing data at the rate its
upstream implies it should?" (the systemic answer to the 2026-07-14 incident).

Eight features died silently because nothing compared each pipeline's OUTPUT
rate against its UPSTREAM driver.  The stop-geometry A/B stamped zero pairs
for 25 hours while the suppression audit — the exact same event stream —
classified hundreds; a single subtraction would have caught it on the first
5-minute cycle.  This module does that subtraction, every cycle, for every
registered feature, and publishes the verdicts where the existing pager can
see them.

Design:

- **RateProbe** — output counter vs upstream counter, both monotonic
  since-boot floats supplied as zero-argument callables (in-memory reads
  only).  A cycle is *violating* when the upstream advanced by at least
  ``min_upstream_delta`` while the output advanced by zero.  Violations must
  persist for ``min_streak`` consecutive cycles before they alert — a quiet
  market never pages, only a flowing upstream with a dead output does.
- **PredicateProbe** — arbitrary ``fn() -> (ok, detail)`` for value checks
  (context publish freshness, ATR-percentile present, candle coverage, BTC
  reference price readable), same streak discipline.
- **Fail-open telemetry** (:mod:`src.fail_open`) rides along: any site whose
  counter grew this cycle increments a per-site streak; sustained growth or
  a burst alerts.  This is what makes a swallowed exception impossible to
  hide — the geometry-A/B bug would have alerted on the first cycle's burst.
- **Boot grace**: no violation accounting for the first
  ``FEATURE_LIVENESS_BOOT_GRACE_SEC`` after engine start (S55 lesson:
  restart storms must not page through warmup).
- Output: ``data/feature_liveness.json`` (atomic write, ~2 KB, local disk,
  once per 5-min audit cycle — no network, no Firestore).  ``alerts`` in the
  payload have already cleared their streak thresholds, so the consumer
  (``scripts/monitor_heartbeat.py``) stays dumb: one ``INVARIANT_WARN`` line
  per entry, and the existing liveness workflow pages Telegram + files the
  auto-detected issue (F-09 wiring — no workflow change needed).

Observe-only: nothing here can alter scanning, scoring, dispatch, or exits.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple, Union

from src import fail_open
from src.utils import get_logger

log = get_logger("feature_liveness")

_DEFAULT_PATH = os.getenv("FEATURE_LIVENESS_PATH", "data/feature_liveness.json")

# A fail-open site alerts when it grew in this many consecutive cycles…
_FAIL_OPEN_STREAK_CYCLES = int(os.getenv("FEATURE_LIVENESS_FAIL_OPEN_STREAK", "3"))
# …or immediately when it grew by at least this much in ONE cycle (a hot loop
# failing every tick — the geometry-A/B signature).
_FAIL_OPEN_BURST_MIN = int(os.getenv("FEATURE_LIVENESS_FAIL_OPEN_BURST", "20"))


@dataclass
class RateProbe:
    """Output-vs-upstream rate expectation."""

    name: str
    counter: Callable[[], Optional[float]]
    upstream: Callable[[], Optional[float]]
    min_upstream_delta: float = 1.0
    min_streak: int = 6  # cycles (×5 min) the violation must persist to alert
    detail: str = ""

    # runtime state
    _last_counter: Optional[float] = field(default=None, repr=False)
    _last_upstream: Optional[float] = field(default=None, repr=False)
    streak: int = field(default=0, repr=False)

    def check(self) -> Tuple[str, str]:
        """Return (status, detail); status ∈ ok|violating|unknown."""
        try:
            cur = self.counter()
            up = self.upstream()
        except Exception as exc:
            fail_open.record(f"feature_liveness.probe.{self.name}", exc)
            return "unknown", f"probe read failed: {exc}"
        if cur is None or up is None:
            return "unknown", "counter unavailable"
        prev_c, prev_u = self._last_counter, self._last_upstream
        self._last_counter, self._last_upstream = cur, up
        if prev_c is None or prev_u is None:
            return "ok", "first cycle"
        c_delta = cur - prev_c
        u_delta = up - prev_u
        if c_delta < 0 or u_delta < 0:  # restart of the counted component
            self.streak = 0
            return "ok", "counter reset"
        if u_delta >= self.min_upstream_delta and c_delta == 0:
            self.streak += 1
            return "violating", (
                f"upstream +{u_delta:g} but output +0 "
                f"(streak {self.streak}/{self.min_streak})"
            )
        self.streak = 0
        return "ok", f"output +{c_delta:g} / upstream +{u_delta:g}"


@dataclass
class PredicateProbe:
    """Arbitrary health predicate: fn() -> (ok, detail)."""

    name: str
    fn: Callable[[], Tuple[bool, str]]
    min_streak: int = 6
    streak: int = field(default=0, repr=False)

    def check(self) -> Tuple[str, str]:
        try:
            ok, detail = self.fn()
        except Exception as exc:
            fail_open.record(f"feature_liveness.probe.{self.name}", exc)
            return "unknown", f"probe read failed: {exc}"
        if ok:
            self.streak = 0
            return "ok", detail
        self.streak += 1
        return "violating", f"{detail} (streak {self.streak}/{self.min_streak})"


class FeatureLiveness:
    """Probe registry + manifest publisher, driven by the 5-min audit loop."""

    def __init__(
        self,
        *,
        path: str = _DEFAULT_PATH,
        boot_grace_sec: Optional[float] = None,
        now: Optional[Callable[[], float]] = None,
    ) -> None:
        from config import FEATURE_LIVENESS_BOOT_GRACE_SEC

        self._path = path
        self._now = now or time.time
        self._started = self._now()
        self._boot_grace = (
            FEATURE_LIVENESS_BOOT_GRACE_SEC
            if boot_grace_sec is None
            else float(boot_grace_sec)
        )
        self._rate_probes: List[RateProbe] = []
        self._predicate_probes: List[PredicateProbe] = []
        self._fail_open_prev: Dict[str, int] = {}
        self._fail_open_streak: Dict[str, int] = {}

    # ---- registration -----------------------------------------------------

    def add_rate(self, probe: RateProbe) -> None:
        self._rate_probes.append(probe)

    def add_predicate(self, probe: PredicateProbe) -> None:
        self._predicate_probes.append(probe)

    # ---- cycle ------------------------------------------------------------

    def run_cycle(self) -> dict:
        """Run every probe once; write + return the manifest (never raises)."""
        try:
            return self._run_cycle_inner()
        except Exception as exc:
            fail_open.record("feature_liveness.run_cycle", exc)
            return {}

    def _run_cycle_inner(self) -> dict:
        ts = self._now()
        in_grace = (ts - self._started) < self._boot_grace
        features: Dict[str, dict] = {}
        alerts: List[dict] = []

        probes: List[Union[RateProbe, PredicateProbe]] = [
            *self._rate_probes,
            *self._predicate_probes,
        ]
        for probe in probes:
            status, detail = probe.check()
            if in_grace and status == "violating":
                # Warmup: track nothing, page nothing — but say so honestly.
                probe.streak = 0
                status, detail = "ok", f"boot grace ({detail})"
            features[probe.name] = {
                "status": status,
                "detail": detail,
                "streak": probe.streak,
            }
            if status == "violating" and probe.streak >= probe.min_streak:
                alerts.append(
                    {"feature": probe.name, "detail": detail, "streak": probe.streak}
                )

        fo = fail_open.snapshot()
        for site, entry in fo.items():
            count = int(entry.get("count", 0))  # type: ignore[arg-type]
            delta = count - self._fail_open_prev.get(site, 0)
            self._fail_open_prev[site] = count
            if delta <= 0 or in_grace:
                self._fail_open_streak[site] = 0
                continue
            streak = self._fail_open_streak.get(site, 0) + 1
            self._fail_open_streak[site] = streak
            if delta >= _FAIL_OPEN_BURST_MIN or streak >= _FAIL_OPEN_STREAK_CYCLES:
                alerts.append(
                    {
                        "feature": f"fail_open:{site}",
                        "detail": (
                            f"+{delta} fail-open(s) this cycle "
                            f"(total {count}); last: {entry.get('last_error', '')}"
                        ),
                        "streak": streak,
                    }
                )

        payload = {
            "generated_at": ts,
            "generated_at_iso": time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)
            ),
            "boot_grace_active": in_grace,
            "features": features,
            "fail_open": fo,
            "alerts": alerts,
        }
        self._write(payload)
        if alerts:
            log.warning(
                "feature_liveness ALERT: {}",
                "; ".join(f"{a['feature']}: {a['detail']}" for a in alerts),
            )
        return payload

    # ---- persistence ------------------------------------------------------

    def _write(self, payload: dict) -> None:
        if not self._path:
            return
        try:
            dirname = os.path.dirname(self._path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            tmp = self._path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, self._path)
        except Exception as exc:
            fail_open.record("feature_liveness.write", exc)
