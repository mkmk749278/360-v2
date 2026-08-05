"""SMC Detection Orchestrator.

Provides :class:`SMCDetector` which bundles all Smart Money Concepts detection
logic into a single, reusable component.  The result is returned as an
:class:`SMCResult` dataclass so ``main.py._scan_symbol()`` stays thin.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import numpy as np
from typing import Any, Dict, List, Optional

from src.ai_engine import WhaleAlert, detect_volume_delta_spike, detect_whale_trade
from src.order_flow import OrderFlowStore, is_oi_invalidated
from src.smc import FVGZone, LiquiditySweep, MSSSignal, detect_fvg, detect_liquidity_sweeps, detect_mss


def _env_float(name: str, default: float) -> float:
    """Read a float env var with a safe default; logs nothing to keep import-time clean."""
    raw = os.getenv(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


# B8 compliance: whale-trade USD threshold must be env-overridable so the
# operator can tune it without a redeploy.  Default $100k (lowered from
# $250k on 2026-05-27, and from $1M on 2026-05-11): truth report showed
# WHALE_MOMENTUM still producing 0 signals from 308k attempts even after
# the first cut to $250k.  $100k is the 80th-percentile single-trade
# ticket across top-75 alts — captures meaningful institutional flow
# without excluding mid-cap pairs whose tickets rarely exceed $200k.
# Companion change: _WHALE_MIN_TICK_VOLUME_USD in scalp.py also lowered
# $500k → $200k so the per-tick flow gate doesn't kill the path first.
WHALE_TRADE_USD_THRESHOLD: float = _env_float("WHALE_TRADE_USD_THRESHOLD", 100_000.0)

# Multiplier for `detect_volume_delta_spike` — fires when the absolute
# cumulative-delta is >= multiplier × average per-side flow.  Was
# hard-coded at 2.0 (extreme: imbalance ≥ total volume), which combined
# with whale_alert starvation produced the 99.92% momentum_reject
# bottleneck on WHALE_MOMENTUM.  1.3 = imbalance ≥ 1.3× average per-side
# flow — clear directional bias without requiring an extreme.  B8
# env-overridable so the operator can tune post-observation.
VOLUME_DELTA_SPIKE_MULTIPLIER: float = _env_float(
    "VOLUME_DELTA_SPIKE_MULTIPLIER", 1.3,
)
from src.utils import get_logger  # noqa: E402

log = get_logger("detector")

# Lower-timeframe lookup used for MSS confirmation
_LTF_MAP: Dict[str, str] = {
    "4h": "1h",
    "1h": "15m",
    "15m": "5m",
    "5m": "1m",
}

# Ordered preference for SMC detection timeframes (most sensitive first)
# Default: higher timeframes first so institutional sweeps take priority.
_SMC_TIMEFRAMES: tuple[str, ...] = ("4h", "1h", "15m", "5m", "1m")

# Minimum number of candles required for CVD divergence detection.
# Must be >= the default lookback passed to detect_cvd_divergence (20).
_CVD_MIN_CANDLES: int = 21


@dataclass
class SMCResult:
    """Unified output of SMC detection for a single symbol."""

    sweeps: List[LiquiditySweep] = field(default_factory=list)
    mss: Optional[MSSSignal] = None
    fvg: List[FVGZone] = field(default_factory=list)
    orderblocks: List[Dict[str, Any]] = field(default_factory=list)
    orderblocks_detector_status: str = "not_implemented"
    # ── Phase 3, dark ───────────────────────────────────────────────────
    # The detector's REAL output. It lands here rather than in `orderblocks`
    # so that the eight `bool(fvgs) or bool(orderblocks)` gates behave
    # byte-identically: assigning it above would ship the effect, not the
    # measurement. `ORDERBLOCKS_LIVE` is what moves it across.
    orderblocks_measured: List[Dict[str, Any]] = field(default_factory=list)
    # FVG at the wide window. `fvg` above stays the narrow list the gates
    # already read — derived from this one by an index filter, so it is the
    # same list `detect_fvg(lookback=10)` returns rather than an equivalent.
    fvg_wide: List[FVGZone] = field(default_factory=list)
    fvg_lookback_live: int = 0
    fvg_lookback_wide: int = 0
    whale_alert: Optional[WhaleAlert] = None
    volume_delta_spike: bool = False
    recent_ticks: List[Dict[str, Any]] = field(default_factory=list)
    oi_invalidated: bool = False
    cvd_divergence: Optional[str] = None  # "BULLISH", "BEARISH", or None
    cvd_divergence_age: Optional[int] = None  # candles since divergence formed
    cvd_divergence_strength: Optional[float] = None  # magnitude 0.0–1.0

    def as_dict(self) -> dict:
        """Return a plain dict for backward-compat with channel evaluate() calls."""
        return {
            "sweeps": self.sweeps,
            "mss": self.mss,
            "fvg": self.fvg,
            "orderblocks": self.orderblocks,
            "orderblocks_detector_status": self.orderblocks_detector_status,
            "orderblocks_measured": self.orderblocks_measured,
            "fvg_wide": self.fvg_wide,
            "fvg_lookback_live": self.fvg_lookback_live,
            "fvg_lookback_wide": self.fvg_lookback_wide,
            "whale_alert": self.whale_alert,
            "volume_delta_spike": self.volume_delta_spike,
            "recent_ticks": self.recent_ticks,
            "oi_invalidated": self.oi_invalidated,
            "cvd_divergence": self.cvd_divergence,
            "cvd_divergence_age": self.cvd_divergence_age,
            "cvd_divergence_strength": self.cvd_divergence_strength,
        }


class SMCDetector:
    """Runs all SMC + whale/tape detection for a given symbol snapshot."""

    def detect(
        self,
        symbol: str,
        candles: Dict[str, Dict[str, Any]],
        ticks: List[Dict[str, Any]],
        order_flow_store: Optional[OrderFlowStore] = None,
        lookback: int = 50,
        tolerance_pct: float = 0.05,
        smc_timeframes: Optional[tuple[str, ...]] = None,
    ) -> SMCResult:
        """Run full SMC detection and return an :class:`SMCResult`.

        Parameters
        ----------
        symbol:
            Trading symbol (used only for logging).
        candles:
            Dict of timeframe → OHLCV arrays, e.g. ``{"5m": {"high": ..., ...}}``.
        ticks:
            Recent trade ticks from the data store.
        order_flow_store:
            Optional :class:`src.order_flow.OrderFlowStore` for OI trend and
            CVD divergence checks.  When provided, detected sweeps are validated
            against the current OI trend (rising OI during a sweep in the
            opposing direction sets ``oi_invalidated = True``).  CVD divergence
            is also queried and attached to the result.
        lookback:
            Number of prior candles used to establish the recent high/low range
            for sweep detection.  Defaults to 50 (swing-appropriate).  Pass a
            smaller value (e.g. 20) for scalp-timeframe scans so that only the
            most recent support/resistance levels are considered.
        tolerance_pct:
            Wick-close tolerance for sweep detection (percentage).  Defaults to
            0.05.  Use a wider value (e.g. 0.15) for scalp scans to catch
            institutional sweeps that reclaim $100-200 past the swept level.
        smc_timeframes:
            Optional ordered tuple of timeframe keys to use for SMC detection.
            When provided, overrides the module-level :data:`_SMC_TIMEFRAMES`
            default.  This allows each channel to pass its own preferred order
            (e.g. scalp channels prefer low TFs first; swing/spot prefer high TFs).
        """
        result = SMCResult()
        _timeframes = smc_timeframes if smc_timeframes is not None else _SMC_TIMEFRAMES

        # ------------------------------------------------------------------
        # SMC detection (sweeps + MSS) across preferred timeframes
        # ------------------------------------------------------------------
        min_candles = lookback + 1
        _sweep_tf_key: Optional[str] = None
        for tf_key in _timeframes:
            cd = candles.get(tf_key)
            if cd is None or len(cd.get("close", [])) < min_candles:
                continue

            sweeps = detect_liquidity_sweeps(
                cd["high"], cd["low"], cd["close"],
                lookback=lookback,
                tolerance_pct=tolerance_pct,
                open_prices=cd.get("open"),
            )
            if not sweeps:
                continue

            result.sweeps = sweeps
            _sweep_tf_key = tf_key

            ltf_key = _LTF_MAP.get(tf_key, "1m")
            ltf_cd = candles.get(ltf_key)
            if ltf_cd and len(ltf_cd.get("close", [])) > 1:
                mss_sig = detect_mss(sweeps[0], ltf_cd["close"])
                result.mss = mss_sig

            break  # use first timeframe that has a sweep

        # ------------------------------------------------------------------
        # FVG detection – independent of sweeps so that ScalpFVGChannel,
        # ScalpOrderblockChannel, and other channels can fire without sweeps.
        # Uses the sweep timeframe if available, otherwise the first TF with
        # enough candles.
        # ------------------------------------------------------------------
        _fvg_tf_key = _sweep_tf_key
        if _fvg_tf_key is None:
            _fvg_tf_key = next(
                (tf for tf in _timeframes if candles.get(tf) and
                 len(candles[tf].get("close", [])) >= min_candles),
                None,
            )
        if _fvg_tf_key is not None:
            _fvg_cd = candles[_fvg_tf_key]
            # Phase 3. Detect ONCE at the wide window; the live list is that
            # result filtered by index, which is exactly what
            # `detect_fvg(lookback=narrow)` returns. A wide lookback subsumes a
            # narrow one, so this is one pass rather than two on a path that
            # runs per scan, per symbol, per channel.
            from src import layer3_repair as _l3

            _lb_live, _lb_wide = _l3.lookbacks()
            result.fvg_lookback_live = _lb_live
            result.fvg_lookback_wide = _lb_wide
            _n_bars = len(np.asarray(_fvg_cd["close"]).ravel())
            result.fvg_wide = detect_fvg(
                _fvg_cd["high"], _fvg_cd["low"], _fvg_cd["close"],
                lookback=max(_lb_live, _lb_wide),
            )
            _fvg_narrow = _l3.narrow_from_wide(
                result.fvg_wide, _n_bars, _lb_live,
            )
            # Effect flag OFF by default: the gates keep reading the narrow
            # list. This is the line that makes the change dark rather than
            # live, and it is the only line that has to move to activate it.
            result.fvg = result.fvg_wide if _l3.fvg_wide_live() else _fvg_narrow

            # The detector that has never existed. Its output lands under its
            # own key; `result.orderblocks` stays empty until the flag flips.
            if _l3.orderblocks_enabled():
                result.orderblocks_measured = _l3.detect_orderblocks(
                    _fvg_cd["high"], _fvg_cd["low"], _fvg_cd["close"],
                    _fvg_cd.get("open"),
                )
                if _l3.orderblocks_live():
                    result.orderblocks = result.orderblocks_measured
            result.orderblocks_detector_status = _l3.detector_status()
            _l3.observe(
                fvg_narrow=_fvg_narrow,
                fvg_wide=result.fvg_wide,
                orderblocks=result.orderblocks_measured,
            )

        # ------------------------------------------------------------------
        # Order flow validation (OI trend check requires sweeps)
        # ------------------------------------------------------------------
        if order_flow_store is not None and result.sweeps:
            primary_sweep = result.sweeps[0]
            oi_trend = order_flow_store.get_oi_trend(symbol)
            oi_change_pct = order_flow_store.get_oi_change_pct(symbol)

            if is_oi_invalidated(oi_trend, primary_sweep.direction.value, oi_change_pct):
                result.oi_invalidated = True
                log.debug(
                    "{}: OI RISING ({:+.2%}) during {} sweep – signal invalidated",
                    symbol, oi_change_pct, primary_sweep.direction.value,
                )

        # ------------------------------------------------------------------
        # CVD divergence – independent of sweeps so that ScalpCVDChannel can
        # fire on its own.  When sweeps exist the CVD confirms the sweep;
        # without sweeps the CVD channel still gets divergence data.
        # ------------------------------------------------------------------
        if order_flow_store is not None:
            tf_key_for_cvd = next(
                (tf for tf in _timeframes if candles.get(tf) and
                 len(candles[tf].get("close", [])) >= _CVD_MIN_CANDLES),
                None,
            )
            if tf_key_for_cvd is not None:
                # numpy is imported at module level; a function-local `import
                # numpy as np` here made `np` local to this whole method and
                # shadowed it for every earlier line.
                close_arr = np.asarray(
                    candles[tf_key_for_cvd]["close"], dtype=np.float64
                ).ravel()
                result.cvd_divergence = order_flow_store.get_cvd_divergence(
                    symbol, close_arr
                )
                if result.cvd_divergence:
                    log.debug(
                        "{}: CVD divergence detected – {}",
                        symbol, result.cvd_divergence,
                    )
                    # Populate metadata fields for ScalpCVDChannel.
                    # get_cvd_divergence_detail returns (type, age, strength)
                    # when available; fall back to sensible defaults.
                    _detail = getattr(order_flow_store, "get_cvd_divergence_detail", None)
                    if _detail is not None:
                        try:
                            _dtype, _age, _strength = _detail(symbol, close_arr)
                            result.cvd_divergence_age = _age
                            result.cvd_divergence_strength = _strength
                        except Exception:
                            # Method exists but failed — use defaults
                            result.cvd_divergence_age = 3
                            result.cvd_divergence_strength = 0.5
                    else:
                        # OrderFlowStore doesn't have the detail method yet —
                        # provide reasonable defaults so CVD channel doesn't
                        # reject via _CVD_REQUIRE_METADATA.
                        result.cvd_divergence_age = 3
                        result.cvd_divergence_strength = 0.5

        # ------------------------------------------------------------------
        # Whale / tape detection
        # ------------------------------------------------------------------
        if ticks:
            recent = ticks[-100:]
            result.recent_ticks = recent

            # Scan the recent-tick window for ANY whale trade rather than only
            # checking the most recent tick.  Pre-fix, a $1M whale at tick[-50]
            # was overwritten by every subsequent small tick, so the alert was
            # detectable for ~50–100ms — almost never aligned with a 15s scan
            # cycle.  The institutional-impact thesis lasts minutes; the
            # detection window must too.  We walk newest-first so the alert
            # carries the freshest qualifying trade.
            whale_alert: Optional[WhaleAlert] = None
            for t in reversed(recent):
                candidate = detect_whale_trade(
                    t.get("price", 0.0),
                    t.get("qty", 0.0),
                    threshold_usd=WHALE_TRADE_USD_THRESHOLD,
                )
                if candidate is not None:
                    whale_alert = candidate
                    break
            result.whale_alert = whale_alert

            buy_v = sum(
                t.get("qty", 0) * t.get("price", 0)
                for t in recent
                if not t.get("isBuyerMaker", True)
            )
            sell_v = sum(
                t.get("qty", 0) * t.get("price", 0)
                for t in recent
                if t.get("isBuyerMaker", True)
            )
            avg_delta = (buy_v + sell_v) / 2.0 if (buy_v + sell_v) > 0 else 0.0
            result.volume_delta_spike = detect_volume_delta_spike(
                buy_v - sell_v, avg_delta,
                multiplier=VOLUME_DELTA_SPIKE_MULTIPLIER,
            )

        return result
