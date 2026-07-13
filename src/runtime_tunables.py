"""Runtime tunables — ops-controlled engine parameters, no env edits needed.

Owner directive 2026-07-07: every new money-path behaviour ships ACTIVE with
its knobs surfaced on the 360 CE Ops control panel instead of requiring manual
`.env` changes + redeploys on the VPS.  This module is the single registry and
read/write path for those knobs.

Design (mirrors the kill-switch ``signal_expiry_enabled`` pattern):

- **Firestore-persisted** on one doc (``control/runtime_tunables``) so values
  survive engine restarts and are shared across the engine + api containers.
- **5s whole-doc cache** — consumers call :func:`get` from scan / monitor hot
  paths, so reads must never hit Firestore per-signal (Cost Discipline).  One
  read per TTL covers every tunable.
- **Env boot defaults** — each tunable falls back to its config env default
  when the doc/field is absent or Firestore isn't wired (single-process mode,
  tests, dev boots).  ``get`` never raises.
- **Typed registry** — the ops panel renders from :func:`registry_snapshot`,
  so adding a tunable here is the *only* step needed to surface it in ops.

Writes go through :func:`set_values` (owner-gated at the API layer): values
are validated + coerced against the registry, written with merge=True, and
the cache is invalidated so the engine sees the change within one TTL.
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from src.utils import get_logger

log = get_logger("runtime_tunables")

_DOC_PATH = ("control", "runtime_tunables")
_CACHE_TTL_S = 5.0


@dataclass(frozen=True)
class Tunable:
    """One ops-controllable engine parameter."""

    key: str
    label: str
    description: str
    type: str                      # "bool" | "float" | "int"
    default: Any                   # env boot default (config value)
    category: str                  # ops panel grouping
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: str = ""


def _build_registry() -> Dict[str, Tunable]:
    # Imported lazily so config env parsing happens once at first use and
    # test overrides of config values are honoured.
    from config import (
        ACTIVE_DUP_GUARD_ENABLED,
        ALLOCATOR_RECOMMEND_ENABLED,
        BE_ARM_NOISE_MULT,
        BE_ARM_R_MULT,
        BE_ARM_TP1_CAP_FRACTION,
        BE_PARK_TOLERANCE_PCT,
        BE_SHIFT_TRIGGER_PCT,
        BE_THEN_TP1_DEFAULT_ENABLED,
        COHORT_EDGE_GATE_ENABLED,
        COHORT_EDGE_GATE_MIN_N,
        COHORT_EDGE_SUPPRESS_BELOW,
        GEOMETRY_AB_ENABLED,
        LOSS_STREAK_CAP_HOURS,
        LOSS_STREAK_ESCALATION_ENABLED,
        MARKET_CONTEXT_ENABLED,
        MARK_FEED_STALENESS_ENABLED,
        MARK_FEED_STALENESS_MAX_AGE_SEC,
        MOVER_AVWAP_SCALP_ENABLED,
        MOVER_RUNNER_EXIT_ENABLED,
        MOVER_TREND_PULLBACK_ENABLED,
        NOISE_FLOOR_ATR_MULT,
        NOISE_FLOOR_MAX_SL_PCT,
        NOISE_FLOOR_STOPS_ENABLED,
        SHADOW_STRATEGIES_ENABLED,
        SUPPRESSION_AUDIT_ENABLED,
    )

    items = [
        Tunable(
            key="noise_floor_stops_enabled",
            label="Noise-floor stops",
            description=(
                "Widen every stop to clear the pair's own recent volatility "
                "(the 1h ATR noise band) before it ships. The 7d study showed "
                "52% of stops were shaken out and recovered within 1 hour — "
                "stops narrower than the noise band are coin flips. Position "
                "notional is scaled down by the same factor, so the money "
                "risked per trade DOES NOT change."
            ),
            type="bool",
            default=NOISE_FLOOR_STOPS_ENABLED,
            category="Stops & exits",
        ),
        Tunable(
            key="noise_floor_atr_mult",
            label="Noise floor × ATR(1h)",
            description=(
                "Minimum stop distance as a multiple of the pair's 1-hour ATR. "
                "1.0 = the stop must be at least one hour of typical movement "
                "away from entry. Raise for fewer, later stops; lower toward "
                "0 to trust evaluator geometry more."
            ),
            type="float",
            default=NOISE_FLOOR_ATR_MULT,
            category="Stops & exits",
            min_value=0.0,
            max_value=3.0,
            unit="× ATR",
        ),
        Tunable(
            key="noise_floor_max_sl_pct",
            label="Noise floor cap",
            description=(
                "Hard ceiling on how far the noise floor may push a stop, as % "
                "of entry price. Protects margin at leverage regardless of how "
                "volatile the pair is."
            ),
            type="float",
            default=NOISE_FLOOR_MAX_SL_PCT,
            category="Stops & exits",
            min_value=0.5,
            max_value=5.0,
            unit="%",
        ),
        Tunable(
            key="be_shift_enabled",
            label="Break-even ratchet",
            description=(
                "Once a trade has been in profit past the arm threshold, "
                "ratchet the stop to protect the position. The arm threshold "
                "and park position are the two knobs below."
            ),
            type="bool",
            default=BE_THEN_TP1_DEFAULT_ENABLED,
            category="Stops & exits",
        ),
        Tunable(
            key="be_arm_trigger_pct",
            label="BE arm: flat trigger",
            description=(
                "Legacy flat arm threshold (% in profit). The ratchet arms at "
                "the LARGEST of this, the R-multiple arm, and the noise arm — "
                "so on volatile pairs the effective threshold is noise-aware, "
                "not this flat 1%."
            ),
            type="float",
            default=BE_SHIFT_TRIGGER_PCT,
            category="Stops & exits",
            min_value=0.1,
            max_value=5.0,
            unit="%",
        ),
        Tunable(
            key="be_arm_r_mult",
            label="BE arm: R multiple",
            description=(
                "Arm the break-even ratchet only after the trade has moved this "
                "many R (multiples of its own stop distance) in profit. 1.0 = "
                "one full stop-distance in profit. The 7d study: 84% of BE "
                "scratches armed too early and the move resumed without us."
            ),
            type="float",
            default=BE_ARM_R_MULT,
            category="Stops & exits",
            min_value=0.0,
            max_value=3.0,
            unit="R",
        ),
        Tunable(
            key="be_arm_noise_mult",
            label="BE arm: noise multiple",
            description=(
                "Arm threshold as a multiple of the pair's noise floor (1h "
                "ATR). Keeps the ratchet from arming inside ordinary wick "
                "territory on fast movers."
            ),
            type="float",
            default=BE_ARM_NOISE_MULT,
            category="Stops & exits",
            min_value=0.0,
            max_value=3.0,
            unit="× noise",
        ),
        Tunable(
            key="be_arm_tp1_cap_fraction",
            label="BE arm: TP1 cap",
            description=(
                "Cap the BE arm threshold at this fraction of the trade's own "
                "TP1 distance, so the ratchet always arms before the TP1 "
                "full-close can beat it there. Without the cap, 1R of a "
                "noise-widened 2.4-2.7% stop put the arm at or above TP1 — "
                "unreachable — and +2% runs round-tripped to the full SL with "
                "no BE shift (owner-reported 2026-07-10). Never caps below "
                "the flat trigger. 0 = cap off (pre-fix behaviour)."
            ),
            type="float",
            default=BE_ARM_TP1_CAP_FRACTION,
            category="Stops & exits",
            min_value=0.0,
            max_value=1.0,
            unit="× TP1 dist",
        ),
        Tunable(
            key="be_park_tolerance_pct",
            label="BE park tolerance",
            description=(
                "When armed, park the stop this far on the LOSS side of entry "
                "instead of exactly at entry — a wick that tags the exact "
                "entry price no longer scratches the trade. Worst case the "
                "trade exits at minus this % instead of 0%."
            ),
            type="float",
            default=BE_PARK_TOLERANCE_PCT,
            category="Stops & exits",
            min_value=0.0,
            max_value=1.0,
            unit="%",
        ),
        Tunable(
            key="cohort_edge_gate_enabled",
            label="Cohort-edge gate",
            description=(
                "Suppress signals from cohorts (setup × side × regime family × "
                "BTC macro) whose MEASURED live expectancy is negative with "
                "enough samples. This is what stops a 'textbook-perfect' path "
                "from shipping losers week after week — the score says how "
                "clean the pattern looks; this gate says whether it has "
                "actually been making money."
            ),
            type="bool",
            default=COHORT_EDGE_GATE_ENABLED,
            category="Signal gating",
        ),
        Tunable(
            key="cohort_edge_gate_min_n",
            label="Cohort gate: min samples",
            description=(
                "Minimum resolved signals a cohort needs before the gate may "
                "suppress it. Below this the gate fails open (signal emits)."
            ),
            type="int",
            default=COHORT_EDGE_GATE_MIN_N,
            category="Signal gating",
            min_value=5,
            max_value=100,
        ),
        Tunable(
            key="mark_feed_staleness_enabled",
            label="Mark-feed freshness guard",
            description=(
                "When a live signal's symbol drops out of the scan universe "
                "(surge-promoted movers, intermittently re-scanned pairs), its "
                "1m candle in the store freezes — pinning the monitored price "
                "near entry and silently freezing PnL, peak (MFE) and the "
                "SL/TP backstop on a stale price. With this on, once the last "
                "1m kline is older than the bound below, the monitor prices the "
                "signal off the all-symbols mark feed (1s, every USDT-M pair) "
                "instead of the frozen candle."
            ),
            type="bool",
            default=MARK_FEED_STALENESS_ENABLED,
            category="Stops & exits",
        ),
        Tunable(
            key="mark_feed_staleness_max_age_sec",
            label="Mark-feed freshness bound",
            description=(
                "How old the store's last 1m kline may be before the monitor "
                "switches that signal to the mark feed. Comfortably above the "
                "60s 1m-candle cadence so healthy pairs are never diverted; "
                "low enough to catch a dropped-universe mover within minutes. "
                "A never-stamped kline (fresh boot, seed-loaded) counts as "
                "fresh, mirroring the scanner's dispatch staleness gate."
            ),
            type="float",
            default=MARK_FEED_STALENESS_MAX_AGE_SEC,
            category="Stops & exits",
            min_value=30.0,
            max_value=600.0,
            unit="s",
        ),
        Tunable(
            key="mover_runner_exit_enabled",
            label="Mover runner exit",
            description=(
                "For the two mover continuation paths (MOVER_TREND_PULLBACK, "
                "MOVER_AVWAP_SCALP) only: instead of closing 100% at TP1, bank "
                "40% at TP1, 30% more at TP2 (stop lifts to TP1), and let the "
                "last 30% ride an ATR trail with NO fixed cap — crossing TP3 "
                "is stamped but does not close; the trail is the only exit "
                "for the final slice. A momentum path's edge "
                "is the tail — 42% of mover signals reached ≥1% profit but "
                "realised ≤0 under the 1R full-close (HMSTR ran +31%, banked "
                "0). ACTIVE (owner sign-off 2026-07-09). While off, every "
                "mover TP1 close logs what the runner would have held, and "
                "the Profit page's give-back column measures what it would "
                "have kept."
            ),
            type="bool",
            default=MOVER_RUNNER_EXIT_ENABLED,
            category="Stops & exits",
        ),
        Tunable(
            key="mover_trend_pullback_live",
            label="MOVER_TREND_PULLBACK live",
            description=(
                "Emit MOVER_TREND_PULLBACK signals live. Off = shadow-only: "
                "the evaluator still runs and logs every would-be signal "
                "([SHADOW] MOVER_TREND_PULLBACK_WOULD_FIRE) so the path keeps "
                "measuring while emitting nothing. Jun-01→Jul-05: 97 signals, "
                "−13.5% total, 28% win rate; 3d post-#702: 18 signals, −8.4%."
            ),
            type="bool",
            default=MOVER_TREND_PULLBACK_ENABLED,
            category="Signal gating",
        ),
        Tunable(
            key="mover_avwap_scalp_live",
            label="MOVER_AVWAP_SCALP live",
            description=(
                "Emit MOVER_AVWAP_SCALP signals live. Off = shadow-only "
                "([SHADOW] MOVER_AVWAP_SCALP_WOULD_FIRE log, no signal). "
                "Across Jun-01→Jul-09 this path emitted 20 signals with zero "
                "TP hits and zero SL hits — every one expired; pure fee drag "
                "as currently shaped."
            ),
            type="bool",
            default=MOVER_AVWAP_SCALP_ENABLED,
            category="Signal gating",
        ),
        Tunable(
            key="loss_streak_escalation_enabled",
            label="Loss-streak cooldown escalation",
            description=(
                "Double the post-loss dispatch cooldown per consecutive "
                "losing outcome on the same symbol × setup × direction (SL "
                "1h → 2h → 4h …, capped below), so the scanner stops "
                "re-entering the same failing setup every time the flat "
                "cooldown lapses (MONUSDT pullback longs: 6 dispatches, "
                "−3.7% in 3 days). A profitable outcome resets the streak; "
                "breakeven scratches leave it unchanged. ACTIVE (owner "
                "sign-off 2026-07-09); while off, would-be extensions are "
                "shadow-logged."
            ),
            type="bool",
            default=LOSS_STREAK_ESCALATION_ENABLED,
            category="Signal gating",
        ),
        Tunable(
            key="loss_streak_cap_hours",
            label="Loss-streak cooldown cap",
            description=(
                "Upper bound on the escalated cooldown so a long losing "
                "streak can never lock a setup out for days — conditions "
                "change and the cohort-edge gate owns permanent suppression."
            ),
            type="float",
            default=LOSS_STREAK_CAP_HOURS,
            category="Signal gating",
            min_value=1.0,
            max_value=48.0,
            unit="h",
        ),
        Tunable(
            key="active_dup_guard_enabled",
            label="Active-duplicate guard",
            description=(
                "Block a dispatch when the live signal book already holds an "
                "open signal with the same symbol × setup × direction. The "
                "30-min dispatch cooldown intends this but doesn't survive "
                "every restart path (SPCXUSDT mover short emitted twice, 7 "
                "min apart, identical entry/SL). ACTIVE (owner sign-off "
                "2026-07-09); while off, would-be blocks are shadow-logged."
            ),
            type="bool",
            default=ACTIVE_DUP_GUARD_ENABLED,
            category="Signal gating",
        ),
        Tunable(
            key="cohort_edge_suppress_below",
            label="Cohort gate: suppress below",
            description=(
                "Suppress when the cohort's Wilson-lower-bounded expectancy "
                "(% per trade) is at or below this. -0.05 means: only block "
                "cohorts measurably losing money, never marginal ones."
            ),
            type="float",
            default=COHORT_EDGE_SUPPRESS_BELOW,
            category="Signal gating",
            min_value=-2.0,
            max_value=0.0,
            unit="%/trade",
        ),
        # -- Measurement (all observe-only; none change live signal output) --
        Tunable(
            key="market_context_enabled",
            label="Market-context stamping",
            description=(
                "Compute and stamp the market-context vector (session / "
                "Wyckoff phase / volatility / funding / BTC rotation) on "
                "every signal, and publish the current global vector for "
                "ops. Observe-only: nothing consumes it to change live "
                "output — it is the key the Strategy×Context edge matrix "
                "and the allocator route on."
            ),
            type="bool",
            default=MARKET_CONTEXT_ENABLED,
            category="Measurement",
        ),
        Tunable(
            key="suppression_audit_enabled",
            label="Suppression quality audit",
            description=(
                "Record every post-scoring gate-suppressed candidate and "
                "forward-measure on real candles whether it WOULD have won "
                "— per-gate KEEP/TUNE/DROP verdicts plus the shadow feed "
                "of the Strategy×Context edge matrix. Observe-only; O(1) "
                "in-memory stamps, no hot-path I/O."
            ),
            type="bool",
            default=SUPPRESSION_AUDIT_ENABLED,
            category="Measurement",
        ),
        Tunable(
            key="shadow_strategies_enabled",
            label="Shadow strategy units",
            description=(
                "Run the shadow-only strategy units (range-fade, "
                "mean-revert, funding-fade, cascade-reversal) whose "
                "would-be trades enter the shadow ledger and edge matrix. "
                "They have no path to the signal queue — pure measurement "
                "of candidate strategies against live ones."
            ),
            type="bool",
            default=SHADOW_STRATEGIES_ENABLED,
            category="Measurement",
        ),
        Tunable(
            key="geometry_ab_enabled",
            label="Stop-geometry A/B",
            description=(
                "Stamp every post-scoring candidate (emitted and "
                "gate-suppressed) as a counterfactual pair — its live "
                "fixed-% stop vs an ATR/structure stop beyond the "
                "liquidity pool — and forward-measure both identically, "
                "so the edge matrix shows which geometry wins per "
                "strategy and context. Observe-only: live stops are "
                "untouched; applying a winner is a separate dark-first, "
                "owner-signed change."
            ),
            type="bool",
            default=GEOMETRY_AB_ENABLED,
            category="Measurement",
        ),
        Tunable(
            key="allocator_recommend_enabled",
            label="Allocator (recommendation mode)",
            description=(
                "Every audit cycle, compute which strategies the allocator "
                "WOULD activate and how it would weight them in the "
                "current market context, from the measured edge matrix — "
                "persisted for ops only. Nothing consumes the "
                "recommendation; live promotion stays owner-armed."
            ),
            type="bool",
            default=ALLOCATOR_RECOMMEND_ENABLED,
            category="Measurement",
        ),
    ]
    return {t.key: t for t in items}


class RuntimeTunables:
    """Cached Firestore-backed tunable store.  Thread-safe."""

    def __init__(self, firestore_client: Any, clock: Callable[[], float] = time.monotonic) -> None:
        self._db = firestore_client
        self._clock = clock
        self._lock = threading.Lock()
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_read_at: float = 0.0

    # ---- read path (hot, cached) ----------------------------------------

    def _doc_values(self) -> Dict[str, Any]:
        with self._lock:
            now = self._clock()
            if self._cache is not None and (now - self._cache_read_at) < _CACHE_TTL_S:
                return self._cache
        values: Dict[str, Any] = {}
        try:
            doc = (
                self._db.collection(_DOC_PATH[0]).document(_DOC_PATH[1]).get()
            )
            if getattr(doc, "exists", False):
                values = dict(doc.to_dict() or {})
        except Exception:
            log.exception("runtime_tunables doc read failed — using env defaults")
            values = {}
        with self._lock:
            self._cache = values
            self._cache_read_at = self._clock()
        return values

    def get(self, key: str) -> Any:
        reg = registry()
        tun = reg.get(key)
        if tun is None:
            raise KeyError(f"unknown tunable: {key}")
        raw = self._doc_values().get(key)
        if raw is None:
            return tun.default
        coerced = _coerce(tun, raw)
        return coerced if coerced is not None else tun.default

    # ---- write path (owner action, rare) ---------------------------------

    def set_values(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate + persist ``updates``.  Returns the coerced values written.

        Raises ``ValueError`` on any unknown key or out-of-range value —
        all-or-nothing so the ops panel can show one clear error.
        """
        from datetime import datetime, timezone

        reg = registry()
        coerced: Dict[str, Any] = {}
        for key, raw in updates.items():
            tun = reg.get(key)
            if tun is None:
                raise ValueError(f"unknown tunable: {key}")
            value = _coerce(tun, raw)
            if value is None:
                raise ValueError(f"{key}: cannot parse {raw!r} as {tun.type}")
            if tun.type in ("float", "int"):
                if tun.min_value is not None and value < tun.min_value:
                    raise ValueError(f"{key}: {value} below minimum {tun.min_value}")
                if tun.max_value is not None and value > tun.max_value:
                    raise ValueError(f"{key}: {value} above maximum {tun.max_value}")
            coerced[key] = value
        if not coerced:
            return {}
        payload = dict(coerced)
        payload["updated_at"] = datetime.now(timezone.utc)
        self._db.collection(_DOC_PATH[0]).document(_DOC_PATH[1]).set(
            payload, merge=True
        )
        with self._lock:
            self._cache = None
        log.info("runtime_tunables updated: {}", coerced)
        return coerced


def _coerce(tun: Tunable, raw: Any) -> Any:
    try:
        if tun.type == "bool":
            if isinstance(raw, bool):
                return raw
            return str(raw).strip().lower() in ("1", "true", "yes", "on")
        if tun.type == "int":
            return int(float(raw))
        if tun.type == "float":
            return float(raw)
    except (TypeError, ValueError):
        return None
    return None


# ---- module-level singleton (kill-switch pattern) -------------------------

_lock = threading.Lock()
_client: Optional[RuntimeTunables] = None
_registry: Optional[Dict[str, Tunable]] = None


def registry() -> Dict[str, Tunable]:
    global _registry
    with _lock:
        if _registry is None:
            _registry = _build_registry()
        return _registry


def init_runtime_tunables(firestore_client: Any) -> None:
    global _client
    with _lock:
        _client = RuntimeTunables(firestore_client)
    log.info("runtime_tunables initialised (Firestore-backed)")


def is_initialised() -> bool:
    with _lock:
        return _client is not None


def get(key: str) -> Any:
    """Hot-path safe accessor: env default when Firestore isn't wired,
    cached doc value otherwise.  Never raises on read failures."""
    with _lock:
        client = _client
    if client is None:
        tun = registry().get(key)
        if tun is None:
            raise KeyError(f"unknown tunable: {key}")
        return tun.default
    try:
        return client.get(key)
    except KeyError:
        raise
    except Exception:  # pragma: no cover — defensive: never break scan/monitor
        log.exception("runtime_tunables get({}) failed — using default", key)
        return registry()[key].default


def set_values(updates: Dict[str, Any]) -> Dict[str, Any]:
    with _lock:
        client = _client
    if client is None:
        raise RuntimeError(
            "runtime tunables not initialised (no Firestore/GCP creds)"
        )
    return client.set_values(updates)


def snapshot() -> List[Dict[str, Any]]:
    """Registry + current effective values, for the ops panel."""
    out: List[Dict[str, Any]] = []
    for tun in registry().values():
        out.append(
            {
                "key": tun.key,
                "label": tun.label,
                "description": tun.description,
                "type": tun.type,
                "default": tun.default,
                "value": get(tun.key),
                "min": tun.min_value,
                "max": tun.max_value,
                "unit": tun.unit,
                "category": tun.category,
            }
        )
    return out


def reset_for_test() -> None:
    global _client, _registry
    with _lock:
        _client = None
        _registry = None
