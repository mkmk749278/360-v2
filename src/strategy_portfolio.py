"""Strategy portfolio registry (Layer B) — context-affinity tags per strategy.

Every strategy in the portfolio — the live evaluator setup classes plus the
shadow-only units — is registered here with the market contexts it is *built
for*: the Wyckoff phases where its thesis pays and the sessions where it has
the liquidity to work (Crypto Market Doctrine §3, §5: a breakout is +EV in
markup/markdown and −EV in accumulation/distribution; a weekend 03:00-UTC
breakout is the lowest-quality trade on the board).

Observe-only in this phase: the tags are *displayed* in ops next to each
strategy's measured Strategy×Context edge (so the owner can see "this setup is
firing outside its design context — and the matrix confirms it loses there")
and consumed by the allocator's recommendation math.  Nothing here changes
which signals emit.

Pure data + pure functions, no I/O — safe to import anywhere.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, FrozenSet, Optional

from src.market_context import (
    MarketContext,
    PHASE_ACCUMULATION,
    PHASE_DISTRIBUTION,
    PHASE_MARKDOWN,
    PHASE_MARKUP,
    PHASE_QUIET,
    PHASE_RANGE,
    PHASE_VOLATILE,
    SESSION_LONDON,
    SESSION_NY,
    SESSION_OVERLAP,
)

# Shadow-only strategy unit names (src/shadow_strategies.py).  Deliberately NOT
# SetupClass members: the enum's values are stringly-coupled to money-path maps
# (_MAX_SL_PCT_BY_SETUP, telemetry) and these units must never reach them.
SHADOW_RANGE_FADE = "SHADOW_RANGE_FADE"
SHADOW_MEAN_REVERT = "SHADOW_MEAN_REVERT"
SHADOW_FUNDING_FADE = "SHADOW_FUNDING_FADE"
SHADOW_CASCADE_REVERSAL = "SHADOW_CASCADE_REVERSAL"

SHADOW_STRATEGY_NAMES = frozenset(
    {SHADOW_RANGE_FADE, SHADOW_MEAN_REVERT, SHADOW_FUNDING_FADE, SHADOW_CASCADE_REVERSAL}
)

# Tag groups.  An EMPTY frozenset means "any" — the strategy is not
# phase/session-selective by design (e.g. funding extremes trade the clock, not
# the chart).
_ANY: FrozenSet[str] = frozenset()
_TREND_PHASES = frozenset({PHASE_MARKUP, PHASE_MARKDOWN})
_RANGE_PHASES = frozenset({PHASE_ACCUMULATION, PHASE_DISTRIBUTION, PHASE_RANGE})
_LIQUID_SESSIONS = frozenset({SESSION_LONDON, SESSION_NY, SESSION_OVERLAP})


@dataclass(frozen=True)
class StrategyAffinity:
    """The contexts a strategy is designed for.  Empty set = any."""

    phases: FrozenSet[str] = _ANY
    sessions: FrozenSet[str] = _ANY

    def as_dict(self) -> Dict[str, list]:
        return {
            "phases": sorted(self.phases),
            "sessions": sorted(self.sessions),
        }


# One entry per SetupClass value (src/signal_quality.py — value == name) plus
# the shadow units.  Tags follow each setup's *thesis*, per the doctrine:
# continuation/breakout setups need a trending phase and a liquid session;
# fades and range tactics live where trends don't; sweep/liquidation reversals
# are volatility events; funding plays are calendar/positioning events.
AFFINITY: Dict[str, StrategyAffinity] = {
    # -- trend / continuation family: pays in markup/markdown, needs liquidity --
    "TREND_PULLBACK_CONTINUATION": StrategyAffinity(_TREND_PHASES, _LIQUID_SESSIONS),
    "TREND_PULLBACK_EMA": StrategyAffinity(_TREND_PHASES, _LIQUID_SESSIONS),
    "BREAKOUT_RETEST": StrategyAffinity(_TREND_PHASES, _LIQUID_SESSIONS),
    "MOMENTUM_EXPANSION": StrategyAffinity(
        _TREND_PHASES | {PHASE_VOLATILE}, _LIQUID_SESSIONS
    ),
    "VOLUME_SURGE_BREAKOUT": StrategyAffinity(_TREND_PHASES, _LIQUID_SESSIONS),
    "BREAKDOWN_SHORT": StrategyAffinity(
        frozenset({PHASE_MARKDOWN, PHASE_DISTRIBUTION}), _LIQUID_SESSIONS
    ),
    "DIVERGENCE_CONTINUATION": StrategyAffinity(_TREND_PHASES, _ANY),
    "CONTINUATION_LIQUIDITY_SWEEP": StrategyAffinity(_TREND_PHASES, _LIQUID_SESSIONS),
    "POST_DISPLACEMENT_CONTINUATION": StrategyAffinity(
        _TREND_PHASES | {PHASE_VOLATILE}, _LIQUID_SESSIONS
    ),
    "MA_CROSS_TREND_SHIFT": StrategyAffinity(_TREND_PHASES, _ANY),
    "MOVER_TREND_PULLBACK": StrategyAffinity(frozenset({PHASE_MARKUP}), _ANY),
    "MOVER_AVWAP_SCALP": StrategyAffinity(
        frozenset({PHASE_MARKUP, PHASE_VOLATILE}), _ANY
    ),
    "FVG_RETEST": StrategyAffinity(_TREND_PHASES, _LIQUID_SESSIONS),
    "FVG_RETEST_HTF_CONFLUENCE": StrategyAffinity(_TREND_PHASES, _LIQUID_SESSIONS),
    "SMC_ORDERBLOCK": StrategyAffinity(_TREND_PHASES | {PHASE_RANGE}, _LIQUID_SESSIONS),
    "OPENING_RANGE_BREAKOUT": StrategyAffinity(
        _TREND_PHASES | {PHASE_RANGE}, frozenset({SESSION_LONDON, SESSION_NY})
    ),
    "QUIET_COMPRESSION_BREAK": StrategyAffinity(
        frozenset({PHASE_QUIET, PHASE_ACCUMULATION}), _LIQUID_SESSIONS
    ),
    # -- range / fade / reversal family: pays where trends don't --
    "RANGE_REJECTION": StrategyAffinity(_RANGE_PHASES | {PHASE_QUIET}, _ANY),
    "LIQUIDITY_SWEEP_REVERSAL": StrategyAffinity(
        _RANGE_PHASES | {PHASE_VOLATILE}, _ANY
    ),
    "LIQUIDATION_REVERSAL": StrategyAffinity(frozenset({PHASE_VOLATILE}), _ANY),
    "EXHAUSTION_FADE": StrategyAffinity(
        frozenset({PHASE_DISTRIBUTION, PHASE_VOLATILE, PHASE_RANGE}), _ANY
    ),
    "FAILED_AUCTION_RECLAIM": StrategyAffinity(_RANGE_PHASES, _ANY),
    "SR_FLIP_RETEST": StrategyAffinity(_TREND_PHASES | {PHASE_RANGE}, _ANY),
    "RSI_MACD_DIVERGENCE": StrategyAffinity(_RANGE_PHASES, _ANY),
    # -- event-driven: trade positioning/flow, not the chart phase --
    "WHALE_MOMENTUM": StrategyAffinity(_TREND_PHASES | {PHASE_VOLATILE}, _ANY),
    "FUNDING_EXTREME_SIGNAL": StrategyAffinity(_ANY, _ANY),
    "MULTI_STRATEGY_CONFLUENCE": StrategyAffinity(_ANY, _ANY),
    # -- shadow-only units (no emit path; measured in the ledger only) --
    SHADOW_RANGE_FADE: StrategyAffinity(_RANGE_PHASES | {PHASE_QUIET}, _ANY),
    SHADOW_MEAN_REVERT: StrategyAffinity(_RANGE_PHASES | {PHASE_QUIET}, _ANY),
    SHADOW_FUNDING_FADE: StrategyAffinity(_ANY, _ANY),
    SHADOW_CASCADE_REVERSAL: StrategyAffinity(frozenset({PHASE_VOLATILE}), _ANY),
}

_DEFAULT_AFFINITY = StrategyAffinity()


def affinity(setup_class: str) -> StrategyAffinity:
    """Affinity for a strategy; unknown names get the any/any default."""
    return AFFINITY.get((setup_class or "").upper(), _DEFAULT_AFFINITY)


def is_context_aligned(setup_class: str, context_key: str) -> Optional[bool]:
    """Is this strategy inside its design context for the given composite key?

    ``context_key`` is ``MarketContext.context_key()`` — ``SESSION/PHASE/VOL/
    ROTATION``.  Returns ``None`` when the key is unparseable (unknown ≠
    misaligned), True/False otherwise.  An empty tag set never misaligns.
    """
    parts = (context_key or "").split("/")
    if len(parts) != 4:
        return None
    session, phase = parts[0], parts[1]
    aff = affinity(setup_class)
    if aff.phases and phase not in aff.phases:
        return False
    if aff.sessions and session not in aff.sessions:
        return False
    return True


def affinity_as_dict() -> Dict[str, Dict[str, list]]:
    """The whole registry as plain JSON-serialisable data (ops payload)."""
    return {name: aff.as_dict() for name, aff in sorted(AFFINITY.items())}


def build_context_payload(mc: MarketContext, now_ts: Optional[float] = None) -> Dict:
    """The ``data/market_context.json`` payload ops reads.

    Single source of truth for both the current global context vector and the
    strategy-affinity registry, so the ops dashboard hardcodes neither.
    """
    ts = now_ts if now_ts is not None else time.time()
    payload: Dict = dict(mc.as_signal_fields())
    payload["context_key"] = mc.context_key()
    payload["generated_at"] = ts
    payload["generated_at_iso"] = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts)
    )
    payload["strategy_affinity"] = affinity_as_dict()
    return payload
