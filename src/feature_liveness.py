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

# A fully-gated path is only a fault when the candidates it stopped emitting
# were worth emitting.  Below this pooled counterfactual R (over at least
# ``_GATED_PATH_MIN_N`` suppressed samples) the gates are doing their job and
# zero emissions is the correct outcome, not a dead path.
_GATED_PATH_NEGATIVE_R = float(os.getenv("FEATURE_LIVENESS_GATED_NEGATIVE_R", "-0.10"))
_GATED_PATH_MIN_N = int(os.getenv("FEATURE_LIVENESS_GATED_MIN_N", "200"))


def gated_path_verdict(
    *,
    backlog: float,
    emitted_total: float,
    edge: Optional[Dict[str, float]],
    label: str,
    negative_r: float = _GATED_PATH_NEGATIVE_R,
    min_n: int = _GATED_PATH_MIN_N,
) -> Tuple[bool, str]:
    """Is "generates candidates, emits none" a fault here?  (pure)

    Three outcomes, and the whole point is that they are different:

    * **measured-negative** → healthy.  The gates are refusing candidates that
      lose money; emitting them would cost us.  Reported, never paged.
    * **measured-positive** → violating, and now the alert says what the
      blockage is *costing* instead of only that it exists.
    * **not yet measured** → violating, because an unmeasured silent path is
      exactly the 2026-07-14 failure this module was built for.

    **``edge`` covers POST-SCORING suppressions only, and the verdict says so**
    (2026-08-04).  ``suppression_audit.feeds_edge_matrix`` excludes every
    pre-scoring reject — ``setup_compat:*`` and ``execution:*`` fire ahead of
    the scoring engine — so a path whose output is being stopped *there* reads
    as "correctly gated" or "costing us" on a population that never contained
    the gate doing the stopping.  MEAN_REVERT is the live example: 8,472
    pre-scoring rejects in the 2026-08-04 window against a matter of hundreds
    post-scoring, and its dark-lane rows (all pre-scoring, disjoint from this
    edge by construction) measure −0.66% while this edge reads +0.50R.  Neither
    number is wrong and they are not in conflict; they describe different
    candidates.  Naming the population on the verdict is what keeps the next
    reader from treating one as a check on the other — which is the mistake
    this docstring exists to prevent, made once already.

    This does not silence a detected problem — the detection is unchanged and
    the state is always reported.  It reclassifies it using a measurement that
    was available all along, so a page means money is being left on the table
    rather than "a gate is working".
    """
    if edge is None or int(edge.get("n", 0)) < min_n:
        seen = 0 if edge is None else int(edge.get("n", 0))
        return False, (
            f"{backlog:g} detections since last emission (emitted_total={emitted_total:g}) "
            f"— and only {seen} POST-SCORING suppressed samples measured (need {min_n}), so we "
            f"cannot tell a dead path from a correctly-gated one. Pre-scoring rejects "
            f"(setup_compat:* / execution:*) are NOT in this population — check the dark "
            f"lane and the gate-reject counters for those."
        )
    avg_r = float(edge.get("avg_r", 0.0))
    n = int(edge.get("n", 0))
    if avg_r <= negative_r:
        return True, (
            f"fully gated, and correctly: {label} POST-SCORING counterfactuals measure "
            f"{avg_r:+.2f}R over n={n} — emitting them would lose money "
            f"(pre-scoring rejects are measured in the dark lane, not here)"
        )
    return False, (
        f"{backlog:g} detections since last emission (emitted_total={emitted_total:g}) "
        f"— and the POST-SCORING blocked candidates measure {avg_r:+.2f}R over n={n}, "
        f"so that gating is COSTING us. Check gate rejections — but confirm the "
        f"output is actually being stopped post-scoring before loosening anything: "
        f"pre-scoring rejects are a different, disjoint population measured in the "
        f"dark lane."
    )

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
