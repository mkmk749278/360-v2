"""Market-Context Engine — the "what regime is it *right now*" vector.

This is Layer A of the Autonomous Regime-Adaptive Strategy Portfolio.  It answers,
per scan, the question every professional desk answers *before* it decides which
strategy to run: what phase, session, season, volatility, funding, and BTC-rotation
regime are we in?  The resulting :class:`MarketContext` vector is the **key** the
Strategy×Context edge matrix and the autonomous allocator route on.

Design (mirrors ``src/btc_state.py`` and ``src/invalidation_audit.py``):

* **Pure + self-contained.**  Every classifier is a plain function over primitives
  (UTC clock, ATR percentile, funding rate, a BTC-State read) — no network, no
  Firestore, no indicator-engine dependency — so the whole module is deterministically
  unit-testable and adds **zero** hot-path I/O (Cost Discipline).
* **Fail toward neutral.**  Missing/degenerate inputs yield ``UNKNOWN``/neutral, never
  an exception — a context read never blocks a scan.
* **Observe-only in Phase 1.**  The scanner *computes and stamps* the vector on every
  signal; nothing downstream *consumes* it to change live output until later phases
  gate on it.  Stamping is off the money path.

The context vector is deliberately **stringly-typed** (like ``entry_regime``) so it
stamps cleanly onto the signal, serialises into the truth report / ops edge matrix,
and forms a low-cardinality composite key via :meth:`MarketContext.context_key`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Vocabulary — low-cardinality tokens for each context dimension.
# ---------------------------------------------------------------------------

# Intraday session (UTC clock).  The London–NY overlap is where the biggest, cleanest
# moves happen; the weekend is thin/wicky/manipulated (research: doctrine §Sessions).
SESSION_OVERLAP = "OVERLAP"      # 12:00–16:00 UTC — London+NY, deepest liquidity
SESSION_NY = "NY"                # 16:00–22:00 UTC — US flow / macro
SESSION_LONDON = "LONDON"        # 07:00–12:00 UTC — volatile, fake-out prone
SESSION_ASIA = "ASIA"            # 00:00–07:00 UTC — quiet, range-bound
SESSION_OFF = "OFF_HOURS"        # 22:00–00:00 UTC — thinnest weekday window

# Wyckoff / cycle phase.  Trend/breakout setups pay in MARKUP/MARKDOWN; range tactics
# pay in ACCUMULATION/DISTRIBUTION; stand down in AMBIGUOUS (doctrine §Phase model).
PHASE_MARKUP = "MARKUP"
PHASE_MARKDOWN = "MARKDOWN"
PHASE_ACCUMULATION = "ACCUMULATION"
PHASE_DISTRIBUTION = "DISTRIBUTION"
PHASE_RANGE = "RANGE"                # range without a resolvable prior-trend bias
PHASE_VOLATILE = "VOLATILE_EXPANSION"
PHASE_QUIET = "QUIET"
PHASE_UNKNOWN = "AMBIGUOUS"

# Volatility regime, from ATR percentile + cascade flag.
VOL_COMPRESSED = "COMPRESSED"
VOL_NORMAL = "NORMAL"
VOL_EXPANDED = "EXPANDED"
VOL_CASCADE = "CASCADE"

# Funding / positioning regime, from the perp funding rate.
FUNDING_NEUTRAL = "NEUTRAL"
FUNDING_CROWDED_LONG = "CROWDED_LONG"     # longs pay shorts — crowded long
FUNDING_CROWDED_SHORT = "CROWDED_SHORT"   # shorts pay longs — crowded short
FUNDING_EXTREME_LONG = "EXTREME_LONG"
FUNDING_EXTREME_SHORT = "EXTREME_SHORT"
FUNDING_UNKNOWN = "UNKNOWN"

# BTC rotation regime (proxy from BTC-State until a dominance feed is wired).
ROTATION_BTC_RISING = "BTC_RISING"
ROTATION_BTC_FALLING = "BTC_FALLING"
ROTATION_NEUTRAL = "BTC_NEUTRAL"

# ---------------------------------------------------------------------------
# Thresholds — env-overridable (boot), following the invalidation_audit pattern.
# ---------------------------------------------------------------------------

# ATR-percentile cut points for the volatility regime.
_VOL_COMPRESSED_MAX_PCTILE: float = float(os.getenv("MC_VOL_COMPRESSED_MAX_PCTILE", "20"))
_VOL_EXPANDED_MIN_PCTILE: float = float(os.getenv("MC_VOL_EXPANDED_MIN_PCTILE", "75"))
_VOL_CASCADE_MIN_PCTILE: float = float(os.getenv("MC_VOL_CASCADE_MIN_PCTILE", "92"))

# Funding-rate magnitudes (fraction, e.g. 0.0005 = 0.05% per 8h).
_FUNDING_CROWDED_ABS: float = float(os.getenv("MC_FUNDING_CROWDED_ABS", "0.0005"))
_FUNDING_EXTREME_ABS: float = float(os.getenv("MC_FUNDING_EXTREME_ABS", "0.001"))

# BTC-State |b| above which BTC is "leading" (alts follow, counter-trend alt trades
# fight a headwind).  Below this, rotation is neutral.
_ROTATION_BTC_LED_ABS: float = float(os.getenv("MC_ROTATION_BTC_LED_ABS", "0.5"))


# ---------------------------------------------------------------------------
# Per-dimension classifiers — each pure, each fail-neutral.
# ---------------------------------------------------------------------------


def classify_session(ts: Optional[datetime] = None) -> tuple[str, bool, float]:
    """Return ``(session_token, is_weekend, session_quality)`` from the UTC clock.

    ``session_quality`` ∈ [0,1] is a liquidity/edge proxy: the London–NY overlap is
    best, the weekend worst.  Pure function of wall-clock time — cache once per scan.
    """
    now = ts or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)
    hour = now.hour + now.minute / 60.0
    # Monday=0 … Sunday=6.  Crypto trades weekends but thin & manipulated.
    is_weekend = now.weekday() >= 5

    if 12.0 <= hour < 16.0:
        session, base_q = SESSION_OVERLAP, 1.0
    elif 16.0 <= hour < 22.0:
        session, base_q = SESSION_NY, 0.85
    elif 7.0 <= hour < 12.0:
        session, base_q = SESSION_LONDON, 0.80
    elif 0.0 <= hour < 7.0:
        session, base_q = SESSION_ASIA, 0.45
    else:  # 22:00–24:00
        session, base_q = SESSION_OFF, 0.30

    quality = base_q * (0.6 if is_weekend else 1.0)
    return session, is_weekend, round(quality, 3)


def classify_volatility(
    atr_percentile: Optional[float],
    *,
    cascade_active: bool = False,
) -> str:
    """Volatility regime from ATR percentile (0–100).  Cascade flag overrides."""
    if cascade_active:
        return VOL_CASCADE
    if atr_percentile is None:
        return VOL_NORMAL
    try:
        p = float(atr_percentile)
    except (TypeError, ValueError):
        return VOL_NORMAL
    if p >= _VOL_CASCADE_MIN_PCTILE:
        return VOL_CASCADE
    if p >= _VOL_EXPANDED_MIN_PCTILE:
        return VOL_EXPANDED
    if p <= _VOL_COMPRESSED_MAX_PCTILE:
        return VOL_COMPRESSED
    return VOL_NORMAL


def classify_funding(funding_rate: Optional[float]) -> str:
    """Positioning regime from the perp funding rate (fraction per interval)."""
    if funding_rate is None:
        return FUNDING_UNKNOWN
    try:
        f = float(funding_rate)
    except (TypeError, ValueError):
        return FUNDING_UNKNOWN
    if f >= _FUNDING_EXTREME_ABS:
        return FUNDING_EXTREME_LONG
    if f <= -_FUNDING_EXTREME_ABS:
        return FUNDING_EXTREME_SHORT
    if f >= _FUNDING_CROWDED_ABS:
        return FUNDING_CROWDED_LONG
    if f <= -_FUNDING_CROWDED_ABS:
        return FUNDING_CROWDED_SHORT
    return FUNDING_NEUTRAL


def classify_rotation(btc_state: Optional[float]) -> tuple[str, bool]:
    """Return ``(rotation_token, btc_led)`` from the BTC-State read ``b ∈ [−1,+1]``.

    ``btc_led`` is True when BTC is moving hard enough that alts follow it (so a
    counter-BTC alt trade fights a headwind).  This is a proxy for BTC dominance until
    a live dominance feed is wired — honest about its source, never fabricated.
    """
    if btc_state is None:
        return ROTATION_NEUTRAL, False
    try:
        b = float(btc_state)
    except (TypeError, ValueError):
        return ROTATION_NEUTRAL, False
    btc_led = abs(b) >= _ROTATION_BTC_LED_ABS
    if not btc_led:
        return ROTATION_NEUTRAL, False
    return (ROTATION_BTC_RISING if b > 0 else ROTATION_BTC_FALLING), True


def classify_phase(
    regime_label: Optional[str],
    *,
    htf_trend_prior: Optional[str] = None,
    volatility: str = VOL_NORMAL,
) -> str:
    """Map a regime label (+ optional higher-TF prior trend + volatility) to a Wyckoff
    phase.

    The regime label is the *entry-TF* classification (``TRENDING_UP`` etc.).  The
    ``htf_trend_prior`` — the higher-timeframe trend the range formed *after* — is what
    separates ACCUMULATION (range after a downtrend) from DISTRIBUTION (range after an
    uptrend); without it a range is just ``RANGE``.  This is the one classifier that
    the setup-family selector (later phase) keys on to decide trend-vs-fade-vs-standdown.
    """
    r = (regime_label or "").upper()
    if not r:
        return PHASE_UNKNOWN

    # Explicit trends map straight to markup / markdown.
    if "TRENDING_UP" in r or r in {"STRONG_TREND_UP", "MARKUP", "BULL_LEG"}:
        return PHASE_MARKUP
    if "TRENDING_DOWN" in r or r in {"STRONG_TREND_DOWN", "MARKDOWN", "BEAR_LEG"}:
        return PHASE_MARKDOWN

    # Volatile expansion is its own phase (cascades / news spikes).
    if volatility in {VOL_CASCADE} or "VOLATILE" in r:
        return PHASE_VOLATILE

    # Quiet / low-vol compression.
    if "QUIET" in r or (volatility == VOL_COMPRESSED and "RANGING" in r):
        return PHASE_QUIET

    # Ranging: resolve accumulation vs distribution by the prior HTF trend.
    if "RANGING" in r or "RANGE" in r or "WEAK" in r:
        prior = (htf_trend_prior or "").upper()
        if "UP" in prior or "MARKUP" in prior or "BULL" in prior:
            return PHASE_DISTRIBUTION      # range at highs after an uptrend
        if "DOWN" in prior or "MARKDOWN" in prior or "BEAR" in prior:
            return PHASE_ACCUMULATION      # range at lows after a downtrend
        return PHASE_RANGE

    return PHASE_UNKNOWN


# ---------------------------------------------------------------------------
# The composite context vector.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MarketContext:
    """The per-scan market-context vector.  Immutable; cheap to build; serialisable.

    ``symbol``-scoped dimensions (phase / volatility / funding) vary per pair; the
    ``session`` and ``rotation`` dimensions are global and identical across the scan
    cycle (compute once, reuse).
    """

    session: str = SESSION_OFF
    is_weekend: bool = False
    session_quality: float = 0.0
    phase: str = PHASE_UNKNOWN
    volatility: str = VOL_NORMAL
    funding: str = FUNDING_UNKNOWN
    rotation: str = ROTATION_NEUTRAL
    btc_led: bool = False
    cascade_active: bool = False

    def context_key(self) -> str:
        """Low-cardinality composite key for the Strategy×Context edge matrix.

        Uses the four dimensions that most change a strategy's edge — session bucket,
        phase, volatility, and rotation — keeping the matrix's cardinality tractable
        (funding is stamped on the signal for analysis but kept out of the key to avoid
        combinatorial blow-up).
        """
        return f"{self.session}/{self.phase}/{self.volatility}/{self.rotation}"

    def as_signal_fields(self) -> dict:
        """Field dict for stamping onto a :class:`~src.channels.base.Signal`."""
        return {
            "mc_session": self.session,
            "mc_is_weekend": self.is_weekend,
            "mc_session_quality": self.session_quality,
            "mc_phase": self.phase,
            "mc_volatility": self.volatility,
            "mc_funding": self.funding,
            "mc_rotation": self.rotation,
            "mc_btc_led": self.btc_led,
            "mc_cascade_active": self.cascade_active,
            "mc_context_key": self.context_key(),
        }


def build_market_context(
    *,
    ts: Optional[datetime] = None,
    regime_label: Optional[str] = None,
    htf_trend_prior: Optional[str] = None,
    atr_percentile: Optional[float] = None,
    funding_rate: Optional[float] = None,
    btc_state: Optional[float] = None,
    cascade_active: bool = False,
) -> MarketContext:
    """Assemble the full :class:`MarketContext` from raw primitives the scanner holds.

    Every argument is optional and fails toward neutral, so a partially-warm scan still
    produces a usable (if coarser) context rather than raising.
    """
    session, is_weekend, quality = classify_session(ts)
    volatility = classify_volatility(atr_percentile, cascade_active=cascade_active)
    funding = classify_funding(funding_rate)
    rotation, btc_led = classify_rotation(btc_state)
    phase = classify_phase(
        regime_label, htf_trend_prior=htf_trend_prior, volatility=volatility
    )
    return MarketContext(
        session=session,
        is_weekend=is_weekend,
        session_quality=quality,
        phase=phase,
        volatility=volatility,
        funding=funding,
        rotation=rotation,
        btc_led=btc_led,
        cascade_active=bool(cascade_active or volatility == VOL_CASCADE),
    )
