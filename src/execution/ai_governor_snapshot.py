"""The Reality Feed, assembled — with every field carrying its own readability.

`docs/PLAN_AI_TRADE_GOVERNOR.md` §3. The brief asks the governor to read live
price action, order-book imbalance, CVD and BTC context. Three of those exist
and their coverage is narrower than the brief assumes:
``DEPTH_MAX_SYMBOLS`` and ``AGGTRADE_MAX_SYMBOLS`` are both 40, much of the
delivered book is promoted movers outside that, and ``DEPTH_LIVE_FOR_CONSUMERS``
defaults off.

So a large share of governed signals will be book-blind and flow-blind, and the
one thing this module must never do is let that look like a reading. `False`
because we could not ask and `False` because the answer is no are different
facts (`CLAUDE.md`, the money-path readability hard limit) — and the version of
that defect which reached a paying subscriber's screen on 2026-09-02 is the
reason every value here is a :class:`Readable` rather than a float.

Signed toward the trade
-----------------------
`cvd_slope_aligned` and `book_imbalance_aligned` are read from
``entry_features``, which already signs them. A falling CVD is the dip being
*sold* — bad for a long, exactly what a short wants — and the raw form scored
every SHORT backwards for a month without producing an empty column or a crash,
because the book is ~50/50 by side. Reading the raw values here and re-deriving
the sign would re-buy that bug; reading the `_aligned` form inherits the fix.

Immutability
------------
:class:`Snapshot` is frozen and holds no reference to a `Position` or a
`Signal`. The evaluation task outlives the tick that built it, and those objects
mutate underneath — a task holding a live `Position` would read fields that
changed after the model saw them, which is the same class as a denominator
computed from mutable state.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional

from src import fail_open
from src.execution.ai_governor_menu import Menu
from src.utils import get_logger

log = get_logger("ai_governor_snapshot")

#: Why a value could not be read. Named, because the next move differs: a
#: symbol outside the stream budget is a capacity decision, a stale feed is an
#: incident, and a disabled consumer flag is a switch somebody has not thrown.
WHY_OK = "ok"
WHY_NOT_SUBSCRIBED = "not_subscribed"
WHY_STALE = "stale"
WHY_DISABLED = "disabled"
WHY_ERROR = "error"


@dataclass(frozen=True)
class Readable:
    """A value, and whether we could observe it. Never a bare float.

    ``value is None`` means *we could not ask*. It is deliberately impossible to
    construct a readable-looking zero: `Readable.unknown(...)` is the only way
    to express absence, and it always carries a reason.
    """

    value: Optional[float]
    readable: bool
    reason: str = WHY_OK

    @classmethod
    def known(cls, value: float) -> "Readable":
        return cls(value=float(value), readable=True, reason=WHY_OK)

    @classmethod
    def unknown(cls, reason: str) -> "Readable":
        return cls(value=None, readable=False, reason=reason or WHY_ERROR)

    def as_dict(self) -> Dict[str, Any]:
        if not self.readable:
            return {"readable": False, "reason": self.reason}
        return {"readable": True, "value": round(float(self.value or 0.0), 6)}


@dataclass(frozen=True)
class Snapshot:
    """One position's world at one closed bar. Stored WITH the verdict.

    A row that cannot be re-scored from its own contents is not evidence, so
    everything the model saw is here — including the menu it was offered, which
    is what makes a choice key meaningful months later.
    """

    signal_id: str
    symbol: str
    side: str
    setup_class: str
    entry_regime: str
    trigger_tf: str
    as_of_bar_ms: int
    taken_at: float

    dist_to_tp1_pct: float
    dist_to_sl_pct: float
    r_multiple_now: float
    tp1_r_multiple: float
    mfe_pct: float
    mae_pct: float
    bars_since_entry: int

    book_imbalance_aligned: Readable
    cvd_slope_aligned: Readable
    price: Readable

    #: The price action, normalised to entry. See `bars_block`.
    bars: Mapping[str, Any] = field(default_factory=dict)
    #: What this trade required, and what those requirements read now.
    premise: Mapping[str, Any] = field(default_factory=dict)
    #: Where the trade sits in the FSM: breakeven, ladder stage, partials.
    lifecycle: Mapping[str, Any] = field(default_factory=dict)
    macro: Mapping[str, Any] = field(default_factory=dict)
    #: What KIND of instrument this is — liquidity band, 24h move, parabolic
    #: flag — from `instrument_xray`, which reads `pair_manager` and calls no
    #: vendor. Stamped and consumed by nothing: identifying the instrument is a
    #: measurement, and what to do about it is what a scored window decides.
    instrument: Mapping[str, Any] = field(default_factory=dict)
    menu: Optional[Menu] = None

    def as_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "signal_id": self.signal_id,
            "symbol": self.symbol,
            "side": self.side,
            "setup_class": self.setup_class,
            "entry_regime": self.entry_regime,
            "trigger_tf": self.trigger_tf,
            "as_of_bar_ms": self.as_of_bar_ms,
            "instrument": dict(self.instrument or {}),
            "dist_to_tp1_pct": round(self.dist_to_tp1_pct, 4),
            "dist_to_sl_pct": round(self.dist_to_sl_pct, 4),
            "r_multiple_now": round(self.r_multiple_now, 4),
            "tp1_r_multiple": round(self.tp1_r_multiple, 4),
            "mfe_pct": round(self.mfe_pct, 4),
            "mae_pct": round(self.mae_pct, 4),
            "bars_since_entry": int(self.bars_since_entry),
            "bars": dict(self.bars or {}),
            "premise": dict(self.premise or {}),
            "lifecycle": dict(self.lifecycle or {}),
            "book": self.book_imbalance_aligned.as_dict(),
            "flow": self.cvd_slope_aligned.as_dict(),
            "price": self.price.as_dict(),
            "macro": dict(self.macro),
        }
        if self.menu is not None:
            out.update(self.menu.as_dict())
        return out

    def blind_fraction(self) -> float:
        """Share of the optional context fields we could not read.

        On screen as `unknown_frac`. A governor is fail-open by design (its
        input is a measurement lane, and failing closed would freeze exits the
        moment a feed hiccupped), and the cost of fail-open is that an inert
        lane reads exactly like a working one on every count except this.
        """
        fields = (self.book_imbalance_aligned, self.cvd_slope_aligned)
        return sum(0 if f.readable else 1 for f in fields) / float(len(fields))

    def readability(self) -> Dict[str, Any]:
        """Per-field readability, beside the pooled fraction rather than instead.

        ``blind_fraction`` pools book and flow into one number, and those two
        have **different causes and different fixes**: an unsubscribed symbol is
        a stream-budget decision (`DEPTH_MAX_SYMBOLS` / `AGGTRADE_MAX_SYMBOLS`
        are both 40 while much of the delivered book is promoted movers), a
        stale feed is an incident, and a disabled consumer flag is a switch
        nobody threw. Pooling two states whose next moves differ is what this
        repo has paid for under several names, so the pooled figure stays for
        continuity and the split ships beside it.
        """
        return {
            "book_readable": bool(self.book_imbalance_aligned.readable),
            "book_reason": str(self.book_imbalance_aligned.reason or ""),
            "flow_readable": bool(self.cvd_slope_aligned.readable),
            "flow_reason": str(self.cvd_slope_aligned.reason or ""),
        }

    def digest(self) -> str:
        """Stable hash of what the model saw, for the ledger.

        Lets a reader tell "the model was asked twice about the same world and
        answered differently" from "the world moved" — which is the only handle
        anyone has on a non-deterministic component.
        """
        try:
            blob = json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":"))
        except Exception as exc:  # noqa: BLE001
            fail_open.record("ai_governor_snapshot.digest", exc)
            return ""
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def _readable_from(getter: Any, *, disabled_reason: str = "") -> Readable:
    """Call a context getter and convert its answer, never its absence.

    A getter that raises is `error`; one that returns None is *not* an error —
    it is the upstream saying it has nothing for this symbol, which is the
    common case on a promoted mover and must not fill `fail_open` with
    non-failures.
    """
    if disabled_reason:
        return Readable.unknown(disabled_reason)
    try:
        value = getter()
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor_snapshot.context", exc)
        return Readable.unknown(WHY_ERROR)
    if value is None:
        return Readable.unknown(WHY_NOT_SUBSCRIBED)
    return Readable.known(float(value))


#: How many closed bars of the trigger timeframe travel with a snapshot.
#:
#: The sweep already holds the whole array — it resolves it for the menu and
#: then discarded it, so every one of these is free: no vendor call, no
#: Firestore read, nothing that scales with the member count. Twelve is chosen
#: to cover the trade's own life on a 15m trigger without turning the payload
#: into a chart; the ATR and streak summaries below carry what a longer window
#: would have said.
BAR_ROWS = 12

#: Column order for `bars.rows`, published WITH the rows so a reader never has
#: to know it. A bare array of arrays whose meaning lives in a docstring is the
#: cross-repo contract this file already learned not to write.
BAR_COLUMNS = (
    "bars_ago",
    "open_pct",
    "favourable_extreme_pct",
    "adverse_extreme_pct",
    "close_pct",
    "vol_ratio",
)


def _pct_toward(entry: float, price: float, is_long: bool) -> Optional[float]:
    if entry <= 0 or price <= 0:
        return None
    raw = (price - entry) / entry * 100.0
    return round(raw if is_long else -raw, 4)


def _atr_pct(highs, lows, closes, period: int = 14) -> Optional[float]:
    """ATR as a percentage of the last close. None when the window is short."""
    n = min(len(highs), len(lows), len(closes))
    if n < period + 1 or closes[-1] <= 0:
        return None
    trs = []
    for i in range(n - period, n):
        prev = closes[i - 1]
        trs.append(max(highs[i] - lows[i], abs(highs[i] - prev), abs(lows[i] - prev)))
    if not trs:
        return None
    return round(sum(trs) / len(trs) / closes[-1] * 100.0, 4)


def bars_block(
    series: Optional[Mapping[str, Any]],
    *,
    entry: float,
    is_long: bool,
    trigger_tf: str,
    atr_pct_at_entry: Optional[float] = None,
) -> Dict[str, Any]:
    """The price action, normalised to entry and signed toward the trade.

    Absent from the payload entirely until 2026-09-10: the model was asked
    whether reality still supported a premise while being shown no bar of the
    market at all. `sweep` resolves this array for the menu on the same tick, so
    the whole block costs nothing.

    Every price is a PERCENT FROM ENTRY signed toward the trade, never a raw
    price. Two reasons, and the second is the load-bearing one: the book spans
    instruments quoted at 64,000 and at 0.02, so raw prices would make the model
    reason about scale rather than about the trade; and every other distance in
    this payload is already signed that way, so a raw block would be the one
    place direction has to be re-derived — which is exactly how `cvd_slope`
    scored every SHORT backwards for a month.
    """
    # `is None`, never a truthiness test: this argument is the candle mapping
    # and the values inside it are numpy arrays. Same hard limit as above.
    if series is None or len(series) == 0:
        return {"readable": False, "reason": WHY_STALE, "tf": str(trigger_tf or "")}
    try:
        highs = [float(v) for v in series.get("high", [])]
        lows = [float(v) for v in series.get("low", [])]
        closes = [float(v) for v in series.get("close", [])]
        raw_opens = [float(v) for v in series.get("open", [])]
        opens = raw_opens if len(raw_opens) > 0 else closes
        vols = [float(v) for v in series.get("volume", [])]
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor_snapshot.bars", exc)
        return {"readable": False, "reason": WHY_ERROR, "tf": str(trigger_tf or "")}

    n = min(len(highs), len(lows), len(closes), len(opens))
    if n < 2 or entry <= 0:
        return {"readable": False, "reason": WHY_STALE, "tf": str(trigger_tf or "")}

    take = min(BAR_ROWS, n)
    base_vol = None
    if len(vols) >= take + 20:
        window = vols[-take - 20:-take]
        base_vol = (sum(window) / len(window)) if window else None

    rows: List[List[Optional[float]]] = []
    for k in range(take, 0, -1):
        i = n - k
        fav = highs[i] if is_long else lows[i]
        adv = lows[i] if is_long else highs[i]
        vol_ratio = None
        if base_vol and base_vol > 0 and len(vols) > i:
            vol_ratio = round(vols[i] / base_vol, 3)
        rows.append([
            k - 1,
            _pct_toward(entry, opens[i], is_long),
            _pct_toward(entry, fav, is_long),
            _pct_toward(entry, adv, is_long),
            _pct_toward(entry, closes[i], is_long),
            vol_ratio,
        ])

    # Consecutive closes moving AGAINST the trade. The cheapest honest measure
    # of "it stopped working", and one no scalar in the old payload could give:
    # `r_multiple_now` says where the trade is and never how it got there.
    streak = 0
    for i in range(n - 1, 0, -1):
        delta = closes[i] - closes[i - 1]
        if (delta if is_long else -delta) < 0:
            streak += 1
        else:
            break

    atr_now = _atr_pct(highs, lows, closes)
    ratio = None
    if atr_now and atr_pct_at_entry:
        try:
            ratio = round(float(atr_now) / float(atr_pct_at_entry), 3)
        except Exception:  # noqa: BLE001
            ratio = None
    last_range_atr = None
    if atr_now and closes[-1] > 0:
        rng = (highs[-1] - lows[-1]) / closes[-1] * 100.0
        last_range_atr = round(rng / atr_now, 2) if atr_now > 0 else None

    return {
        "readable": True,
        "tf": str(trigger_tf or ""),
        "n": len(rows),
        "columns": list(BAR_COLUMNS),
        "rows": rows,
        "atr_pct_now": atr_now,
        # From the signal's own geometry stamp, so a volatility CHANGE is
        # readable rather than an absolute nobody can scale.
        "atr_pct_at_entry": atr_pct_at_entry,
        "atr_ratio_now_vs_entry": ratio,
        "closes_against_streak": streak,
        "range_last_bar_atr": last_range_atr,
        "vol_ratio_last": rows[-1][5] if rows else None,
        "note": (
            "Percent from ENTRY, signed toward the trade: positive is in its "
            "favour on both a LONG and a SHORT."
        ),
    }


def lifecycle_block(signal: Any, original_sl: float) -> Dict[str, Any]:
    """Where this trade is in the FSM — facts the model could not previously see.

    A breakeven-shifted trade has no risk left to reduce, and a governor shown
    only `dist_to_sl_pct` cannot tell that from a trade still carrying its full
    designed stop. Tightening the first is pure downside; it was indistinguishable
    from tightening the second.
    """
    try:
        stop = float(getattr(signal, "stop_loss", 0.0) or 0.0)
        entry = float(getattr(signal, "entry", 0.0) or 0.0)
        moved = None
        if original_sl > 0 and entry > 0 and stop > 0:
            moved = abs(abs(entry - stop) - original_sl) > (original_sl * 0.01)
        return {
            "breakeven_set": bool(getattr(signal, "breakeven_set", False)),
            "trailing_stage": int(getattr(signal, "trailing_stage", 0) or 0),
            "partial_close_pct": float(getattr(signal, "partial_close_pct", 0.0) or 0.0),
            "stop_moved_since_entry": moved,
            "status": str(getattr(signal, "status", "") or ""),
        }
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor_snapshot.lifecycle", exc)
        return {}


def build_snapshot(
    *,
    signal: Any,
    trigger_tf: str,
    as_of_bar_ms: int,
    bars_since_entry: int,
    last_price: Optional[float],
    menu: Menu,
    book_getter: Any = None,
    flow_getter: Any = None,
    macro: Optional[Mapping[str, Any]] = None,
    instrument: Optional[Mapping[str, Any]] = None,
    series: Optional[Mapping[str, Any]] = None,
    premise: Optional[Mapping[str, Any]] = None,
    now: Optional[float] = None,
) -> Snapshot:
    """Assemble one snapshot from a signal plus injected context getters.

    The getters are injected rather than imported so this module has no opinion
    about which store is live — and so a test drives the real shapes instead of
    a fixture that chooses a location and then agrees with you about it.
    """
    entry = float(getattr(signal, "entry", 0.0) or 0.0)
    stop = float(getattr(signal, "stop_loss", 0.0) or 0.0)
    tp1 = float(getattr(signal, "tp1", 0.0) or 0.0)
    is_long = str(getattr(signal, "direction", "")).upper().endswith("LONG")

    # The denominator is the risk the trade was SIZED for, never the stop as it
    # stands now. `trade_monitor` moves `sig.stop_loss` in place (BE shift, TP1
    # park, trail), so dividing by it reports a BE-shifted −0.1% loser as
    # exactly −1.00R — the defect that flipped the sign of a whole window's
    # headline (#848). `original_sl_distance` is the field that survives.
    risk = float(getattr(signal, "original_sl_distance", 0.0) or 0.0)
    if risk <= 0:
        risk = abs(entry - stop) if entry > 0 and stop > 0 else 0.0

    price = (
        Readable.known(last_price)
        if last_price and last_price > 0
        else Readable.unknown(WHY_STALE)
    )

    def _pct(target: float) -> float:
        if entry <= 0 or target <= 0:
            return 0.0
        raw = (target - entry) / entry * 100.0
        return raw if is_long else -raw

    move_pct = 0.0
    if price.readable and entry > 0:
        raw = (float(price.value or 0.0) - entry) / entry * 100.0
        move_pct = raw if is_long else -raw

    r_now = 0.0
    if risk > 0 and price.readable and entry > 0:
        signed = (float(price.value or 0.0) - entry) * (1 if is_long else -1)
        r_now = signed / risk

    return Snapshot(
        signal_id=str(getattr(signal, "signal_id", "") or ""),
        symbol=str(getattr(signal, "symbol", "") or ""),
        side="LONG" if is_long else "SHORT",
        setup_class=str(getattr(signal, "setup_class", "") or ""),
        entry_regime=str(getattr(signal, "entry_regime", "") or ""),
        trigger_tf=str(trigger_tf or ""),
        as_of_bar_ms=int(as_of_bar_ms),
        taken_at=float(now if now is not None else time.time()),
        dist_to_tp1_pct=_pct(tp1) - move_pct,
        dist_to_sl_pct=_pct(stop) - move_pct,
        r_multiple_now=r_now,
        tp1_r_multiple=(abs(tp1 - entry) / risk) if risk > 0 and tp1 > 0 else 0.0,
        mfe_pct=float(getattr(signal, "max_favorable_excursion_pct", 0.0) or 0.0),
        mae_pct=float(getattr(signal, "max_adverse_excursion_pct", 0.0) or 0.0),
        bars_since_entry=int(bars_since_entry),
        book_imbalance_aligned=_readable_from(book_getter) if book_getter
        else Readable.unknown(WHY_NOT_SUBSCRIBED),
        cvd_slope_aligned=_readable_from(flow_getter) if flow_getter
        else Readable.unknown(WHY_NOT_SUBSCRIBED),
        price=price,
        macro=dict(macro or {}),
        instrument=dict(instrument or {}),
        bars=bars_block(
            series,
            entry=entry,
            is_long=is_long,
            trigger_tf=trigger_tf,
            # The evaluator's own ATR at entry, so the ratio beside it reads as
            # a volatility CHANGE. `geo_atr_stop` is an absolute price distance;
            # converted here once rather than in the block, which has no entry.
            atr_pct_at_entry=(
                round(float(getattr(signal, "geo_atr_stop", 0.0) or 0.0) / entry * 100.0, 4)
                if entry > 0 and float(getattr(signal, "geo_atr_stop", 0.0) or 0.0) > 0
                else None
            ),
        ),
        premise=dict(premise or {}),
        lifecycle=lifecycle_block(signal, risk),
    )


def with_menu(snapshot: Snapshot, menu: Menu) -> Snapshot:
    """Attach the menu. Separate so the menu can be built from the same series
    the bar clock already resolved, without threading it through every call."""
    return Snapshot(
        **{
            **{k: getattr(snapshot, k) for k in snapshot.__dataclass_fields__ if k != "menu"},
            "menu": menu,
        }
    )


def macro_vector(context_key: str, btc: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """The macro half, as scalars the engine computed.

    **No news text, no social text, no user-supplied string.** The MacroWatchdog
    already pulls news through `openai_evaluator`; that lane must not be joined
    to this one. Free-form external text in a prompt whose output can close a
    live position is a money-path injection surface, and the structural defence
    (menu keys, closed vocabularies, invariants in code) is what holds if it is
    ever breached anyway — but the cheapest defence is not to open the door.
    """
    out: Dict[str, Any] = {"context_key": str(context_key or "")}
    for key in ("btc_ret_1m", "btc_ret_5m", "btc_atr_mult"):
        value = (btc or {}).get(key)
        out[key] = None if value is None else round(float(value), 6)
    out["btc_readable"] = bool(btc)
    return out


def macro_for_signal(
    signal: Any,
    *,
    opposes: Optional[bool] = None,
    oppose_reason: str = "",
    same_direction_open: Optional[int] = None,
) -> Dict[str, Any]:
    """The macro block for ONE position, with entry-time and now kept apart.

    This exists because the batch-level `macro_vector` above had **no caller**.
    `sweep(macro=..., macro_moved=...)` was never passed by `trade_monitor`, so
    the block reached the model as `{}` — no BTC context of any kind — and the
    `macro` trigger reason could never fire. Measured on the live lane
    2026-09-10: `trigger:r_band 52`, `trigger:near_tp 22`, `trigger:macro 0`,
    `trigger:flow_opposed 0`. The observed mix is exactly the two reasons that
    were reachable.

    **`btc_state` is stamped by the scanner at scoring time, so it is a fact
    about ENTRY.** It is published as `btc_state_at_entry` and never as a
    present-tense reading: labelling an entry-time value as "now" is the defect
    this repo has recorded under `entry_regime`, and the whole point of the
    governor is to compare then with now. The live half is
    `btc_opposes_now`, which comes from the monitor's own TTL-cached read of
    the same classifier the scanner used at birth — so entry-time and life-time
    BTC logic agree by construction rather than by coincidence.

    Tri-state throughout: `None` is "we could not ask", never "no".
    """
    try:
        raw_state = getattr(signal, "btc_state", None)
        raw_factor = getattr(signal, "btc_state_factor", None)
        return {
            "context_key": str(getattr(signal, "mc_pair_cohort", "") or ""),
            "entry_regime": str(getattr(signal, "entry_regime", "") or ""),
            "entry_regime_15m": str(getattr(signal, "entry_regime_15m", "") or ""),
            "btc_state_at_entry": (
                None if raw_state is None else round(float(raw_state), 4)
            ),
            "btc_state_factor_at_entry": (
                None if raw_factor is None else round(float(raw_factor), 4)
            ),
            # The live half. True means BTC's 1H AND 4H both lean against this
            # trade right now; None means the read was unavailable, which is
            # NOT the same as BTC being neutral.
            "btc_opposes_now": opposes,
            "btc_opposes_reason": str(oppose_reason or ""),
            "same_direction_open": same_direction_open,
            "note": (
                "btc_state_* are stamped at ENTRY. btc_opposes_now is a live "
                "read. They are separate fields on purpose."
            ),
        }
    except Exception as exc:  # noqa: BLE001
        fail_open.record("ai_governor_snapshot.macro_for_signal", exc)
        return {}
