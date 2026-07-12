"""360-Crypto-Eye-Scalping – configuration module.

All tunables live here so every other module simply does
``from config.settings import cfg`` and reads what it needs.
"""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Safe environment-variable parsing helpers (FINDING-010)
# ---------------------------------------------------------------------------

def _safe_int(name: str, default: str) -> int:
    """Parse an env var as ``int``, falling back to *default* on error."""
    raw = os.getenv(name, default)
    try:
        return int(raw)
    except (ValueError, TypeError):
        logging.warning(
            "Invalid integer for env var %s=%r — using default %s", name, raw, default
        )
        return int(default)


def _safe_float(name: str, default: str) -> float:
    """Parse an env var as ``float``, falling back to *default* on error."""
    raw = os.getenv(name, default)
    try:
        return float(raw)
    except (ValueError, TypeError):
        logging.warning(
            "Invalid float for env var %s=%r — using default %s", name, raw, default
        )
        return float(default)


def _safe_bool(name: str, default: str) -> bool:
    """Parse an env var as ``bool`` (true/1/yes → True, else False)."""
    return os.getenv(name, default).lower() in ("true", "1", "yes")


def _safe_choice(name: str, default: str, allowed: frozenset[str]) -> str:
    """Parse an env var as constrained string, fail-closing to ``default``."""
    raw = os.getenv(name, default)
    val = str(raw).strip().lower()
    if val in allowed:
        return val
    logging.warning(
        "Invalid choice for env var %s=%r — using default %s (allowed=%s)",
        name, raw, default, ",".join(sorted(allowed)),
    )
    return default


def _safe_symbol_set(name: str, default: str) -> frozenset[str]:
    """Parse comma-separated symbol list into an uppercase frozenset."""
    return frozenset(
        s.strip().upper()
        for s in os.getenv(name, default).split(",")
        if s.strip()
    )


# ---------------------------------------------------------------------------
# LOG_LEVEL validation (FINDING-033)
# ---------------------------------------------------------------------------
_VALID_LOG_LEVELS = frozenset(
    {"TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"}
)


# ---------------------------------------------------------------------------
# Boot-time validation for critical env vars (FINDING-011)
# ---------------------------------------------------------------------------

def validate_critical_env_vars() -> None:
    """Emit startup warnings for missing critical env vars.

    Called during engine boot (not at import time) so that test suites can
    import ``config`` without requiring a full ``.env`` file.
    """
    if not TELEGRAM_BOT_TOKEN:
        logging.warning(
            "⚠️  TELEGRAM_BOT_TOKEN is not set — Telegram alerts will be disabled."
        )
    if not TELEGRAM_ADMIN_CHAT_ID:
        logging.warning(
            "⚠️  TELEGRAM_ADMIN_CHAT_ID is not set — admin commands will be disabled. "
            "Set this to your personal Telegram chat ID (a numeric value like 123456789). "
            "Send /start to the bot and call https://api.telegram.org/bot<TOKEN>/getUpdates "
            "to find your chat ID."
        )
    else:
        # Log the length and first/last 2 chars so the operator can verify the format
        # without exposing the full value in logs.
        _aid = TELEGRAM_ADMIN_CHAT_ID.strip()
        logging.info(
            "ℹ️  TELEGRAM_ADMIN_CHAT_ID configured: length=%d, starts=%r ends=%r",
            len(_aid), _aid[:2], _aid[-2:],
        )
    if not TELEGRAM_ACTIVE_CHANNEL_ID:
        logging.warning(
            "⚠️  TELEGRAM_ACTIVE_CHANNEL_ID is not set — signals will not be delivered."
        )


# ---------------------------------------------------------------------------
# Binance endpoints
# ---------------------------------------------------------------------------
BINANCE_REST_BASE: str = os.getenv("BINANCE_REST_BASE", "https://api.binance.com")
# WebSocket base URLs — use Binance's documented routed-path form
# ``/market/stream`` per the 2023-12-15 "Important WebSocket Change Notice"
# (legacy ``/ws`` and ``/stream`` decommissioned 2026-04-23).  Connections
# without a routed path (``/public``, ``/market``, ``/private``) silently
# refuse to forward streams belonging to ``/market`` (kline, aggTrade,
# markPrice, forceOrder, ticker) — TCP+WS handshake succeeds but zero
# application-layer data ever arrives.  Discovered 2026-05-14 after a
# multi-hour bleeding incident where the engine connected cleanly but
# received zero TEXT frames; mobile-IP verification confirmed it wasn't
# our VPS specifically.
#
# All streams we subscribe to (``@kline_*``, ``@forceOrder``) belong to
# the ``/market`` path, so a single base URL works for both kline + liq
# managers.  ``_build_combined_stream_url`` defensively normalises any
# legacy value here to always produce the documented form so an
# env-override of the old path can't silently re-break this.
BINANCE_WS_BASE: str = os.getenv("BINANCE_WS_BASE", "wss://stream.binance.com:9443/market/stream")
BINANCE_FUTURES_REST_BASE: str = os.getenv("BINANCE_FUTURES_REST_BASE", "https://fapi.binance.com")
BINANCE_FUTURES_WS_BASE: str = os.getenv("BINANCE_FUTURES_WS_BASE", "wss://fstream.binance.com/market/stream")

# Mark-price all-symbols feed (src/execution/mark_price_feed.py).  Mark-price
# streams belong to the ``/market`` category, so the raw-stream form must use
# the routed ``/market/ws/<stream>`` path.  The pre-2026-04-23 legacy
# ``/ws/<stream>`` form still completes the TCP+WS handshake but never pushes
# a single frame — the silent-death mode that left the SL/TP backstop BLIND
# on every out-of-universe symbol (TAIKOUSDT/APEUSDT/POWERUSDT, 2026-07-10,
# F-07).  ``mark_price_feed`` defensively normalises a legacy override.
MARK_PRICE_FEED_WS_URL: str = os.getenv(
    "MARK_PRICE_FEED_WS_URL",
    "wss://fstream.binance.com/market/ws/!markPrice@arr@1s",
)
# The @1s all-symbols stream ticks every second when healthy.  A connection
# that stays silent this long is dead-but-open (the exact legacy-URL failure
# shape) — force a reconnect and log loudly instead of trusting it forever.
MARK_PRICE_FEED_SILENCE_TIMEOUT_SEC: float = _safe_float(
    "MARK_PRICE_FEED_SILENCE_TIMEOUT_SEC", "30"
)

# User Data Stream (src/execution/user_data_stream.py).  Private streams
# moved to ``/private/ws?listenKey=<key>&events=<e1>/<e2>/...`` in the same
# 2026-04-23 migration; the legacy ``/ws/<listenKey>`` form connects but
# delivers no payloads, and on the new endpoint omitting ``events`` ALSO
# delivers no payloads (confirmed in the field by unicorn-binance-websocket-api).
# The default event list mirrors everything the legacy URL streamed
# implicitly, so parser behaviour is unchanged (unknown types are skipped).
USER_DATA_STREAM_WS_BASE: str = os.getenv(
    "USER_DATA_STREAM_WS_BASE", "wss://fstream.binance.com/private/ws"
)
USER_DATA_STREAM_EVENTS: str = os.getenv(
    "USER_DATA_STREAM_EVENTS",
    "ORDER_TRADE_UPDATE/ACCOUNT_UPDATE/MARGIN_CALL/TRADE_LITE/"
    "ACCOUNT_CONFIG_UPDATE/STRATEGY_UPDATE/GRID_UPDATE/"
    "CONDITIONAL_ORDER_TRIGGER_REJECT/ALGO_ORDER_UPDATE/listenKeyExpired",
)

# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
# Active Trading channel — ALL signals from every scalp strategy are routed here.
TELEGRAM_ACTIVE_CHANNEL_ID: str = os.getenv("TELEGRAM_ACTIVE_CHANNEL_ID", "")
# Free channel — receives one condensed preview signal per day (confidence ≥ 75).
TELEGRAM_FREE_CHANNEL_ID: str = os.getenv("TELEGRAM_FREE_CHANNEL_ID", "")
TELEGRAM_ADMIN_CHAT_ID: str = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")

# ---------------------------------------------------------------------------
# AI / Sentiment keys (optional)
# ---------------------------------------------------------------------------
NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
SOCIAL_SENTIMENT_API_KEY: str = os.getenv("SOCIAL_SENTIMENT_API_KEY", "")

# Fear & Greed Index (free, no key needed)
FEAR_GREED_API_URL: str = os.getenv(
    "FEAR_GREED_API_URL", "https://api.alternative.me/fng/?limit=1"
)

# OpenAI GPT-4 – repurposed exclusively for macro/news event evaluation
# (no longer used in the trade-signal hot path)
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
# Kept for backward compatibility – no longer used by the scanner.
OPENAI_MIN_CONFIDENCE_THRESHOLD: float = float(
    os.getenv("OPENAI_MIN_CONFIDENCE_THRESHOLD", "85.0")
)
# Kept for backward compatibility – no longer used by the scanner.
OPENAI_HOT_PATH_BYPASS_CHANNELS: List[str] = ["360_SCALP"]

# ---------------------------------------------------------------------------
# Macro Watchdog – async background task for global market-event alerts
# ---------------------------------------------------------------------------
MACRO_WATCHDOG_ENABLED: bool = _safe_bool("MACRO_WATCHDOG_ENABLED", "true")
MACRO_WATCHDOG_POLL_INTERVAL: float = float(
    os.getenv("MACRO_WATCHDOG_POLL_INTERVAL", "300")  # seconds (5 min default)
)
MACRO_WATCHDOG_FEAR_GREED_THRESHOLD_LOW: int = int(
    os.getenv("MACRO_WATCHDOG_FEAR_GREED_THRESHOLD_LOW", "20")
)
MACRO_WATCHDOG_FEAR_GREED_THRESHOLD_HIGH: int = int(
    os.getenv("MACRO_WATCHDOG_FEAR_GREED_THRESHOLD_HIGH", "80")
)
# Phase-2 free-channel content rollout: BTC big-move alert.  When BTC
# moves ≥ this % in the last 1h, MacroWatchdog broadcasts an event-driven
# market update (HIGH severity at the threshold, CRITICAL at ≥5%).  The
# alert routes to admin AND free channel via the same _broadcast helper
# used by macro news / F&G alerts (see PR #274).
# Default 3.0% — captures a meaningful move while filtering routine
# intraday volatility on BTC.  Env-overridable per B8.
MACRO_BTC_MOVE_THRESHOLD_PCT: float = float(
    os.getenv("MACRO_BTC_MOVE_THRESHOLD_PCT", "3.0")
)
# Cooldown (seconds) per direction (up vs down) — prevents alert burst
# during sustained large moves.  Default 1h matches the candle window
# used to compute the move; cleaner one-alert-per-leg behaviour.
MACRO_BTC_MOVE_COOLDOWN_SEC: int = int(
    os.getenv("MACRO_BTC_MOVE_COOLDOWN_SEC", "3600")
)

# Phase 2b — BTC/ETH 1h regime-shift alerts.
# When the 1h close crosses the 21-period EMA on BTC or ETH the watchdog
# broadcasts a HIGH-severity alert to admin + free channel.  Per-symbol
# cooldown defaults to 4h to absorb chop when price hovers near EMA21.
MACRO_REGIME_SHIFT_ENABLED: bool = _safe_bool("MACRO_REGIME_SHIFT_ENABLED", "true")
MACRO_REGIME_SHIFT_COOLDOWN_SEC: int = int(
    os.getenv("MACRO_REGIME_SHIFT_COOLDOWN_SEC", "14400")
)

# ---------------------------------------------------------------------------
# Pre-TP grab — Phase A
# ---------------------------------------------------------------------------
# In QUIET-dominated markets most signals catch a small move (0.2–0.5%
# raw) before momentum dies and the invalidator kills near-breakeven.
# Truth-report data shows 2/3 of recent kills are PROTECTIVE — i.e. the
# kill saved money relative to where price went next.  But at typical
# subscriber leverage (10x) with 0.07% round-trip fees (= 0.7% on margin),
# a "near-breakeven" close is actually a ~0.7% NET LOSS.  Pre-TP banks a
# small symbolic win + moves SL to breakeven so the rest of the position
# becomes free, turning these would-be-net-losses into net-positive trades.
#
# Threshold derivation: at 10x leverage the breakeven price move (after
# fees) is ~0.07%.  Below that, fees eat the move.  +0.35% raw → +3.5%
# gross @ 10x → +2.8% net after fees — comfortably above noise.
#
# Default OFF until a runtime truth report verifies fire rate / fire
# timing match expectations.  Env-overridable per B8.
PRE_TP_ENABLED: bool = _safe_bool("PRE_TP_ENABLED", "false")
PRE_TP_THRESHOLD_PCT: float = float(os.getenv("PRE_TP_THRESHOLD_PCT", "0.35"))
# ATR-adaptive threshold (B11 fee-aware refinement).  Resolved threshold is
# ``max(PRE_TP_FEE_FLOOR_PCT, PRE_TP_ATR_MULTIPLIER × atr_pct)`` where
# ``atr_pct = atr_last / entry * 100`` from the latest 5m candle.  This lets
# pre-TP capture a +0.2-0.3% win on a low-vol pair (BNB-like) where the static
# 0.35% would never trigger, while still scaling up to +0.5%+ on volatile
# alts where 0.35% is noise.  When ATR is unavailable we fall back to the
# static ``PRE_TP_THRESHOLD_PCT`` (per soft-penalty doctrine — never block
# on missing data).
PRE_TP_ATR_MULTIPLIER: float = float(os.getenv("PRE_TP_ATR_MULTIPLIER", "0.5"))
# Hard fee-economic floor.  Below this, +0.2% raw at 10x = +1.3% net which is
# the minimum ratio where banking the win pays for the fees with margin.
# 0.07% raw is the breakeven point — anything below 0.20% destroys subscriber
# value.  Per B11.
PRE_TP_FEE_FLOOR_PCT: float = float(os.getenv("PRE_TP_FEE_FLOOR_PCT", "0.20"))
PRE_TP_MIN_AGE_SEC: int = int(os.getenv("PRE_TP_MIN_AGE_SEC", "30"))
PRE_TP_MAX_AGE_SEC: int = int(os.getenv("PRE_TP_MAX_AGE_SEC", "1800"))
# Default leverage assumption for subscriber-facing net-of-fees math.
# Engine-side decisions (the threshold itself) are derived assuming this.
PRE_TP_LEVERAGE: float = float(os.getenv("PRE_TP_LEVERAGE", "10.0"))
# Round-trip fee on a single-leg trade — taker entry (~0.05%) + maker exit
# (~0.02%) on Binance USDT-M futures.  At 10x this is 0.7% of margin.
PRE_TP_FEE_PCT_ROUND_TRIP: float = float(
    os.getenv("PRE_TP_FEE_PCT_ROUND_TRIP", "0.07")
)
# Setups that are STRUCTURALLY built for bigger moves — pre-TP would cap
# the thesis.  Breakouts (VSB / BDS / ORB) belong here.  Comma-separated.
PRE_TP_SETUP_BLACKLIST_RAW: str = os.getenv(
    "PRE_TP_SETUP_BLACKLIST",
    "VOLUME_SURGE_BREAKOUT,BREAKDOWN_SHORT,OPENING_RANGE_BREAKOUT",
)
# OWNER_BRIEF B17 — pre-TP fires a REAL partial close (not just SL→BE).
# *** Session 34 (2026-06-24) owner directive — engine default is now NO pre-TP. ***
# Profit-Lab on 494 live signals (ops.luminapp.org/profit) proved the engine's
# real pre-TP + invalidation exits NET −25.79% while a plain TP1-full exit nets
# −6.65% on the same signals (+19.14% edge).  The exit machinery, not the
# entries, was giving back the edge, so the default exit is now TP1-full against
# a fixed SL: grab_fraction default 0.0 = no pre-TP partial / no SL→BE ratchet.
# A user may still re-enable banking via the per-user dial (30% floor / 100%
# ceiling enforced in `src/api/user_overrides.py:_coerce_pretp`); NULL/unset =
# this engine default.
PRE_TP_GRAB_FRACTION: float = float(os.getenv("PRE_TP_GRAB_FRACTION", "0.0"))
# OWNER_BRIEF B17 — invalidation aggressiveness mode.
# *** Session 34 owner directive — engine default is now ``loose``. ***
# Same Profit-Lab finding: invalidation kills are part of the exit machinery the
# data says to stop.  ``loose`` = thesis-conservative, only the protective SL
# closes the trade (no momentum / trailing / adverse-excursion kills) → the
# position rides to TP1 or SL exactly as the winning lab method assumes.
# A user may still opt into ``standard``/``tight`` via the per-user dial.
# ``standard`` = current behaviour + MFE-protection on momentum kills;
# ``tight`` = capital-preservation (adds ATR-trailing kill at MFE ≥ 0.3R).
INVALIDATION_MODE_DEFAULT: str = os.getenv("INVALIDATION_MODE_DEFAULT", "loose")
# Session 34 — TP-ladder split for the engine-default exit.  Fractions of the
# filled qty closed at each take-profit leg; they sum to 1.0 and the last active
# leg absorbs the rounding residual (see signal_dispatch._compute_quantities).
# Default = TP1-full (100% @ TP1, no TP2/TP3) per the owner directive above.
# Env-overridable (B8): set e.g. TP1_CLOSE_FRACTION=0.5 / TP2_CLOSE_FRACTION=0.5
# to restore a two-leg ladder without a code change.
TP1_CLOSE_FRACTION: float = _safe_float("TP1_CLOSE_FRACTION", "1.0")
TP2_CLOSE_FRACTION: float = _safe_float("TP2_CLOSE_FRACTION", "0.0")
TP3_CLOSE_FRACTION: float = _safe_float("TP3_CLOSE_FRACTION", "0.0")
# Trailing-kill tunables (active in ``tight`` mode by default).  MFE
# threshold expressed in multiples of SL distance; retrace fraction of
# the MFE peak at which the kill fires.
INVALIDATION_TRAILING_MFE_R_DEFAULT: float = float(
    os.getenv("INVALIDATION_TRAILING_MFE_R_DEFAULT", "0.30")
)
INVALIDATION_TRAILING_RETRACE_PCT_DEFAULT: float = float(
    os.getenv("INVALIDATION_TRAILING_RETRACE_PCT_DEFAULT", "0.50")
)
# Regime-differentiated trailing-kill retrace (session 20, ships dark).
# In TRENDING regimes price routinely pulls back 50-65% of a leg without
# ending the trend — the 0.50 default kills profitable runners on normal
# continuation pauses.  When INVALIDATION_TRAILING_RETRACE_REGIME_AWARE
# is enabled, TRENDING_UP/TRENDING_DOWN signals use this wider threshold.
INVALIDATION_TRAILING_RETRACE_REGIME_AWARE: bool = _safe_bool(
    "INVALIDATION_TRAILING_RETRACE_REGIME_AWARE", "false"
)
INVALIDATION_TRAILING_RETRACE_PCT_TRENDING: float = float(
    os.getenv("INVALIDATION_TRAILING_RETRACE_PCT_TRENDING", "0.70")
)

# R-scaled trailing-kill ARM threshold (session 22, ships dark).
#
# The trailing kill arms at a flat ``INVALIDATION_TRAILING_MFE_R_DEFAULT``
# (0.30R) regardless of SL width.  Audit (invalidation_records.json,
# 2026-06-07) shows trailing_invalidation is the dominant SR_FLIP premature
# killer at 44% (7/16) — far above momentum_loss (16%) and adverse_excursion
# (18%).  Root cause: SR_FLIP carries wide structural SLs (1.6–2.5%), so 0.30R
# is only ~0.5–0.75% absolute profit; the kill arms at trivial profit and a
# normal reversal pullback (SR_FLIP routinely retraces >50% before continuing)
# then fires it near breakeven.  Confirmed case EDGEUSDT: armed at MFE_R=0.34,
# killed at +0.06% after a +0.56% peak, price then ran ~2.4% further in favour.
#
# Fix: scale the arm threshold proportional to SL width so wide-SL signals must
# bank a more meaningful R-multiple before trailing engages, while tight-SL
# setups are barely affected.  Applies to ALL setups (owner decision
# 2026-06-07 — global, not a SR_FLIP special-case).
#
#   arm_R = min(ARM_R_MAX, MFE_R_DEFAULT + ARM_R_PER_SL_PCT × sl_dist_pct)
#
# With defaults (base 0.30, +0.15R per 1% SL, cap 0.80):
#   0.8% SL → 0.42R   1.6% SL → 0.54R   2.5% SL → 0.675R
# The EDGE case (1.63% SL, armed 0.34R) would no longer arm → no premature kill.
#
# Ships false.  Shadow telemetry ([SHADOW] TRAILING_RSCALE_WOULD_SUPPRESS) logs
# every trailing kill that fires below the scaled arm so the suppression set is
# measurable (cross-reference against the audit's PROTECTIVE/PREMATURE split)
# before activation.
INVALIDATION_TRAILING_ARM_RSCALE_ENABLED: bool = _safe_bool(
    "INVALIDATION_TRAILING_ARM_RSCALE_ENABLED", "false"
)
INVALIDATION_TRAILING_ARM_R_PER_SL_PCT: float = _safe_float(
    "INVALIDATION_TRAILING_ARM_R_PER_SL_PCT", "0.15"
)
INVALIDATION_TRAILING_ARM_R_MAX: float = _safe_float(
    "INVALIDATION_TRAILING_ARM_R_MAX", "0.80"
)
PRE_TP_SETUP_BLACKLIST: frozenset = frozenset(
    s.strip() for s in PRE_TP_SETUP_BLACKLIST_RAW.split(",") if s.strip()
)
# Regimes in which pre-TP is allowed to fire.  TRENDING regimes are
# excluded — let TP1 catch the full trend ride.  Comma-separated.
PRE_TP_REGIME_ALLOWLIST_RAW: str = os.getenv(
    "PRE_TP_REGIME_ALLOWLIST",
    "QUIET,RANGING,VOLATILE",
)
PRE_TP_REGIME_ALLOWLIST: frozenset = frozenset(
    s.strip().upper() for s in PRE_TP_REGIME_ALLOWLIST_RAW.split(",") if s.strip()
)
# Regime-differentiated pre-TP suppression (session 20, ships dark).
# When enabled, signals dispatched in TRENDING_UP/TRENDING_DOWN entry
# regimes bypass pre-TP entirely — the full position rides the trend
# rather than banking 50% at +0.35% and capping the runner at that gain.
# Empirical: Binance realized data shows >40min TRENDING holds net
# +$1.049 (67% win rate) vs <40min holds -$0.492 (39% win rate);
# hold-time Pearson r = +0.379 — longer holds win more.
TRENDING_PRETP_SUPPRESSED: bool = _safe_bool("TRENDING_PRETP_SUPPRESSED", "false")

# ── Regime-per-exit: trend-aligned runner profile (§3.2b, Session 31) ─────────
# Raw Edge (all-time, 474 closed): book capture 5% with avg MFE 0.535% — the
# exit machinery banks ~1/20th of the move it reaches.  TRENDING_UP capture is
# the worst (−10%, 21% runners): trend signals bank 50% at the flat +0.35%
# pre-TP and trail only the residual, capping the runner exactly where it should
# ride.  The FSM already routes a trend-aligned pre-TP fill to the trailing path
# (_pretp_trail_path: keep TP2 live + ATR trail); this profile feeds it better —
# bank a SMALL partial, LATER (at an R-multiple of the stop), then let the trail
# run.  Owner-signed-off 2026-06-21 ("raised threshold + trailing").  Reversible
# env off-switch (default ON — testing phase); OFF restores the prior behaviour.
REGIME_PER_EXIT_ENABLED: bool = _safe_bool("REGIME_PER_EXIT_ENABLED", "true")
#: Pre-TP threshold floor for trend-aligned signals, as a multiple of the stop
#: distance.  1.0R = bank only once the move equals the risk taken — the residual
#: then trails for the rest of the run instead of being capped at +0.35%.
REGIME_TREND_PRETP_R_FACTOR: float = _safe_float("REGIME_TREND_PRETP_R_FACTOR", "1.0")
#: Grab fraction for trend-aligned signals — bank a small partial (30%) and let
#: the 70% residual ride the ATR trail past TP2 (vs the flat 50% default).
REGIME_TREND_GRAB_FRACTION: float = _safe_float("REGIME_TREND_GRAB_FRACTION", "0.30")


# Shadow telemetry for the dark exit flags (session 20 follow-up #3).
# When enabled (default), the engine logs a structured ``[SHADOW]`` line
# every time one of the dark exit flags WOULD fire but is currently off —
# i.e. TRENDING_PRETP_SUPPRESSED, PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED,
# INVALIDATION_BTC_CORRELATION_ENABLED.  This makes each flag's blast radius
# measurable from prod logs before it is switched on, so the owner can size
# the impact instead of flipping blind.  Behaviour-neutral: log-only, never
# changes an exit.  Set to false to silence if the lines get noisy.  Once a
# real flag is enabled its shadow path stops (it then actually fires).
DARK_FLAG_SHADOW_TELEMETRY: bool = _safe_bool("DARK_FLAG_SHADOW_TELEMETRY", "true")

# ---------------------------------------------------------------------------
# Graded BTC-State soft-confirmation (counter-trend-long fix — src/btc_state.py)
# ---------------------------------------------------------------------------
# Replaces the binary check_btc_direction_gate + direction-blind correlation
# penalty with a graded confidence haircut on signals that fight BTC's macro
# direction, scaled by per-pair downside coupling, asymmetric (counter-trend
# LONG ~2× the SHORT), and AUTO-RESTORING as BTC turns (recomputed per dispatch).
#
# Production phase (CLAUDE.md § Project Phase): ships DARK-FIRST.
#   * BTC_STATE_ENABLED (default ON) — compute + STAMP b/w_pair/factor on every
#     signal and shadow-log the would-be effect.  Changes NO live output on its
#     own; it is the observe-only measurement layer.
#   * BTC_STATE_HAIRCUT_ENABLED (default OFF) — actually MULTIPLY confidence by
#     factor.  Owner-sign-off to flip ON after the shadow window + backfill
#     confirm.  Until then the haircut is computed but never applied.
# The numeric knobs are PRE-CALIBRATION defaults — the shadow stamps + the
# btc_state backfill (scripts/btc_state_backfill.py) size them before activation.
BTC_STATE_ENABLED: bool = _safe_bool("BTC_STATE_ENABLED", "true")
BTC_STATE_HAIRCUT_ENABLED: bool = _safe_bool("BTC_STATE_HAIRCUT_ENABLED", "false")
BTC_STATE_K: float = _safe_float("BTC_STATE_K", "0.40")
BTC_STATE_FLOOR: float = _safe_float("BTC_STATE_FLOOR", "0.55")
BTC_STATE_CT_LONG_MULT: float = _safe_float("BTC_STATE_CT_LONG_MULT", "1.0")
BTC_STATE_CT_SHORT_MULT: float = _safe_float("BTC_STATE_CT_SHORT_MULT", "0.5")
BTC_STATE_SEVERE_SETUP_WEIGHT: float = _safe_float("BTC_STATE_SEVERE_SETUP_WEIGHT", "1.0")
BTC_STATE_MILD_SETUP_WEIGHT: float = _safe_float("BTC_STATE_MILD_SETUP_WEIGHT", "0.5")
# Per-cycle cache TTL for the (pair-independent) BTC-State read — keeps the
# multi-TF EMA/RSI/ATR compute off the per-signal hot path (Cost Discipline).
BTC_STATE_CACHE_TTL_SEC: float = _safe_float("BTC_STATE_CACHE_TTL_SEC", "10.0")
# Coupling timeframe (15m returns per ACTIVE_CONTEXT S38 design) + window.
BTC_STATE_COUPLING_TF: str = _safe_choice(
    "BTC_STATE_COUPLING_TF", "15m", frozenset({"5m", "15m", "1h"}),
)
BTC_STATE_COUPLING_LOOKBACK: int = _safe_int("BTC_STATE_COUPLING_LOOKBACK", "200")

# ---------------------------------------------------------------------------
# Market-Context Engine (src/market_context.py, Layer A) — Autonomous Portfolio
# ---------------------------------------------------------------------------
# Off the money path: when ON (default), the scanner computes + STAMPS the
# per-scan market-context vector (session / Wyckoff phase / volatility / funding
# / BTC-rotation) on every signal.  Nothing consumes it to change live output in
# Phase 1 — it is the key the Strategy×Context edge matrix and the autonomous
# allocator route on.  Pure/cheap: no hot-path network or Firestore reads.
MARKET_CONTEXT_ENABLED: bool = _safe_bool("MARKET_CONTEXT_ENABLED", "true")

# ---------------------------------------------------------------------------
# Shadow ledger / strategy portfolio measurement (Layer C) — Autonomous Portfolio
# ---------------------------------------------------------------------------
# ALL observe-only, off the money path: none of these change which signals emit
# or how they score.  They only measure, on real data, what WOULD have happened.
#
# Suppression Quality Audit: stamp every post-scoring gate-suppressed candidate
# (O(1) in-memory, no I/O) and forward-measure TP1-before-SL on real candles in
# the existing 5-min audit loop → per-gate KEEP/TUNE/DROP + edge-matrix feed.
SUPPRESSION_AUDIT_ENABLED: bool = _safe_bool("SUPPRESSION_AUDIT_ENABLED", "true")
# Shadow-only strategy units (src/shadow_strategies.py): range-fade, mean-revert,
# funding-fade, cascade-reversal.  They have NO path to the signal queue — their
# would-be trades enter the shadow ledger only, so the edge matrix can compare
# them against live evaluators per market context.
SHADOW_STRATEGIES_ENABLED: bool = _safe_bool("SHADOW_STRATEGIES_ENABLED", "true")
# Min seconds between two ledger stamps of the same (shadow unit, symbol) so a
# persisting condition yields one measurable entry per window, not one per scan.
SHADOW_STRATEGY_COOLDOWN_SEC: float = _safe_float("SHADOW_STRATEGY_COOLDOWN_SEC", "1800")
# Allocator recommendation mode (src/strategy_allocator.py, Layer D): every audit
# cycle, compute which strategies it WOULD activate/weight in the current context
# from the measured edge matrix, and persist the recommendation for ops.  Nothing
# consumes the recommendation — arming live promotion is a later owner decision.
ALLOCATOR_RECOMMEND_ENABLED: bool = _safe_bool("ALLOCATOR_RECOMMEND_ENABLED", "true")
# Safety-envelope bounds baked into the recommendation math (Layer E): the
# allocator can never recommend more concurrent strategies than this, nor weight
# a single strategy above this cap.  These bound RECOMMENDATIONS today; the same
# limits bind live promotion when the owner arms Phase 4.
ALLOCATOR_MAX_CONCURRENT_STRATEGIES: int = _safe_int("ALLOCATOR_MAX_CONCURRENT_STRATEGIES", "6")
ALLOCATOR_MAX_STRATEGY_WEIGHT: float = _safe_float("ALLOCATOR_MAX_STRATEGY_WEIGHT", "0.35")

# ---------------------------------------------------------------------------
# Counter-trend-LONG macro-direction suppression (S39 — the validated scalp filter)
# ---------------------------------------------------------------------------
# SCALP-FIRST (owner directive): this is a thin context filter on genuine counter-
# trend REVERSAL long scalps — NOT a macro/position trade, and NOT trend-following
# longs.  Only setups whose thesis is to fade the trend are in scope:
#   * LIQUIDITY_SWEEP_REVERSAL — a reversal long fighting recent structure.
#   * SR_FLIP_RETEST — in scope since the V2 long repair (S40): while the side
#     is statically off this is inert; the day SR_FLIP_LONG_ENABLED flips, the
#     macro layer protects the re-enabled longs from the steamroll case.
# Deliberately EXCLUDED: MOVER_TREND_PULLBACK.  Despite the −12.78% backfill aggregate,
# it is a trend-CONTINUATION setup — it longs a coin that is already ripping (riding
# its own momentum, by construction trend-ALIGNED with the coin).  Live evidence (the
# owner's feed: ALAB +4.15%, RIF +6.16% as MOVER longs while BTC was macro-bear) shows
# blocking it on BTC weakness kills working trend-following scalps.  The macro filter
# suppresses longs that fight the trend, never longs that ride it.
# Exits stay pure scalp; SHORTs and every non-reversal setup fire normally.  Suppresses
# only while the big trend (BTC and/or the coin's own) is heading DOWN, via
# src/btc_state.py::macro_direction, and AUTO-RESTORES when it turns up.
CT_LONG_MACRO_GATE_ENABLED: bool = _safe_bool("CT_LONG_MACRO_GATE_ENABLED", "true")
CT_LONG_MACRO_GATE_SETUPS: frozenset = frozenset(
    s.strip().upper()
    for s in os.getenv(
        "CT_LONG_MACRO_GATE_SETUPS", "LIQUIDITY_SWEEP_REVERSAL,SR_FLIP_RETEST"
    ).split(",")
    if s.strip()
)
# "A long needs BOTH to permit it" — suppress if EITHER layer reads DOWN.
CT_LONG_MACRO_USE_BTC: bool = _safe_bool("CT_LONG_MACRO_USE_BTC", "true")
CT_LONG_MACRO_USE_PER_COIN: bool = _safe_bool("CT_LONG_MACRO_USE_PER_COIN", "true")
# BTC macro layer — weekly (the cycle backdrop; the owner's 200-week thesis).
BTC_MACRO_TF: str = _safe_choice("BTC_MACRO_TF", "1w", frozenset({"1d", "1w"}))
BTC_MACRO_FAST_PERIOD: int = _safe_int("BTC_MACRO_FAST_PERIOD", "50")
BTC_MACRO_RECOVER_PERIOD: int = _safe_int("BTC_MACRO_RECOVER_PERIOD", "25")
BTC_MACRO_SLOW_PERIOD: int = _safe_int("BTC_MACRO_SLOW_PERIOD", "200")
BTC_MACRO_CACHE_TTL_SEC: float = _safe_float("BTC_MACRO_CACHE_TTL_SEC", "300.0")
# Per-coin layer — the coin's OWN higher-TF trend (daily: responsive, not weekly-slow).
COIN_MACRO_TF: str = _safe_choice("COIN_MACRO_TF", "1d", frozenset({"4h", "1d", "1w"}))
COIN_MACRO_FAST_PERIOD: int = _safe_int("COIN_MACRO_FAST_PERIOD", "50")
COIN_MACRO_RECOVER_PERIOD: int = _safe_int("COIN_MACRO_RECOVER_PERIOD", "25")
COIN_MACRO_SLOW_PERIOD: int = _safe_int("COIN_MACRO_SLOW_PERIOD", "200")
COIN_MACRO_CACHE_TTL_SEC: float = _safe_float("COIN_MACRO_CACHE_TTL_SEC", "300.0")

# Counter-trend SHORT macro mirror (S40).  ACTIVE — explicit owner sign-off
# 2026-07-03 ("Activate now", AskUserQuestion), same day it shipped dark (#687).
# Evidence: the 2026-07-01..03 clean window (64 real trades) put the ENTIRE
# short-side bleed in shorts fired against a weekly-BULL BTC macro (36 shorts,
# 25% win, −8.08% total; the book without them: +0.42%), while the intraday
# BTC-State haircut FAILED its acceptance test on the same window (the
# bleeding shorts were BTC-*aligned* at 5m/15m/1h — intraday dips inside the
# macro recovery).  Caveat accepted at activation: one weekly regime state
# observed; the gate auto-restores shorts the moment the macro turns down,
# and the flag is env-reversible (CT_SHORT_MACRO_GATE_ENABLED=false) if live
# data disagrees.  Mirror of CT_LONG_MACRO_GATE: suppress a counter-trend
# reversal SHORT while the big trend reads UP (BTC macro and/or the coin's
# own).  Scope = the window's 0–20%-win short bleeders; QUIET_COMPRESSION
# (67% win in the same regime) and SR_FLIP shorts (breakeven) stay out.
CT_SHORT_MACRO_GATE_ENABLED: bool = _safe_bool("CT_SHORT_MACRO_GATE_ENABLED", "true")
CT_SHORT_MACRO_GATE_SETUPS: frozenset = frozenset(
    s.strip().upper()
    for s in os.getenv(
        "CT_SHORT_MACRO_GATE_SETUPS",
        "LIQUIDITY_SWEEP_REVERSAL,FAILED_AUCTION_RECLAIM,BREAKDOWN_SHORT",
    ).split(",")
    if s.strip()
)
CT_SHORT_MACRO_USE_BTC: bool = _safe_bool("CT_SHORT_MACRO_USE_BTC", "true")
CT_SHORT_MACRO_USE_PER_COIN: bool = _safe_bool("CT_SHORT_MACRO_USE_PER_COIN", "true")

# ---------------------------------------------------------------------------
# Dynamic Tiering (Market Watchdog) — PR 2
# ---------------------------------------------------------------------------
# Enable/disable the background TierManager that periodically polls Binance
# global 24hr tickers and re-ranks the entire pair universe into Hot / Warm /
# Cold tiers based on volume + volatility.
DYNAMIC_TIER_ENABLED: bool = _safe_bool("DYNAMIC_TIER_ENABLED", "true")
# How often (seconds) the TierManager polls Binance aggregate ticker endpoints.
DYNAMIC_TIER_POLL_INTERVAL: float = float(
    os.getenv("DYNAMIC_TIER_POLL_INTERVAL", "300")  # 5 minutes default
)
# Number of pairs in Tier 1 (Hot) — highest volume + volatility rank.
DYNAMIC_TIER1_HOT_COUNT: int = _safe_int("DYNAMIC_TIER1_HOT_COUNT", "50")
# Total pairs in Tier 1 + Tier 2 combined; Tier 2 = (DYNAMIC_TIER12_WARM_CUTOFF - DYNAMIC_TIER1_HOT_COUNT).
DYNAMIC_TIER12_WARM_CUTOFF: int = _safe_int("DYNAMIC_TIER12_WARM_CUTOFF", "200")
# Weighting of 24h quote-volume in the composite ranking score (0–1).
DYNAMIC_TIER_VOLUME_WEIGHT: float = _safe_float("DYNAMIC_TIER_VOLUME_WEIGHT", "0.7")
# Weighting of absolute 24h price-change-percent in the composite ranking score (0–1).
DYNAMIC_TIER_VOLATILITY_WEIGHT: float = _safe_float("DYNAMIC_TIER_VOLATILITY_WEIGHT", "0.3")
# Redis key names for tier membership sets.
DYNAMIC_TIER1_REDIS_KEY: str = os.getenv("DYNAMIC_TIER1_REDIS_KEY", "tier_1_active")
DYNAMIC_TIER2_REDIS_KEY: str = os.getenv("DYNAMIC_TIER2_REDIS_KEY", "tier_2_active")
DYNAMIC_TIER3_REDIS_KEY: str = os.getenv("DYNAMIC_TIER3_REDIS_KEY", "tier_3_active")

# On-chain intelligence — Glassnode (optional)
ONCHAIN_API_KEY: str = os.getenv("ONCHAIN_API_KEY", "")

# Whale Alert (free tier) — https://whale-alert.io/
# Optional; without a key on-chain scores fall back to Glassnode-only neutral
WHALE_ALERT_API_KEY: str = os.getenv("WHALE_ALERT_API_KEY", "")

# Etherscan (free tier, 5 calls/sec) — https://etherscan.io/apis
ETHERSCAN_API_KEY: str = os.getenv("ETHERSCAN_API_KEY", "")

# Cornix auto-execution signal formatting
# When true, a Cornix-compatible block is appended to SPOT/GEM/SWING signals
CORNIX_FORMAT_ENABLED: bool = _safe_bool("CORNIX_FORMAT_ENABLED", "false")

# Dynamic SL/TP based on ATR percentile, market regime, and pair tier (PR_07).
# Set to "false" to revert to the static signal_params.py behaviour for safety.
DYNAMIC_SL_TP_ENABLED: bool = _safe_bool("DYNAMIC_SL_TP_ENABLED", "true")

# ATR-percentile → trailing-stop width (Fix B, regime-per-exit precondition).
# A runner's ATR trail must widen with volatility: a 1.5× ATR trail that is
# right in normal conditions gets stopped out by noise when ATR is at the top
# of its range.  The exit FSM selects the multiplier from the signal's
# atr_percentile_at_entry via trail_atr_multiplier() below.  Defaults match the
# intraday research consensus (1.5× normal, widening to 2.5× in extreme vol).
TRAIL_ATR_PCTILE_HIGH: float = _safe_float("TRAIL_ATR_PCTILE_HIGH", "75.0")
TRAIL_ATR_PCTILE_EXTREME: float = _safe_float("TRAIL_ATR_PCTILE_EXTREME", "90.0")
TRAIL_ATR_MULT_NORMAL: float = _safe_float("TRAIL_ATR_MULT_NORMAL", "1.5")
TRAIL_ATR_MULT_HIGH: float = _safe_float("TRAIL_ATR_MULT_HIGH", "2.0")
TRAIL_ATR_MULT_EXTREME: float = _safe_float("TRAIL_ATR_MULT_EXTREME", "2.5")


def trail_atr_multiplier(atr_percentile: float) -> float:
    """Map an entry-time ATR percentile (0-100) to a trailing-stop ATR multiplier.

    Pure value mapping used by the exit FSM when activating a runner's ATR
    trail.  Wider trails in higher-volatility regimes prevent noise stop-outs;
    tighter trails in calm regimes lock gains sooner.

    * percentile >= TRAIL_ATR_PCTILE_EXTREME → TRAIL_ATR_MULT_EXTREME
    * percentile >= TRAIL_ATR_PCTILE_HIGH    → TRAIL_ATR_MULT_HIGH
    * otherwise                              → TRAIL_ATR_MULT_NORMAL
    """
    try:
        pct = float(atr_percentile)
    except (TypeError, ValueError):
        return TRAIL_ATR_MULT_NORMAL
    if pct >= TRAIL_ATR_PCTILE_EXTREME:
        return TRAIL_ATR_MULT_EXTREME
    if pct >= TRAIL_ATR_PCTILE_HIGH:
        return TRAIL_ATR_MULT_HIGH
    return TRAIL_ATR_MULT_NORMAL

# QUIET-regime TP compression multiplier (2026-05-23 doctrine).
# Per-signal data showed only 1/100 signals hit TP1; 18.9% reached TP1
# distance MFE but exited via pre-TP grab or invalidation before TP1 could
# fire. In QUIET regime (~63% of cycles per truth-snapshot regime
# distribution) the implied vol does not support the default TP geometry.
# Apply a single multiplier to all TP rungs in QUIET — bring them within
# reach of the typical MFE band so the residual position has a realistic
# chance of hitting TP1 instead of expiring in profit.
# RANGING regime retains the prior 0.9× compression; only QUIET is tightened.
TP_QUIET_COMPRESSION_FACTOR: float = float(os.getenv("TP_QUIET_COMPRESSION_FACTOR", "0.6"))

# Feedback-loop confidence adjustment (legacy "AI" history-based modifier).
# Default OFF as of 2026-05-23 — per-signal analysis of the last 100 closed
# signals showed the adjustment averaged +3.40 confidence-pts on 70% of
# signals, but the raised cohort had a 47% SL-rate vs 40% for the
# flat/lowered cohort (i.e. anti-predictive at current calibration).
# The history-aware design is correct in principle; the current calibration
# is not earning its keep. Re-enable only after the win-rate model is
# refit on a representative sample and the lift is shown to be predictive
# in a hold-out cycle of the truth report.
FEEDBACK_LOOP_ENABLED: bool = _safe_bool("FEEDBACK_LOOP_ENABLED", "false")

# Symbol-class narrative-pair bonus (2026-05-23 doctrine).
# Per-signal analysis of the last 100 closed signals showed extreme symbol
# concentration: 5 pairs (FARTCOIN, JTO, FIL, ENA, PLAY) carried +12.19%
# of net PnL on 43 signals — 51% of signal volume, 100% of net wins. These
# share a common structural property: they trade on narrative flow
# (DeFi-launchpad rotations, restaking, GameFi, memes) which has realistic
# intraday volatility in the current BTC-dominant compression regime.
#
# Apply a small confidence bonus to candidates on this list — enough to lift
# a marginal 67-conf signal into the 70+ band where SL rate is best (35%),
# without inflating into the 75-80 band where SL rate is worst (64%).
#
# The list is env-overridable so operators can re-tune the narrative cohort
# as market regime shifts (e.g. AI-token rotation → swap FARTCOIN for TAO).
# Set NARRATIVE_PAIR_BONUS=0 to disable the modifier without unsetting the
# list — preserves the symbol-class intent for telemetry.
NARRATIVE_PAIR_LIST_RAW: str = os.getenv(
    "NARRATIVE_PAIR_LIST",
    "FARTCOINUSDT,JTOUSDT,FILUSDT,ENAUSDT,PLAYUSDT",
)
NARRATIVE_PAIR_LIST: frozenset = frozenset(
    s.strip() for s in NARRATIVE_PAIR_LIST_RAW.split(",") if s.strip()
)
NARRATIVE_PAIR_BONUS: float = float(os.getenv("NARRATIVE_PAIR_BONUS", "2.0"))

# ---------------------------------------------------------------------------
# Signal dispatch — data freshness gate
# ---------------------------------------------------------------------------
#: Reject signal dispatch when the most-recent 1m kline for the symbol is
#: older than this.  Defends against frozen feeds (e.g. promoted pairs whose
#: WS subscription hasn't caught up, dropped streams without recovery) that
#: would otherwise dispatch signals against stale candle data and report
#: deterministic micro-loss closes (bug 2026-05-11: QUSDT carbon-copy
#: emissions at -0.10358%, all closing at the same frozen exit price).
#: 180s = up to 3 missed 1m candles, accommodates a single WS reconnect
#: + catch-up without false-positives on healthy feeds.
MAX_KLINE_STALENESS_SEC: int = _safe_int("MAX_KLINE_STALENESS_SEC", "180")

# ---------------------------------------------------------------------------
# Signal dispatch — level-rearm state machine
# ---------------------------------------------------------------------------
# Stuck-level repeat-fire suppression for level-anchored evaluators
# (SR_FLIP_RETEST / VOLUME_SURGE_BREAKOUT / BREAKDOWN_SHORT /
# FAILED_AUCTION_RECLAIM).  Bug observed 2026-05-13: ETHUSDT SR_FLIP SHORT
# dispatched 13× over 26h at identical entry 2305.32 while price chopped
# within 0.3% of the level — every dispatch expired at +0.11% MFE with
# zero TPs.  68% of paid emission was duplicates of 4 stuck levels.
#
# Doctrine: once a signal dispatches at a structural level, that level is
# "in play".  Block additional dispatches at the same level until price has
# decisively travelled away (real move).  Then re-arm automatically so the
# next genuine retest fires normally.

#: Multiplier applied to the dispatched signal's SL distance to derive the
#: excursion threshold.  SL distance is ATR-calibrated per evaluator at
#: signal creation, so it tracks per-pair volatility automatically without
#: us reaching back into indicator state.  1.5× SL = "decisive move past
#: thesis" benchmark.
LEVEL_REARM_SL_MULTIPLIER: float = _safe_float("LEVEL_REARM_SL_MULTIPLIER", "1.5")
#: Hard floor on the excursion threshold (e.g. 0.5%).  Prevents over-tight
#: gates on stablecoins / very low-vol majors where SL distance can be ~0.3%.
LEVEL_REARM_FLOOR_PCT: float = _safe_float("LEVEL_REARM_FLOOR_PCT", "0.005")
#: Hard ceiling on the excursion threshold (e.g. 3.0%).  Prevents over-loose
#: gates on volatile alt-coins (NAORI / BLUAI class) where SL distance can
#: spike to 5%+ in fast-moving regimes.
LEVEL_REARM_CEILING_PCT: float = _safe_float("LEVEL_REARM_CEILING_PCT", "0.030")
#: Fallback threshold when SL distance cannot be computed (entry or
#: stop_loss missing / zero on the Signal — should not happen in practice,
#: defensive only).
LEVEL_REARM_FALLBACK_PCT: float = _safe_float("LEVEL_REARM_FALLBACK_PCT", "0.012")
#: Max-age safety net.  After this many seconds with no excursion observed,
#: drop the level from the state machine (regime has likely shifted; let
#: the detector re-discover from current structure).
LEVEL_REARM_TTL_SEC: int = _safe_int("LEVEL_REARM_TTL_SEC", "86400")
#: Level-bucket granularity in basis points.  Levels within this distance
#: of a stored level_price are treated as the same level (protects against
#: clustering noise: 2305.32 vs 2305.33 on different scan cycles).
LEVEL_REARM_BUCKET_BPS: int = _safe_int("LEVEL_REARM_BUCKET_BPS", "5")

# ---------------------------------------------------------------------------
# Pair management
# ---------------------------------------------------------------------------
PAIR_FETCH_INTERVAL_HOURS: int = _safe_int("PAIR_FETCH_INTERVAL_HOURS", "6")
TOP_PAIRS_COUNT: int = _safe_int("TOP_PAIRS_COUNT", "150")
BATCH_REQUEST_DELAY: float = 0.75  # seconds between Binance REST calls
NEW_PAIR_MIN_CONFIDENCE: float = 50.0  # lower cap until enough data
# Minimum 24h USD volume for a symbol to be included in expensive API scans.
# Symbols below this threshold are skipped by the pre-filter before any
# order-book or kline fetches, reducing unnecessary weight consumption.
SCAN_MIN_VOLUME_USD: float = _safe_float("SCAN_MIN_VOLUME_USD", "1000000")

# ---------------------------------------------------------------------------
# PR8 — Volume Surge Breakout & Dynamic Pair Promotion
# ---------------------------------------------------------------------------
#: Volume multiplier vs rolling 7-candle average required for a surge signal.
SURGE_VOLUME_MULTIPLIER: float = _safe_float("SURGE_VOLUME_MULTIPLIER", "3.0")
#: Volume multiplier vs previous baseline required to promote a non-scanned pair.
SURGE_PROMOTION_VOLUME_MULTIPLIER: float = _safe_float("SURGE_PROMOTION_VOLUME_MULT", "5.0")
#: Seconds between status-pulse messages for each open signal.
SIGNAL_PULSE_INTERVAL_SECONDS: int = _safe_int("SIGNAL_PULSE_INTERVAL_SECONDS", "1800")
#: Funding rate absolute value above/below which extreme funding signals fire.
FUNDING_RATE_EXTREME_THRESHOLD: float = _safe_float("FUNDING_RATE_EXTREME_THRESHOLD", "0.001")
#: Maximum number of dynamically promoted pairs per scan cycle.
SURGE_PROMOTION_MAX_PAIRS: int = _safe_int("SURGE_PROMOTION_MAX_PAIRS", "5")
#: Minimum 24h price change % (absolute) to promote a pair via movers promotion.
MOVER_PROMOTION_MIN_PCT: float = _safe_float("MOVER_PROMOTION_MIN_PCT", "15.0")
#: Minimum 24h USD volume for movers-promoted pairs (lower than vol-surge gate).
MOVER_PROMOTION_MIN_VOLUME_USD: float = _safe_float("MOVER_PROMOTION_MIN_VOLUME", "5000000")
#: How many scan cycles a movers-promoted pair stays in the scan universe.
#: DEPRECATED for the ignition path — superseded by the time-based
#: MOVER_PROMOTION_TTL_SEC below. Retained for any external tooling.
MOVER_PROMOTION_CYCLES: int = _safe_int("MOVER_PROMOTION_CYCLES", "5")
#: How long (seconds) a mover stays in the scan universe after promotion. Once a
#: pair ignites we hold it long enough for VSB/BDS/MOVER_TREND_PULLBACK to find a
#: real entry as the move develops on 5m/15m structure — a ~25 s cycle-count hold
#: dropped pairs before any setup could form. Default 6 h (owner, 2026-06-28).
MOVER_PROMOTION_TTL_SEC: float = _safe_float("MOVER_PROMOTION_TTL_SEC", "21600")
#: Max concurrently-scanned mover-promoted pairs. Separate from the volume-surge
#: SURGE_PROMOTION_MAX_PAIRS — with a 6 h hold the old shared cap of 5 would fill
#: and starve fresh ignitions, so movers get their own (larger) budget.
MOVER_PROMOTION_MAX_PAIRS: int = _safe_int("MOVER_PROMOTION_MAX_PAIRS", "30")
#: Re-seed a promoted mover's candles when its 1m data is older than this many
#: seconds (2026-07-10).  Promoted movers sit outside the WS kline subscription
#: set — their candles came ONLY from the one-time promotion seed, so minutes
#: into a 6 h hold every evaluator was reading frozen data and (now that REST
#: seeds stamp freshness) the dispatch staleness gate would block them.  Keep
#: this below MAX_KLINE_STALENESS_SEC (180) so an actively-scanned mover never
#: trips that gate.  0 disables the refresh.
MOVER_CANDLE_REFRESH_SEC: float = _safe_float("MOVER_CANDLE_REFRESH_SEC", "120")
#: Max mover re-seeds per scan cycle — bounds the REST weight burst when many
#: promoted movers go stale in the same cycle (each re-seed is ~6 kline calls).
MOVER_CANDLE_REFRESH_MAX_PER_CYCLE: int = _safe_int("MOVER_CANDLE_REFRESH_MAX_PER_CYCLE", "8")
#: Max bid/ask spread (as a PERCENT of mid — same unit as ScanContext.spread_pct,
#: i.e. 0.5 == 0.5%) a mover-promoted pair may have to be scanned by the scalp
#: channel. Movers are lower-cap and run wider than blue chips, so this is looser
#: than the regular adaptive spread gate. NB: the old hard-coded gate used 0.005
#: against a percent-unit value — that meant 0.005%, ~100× too tight, and silently
#: skipped EVERY promoted mover before evaluation (the "nothing fires" root cause).
MOVER_MAX_SPREAD_PCT: float = _safe_float("MOVER_MAX_SPREAD_PCT", "0.5")

# ── Real-time mover IGNITION detector (catch movers at minute-zero) ───────────
# Replaces the lagging 24h-%change promotion trigger with a real-time signal off
# the `!ticker@arr` all-market futures stream: a short-window price move + a
# trade-rate burst vs the pair's own baseline + a min traded notional. When
# enabled, `_update_movers_promotion` promotes ignited pairs INSTEAD of the
# `MOVER_PROMOTION_MIN_PCT` 24h candidates; flip off to fall back to the 24h
# path. Pure in-memory arithmetic over a stream we already receive — no REST,
# no Firestore (Cost Discipline). See `src/mover_ignition.py`.
MOVER_IGNITION_ENABLED: bool = _safe_bool("MOVER_IGNITION_ENABLED", "true")
#: Trailing window (seconds) over which the price move and trade-rate are measured.
#: A burst is the window-averaged rate ÷ baseline, so it requires a *sustained*
#: surge (not a single-frame spike) — shorter window ⇒ earlier, noisier catch.
MOVER_IGNITION_WINDOW_SEC: float = _safe_float("MOVER_IGNITION_WINDOW_SEC", "30")
#: Minimum |price move| % within the window to count as a live move.
MOVER_IGNITION_MOVE_FLOOR_PCT: float = _safe_float("MOVER_IGNITION_MOVE_FLOOR_PCT", "1.0")
#: Trade-rate burst (window rate ÷ EWMA baseline) required — real-time RVOL.
MOVER_IGNITION_BURST_MULT: float = _safe_float("MOVER_IGNITION_BURST_MULT", "3.0")
#: Minimum traded quote notional (USD) within the window — filters micro-caps.
MOVER_IGNITION_MIN_NOTIONAL_USD: float = _safe_float("MOVER_IGNITION_MIN_NOTIONAL_USD", "100000")
#: Seconds a pair will not re-ignite after firing (avoids re-promote thrash).
MOVER_IGNITION_COOLDOWN_SEC: float = _safe_float("MOVER_IGNITION_COOLDOWN_SEC", "1800")
#: EWMA smoothing for the trade-rate baseline (small = slow/stable baseline).
MOVER_IGNITION_BASELINE_ALPHA: float = _safe_float("MOVER_IGNITION_BASELINE_ALPHA", "0.02")
#: Samples folded into the baseline before a burst is trusted (warmup gate).
MOVER_IGNITION_MIN_BASELINE_SAMPLES: int = _safe_int("MOVER_IGNITION_MIN_BASELINE_SAMPLES", "30")
#: Inter-frame gap (seconds) beyond which per-symbol state is reset, not measured.
MOVER_IGNITION_MAX_GAP_SEC: float = _safe_float("MOVER_IGNITION_MAX_GAP_SEC", "30")

# ── MOVER_TREND_PULLBACK path (Session 29, owner-approved) ────────────────────
# A continuation path for promoted movers: once a mover is MA-stacked, enter each
# pullback that tags the fast MA and reclaims in the trend direction.  VSB/BDS
# catch only the *ignition* breakout+retest and go silent once a mover trends;
# this path catches the recurring *continuation* pullbacks the owner trades by
# hand (MA cross → ride the stack → buy each dip to the MA).  Direction comes from
# the MA stack itself, so no aged HTF structure is needed (which is exactly why
# TPE, gated on a 1H structure a young mover lacks, cannot serve movers).
#
# Ships LIVE (testing phase — no subscribers yet, we ship changes live for fast
# iteration rather than behind dark flags; see CLAUDE.md § Project Phase).  Set
# MOVER_TREND_PULLBACK_ENABLED=false to fall back to shadow-only
# (``[SHADOW] MOVER_TREND_PULLBACK_WOULD_FIRE`` log, no live signal).
MOVER_TREND_PULLBACK_ENABLED: bool = _safe_bool("MOVER_TREND_PULLBACK_ENABLED", "true")
#: MA periods (SMA on 15m closes) defining the mover trend stack — match the
#: MA(7)/MA(25)/MA(99) the owner reads on the Binance 15m chart.
MOVER_TP_MA_FAST: int = _safe_int("MOVER_TP_MA_FAST", "7")
MOVER_TP_MA_MID: int = _safe_int("MOVER_TP_MA_MID", "25")
MOVER_TP_MA_SLOW: int = _safe_int("MOVER_TP_MA_SLOW", "99")
#: Band (%) around the fast MA within which a pullback wick counts as a "tag".
MOVER_TP_PULLBACK_BAND_PCT: float = _safe_float("MOVER_TP_PULLBACK_BAND_PCT", "0.35")
#: ATR buffer beyond the SL anchor (mid MA / pullback extreme) for the stop.
MOVER_TP_SL_BUFFER_ATR: float = _safe_float("MOVER_TP_SL_BUFFER_ATR", "0.5")
#: Minimum fast-MA↔slow-MA separation (%) for a pair to count as a "mover".
#: This is what makes the path mover-specific WITHOUT depending on the
#: mover-promotion bookkeeping — real movers (BTW, ESPORTS) enter the scan as
#: universe/young pairs, not via promotion, so gating on `is_mover_promoted`
#: locked the path out of its own targets.  A strong run puts MA7 far above
#: MA99 (or below, for shorts); a gently-trending blue chip won't clear this.
MOVER_TP_MIN_STACK_SEP_PCT: float = _safe_float("MOVER_TP_MIN_STACK_SEP_PCT", "3.0")

# ── Additional continuation triggers (Session 31, owner+research-approved) ────
# The path originally fired on ONE shape only: a shallow pullback that tags the
# FAST MA (SMA7) and reclaims.  Research (hyrotrader crypto-MA guide, pyramiding
# literature) says a strong mover offers several distinct continuation re-entries;
# catching only the shallowest one leaves most of the move's re-entries on the
# table.  Two further triggers, each gated, each stamped with its own
# `entry_trigger` tag so per-trigger win-rate is measurable and the weak one can
# be killed independently (same head-to-head discipline as VSB/BDS vs MOVER).
#
# Trigger DEEP — pullback to the MID MA (SMA25), the canonical "scale into the
# deeper dip" entry: higher-probability, better R, lower chase risk.  Reversible
# env off-switch (default ON — testing phase).
MOVER_TP_TRIGGER_DEEP_ENABLED: bool = _safe_bool("MOVER_TP_TRIGGER_DEEP_ENABLED", "true")
# Trigger CONSOL — a guarded consolidation break for movers that DON'T pull back
# (they grind).  Research is explicit that a naive "chase the breakout" entry is
# the classic mistake, so this fires ONLY when it is NOT extended: price holds
# above the fast MA, a tight K-bar micro-range breaks, AND volume confirms.
MOVER_TP_TRIGGER_CONSOL_ENABLED: bool = _safe_bool("MOVER_TP_TRIGGER_CONSOL_ENABLED", "true")
#: Bars in the consolidation window scanned for the micro-range break.
MOVER_TP_CONSOL_LOOKBACK: int = _safe_int("MOVER_TP_CONSOL_LOOKBACK", "6")
#: Max consolidation height (× ATR) for the range to count as "tight" — a wide
#: range is not a flag, it is the move itself; don't treat it as a base.
MOVER_TP_CONSOL_RANGE_ATR: float = _safe_float("MOVER_TP_CONSOL_RANGE_ATR", "1.5")
#: Anti-extension guard: max distance (× ATR) the breakout close may sit beyond
#: the fast MA.  1.0 is the strict reading of the "stop > 1.5× ATR = too sloppy"
#: rule from the continuation-pattern literature — keeps us off parabolic chases.
MOVER_TP_BREAKOUT_EXT_ATR: float = _safe_float("MOVER_TP_BREAKOUT_EXT_ATR", "1.0")
#: Volume confirmation on the breakout bar (× the consolidation-window average).
#: Research: a break without >=1.5× volume "is almost certainly a fake-out".
MOVER_TP_BREAKOUT_VOL_MULT: float = _safe_float("MOVER_TP_BREAKOUT_VOL_MULT", "1.5")

# ── MOVER_AVWAP_SCALP path (2026-06-28, owner+research-approved) ───────────────
# Anchored-VWAP continuation scalp for movers. Research (snappchart/TrendSpider/
# trademomentum VWAP-momentum playbooks) is unanimous: the professional way to
# scalp a confirmed mover is the VWAP anchored at the move's ORIGIN, traded WITH
# the AVWAP slope on pullbacks to it — the participant-cost reference, far more
# robust than an MA stack. Anchor = the swing extreme over a lookback (the start
# of the current leg); reuses compute_vwap over candles[anchor:]. Live by default
# (testing phase); MOVER_AVWAP_SCALP_ENABLED=false → shadow-only log, no signal.
MOVER_AVWAP_SCALP_ENABLED: bool = _safe_bool("MOVER_AVWAP_SCALP_ENABLED", "true")
#: Entry timeframe (matches the 15m the owner reads on the Binance chart).
MOVER_AVWAP_TF: str = os.getenv("MOVER_AVWAP_TF", "15m")
#: Candles scanned back for the swing anchor (start of the current leg).
MOVER_AVWAP_ANCHOR_LOOKBACK: int = _safe_int("MOVER_AVWAP_ANCHOR_LOOKBACK", "50")
#: Minimum net move (%) from the anchor to "now" to qualify as a real mover leg.
MOVER_AVWAP_MIN_MOVE_PCT: float = _safe_float("MOVER_AVWAP_MIN_MOVE_PCT", "3.0")
#: Min |AVWAP slope| over the last few bars (% of price) to confirm trend
#: direction — the "rising VWAP = long only / falling = short only" filter.
MOVER_AVWAP_SLOPE_MIN_PCT: float = _safe_float("MOVER_AVWAP_SLOPE_MIN_PCT", "0.02")
#: Bars back used to measure the AVWAP slope.
MOVER_AVWAP_SLOPE_LOOKBACK: int = _safe_int("MOVER_AVWAP_SLOPE_LOOKBACK", "3")
#: Band (%) around the AVWAP within which a pullback wick counts as a "tag".
MOVER_AVWAP_PULLBACK_BAND_PCT: float = _safe_float("MOVER_AVWAP_PULLBACK_BAND_PCT", "0.30")
#: Volume confirmation on the reclaim/bounce bar (× recent-bar average). Research:
#: "a reclaim without a volume spike is not a reclaim, it's a drift."
MOVER_AVWAP_VOL_MULT: float = _safe_float("MOVER_AVWAP_VOL_MULT", "1.5")
#: ATR buffer beyond the AVWAP/swing for the stop.
MOVER_AVWAP_SL_BUFFER_ATR: float = _safe_float("MOVER_AVWAP_SL_BUFFER_ATR", "0.5")

# ── Counter-trend hard-block on confirmed strong movers (Session 30, owner-approved) ─
# §3.2 #5 reserves HARD blocks for structural impossibility.  Fading a CONFIRMED
# strong mover with a reversal IS that case: SYNUSDT (+300%/7d, 4h+1h both stacked
# up) was repeatedly SHORTED by LIQUIDITY_SWEEP_REVERSAL → full SL (-3.36%).  The
# per-symbol direction gate only SOFT-penalises and EXEMPTS LSR/FAR, so a reversal
# fading a rocket got no penalty at all.  This gate HARD-rejects a counter-trend
# reversal/structure entry that opposes BOTH the pair's 1H and 4H EMA trend WHEN
# the move is mover-grade (1H or 4H EMA21/50 fan width >= the threshold below).  A
# gently-trending pair (narrow fan) keeps the soft penalty; only the parabolic case
# is hard-blocked.  Reversible env off-switch (default ON — testing phase).
COUNTERTREND_MOVER_HARD_BLOCK_ENABLED: bool = _safe_bool(
    "COUNTERTREND_MOVER_HARD_BLOCK_ENABLED", "true"
)
#: HTF EMA21/50 fan width (%) above which the aligned 1H+4H trend is "mover-grade".
#: ~3% mirrors MOVER_TP_MIN_STACK_SEP_PCT: a strong run fans the EMAs wide, an
#: ordinary trend keeps them within ~1-2%.
COUNTERTREND_MOVER_MIN_FAN_PCT: float = _safe_float("COUNTERTREND_MOVER_MIN_FAN_PCT", "3.0")

# Regime-aware volume floors (USD 24h volume).
# TRENDING/VOLATILE need depth for follow-through; RANGING/QUIET mean-reversion
# setups work fine with less liquidity.
REGIME_MIN_VOLUME_USD: Dict[str, float] = {
    "TRENDING_UP":   float(os.getenv("VOL_FLOOR_TRENDING",  "3000000")),
    "TRENDING_DOWN": float(os.getenv("VOL_FLOOR_TRENDING",  "3000000")),
    "VOLATILE":      float(os.getenv("VOL_FLOOR_VOLATILE",  "5000000")),
    "RANGING":       float(os.getenv("VOL_FLOOR_RANGING",   "1500000")),
    "QUIET":         float(os.getenv("VOL_FLOOR_QUIET",     "1000000")),
    "":              float(os.getenv("VOL_FLOOR_DEFAULT",   "2000000")),  # empty string key handles unknown/unset regime states (intentional fallback)
}
# Symbols permanently excluded from scanning. Two classes of junk:
#   1. Gold-pegged tokens + micro-caps (XAUT/PAXG/MMT/KOMA/STO).
#   2. Tokenized stocks — crypto-wrapped equities whose price discovery
#      happens during US regular trading hours, then drift through Asian/EU
#      hours. Scalp microstructure does not apply; they fire near-exclusively
#      SHORT and their quotes track equity prices, not crypto. See
#      docs/SYMBOL_CLASS_RESEARCH_2026_05_23.md (Class C).
#        - AVGO/QQQ/SKHYNIX/DRAM: were actively firing to the paid channel
#          (monitor-logs/signals_last100), blocked session 20b.
#        - CRCL/MU/INTC/CL/EWY: already QUIET-suppressed (not reaching
#          subscribers) but still scanned; blocked here so a regime shift
#          can't leak a dormant tokenized stock to the paid channel.
# Configurable via comma-separated env var; defaults cover the known junk pairs.
SCAN_SYMBOL_BLACKLIST: set = set(
    s for s in os.getenv(
        "SCAN_SYMBOL_BLACKLIST",
        "XAUTUSDT,PAXGUSDT,MMTUSDT,KOMAUSDT,STOUSDT,"
        "AVGOUSDT,QQQUSDT,SKHYNIXUSDT,DRAMUSDT,"
        "CRCLUSDT,MUUSDT,INTCUSDT,CLUSDT,EWYUSDT,"
        # Tokenised stocks / metals that re-entered via mover promotion
        # (2026-07-03 signal-book sweep) — scan-time mirror of the
        # selection-time _NON_CRYPTO_BLACKLIST additions in pair_manager.
        "SAMSUNGUSDT,HOODUSDT,COINUSDT,QCOMUSDT,PLTRUSDT,SNDKUSDT,"
        "RKLBUSDT,ASTSUSDT,AXTIUSDT,LITEUSDT,ARMUSDT,MRVLUSDT,XPTUSDT",
    ).split(",")
    if s
)

# ---------------------------------------------------------------------------
# Top-50 futures-only mode (PR1–PR5)
# ---------------------------------------------------------------------------
# When enabled, the engine restricts scanning, WS streams, and AI inference
# exclusively to the top-50 USDT-M futures pairs by 24h volume.  Spot pairs
# and all lower-ranked futures pairs are excluded.  This reduces API weight
# consumption and scan latency significantly.
TOP50_FUTURES_ONLY: bool = _safe_bool("TOP50_FUTURES_ONLY", "true")
# Number of top futures pairs to maintain in top-50 mode.
TOP50_FUTURES_COUNT: int = _safe_int("TOP50_FUTURES_COUNT", "75")
# Minimum seconds between consecutive top-50 refresh calls (rate-limiting
# guard to prevent excessive Binance REST weight consumption).
TOP50_UPDATE_INTERVAL_SECONDS: int = _safe_int("TOP50_UPDATE_INTERVAL_SECONDS", "3600")

# ---------------------------------------------------------------------------
# Tiered pair universe
# ---------------------------------------------------------------------------
# Tier 1 — Core: top pairs by 24h volume.  Full scan every cycle, all channels,
# WebSocket streams + order book depth.  Primary signal source.
TIER1_PAIR_COUNT: int = _safe_int("TIER1_PAIR_COUNT", "75")
# Tier 2 — Discovery: next tier by volume.  Scanned every N cycles, SWING +
# SPOT channels only (no SCALP), REST klines only (no WS, no order book).
TIER2_PAIR_COUNT: int = _safe_int("TIER2_PAIR_COUNT", "200")
TIER2_SCAN_EVERY_N_CYCLES: int = _safe_int("TIER2_SCAN_EVERY_N_CYCLES", "3")
# Tier 3 — Full Universe: all remaining USDT pairs.  Lightweight volume /
# momentum scan every N minutes.  Auto-promoted to Tier 2 on volume surges.
# Also supports cycle-based scheduling: Tier 3 is included in the main scan
# loop every TIER3_SCAN_EVERY_N_CYCLES cycles (default 6).
TIER3_SCAN_INTERVAL_MINUTES: int = _safe_int("TIER3_SCAN_INTERVAL_MINUTES", "30")
TIER3_SCAN_EVERY_N_CYCLES: int = _safe_int("TIER3_SCAN_EVERY_N_CYCLES", "6")
TIER3_VOLUME_SURGE_MULTIPLIER: float = _safe_float("TIER3_VOLUME_SURGE_MULTIPLIER", "3.0")
# Diagnostic: log per-stage wall-time (onchain, cross-exchange, SMC/indicator
# compute, predictive) summed across each scan cycle. Read-only telemetry to
# locate the dominant cost when scan latency exceeds the ~15s target. Default
# on; set false to silence once the bottleneck is identified.
SCAN_STAGE_TIMING_ENABLED: bool = _safe_bool("SCAN_STAGE_TIMING_ENABLED", "true")
# Worker-thread count for the scan executor. Default 2× cpu_count, capped at
# 20. Raise via .env once the SMC/indicator caches reduce baseline CPU load and
# more thread throughput is needed for cold-start pairs.
SCAN_EXECUTOR_WORKERS: int = _safe_int(
    "SCAN_EXECUTOR_WORKERS",
    str(min((os.cpu_count() or 4) * 2, 20)),
)

# ---------------------------------------------------------------------------
# Tiered scanning configuration
# ---------------------------------------------------------------------------
SCANNING_TIERS: Dict[str, Any] = {
    "TIER_1_CRITICAL": {
        "pairs": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"],
        "scan_interval_seconds": 5,
        "priority": "HIGH",
    },
    "TIER_2_FUTURES_TOP": {
        "count": 50,
        "scan_interval_seconds": 15,
        "priority": "MEDIUM",
    },
    "TIER_3_SPOT_BATCH": {
        "count": 200,
        "scan_interval_seconds": 60,
        "priority": "LOW",
        "batch_size": 25,
    },
}

#: Enable adaptive per-tier regime threshold adjustment.
ADAPTIVE_REGIME_ENABLED: bool = _safe_bool("ADAPTIVE_REGIME_ENABLED", "true")
# When enabled, pairs absent from the latest exchange response are pruned from
# the active universe (handles delistings and low-volume pair removal).
PAIR_PRUNE_ENABLED: bool = _safe_bool("PAIR_PRUNE_ENABLED", "true")

# ---------------------------------------------------------------------------
# Sweep detection tuning
# ---------------------------------------------------------------------------
# Scalp-optimised parameters: shorter lookback catches recent S/R levels
# relevant to 1m/5m timeframes; wider tolerance catches real institutional
# sweeps that reclaim $100-200 past the level on high-priced assets.
SMC_SCALP_LOOKBACK: int = _safe_int("SMC_SCALP_LOOKBACK", "20")
SMC_SCALP_TOLERANCE_PCT: float = _safe_float("SMC_SCALP_TOLERANCE_PCT", "0.15")
# Default (swing/spot) parameters — preserved for backward compatibility.
SMC_DEFAULT_LOOKBACK: int = _safe_int("SMC_DEFAULT_LOOKBACK", "50")
SMC_DEFAULT_TOLERANCE_PCT: float = _safe_float("SMC_DEFAULT_TOLERANCE_PCT", "0.05")


# ---------------------------------------------------------------------------
# Historical-data seeding – minimum candles per timeframe
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TimeframeSeed:
    interval: str
    limit: int


SEED_TIMEFRAMES: List[TimeframeSeed] = [
    TimeframeSeed("1m", 500),
    TimeframeSeed("5m", 500),
    TimeframeSeed("15m", 500),
    TimeframeSeed("1h", 500),
    TimeframeSeed("4h", 500),
    TimeframeSeed("1d", 500),
    # 1w added 2026-05-06 to seed cycle-level S/R levels into the LevelBook
    # (chartist-eye seeding-gap fix).  200 weekly candles ≈ ~3.8 years —
    # enough to capture every major cycle high / low for our universe.
    TimeframeSeed("1w", 200),
]
SEED_TICK_LIMIT: int = 1000  # BUG FIX: REST caps at 1000  # recent trades

# Candle counts for gem scanner daily/weekly seeding (~1 year lookback).
# These are read from env-vars so they can be tuned without code changes.
GEM_SEED_DAILY_CANDLES: int = _safe_int("GEM_SEED_DAILY_CANDLES", "365")
GEM_SEED_WEEKLY_CANDLES: int = _safe_int("GEM_SEED_WEEKLY_CANDLES", "52")

# Timeframes fetched specifically for the gem scanner — daily for 1-year
# lookback and weekly for macro ATH detection.  Kept separate from
# SEED_TIMEFRAMES so existing SCALP/SWING/SPOT seeding is unaffected.
GEM_SEED_TIMEFRAMES: List[TimeframeSeed] = [
    TimeframeSeed("1d", GEM_SEED_DAILY_CANDLES),
    TimeframeSeed("1w", GEM_SEED_WEEKLY_CANDLES),
]

# ---------------------------------------------------------------------------
# Channel-level risk profiles
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ChannelConfig:
    name: str
    emoji: str
    timeframes: List[str]
    sl_pct_range: tuple  # (min%, max%)
    tp_ratios: List[float]  # R-multiples
    trailing_atr_mult: float
    adx_min: float
    adx_max: float
    spread_max: float
    min_confidence: float
    min_volume: float = 1_000_000.0  # minimum 24h USD volume
    # DCA (Double Entry / Dollar-Cost Averaging) config
    dca_enabled: bool = False                  # Whether DCA is enabled for this channel
    dca_zone_range: tuple = (0.30, 0.70)       # DCA zone as fraction of SL distance
    dca_weight_1: float = 0.6                  # Position weight for Entry 1
    dca_weight_2: float = 0.4                  # Position weight for Entry 2
    dca_min_momentum: float = 0.2              # Minimum |momentum| for DCA validation
    min_signal_lifespan: int = 900             # Default minimum lifespan; overridden per-channel by callers


# ---------------------------------------------------------------------------
# Per-Pair Config Profiles
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PairProfile:
    """Per-pair threshold profile applied on top of global channel config."""
    tier: str                         # "MAJOR", "MIDCAP", "ALTCOIN"
    # Multipliers applied to global config values (1.0 = no change)
    atr_mult: float = 1.0             # Multiplier for ATR-based SL distance
    momentum_threshold_mult: float = 1.0   # Multiplier for momentum threshold
    spread_max_mult: float = 1.0      # Multiplier for max spread tolerance
    volume_min_mult: float = 1.0      # Multiplier for minimum volume
    rsi_ob_level: float = 70.0        # RSI overbought level
    rsi_os_level: float = 30.0        # RSI oversold level
    adx_min_mult: float = 1.0         # Multiplier for minimum ADX
    bb_touch_pct: float = 0.002       # BB-touch proximity (0.2% default)
    momentum_persist_candles: int = 2  # Required consecutive momentum candles
    kill_zone_hard_gate: bool = False  # Hard-reject signals outside kill zones
    # Extended per-pair enrichment fields (item 17)
    session_score: float = 1.0        # Per-pair session affinity score (0-2)
    liquidity_tier: int = 2           # 1=highest liquidity, 2=mid, 3=smallest
    avg_spread_bps: float = 3.0       # Average spread in basis points
    volatility_class: str = "medium"  # "low", "medium", "high"


# Tier profiles
PAIR_PROFILES: Dict[str, PairProfile] = {
    "MAJOR": PairProfile(
        tier="MAJOR",
        atr_mult=1.0,
        momentum_threshold_mult=0.8,   # BTC/ETH: lower threshold (tighter moves)
        spread_max_mult=0.5,           # Tighter spread requirement
        volume_min_mult=5.0,           # Higher absolute volume floor
        rsi_ob_level=75.0,
        rsi_os_level=25.0,
        adx_min_mult=0.9,
        bb_touch_pct=0.003,            # Slightly wider tolerance for majors
        momentum_persist_candles=2,
        kill_zone_hard_gate=False,
        liquidity_tier=1,
        avg_spread_bps=1.5,
        volatility_class="medium",
    ),
    "MIDCAP": PairProfile(
        tier="MIDCAP",
        atr_mult=1.1,
        momentum_threshold_mult=1.0,
        spread_max_mult=1.0,
        volume_min_mult=1.0,
        rsi_ob_level=70.0,
        rsi_os_level=30.0,
        adx_min_mult=1.0,
        bb_touch_pct=0.002,
        momentum_persist_candles=2,
        kill_zone_hard_gate=False,
        liquidity_tier=2,
        avg_spread_bps=3.0,
        volatility_class="medium",
    ),
    "ALTCOIN": PairProfile(
        tier="ALTCOIN",
        atr_mult=1.3,
        momentum_threshold_mult=2.0,   # High-vol pairs need larger momentum moves
        spread_max_mult=2.0,           # Wider spreads acceptable
        volume_min_mult=0.3,           # Lower volume floor (smaller markets)
        rsi_ob_level=65.0,
        rsi_os_level=35.0,
        adx_min_mult=1.1,
        bb_touch_pct=0.001,            # Tighter touch requirement
        momentum_persist_candles=3,    # Extra confirmation candles
        kill_zone_hard_gate=True,      # Hard-gate: only trade in kill zones
        liquidity_tier=3,
        avg_spread_bps=6.0,
        volatility_class="high",
    ),
}

# Static symbol → tier mapping (auto-classified for unlisted pairs)
PAIR_TIER_MAP: Dict[str, str] = {
    "BTCUSDT": "MAJOR",
    "ETHUSDT": "MAJOR",
    "BNBUSDT": "MIDCAP",
    "SOLUSDT": "MIDCAP",
    "LINKUSDT": "MIDCAP",
    "MATICUSDT": "MIDCAP",
    "AVAXUSDT": "MIDCAP",
    "DOTUSDT": "MIDCAP",
    "DOGEUSDT": "ALTCOIN",
    "SHIBUSDT": "ALTCOIN",
    "PEPEUSDT": "ALTCOIN",
}


# ---------------------------------------------------------------------------
# Symbol-specific PairProfile overrides  (Rec 1)
#
# Per-symbol overrides that layer ON TOP of the tier defaults.  Only the
# fields that differ from the tier baseline need to be specified; the rest
# are inherited from PAIR_PROFILES[tier].
# ---------------------------------------------------------------------------

PAIR_OVERRIDES: Dict[str, Dict[str, Any]] = {
    "BTCUSDT": {
        "momentum_threshold_mult": 0.6,   # BTC moves in tight bands
        "spread_max_mult": 0.4,           # Excellent liquidity
        "adx_min_mult": 1.1,              # ADX 28 is rare; require stronger trend
    },
    "ETHUSDT": {
        "momentum_threshold_mult": 0.9,   # More volatile momentum than BTC
        "adx_min_mult": 0.9,              # ETH trends earlier
    },
    "DOGEUSDT": {
        "momentum_threshold_mult": 1.6,   # Less noisy than PEPE
        "kill_zone_hard_gate": False,      # Decent Asian volume
        "momentum_persist_candles": 2,     # Faster momentum
    },
    "PEPEUSDT": {
        "momentum_threshold_mult": 2.5,   # Extreme noise
        "kill_zone_hard_gate": True,       # Needs concentrated liquidity
        "rsi_ob_level": 62.0,             # Extreme RSI levels more common
        "rsi_os_level": 38.0,
    },
    "SOLUSDT": {
        "adx_min_mult": 0.85,            # SOL trends decisively
        "momentum_threshold_mult": 0.9,
    },
    "SHIBUSDT": {
        "spread_max_mult": 2.5,           # Wider spreads typical
        "volume_min_mult": 0.2,           # Lower volume legitimate
    },
}


# Per-pair × regime confidence offsets  (Rec 4)
# Keys: (symbol_or_tier, regime_key) → offset
# Falls back to tier-level then to global _REGIME_THRESHOLD_OFFSETS.
PAIR_REGIME_OFFSETS: Dict[str, Dict[str, float]] = {
    "BTCUSDT": {
        "TRENDING": -5.0,     # BTC trends reliably
        "RANGING": +3.0,      # BTC ranges are clean
        "VOLATILE": +5.0,     # BTC volatile moves are institutional
        "QUIET": +1.0,
    },
    "ETHUSDT": {
        "TRENDING": -4.0,
        "RANGING": +4.0,
        "VOLATILE": +6.0,
        "QUIET": 0.0,
    },
    "DOGEUSDT": {
        "TRENDING": -2.0,     # Noisy trends
        "RANGING": +8.0,      # Choppy ranges
        "VOLATILE": +10.0,    # Retail chaos
        "QUIET": 0.0,
    },
    "PEPEUSDT": {
        "TRENDING": -1.0,
        "RANGING": +10.0,
        "VOLATILE": +12.0,    # PEPE volatility is retail noise
        "QUIET": +2.0,
    },
    "MAJOR": {
        "TRENDING": -4.0,
        "RANGING": +3.0,
        "VOLATILE": +5.0,
        "QUIET": 0.0,
    },
    "MIDCAP": {
        "TRENDING": -3.0,
        "RANGING": +5.0,
        "VOLATILE": +8.0,
        "QUIET": 0.0,
    },
    "ALTCOIN": {
        "TRENDING": -2.0,
        "RANGING": +7.0,
        "VOLATILE": +10.0,
        "QUIET": +1.0,
    },
}


# Per-pair session multiplier adjustments  (Rec 10)
# Adjustments added to the base session multiplier per tier.
PAIR_SESSION_ADJUSTMENTS: Dict[str, Dict[str, float]] = {
    "MAJOR": {
        "ASIAN_SESSION": +0.10,       # BTC/ETH have decent Asian volume
        "ASIAN_DEAD_ZONE": +0.05,
        "WEEKEND_DEAD_ZONE": +0.15,   # BTC trades 24/7
        "POST_NY_LULL": +0.05,
    },
    "MIDCAP": {},                      # No adjustment (baseline)
    "ALTCOIN": {
        "ASIAN_SESSION": -0.10,       # Very thin liquidity
        "ASIAN_DEAD_ZONE": -0.15,     # Almost no volume
        "WEEKEND_DEAD_ZONE": -0.05,   # Even lower liquidity
        "POST_NY_LULL": -0.10,
    },
}


CHANNEL_SCALP = ChannelConfig(
    name="360_SCALP",
    emoji="⚡",
    timeframes=["1m", "5m"],
    sl_pct_range=(0.50, 1.00),  # capped at 1.00%: 1.20% was 12% margin loss at 10×
    tp_ratios=[1.5, 2.5, 4.0],
    trailing_atr_mult=1.5,
    adx_min=int(os.getenv("ADX_MIN_SCALP", "20")),
    adx_max=100,
    spread_max=0.02,
    min_confidence=int(os.getenv("MIN_CONFIDENCE_SCALP", "65")),
    min_volume=5_000_000.0,
    dca_enabled=True,
    min_signal_lifespan=int(os.getenv("SCALP_MIN_LIFESPAN", "900")),
)

# ---------------------------------------------------------------------------
# New scalp trigger channel configs (Phase 3)
# ---------------------------------------------------------------------------

CHANNEL_SCALP_FVG = ChannelConfig(
    name="360_SCALP_FVG",
    emoji="⚡",
    timeframes=["5m", "15m"],
    sl_pct_range=(0.50, 1.00),  # capped at 1.00%: 1.20% was 12% margin loss at 10×
    tp_ratios=[1.5, 2.5, 3.0],
    trailing_atr_mult=1.5,
    adx_min=int(os.getenv("ADX_MIN_FVG", "18")),
    adx_max=100,
    spread_max=0.02,
    min_confidence=int(os.getenv("MIN_CONFIDENCE_FVG", "78")),
    min_volume=5_000_000.0,
    dca_enabled=True,
    min_signal_lifespan=int(os.getenv("SCALP_MIN_LIFESPAN", "900")),
)

CHANNEL_SCALP_CVD = ChannelConfig(
    name="360_SCALP_CVD",
    emoji="⚡",
    timeframes=["5m"],
    sl_pct_range=(0.50, 1.00),  # capped at 1.00%: 1.20% was 12% margin loss at 10×
    tp_ratios=[1.5, 2.5, 3.5],
    trailing_atr_mult=1.5,
    adx_min=15,
    adx_max=100,
    spread_max=0.02,
    min_confidence=75,
    min_volume=5_000_000.0,
    dca_enabled=True,
    min_signal_lifespan=int(os.getenv("SCALP_MIN_LIFESPAN", "900")),
)

CHANNEL_SCALP_VWAP = ChannelConfig(
    name="360_SCALP_VWAP",
    emoji="⚡",
    timeframes=["5m", "15m"],
    sl_pct_range=(0.50, 1.00),  # capped at 1.00%: 1.20% was 12% margin loss at 10×
    tp_ratios=[1.5, 2.5, 3.5],
    trailing_atr_mult=1.5,
    adx_min=0,
    adx_max=25,
    spread_max=0.02,
    min_confidence=75,
    min_volume=5_000_000.0,
    dca_enabled=True,
    min_signal_lifespan=int(os.getenv("SCALP_MIN_LIFESPAN", "900")),
)

CHANNEL_SCALP_DIVERGENCE = ChannelConfig(
    name="360_SCALP_DIVERGENCE",
    emoji="⚡",
    timeframes=["5m"],
    sl_pct_range=(0.50, 1.00),  # capped at 1.00%: 1.20% was 12% margin loss at 10×
    tp_ratios=[1.5, 2.5, 3.5],
    trailing_atr_mult=1.5,
    adx_min=15,
    adx_max=40,
    spread_max=0.02,
    min_confidence=int(os.getenv("MIN_CONFIDENCE_DIVERGENCE", "76")),
    min_volume=5_000_000.0,
    dca_enabled=True,
    min_signal_lifespan=int(os.getenv("SCALP_MIN_LIFESPAN", "900")),
)

CHANNEL_SCALP_SUPERTREND = ChannelConfig(
    name="360_SCALP_SUPERTREND",
    emoji="⚡",
    timeframes=["5m"],
    sl_pct_range=(0.50, 1.00),  # capped at 1.00%: 1.20% was 12% margin loss at 10×
    tp_ratios=[1.5, 2.5, 3.5],
    trailing_atr_mult=1.5,
    adx_min=15,
    adx_max=100,
    spread_max=0.02,
    min_confidence=75,
    min_volume=5_000_000.0,
    dca_enabled=True,
    min_signal_lifespan=int(os.getenv("SCALP_MIN_LIFESPAN", "900")),
)

CHANNEL_SCALP_ICHIMOKU = ChannelConfig(
    name="360_SCALP_ICHIMOKU",
    emoji="⚡",
    timeframes=["5m", "15m"],
    sl_pct_range=(0.50, 1.00),  # capped at 1.00%: 1.20% was 12% margin loss at 10×
    tp_ratios=[1.5, 2.5, 3.0],
    trailing_atr_mult=1.5,
    adx_min=15,
    adx_max=100,
    spread_max=0.02,
    min_confidence=75,
    min_volume=5_000_000.0,
    dca_enabled=True,
    min_signal_lifespan=int(os.getenv("SCALP_MIN_LIFESPAN", "900")),
)

CHANNEL_SCALP_ORDERBLOCK = ChannelConfig(
    name="360_SCALP_ORDERBLOCK",
    emoji="⚡",
    timeframes=["5m"],
    sl_pct_range=(0.50, 1.00),  # capped at 1.00%: 1.20% was 12% margin loss at 10×
    tp_ratios=[1.5, 2.5, 3.0],
    trailing_atr_mult=1.5,
    adx_min=0,
    adx_max=100,
    spread_max=0.02,
    min_confidence=int(os.getenv("MIN_CONFIDENCE_ORDERBLOCK", "78")),
    min_volume=5_000_000.0,
    dca_enabled=True,
    min_signal_lifespan=int(os.getenv("SCALP_MIN_LIFESPAN", "900")),
)

ALL_CHANNELS: List[ChannelConfig] = [
    CHANNEL_SCALP,
    CHANNEL_SCALP_FVG,
    CHANNEL_SCALP_CVD,
    CHANNEL_SCALP_VWAP,
    CHANNEL_SCALP_DIVERGENCE,
    CHANNEL_SCALP_SUPERTREND,
    CHANNEL_SCALP_ICHIMOKU,
    CHANNEL_SCALP_ORDERBLOCK,
]

# ---------------------------------------------------------------------------
# Channel enable/disable flags.
# Set to false to disable a channel without deleting any code.
# The channel's evaluate() method still exists and works — the scanner simply
# skips it. Flip back to true in .env to re-enable instantly.
# ---------------------------------------------------------------------------
CHANNEL_ENABLE_DEFAULTS: Dict[str, bool] = {
    "360_SCALP": True,
    "360_SCALP_FVG": False,
    "360_SCALP_ORDERBLOCK": False,
    # PR-5 first rollout step: divergence path enters controlled limited-live.
    # This remains narrow via channel rollout-state + pilot symbol guardrails.
    "360_SCALP_DIVERGENCE": True,
    "360_SCALP_CVD": False,
    "360_SCALP_VWAP": False,
    "360_SCALP_SUPERTREND": False,
    "360_SCALP_ICHIMOKU": False,
}

# Explicit radar-role governance by channel.
# True means: when runtime-disabled, this channel is allowed to participate in
# radar/watchlist discovery paths (not paid dispatch).
CHANNEL_RADAR_ROLE_DEFAULTS: Dict[str, bool] = {
    "360_SCALP": False,
    "360_SCALP_FVG": True,
    "360_SCALP_ORDERBLOCK": True,
    "360_SCALP_DIVERGENCE": True,
    "360_SCALP_CVD": False,
    "360_SCALP_VWAP": False,
    "360_SCALP_SUPERTREND": False,
    "360_SCALP_ICHIMOKU": False,
}

# Volatile contradiction-cleanup scope (PR-3).
# Only these channels bypass channel-level volatile pre-skip so that setup/family
# compatibility can decide downstream in _prepare_signal.
CHANNEL_VOLATILE_FAMILY_GOVERNED: frozenset[str] = frozenset({
    "360_SCALP",
    "360_SCALP_FVG",
    "360_SCALP_DIVERGENCE",
    "360_SCALP_ORDERBLOCK",
})

CHANNEL_SCALP_ENABLED:            bool = _safe_bool("CHANNEL_SCALP_ENABLED",            "true")
# PR-04/PR-05: Auxiliary channels are governed by explicit rollout states.
# Flags remain emergency operator overrides for rapid rollback/disable.
CHANNEL_SCALP_FVG_ENABLED:        bool = _safe_bool("CHANNEL_SCALP_FVG_ENABLED",        "false")
CHANNEL_SCALP_ORDERBLOCK_ENABLED: bool = _safe_bool("CHANNEL_SCALP_ORDERBLOCK_ENABLED", "false")
CHANNEL_SCALP_DIVERGENCE_ENABLED: bool = _safe_bool("CHANNEL_SCALP_DIVERGENCE_ENABLED", "true")
# Soft-disabled noisy channels — set env var to "true" to re-enable instantly
CHANNEL_SCALP_CVD_ENABLED:        bool = _safe_bool("CHANNEL_SCALP_CVD_ENABLED",        "false")
CHANNEL_SCALP_VWAP_ENABLED:       bool = _safe_bool("CHANNEL_SCALP_VWAP_ENABLED",       "false")
CHANNEL_SCALP_SUPERTREND_ENABLED: bool = _safe_bool("CHANNEL_SCALP_SUPERTREND_ENABLED", "false")
CHANNEL_SCALP_ICHIMOKU_ENABLED:   bool = _safe_bool("CHANNEL_SCALP_ICHIMOKU_ENABLED",   "false")

# Controlled rollout doctrine (PR-5):
# - disabled    : channel does not evaluate in live or radar paths.
# - radar_only  : observe-only; no paid/live dispatch.
# - limited_live: paid/live enabled only for pilot symbols (plus radar outside pilot).
# - full_live   : normal paid/live channel operation.
CHANNEL_ROLLOUT_STATES_ALLOWED: frozenset[str] = frozenset({
    "disabled",
    "radar_only",
    "limited_live",
    "full_live",
})
CHANNEL_ROLLOUT_STATE_DEFAULTS: Dict[str, str] = {
    "360_SCALP": _safe_choice(
        "CHANNEL_ROLLOUT_STATE_360_SCALP", "full_live", CHANNEL_ROLLOUT_STATES_ALLOWED
    ),
    "360_SCALP_FVG": _safe_choice(
        "CHANNEL_ROLLOUT_STATE_360_SCALP_FVG", "radar_only", CHANNEL_ROLLOUT_STATES_ALLOWED
    ),
    # radar_only still works when the CHANNEL_SCALP_ORDERBLOCK_ENABLED env var is false because
    # the runtime flag override is applied only to live rollout states.
    "360_SCALP_ORDERBLOCK": _safe_choice(
        "CHANNEL_ROLLOUT_STATE_360_SCALP_ORDERBLOCK", "radar_only", CHANNEL_ROLLOUT_STATES_ALLOWED
    ),
    # PR-5 first selective activation: narrow limited-live pilot.
    "360_SCALP_DIVERGENCE": _safe_choice(
        "CHANNEL_ROLLOUT_STATE_360_SCALP_DIVERGENCE", "limited_live", CHANNEL_ROLLOUT_STATES_ALLOWED
    ),
    "360_SCALP_CVD": _safe_choice(
        "CHANNEL_ROLLOUT_STATE_360_SCALP_CVD", "disabled", CHANNEL_ROLLOUT_STATES_ALLOWED
    ),
    "360_SCALP_VWAP": _safe_choice(
        "CHANNEL_ROLLOUT_STATE_360_SCALP_VWAP", "disabled", CHANNEL_ROLLOUT_STATES_ALLOWED
    ),
    "360_SCALP_SUPERTREND": _safe_choice(
        "CHANNEL_ROLLOUT_STATE_360_SCALP_SUPERTREND", "disabled", CHANNEL_ROLLOUT_STATES_ALLOWED
    ),
    "360_SCALP_ICHIMOKU": _safe_choice(
        "CHANNEL_ROLLOUT_STATE_360_SCALP_ICHIMOKU", "disabled", CHANNEL_ROLLOUT_STATES_ALLOWED
    ),
}

# Channel-specific pilot universe for limited-live rollouts.
# Empty set means rollback to observe-only behavior for that channel.
CHANNEL_LIMITED_LIVE_PILOT_SYMBOLS: Dict[str, frozenset[str]] = {
    "360_SCALP_DIVERGENCE": _safe_symbol_set(
        "CHANNEL_LIMITED_LIVE_PILOT_SYMBOLS_360_SCALP_DIVERGENCE",
        "BTCUSDT,ETHUSDT",
    ),
}
# PR-06: OPENING_RANGE_BREAKOUT disabled by default pending rebuild with true
# session-opening-range logic.  The current implementation uses the last 8 bars
# as a proxy — not an institutional-grade session-anchored range.  Code is
# preserved; set SCALP_ORB_ENABLED=true in .env to re-enable explicitly.
SCALP_ORB_ENABLED:                bool = _safe_bool("SCALP_ORB_ENABLED",                "false")

# ---------------------------------------------------------------------------
# Mapping from signal setup_class to the display header shown in Telegram.
# Every signal already has setup_class set in build_channel_signal().
# Subscribers see exactly what setup they are trading.
# ---------------------------------------------------------------------------
SIGNAL_TYPE_LABELS: Dict[str, str] = {
    "LIQUIDITY_SWEEP_REVERSAL":      "⚡ SWEEP REVERSAL",
    "WHALE_MOMENTUM":                "🐋 WHALE MOMENTUM",
    "FVG_RETEST":                    "⚡ FVG RETEST",
    "FVG_RETEST_HTF_CONFLUENCE":     "⚡ FVG RETEST ★ HTF CONFLUENCE",
    "CVD_DIVERGENCE":                "📉 CVD DIVERGENCE",
    "ORDERBLOCK_BOUNCE":             "🧱 ORDER BLOCK",
    "DIVERGENCE_REVERSAL":           "🔄 DIVERGENCE",
    "OBI_IMBALANCE":                 "📊 ORDER IMBALANCE",
    "SUPERTREND_SIGNAL":             "📈 SUPERTREND",
    "ICHIMOKU_SIGNAL":               "☁️ ICHIMOKU",
    "VWAP_EXTENSION":                "📏 VWAP EXTENSION",
    "MULTI_STRATEGY_CONFLUENCE":     "🌟 MULTI-STRATEGY",
    "VOLUME_SURGE_BREAKOUT":         "🚀 SURGE BREAKOUT",
    "BREAKDOWN_SHORT":               "📉 BREAKDOWN SHORT",
    "MOVER_TREND_PULLBACK":          "🚀 MOVER PULLBACK",
    "OPENING_RANGE_BREAKOUT":        "🕯️ OPENING RANGE BREAKOUT",
    "SR_FLIP_RETEST":                "🔄 S/R FLIP RETEST",
    "FUNDING_EXTREME_SIGNAL":        "💰 FUNDING EXTREME",
    "QUIET_COMPRESSION_BREAK":       "🔋 COMPRESSION BREAK",
    "DIVERGENCE_CONTINUATION":       "📊 DIVERGENCE CONTINUATION",
    "CONTINUATION_LIQUIDITY_SWEEP":  "🔁 CONTINUATION SWEEP",
    # S41 wiring audit: six emitted setups had no display label and fell back
    # to their raw enum names in subscriber-facing messages.
    "FAILED_AUCTION_RECLAIM":        "🔃 FAILED AUCTION RECLAIM",
    "LIQUIDATION_REVERSAL":          "💥 LIQUIDATION REVERSAL",
    "MA_CROSS_TREND_SHIFT":          "✂️ MA CROSS TREND SHIFT",
    "MOVER_AVWAP_SCALP":             "⚓ MOVER AVWAP SCALP",
    "POST_DISPLACEMENT_CONTINUATION": "➡️ DISPLACEMENT CONTINUATION",
    "TREND_PULLBACK_EMA":            "📈 TREND PULLBACK EMA",
}

CHANNEL_EMOJIS: Dict[str, str] = {
    "360_SCALP": "⚡",
}

def _build_channel_telegram_map() -> Dict[str, str]:
    """Build the channel → Telegram chat-ID mapping.

    All nine scalp strategy channels route to the single
    ``TELEGRAM_ACTIVE_CHANNEL_ID``.  Each message header already contains the
    specific signal type (e.g. RANGE FADE, FVG RETEST) so subscribers can
    distinguish setups within the one channel.
    """
    active = TELEGRAM_ACTIVE_CHANNEL_ID
    return {
        "360_SCALP":            active,
        "360_SCALP_FVG":        active,
        "360_SCALP_CVD":        active,
        "360_SCALP_VWAP":       active,
        "360_SCALP_DIVERGENCE": active,
        "360_SCALP_SUPERTREND": active,
        "360_SCALP_ICHIMOKU":   active,
        "360_SCALP_ORDERBLOCK": active,
    }


CHANNEL_TELEGRAM_MAP: Dict[str, str] = _build_channel_telegram_map()

# ---------------------------------------------------------------------------
# WebSocket settings
# ---------------------------------------------------------------------------
# Binance allows up to 1024 streams per connection; keep well below that.
# 200 streams/connection is a safe operational cap that still gives plenty of
# room before Binance's hard limit while allowing reasonable shard counts.
WS_MAX_STREAMS_PER_CONN: int = _safe_int("WS_MAX_STREAMS_PER_CONN", "200")
# Ping/pong latency threshold: if the RTT of a manual ping exceeds this value
# (in milliseconds) or a pong is not received within this window, the shard is
# force-closed so _run_connection can reconnect with fresh TCP state.
WS_PING_TIMEOUT_MS: int = _safe_int("WS_PING_TIMEOUT_MS", "5000")
WS_HEARTBEAT_INTERVAL: int = 30  # seconds (spot)
# Futures WS endpoint (fstream.binance.com) is higher-throughput and can delay
# PONG responses beyond 45 s during liquidation cascades (e.g. Extreme Fear
# events); 60 s gives Binance enough headroom before aiohttp auto-closes.
WS_HEARTBEAT_INTERVAL_FUTURES: int = _safe_int("WS_HEARTBEAT_INTERVAL_FUTURES", "60")
WS_RECONNECT_BASE_DELAY: float = 1.0
WS_RECONNECT_MAX_DELAY: float = 60.0
# Staleness multiplier: a connection is considered stale when
# (now - last_pong) >= heartbeat_interval * multiplier.
# Spot uses 10 (30 × 10 = 300 s).  Futures uses 15 (60 × 15 = 900 s) to
# provide extra headroom during liquidation cascades (Extreme Fear events)
# where Binance can delay PONG frames beyond the normal window.  The higher
# futures value also breaks the exact 600 s = WS_ALERT_COOLDOWN coincidence
# that was causing the repeating 10-minute drop/alert cycle.
WS_STALENESS_MULTIPLIER: int = 10  # spot
# Futures WS staleness multiplier — 2026-05-14 dropped from 15 to 5 after a 13h
# emission blackout where conn[0]/conn[1] sat at sec_since_last_msg≈12 min under
# a 900 s (60×15) threshold that never tripped before subscriber-visible silence
# became hours.  60 s × 5 = 300 s = 5 min: aggressive enough to catch the
# silent-but-pingable failure mode the May 12 diag first surfaced, while still
# leaving 2-3 min reconnect buffer for 200-stream resubscription cycles
# (per the WS_REST_FALLBACK_ALERT_GRACE_SEC docstring on live evidence).
WS_STALENESS_MULTIPLIER_FUTURES: int = _safe_int("WS_STALENESS_MULTIPLIER_FUTURES", "5")
# Admin alert dedup window (seconds) — alerts are throttled to at most one per
# 10-minute window per manager to avoid Telegram spam during prolonged outages.
WS_ALERT_COOLDOWN: int = _safe_int("WS_ALERT_COOLDOWN", "600")
# REST-fallback admin-alert grace period (seconds).  Transient WS drops that
# reconnect inside this window do not fire the "REST fallback activated" alert
# — only sustained outages do.  Originally tuned to 60s assuming "<2s clean
# reconnect" after the staleness-watchdog force-close.  Live evidence
# (2026-05-04) showed reconnects routinely take 60-180s on the futures stream
# (likely due to Binance re-subscription latency for the full kline-stream set),
# so the 60s grace was firing alerts on every 15-min staleness cycle even
# though signals continued flowing through REST fallback.  Bumped to 180s to
# filter out the recoverable mid-length outages while still alerting on
# genuinely prolonged degradations (>3 min reconnect = real problem).
WS_REST_FALLBACK_ALERT_GRACE_SEC: int = _safe_int("WS_REST_FALLBACK_ALERT_GRACE_SEC", "180")
# How many consecutive failed reconnection attempts before the aiohttp session
# is recycled (clears stale TCP connection pool and DNS cache).
WS_SESSION_RECYCLE_ATTEMPTS: int = _safe_int("WS_SESSION_RECYCLE_ATTEMPTS", "5")
# REST fallback — number of historical candles fetched in the one-time bulk
# backfill that warms indicator pipelines when a WS outage begins.
WS_FALLBACK_BULK_LIMIT: int = _safe_int("WS_FALLBACK_BULK_LIMIT", "50")
# Timeframes fetched in the bulk backfill (covers all channel strategies).
WS_FALLBACK_TIMEFRAMES: List[str] = ["1m", "5m", "15m", "1h", "4h"]
# Timeframes polled in the ongoing limit=1 REST loop (most frequently needed).
WS_FALLBACK_POLL_INTERVALS: List[str] = ["1m", "5m"]

# ---------------------------------------------------------------------------
# Trade monitoring
# ---------------------------------------------------------------------------
MONITOR_POLL_INTERVAL: float = 5.0  # seconds

# ---------------------------------------------------------------------------
# Telemetry
# ---------------------------------------------------------------------------
TELEMETRY_INTERVAL: float = 60.0  # seconds

# ---------------------------------------------------------------------------
# Anti-duplicate: per-channel cooldown after a signal completes (seconds)
# ---------------------------------------------------------------------------
CHANNEL_COOLDOWN_SECONDS: Dict[str, int] = {
    "360_SCALP": 60,
}

# ---------------------------------------------------------------------------
# Scanner-level signal cooldown: per-(symbol, channel) cooldown after a
# signal is *fired* (i.e. enqueued), to prevent re-evaluating the same setup
# within the cooldown window.
# ---------------------------------------------------------------------------
SIGNAL_SCAN_COOLDOWN_SECONDS: Dict[str, int] = {
    "360_SCALP": int(os.getenv("SCALP_SCAN_COOLDOWN", "600")),
}

# ---------------------------------------------------------------------------
# Circuit Breaker thresholds
# ---------------------------------------------------------------------------
CIRCUIT_BREAKER_MAX_CONSECUTIVE_SL: int = int(
    os.getenv("CIRCUIT_BREAKER_MAX_CONSECUTIVE_SL", "3")
)
CIRCUIT_BREAKER_MAX_HOURLY_SL: int = int(
    os.getenv("CIRCUIT_BREAKER_MAX_HOURLY_SL", "3")
)
CIRCUIT_BREAKER_MAX_DAILY_DRAWDOWN_PCT: float = float(
    os.getenv("CIRCUIT_BREAKER_MAX_DAILY_DRAWDOWN_PCT", "5.0")
)
CIRCUIT_BREAKER_COOLDOWN_SECONDS: int = int(
    os.getenv("CIRCUIT_BREAKER_COOLDOWN_SECONDS", "1800")
)

# Per-symbol consecutive SL tracking: after this many consecutive SL hits on
# the same symbol, that symbol is suppressed across all channels.
CIRCUIT_BREAKER_PER_SYMBOL_MAX_SL: int = int(
    os.getenv("CIRCUIT_BREAKER_PER_SYMBOL_MAX_SL", "3")
)
CIRCUIT_BREAKER_PER_SYMBOL_COOLDOWN_SECONDS: int = int(
    os.getenv("CIRCUIT_BREAKER_PER_SYMBOL_COOLDOWN_SECONDS", "3600")
)

# Startup grace period: the circuit breaker will not trip for this many
# seconds after the engine starts.  Cold-start cache warming produces
# elevated scan latency and temporary elevated SL rates that would
# otherwise trip the breaker immediately after every deploy.
CIRCUIT_BREAKER_STARTUP_GRACE_SECONDS: int = int(
    os.getenv("CIRCUIT_BREAKER_STARTUP_GRACE_SECONDS", "180")
)

# Bounded-recovery mode (DARK-FLAG, default OFF — owner activates after sign-off).
# When a trip is driven by the rolling daily-drawdown (or hourly-SL) gate, the
# breaker otherwise stays in ``recovery_pending`` until those losses age out of
# their rolling window (up to 24h). Because a halt stops all new outcomes, it
# starves its own recovery — a "900s cooldown" can become a multi-hour hold
# (2026-07-06 incident: 6h silent halt). When this is enabled, the breaker
# resumes on cooldown expiry with a fresh monitoring window, so the halt is a
# predictable cooldown-length pause. Tradeoff: it "forgets" the drawdown sooner
# (less conservative) — hence default OFF and owner-gated activation.
CIRCUIT_BREAKER_RESUME_AFTER_COOLDOWN: bool = _safe_bool(
    "CIRCUIT_BREAKER_RESUME_AFTER_COOLDOWN", "false"
)

# ---------------------------------------------------------------------------
# Thesis-based cooldown: after an SL hit, suppress the same (symbol, channel,
# direction, setup_class) tuple for a much longer period.
# ---------------------------------------------------------------------------
THESIS_COOLDOWN_AFTER_SL_SECONDS: Dict[str, int] = {
    "360_SCALP": int(os.getenv("THESIS_COOLDOWN_SCALP", "3600")),       # 1 hour
}

# ---------------------------------------------------------------------------
# Lifecycle-aware dispatch cooldown extensions (per (symbol, setup_class,
# direction)).  Owner-flagged 2026-05-09: 4 identical DOGEUSDT SR_FLIP_RETEST
# SHORT signals dispatched in 7h, all EXPIRED — same level, same geometry, no
# learning between dispatches.  Root cause: the existing 30-min dispatch
# cooldown elapsed mid-trade (max scalp hold = 1h), so by the time the signal
# expired there was nothing to prevent the next scan from emitting the same
# setup on the same level.
#
# Fix: on each non-TP lifecycle outcome, extend the dispatch cooldown so the
# next emission is meaningfully delayed — proportional to how strongly the
# market has rejected the thesis.
#
# - EXPIRED: 2h.  Hold timed out without TP / SL / INVAL — the level didn't
#   resolve; give it time to redevelop or break.
# - SL_HIT: 1h.  Thesis explicitly proven wrong; let the level reset.
# - INVALIDATED: 30 min.  Engine killed the signal before the market did —
#   softer; the level may still matter if regime / structure shifts.
# ---------------------------------------------------------------------------
LIFECYCLE_COOLDOWN_EXPIRED_SEC: int = _safe_int(
    "LIFECYCLE_COOLDOWN_EXPIRED_SEC", "7200"
)
LIFECYCLE_COOLDOWN_SL_SEC: int = _safe_int(
    "LIFECYCLE_COOLDOWN_SL_SEC", "3600"
)
LIFECYCLE_COOLDOWN_INVALIDATION_SEC: int = _safe_int(
    "LIFECYCLE_COOLDOWN_INVALIDATION_SEC", "1800"
)

# ---------------------------------------------------------------------------
# Performance Tracker persistence path
# ---------------------------------------------------------------------------
PERFORMANCE_TRACKER_PATH: str = os.getenv(
    "PERFORMANCE_TRACKER_PATH", "data/signal_performance.json"
)

# ---------------------------------------------------------------------------
# Max concurrent signals per channel.
#
# SCALP: capped for capital protection (leveraged trades).
# ---------------------------------------------------------------------------
MAX_CONCURRENT_SIGNALS_PER_CHANNEL: Dict[str, int] = {
    "360_SCALP":            int(os.getenv("MAX_SCALP_SIGNALS", "5")),
    "360_SCALP_FVG":        int(os.getenv("MAX_SCALP_FVG_SIGNALS", "3")),
    "360_SCALP_CVD":        int(os.getenv("MAX_SCALP_CVD_SIGNALS", "3")),
    "360_SCALP_VWAP":       int(os.getenv("MAX_SCALP_VWAP_SIGNALS", "3")),
    "360_SCALP_DIVERGENCE": int(os.getenv("MAX_SCALP_DIV_SIGNALS", "3")),
    "360_SCALP_SUPERTREND": int(os.getenv("MAX_SCALP_STR_SIGNALS", "3")),
    "360_SCALP_ICHIMOKU":   int(os.getenv("MAX_SCALP_ICH_SIGNALS", "3")),
    "360_SCALP_ORDERBLOCK": int(os.getenv("MAX_SCALP_ORB_SIGNALS", "3")),
}

# Global same-direction cap (Correlation Throttle).
#
# Top-75 USDT-M futures pairs are 0.85-0.95 correlated to BTC.  When BTC
# dumps, every LONG alt SL fires simultaneously — 5 concurrent LONGs means
# 5 simultaneous full-SL losses on a single BTC move.  This cap limits the
# blast radius to MAX_SAME_DIRECTION_GLOBAL open positions in the same
# direction at any moment, globally across all channels and symbols.
#
# Default 3: empirically one BTC-direction move at 2-5× leverage hits at
# most ~3 of our pairs before the dump exhausts.  Env-overridable per B8
# so the operator can widen on low-volatility days without a redeploy.
MAX_SAME_DIRECTION_GLOBAL: int = int(os.getenv("MAX_SAME_DIRECTION_GLOBAL", "3"))

# ---------------------------------------------------------------------------
# Regime Kill Switch — BTC whipsaw detection
# ---------------------------------------------------------------------------
# Detailed documentation in src/regime_kill_switch.py.  These constants are
# referenced here for documentation/discoverability; the authoritative values
# live in the module-level env reads in regime_kill_switch.py (B8 compliant).
#
# REGIME_KILL_ENABLED            — master on/off (env: REGIME_KILL_ENABLED)
# REGIME_KILL_LOOKBACK           — 15m candles to examine (env: REGIME_KILL_LOOKBACK, default 16 = 4h)
# REGIME_KILL_EFFICIENCY_MIN     — efficiency below which BTC is whipsaw (env: REGIME_KILL_EFFICIENCY_MIN, default 0.20)
# REGIME_KILL_MIN_RANGE_PCT      — min BTC range % for gate to activate (env: REGIME_KILL_MIN_RANGE_PCT, default 1.5%)
# REGIME_KILL_EXEMPT_SETUPS      — tape-driven setups that bypass the gate (env: REGIME_KILL_EXEMPT_SETUPS)

# ---------------------------------------------------------------------------
# Anti-noise: minimum signal lifespan before SL/TP checks are applied (secs)
# ---------------------------------------------------------------------------
MIN_SIGNAL_LIFESPAN_SECONDS: Dict[str, int] = {
    "360_SCALP":            int(os.getenv("MIN_LIFESPAN_SCALP",      "30")),
    "360_SCALP_FVG":        int(os.getenv("MIN_LIFESPAN_SCALP_FVG",  "30")),
    "360_SCALP_CVD":        int(os.getenv("MIN_LIFESPAN_SCALP_CVD",  "30")),
    "360_SCALP_VWAP":       int(os.getenv("MIN_LIFESPAN_SCALP_VWAP",  "30")),
    "360_SCALP_DIVERGENCE": int(os.getenv("MIN_LIFESPAN_SCALP_DIV",  "30")),
    "360_SCALP_SUPERTREND": int(os.getenv("MIN_LIFESPAN_SCALP_STR",  "30")),
    "360_SCALP_ICHIMOKU":   int(os.getenv("MIN_LIFESPAN_SCALP_ICH",  "30")),
    "360_SCALP_ORDERBLOCK": int(os.getenv("MIN_LIFESPAN_SCALP_ORB",  "30")),
}

# ---------------------------------------------------------------------------
# QUIET regime scalp signal quality gates
# ---------------------------------------------------------------------------

#: Minimum confidence score for scalp signals to pass in QUIET regime.
#: Acts as a hard floor — only top-tier signals proceed when the market is
#: compressed.  Configurable via the QUIET_SCALP_MIN_CONFIDENCE env var.
QUIET_SCALP_MIN_CONFIDENCE: float = float(
    os.getenv("QUIET_SCALP_MIN_CONFIDENCE", "65.0")
)

#: Volume multiplier required for scalp entries in QUIET regime.
#: Scalp signals in low-volatility markets are only accepted when current
#: volume is at least this multiple of the rolling average, ensuring signals
#: fire on genuine micro-breakouts rather than random noise.
#: This constant is exported for use by volume-aware gate logic in the
#: scalp channel evaluation pipeline.  The `_compute_base_confidence`
#: path reads this value when checking volume-spike conditions in QUIET.
QUIET_SCALP_VOLUME_MULTIPLIER: float = float(
    os.getenv("QUIET_SCALP_VOLUME_MULTIPLIER", "2.5")
)

#: Confidence penalty applied to SCALP signals in QUIET regime.
REGIME_QUIET_PENALTY: float = _safe_float("REGIME_QUIET_PENALTY", "8.0")

#: Confidence penalty applied to SCALP signals in RANGING regime with ADX below threshold.
REGIME_RANGING_PENALTY: float = _safe_float("REGIME_RANGING_PENALTY", "5.0")

#: ADX threshold below which SCALP signals receive a soft penalty in RANGING.
RANGING_ADX_SUPPRESS_THRESHOLD: float = float(
    os.getenv("RANGING_ADX_SUPPRESS_THRESHOLD", "12.0")
)

# ---------------------------------------------------------------------------
# Per-channel pair quality thresholds (overridable via env vars)
# ---------------------------------------------------------------------------
PAIR_QUALITY_THRESHOLD_SCALP: float = _safe_float("PAIR_QUALITY_THRESHOLD_SCALP", "58.0")

# ---------------------------------------------------------------------------
# How long a signal setup remains actionable (minutes).  After this window
# users should NOT enter the trade even if price is still in zone.
# ---------------------------------------------------------------------------
SIGNAL_VALID_FOR_MINUTES: Dict[str, int] = {
    "360_SCALP":            int(os.getenv("SIGNAL_VALID_SCALP",  "15")),
    "360_SCALP_FVG":        int(os.getenv("SIGNAL_VALID_SCALP",  "15")),
    "360_SCALP_CVD":        int(os.getenv("SIGNAL_VALID_SCALP",  "15")),
    "360_SCALP_VWAP":       int(os.getenv("SIGNAL_VALID_SCALP",  "15")),
    "360_SCALP_DIVERGENCE": int(os.getenv("SIGNAL_VALID_SCALP",  "15")),
    "360_SCALP_SUPERTREND": int(os.getenv("SIGNAL_VALID_SCALP",  "15")),
    "360_SCALP_ICHIMOKU":   int(os.getenv("SIGNAL_VALID_SCALP",  "15")),
    "360_SCALP_ORDERBLOCK": int(os.getenv("SIGNAL_VALID_SCALP",  "15")),
}

# ---------------------------------------------------------------------------
# Maximum hold duration per channel (seconds).  Signals older than this
# are auto-closed at current market price to free up concurrent-signal slots.
# ---------------------------------------------------------------------------
MAX_SIGNAL_HOLD_SECONDS: Dict[str, int] = {
    "360_SCALP": int(os.getenv("MAX_SCALP_HOLD", "3600")),       # 1 hour
}

# Time-based signal-expiry backstop. When False (default — owner decision
# 2026-06-26), the MAX_SIGNAL_HOLD_SECONDS max-hold force-close is DISABLED:
# signals run to TP or SL only, never expiring mid-move (the data showed
# signals expiring at small +MFE, surrendering the move). This env is the
# BOOT DEFAULT / fallback — the live value is toggled from the ops control
# plane and persisted on the kill-switch doc (signal_expiry_enabled field),
# read with a 5s cache so the monitor poll never hits Firestore per-signal.
# NB: the 2h auto-trade reconciler stale-close safety net is unaffected —
# that backstop stays regardless of this flag.
SIGNAL_EXPIRY_ENABLED: bool = _safe_bool("SIGNAL_EXPIRY_ENABLED", "false")

# Fill-window enforcement (S41 wiring audit).  The signal card advertises
# "valid for N minutes" (SIGNAL_VALID_FOR_MINUTES / sig.valid_for_minutes) but
# nothing enforced it — the engine/paper book could accept a limit fill up to
# the 1h max-hold on a setup subscribers were told to abandon at minute 15,
# diverging the book from the subscriber experience AND entering on a stale
# thesis.  When ON (default), an unfilled limit signal finalises as
# EXPIRED_NO_FILL the moment its advertised validity lapses.
ENTRY_FILL_WINDOW_ENFORCED: bool = _safe_bool("ENTRY_FILL_WINDOW_ENFORCED", "true")

# FSM LIMIT-at-zone + TTL entry (S41, docs/FSM_LIMIT_ENTRY_DESIGN.md).
# Owner-approved direction 2026-07-03 ("LIMIT at zone + TTL"); ships DARK.
# While false, every real dispatch logs "[SHADOW] FSM_LIMIT_ENTRY" with the
# would-be order mode (in_zone / would_rest / market_semantics) so activation
# is decided on measured dispatch data.  The full PENDING_ENTRY machinery
# (limit placement, SL-first fill handling, TTL sweep) activates with this
# flag; until then entries remain MARKET-at-dispatch.
FSM_LIMIT_ENTRY_ENABLED: bool = _safe_bool("FSM_LIMIT_ENTRY_ENABLED", "false")
FSM_ENTRY_TTL_FALLBACK_MIN: int = _safe_int("FSM_ENTRY_TTL_FALLBACK_MIN", "15")

# ---------------------------------------------------------------------------
# Concurrency cap – DEPRECATED: replaced by per-channel cap above.
# Kept for backwards-compatibility with any external tooling that imports it.
# ---------------------------------------------------------------------------
MAX_CONCURRENT_SIGNALS: int = 5

# ---------------------------------------------------------------------------
# Signal invalidation – minimum age before market-structure checks apply (secs)
# ---------------------------------------------------------------------------
INVALIDATION_MIN_AGE_SECONDS: Dict[str, int] = {
    "360_SCALP": 120,       # 120s: enough for entry candle to close; 600s was masking real fails
    # Per-setup overrides (key format: "{channel}::{setup_class}").
    # Reversal and flip-structure setups need extra patience before the
    # momentum/regime gates are allowed to invalidate: truth-report window
    # shows LSR=16/147 PREMATURE and SR_FLIP=17/175 PREMATURE — both setups
    # were killing correct-direction trades during normal post-entry reversal
    # dynamics that look like momentum loss on 1m but resolve within 2-4 min.
    "360_SCALP::LIQUIDITY_SWEEP_REVERSAL": int(os.getenv("INVALIDATION_MIN_AGE_LSR", "300")),
    "360_SCALP::SR_FLIP_RETEST":           int(os.getenv("INVALIDATION_MIN_AGE_SR_FLIP", "240")),
}

# Momentum threshold below which a signal is considered to have lost its thesis.
# Per-channel to account for different timeframe noise levels.
# SCALP uses 1m/5m candles which have rapid momentum oscillation — use a lower threshold.
INVALIDATION_MOMENTUM_THRESHOLD: Dict[str, float] = {
    "360_SCALP": float(os.getenv("INVALIDATION_MOMENTUM_THRESHOLD_SCALP", "0.10")),
}

# Micro-cap (entry < $0.001) momentum-threshold multiplier.
#
# History: sub-$0.001 coins (1000PEPE, CHIP, JCT, PLAY, HMSTR …) had their
# momentum kill threshold multiplied by 0.1 — a 10× *tighter* threshold — on
# the theory that cheap coins are noisier.  But `momentum` here is
# `_compute_momentum(closes, 3)`, a scale-invariant *percentage* rate of
# change: a 0.84 reading is an 84% move whether the coin trades at 0.0005 or
# 50.0.  The 10× tightening had no sound basis and made micro-caps far too
# easy to kill on noise (e.g. `momentum=0.101 > 0.010` killed a signal that
# would have cleanly passed the normal 0.10 threshold).  Invalidations audit
# (2026-06-15): micro-cap pairs dominated the PREMATURE momentum kills.
#
# Default 1.0 = micro-caps use the same threshold as every other pair (bug
# removed).  Set to 0.1 to restore the legacy 10×-tighter behaviour.  Env-
# overridable per B8; reversible without a code change.
INVALIDATION_MOMENTUM_MICROCAP_MULT: float = float(
    os.getenv("INVALIDATION_MOMENTUM_MICROCAP_MULT", "1.0")
)

# ---------------------------------------------------------------------------
# RANGING low-ATR loser-setup suppression (2026-06-15 — ships dark).
#
# Live last-100 audit (RANGING = 67% of volume, −7.22% of the −8.7% total):
#   SR_FLIP_RETEST            45 sigs  −4.36%  (avg win +0.25 vs avg loss −0.38)
#   LIQUIDITY_SWEEP_REVERSAL  20 sigs  −3.77%  (avg win +0.47 vs avg loss −0.73)
#   FAILED_AUCTION_RECLAIM    24 sigs  +0.71%  (67% win)   ← leave alone
#   DIVERGENCE_CONTINUATION    5 sigs  +0.42%  (60% win)   ← leave alone
#
# SR_FLIP (Structure) and LSR (Reversal) families are deliberately ALLOWED in
# low-ADX ranging today (they are not in _SCALP_RANGING_LOW_ADX_BLOCKED_FAMILIES),
# so they fire repeatedly into dead chop at ~1:2 win:loss.  This gate suppresses
# ONLY those two setups, and only when the range is also low-ATR (the deadest
# chop where mean-reversion scalping has no edge net of fees).
#
# Ships dark (flag false) with [SHADOW] telemetry so the suppressed volume and
# its would-be PnL are measurable before activation.  Paid-channel routing
# change — owner sign-off required to set
# RANGING_LOW_ATR_LOSER_SUPPRESS_ENABLED=true on the VPS.
RANGING_LOW_ATR_LOSER_SUPPRESS_ENABLED: bool = _safe_bool(
    "RANGING_LOW_ATR_LOSER_SUPPRESS_ENABLED", "false"
)
RANGING_LOW_ATR_SUPPRESS_PCTILE: float = _safe_float(
    "RANGING_LOW_ATR_SUPPRESS_PCTILE", "25.0"
)
RANGING_LOW_ATR_SUPPRESS_SETUPS: frozenset = frozenset(
    s.strip()
    for s in os.getenv(
        "RANGING_LOW_ATR_SUPPRESS_SETUPS",
        "SR_FLIP_RETEST,LIQUIDITY_SWEEP_REVERSAL",
    ).split(",")
    if s.strip()
)

# Number of *consecutive* below-threshold momentum readings required before a
# signal is invalidated for momentum loss.  A single weak reading is common on
# 1m/5m candles (price pauses before continuation) — requiring two consecutive
# readings reduces false kills while still catching genuine exhaustion.
INVALIDATION_CONSECUTIVE_THRESHOLD: Dict[str, int] = {
    "360_SCALP": int(os.getenv("INVALIDATION_CONSECUTIVE_THRESHOLD_SCALP", "2")),
    # SR_FLIP grace (A — ships dark).  Truth-report: 18/91 SR_FLIP kills were
    # PREMATURE (19.8%) vs 14.5% baseline.  Requiring one extra consecutive
    # bad-momentum reading (3 instead of 2 = +15s at 15s scan cycle) before
    # killing a SR_FLIP signal cuts the premature rate toward baseline without
    # touching the 68 PROTECTIVE saves.  Default 2 = unchanged; set to 3 when
    # SR_FLIP_MOMENTUM_GRACE_ENABLED is flipped on the VPS.
    "360_SCALP::SR_FLIP_RETEST": int(os.getenv("SR_FLIP_CONSECUTIVE_REQUIRED", "2")),
}

# Dark flag — activates the SR_FLIP momentum grace (change A).
# Ships false.  Read shadow telemetry counts via:
#   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "[SHADOW] SR_FLIP_GRACE_WOULD_DELAY"
# Enable by setting SR_FLIP_CONSECUTIVE_REQUIRED=3 on the VPS (no separate flag needed
# — shadow fires whenever the per-setup count > channel default, even before activation).
SR_FLIP_MOMENTUM_GRACE_ENABLED: bool = _safe_bool("SR_FLIP_MOMENTUM_GRACE_ENABLED", "false")

# SR_FLIP long-side enable (owner directive 2026-06-29, stopgap). Profit-Lab on
# 85 closed SR_FLIP signals: SHORT nets +5.1% (52% win) but LONG nets −21.8%
# (19% win) — the long side is the path's entire drag and loses in every regime
# (9% win even in TRENDING_UP). Disabled by default until the long-entry thesis
# is repaired; flip true to re-enable. This is a tourniquet, not a fix.
SR_FLIP_LONG_ENABLED: bool = _safe_bool("SR_FLIP_LONG_ENABLED", "false")

# SR_FLIP long V2 — the thesis repair (S40, issue #674).  Diagnosis: the code
# is long/short symmetric; the LONG side loses because a break ABOVE
# resistance in crypto is disproportionately a BULL TRAP — breakout-chasing
# longs get flushed exactly at the retest the setup buys.  V1 confirmed a
# flip on pure price (one break-and-close), which cannot tell acceptance
# from a trap.  V2 demands trap-discriminating evidence before any LONG:
#   1. Volume-backed break — the breakout candle's volume must be at least
#      SR_FLIP_LONG_BREAK_VOL_MULT × the mean of the prior 20 candles.
#      Genuine acceptance prints real volume; traps break thin.
#   2. Acceptance hold — at least SR_FLIP_LONG_MIN_HOLD_CLOSES closed 5m
#      candles above the level between break and retest (the break close
#      counts).  A single poke above the level is not a flip.
#   3. Whipsaw guard — if BOTH a long and a short flip confirm inside the
#      same 8-candle window the structure is chop, not a flip: reject
#      (V1 silently resolved these LONG — long had if-priority).
#   4. Macro protection — SR_FLIP_RETEST joins CT_LONG_MACRO_GATE_SETUPS,
#      so re-enabled longs are suppressed while BTC weekly / coin daily
#      reads DOWN (the steamroll case), auto-restoring on the turn.
# While SR_FLIP_LONG_ENABLED stays false, V2-passing longs emit
# "[SHADOW] SR_FLIP_LONG_V2_WOULD_FIRE" so the candidate rate and quality
# are measurable before re-enable (owner sign-off on the shadow window).
SR_FLIP_LONG_BREAK_VOL_MULT: float = _safe_float("SR_FLIP_LONG_BREAK_VOL_MULT", "1.5")
SR_FLIP_LONG_MIN_HOLD_CLOSES: int = _safe_int("SR_FLIP_LONG_MIN_HOLD_CLOSES", "2")

# ---------------------------------------------------------------------------
# SR_FLIP pre-TP R-scaling (change B — ships dark).
#
# Problem: SR_FLIP's structural SL can be 1–2.5% wide (1×ATR minimum).
# The ATR-adaptive pre-TP threshold averages 0.503% raw (truth-report).
# On a 2.5% SL that's only 0.20R — the banked half captures minimal reward
# relative to the risk.  R-scaling floors the threshold at
# SL_dist_pct × SR_FLIP_PRETP_R_FACTOR so wide-SL signals don't bank at 0.2R.
#
# Example: SL=2.5%, factor=0.35 → threshold = max(0.503%, 0.875%) = 0.875%
# Example: SL=0.8%, factor=0.35 → threshold = max(0.503%, 0.28%) = 0.503% (unchanged)
#
# Shadow telemetry fires when scaling is binding but flag is OFF:
#   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "[SHADOW] SR_FLIP_RSCALE_WOULD_RAISE"
SR_FLIP_PRETP_R_SCALING_ENABLED: bool = _safe_bool("SR_FLIP_PRETP_R_SCALING_ENABLED", "false")
SR_FLIP_PRETP_R_FACTOR: float = _safe_float("SR_FLIP_PRETP_R_FACTOR", "0.35")

# ---------------------------------------------------------------------------
# LIQUIDITY_SWEEP_REVERSAL geometry rebuild (2026-06-15 — ships dark).
#
# Live last-100: LSR is the worst R:R — avg win +0.47 vs avg loss −0.73
# (−3.77% over 20 sigs).  Two independent, separately-flagged levers:
#
# (1) Win-side — pre-TP R-scaling (mirror of SR_FLIP change B).  Floors the
#     pre-TP threshold at SL_dist_pct × LSR_PRETP_R_FACTOR so surviving LSR
#     wins bank a real R-multiple instead of a +0.47 nibble.  Does NOT touch
#     the stop.  Shadow: [SHADOW] LSR_RSCALE_WOULD_RAISE.
#
# (2) Loss-side — tighten the max-SL cap.  LSR is in
#     STRUCTURAL_SLTP_PROTECTED_SETUPS (reject-not-compress), so lowering the
#     cap does NOT move the stop into the post-sweep wick zone — it DROPS the
#     LSRs whose structural sweep-stop is wider than the cap, trimming the
#     wide-stop tail that produces the −0.73 losses.  Shadow:
#     [SHADOW] LSR_SL_TIGHTEN_WOULD_DROP.
#
# Both ship dark.  Geometry / Position-FSM change — owner sign-off required to
# enable either flag.  Tunable per B8.
LSR_PRETP_R_SCALING_ENABLED: bool = _safe_bool("LSR_PRETP_R_SCALING_ENABLED", "false")
LSR_PRETP_R_FACTOR: float = _safe_float("LSR_PRETP_R_FACTOR", "0.35")
LSR_SL_TIGHTEN_ENABLED: bool = _safe_bool("LSR_SL_TIGHTEN_ENABLED", "false")
LSR_MAX_SL_PCT_TIGHT: float = _safe_float("LSR_MAX_SL_PCT_TIGHT", "1.5")

# Adverse-excursion invalidation (2026-05-20 — truth-report follow-up).
# Catches the full-SL pattern that momentum_loss / regime_shift /
# ema_crossover all miss: price grinding against the position from
# entry → SL with momentum reading inside the noise band and the
# regime/EMA structure intact the whole way down.
#
# Rule fires when price has moved against entry by this fraction of
# the SL distance AND momentum is not strongly confirming.  Default
# 0.70 saves ~30% of the SL distance per kill (≈ 2.4% on margin at
# 10×).  Counter-cases: a single deep wick that reverses immediately
# can trip this — minimum-age gate (300s) + momentum-not-confirming
# requirement together suppress those.
#
# Env-overridable per B8.  If the next truth-report window shows
# > 25% PREMATURE classification on this rule, raise to 0.80 or
# disable via setting to 1.0 (no signal can be that far adverse
# without already hitting SL).
INVALIDATION_ADVERSE_EXCURSION_FRACTION: float = float(
    os.getenv("INVALIDATION_ADVERSE_EXCURSION_FRACTION", "0.55")
)

# Per-setup adverse-excursion fraction overrides.
#
# SR_FLIP_RETEST (2.5% SL) and LIQUIDITY_SWEEP_REVERSAL (2.0% SL) have wide
# structural stops by design.  At the global 0.55 fraction the early-exit gate
# wouldn't fire until 1.375% adverse (2.5% × 0.55) — too late to limit damage.
#
# At 0.40 fraction:
#   SR_FLIP  exits at 2.5% × 0.40 = 1.0% adverse (if momentum not confirming)
#   LSR      exits at 2.0% × 0.40 = 0.8% adverse (if momentum not confirming)
#
# This matches the effective loss cap that PR #513's artificial SL compression
# was targeting, without placing the stop inside the structural zone.  When
# momentum IS confirming the signal still runs — the gate is skipped.
INVALIDATION_ADVERSE_EXCURSION_FRACTION_BY_SETUP: Dict[str, float] = {
    "360_SCALP::SR_FLIP_RETEST": float(
        os.getenv("INVALIDATION_ADV_EXC_SR_FLIP", "0.40")
    ),
    "360_SCALP::LIQUIDITY_SWEEP_REVERSAL": float(
        os.getenv("INVALIDATION_ADV_EXC_LSR", "0.40")
    ),
}

# Minimum age gate for adverse_excursion.  Defaults to match the
# 360_SCALP function-level INVALIDATION_MIN_AGE_SECONDS gate (600s)
# so this rule cannot fire any earlier than the engine's baseline
# scalp invalidation grace period.  Defense-in-depth — leaving the
# explicit per-rule gate in case the function-level gate is later
# loosened, or to allow tighter per-rule tuning via env without
# affecting other rules.
INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC: int = int(
    os.getenv("INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_SEC", "120")
)

# Per-setup minimum age for adverse excursion — deliberately SHORTER than
# the corresponding INVALIDATION_MIN_AGE_SECONDS entry so that fast-moving
# losing signals (e.g. SR_FLIP hitting SL in < 4 min) are caught before the
# main patience gate opens.  Regime/EMA/momentum checks still sit behind the
# full patience window; adverse excursion is purely price-derived and safe to
# fire earlier.
#
# SR_FLIP 90s  — main patience 240s; early window catches 90–240s losers
# LSR     120s — main patience 300s; early window catches 120–300s losers
#
# Env-overridable per B8.
INVALIDATION_ADVERSE_EXCURSION_MIN_AGE_BY_SETUP: Dict[str, int] = {
    "360_SCALP::SR_FLIP_RETEST": int(os.getenv("INVALIDATION_ADV_EXC_AGE_SR_FLIP", "90")),
    "360_SCALP::LIQUIDITY_SWEEP_REVERSAL": int(os.getenv("INVALIDATION_ADV_EXC_AGE_LSR", "120")),
}

# ---------------------------------------------------------------------------
# BTC-correlation invalidation overlay (research session 19, 2026-06-05).
#
# Doctrine: alts are 0.65–0.90 BTC-correlated.  The existing BTC direction
# gate (``src.btc_direction.check_btc_direction_gate``) only fires at signal
# BIRTH — a soft entry penalty.  It does NOT watch BTC during the position's
# LIFE.  A position that entered while BTC was neutral can later find BTC
# turning decisively against it; because of the correlation, the pair tends
# to follow.  That is the adverse move the invalidation system already tries
# to catch via the price-derived adverse-excursion gate — BTC opposition is
# simply a LEADING indicator of it.
#
# This overlay does NOT add a new standalone kill.  It only TIGHTENS the
# existing adverse-excursion gate: when a position is already on the losing
# side of entry AND BTC's 1H+4H both oppose the trade direction, the adverse
# fraction threshold is multiplied by ``_MULT`` (<1.0) so the capital-
# preservation exit fires a little earlier.  BTC-aligned or BTC-neutral →
# no change (fail-open).  Tape-driven setups (WHALE / FUNDING / LIQ_REVERSAL)
# are exempt via the same exempt set used by the entry gate.
#
# Ships DARK: default OFF so a merge to main changes no live behaviour.  Flip
# ``INVALIDATION_BTC_CORRELATION_ENABLED=true`` to A/B it against the truth
# report's PROTECTIVE/PREMATURE classifier before adopting.
INVALIDATION_BTC_CORRELATION_ENABLED: bool = _safe_bool(
    "INVALIDATION_BTC_CORRELATION_ENABLED", "false"
)
# Multiplier applied to the adverse-excursion fraction when BTC opposes.
# 0.70 → SR_FLIP early exit shifts from 1.0% adverse (2.5%×0.40) to 0.70%
# (2.5%×0.40×0.70) when BTC is also leaning against the trade.  Range-checked
# to (0, 1]; a value >= 1.0 disables the tightening even when the flag is on.
INVALIDATION_BTC_ADVERSE_FRACTION_MULT: float = float(
    os.getenv("INVALIDATION_BTC_ADVERSE_FRACTION_MULT", "0.70")
)
# TTL (seconds) for the engine-wide cached BTC 1H/4H direction read in the
# TradeMonitor.  1H/4H trends move slowly, so one recompute per minute is
# ample and keeps the per-position invalidation loop cheap.
INVALIDATION_BTC_DIRECTION_CACHE_TTL_SEC: int = int(
    os.getenv("INVALIDATION_BTC_DIRECTION_CACHE_TTL_SEC", "60")
)

# ---------------------------------------------------------------------------
# CANCEL-path pre-TP fee optimisation (research session 19, 2026-06-05).
#
# When the entry regime routes the pre-TP to the CANCEL exit path (RANGING /
# QUIET — see ``position_fsm._regime_exit_path``), a *partial* pre-TP banks
# part of the position via the maker LIMIT and then MARKET-closes the
# residual immediately.  That residual market close is a 3rd fee event plus
# taker slippage on EVERY such win — and the CANCEL path does NOT ride the
# residual to TP1 (it closes it at once), so the partial buys nothing.
#
# Closing the FULL position at the pre-TP LIMIT instead (grab = 1.0) removes
# the residual market close entirely: 2 fees not 3, all maker, no slippage,
# identical exit price.  The losing side is unchanged — if price never
# reaches the pre-TP threshold the LIMIT doesn't fill either way, and the
# native SL still protects the full position until it does.
#
# This is a fee-efficiency win, not a profitability flip (it does not change
# SRFLIP/LSR's win/loss-size asymmetry).  Ships DARK: default OFF so the
# merge changes no live behaviour.  Flip
# ``PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED=true`` to A/B the fee saving.
PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED: bool = _safe_bool(
    "PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED", "false"
)

# ---------------------------------------------------------------------------
# Geo-block for Play Store launch (PLAYSTORE_PLAN.md A6 + E2).
#
# ISO 3166-1 alpha-2 country codes that the auto-execution feature
# is NOT available in.  The client app reads ``GET /api/region`` on
# startup; if the response's ``country_code`` is in this set, the
# auto-trade UI is hidden and the user is shown a "not available in
# your region" message.  Defense-in-depth: dispatch never sees these
# users anyway (since they can't connect a Binance key in the first
# place), but blocking client-side avoids a confusing UX of asking
# for a key and then rejecting it later.
#
# Default list rationale:
#   US — CFTC complexity around crypto derivatives; not worth the
#        risk for a Phase-1 solo-developer product
#   CN — crypto trading is prohibited; serving Chinese users would
#        violate local law
#   BD — crypto trading is banned by Bangladesh Bank circular
#
# Env-overridable (B8): set ``BLOCKED_REGIONS`` to a comma-separated
# list, e.g. ``BLOCKED_REGIONS=US,CN,BD,IR``.  Empty string disables
# the block (useful for development).
_BLOCKED_REGIONS_RAW = os.getenv("BLOCKED_REGIONS", "US,CN,BD")
BLOCKED_REGIONS: frozenset = frozenset(
    code.strip().upper()
    for code in _BLOCKED_REGIONS_RAW.split(",")
    if code.strip()
)


# ---------------------------------------------------------------------------
# Backtester – default slippage per trade (percent, e.g. 0.03 = 0.03 %)
# ---------------------------------------------------------------------------
BACKTEST_SLIPPAGE_PCT: float = _safe_float("BACKTEST_SLIPPAGE_PCT", "0.03")

# ---------------------------------------------------------------------------
# Auto-Execution (V3 groundwork) – when enabled the OrderManager will attempt
# to place orders directly on the exchange instead of (or in addition to)
# publishing Telegram signals.  Disabled by default; flip to True once real
# exchange API keys and order logic are wired in.
#
# Phase A1 (Lumin app foundation): introduce a three-state mode in addition
# to the legacy boolean flag.
#   - off   : no order execution, signals only Telegram (default)
#   - paper : PaperOrderManager — simulates fills against 1m candle data,
#             tracks paper PnL, logs structured paper_trade_fill markers.
#             ZERO real-money risk — used for Demo mode in the app and for
#             our own auto-trade testing before flipping to live.
#   - live  : OrderManager via CCXT — places real orders with real funds.
#             Requires EXCHANGE_API_KEY + EXCHANGE_API_SECRET set.
# ``AUTO_EXECUTION_ENABLED`` is preserved as a derived flag (true when mode
# is not "off") for backwards compatibility with existing call sites.
# ---------------------------------------------------------------------------
# Default flipped from "off" → "paper" 2026-05-07: paper mode is zero-risk
# (no real orders, no exchange API surface) and turns every dispatched
# signal into a tracked virtual position.  Without this, subscribers see
# `today_pnl_usd=$0.00` on Pulse / Trade indefinitely because no broker
# wires up to record fills — making the dashboards feel empty for
# off-mode operators.  Paper-as-default makes the "P&L is zero" failure
# mode explicit (you have to consciously turn it OFF) instead of silent.
# Live mode still requires explicit opt-in via the env var or app toggle.
AUTO_EXECUTION_MODE: str = _safe_choice(
    "AUTO_EXECUTION_MODE",
    default="paper",
    allowed=frozenset({"off", "paper", "live"}),
)
# Backwards-compat alias — true for paper or live, false for off.
AUTO_EXECUTION_ENABLED: bool = AUTO_EXECUTION_MODE != "off"

# Per-user paper books (2026-06-20).  Operational kill switch selecting
# between two fully-wired paper implementations — NOT a dark flag:
#   off (default) → single shared PaperOrderManager + shared pnl_history
#                   "paper" bucket + subscription-window-filtered reads
#                   (the pre-2026-06-20 behaviour, untouched).
#   on            → PaperBookFanout: one PaperOrderManager per user_id, each
#                   writing its own ``paper:<uid>`` pnl bucket + per-user
#                   trades DB; reads repoint to those per-user books.  Both
#                   write and read sides flip together — no half-wired state.
# Default OFF until validated on the VPS with live engine data; flip ON there,
# confirm per-user snapshots populate, then promote ON to the default.
PAPER_PER_USER_BOOKS: bool = _safe_bool("PAPER_PER_USER_BOOKS", "false")
# Directory for per-user paper book artifacts (pnl + trades DB per user).
PAPER_BOOKS_DIR: str = os.getenv("PAPER_BOOKS_DIR", "data/paper_books")

# ---------------------------------------------------------------------------
# Exchange / CCXT execution config (feature 3)
# ---------------------------------------------------------------------------
EXCHANGE_ID: str = os.getenv("EXCHANGE_ID", "binance")
EXCHANGE_API_KEY: str = os.getenv("EXCHANGE_API_KEY", "")
EXCHANGE_API_SECRET: str = os.getenv("EXCHANGE_API_SECRET", "")
EXCHANGE_SANDBOX: bool = os.getenv("EXCHANGE_SANDBOX", "true").lower() == "true"
POSITION_SIZE_PCT: float = _safe_float("POSITION_SIZE_PCT", "2.0")
MAX_POSITION_USD: float = _safe_float("MAX_POSITION_USD", "100.0")

# ---------------------------------------------------------------------------
# Binance USDT-M perpetual futures fee schedule (VIP 0, no BNB discount).
# Used by ``PaperOrderManager`` to deduct realistic fees from simulated
# fills so paper P&L matches what live execution would produce.
# https://www.binance.com/en/fee/futureFee  (verified 2026-05-10)
# Owner-flagged 2026-05-10: pre-fix paper P&L was gross (no fees), making
# the dashboard +$0.87/30d figure misleading vs. real live results.
# ---------------------------------------------------------------------------
BINANCE_FUTURES_MAKER_FEE_PCT: float = _safe_float(
    "BINANCE_FUTURES_MAKER_FEE_PCT", "0.02"
)
BINANCE_FUTURES_TAKER_FEE_PCT: float = _safe_float(
    "BINANCE_FUTURES_TAKER_FEE_PCT", "0.04"
)

# ---------------------------------------------------------------------------
# Risk gates — Phase A2 (mandatory before any live execution per B12)
# ---------------------------------------------------------------------------
# Starting equity reference for daily-loss percentage math.  In paper mode
# this is the synthetic balance.  In live mode the bootstrap should query
# the exchange at boot and override via RiskManager.update_equity().
RISK_STARTING_EQUITY_USD: float = _safe_float("RISK_STARTING_EQUITY_USD", "1000.0")
# Daily-loss kill threshold (negative percent of starting equity).
# Default -3% — generous enough that normal-day drawdowns don't trip but
# tight enough to halt a runaway losing streak before it compounds.
RISK_DAILY_LOSS_LIMIT_PCT: float = _safe_float("RISK_DAILY_LOSS_LIMIT_PCT", "-3.0")
# Max concurrent positions across all symbols.
RISK_MAX_CONCURRENT: int = _safe_int("RISK_MAX_CONCURRENT", "5")
# Max leverage allowed.  Walbi's 200x is irresponsible; we cap at 30x.
RISK_MAX_LEVERAGE: float = _safe_float("RISK_MAX_LEVERAGE", "30.0")
# Min equity floor — auto-pause if equity falls below this.  Default 0
# (disabled).  Useful in live mode to guard against long-tail bleed.
RISK_MIN_EQUITY_USD: float = _safe_float("RISK_MIN_EQUITY_USD", "0.0")
# Comma-separated setups to silently reject at the gate (e.g. emergency
# disable of a misbehaving path without redeploy).  Empty by default.
RISK_SETUP_BLACKLIST_RAW: str = os.getenv("RISK_SETUP_BLACKLIST", "")
RISK_SETUP_BLACKLIST: frozenset = frozenset(
    s.strip() for s in RISK_SETUP_BLACKLIST_RAW.split(",") if s.strip()
)

# ---------------------------------------------------------------------------
# Position reconciliation — Phase A3
# ---------------------------------------------------------------------------
# Periodic drift-check interval (seconds).  Live-mode only.  Default 300
# (5 min) — frequent enough to catch SL/TP / liquidation drift quickly,
# infrequent enough not to hammer the exchange API.
RECONCILER_PERIODIC_INTERVAL_SEC: int = _safe_int(
    "RECONCILER_PERIODIC_INTERVAL_SEC", "300"
)
# When True the reconciler closes orphan positions on boot (positions on
# the exchange that the engine doesn't know about).  Default False —
# alerts only.  Owners who want fully unattended recovery flip this on.
RECONCILER_AUTO_CLOSE_ORPHANS: bool = _safe_bool(
    "RECONCILER_AUTO_CLOSE_ORPHANS", "false"
)
# Last-resort stale-position backstop.  When the reconciler confirms (via
# positionRisk) that a position is STILL open on Binance but its FSM record
# is older than this ceiling, it force-closes at market and marks the
# position CLOSED (reason STALE_EXPIRY).  This is the safety net behind the
# JTOUSDT 2026-06-01 incident — a position whose SL failed to place rode for
# 5h09m (-2.15%) because nothing closed it.  The engine-wide TradeMonitor
# expiry (MAX_SCALP_HOLD = 3600s) only covers signals in its own book; an
# orphaned per-user FSM position with no live signal needs this independent
# ceiling.  Default 7200s (2h) — comfortably beyond any legitimate scalp
# hold (doctrine: 5-60 min) so it never clips a healthy position.
RECONCILER_MAX_POSITION_AGE_SEC: int = _safe_int(
    "RECONCILER_MAX_POSITION_AGE_SEC", "7200"
)
# When True the reconciler's stale-position backstop is armed (the
# force-close above).  Default True — an uncovered position past the age
# ceiling is strictly worse than a market exit.  Flip OFF only to revert to
# alert-only behaviour during incident triage.
RECONCILER_STALE_CLOSE_ENABLED: bool = _safe_bool(
    "RECONCILER_STALE_CLOSE_ENABLED", "true"
)

# Defensive resync interval (seconds) for the engine's in-memory live-
# position index.  The index is maintained write-through by put_position /
# delete_position (the same sole-writer invariant behind the write-generation
# counter), so this only guards against a write that bypasses those two
# paths.  ONE collection-group read per interval — negligible.  Default 300s
# (5 min).  Set 0 to disable the resync loop entirely (write-through only).
POSITION_INDEX_RESYNC_SEC: int = _safe_int("POSITION_INDEX_RESYNC_SEC", "300")

# ---------------------------------------------------------------------------
# Margin-mode enforcement — 2026-06-01 (VTHOUSDT isolated-margin incident)
# ---------------------------------------------------------------------------
# Before the first entry on each (user, symbol) the FSM asserts CROSSED
# margin via POST /fapi/v1/marginType.  A test account placed five VTHOUSDT
# positions in ISOLATED margin (all losses) because the symbol defaulted to
# isolated on the account; the engine assumed CROSSED but never enforced it.
# Default True.  Best-effort: a failed switch is logged + surfaced but does
# not block the entry (the position still opens, just possibly isolated).
MARGIN_MODE_ENFORCE_CROSS: bool = _safe_bool("MARGIN_MODE_ENFORCE_CROSS", "true")

# Number of SL placement attempts at entry before the FSM force-closes an
# otherwise-uncovered position.  A position must never sit OPEN without a
# stop; if the SL can't be placed after this many tries, the entry is
# market-closed rather than left naked.  Retries cover transient failures —
# signing/network blips AND transient Binance rejects (chiefly -2021 "would
# immediately trigger"); deterministic rejects (tick size, precision, price
# filter, key errors) short-circuit straight to force-close.
#
# Default 6 (2026-06-01 follow-up): PR #555 retried -2021 but the window was
# only 3 attempts × 0.5s = 1.5s.  The mark-price wicks on thin alts (IDUSDT,
# AIAUSDT) right after a MARKET entry persist 2-5s — long enough to exhaust
# the 1.5s window on every attempt, so the force-close still fired in 4-8s at
# ~entry price (the regression visibly persisted post-merge).  6 attempts with
# a 1.0s linear backoff gives a ~15s window (1+2+3+4+5), covering an observed
# 5s wick 3x over while keeping the uncovered window short.  The position is
# uncovered only during this window (the TradeMonitor 5s poll + mark-price
# backstop still guard a catastrophic move); a momentary uncovered window beats
# force-closing a live signal the engine still considers ACTIVE.
SL_PLACEMENT_MAX_ATTEMPTS: int = _safe_int("SL_PLACEMENT_MAX_ATTEMPTS", "6")
# Backoff (seconds) between SL placement attempts, multiplied by the attempt
# number (1.0, 2.0, 3.0 …).  Gives a transient mark-price wick that caused a
# -2021 reject time to recede before the retry.  Default 1.0 → a ~15s window
# across 6 attempts, long enough for thin-alt wicks to recede.
SL_RETRY_BACKOFF_SEC: float = _safe_float("SL_RETRY_BACKOFF_SEC", "1.0")

# ---------------------------------------------------------------------------
# Trailing stop – ATR multiplier for adaptive trailing distance
# ---------------------------------------------------------------------------
TRAILING_ATR_MULTIPLIER: float = _safe_float("TRAILING_ATR_MULTIPLIER", "1.5")

# ---------------------------------------------------------------------------
# Break-even SL shift — mark-price-triggered
# ---------------------------------------------------------------------------
# Once mark price has moved BE_SHIFT_TRIGGER_PCT% in our favour from the
# filled entry price, the pretp_dispatcher cancels the original SL and
# places a new STOP_MARKET at entry (break-even).  If price then reverses
# to entry the position exits at 0% gross (−fees) instead of the full SL
# loss.  Owner-confirmed value: 1.0% (Session 34 simulation showed +0.89%
# total PnL edge vs TP1-only across 499 closed signals).
BE_SHIFT_TRIGGER_PCT: float = _safe_float("BE_SHIFT_TRIGGER_PCT", "1.0")

# Engine-default signal-exit model (owner directive, 2026-06-29). Profit-Lab on
# 233 closed signals: the engine's real tracked exits net −18.13% while a simple
# "move SL→entry once +1% in profit, then close 100% at TP1" exit nets −0.23%
# (+17.89% edge). The leak is the exit logic (40%-at-TP1 partial + TP2/TP3
# runner + invalidation kills giving back MFE), NOT the entries. When enabled
# (engine default), trade_monitor — the signal tracker that drives subscriber
# outcomes + the Profit page — manages the engine's signal book as:
#   * BE-to-entry once max-favorable-excursion ≥ BE_SHIFT_TRIGGER_PCT (1%), and
#   * full close (100%) at TP1 — no partial, no TP2/TP3 runner, and
#   * no engine-wide structural/trailing invalidation kills.
# Pre-TP and invalidation remain available to users who opt in via their
# per-user invalidation_mode (handled separately in _check_per_user_invalidation
# + the FSM); this flag only governs the engine's own default book. Reversible
# env off-switch — set false to restore the laddered exit.
BE_THEN_TP1_DEFAULT_ENABLED: bool = _safe_bool("BE_THEN_TP1_DEFAULT_ENABLED", "true")

# ---------------------------------------------------------------------------
# Noise-aware exits + cohort-edge gate (owner-approved ACTIVE, 2026-07-07)
# ---------------------------------------------------------------------------
# Root cause (7d study, 200 shorts + 300 tracked signals vs real 1m klines):
#   * 52% of SL hits crossed back through entry within 1h of stopping out
#     (75% within 3h) — median stop distance 1.00% vs 1.80% average post-SL
#     favourable move: stops sat INSIDE the pairs' hourly noise band.
#   * 84% of BREAKEVEN_EXIT scratches reached ≥1% profit within 3h — the 1%
#     flat BE arm + exact-entry park systematically scratched winners.
# These are ENV BOOT DEFAULTS ONLY — the live values are runtime tunables on
# the ``control/runtime_tunables`` Firestore doc, owner-controlled from the
# 360 CE Ops panel (src/runtime_tunables.py), read via a 5s-cached accessor.
# No manual .env changes are needed on the VPS to adjust any of them.

# Widen every stop to ≥ NOISE_FLOOR_ATR_MULT × ATR(1h)% of entry (capped at
# NOISE_FLOOR_MAX_SL_PCT). Auto-trade notional is scaled down by the same
# widening factor so per-trade capital at risk is unchanged (risk-constant).
NOISE_FLOOR_STOPS_ENABLED: bool = _safe_bool("NOISE_FLOOR_STOPS_ENABLED", "true")
NOISE_FLOOR_ATR_MULT: float = _safe_float("NOISE_FLOOR_ATR_MULT", "1.0")
NOISE_FLOOR_MAX_SL_PCT: float = _safe_float("NOISE_FLOOR_MAX_SL_PCT", "3.0")

# BE ratchet arms at the LARGEST of: BE_SHIFT_TRIGGER_PCT (legacy flat %),
# BE_ARM_R_MULT × the signal's own stop distance, and BE_ARM_NOISE_MULT × the
# pair's noise floor. The armed stop parks BE_PARK_TOLERANCE_PCT on the loss
# side of entry so an exact-entry wick no longer scratches the trade.
BE_ARM_R_MULT: float = _safe_float("BE_ARM_R_MULT", "1.0")
BE_ARM_NOISE_MULT: float = _safe_float("BE_ARM_NOISE_MULT", "0.75")
BE_PARK_TOLERANCE_PCT: float = _safe_float("BE_PARK_TOLERANCE_PCT", "0.15")
# Cap the BE arm threshold at this fraction of the trade's own TP1 distance
# (2026-07-10).  The noise-aware arm (max of flat / 1R / 0.75×noise) double-
# counted the #702 noise-floor stop WIDENING: 1R of an already-noise-widened
# 2.4-2.7% stop put the arm at ≈ the stop distance — at or ABOVE TP1 for the
# tighter setups, i.e. unreachable under the TP1-full-close default.  Owner-
# reported symptom (2026-07-10): signals ran +2% and round-tripped to the full
# −2.4-2.7% SL with no BE shift, a ~5% swing.  With the cap, a trade that has
# covered this fraction of the way to TP1 always arms, whatever the stop
# width.  Never caps below the flat trigger (BE_SHIFT_TRIGGER_PCT).  0 = off.
BE_ARM_TP1_CAP_FRACTION: float = _safe_float("BE_ARM_TP1_CAP_FRACTION", "0.5")

# Cohort-edge STEP 2 (activates the #696 STEP 1 store): suppress emission when
# the signal's cohort (setup × side × regime family × BTC macro) has at least
# COHORT_EDGE_GATE_MIN_N resolved outcomes and Wilson-lower-bounded expectancy
# ≤ COHORT_EDGE_SUPPRESS_BELOW %/trade. Fail-open below min samples.
COHORT_EDGE_GATE_ENABLED: bool = _safe_bool("COHORT_EDGE_GATE_ENABLED", "true")
COHORT_EDGE_GATE_MIN_N: int = _safe_int("COHORT_EDGE_GATE_MIN_N", "10")
COHORT_EDGE_SUPPRESS_BELOW: float = _safe_float("COHORT_EDGE_SUPPRESS_BELOW", "-0.05")

# Mark-feed freshness guard for the trade monitor. ``_latest_price`` /
# ``_candle_extremes`` read the last 1m candle from the scan store, which keeps
# serving a STALE non-None value once a signal's symbol drops out of the active
# scan universe (surge-promoted MOVER / intermittently re-scanned Tier-3 pairs).
# That froze sig.current_price near entry and, with it, pnl_pct, MFE and the
# SL/TP backstop (CAPUSDT SHORT sat 3h at a stored +0.05% MFE while the pair had
# actually run +3.24% favourable). When the store's last 1m kline is older than
# MARK_FEED_STALENESS_MAX_AGE_SEC, prefer the all-symbols mark-price feed (1s
# cadence, every USDT-M pair) — the same feed the None-path already trusted.
# ``age is None`` is treated as fresh, mirroring the scanner's dispatch gate
# (seed-loaded candles don't stamp a timestamp until the first WS frame).
MARK_FEED_STALENESS_ENABLED: bool = _safe_bool("MARK_FEED_STALENESS_ENABLED", "true")
MARK_FEED_STALENESS_MAX_AGE_SEC: float = _safe_float("MARK_FEED_STALENESS_MAX_AGE_SEC", "120.0")

# How often the trade monitor publishes data/pricing_freshness.json — the
# per-open-position pricing-source freshness snapshot the watchdog and the
# liveness probe consume (audit F-07: an open position priced off a frozen
# source must PAGE, not just fall back).  Local disk write, off the per-tick
# hot path (throttled inside _check_all); 0 disables publishing.
PRICING_FRESHNESS_PUBLISH_SEC: float = _safe_float("PRICING_FRESHNESS_PUBLISH_SEC", "30.0")

# ---------------------------------------------------------------------------
# Mover-path profitability package (owner-approved ACTIVE, 2026-07-09)
# ---------------------------------------------------------------------------
# Root cause (3d post-#702 window vs the Jun-01→Jul-05 range, ops Profit CSVs):
# the non-mover book runs +0.37%/trade net while the mover paths run −0.44%/
# trade net.  Mover entries FIND the moves (avg MFE 3.38% on MVRTP) but the
# engine-default exit banks at most TP1 = 1R and the BE park realises ~0 on
# runs that reach +12% / +31% MFE — 42% of mover signals reached ≥1% MFE yet
# realised ≤0, forfeiting 68% MFE in 3 days.  A momentum-continuation path
# needs a runner exit, not a 1R full-close.
# Owner sign-off in-session (2026-07-09): "make it live, no dark flags" — the
# measured counterfactual (the Profit tracker's MFE / give-back columns over
# both windows) IS the shadow evidence, mirroring the #702 activation.  These
# are ENV BOOT DEFAULTS ONLY — live values are runtime tunables on the ops
# panel (src/runtime_tunables.py); each remains reversible from ops with one
# click, no redeploy.  When a flag is turned OFF, its shadow logging
# ("[SHADOW] …_WOULD_…") resumes so the off-state keeps measuring.

# Runner exit for mover setup classes (MOVER_TREND_PULLBACK /
# MOVER_AVWAP_SCALP) on the engine's own signal book: instead of the
# BE_THEN_TP1 full close at TP1, bank a partial at TP1, a further partial at
# TP2 (stop→TP1), and let the remainder ride the existing phase-tightened ATR
# trail to TP3 / trail-out.  Realised PnL blends the banked slices honestly
# (see TradeMonitor._set_realized_pnl).
MOVER_RUNNER_EXIT_ENABLED: bool = _safe_bool("MOVER_RUNNER_EXIT_ENABLED", "true")

# Loss-streak cooldown escalation: consecutive losing outcomes on the same
# (symbol, setup_class, direction) double the lifecycle cooldown extension per
# repeat (SL 1h → 2h → 4h …, capped at LOSS_STREAK_CAP_HOURS) so the scanner
# stops re-entering the same failing setup every cooldown lapse (MONUSDT
# MVRTP LONG: 6 dispatches / −3.7% in 3 days).  A streak counts outcomes at or
# below LOSS_STREAK_LOSS_PCT and resets at or above LOSS_STREAK_RESET_PCT
# (BE-park scratches in between leave it unchanged).
LOSS_STREAK_ESCALATION_ENABLED: bool = _safe_bool("LOSS_STREAK_ESCALATION_ENABLED", "true")
LOSS_STREAK_CAP_HOURS: float = _safe_float("LOSS_STREAK_CAP_HOURS", "12.0")
LOSS_STREAK_LOSS_PCT: float = _safe_float("LOSS_STREAK_LOSS_PCT", "-0.5")
LOSS_STREAK_RESET_PCT: float = _safe_float("LOSS_STREAK_RESET_PCT", "0.5")

# Active-duplicate dispatch guard: block a dispatch when the active signal
# book already holds an OPEN signal with the same (symbol, setup_class,
# direction).  The 30-min dispatch cooldown intends this but does not survive
# every restart path (SPCXUSDT MVRTP SHORT emitted twice 7 min apart at an
# identical entry/SL on 2026-07-08); checking the live book is restart-proof.
ACTIVE_DUP_GUARD_ENABLED: bool = _safe_bool("ACTIVE_DUP_GUARD_ENABLED", "true")

# ---------------------------------------------------------------------------
# Funding-rate exit
# ---------------------------------------------------------------------------
# How many seconds before a symbol's next funding settlement to exit a
# position that would PAY funding. Funding is charged only on positions
# held at the exact settlement timestamp, so exiting inside this window
# avoids the fee entirely. The watcher reads each symbol's real
# next-funding-time from the mark-price stream, so this works regardless
# of the pair's funding interval (Binance uses 4h / 8h / 1h). A
# REDUCE_ONLY market close fills in well under a second, so 120s is amply
# safe with the 30s poll. Set to 0 to disable the watcher entirely.
PRE_FUNDING_EXIT_WINDOW_SEC: int = _safe_int("PRE_FUNDING_EXIT_WINDOW_SEC", "120")

# Minimum absolute funding rate (fraction, not percent) for the watcher to
# act. Baseline Binance funding is ~0.0001 (0.01%) per settlement; dodging
# that is not worth the taker fee to close early. Default 0.0005 (0.05%, 5x
# baseline) means we only exit when funding is clearly elevated — exactly
# the crowded-trend conditions where the fee drag is material.
PRE_FUNDING_MIN_RATE: float = _safe_float("PRE_FUNDING_MIN_RATE", "0.0005")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
_raw_log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL: str = _raw_log_level if _raw_log_level in _VALID_LOG_LEVELS else "INFO"
if _raw_log_level not in _VALID_LOG_LEVELS and _raw_log_level != "INFO":
    logging.warning(
        "Invalid LOG_LEVEL=%r — falling back to INFO. Valid levels: %s",
        _raw_log_level,
        ", ".join(sorted(_VALID_LOG_LEVELS)),
    )

# ---------------------------------------------------------------------------
# AI Trade Observer – background module that captures full trade lifecycle data
# and generates periodic AI-powered digests for the admin Telegram channel.
# ---------------------------------------------------------------------------
OBSERVER_ENABLED: bool = _safe_bool("OBSERVER_ENABLED", "true")
OBSERVER_POLL_INTERVAL: float = _safe_float("OBSERVER_POLL_INTERVAL", "60")
OBSERVER_DIGEST_INTERVAL_SECONDS: int = _safe_int("OBSERVER_DIGEST_INTERVAL", "21600")  # 6 hours
OBSERVER_DATA_PATH: str = os.getenv("OBSERVER_DATA_PATH", "data/trade_observations.json")
OBSERVER_MAX_OBSERVATIONS_PER_TRADE: int = _safe_int("OBSERVER_MAX_OBSERVATIONS", "120")
OBSERVER_DIGEST_LOOKBACK_HOURS: int = _safe_int("OBSERVER_DIGEST_LOOKBACK", "24")

# ---------------------------------------------------------------------------
# MTF hard block – when True, MTF misalignment is a hard veto (signal blocked)
# instead of a soft -5.0 confidence penalty.
# Defaults to False: each channel's own evaluate() method already runs a
# channel-specific, regime-aware MTF hard gate (e.g. mtf_gate_scalp_standard).
# A second scanner-level hard block on top of that double-gates every signal
# and blocks many valid setups where the 1h/4h trend lags the 5m signal.
# Set MTF_HARD_BLOCK=true to restore the strict scanner-level veto.
# ---------------------------------------------------------------------------
MTF_HARD_BLOCK: bool = _safe_bool("MTF_HARD_BLOCK", "false")

# ---------------------------------------------------------------------------
# Correlated position exposure cap
# Maximum number of same-direction active scalp signals allowed concurrently.
# When this threshold is reached, additional signals in the same direction are
# blocked to limit correlated exposure (e.g. all LONG scalps stopped out by BTC).
# ---------------------------------------------------------------------------
MAX_CORRELATED_SCALP_SIGNALS: int = _safe_int("MAX_CORRELATED_SCALP_SIGNALS", "4")

# ---------------------------------------------------------------------------
# SMC hard gate — minimum structural basis required before a signal can fire.
# A signal with smc_score < SMC_HARD_GATE_MIN has no institutional footprint;
# sweep detected (10pts base) + partial depth bonus reaches 12 pts minimum.
# ---------------------------------------------------------------------------
SMC_HARD_GATE_MIN: float = _safe_float("SMC_HARD_GATE_MIN", "12.0")

# ---------------------------------------------------------------------------
# Trend hard gate — minimum indicator sub-score for scalp channels.
# indicator_score < 10 means MACD/RSI/EMA are not supporting the direction —
# a structural contradiction for momentum scalp channels.
# ---------------------------------------------------------------------------
TREND_HARD_GATE_MIN: float = _safe_float("TREND_HARD_GATE_MIN", "10.0")

# ---------------------------------------------------------------------------
# Global per-symbol cooldown (seconds) across ALL channels combined.
# After ANY channel fires on a symbol, that symbol is locked on all channels
# for this duration. Prevents multiple same-symbol signals in quick succession.
# ---------------------------------------------------------------------------
GLOBAL_SYMBOL_COOLDOWN_SECONDS: int = _safe_int(
    "GLOBAL_SYMBOL_COOLDOWN_SECONDS", "900"  # 15 minutes (reduced from 30)
)

# ---------------------------------------------------------------------------
# MTF / SMC score relaxation for SHORT signals in TRENDING_DOWN regime.
# ---------------------------------------------------------------------------
MTF_MIN_SCORE_TRENDING_SHORT: float = float(
    os.getenv("MTF_MIN_SCORE_TRENDING_SHORT", "0.45")
)
SMC_SCORE_MIN_TRENDING_SHORT: float = float(
    os.getenv("SMC_SCORE_MIN_TRENDING_SHORT", "6.0")
)

# ---------------------------------------------------------------------------
# Confidence log (data-driven weight profiling infrastructure)
# When enabled, compute_confidence() appends a structured JSON record to
# CONFIDENCE_LOG_PATH for each scored signal.  The log can be used offline
# for logistic-regression analysis to derive optimal weight profiles.
# ---------------------------------------------------------------------------
CONFIDENCE_LOG_ENABLED: bool = _safe_bool("CONFIDENCE_LOG_ENABLED", "false")
CONFIDENCE_LOG_PATH: str = os.getenv("CONFIDENCE_LOG_PATH", "data/confidence_log.jsonl")

# ---------------------------------------------------------------------------
# Macro blackout window – block signals before/after major macro events.
# ---------------------------------------------------------------------------
MACRO_BLACKOUT_PRE_MINUTES: int = _safe_int("MACRO_BLACKOUT_PRE_MINUTES", "30")
MACRO_BLACKOUT_POST_MINUTES: int = _safe_int("MACRO_BLACKOUT_POST_MINUTES", "60")


# ---------------------------------------------------------------------------
# No-signal watchdog — alert admin when no new signals are generated for an
# extended period while WebSocket health is degraded.
# ---------------------------------------------------------------------------
# Seconds without a new signal before the watchdog fires (default: 1 hour).
NO_SIGNAL_ALERT_THRESHOLD_SECONDS: int = int(
    os.getenv("NO_SIGNAL_ALERT_THRESHOLD_SECONDS", "3600")
)
# Minimum seconds between repeated no-signal alerts (cooldown to avoid spam).
NO_SIGNAL_ALERT_COOLDOWN_SECONDS: int = int(
    os.getenv("NO_SIGNAL_ALERT_COOLDOWN_SECONDS", "3600")
)

# ---------------------------------------------------------------------------
# WS health-aware scan gating
# ---------------------------------------------------------------------------
# Number of consecutive scan cycles with both WS managers unhealthy before
# an admin alert is sent.
WS_DEGRADED_CYCLES_ALERT: int = _safe_int("WS_DEGRADED_CYCLES_ALERT", "10")

# Maximum consecutive degraded cycles before the scanner falls back to REST-only
# scanning instead of blocking indefinitely.  After this many skipped cycles
# the scanner proceeds with REST-based data fetching for top pairs.
# Default 60 cycles × 5 s = ~5 minutes.
WS_DEGRADED_MAX_CYCLES: int = _safe_int("WS_DEGRADED_MAX_CYCLES", "60")

# Health-ratio threshold below which a single WS manager is considered
# "partially degraded".  When either WS manager drops below this fraction
# of healthy connections the scanner applies reduced scan limits to avoid
# burning Binance API weight on REST depth fetches for all 800 pairs.
# 0.5 = fewer than half of connections are open/non-stale → degraded mode.
WS_PARTIAL_HEALTH_THRESHOLD: float = float(
    os.getenv("WS_PARTIAL_HEALTH_THRESHOLD", "0.5")
)

# Maximum number of symbols to scan per cycle when WS is partially degraded.
# Reduces REST API consumption while still providing signals for top pairs.
WS_DEGRADED_MAX_PAIRS: int = _safe_int("WS_DEGRADED_MAX_PAIRS", "75")

# ---------------------------------------------------------------------------
# WS reconnection resilience — escalation alert threshold
# ---------------------------------------------------------------------------
# After this many consecutive reconnect failures on any one connection, fire
# a "manual intervention needed" admin alert.
WS_RECONNECT_FAIL_ALERT_THRESHOLD: int = int(
    os.getenv("WS_RECONNECT_FAIL_ALERT_THRESHOLD", "50")
)

#: Interval (seconds) between WebSocket connection health checks.
WS_HEALTH_CHECK_INTERVAL: int = _safe_int("WS_HEALTH_CHECK_INTERVAL", "30")
#: Minimum message rate (messages/minute) below which a connection is flagged unhealthy.
WS_MIN_MESSAGE_RATE: float = _safe_float("WS_MIN_MESSAGE_RATE", "1.0")
#: How long a connection must stay below ``WS_MIN_MESSAGE_RATE`` before the
#: health-check loop force-closes it to trigger reconnect.  2026-05-14: added
#: to make the previously-passive ``_health_check_loop`` actually act on the
#: low-rate signal.  Without this, the loop logged "low message rate" forever
#: while the futures connection sat in silent-but-pingable state.  90 s gives
#: enough window to absorb a single missed kline frame without churning.
WS_LOW_MSGRATE_FORCE_CLOSE_AFTER_SEC: int = _safe_int(
    "WS_LOW_MSGRATE_FORCE_CLOSE_AFTER_SEC", "90"
)
#: Skip the health-check force-close for connections that have been open less
#: than this many seconds.  Prevents post-reconnect churn while the new
#: connection is still in its resubscribe phase (200 streams typically take
#: 30-60 s before kline data begins arriving).
WS_HEALTH_CHECK_MIN_CONN_AGE_SEC: int = _safe_int(
    "WS_HEALTH_CHECK_MIN_CONN_AGE_SEC", "120"
)
#: Per-symbol kline staleness threshold (seconds).  Per-connection health is
#: necessary but not sufficient — a "healthy" connection can have a subset of
#: subscribed symbol streams silent inside it.  Every health-check cycle we
#: read ``data_store.last_kline_age_seconds(symbol, "1m")`` for each subscribed
#: symbol; symbols with age above this threshold are counted as stale.
WS_PER_SYMBOL_STALENESS_THRESHOLD_SEC: float = _safe_float(
    "WS_PER_SYMBOL_STALENESS_THRESHOLD_SEC", "180"
)
#: Fraction of subscribed symbols that must be stale (per above threshold)
#: before the manager force-closes ALL its connections to trigger a full
#: resubscribe.  Set conservatively at 0.5 so a few low-volume coins don't
#: trigger reconnects on their own.
WS_PER_SYMBOL_STALENESS_RATIO: float = _safe_float(
    "WS_PER_SYMBOL_STALENESS_RATIO", "0.5"
)
#: WS-trace file — dedicated loguru sink writes structured ``<WS:LABEL>``
#: events to this path so the operator can pull the file via the ``/ws_log``
#: Telegram command without SSH access.  Captures every connect, close,
#: subscribe ack, watchdog/health-check force-close, per-symbol staleness
#: trip, and a periodic per-connection summary (active vs. silent streams).
#: Path is relative to the engine working directory; matches the engine
#: log convention (``logs/engine_{time}.log``).
WS_TRACE_LOG_PATH: str = os.getenv("WS_TRACE_LOG_PATH", "logs/ws_trace.log")
#: Rotation size for the WS-trace file.  Loguru rotates on size; rotated
#: files share the base name with a counter suffix.
WS_TRACE_LOG_ROTATION: str = os.getenv("WS_TRACE_LOG_ROTATION", "5 MB")
#: Number of rotated WS-trace files to retain.  5 × 5 MB = 25 MB ceiling
#: for the rolling history.  More than enough for a multi-hour incident
#: replay without blowing the data volume.
WS_TRACE_LOG_RETENTION: int = _safe_int("WS_TRACE_LOG_RETENTION", "5")
#: How often (seconds) the WS health-check loop emits the periodic
#: ``stream_summary`` event.  Lower = noisier log, faster diagnostic
#: signal; higher = quieter file, slower to spot per-symbol drops.
WS_TRACE_SUMMARY_INTERVAL_SEC: int = _safe_int(
    "WS_TRACE_SUMMARY_INTERVAL_SEC", "60"
)
#: Per-stream staleness threshold (seconds) for the periodic summary.
#: Streams that haven't delivered a TEXT frame within this window count
#: as ``silent_*`` in the summary line.  Separate from the per-symbol
#: force-close threshold (which acts on data_store kline age, not on raw
#: WS frame arrival).
WS_TRACE_SUMMARY_STALENESS_SEC: int = _safe_int(
    "WS_TRACE_SUMMARY_STALENESS_SEC", "180"
)
#: Number of first raw WS messages to log per connection regardless of
#: type (TEXT / BINARY / CLOSED / etc.).  Diagnostic added 2026-05-14
#: to identify whether Binance is sending BINARY frames (which our
#: original ``_listen`` silently dropped) when the stream_summary
#: showed ``never_seen=all`` even after the URL fix landed.  The
#: counter resets on each ``_connect``; once exceeded, subsequent
#: messages are processed normally without the sample log.
WS_TRACE_SAMPLE_FIRST_N: int = _safe_int("WS_TRACE_SAMPLE_FIRST_N", "10")
#: Pairs that get dedicated (non-multiplexed) WebSocket connections for lowest latency.
WS_PRIORITY_DEDICATED_PAIRS: List[str] = [
    p.strip() for p in os.getenv(
        "WS_PRIORITY_DEDICATED_PAIRS", "BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT"
    ).split(",") if p.strip()
]

# ---------------------------------------------------------------------------
# Suppression telemetry
# ---------------------------------------------------------------------------
#: Enable suppression telemetry collection.
SUPPRESSION_TELEMETRY_ENABLED: bool = _safe_bool("SUPPRESSION_TELEMETRY_ENABLED", "true")
#: Maximum number of suppression events to keep in memory.
SUPPRESSION_TELEMETRY_MAX_EVENTS: int = _safe_int("SUPPRESSION_TELEMETRY_MAX_EVENTS", "10000")

# ---------------------------------------------------------------------------
# PR2 — AI Engagement Layer
# ---------------------------------------------------------------------------
#: Master switch — enable/disable the content engine entirely.
CONTENT_ENGINE_ENABLED: bool = _safe_bool("CONTENT_ENGINE_ENABLED", "true")
#: Enable/disable the radar channel evaluator.
RADAR_CHANNEL_ENABLED: bool = _safe_bool("RADAR_CHANNEL_ENABLED", "true")
#: Enable/disable the silence breaker (auto-post when channel is quiet).
SILENCE_BREAKER_ENABLED: bool = _safe_bool("SILENCE_BREAKER_ENABLED", "true")
#: Minimum confidence score to trigger a radar alert (free channel).
RADAR_ALERT_MIN_CONFIDENCE: int = _safe_int("RADAR_ALERT_MIN_CONFIDENCE", "65")
#: Confidence score at which "watching closely" variant is used for radar alerts.
RADAR_ALERT_WATCHING_CLOSELY_CONFIDENCE: int = _safe_int("RADAR_ALERT_WATCHING_CLOSELY_CONFIDENCE", "70")
#: Per-symbol cooldown (seconds) between radar alerts for the same symbol.
RADAR_PER_SYMBOL_COOLDOWN_SECONDS: int = _safe_int("RADAR_PER_SYMBOL_COOLDOWN_SECONDS", "900")
#: Maximum number of radar alerts posted per hour (cross-symbol rate limit).
RADAR_MAX_PER_HOUR: int = _safe_int("RADAR_MAX_PER_HOUR", "3")
#: TTL (seconds) for an open radar watch before it auto-expires (default 4 h).
RADAR_WATCH_TTL_SECONDS: int = _safe_int("RADAR_WATCH_TTL_SECONDS", "14400")
#: Hours of channel silence before the silence breaker auto-posts content.
SILENCE_BREAKER_HOURS: int = _safe_int("SILENCE_BREAKER_HOURS", "3")
#: GPT model used for content generation (gpt-4o-mini is cost-efficient and fast).
CONTENT_GPT_MODEL: str = os.getenv("CONTENT_GPT_MODEL", "gpt-4o-mini")

# ---------------------------------------------------------------------------
# Funding rate gate — soft penalty/boost thresholds (item 13)
# ---------------------------------------------------------------------------
#: Funding rate penalty threshold: LONG is expensive when funding > this value.
FUNDING_RATE_PENALTY_THRESHOLD: float = float(
    os.getenv("FUNDING_RATE_PENALTY_THRESHOLD", "0.01")
)
#: Funding rate boost threshold: confirmation when funding is extreme in opposite direction.
FUNDING_RATE_BOOST_THRESHOLD: float = float(
    os.getenv("FUNDING_RATE_BOOST_THRESHOLD", "0.02")
)
#: Confidence penalty when funding is crowded against signal direction.
FUNDING_RATE_PENALTY: float = float(os.getenv("FUNDING_RATE_PENALTY", "-8.0"))
#: Confidence boost when funding is extreme in opposite direction (high conviction).
FUNDING_RATE_BOOST: float = float(os.getenv("FUNDING_RATE_BOOST", "5.0"))

# ---------------------------------------------------------------------------
# Lumin app HTTP API (FastAPI)
# ---------------------------------------------------------------------------
#: Opt-in: set true to start the FastAPI server alongside the engine.
API_ENABLED: bool = _safe_bool("API_ENABLED", "false")
#: Bind address for the API server.  Use 127.0.0.1 behind a reverse proxy.
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
#: TCP port for the API server.
API_PORT: int = _safe_int("API_PORT", "8000")
#: HMAC secret used to sign anonymous device JWTs.  Auto-generated by
#: ``tools/setup-vps-api.sh`` on first run; rotate via the same script.
#: When unset the auth endpoints return 503 — every protected endpoint
#: rejects all requests.  Required for normal operation.
API_JWT_SECRET: str = os.getenv("API_JWT_SECRET", "")
#: Owner-only static admin token, used for CTE/debug curl from the VPS.
#: When set, every endpoint accepts this exact bearer string in addition
#: to JWTs.  Empty string disables.
API_AUTH_TOKEN: str = os.getenv("API_AUTH_TOKEN", "")
#: When false, ``API_AUTH_TOKEN`` is ignored even if set — JWT-only mode.
API_ALLOW_STATIC_TOKEN: bool = _safe_bool("API_ALLOW_STATIC_TOKEN", "true")
#: Comma-separated CORS origins.  ``*`` for any (development only).
API_CORS_ORIGINS: str = os.getenv("API_CORS_ORIGINS", "*")
#: When true the engine does NOT launch ``serve_api`` as an asyncio task;
#: instead it runs only ``SnapshotWriter`` which publishes live state to
#: Redis every scan cycle.  A separate ``api`` Docker service (running
#: ``python -m src.api.main``) reads those snapshots and serves HTTP.
#: This eliminates the shared-event-loop bottleneck: scanner cycles can
#: no longer block API requests and settings changes take effect in <500ms.
#: Default false → existing single-process behaviour is unchanged.
API_PROCESS_ISOLATED: bool = _safe_bool("API_PROCESS_ISOLATED", "false")

# ---------------------------------------------------------------------------
# Multi-user expansion (Phase 2 — phone-OTP auth + billing webhook)
# ---------------------------------------------------------------------------
#: SQLite path for the user registry (phone, tier, paid_until).  Lives in
#: the same ``data/`` volume as the JSON state files.  WAL mode enabled
#: at first open by ``UserStore``.
LUMIN_DB_PATH: str = os.getenv("LUMIN_DB_PATH", "data/lumin.sqlite")
#: Owner's E.164 phone.  Inserted as ``user_id=1, tier=owner`` on first
#: boot of an empty ``LUMIN_DB_PATH``.  Empty string skips bootstrap —
#: owner falls back to the static admin token until a phone is set.
OWNER_PHONE_E164: str = os.getenv("OWNER_PHONE_E164", "")
#: OTP TTL in seconds.  5 min default; users have this long to enter the
#: code before it expires and they have to request a fresh one.
OTP_TTL_SECONDS: int = _safe_int("OTP_TTL_SECONDS", "300")
#: Per-phone rate limit on OTP issuance — N requests per rolling hour.
#: Defends against an attacker burning the WhatsApp/SMS balance via a
#: single phone.
OTP_MAX_ISSUES_PER_HOUR: int = _safe_int("OTP_MAX_ISSUES_PER_HOUR", "3")
#: Per-code attempt cap on verify.  Wrong-code Nth time drops the record
#: — user has to request a fresh code rather than brute-force the digits.
OTP_MAX_ATTEMPTS_PER_CODE: int = _safe_int("OTP_MAX_ATTEMPTS_PER_CODE", "5")
#: Primary delivery channel for OTPs.  ``log`` (closed-beta default —
#: writes the code to engine logs for owner-mediated forwarding),
#: ``whatsapp`` (Twilio Authentication template — needs Meta verification),
#: ``sms`` (AWS SNS — needs DLT registration for India), or ``telegram``
#: (DM via @LuminProBot — aligns with OWNER_BRIEF B13 "Telegram is the
#: identity primitive", no Meta/AWS paperwork required).
OTP_PRIMARY_CHANNEL: str = _safe_choice(
    "OTP_PRIMARY_CHANNEL", "log",
    frozenset({"log", "whatsapp", "sms", "telegram"}),
)
#: Fallback delivery channel — tried only when the primary returns
#: ``UNSUPPORTED_CHANNEL`` (recipient unreachable).  Empty string
#: disables fallback (single-provider mode).
OTP_FALLBACK_CHANNEL: str = _safe_choice(
    "OTP_FALLBACK_CHANNEL", "",
    frozenset({"", "log", "whatsapp", "sms", "telegram"}),
)

# Twilio (WhatsApp Authentication template).  Only consulted when
# ``OTP_PRIMARY_CHANNEL`` or ``OTP_FALLBACK_CHANNEL`` is ``whatsapp``.
TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
#: Verified WhatsApp Business sender (E.164, no ``whatsapp:`` prefix —
#: provider adds it on the wire).
TWILIO_WHATSAPP_FROM: str = os.getenv("TWILIO_WHATSAPP_FROM", "")
#: Twilio Content SID (``HX...``) for the approved Authentication
#: template.  Body: ``"Your Lumin verification code is {{1}}. ..."``.
TWILIO_WHATSAPP_CONTENT_SID: str = os.getenv("TWILIO_WHATSAPP_CONTENT_SID", "")

# AWS SNS (SMS fallback).  Only consulted when ``OTP_*_CHANNEL`` is ``sms``.
AWS_SNS_REGION: str = os.getenv("AWS_SNS_REGION", "us-east-1")
AWS_SNS_ACCESS_KEY_ID: str = os.getenv("AWS_SNS_ACCESS_KEY_ID", "")
AWS_SNS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SNS_SECRET_ACCESS_KEY", "")
#: Optional 11-char alphanumeric sender ID (where the destination
#: country supports it — varies by carrier).  Empty leaves SNS to use a
#: default short code.
AWS_SNS_SENDER_ID: str = os.getenv("AWS_SNS_SENDER_ID", "")

#: HMAC secret shared with ``@LuminProBot`` (or future billing
#: adapters).  When empty, ``POST /internal/billing/grant`` returns
#: 503 — failing closed rather than accepting all callers.  Set this in
#: lockstep with the bot's signing config.
BILLING_WEBHOOK_SECRET: str = os.getenv("BILLING_WEBHOOK_SECRET", "")

# ---------------------------------------------------------------------------
# Google Play Billing (B16 — v1 in-app subscription purchase path)
# ---------------------------------------------------------------------------
#
# The app sells the subscription via Google Play Billing; the engine verifies
# the resulting ``purchaseToken`` server-side against the Google Play Developer
# API (``purchases.subscriptionsv2``) and is the entitlement source of truth.
# Nothing here is client-trusted.  See ``src/api/billing_play.py``.
#
# All values are env-overridable.  When ``GOOGLE_PLAY_BILLING_ENABLED`` is
# false OR the package / service-account is unset, the Play billing endpoints
# fail closed (503) — exactly like the HMAC billing webhook above.

#: Master switch.  Off by default until the owner has created the Play
#: subscription products + linked a service account (see ACTIVE_CONTEXT
#: "OWNER ACTIONS").  This is an operational kill switch, NOT a dark flag:
#: there is nothing to "measure in shadow" — it is either wired to a real
#: Play Console project or it is not.
GOOGLE_PLAY_BILLING_ENABLED: bool = _safe_bool("GOOGLE_PLAY_BILLING_ENABLED", "false")

#: Money-path entitlement gate (B16 two-tier model).  When true (default),
#: hands-off server-side auto-execution in ``signal_dispatch`` runs ONLY for
#: users whose tier is ``auto`` (or higher: all-access / owner).  Reversible
#: operational kill switch — flip to false to fall back to the pre-B16
#: behaviour (mode/connection-gated only) if the tier gate ever misbehaves
#: for our own test accounts.  This is NOT a dark flag: it ships ON.
AUTO_TRADE_TIER_GATE_ENABLED: bool = _safe_bool("AUTO_TRADE_TIER_GATE_ENABLED", "true")

#: Android application id of the Lumin app, e.g. ``org.luminapp.lumin``.
#: Must match the ``packageName`` Google signs RTDN notifications with and
#: the package the purchase was made under.
GOOGLE_PLAY_PACKAGE_NAME: str = os.getenv("GOOGLE_PLAY_PACKAGE_NAME", "")

#: Filesystem path to the Google Cloud **service-account JSON** that holds
#: Android Publisher API access (granted in Play Console → Users & permissions
#: / API access).  The key never leaves the engine, is never logged, and is
#: never written anywhere else (Hard Limits).  Falls back to the Firebase
#: service-account path when unset *and* that account has been granted
#: Android Publisher access — but an explicit, separate key is preferred so
#: the two trust scopes stay independent.
GOOGLE_PLAY_SERVICE_ACCOUNT_PATH: str = os.getenv(
    "GOOGLE_PLAY_SERVICE_ACCOUNT_PATH",
    os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", ""),
)

#: Product IDs for the two paid tiers (B16 two-tier auto-trade model).
#: A verified purchase of an ASSIST product grants tier ``assist`` (one-tap
#: live trades, ₹1000/mo); an AUTO product grants tier ``auto`` (hands-off
#: server-side execution, ₹2000/mo).  Signals + levels are free.  Comma-
#: separated; must match the Play Console product IDs exactly.  A purchase
#: for any product not in either set is rejected (defence against a tampered
#: client sending a product we never sold).
GOOGLE_PLAY_ASSIST_PRODUCT_IDS: frozenset[str] = frozenset(
    p.strip()
    for p in os.getenv("GOOGLE_PLAY_ASSIST_PRODUCT_IDS", "lumin_assist_monthly").split(",")
    if p.strip()
)
GOOGLE_PLAY_AUTO_PRODUCT_IDS: frozenset[str] = frozenset(
    p.strip()
    for p in os.getenv("GOOGLE_PLAY_AUTO_PRODUCT_IDS", "lumin_auto_monthly").split(",")
    if p.strip()
)

#: product_id → tier map consumed by the billing verifier.  Built from the
#: two sets above so the verifier has a single source of truth.
GOOGLE_PLAY_PRODUCT_TIERS: dict[str, str] = {
    **{pid: "auto" for pid in GOOGLE_PLAY_AUTO_PRODUCT_IDS},
    **{pid: "assist" for pid in GOOGLE_PLAY_ASSIST_PRODUCT_IDS},
}

#: Expected OIDC audience on Google Pub/Sub **push** requests carrying RTDN
#: (Real-Time Developer Notifications).  Pub/Sub signs each push with a Google
#: OIDC token; the engine verifies the token's ``aud`` matches this value so a
#: third party can't POST forged subscription events.  Set to the engine's
#: RTDN endpoint URL (the audience configured on the push subscription).
#: Empty = audience check skipped (only acceptable behind a private network /
#: secret-path URL; set it for the public endpoint).
GOOGLE_PLAY_RTDN_AUDIENCE: str = os.getenv("GOOGLE_PLAY_RTDN_AUDIENCE", "")

#: Optional shared-secret path component appended to the RTDN endpoint as a
#: cheap unguessable-URL defence in addition to (not instead of) the OIDC
#: audience check.  When set, ``POST /api/billing/play/rtdn/<token>`` must
#: match.  Empty = no path secret.
GOOGLE_PLAY_RTDN_PATH_SECRET: str = os.getenv("GOOGLE_PLAY_RTDN_PATH_SECRET", "")

# ---------------------------------------------------------------------------
# Market Alerts (Lumin app Pulse → Alerts feed) + FCM push
# ---------------------------------------------------------------------------
# 100eyes-class informational alerts: single-condition, non-directional
# detector events (RSI extremes, RSI divergence, abnormal volatility,
# near horizontal S/R, volume anomaly) surfaced in the app's Pulse →
# Alerts tab and pushed via FCM.  Entirely OFF the money path — no
# scoring, dispatch, FSM, or paid-channel routing reads any of this.
# Each detector runs on its NATURAL timeframe (mirrors 100eyes: some
# fire on 4h, some 1h, some 15m) over candles already in memory —
# zero new network reads.

#: Master switch for the alert evaluation loop.
ALERTS_ENABLED: bool = _safe_bool("ALERTS_ENABLED", "true")

#: How often the alert loop sweeps the pair universe (seconds).  Detectors
#: only look at CLOSED candles, so sub-minute sweeps buy nothing.
ALERTS_EVAL_INTERVAL_SEC: int = _safe_int("ALERTS_EVAL_INTERVAL_SEC", "60")

#: In-memory feed ring buffer size (also the max the API returns).
ALERTS_BUFFER_MAX: int = _safe_int("ALERTS_BUFFER_MAX", "300")

#: RSI thresholds for the "Extremely Overbought / Oversold" alerts.
ALERTS_RSI_PERIOD: int = _safe_int("ALERTS_RSI_PERIOD", "14")
ALERTS_RSI_OVERBOUGHT: float = _safe_float("ALERTS_RSI_OVERBOUGHT", "80.0")
ALERTS_RSI_OVERSOLD: float = _safe_float("ALERTS_RSI_OVERSOLD", "20.0")

#: RSI divergence detection: pivot fractal half-width and lookback window
#: (closed candles), plus the RSI zone gates that cut low-signal noise
#: (bearish divergence only counts when the first RSI pivot was ≥ the
#: zone-high; bullish when ≤ zone-low).
ALERTS_DIVERGENCE_LOOKBACK: int = _safe_int("ALERTS_DIVERGENCE_LOOKBACK", "40")
ALERTS_DIVERGENCE_PIVOT_K: int = _safe_int("ALERTS_DIVERGENCE_PIVOT_K", "2")
ALERTS_DIVERGENCE_ZONE_HIGH: float = _safe_float("ALERTS_DIVERGENCE_ZONE_HIGH", "60.0")
ALERTS_DIVERGENCE_ZONE_LOW: float = _safe_float("ALERTS_DIVERGENCE_ZONE_LOW", "40.0")

#: Abnormal volatility: last closed candle's true range must exceed
#: this multiple of the prior ATR(14) on the same timeframe.
ALERTS_VOLATILITY_TR_MULT: float = _safe_float("ALERTS_VOLATILITY_TR_MULT", "3.0")

#: Volume anomaly: last closed candle's volume must exceed this multiple
#: of the prior 20-candle mean volume.
ALERTS_VOLUME_SPIKE_MULT: float = _safe_float("ALERTS_VOLUME_SPIKE_MULT", "5.0")

#: Near horizontal S/R: fire when price is within this % of a LevelBook
#: level (and the level has at least the touch count the book scored it with).
ALERTS_NEAR_LEVEL_PCT: float = _safe_float("ALERTS_NEAR_LEVEL_PCT", "0.3")

#: Quality floor for near-level alerts: a "level" the market has only
#: touched once or twice is not a level, it's a price the market visited.
#: 100eyes-class S/R cards lead with the touch count for exactly this
#: reason — the floor keeps the feed to levels a trader would draw.
ALERTS_NEAR_LEVEL_MIN_TOUCHES: int = _safe_int("ALERTS_NEAR_LEVEL_MIN_TOUCHES", "3")

#: Universe gate: only symbols whose 24h quote volume is at or above this
#: many USD are swept for alerts (majors + midcaps — the coins 100eyes
#: covers).  The scanner still trades the full universe; this only curates
#: the informational feed.  Set <= 0 to disable the gate.
ALERTS_MIN_VOLUME_24H_USD: float = _safe_float("ALERTS_MIN_VOLUME_24H_USD", "50000000")

#: Near-level touch quality (alert-side re-count; the LevelBook's own
#: scoring is money-path shared and stays untouched).  The book counts
#: every candle that straddles a level, so a chop range reads as a
#: "523-touch level" — the alert detector instead counts DISTINCT touch
#: events and rejects ranges.
#: Band half-width (%) around the level that counts as touching it.
ALERTS_NEAR_LEVEL_TOUCH_TOLERANCE_PCT: float = _safe_float(
    "ALERTS_NEAR_LEVEL_TOUCH_TOLERANCE_PCT", "0.15"
)
#: Closed 1h bars examined when re-counting touches (~5 days).
ALERTS_NEAR_LEVEL_LOOKBACK: int = _safe_int("ALERTS_NEAR_LEVEL_LOOKBACK", "120")
#: A new touch only counts after price has stayed OUT of the band for at
#: least this many consecutive bars ...
ALERTS_NEAR_LEVEL_MIN_SEPARATION_BARS: int = _safe_int(
    "ALERTS_NEAR_LEVEL_MIN_SEPARATION_BARS", "3"
)
#: ... AND some close in between sat at least this % away from the level
#: (prominence — hovering at a level is one touch, not many).
ALERTS_NEAR_LEVEL_MIN_LEAVE_PCT: float = _safe_float(
    "ALERTS_NEAR_LEVEL_MIN_LEAVE_PCT", "0.5"
)
#: Chop rejection: if more than this fraction of the lookback bars sit
#: inside the band, the "level" is a trading range, not S/R — no alert.
ALERTS_NEAR_LEVEL_MAX_IN_BAND_FRAC: float = _safe_float(
    "ALERTS_NEAR_LEVEL_MAX_IN_BAND_FRAC", "0.25"
)

#: Per-type refire cooldowns.  Timeframe-relative types use a multiple of
#: the timeframe duration (an RSI-extreme 1h alert may refire after
#: 2 × 1h); wall-clock types use fixed seconds.
ALERTS_COOLDOWN_TF_MULT: float = _safe_float("ALERTS_COOLDOWN_TF_MULT", "2.0")
ALERTS_NEAR_LEVEL_COOLDOWN_SEC: int = _safe_int("ALERTS_NEAR_LEVEL_COOLDOWN_SEC", "14400")
ALERTS_VOLATILITY_COOLDOWN_SEC: int = _safe_int("ALERTS_VOLATILITY_COOLDOWN_SEC", "3600")
ALERTS_VOLUME_COOLDOWN_SEC: int = _safe_int("ALERTS_VOLUME_COOLDOWN_SEC", "3600")

#: Per-symbol feed budget across ALL alert types.  One violent candle
#: trips volume + volatility + RSI at once and a hovering price re-trips
#: level alerts — without a cross-type budget a single symbol floods the
#: feed (the "spam" failure mode).  At most this many alerts per symbol
#: per rolling window; higher-priority types win the budget (divergence >
#: near-level > RSI extreme > volume > volatility).
ALERTS_SYMBOL_MAX_PER_WINDOW: int = _safe_int("ALERTS_SYMBOL_MAX_PER_WINDOW", "2")
ALERTS_SYMBOL_WINDOW_SEC: int = _safe_int("ALERTS_SYMBOL_WINDOW_SEC", "3600")

#: Push curation — the FEED can be rich (it's pull-based, filterable in
#: the app); the PHONE must not buzz for every 15m wiggle.  Only alerts
#: on these timeframes push, and pushes are additionally capped per hour
#: across the alerts topic.  Everything still lands in the feed.
ALERTS_PUSH_TIMEFRAMES: str = os.getenv("ALERTS_PUSH_TIMEFRAMES", "1h,4h")
ALERTS_PUSH_MAX_PER_HOUR: int = _safe_int("ALERTS_PUSH_MAX_PER_HOUR", "12")

#: Persistence file so a deploy/restart neither loses the recent feed nor
#: refires every currently-true condition (the cooldown map is persisted
#: alongside the alerts).
ALERTS_PERSIST_PATH: str = os.getenv("ALERTS_PERSIST_PATH", "data/alerts.json")

# ── FCM push (topic-based; app subscribes client-side) ─────────────────────
#: Master switch for FCM pushes.  Requires Firebase Admin to be initialised
#: (FIREBASE_SERVICE_ACCOUNT_PATH / FIREBASE_PROJECT_ID); the sender
#: degrades to a silent no-op when it isn't, so this can stay ON everywhere.
FCM_PUSH_ENABLED: bool = _safe_bool("FCM_PUSH_ENABLED", "true")

#: Topic names the app subscribes to.  Keep in sync with the Lumin app's
#: NotificationService topic constants.
FCM_ALERTS_TOPIC: str = os.getenv("FCM_ALERTS_TOPIC", "alerts")
FCM_SIGNALS_TOPIC: str = os.getenv("FCM_SIGNALS_TOPIC", "signals")

#: Push classes — each independently gated so ops can silence one class
#: without touching the others.
FCM_PUSH_ALERTS_ENABLED: bool = _safe_bool("FCM_PUSH_ALERTS_ENABLED", "true")
FCM_PUSH_SIGNALS_ENABLED: bool = _safe_bool("FCM_PUSH_SIGNALS_ENABLED", "true")
FCM_PUSH_OUTCOMES_ENABLED: bool = _safe_bool("FCM_PUSH_OUTCOMES_ENABLED", "true")

#: Global send-rate guard (per minute, across all push classes).  FCM is
#: free but a pathological loop must never be able to spam phones.
FCM_MAX_SENDS_PER_MIN: int = _safe_int("FCM_MAX_SENDS_PER_MIN", "60")
