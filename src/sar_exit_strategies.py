"""Stop-management what-ifs, stepped forward on the same bars as the SAR arm.

**The owner's question (2026-08-09):** *"add strategies to check what if you
move SL after moving 3% etc"*. That is a question about **stop management**,
which is a different axis from every exit catalog this system already has —
``exit_sim`` and ``dark_exit_sim`` both ladder *targets* and leave the stop
where the evaluator put it. Nothing anywhere has ever priced moving the stop.

**Why this is stepped and not replayed.** Every arm on ``/signals/sar-live``
exists because a replay could not answer whether a mechanism is *operable* — the
page's whole identity is "this is not a replay". A stop-management rule replayed
after the fact inherits exactly the defect the live arm was built to escape, and
it would be a strictly worse measurement sitting on the same page claiming the
same standing. So each rule carries its own state and is advanced one closed bar
at a time by :func:`step`, from the same loop, over the same bars, under the same
anchor and replay guards the SAR arm already passes.

The conservative judgements, all of which lean against the rules
-----------------------------------------------------------------
* **A stop moves at a bar's CLOSE, never inside it.** A rule triggered by bar
  *i* is armed for bar *i+1* onward. OHLC cannot order two touches inside one
  bar, so arming mid-bar would let a rule harvest a move on the same bar that
  might have stopped it out first. This is the single biggest reason a naive
  version of this measurement reads better than it should.
* **A gap through the stop fills at the bar's open** — worse, never better. The
  same rule ``_close`` already applies to the SAR arm.
* **When one bar both arms a rule and breaches its new stop, the breach wins**
  and the row is flagged ``ambiguous`` rather than silently resolved the
  flattering way.
* **The original stop is never widened.** Every rule here can only move a stop
  *toward* price; a rule that moved it away would breach the risk the trade was
  sized for, which is the defect the SAR arm itself was found to have.

What is deliberately absent
---------------------------
There is **no fee here and no blended "best strategy" number**. Figures are
gross, like every other stamp in this lane, and the surface charges the round
trip to the baseline and the rules alike — charging it to the rules only would
manufacture an edge out of the fee. And a single headline over all rules would
move with the rule mix rather than with any mechanism, which is the same reason
``/signals/sar-live`` publishes two fills and two denominators and calls neither
"the" answer.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# --------------------------------------------------------------------------- #
# Rule catalog — ONE writer
# --------------------------------------------------------------------------- #
#
# Ops renders whatever this ships and looks each key up for its copy; it does
# not keep a second catalog. `MEASUREMENT_SUFFIXES` drifted for a week under
# exactly that shape, and the fix for a drifting mirror is not a second mirror.
# A rule ops has never heard of renders under its raw key rather than vanishing.

#: Move the stop to breakeven (the entry price) once the trade has run ``trigger``
#: percent in our favour.
KIND_BREAKEVEN = "breakeven"
#: Move the stop to ``lock`` percent of profit once the trade has run ``trigger``.
KIND_LOCK = "lock"
#: Once the trade has run ``trigger``, trail the stop ``distance`` percent behind
#: the running peak, ratcheting toward price only.
KIND_TRAIL = "trail"

#: Built once by :func:`build_catalog`. The rules are immutable and shared.
_CATALOG: Optional[Dict[str, "Rule"]] = None


class Rule:
    """One stop-management rule. Immutable; all per-arm state lives in the dict."""

    __slots__ = ("key", "label", "kind", "trigger", "lock", "distance")

    def __init__(
        self,
        key: str,
        label: str,
        kind: str,
        *,
        trigger: float,
        lock: float = 0.0,
        distance: float = 0.0,
    ) -> None:
        self.key = key
        self.label = label
        self.kind = kind
        self.trigger = float(trigger)
        self.lock = float(lock)
        self.distance = float(distance)


def build_catalog() -> Dict[str, Rule]:
    """The rules stamped on every arm.

    Kept deliberately short. Nineteen cells on 46 signals is how
    ``/signals/entry-features`` ended up with one rule clearing 95% *in the
    backwards direction* against a ~62% familywise chance of a spurious hit —
    and a book this size cannot support a wide sweep. Eight rules across three
    mechanisms, with the trigger swept only where the sweep is the question.

    **Built once.** ``step`` runs per bar, per rule, per arm, inside
    TradeMonitor's poll — the hot path the cost rules name explicitly. Rebuilding
    eight objects on every call is pure CPU waste on a loop that already carries
    two SAR walks per signal. The rules are immutable, so one instance is safe to
    share; ``Rule.__slots__`` keeps it honest.
    """
    global _CATALOG
    if _CATALOG is not None:
        return _CATALOG
    rules = [
        Rule("be_1", "BE stop after +1%", KIND_BREAKEVEN, trigger=1.0),
        Rule("be_2", "BE stop after +2%", KIND_BREAKEVEN, trigger=2.0),
        Rule("be_3", "BE stop after +3%", KIND_BREAKEVEN, trigger=3.0),
        Rule("be_5", "BE stop after +5%", KIND_BREAKEVEN, trigger=5.0),
        Rule("lock1_3", "Lock +1% after +3%", KIND_LOCK, trigger=3.0, lock=1.0),
        Rule("lock2_5", "Lock +2% after +5%", KIND_LOCK, trigger=5.0, lock=2.0),
        Rule("trail2_3", "Trail 2% behind peak after +3%", KIND_TRAIL, trigger=3.0, distance=2.0),
        Rule("trail1_2", "Trail 1% behind peak after +2%", KIND_TRAIL, trigger=2.0, distance=1.0),
    ]
    _CATALOG = {r.key: r for r in rules}
    return _CATALOG


#: Stable render order, so the ops table cannot reorder itself between deploys.
CATALOG_ORDER: Tuple[str, ...] = tuple(build_catalog().keys())

# Terminal states. Three, not two — "the rule stopped us out", "the original
# stop caught us with the rule never armed" and "we ran out of window" have
# three different readings and pooling any two of them misdescribes the rule.
ST_OPEN = "OPEN"
ST_RULE_STOP = "RULE_STOP"      # the managed stop was touched
ST_ORIGINAL_SL = "ORIGINAL_SL"  # the untouched original stop was touched
ST_HORIZON = "HORIZON"          # walked to the end of the arm's life, still open


def new_state(rule: Rule, entry: float, stop_loss: float, side: str) -> Dict[str, Any]:
    """Per-arm state for one rule, at the moment the arm opens."""
    return {
        "key": rule.key,
        "status": ST_OPEN,
        "armed": False,
        "armed_at_bar": None,
        # Starts on the trade's own stop: before the rule triggers, this is an
        # ordinary trade. A rule that never arms must therefore score exactly
        # the same as the baseline, which is what makes "would have removed"
        # readable — and there is a test pinning it.
        "stop": float(stop_loss),
        "peak_pct": 0.0,
        "fill": None,
        "pnl_pct": None,
        "bars": 0,
        "ambiguous": False,
    }


def new_states(entry: float, stop_loss: float, side: str) -> Dict[str, Dict[str, Any]]:
    cat = build_catalog()
    return {k: new_state(r, entry, stop_loss, side) for k, r in cat.items()}


def _pnl_pct(entry: float, price: float, is_long: bool) -> float:
    if entry <= 0:
        return 0.0
    return ((price - entry) if is_long else (entry - price)) / entry * 100.0


def _price_at_pct(entry: float, pct: float, is_long: bool) -> float:
    """The price that represents ``pct`` percent of profit from ``entry``."""
    return entry * (1.0 + pct / 100.0) if is_long else entry * (1.0 - pct / 100.0)


def step(
    states: Dict[str, Dict[str, Any]],
    *,
    entry: float,
    stop_loss: float,
    side: str,
    high: float,
    low: float,
    open_: float,
    bar_index: int,
) -> bool:
    """Advance every still-open rule over one closed bar. True if anything changed.

    The order inside the bar is the whole design, and it is pessimistic
    throughout:

    1. **Breach first.** The stop standing at the START of this bar (parked at
       the previous close) is what this bar can touch. A rule armed by *this*
       bar cannot save it.
    2. **Then arm.** The favourable extreme of this bar may trigger a rule, which
       takes effect from the next bar.

    Reversing those two steps is how a stop-management study reads better than
    the mechanism could ever have performed live.
    """
    cat = build_catalog()
    is_long = str(side or "").upper() == "LONG"
    changed = False

    for key, st in states.items():
        if st.get("status") != ST_OPEN:
            continue
        rule = cat.get(key)
        if rule is None:
            continue
        st["bars"] = int(st.get("bars") or 0) + 1
        parked = float(st["stop"])

        # ── 1. breach, against the stop this bar inherited ──────────────────
        breached = (low <= parked) if is_long else (high >= parked)
        if breached:
            gapped = (open_ <= parked) if is_long else (open_ >= parked)
            fill = open_ if gapped else parked
            st["fill"] = float(fill)
            st["pnl_pct"] = _pnl_pct(entry, fill, is_long)
            # Which stop caught us is the reading, not a detail: a rule that
            # never armed scores the baseline and must not be credited with
            # having "managed" anything.
            st["status"] = ST_RULE_STOP if st.get("armed") else ST_ORIGINAL_SL
            changed = True
            continue

        # ── 2. arm / ratchet, on this bar's favourable extreme ──────────────
        fav = _pnl_pct(entry, high if is_long else low, is_long)
        if fav > float(st.get("peak_pct") or 0.0):
            st["peak_pct"] = fav
            changed = True
        peak = float(st["peak_pct"])

        if not st.get("armed") and peak >= rule.trigger:
            st["armed"] = True
            st["armed_at_bar"] = bar_index
            changed = True

        if st.get("armed"):
            if rule.kind == KIND_BREAKEVEN:
                target = entry
            elif rule.kind == KIND_LOCK:
                target = _price_at_pct(entry, rule.lock, is_long)
            elif rule.kind == KIND_TRAIL:
                target = _price_at_pct(entry, max(0.0, peak - rule.distance), is_long)
            else:  # pragma: no cover - catalog is closed
                continue
            # Ratchet only. A stop that can move away from price would hand the
            # rule more risk than the trade was sized for — the exact defect the
            # SAR arm was measured to have, and not one to reintroduce here.
            better = (target > float(st["stop"])) if is_long else (target < float(st["stop"]))
            if better:
                st["stop"] = float(target)
                changed = True
    return changed


def finalize_open(
    states: Dict[str, Dict[str, Any]], *, entry: float, side: str, last_close: Optional[float]
) -> None:
    """Close out still-open rules at the horizon, marked to the last close.

    Named ``HORIZON`` rather than folded into a stop-out: the trade did not end,
    we stopped watching. Reporting it as an exit would book a result the market
    never gave, and reporting it as nothing would quietly drop the rules that
    were still winning — which is the direction that flatters every rule here.
    """
    is_long = str(side or "").upper() == "LONG"
    for st in states.values():
        if st.get("status") != ST_OPEN:
            continue
        st["status"] = ST_HORIZON
        if last_close is not None:
            st["fill"] = float(last_close)
            st["pnl_pct"] = _pnl_pct(entry, float(last_close), is_long)


def summarize(states: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """The compact per-rule block written to the ledger.

    Only what a reader needs, and every field is a fact about this arm: no
    aggregates, no ranking, no "best rule". Ranking across arms belongs to the
    surface that can show n beside it.
    """
    cat = build_catalog()
    out: Dict[str, Any] = {}
    for key in CATALOG_ORDER:
        st = states.get(key)
        if st is None:
            continue
        rule = cat[key]
        out[key] = {
            "label": rule.label,
            "kind": rule.kind,
            "trigger_pct": rule.trigger,
            "status": st.get("status"),
            "armed": bool(st.get("armed")),
            "armed_at_bar": st.get("armed_at_bar"),
            "stop": st.get("stop"),
            "fill": st.get("fill"),
            "pnl_pct": st.get("pnl_pct"),
            "peak_pct": st.get("peak_pct"),
            "bars": st.get("bars"),
        }
    return out


def catalog_manifest() -> List[Dict[str, Any]]:
    """The catalog as data, for the surface to render labels from.

    Shipped with the ledger so ops never keeps its own copy of the rules. This
    is the ``spec`` block pattern ``entry_features`` established for exactly the
    same reason.
    """
    cat = build_catalog()
    return [
        {
            "key": k,
            "label": cat[k].label,
            "kind": cat[k].kind,
            "trigger_pct": cat[k].trigger,
            "lock_pct": cat[k].lock,
            "trail_pct": cat[k].distance,
        }
        for k in CATALOG_ORDER
    ]
