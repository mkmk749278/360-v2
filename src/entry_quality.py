"""Entry quality — the consuming half of the entry-feature lane (2026-08-02).

Owner: *"make entry features live, not only measurement"* — against #849, which
stamped what every path could have looked at, and #851, which generalised those
stamps past MVRTP and signed the directional ones toward the trade.

Both of those PRs end at the same sentence: **applied, nothing.** The features
were recorded and the emitted signal was byte-identical with the lane on or off.
This module is the part that was missing: a real gate, in the scanner's
post-scoring chain, that can suppress a candidate on what its entry-time
readings said — wired end-to-end, stamped into the suppression audit like every
other live gate, bounded by a blast-radius cap, and switchable per rule from the
ops control plane without a deploy.

Which rules earn enforcement, and which do not
----------------------------------------------
This is the whole design question, and the repo already paid for getting it
wrong at a smaller n.  ``FAILED_AUCTION_RECLAIM`` read +0.846R on three rows
(CI [−1.00, +2.00]) and a promotion request followed the same day.  The
entry-feature window is bigger and no better: #849 tested nineteen cells across
six candidate discriminators on 46 closed MVRTP signals, exactly one 95% CI
excluded zero — *in the backwards direction* — against a ~62% familywise
probability of at least one doing so by luck.  **That window cannot choose a
threshold**, and nothing since has changed it.

So the rules here are not the discriminators the splits ranked.  A rule ships in
``enforce`` only when it is a **repair of a filter the engine already believes
in and fails to apply** — where the threshold comes from code that already
exists, not from a p-value read off this window:

``profile_reject``
    ``_pass_basic_filters`` takes a ``profile`` argument that adjusts the
    liquidity and spread thresholds per pair tier — Tier 1 needs 1.5× the volume,
    a historically wide-spread pair gets 0.85× the spread allowance.  **One of
    twenty call sites passes it**, and the path that is ~94% of the delivered
    book is not that one.  #849 stamped the shadow of the omitted argument as
    ``profile_would_reject``.  Enforcing it invents no number: it is the engine
    applying the tier adjustment it already computes and then discards.  Ships
    live.

    **First live window, 2026-08-02: 900 candidates judged, 900 passed, 0
    rejected, 0 unknown.**  So the argument was right and empty — the rule reads
    its input on every single candidate (not blind, ``pair_profile`` is always
    present) and changes no outcome, because the profile-free
    ``_pass_basic_filters`` call upstream already rejects everything the
    tier-adjusted one would.  It is kept live: it is proven safe rather than
    merely argued safe, it costs nothing, and it starts filtering by itself the
    day a tier multiplier does bite.  But **this gate currently filters nothing
    on the money path**, and no panel should be read as though it does.

One rule, deliberately.  A gate carrying twelve of them is twelve thresholds
against a book this size, which guarantees a spurious winner (``CLAUDE.md``:
count how many cells you looked at before calling one special).  The ops
now-vs-later page remains where arbitrary thresholds are *explored*; a rule
arrives here only when it is a candidate for enforcement.

The rule that was retired, and why it matters more than the one that stayed
---------------------------------------------------------------------------
``tpe_smc_zone`` shipped here on 2026-08-02 and was removed the same day.  It
existed because ``_evaluate_trend_pullback``'s SMC check reads *"require at
least one FVG or orderblock in the pullback zone"* while the code is
``bool(fvgs) or bool(orderblocks)`` — a global existence test which, in this
module's own words, *"a zone forty ATR away satisfies"*.

**No such candidate exists.**  Once ``smc_zone_dist_atr`` was actually
computable (it had been returning ``None`` on every row until the same day's fix
to ``zone_distance_atr``), the first 89 TPE signals measured:

===========  ==========
percentile   distance
===========  ==========
p0           0.00 ATR
p50          0.13 ATR
p90          0.42 ATR
p100         **0.52 ATR**
===========  ==========

88 of 89 inside half an ATR, and no tail at all.  The mechanism is
``detect_fvg``'s own ``lookback=10``: it only finds gaps in the last ~12 bars,
and a gap that recent is necessarily still near price.  **The narrow lookback is
what makes the loose gate behave like the strict one its comment describes.**
So the gate rejects symbols with no recent gap — real work — and when it passes,
the structure genuinely is at the entry.

No threshold can discriminate on that distribution: anything above 0.52 keeps
every row, anything below cuts arbitrarily into a tight cluster.  A rule that
cannot discriminate is not a shadow rule waiting for evidence, it is noise on a
panel, so it is gone rather than left to look promotable.

The lesson is not about SMC.  A gate whose comment and code disagree is worth
*checking*; it is not thereby a gate that does nothing.  Reading the code
produced a confident story about 40-ATR zones, and one query against the
measurement — which had to be repaired before it could answer — showed the
harm never happened.  ``smc_zone_dist_atr`` is still stamped, because the
measurement is the thing that settled this and is what would show the gate
drifting later.

Where the gate runs, and why it runs last
------------------------------------------
In the scanner, after the confidence floor has passed — so an ``entry_quality``
rejection is always a candidate that **would otherwise have emitted**.  Two
consequences, both wanted:

* the counter means "signals this gate cost us", not "signals that were dying
  anyway";
* the shadow ``would_reject`` population is measured on the emitting book, which
  is the only population an adoption decision is allowed to read
  (``CLAUDE.md``: *"emitted" means DELIVERED*).

An enforcing gate starves its own evidence
-------------------------------------------
``cohort_edge`` suppressed on measured expectancy whose only writer was a
*delivered* signal resolving — suppressed → never emits → never resolves →
verdict permanent.  This gate has the same shape and the same answer: every live
rejection is stamped through ``_stamp_suppressed``, so the suppression audit
forward-measures on real candles what the gate cost, and the verdict keeps
arriving after enforcement starts.  A rule that begins losing money is visible
in the same table that ranks every other gate.

The budget is a blast-radius cap, not a filter
-----------------------------------------------
No rule's rejection *volume* had been measured when this shipped — the ledger
lives on the VPS and the first live window was the first look anyone got.  A
rule that turned out to reject 60% of the book would have starved a feed already
running at single digits per day, and "the owner notices the feed went quiet" is
not a detection mechanism (the deny-list lesson, one subsystem over).

That first window has now been read: ``profile_reject`` rejected **0 of 900**
and the cap was never approached.  The cap stays, because it is a bound on the
*next* rule as much as this one, and because a rule that bites zero times today
can bite on a different pair mix tomorrow.

So enforcement carries a rolling cap: over the last ``window`` candidates the
gate **could** have suppressed, if the rejected fraction exceeds
``max_reject_frac`` it **degrades to shadow** — it keeps stamping
``would_reject_by`` and stops suppressing — until the window recovers.  This is
order-dependent by construction, and that is the honest cost of a bound that
cannot be computed in advance.  It is therefore **counted and named**
(``suspended_total`` beside ``enforced_total`` and ``considered_total``) rather
than silent: a gate sitting over budget reads as a distinct state on the ops
panel, never as a quiet market.

"Could have suppressed" is the denominator and it is not the same as "wanted
to".  Counting only the rejections leaves an all-rejection window, a fraction
that reads 1.0, and a gate that suspends itself permanently after
``max_reject_frac × window`` rejections with nothing able to push them out —
so a pass under a live rule is recorded too, and it is what lets a spent budget
recover.  A shadow-only window is not recorded at all: the cap exists to protect
live output, and spending it on decisions that were never going to suppress
would suspend a gate that had done nothing.

Unknown is not a rejection
---------------------------
A feature that did not compute makes its rule **abstain**, counted per rule.
The direction of the fail is deliberate and it is the opposite of
``crypto_perp_admission``'s: there, the input is the whole exchange and absence
of knowledge is not permission.  Here the input is a measurement lane, and a
fail-closed rule would silently kill the entire feed the moment an upstream
(the order book, the level book, ``pair_profile``) went dark — the failure mode
would be indistinguishable from a quiet market, which is the thing this repo
keeps paying for.

But an abstaining rule is *inert*, and an inert rule reads exactly like a rule
that is passing everything.  So ``unknown_frac`` is on the snapshot and the
liveness probe fails when an **enforcing** rule cannot see its own feature on
most of its population — an enforcing gate that never fires because its input
died is a fault, not a healthy gate.

Pure functions only.  The scanner owns wiring, suppression stamping, counters
and the ledger annotation; nothing here does I/O.
"""
from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional, Tuple

#: Rule verdicts.
VERDICT_PASS = "pass"
VERDICT_REJECT = "reject"
VERDICT_UNKNOWN = "unknown"

#: How a rule reads its feature.
#: ``max`` — reject when the value is ABOVE the threshold.
#: ``min`` — reject when the value is BELOW the threshold.
#: ``flag`` — the feature is a boolean shadow; reject when it is true.
CMP_MAX = "max"
CMP_MIN = "min"
CMP_FLAG = "flag"


@dataclass(frozen=True)
class Rule:
    """One entry-quality rule.

    ``setup_class`` empty means "every path that stamps this feature".  A rule
    naming a path applies to that path only — the paths do not share a trigger,
    a timeframe or a stop geometry, so a threshold that is right on one can be
    meaningless on another (``entry_features.select``'s own reasoning).
    """

    key: str
    feature: str
    compare: str
    setup_class: str
    label: str
    #: Why this rule exists *in code terms*. A rule whose rationale is a
    #: measured delta on this window does not belong here yet — see the module
    #: docstring.
    rationale: str
    #: Boot default for the per-rule enforcement flag. The shadow evaluation is
    #: governed by the module-level ``enabled`` flag and always runs.
    live_default: bool
    #: Boot default threshold. Ignored for ``flag`` rules.
    threshold_default: float = 0.0
    #: Ops tunable keys, derived once so the scanner, the registry and the ops
    #: panel cannot drift into three spellings of the same knob.
    @property
    def live_key(self) -> str:
        return f"entry_quality_{self.key}_live"

    @property
    def threshold_key(self) -> str:
        return f"entry_quality_{self.key}_threshold"


#: The rule set. Short on purpose — see the module docstring.
RULES: Tuple[Rule, ...] = (
    Rule(
        key="profile_reject",
        feature="profile_would_reject",
        compare=CMP_FLAG,
        setup_class="",
        label="Pair-tier liquidity / spread filter",
        rationale=(
            "_pass_basic_filters computes tier-adjusted volume and spread "
            "thresholds from the pair profile and 19 of 20 call sites discard "
            "them, including the path that is ~94% of the delivered book. "
            "Enforcing invents no threshold — it applies the one the engine "
            "already computes."
        ),
        live_default=True,
    ),
    Rule(
        key="session_quality",
        feature="session_quality",
        compare=CMP_MIN,
        setup_class="",
        label="Low-liquidity clock window",
        rationale=(
            "market_context.classify_session already scores every entry's "
            "clock (OVERLAP 1.0, NY 0.85, LONDON 0.80, ASIA 0.45, OFF_HOURS "
            "0.30, x0.6 on a weekend) and stores it on the signal as "
            "mc_session_quality. No emission decision has ever read it. The "
            "threshold is a boundary on that existing scale, not a number "
            "fitted here: 0.8 is exactly 'weekday London/Overlap/NY'. SHADOW "
            "— see the docstring; this is a discovery, not a repair, and it "
            "would move roughly half the delivered book."
        ),
        live_default=False,
        threshold_default=0.8,
    ),
    Rule(
        key="mover_stack_15m",
        feature="sep_15m_pct",
        compare=CMP_MIN,
        setup_class="MOVER_TREND_PULLBACK",
        label="Mover run has died on the traded timeframe",
        rationale=(
            "The mover gate clears on max(15m MA7<->MA99, 1H EMA21/50 fan), so "
            "a candidate can qualify entirely on the 1H fan while the 15m "
            "stack — the timeframe this path actually enters and exits on — is "
            "flat. The threshold is MOVER_TP_MIN_STACK_SEP_PCT, the path's own "
            "floor, applied to the 15m term alone; it invents no number. "
            "SHADOW: unlike profile_reject this rejects real volume, and the "
            "widened gate was a deliberate fix for movers whose 15m stack "
            "compresses on a pullback (BTW/ESPORTS) — so it has to prove it is "
            "not simply undoing that."
        ),
        live_default=False,
    ),
    Rule(
        key="cvd_aligned",
        feature="cvd_slope_aligned",
        compare=CMP_MIN,
        setup_class="",
        label="Order flow ran against the trade at entry",
        rationale=(
            "cvd_slope is computed into smc_data on every scan and no "
            "evaluator reads it; MOVER_TREND_PULLBACK — ~59% of the enqueued "
            "book — is a three-SMA pullback trigger with no notion of volume "
            "at all. The comparison is against ZERO, which is the sign of the "
            "feature and not a level fitted to a window: `_align` has already "
            "put 'favours this trade' on the positive side for both "
            "directions, so 'CVD was with the trade' and 'CVD was against it' "
            "is the whole rule. That is the one threshold this lane can state "
            "without a number.\n\n"
            "SHADOW, and it must stay shadow until the dark lane has spoken. "
            "The delivered book measures +1.018%/row on the 90 rows it keeps "
            "against -0.118% on the 71 it drops, CI95 [+0.200, +1.823], full "
            "coverage and no abstentions — but that is 161 rows, 156 of them "
            "one path, from a page on which ~21 candidate cells were drawn, "
            "and the best of 21 beats a coin flip by construction. The "
            "campaign-unit average agrees in sign (+0.161% vs -0.343%) and is "
            "six times smaller than the per-row one, which says part of the "
            "gap is repeat entries into symbols that went on to work. "
            "Promotion waits for the dark population (schema 5 carries the "
            "features onto ~1,400 rows with outcomes), not for a better "
            "number on this one."
        ),
        live_default=False,
        threshold_default=0.0,
    ),
)

RULES_BY_KEY: Dict[str, Rule] = {r.key: r for r in RULES}


@dataclass(frozen=True)
class RuleParams:
    """Effective per-rule settings — ops tunables over config boot defaults."""

    rule: Rule
    live: bool
    threshold: float


@dataclass(frozen=True)
class EntryQualityParams:
    """Effective policy envelope.

    ``enabled`` runs the shadow evaluation on every candidate — it is the
    measurement flag and defaults ON, because a measurement shipped OFF produces
    an empty panel and a decision that keeps being deferred.  ``live`` is the
    master money-path switch; a rule enforces only when **both** it and its own
    ``live`` flag are set, so the owner has one lever that stops the whole gate
    and one per rule.
    """

    enabled: bool
    live: bool
    max_reject_frac: float
    budget_window: int
    rules: Tuple[RuleParams, ...]

    def rule(self, key: str) -> Optional[RuleParams]:
        for rp in self.rules:
            if rp.rule.key == key:
                return rp
        return None

    @staticmethod
    def from_config() -> "EntryQualityParams":
        """Read the ops tunables, falling back to the config boot defaults.

        Mirrors ``StalenessV2Params.from_config`` — one 5s-cached whole-doc read
        covers every key, so this is safe on the per-candidate path (Cost
        Discipline).
        """
        from config import (
            ENTRY_QUALITY_BUDGET_WINDOW,
            ENTRY_QUALITY_ENABLED,
            ENTRY_QUALITY_LIVE,
            ENTRY_QUALITY_MAX_REJECT_FRAC,
            ENTRY_QUALITY_RULE_LIVE,
            ENTRY_QUALITY_RULE_THRESHOLD,
        )

        def _rt(key: str, default: Any) -> Any:
            try:
                from src import runtime_tunables as _r

                val = _r.get(key)
                return val if val is not None else default
            except Exception:
                # A typo'd or unregistered key must not pin the gate to a
                # surprise: fall back to the boot default and let the caller's
                # fail_open accounting see any real fault.
                return default

        rules: List[RuleParams] = []
        for rule in RULES:
            live_default = bool(ENTRY_QUALITY_RULE_LIVE.get(rule.key, rule.live_default))
            thr_default = float(
                ENTRY_QUALITY_RULE_THRESHOLD.get(rule.key, rule.threshold_default)
            )
            rules.append(
                RuleParams(
                    rule=rule,
                    live=bool(_rt(rule.live_key, live_default)),
                    threshold=float(_rt(rule.threshold_key, thr_default)),
                )
            )
        return EntryQualityParams(
            enabled=bool(_rt("entry_quality_enabled", ENTRY_QUALITY_ENABLED)),
            live=bool(_rt("entry_quality_live", ENTRY_QUALITY_LIVE)),
            max_reject_frac=max(
                0.0, min(1.0, float(_rt("entry_quality_max_reject_frac", ENTRY_QUALITY_MAX_REJECT_FRAC)))
            ),
            budget_window=max(
                10, int(float(_rt("entry_quality_budget_window", ENTRY_QUALITY_BUDGET_WINDOW)))
            ),
            rules=tuple(rules),
        )


@dataclass(frozen=True)
class RuleOutcome:
    """One rule's reading of one candidate."""

    key: str
    verdict: str
    value: Optional[float]
    threshold: Optional[float]
    live: bool
    #: Which feature was read. Carried on the row rather than left for a reader
    #: to look up: ops renders this panel and must not hold a second copy of the
    #: rule registry to label it — the ``MEASUREMENT_SUFFIXES`` drift is the
    #: reason, and the fix for a drifting mirror is not a second mirror.
    feature: str = ""
    #: Why the rule could not read its feature. Empty when it could.
    unknown_reason: str = ""

    def as_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "rule": self.key,
            "feature": self.feature,
            "verdict": self.verdict,
            "value": self.value,
            "threshold": self.threshold,
            "live": self.live,
        }
        if self.unknown_reason:
            out["unknown_reason"] = self.unknown_reason
        return out


@dataclass(frozen=True)
class EntryQualityDecision:
    """What the policy said about one candidate.

    ``would_reject_by`` is every rule that fired, regardless of mode — that is
    the shadow population, and it is the only thing a promotion decision may
    read.  ``enforced_by`` is the rule that actually suppressed, and it is
    ``None`` whenever the master switch is off, the rule is in shadow, or the
    budget is suspended.  The two are deliberately separate fields: collapsing
    them would make "the rule fired" and "the trade was killed" the same fact,
    and the whole point of the shadow half is that they are not.
    """

    evaluated: bool
    would_reject_by: Tuple[str, ...]
    enforced_by: Optional[str]
    outcomes: Tuple[RuleOutcome, ...]
    #: Set when a rule would have enforced and the blast-radius cap held it back.
    budget_suspended: bool = False
    reason: str = ""

    @property
    def suppressed(self) -> bool:
        return self.enforced_by is not None

    def as_row(self) -> Dict[str, Any]:
        """The annotation written back onto the entry-feature ledger row."""
        return {
            "eq_would_reject_by": list(self.would_reject_by),
            "eq_enforced_by": self.enforced_by or "",
            "eq_budget_suspended": bool(self.budget_suspended),
            "eq_rules": [o.as_dict() for o in self.outcomes],
        }


def _num(value: Any) -> Optional[float]:
    """Coerce to a finite float, or None. Never raises, never invents a value."""
    try:
        if value is None or isinstance(value, bool):
            return None
        out = float(value)
        if out != out or out in (float("inf"), float("-inf")):
            return None
        return out
    except (TypeError, ValueError):
        return None


def evaluate_rule(rule_params: RuleParams, features: Dict[str, Any]) -> RuleOutcome:
    """One rule against one candidate's stamped features. Pure.

    A feature that is absent, or present as ``None``, yields ``unknown`` and the
    rule abstains.  ``None`` from the feature helpers is a deliberate refusal
    (``entry_features``: *refuse, don't clamp*) and re-reading it as a zero here
    would undo that at the only place it matters — a missing order book would
    become perfectly balanced depth *and* a suppression.
    """
    rule = rule_params.rule
    raw = features.get(rule.feature, None) if isinstance(features, dict) else None
    if raw is None:
        return RuleOutcome(
            key=rule.key,
            feature=rule.feature,
            verdict=VERDICT_UNKNOWN,
            value=None,
            threshold=None if rule.compare == CMP_FLAG else rule_params.threshold,
            live=rule_params.live,
            unknown_reason=(
                "feature_absent" if rule.feature not in (features or {}) else "feature_none"
            ),
        )

    if rule.compare == CMP_FLAG:
        fired = bool(raw)
        return RuleOutcome(
            key=rule.key,
            feature=rule.feature,
            verdict=VERDICT_REJECT if fired else VERDICT_PASS,
            value=1.0 if fired else 0.0,
            threshold=None,
            live=rule_params.live,
        )

    value = _num(raw)
    if value is None:
        return RuleOutcome(
            key=rule.key,
            feature=rule.feature,
            verdict=VERDICT_UNKNOWN,
            value=None,
            threshold=rule_params.threshold,
            live=rule_params.live,
            unknown_reason="feature_not_numeric",
        )
    if rule.compare == CMP_MAX:
        fired = value > rule_params.threshold
    else:
        fired = value < rule_params.threshold
    return RuleOutcome(
        key=rule.key,
        feature=rule.feature,
        verdict=VERDICT_REJECT if fired else VERDICT_PASS,
        value=value,
        threshold=rule_params.threshold,
        live=rule_params.live,
    )


def applicable_rules(
    params: EntryQualityParams, setup_class: str
) -> Tuple[RuleParams, ...]:
    """The rules that speak to this path, in registry order."""
    want = str(setup_class or "")
    return tuple(
        rp for rp in params.rules if not rp.rule.setup_class or rp.rule.setup_class == want
    )


def evaluate(
    features: Optional[Dict[str, Any]],
    setup_class: str,
    params: EntryQualityParams,
    *,
    budget_allows: bool = True,
) -> EntryQualityDecision:
    """The policy's reading of one candidate. Pure — no counters, no I/O.

    ``features`` is the row ``entry_features.capture`` produced for this signal.
    ``None`` means the lane did not stamp it (the measurement flag is off, or
    this path has no stamp site yet), and the gate is then inert **by
    construction rather than by accident**: it reports ``evaluated=False`` with
    a reason, so an ops panel showing a live rule and zero decisions can say
    which of the two it is.

    ``budget_allows`` is passed in rather than read, because the budget is
    stateful and this function must stay pure — the caller owns the window.
    """
    if not params.enabled:
        return EntryQualityDecision(
            evaluated=False,
            would_reject_by=(),
            enforced_by=None,
            outcomes=(),
            reason="disabled",
        )
    if not isinstance(features, dict) or not features:
        return EntryQualityDecision(
            evaluated=False,
            would_reject_by=(),
            enforced_by=None,
            outcomes=(),
            reason="no_stamp",
        )

    rules = applicable_rules(params, setup_class)
    if not rules:
        return EntryQualityDecision(
            evaluated=False,
            would_reject_by=(),
            enforced_by=None,
            outcomes=(),
            reason="no_rules_for_path",
        )

    outcomes = tuple(evaluate_rule(rp, features) for rp in rules)
    would = tuple(o.key for o in outcomes if o.verdict == VERDICT_REJECT)
    # Enforcement candidates in registry order — the first one decides, so the
    # suppression is attributed to exactly one rule and two rules firing on the
    # same candidate do not double-count in the gate table.
    enforcing = [
        o.key
        for o in outcomes
        if o.verdict == VERDICT_REJECT and o.live and params.live
    ]
    if not enforcing:
        return EntryQualityDecision(
            evaluated=True,
            would_reject_by=would,
            enforced_by=None,
            outcomes=outcomes,
            reason="shadow" if would else "pass",
        )
    if not budget_allows:
        return EntryQualityDecision(
            evaluated=True,
            would_reject_by=would,
            enforced_by=None,
            outcomes=outcomes,
            budget_suspended=True,
            reason="budget_suspended",
        )
    return EntryQualityDecision(
        evaluated=True,
        would_reject_by=would,
        enforced_by=enforcing[0],
        outcomes=outcomes,
        reason="enforced",
    )


class RejectBudget:
    """Rolling blast-radius cap on how much of the book this gate may kill.

    Keeps the last ``window`` *enforcement-eligible* decisions as booleans and
    refuses further enforcement while the rejected fraction is at or above
    ``max_frac``.  Refusing is not a clamp: the candidate proceeds exactly as it
    would with the gate in shadow, the rule's ``would_reject`` stamp is
    unchanged, and the suspension is counted — so the degraded mode is a state
    the ops panel renders, not a silence.

    Deliberately counts *decisions*, not wall-clock: a quiet hour must not
    refill a budget that nothing spent, and a burst of candidates on one symbol
    must not exhaust one that nothing was wrong with.
    """

    def __init__(self, window: int = 200, max_frac: float = 0.35) -> None:
        self._window = max(10, int(window))
        self._max_frac = max(0.0, min(1.0, float(max_frac)))
        self._recent: Deque[bool] = deque(maxlen=self._window)
        self._lock = threading.Lock()
        self.suspended_total = 0
        self.enforced_total = 0
        self.considered_total = 0

    def reconfigure(self, window: int, max_frac: float) -> None:
        """Adopt new ops-set bounds without losing the window's history.

        A widened window keeps what it already holds; a narrowed one drops the
        oldest, which is what a narrowed window means.
        """
        window = max(10, int(window))
        max_frac = max(0.0, min(1.0, float(max_frac)))
        with self._lock:
            if window != self._window:
                self._recent = deque(self._recent, maxlen=window)
                self._window = window
            self._max_frac = max_frac

    def allows(self) -> bool:
        """True while the recent rejected fraction is under the cap.

        A window that has not filled yet cannot be over budget on two
        rejections, so the fraction is measured against the window size rather
        than against however many decisions have arrived — otherwise the first
        rejection of a fresh boot reads as 100% and the gate suspends itself
        before it has done anything.
        """
        with self._lock:
            if self._max_frac >= 1.0:
                return True
            if len(self._recent) < self._window:
                denom = self._window
            else:
                denom = len(self._recent)
            return (sum(1 for v in self._recent if v) / denom) < self._max_frac

    def record(self, rejected: bool, *, suspended: bool = False) -> None:
        """Book one enforcement-eligible decision."""
        with self._lock:
            self._recent.append(bool(rejected))
            self.considered_total += 1
            if rejected:
                self.enforced_total += 1
            if suspended:
                self.suspended_total += 1

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            n = len(self._recent)
            rejected = sum(1 for v in self._recent if v)
            return {
                "window": self._window,
                "max_reject_frac": self._max_frac,
                "recent_decisions": n,
                "recent_rejected": rejected,
                "recent_reject_frac": (rejected / n) if n else None,
                "considered_total": self.considered_total,
                "enforced_total": self.enforced_total,
                "suspended_total": self.suspended_total,
            }


class PolicyCounters:
    """Per-rule tallies for ops and the liveness probe.

    ``unknown`` is the one that matters most and is the easiest to omit: a rule
    whose feature never computes passes everything and reads exactly like a rule
    that is working.  An enforcing rule in that state is a dead gate wearing a
    live gate's label, so the count is kept per rule and the probe reads it.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._rules: Dict[str, Dict[str, int]] = {}
        self.evaluated_total = 0
        self.no_stamp_total = 0
        self.enforced_total = 0
        self.shadow_reject_total = 0

    def record(self, decision: EntryQualityDecision) -> None:
        with self._lock:
            if not decision.evaluated:
                if decision.reason == "no_stamp":
                    self.no_stamp_total += 1
                return
            self.evaluated_total += 1
            if decision.enforced_by:
                self.enforced_total += 1
            elif decision.would_reject_by:
                self.shadow_reject_total += 1
            for out in decision.outcomes:
                slot = self._rules.setdefault(
                    out.key, {"seen": 0, "reject": 0, "pass": 0, "unknown": 0, "enforced": 0}
                )
                slot["seen"] += 1
                slot[out.verdict] += 1
                if decision.enforced_by == out.key:
                    slot["enforced"] += 1

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            rules: Dict[str, Any] = {}
            for key, slot in self._rules.items():
                seen = slot["seen"] or 0
                rules[key] = dict(slot)
                rules[key]["unknown_frac"] = (slot["unknown"] / seen) if seen else None
                rules[key]["reject_frac"] = (slot["reject"] / seen) if seen else None
            return {
                "evaluated_total": self.evaluated_total,
                "no_stamp_total": self.no_stamp_total,
                "enforced_total": self.enforced_total,
                "shadow_reject_total": self.shadow_reject_total,
                "rules": rules,
            }


_counters = PolicyCounters()
_budget = RejectBudget()
_state_lock = threading.Lock()


def get_counters() -> PolicyCounters:
    return _counters


def get_budget() -> RejectBudget:
    return _budget


def reset_state() -> None:
    """Fresh counters and budget — tests only."""
    global _counters, _budget
    with _state_lock:
        _counters = PolicyCounters()
        _budget = RejectBudget()


def decide(
    features: Optional[Dict[str, Any]],
    setup_class: str,
    params: Optional[EntryQualityParams] = None,
) -> EntryQualityDecision:
    """Evaluate, book the budget, count. The scanner's single entry point.

    Impure by design — this is the one place the module keeps state, so the
    pure ``evaluate`` above stays testable without touching a global.
    """
    p = params if params is not None else EntryQualityParams.from_config()
    _budget.reconfigure(p.budget_window, p.max_reject_frac)

    provisional = evaluate(features, setup_class, p, budget_allows=True)

    # The budget's denominator is every candidate this gate COULD have
    # suppressed, not every candidate it wanted to. Recording only the
    # rejections would make the window all-True, so the fraction would read 1.0
    # and the gate would suspend itself permanently after `cap × window`
    # rejections with nothing able to push them out — the denominator class this
    # repo keeps paying for, one subsystem over.
    #
    # "Could have" means: the master switch is on, and some rule that applies to
    # this path is live. A shadow-only window must not consume a bound that
    # exists to protect live output, so it is not counted at all.
    eligible = (
        provisional.evaluated
        and p.live
        and any(rp.live for rp in applicable_rules(p, setup_class))
    )
    if not eligible:
        _counters.record(provisional)
        return provisional

    if provisional.enforced_by is None:
        # A pass, and it belongs in the window: it is what lets a spent budget
        # recover.
        _budget.record(False)
        _counters.record(provisional)
        return provisional

    allowed = _budget.allows()
    decision = evaluate(features, setup_class, p, budget_allows=allowed)
    _budget.record(decision.enforced_by is not None, suspended=not allowed)
    _counters.record(decision)
    return decision


def snapshot(params: Optional[EntryQualityParams] = None) -> Dict[str, Any]:
    """Everything ops needs to render the gate, in one payload.

    The rule registry ships **with** the counters rather than being mirrored on
    the reading side.  Ops kept its own copy of ``MEASUREMENT_SUFFIXES`` once and
    it drifted for a week; the fix for a drifting mirror is not a second mirror.
    """
    p = params if params is not None else EntryQualityParams.from_config()
    counters = _counters.snapshot()
    rules: List[Dict[str, Any]] = []
    for rp in p.rules:
        stats = counters["rules"].get(rp.rule.key, {})
        rules.append(
            {
                "key": rp.rule.key,
                "label": rp.rule.label,
                "feature": rp.rule.feature,
                "compare": rp.rule.compare,
                "setup_class": rp.rule.setup_class,
                "rationale": rp.rule.rationale,
                "live": bool(rp.live and p.live),
                "rule_live_flag": bool(rp.live),
                "threshold": rp.threshold,
                "live_key": rp.rule.live_key,
                # Empty for a flag rule: no threshold tunable is registered for
                # one, and handing ops a key it cannot write would render a
                # control that silently does nothing.
                "threshold_key": (
                    "" if rp.rule.compare == CMP_FLAG else rp.rule.threshold_key
                ),
                "stats": stats,
            }
        )
    return {
        "enabled": p.enabled,
        "live": p.live,
        "rules": rules,
        "totals": {
            k: v for k, v in counters.items() if k != "rules"
        },
        "budget": _budget.snapshot(),
    }
