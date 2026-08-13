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
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.utils import get_logger

log = get_logger("runtime_tunables")

_DOC_PATH = ("control", "runtime_tunables")
_CACHE_TTL_S = 5.0
# Warn (throttled to its own interval) once the served cache is this stale —
# it means the background Firestore refresh keeps failing.
_STALE_WARN_S = 60.0


@dataclass(frozen=True)
class Tunable:
    """One ops-controllable engine parameter."""

    key: str
    label: str
    description: str
    type: str                      # "bool" | "float" | "int" | "str"
    default: Any                   # env boot default (config value)
    category: str                  # ops panel grouping
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: str = ""
    #: For a ``str`` tunable whose valid values are a closed set. When present
    #: ``set_values`` REFUSES anything outside it and ops renders a select
    #: rather than a text box.
    #:
    #: Added 2026-08-10 after ``trail_governor_timeframe`` was stored as
    #: ``"5"``. It has exactly two valid values, shipped as free text, and
    #: ``set_values`` range-checks only float/int — so an invalid value was
    #: accepted, and the live trail governor then refused every position with
    #: ``no_series`` (the candle store is keyed ``"5m"``/``"15m"``, so
    #: ``get_candles(sym, "5")`` is None forever). A typo became a permanently
    #: inert money-path mechanism reporting a candle-feed fault.
    choices: Optional[Tuple[str, ...]] = None


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
        BTC_DIR_PENALTY_APPLY,
        COHORT_EDGE_GATE_ENABLED,
        CONTEXT_EMISSION_COHORT_AWARE,
        CONTEXT_EMISSION_GATE_OVERRIDE_ENABLED,
        CONTEXT_EMISSION_GATE_OVERRIDE_LIVE,
        CONTEXT_EMISSION_LIVE,
        DISPATCH_STALENESS_V2_ENABLED,
        DISPATCH_STALENESS_V2_LIVE,
        DISPATCH_STALENESS_V2_TOWARD_SL_MAX_FRAC,
        DISPATCH_STALENESS_V2_TOWARD_TP_MAX_FRAC,
        ENTRY_QUALITY_BUDGET_WINDOW,
        ENTRY_QUALITY_ENABLED,
        ENTRY_QUALITY_LIVE,
        ENTRY_QUALITY_MAX_REJECT_FRAC,
        ENTRY_QUALITY_RULE_LIVE,
        ENTRY_QUALITY_RULE_THRESHOLD,
        CONTEXT_EMISSION_MIN_SAMPLES,
        CONTEXT_EMISSION_POLICY_ENABLED,
        CONTEXT_EMISSION_POSITIVE_RELAX,
        CONTEXT_EMISSION_QUALITY_ANCHOR,
        CONTEXT_EMISSION_STRONG_RELAX,
        CONTEXT_EMISSION_SUPPRESS_NEGATIVE,
        FEATURE_LIVENESS_ENABLED,
        COHORT_EDGE_GATE_MIN_N,
        COHORT_EDGE_MAX_AGE_DAYS,
        COHORT_EDGE_SUPPRESS_BELOW,
        DISPATCH_COOLDOWN_ENABLED,
        DISPATCH_COOLDOWN_SEC,
        GEOMETRY_AB_ENABLED,
        SAR_EXIT_SHADOW_ENABLED,
        STALE_TF_REFUSE_ENABLED,
        TRACK_RECORD_PUBLIC_ENABLED,
        TUNED_VARIANTS_ENABLED,
        LOSS_STREAK_CAP_HOURS,
        LOSS_STREAK_ESCALATION_ENABLED,
        MARKET_CONTEXT_ENABLED,
        MANUAL_TRADE_BUILDER_ENABLED,
        MARK_FEED_STALENESS_ENABLED,
        MARK_FEED_STALENESS_MAX_AGE_SEC,
        MEAN_REVERT_LIVE,
        RANGE_FADE_LIVE,
        MOVER_AVWAP_SCALP_ENABLED,
        MOVER_RUNNER_EXIT_ENABLED,
        MOVER_TREND_PULLBACK_ENABLED,
        NOISE_FLOOR_ATR_MULT,
        NOISE_FLOOR_MAX_SL_PCT,
        NOISE_FLOOR_STOPS_ENABLED,
        DARK_EMISSION_ENABLED,
        DARK_PROMOTION_ENABLED,
        MOVER_RETENTION_ENFORCE,
        PRESCORING_AUDIT_ENABLED,
        SETUP_TF_CORRECTION_LIVE,
        SHADOW_STRATEGIES_ENABLED,
        STRUCTURAL_SNAP_APPLY,
        STRUCTURAL_SNAP_APPLY_PATHS,
        STRUCTURAL_SNAP_MEASURE,
        SUPPRESSION_AUDIT_ENABLED,
        TRAIL_GOVERNOR_ENABLED,
        TRAIL_GOVERNOR_TIMEFRAME,
    )

    items = [
        Tunable(
            key="setup_tf_correction_live",
            label="Per-setup timeframe correction (money path)",
            description=(
                "Compute the sweep / VWAP / OI / volume-divergence / pattern / "
                "composite-score inputs on the timeframe each setup actually "
                "TRADES, instead of always 5m. MOVER_TREND_PULLBACK is ~59% of "
                "the book and trades 15m, so flipping this changes scoring for "
                "most of the feed at once. The mismatch census runs whether or "
                "not this is on — read it at /signals/structural-snap before "
                "flipping. Owner sign-off item."
            ),
            type="bool",
            default=SETUP_TF_CORRECTION_LIVE,
            category="Signal gating",
        ),
        Tunable(
            key="structural_snap_measure",
            label="Structural snap — measure",
            description=(
                "Stamp, on every enqueued signal, where the nearest swing "
                "high/low or round number sits relative to the stop and TP1 "
                "the evaluator computed arithmetically. Measurement only: this "
                "flag never moves a level. Read the result at "
                "/signals/structural-snap."
            ),
            type="bool",
            default=STRUCTURAL_SNAP_MEASURE,
            category="Measurement",
        ),
        Tunable(
            key="structural_snap_apply",
            label="Structural snap — APPLY (money path)",
            description=(
                "Master switch: let the snap actually move the stop and TP1 "
                "that ship. Does nothing on its own — a path must ALSO be "
                "named in the allow-list below. The stop can move by at most "
                "±30% of the designed risk and TP1 only ever moves NEARER, so "
                "this cannot widen a target. Owner sign-off item."
            ),
            type="bool",
            default=STRUCTURAL_SNAP_APPLY,
            category="Stops & exits",
        ),
        Tunable(
            key="structural_snap_apply_paths",
            label="Structural snap — paths allowed to apply",
            description=(
                "Comma-separated setup classes, e.g. "
                "'SR_FLIP_RETEST,FAILED_AUCTION_RECLAIM'. Empty = none. Kept "
                "separate from the master switch so a result measured on one "
                "path cannot silently flip the other eighteen."
            ),
            type="str",
            default=STRUCTURAL_SNAP_APPLY_PATHS,
            category="Stops & exits",
        ),
        Tunable(
            key="trail_governor_enabled",
            label="Live trail governor — PLACES REAL ORDERS",
            description=(
                "The only switch on this page that moves a real stop order. "
                "ON = for each open position whose USER has opted into a trail "
                "mechanism (per-user exit_mechanism column), the engine parks "
                "the mechanism's stop once it comes onside, cancels the "
                "evaluator's SL and TP ladder at that handover, and re-places "
                "the stop on every closed bar (place-then-cancel, so the "
                "position is never naked). OFF = every position keeps the SL/TP "
                "FSM exit, unchanged. This flag AND a per-user opt-in are both "
                "required: ON with nobody opted in governs nothing. Enabled "
                "2026-08-10 for an owner-only live test — the measured edge "
                "over the current exit does NOT exclude zero, so this is a "
                "canary, not a rollout."
            ),
            type="bool",
            default=TRAIL_GOVERNOR_ENABLED,
            category="Stops & exits",
        ),
        Tunable(
            key="trail_governor_timeframe",
            label="Live trail governor — governing timeframe",
            description=(
                "Which arm owns the real stop: 5m or 15m. The measurement lane "
                "runs both as independent arms on the same signal, but only one "
                "can own an order. The other keeps recording in the shadow "
                "lane, so the timeframe comparison survives the live test. "
                "Changing this re-parks on the next closed bar of the new "
                "timeframe; it never leaves a position unprotected."
            ),
            type="str",
            default=TRAIL_GOVERNOR_TIMEFRAME,
            choices=("5m", "15m"),
            category="Stops & exits",
        ),
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
            key="cohort_edge_max_age_days",
            label="Cohort gate: evidence expiry",
            description=(
                "How long a resolved outcome counts as evidence. Past this "
                "age it stops counting, so a suppressed cohort — which emits "
                "nothing and therefore resolves nothing — falls back below "
                "the sample floor and is re-tested on live fills instead of "
                "being locked out on the day it first measured negative. "
                "0 disables expiry (a verdict then lasts forever)."
            ),
            type="float",
            default=COHORT_EDGE_MAX_AGE_DAYS,
            category="Signal gating",
            min_value=0.0,
            max_value=90.0,
            unit="days",
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
            key="mean_revert_live",
            label="MEAN_REVERT live",
            description=(
                "Emit MEAN_REVERT signals live (fade a 2.5σ 15m extension "
                "back to the 20-bar mean, ±1.5·ATR stop). Graduated from "
                "SHADOW_MEAN_REVERT: +0.67R avg / 59% win over n=550 "
                "forward-measured candidates across two windows — the "
                "shadow-window evidence dark-first requires; owner directed "
                "live activation 2026-07-15. Off = shadow-only ([SHADOW] "
                "MEAN_REVERT_WOULD_FIRE log, no signal); the shadow unit "
                "keeps stamping as the ungated control arm either way."
            ),
            type="bool",
            default=MEAN_REVERT_LIVE,
            category="Signal gating",
        ),
        Tunable(
            key="range_fade_live",
            label="RANGE_FADE live (context-gated)",
            description=(
                "Emit RANGE_FADE signals live (fade a ≥2-touch range edge "
                "back to the mid; range = 48×15m ≥ 4·ATR wide, stop 1·ATR "
                "beyond the edge). Graduated DARK from SHADOW_RANGE_FADE — "
                "the Strategy Lab allocator's top pick in range/quiet "
                "contexts (+0.841R n=24 ASIA/QUIET/NORMAL; +0.885R n=15 "
                "OVERLAP/RANGE/NORMAL) — but blanket activation measured "
                "net-negative (gate audit +0.20R/suppression, n=223), so "
                "even when ON it emits only in contexts whose shadow cell "
                "verdict is STRONG (context-edge gate; env-relaxable to "
                "POSITIVE). Off = shadow-only ([SHADOW] "
                "RANGE_FADE_WOULD_FIRE log, no signal); the shadow unit "
                "keeps stamping as the ungated control arm either way."
            ),
            type="bool",
            default=RANGE_FADE_LIVE,
            category="Signal gating",
        ),
        # ── Context-adaptive emission policy (Layer C → emission) ──────────
        # The autonomous best-signal mechanism: the measured edge matrix drives
        # a per-(strategy×context) confidence floor.  LIVE by owner directive
        # 2026-07-19 with full ops control — `context_emission_enabled` is the
        # instant kill, `context_emission_live` toggles apply vs measure-only,
        # and the anchor/relax/samples knobs shape it without a redeploy.
        Tunable(
            key="context_emission_enabled",
            label="Context emission policy",
            description=(
                "Master switch for the context-adaptive emission policy: the "
                "measured Strategy×Context edge matrix drives the confidence "
                "floor per (strategy, context) — relax the floor in cells "
                "measured STRONG/POSITIVE so a path emits its best setups where "
                "it wins, hard-suppress NEGATIVE cells so it stays silent where "
                "it loses, leave the global floor untouched on cold/thin cells. "
                "OFF = the single global floor decides everything (pre-policy "
                "behaviour). Generalises the RANGE_FADE context gate to every "
                "strategy. See docs/PLAN_AUTONOMOUS_EMISSION.md."
            ),
            type="bool",
            default=CONTEXT_EMISSION_POLICY_ENABLED,
            category="Signal gating",
        ),
        Tunable(
            key="context_emission_live",
            label="Context emission — apply live",
            description=(
                "ON = the policy's per-context floor is APPLIED to live "
                "emission (relax STRONG cells, suppress NEGATIVE cells). OFF = "
                "measure-only: the would-be decision is stamped and logged "
                "([CONTEXT_FLOOR_SHADOW]) for the Strategy Lab but live output "
                "is unchanged — the safe way to preview the policy on a real "
                "window before it changes what subscribers see."
            ),
            type="bool",
            default=CONTEXT_EMISSION_LIVE,
            category="Signal gating",
        ),
        Tunable(
            key="context_emission_quality_anchor",
            label="Context emission — quality anchor",
            description=(
                "Absolute confidence floor the policy will never relax below, "
                "no matter how strong a cell measures — paid-tier integrity by "
                "construction. Raise toward the 65 base to shrink the relax "
                "side (65 = suppress-only, no relaxation); lower for more "
                "breadth in proven cells."
            ),
            type="float",
            default=CONTEXT_EMISSION_QUALITY_ANCHOR,
            category="Signal gating",
            min_value=50.0,
            max_value=75.0,
        ),
        Tunable(
            key="context_emission_strong_relax",
            label="Context emission — STRONG relax (pts)",
            description=(
                "Max confidence points to lower the floor in a STRONG cell "
                "(clamped at the quality anchor). 5 = a STRONG cell emits down "
                "to ~60 off a 65 base."
            ),
            type="float",
            default=CONTEXT_EMISSION_STRONG_RELAX,
            category="Signal gating",
            min_value=0.0,
            max_value=15.0,
        ),
        Tunable(
            key="context_emission_positive_relax",
            label="Context emission — POSITIVE relax (pts)",
            description=(
                "Max confidence points to lower the floor in a POSITIVE cell "
                "(clamped at the quality anchor). Kept below the STRONG relax so "
                "a merely-positive cell emits a narrower, higher-bar slice."
            ),
            type="float",
            default=CONTEXT_EMISSION_POSITIVE_RELAX,
            category="Signal gating",
            min_value=0.0,
            max_value=15.0,
        ),
        Tunable(
            key="context_emission_min_samples",
            label="Context emission — min samples to relax",
            description=(
                "Relaxation requires at least this many forward-measured "
                "outcomes in the cell (stricter than the edge-matrix floor of "
                "15 — we only lower the bar on well-populated evidence). "
                "Suppression of NEGATIVE cells uses the matrix's own floor."
            ),
            type="int",
            default=CONTEXT_EMISSION_MIN_SAMPLES,
            category="Signal gating",
            min_value=15,
            max_value=200,
        ),
        Tunable(
            key="context_emission_suppress_negative",
            label="Context emission — suppress NEGATIVE cells",
            description=(
                "ON = a path is hard-suppressed in any context where its "
                "measured edge is NEGATIVE (the protective, RANGE_FADE-gate "
                "side — strictly removes measured losers). OFF = relax-only "
                "(never suppress on context)."
            ),
            type="bool",
            default=CONTEXT_EMISSION_SUPPRESS_NEGATIVE,
            category="Signal gating",
        ),
        Tunable(
            key="context_emission_cohort_aware",
            label="Context emission — pair-cohort aware",
            description=(
                "ON = the policy looks up the pair-cohort-refined cell "
                "(context_key + liquidity tier MAJOR/MIDCAP/ALTCOIN) first, "
                "falling back to the base cell when the cohort cell is thin — "
                "so a path's floor adapts to how it performs on *this kind of "
                "pair* in this context. Cohort cells accumulate in parallel "
                "regardless (additive, never fragments the base matrix); flip "
                "this ON once they have samples. OFF = base context cell only."
            ),
            type="bool",
            default=CONTEXT_EMISSION_COHORT_AWARE,
            category="Signal gating",
        ),
        # ── W5 — gate override + dispatch-staleness V2 (2026-07-23) ────────
        # Both attack the two audited-negative dispatch gates
        # (dispatch_staleness EV −0.19R n=1225 · level_still_in_play EV
        # −0.06R n=989).  Measurement flags default ON (observe-only); the
        # *_live flags are DARK and flip only on owner sign-off over the
        # @DSV2 / @GOV shadow rows in the Strategy Lab.
        Tunable(
            key="context_emission_gate_override_enabled",
            label="Gate override — measure",
            description=(
                "ON = when a STRONG-cell candidate is blocked by "
                "dispatch_staleness or level_still_in_play, stamp the would-be "
                "rescue as an X@GOV shadow arm (entry re-anchored at "
                "dispatch-time price) so the edge matrix measures what the "
                "override would be worth. Never changes live emission by "
                "itself. OFF = no measurement."
            ),
            type="bool",
            default=CONTEXT_EMISSION_GATE_OVERRIDE_ENABLED,
            category="Signal gating",
        ),
        Tunable(
            key="context_emission_gate_override_live",
            label="Gate override — apply live",
            description=(
                "ON = a STRONG-cell candidate (adequate sample, positive "
                "measured edge) actually overrides a dispatch_staleness / "
                "level_still_in_play block and emits. Safety gates are never "
                "overridable. Flip only on owner sign-off over the @GOV "
                "shadow window."
            ),
            type="bool",
            default=CONTEXT_EMISSION_GATE_OVERRIDE_LIVE,
            category="Signal gating",
        ),
        # ── Entry quality (src/entry_quality.py) ─────────────────────────────
        # Registered from the rule registry rather than typed out one by one:
        # the rules, their thresholds and their boot defaults all live in the
        # module that decides them, and a hand-written copy here would be the
        # third spelling of the same knob. Appended below the static list.
        Tunable(
            key="entry_quality_enabled",
            label="Entry quality — measure",
            description=(
                "ON = evaluate the entry-quality rules against each "
                "candidate's stamped entry features and record what each rule "
                "WOULD have rejected. Changes nothing on its own — the "
                "measurement half, and the population every promotion decision "
                "reads. OFF = the gate is inert and the ops panel goes empty."
            ),
            type="bool",
            default=ENTRY_QUALITY_ENABLED,
            category="Signal gating",
        ),
        Tunable(
            key="entry_quality_live",
            label="Entry quality — apply live (master)",
            description=(
                "Master money-path switch for the entry-quality gate. A rule "
                "suppresses only when this AND its own 'apply live' flag are "
                "ON, so this is the single lever that stops the whole gate "
                "without touching per-rule state. Suppressions are stamped "
                "into the suppression audit, so the gate keeps earning or "
                "losing its place on forward-measured candles."
            ),
            type="bool",
            default=ENTRY_QUALITY_LIVE,
            category="Signal gating",
        ),
        Tunable(
            key="entry_quality_max_reject_frac",
            label="Entry quality — blast-radius cap (frac)",
            description=(
                "Over the last N enforcement-eligible decisions, once this "
                "fraction has been rejected the gate degrades to shadow until "
                "the window recovers — it keeps stamping and stops "
                "suppressing. Neither rule's rejection volume has ever been "
                "measured, and a feed running at single digits per day cannot "
                "afford to discover it live. 1.0 disables the cap."
            ),
            type="float",
            default=ENTRY_QUALITY_MAX_REJECT_FRAC,
            category="Signal gating",
            min_value=0.05,
            max_value=1.0,
        ),
        Tunable(
            key="entry_quality_budget_window",
            label="Entry quality — cap window (decisions)",
            description=(
                "How many enforcement-eligible decisions the blast-radius cap "
                "measures over. Decisions, not seconds: a quiet hour must not "
                "refill a budget that nothing spent."
            ),
            type="int",
            default=ENTRY_QUALITY_BUDGET_WINDOW,
            category="Signal gating",
            min_value=10,
            max_value=5000,
        ),
        Tunable(
            key="dispatch_staleness_v2_enabled",
            label="Staleness V2 — measure",
            description=(
                "ON = evaluate the geometry-aware staleness gate "
                "(src/staleness_v2.py) beside the flat V1 gate on every "
                "dispatch attempt and stamp V1-block/V2-pass disagreements as "
                "X@DSV2 shadow arms. V1 keeps deciding. OFF = no V2 "
                "evaluation."
            ),
            type="bool",
            default=DISPATCH_STALENESS_V2_ENABLED,
            category="Signal gating",
        ),
        Tunable(
            key="dispatch_staleness_v2_live",
            label="Staleness V2 — apply live",
            description=(
                "ON = V2 replaces V1 as the deciding staleness gate: drift is "
                "bounded per direction as a fraction of the candidate's own "
                "SL/TP distances instead of a flat 0.5%. Flip only on owner "
                "sign-off over the @DSV2 shadow window."
            ),
            type="bool",
            default=DISPATCH_STALENESS_V2_LIVE,
            category="Signal gating",
        ),
        Tunable(
            key="dispatch_staleness_v2_toward_sl_max_frac",
            label="Staleness V2 — max drift toward SL (frac)",
            description=(
                "Adverse-drift budget: fraction of the entry→SL distance price "
                "may consume before the signal is stale (1.0 = price at the "
                "stop). Applies when V2 is live."
            ),
            type="float",
            default=DISPATCH_STALENESS_V2_TOWARD_SL_MAX_FRAC,
            category="Signal gating",
            min_value=0.05,
            max_value=1.0,
        ),
        Tunable(
            key="dispatch_staleness_v2_toward_tp_max_frac",
            label="Staleness V2 — max drift toward TP (frac)",
            description=(
                "Chase budget: fraction of the entry→TP1 distance price may "
                "already have travelled before dispatch counts as chasing. "
                "Applies when V2 is live."
            ),
            type="float",
            default=DISPATCH_STALENESS_V2_TOWARD_TP_MAX_FRAC,
            category="Signal gating",
            min_value=0.05,
            max_value=1.0,
        ),
        # ── Layer G — autonomous emission controller (S72) ──────────────────
        # The outer loop: consumes the suppression-audit gate verdicts + edge
        # matrix and moves the per-strategy emission overrides itself, dark-first
        # + self-promoting (docs/PLAN_AUTONOMOUS_EMISSION_CONTROLLER.md). Master
        # switch + envelope; there is deliberately no "confirm/go-live" flag —
        # promotion is data-gated, not human-gated.
        Tunable(
            key="emission_controller_enabled",
            label="Emission controller — master / kill",
            description=(
                "ON = the autonomous controller reads its measured gate verdicts "
                "and adjusts per-strategy emission overrides inside its envelope. "
                "OFF = kill: the emission policy reads global params only and all "
                "controller overrides are ignored (instant revert to static)."
            ),
            type="bool",
            default=True,
            category="Signal gating",
        ),
        Tunable(
            key="emission_controller_boot_grace_cycles",
            label="Emission controller — boot-grace cycles",
            description=(
                "Pure-observation cycles after each (re)start before ANY override "
                "can be promoted live. The system-level dark period; needs no "
                "human. Stamps would-be adjustments meanwhile."
            ),
            type="int",
            default=3,
            category="Signal gating",
        ),
        Tunable(
            key="emission_controller_stability_cycles",
            label="Emission controller — stability window (K)",
            description=(
                "A per-strategy override only promotes after its triggering "
                "verdict is consistent across this many consecutive cycles "
                "(hysteresis — never a single-window reflex). A reversal needs K "
                "fresh opposite cycles."
            ),
            type="int",
            default=3,
            category="Signal gating",
        ),
        Tunable(
            key="emission_controller_promote_ev_r",
            label="Emission controller — promote EV bar (R)",
            description=(
                "Minimum |EV/suppression| in R before the controller turns a "
                "strategy's NEGATIVE suppression OFF (the risky, more-emissions "
                "direction). Re-protecting (suppression back ON) is not gated by "
                "this bar."
            ),
            type="float",
            default=0.25,
            category="Signal gating",
        ),
        Tunable(
            key="emission_controller_min_gate_n",
            label="Emission controller — min gate sample",
            description=(
                "A context_floor:<strategy> gate verdict counts toward stability "
                "only when its suppression sample is at least this many — thin "
                "verdicts never advance a promotion."
            ),
            type="int",
            default=40,
            category="Signal gating",
        ),
        Tunable(
            key="emission_controller_max_changes_per_cycle",
            label="Emission controller — blast radius / cycle",
            description=(
                "Cap on distinct per-strategy overrides the controller may "
                "promote in a single cycle (measured-harm fixes prioritised by "
                "|EV|). Bounds how fast live behaviour can move."
            ),
            type="int",
            default=2,
            category="Signal gating",
        ),
        Tunable(
            key="emission_controller_routable_enabled",
            label="Emission controller — routability measurement",
            description=(
                "ON = classify every candidate by whether the emission policy can "
                "actually read its strategy key, report the standing dead-override "
                "footprint, and compute the counterfactual (which live candidates "
                "would have promoted instead of unroutable ones). Measurement only "
                "— changes no behaviour. Read it on the ops Layer-G panel."
            ),
            type="bool",
            default=True,
            category="Signal gating",
        ),
        Tunable(
            key="emission_controller_routable_live",
            label="Emission controller — enforce routability (owner sign-off)",
            description=(
                "ON = act on the measurement: exclude unroutable keys (measurement "
                "arms, shadow-only units) from the action space and prune the dead "
                "overrides already persisted. Side effect: real strategies stop "
                "competing with phantoms for the per-cycle budget, so their "
                "overrides promote sooner — an emission-timing change. Default OFF "
                "until the measured result is signed off."
            ),
            type="bool",
            default=False,
            category="Signal gating",
        ),
        Tunable(
            key="emission_controller_min_samples_floor",
            label="Emission controller — relax-floor lower bound",
            description=(
                "Lower clamp for the per-strategy relax sample floor the "
                "controller may set (it steps down from the global default to "
                "unlock thin-but-STRONG cells, never below this). The strongest "
                "cell today (QUIET_COMPRESSION_BREAK, +2.21R) sits at n=29."
            ),
            type="int",
            default=15,
            category="Signal gating",
        ),
        Tunable(
            key="dispatch_cooldown_enabled",
            label="Dispatch cooldown",
            description=(
                "Per-(symbol, setup, direction) re-emission guard: blocks the "
                "same setup from re-firing within the cooldown window after a "
                "dispatch (stops 15s bit-identical spam). Gate audit read it "
                "DROP (235R missed, 100% would-win — the window blocked "
                "profitable re-entries). OFF = no cooldown (every re-detection "
                "can emit); tune the window below instead of disabling outright."
            ),
            type="bool",
            default=DISPATCH_COOLDOWN_ENABLED,
            category="Signal gating",
        ),
        Tunable(
            key="dispatch_cooldown_sec",
            label="Dispatch cooldown window (s)",
            description=(
                "Seconds the same (symbol, setup, direction) is blocked from "
                "re-emitting after a dispatch. Lowered from 1800 to 900 off the "
                "gate audit; raise toward 1800 for fewer repeat alerts, lower "
                "toward ~300 to let continuing moves re-enter sooner."
            ),
            type="float",
            default=DISPATCH_COOLDOWN_SEC,
            category="Signal gating",
            min_value=0.0,
            max_value=7200.0,
            unit="s",
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
            key="btc_dir_penalty_apply",
            label="BTC-direction penalty (apply)",
            description=(
                "Apply the OWNER_BRIEF §2.1 soft penalty when BTC's 1H AND "
                "4H trend both oppose the signal. The gate was silently "
                "broken in production (numpy truthiness, fixed 2026-07-14), "
                "so re-arming it changes live scoring — it ships dark. "
                "While OFF, every would-fire is shadow-logged "
                "(btc_dir_shadow counter + BTC_DIR_SHADOW log line); flip "
                "ON after reviewing a real would-fire window."
            ),
            type="bool",
            default=BTC_DIR_PENALTY_APPLY,
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
            key="dark_emission_enabled",
            label="Dark emission lane (owner-only feed from the silent paths)",
            description=(
                "Carry an enrolled path PAST the setup-compat and execution "
                "gates so it actually emits, then divert the signal at the "
                "single enqueue site into an owner-only ledger. Every other "
                "gate still applies, so a dark row is a signal the scanner "
                "was willing to send — not a counterfactual. It is NOT what a "
                "user would have received: the router's second layer "
                "(correlation lock, cooldowns, concurrency caps) is not "
                "applied, so the count over-reports a feed size. "
                "MOVER_TREND_PULLBACK is excluded — it already owns 64% of "
                "the delivered book. Nothing here reaches a channel, a push, "
                "the app feed or an order: a dark candidate never enters "
                "signal_queue, and the queue is the only route to any of them."
            ),
            type="bool",
            default=DARK_EMISSION_ENABLED,
            category="Measurement",
        ),
        Tunable(
            key="mover_retention_enforce",
            label="Dynamic mover retention (act on the verdict)",
            description=(
                "A promoted mover is held for a flat 6h and dropped whatever "
                "it did. With this ON the promotion loop instead releases a "
                "pair once it has been scanned enough times to have shown us "
                "something and produced no candidate, or once its trade rate "
                "has sat at its own baseline long enough that the move is "
                "over — and EXTENDS a pair past 6h while it is still "
                "producing, up to a hard ceiling. Scored on opportunity and "
                "liveness only, never on outcomes: a dark row resolves hours "
                "later, and dropping a pair for bad outcomes stops it "
                "producing candidates, so it could never earn its way back. "
                "OFF still measures — the scorer stamps the verdict it would "
                "have reached on every held pair, so a window of would-be "
                "releases is readable before anything is acted on. Money "
                "path: this changes which pairs are scanned, so it changes "
                "which signals emit."
            ),
            type="bool",
            default=MOVER_RETENTION_ENFORCE,
            category="Signal gating",
        ),
        Tunable(
            key="dark_promotion_enabled",
            label="Dark → live promotion (master switch)",
            description=(
                "Engine-wide arming for the per-path promotion rules set on "
                "ops Control → Promotions. OFF means every dark row is "
                "diverted exactly as before, whatever any rule says — this is "
                "the kill switch for the mechanism, not a rule of its own. ON "
                "means a diverted candidate matching an ENABLED rule's gate, "
                "regime, session and direction conditions is enqueued for "
                "real, and then still faces the router's full second layer "
                "(correlation lock, cooldowns, concurrency caps, "
                "same-direction throttle) before reaching anyone. A promoted "
                "row is STILL written to the dark ledger and still walked, "
                "with its delivery outcome stamped, so the measurement that "
                "justified the promotion keeps arriving after it. Each rule "
                "carries its own per-day blast-radius cap. This is a money-"
                "path switch: it changes what paid subscribers receive."
            ),
            type="bool",
            default=DARK_PROMOTION_ENABLED,
            category="Signal gating",
        ),
        Tunable(
            key="entry_features_enabled",
            label="MVRTP entry-feature stamps (observe-only)",
            description=(
                "Record what CVD, order-book depth, funding, the level book, "
                "pullback volume and pullback depth said at the moment each "
                "MOVER_TREND_PULLBACK signal was created. MVRTP decides on "
                "price against three SMAs and one ATR; every one of those "
                "inputs was already in smc_data and unread. Nothing is "
                "applied — the signal emitted is identical with this on or "
                "off — and outcomes are joined from the closed-signal record "
                "rather than resolved by a second forward-measurement lane. "
                "ON by default: a measurement shipped OFF produces an empty "
                "panel and a decision that keeps being deferred."
            ),
            type="bool",
            default=True,
            category="Measurement",
        ),
        Tunable(
            key="prescoring_audit_enabled",
            label="Pre-scoring gate audit (setup_compat / execution)",
            description=(
                "Also record the candidates killed BEFORE scoring by the "
                "setup-compatibility and execution-quality gates, and "
                "forward-measure them like every other suppression. These "
                "two were the last live gates with no row in the audit — "
                "they fired ahead of the stamping point, so 37,782 "
                "suppressions in one window carried no WOULD_WIN%, no EV "
                "and no KEEP/TUNE/DROP, while every other gate was ranked "
                "beside them. This is where every regime-confined "
                "evaluator dies (MEAN_REVERT 98% of its rejects, "
                "RANGE_FADE 89%) and where MOVER_TREND_PULLBACK takes "
                "zero. Observe-only: the gates still suppress exactly as "
                "before, the rows are excluded from the edge matrix so "
                "Layer C cannot route on them, and nothing reaches a user."
            ),
            type="bool",
            default=PRESCORING_AUDIT_ENABLED,
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
            key="feature_liveness_enabled",
            label="Feature-liveness watchdog",
            description=(
                "Compare every measurement pipeline's output rate against "
                "its upstream driver each audit cycle and publish "
                "data/feature_liveness.json; sustained flat-lines and "
                "growing fail-open exception counters page via the "
                "monitor's INVARIANT_WARN path. The systemic answer to the "
                "2026-07-14 silently-dead-features incident. Observe-only."
            ),
            type="bool",
            default=FEATURE_LIVENESS_ENABLED,
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
            key="sar_exit_shadow_enabled",
            label="SAR exit shadow arm",
            description=(
                "Stamp a SETUP@SARBASE / SETUP@SAREXIT counterfactual pair "
                "for every post-scoring candidate — the live evaluator "
                "geometry vs the same entry exited by a trailing 15m "
                "Parabolic SAR — and forward-measure both over the SAME "
                "48h window, so the edge matrix shows whether the "
                "bake-off's PF 1.60 survives on real live signals. Both "
                "arms share the live sl_distance as their R denominator. "
                "DEFAULT-OFF (dark-first): observe-only even when on — no "
                "live exit, FSM transition or dispatch reads it, and "
                "activating a SAR exit is a separate owner-signed change."
            ),
            type="bool",
            default=SAR_EXIT_SHADOW_ENABLED,
            category="Measurement",
        ),
        Tunable(
            key="stale_tf_refuse_enabled",
            label="Refuse to score on a known-stale timeframe",
            description=(
                "When a symbol's 15m series has stopped updating, withhold "
                "its indicators from the evaluators and let the BTC regime "
                "kill switch decline to rule, instead of sizing geometry "
                "from a frozen bar. Every consumer already owns a written "
                "fallback for absent 15m (MOVER falls to 5m ATR, QCB to the "
                "legacy 5m compression check, pre-TP to its static "
                "threshold), so refusing routes into tested paths. "
                "DEFAULT-OFF (dark-first): the measurement beside it runs "
                "from day one — see the stale_tf_scoring liveness probe — "
                "and this flips only on owner sign-off once a real window "
                "shows what it would have withheld. Unknown age is never "
                "treated as stale: a missing stamp must not degrade "
                "geometry after a snapshot restore."
            ),
            type="bool",
            default=STALE_TF_REFUSE_ENABLED,
            category="Measurement",
        ),
        Tunable(
            key="tuned_variants_enabled",
            label="Tuned-variant shadow arms",
            description=(
                "Stamp a SETUP@TUNED counterfactual arm for every "
                "MOVER_AVWAP_SCALP / VOLUME_SURGE_BREAKOUT candidate — the "
                "owner-directed tune-don't-disable recipe (TP1 at the "
                "measured median MFE behind an ATR/structure stop; VSB also "
                "skips entries stretched >1 ATR from the 20-bar mean) — and "
                "forward-measure it against the live arm in the edge "
                "matrix. Observe-only: live output untouched; applying a "
                "winning recipe is a separate dark-first, owner-signed "
                "change."
            ),
            type="bool",
            default=TUNED_VARIANTS_ENABLED,
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
        Tunable(
            key="manual_trade_builder_enabled",
            label="Manual trade builder",
            description=(
                "Master switch for the server-side manual trade builder "
                "(POST /api/manual-trade/take): lets an Assist-or-higher user "
                "place a trade they built on the chart — MARKET or a resting "
                "LIMIT at a slid entry, with optional SL/TP — on their "
                "server-connected key. Ships DARK; flip ON here to activate "
                "after shadow + sign-off. OFF → the endpoint returns 503 and "
                "the app renders it as unavailable (no client-side fallback)."
            ),
            type="bool",
            default=MANUAL_TRADE_BUILDER_ENABLED,
            category="Execution",
        ),
        Tunable(
            key="track_record_public_enabled",
            label="Public track record (Lumin Pulse)",
            description=(
                "Serve the recorded delivered-signal book on "
                "GET /api/track-record, which the Lumin app's Pulse tab "
                "renders so a new subscriber can read the product's actual "
                "history before their own paper book has a row in it. Every "
                "number is RECORDED — trade_monitor wrote it at the terminal "
                "transition — never replayed or reconstructed, and it is the "
                "pooled signal book, not any user's account. This is not a "
                "money-path switch: it changes no score, no dispatch and no "
                "exit. It is here rather than in .env so a subscriber-facing "
                "performance claim can be pulled without a redeploy. OFF → "
                "the endpoint returns an empty book with "
                "unavailable_reason='disabled' and the app hides the card."
            ),
            type="bool",
            default=TRACK_RECORD_PUBLIC_ENABLED,
            category="Measurement",
        ),
    ]

    # ── Per-rule entry-quality knobs, generated from the rule registry ───────
    # Not typed out above on purpose. The rules, their comparison direction and
    # their boot defaults are decided in ``src/entry_quality.py``; a
    # hand-maintained copy here would be a second spelling of the same knob and
    # would drift the first time a rule is added — the ``MEASUREMENT_SUFFIXES``
    # lesson, which cost a week of an inflated ops rollup. One writer, one
    # reader: adding a Rule there surfaces its controls in ops with no edit here.
    try:
        from src.entry_quality import CMP_FLAG, RULES as _EQ_RULES

        for _rule in _EQ_RULES:
            _scope = _rule.setup_class or "every path"
            items.append(
                Tunable(
                    key=_rule.live_key,
                    label=f"Entry quality · {_rule.label} — apply live",
                    description=(
                        f"{_rule.rationale} Applies to {_scope}. Suppresses "
                        "only while the entry-quality master switch is also ON; "
                        "OFF leaves the rule stamping what it would have "
                        "rejected."
                    ),
                    type="bool",
                    default=bool(
                        ENTRY_QUALITY_RULE_LIVE.get(_rule.key, _rule.live_default)
                    ),
                    category="Signal gating",
                )
            )
            if _rule.compare == CMP_FLAG:
                # A boolean shadow has nothing to compare against; registering a
                # threshold for it would put a knob in ops that changes nothing.
                continue
            items.append(
                Tunable(
                    key=_rule.threshold_key,
                    label=f"Entry quality · {_rule.label} — threshold",
                    description=(
                        f"Rejects when {_rule.feature} is "
                        f"{'above' if _rule.compare == 'max' else 'below'} this "
                        f"value. Applies to {_scope}."
                    ),
                    type="float",
                    default=float(
                        ENTRY_QUALITY_RULE_THRESHOLD.get(
                            _rule.key, _rule.threshold_default
                        )
                    ),
                    category="Signal gating",
                )
            )
    except Exception as exc:  # noqa: BLE001
        # A registry that cannot describe a rule must not take the whole tunable
        # panel down with it — every other knob still renders, and the failure
        # is loud rather than a silently missing control.
        log.error("runtime_tunables: entry-quality rule registration failed: {}", exc)

    return {t.key: t for t in items}


class RuntimeTunables:
    """Cached Firestore-backed tunable store.  Thread-safe.

    Read-path contract (2026-07-13 incident): callers run on the engine's
    single asyncio event loop, so a read here must NEVER wait on the network.
    On TTL expiry the caller gets the *stale* cache back immediately and a
    single-flight daemon thread refreshes Firestore in the background — the
    Firestore client's internal retry deadline (minutes, on a network stall)
    can therefore never wedge the scan/monitor loops.  Only the very first
    cold read (boot path, before any loop starts) fetches inline.
    """

    def __init__(self, firestore_client: Any, clock: Callable[[], float] = time.monotonic) -> None:
        self._db = firestore_client
        self._clock = clock
        self._lock = threading.Lock()
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_read_at: float = 0.0
        self._refresh_in_flight: bool = False
        self._stale_warned_at: float = 0.0

    # ---- read path (hot, cached, never blocks on the network) ------------

    def _doc_values(self) -> Dict[str, Any]:
        with self._lock:
            now = self._clock()
            if self._cache is not None:
                age = now - self._cache_read_at
                if age < _CACHE_TTL_S:
                    return self._cache
                if not self._refresh_in_flight:
                    self._refresh_in_flight = True
                    self._spawn_refresh()
                if age >= _STALE_WARN_S and now - self._stale_warned_at >= _STALE_WARN_S:
                    self._stale_warned_at = now
                    log.warning(
                        "runtime_tunables cache is {:.0f}s stale — Firestore "
                        "slow/unreachable; serving last-known values",
                        age,
                    )
                return self._cache
            # Cold cache: first read ever (boot, before the loops start).
            self._refresh_in_flight = True
        return self._refresh()

    def _spawn_refresh(self) -> None:
        """Kick the background refresh (separate method so tests can run it
        synchronously)."""
        threading.Thread(
            target=self._refresh, daemon=True, name="runtime-tunables-refresh"
        ).start()

    def _refresh(self) -> Dict[str, Any]:
        """Blocking Firestore read + cache update.  Never raises.

        A failed refresh keeps the last-known values (an ops flag the owner
        set must survive a Firestore blip) — except on a failed COLD read,
        where an empty cache is stored so callers fall to env defaults
        without ever inline-fetching again.
        """
        values: Optional[Dict[str, Any]] = None
        try:
            doc = (
                self._db.collection(_DOC_PATH[0]).document(_DOC_PATH[1]).get()
            )
            values = dict(doc.to_dict() or {}) if getattr(doc, "exists", False) else {}
        except Exception:
            log.exception(
                "runtime_tunables doc read failed — serving last-known/env values"
            )
        with self._lock:
            self._refresh_in_flight = False
            if values is not None:
                self._cache = values
                self._cache_read_at = self._clock()
            elif self._cache is None:
                self._cache = {}
                self._cache_read_at = 0.0  # ancient → next read retries in background
            return self._cache

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
            if tun.choices and str(value) not in tun.choices:
                raise ValueError(
                    f"{key}: {value!r} is not one of {', '.join(tun.choices)}"
                )
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
        # Merge into the live cache instead of dropping it — dropping would
        # force the next reader into a cold INLINE fetch, which blocks the
        # event loop in single-process mode (2026-07-13 incident class).
        with self._lock:
            self._cache = {**(self._cache or {}), **coerced}
            self._cache_read_at = self._clock()
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
        if tun.type == "str":
            # Free text. The empty string is a legitimate value ("no paths
            # selected"), so this returns "" rather than None — None is the
            # channel `set_values` reads as a parse failure, and an allow-list
            # you cannot clear from ops is an allow-list that only grows.
            return str(raw).strip()
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
                "choices": list(tun.choices) if tun.choices else None,
            }
        )
    return out


def reset_for_test() -> None:
    global _client, _registry
    with _lock:
        _client = None
        _registry = None
