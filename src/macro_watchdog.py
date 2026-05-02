"""Macro Watchdog — async background task for global market-event alerts.

This module replaces the AI's role in the trade-signal hot path.  Instead of
scoring individual trade signals (which added 2-5 s latency), the AI is now
used exclusively for *global market awareness*.  The ``MacroWatchdog`` polls
news feeds, the Fear & Greed Index, and an OpenAI-powered classifier to detect
macro-level events that could materially move crypto markets:

* 📰 Breaking news (wars, regulatory bans, exchange hacks)
* 🏛️ FOMC meetings / interest-rate decisions
* 📈 Major macroeconomic data releases (CPI, NFP)
* 🔰 New token listings on major exchanges
* ⚠️  Fear & Greed index extremes

When a significant event is detected it is formatted as a high-priority alert
and routed to the Telegram channels:

* HIGH / CRITICAL severity — broadcast to BOTH the admin alert channel AND
  the free subscriber channel.  Subscribers see breaking macro context which
  builds the free-channel value as a paid-conversion funnel.
* MEDIUM / LOW severity — admin channel only (operational signal, not
  subscriber content).

The free-channel post is skipped silently when no ``send_to_free`` callable
is provided (backwards compatible with admin-only usage).

Configuration (via environment variables):
  MACRO_WATCHDOG_ENABLED                  – "true" to enable (default: "true")
  MACRO_WATCHDOG_POLL_INTERVAL            – seconds between polls (default: "300")
  MACRO_WATCHDOG_FEAR_GREED_THRESHOLD_LOW  – F&G below this → extreme fear alert (default: "20")
  MACRO_WATCHDOG_FEAR_GREED_THRESHOLD_HIGH – F&G above this → extreme greed alert (default: "80")
"""

from __future__ import annotations

import asyncio
import hashlib
import time
from typing import Any, Callable, Coroutine, Dict, List, Optional

import aiohttp

from config import (
    MACRO_BTC_MOVE_COOLDOWN_SEC,
    MACRO_BTC_MOVE_THRESHOLD_PCT,
    MACRO_REGIME_SHIFT_COOLDOWN_SEC,
    MACRO_REGIME_SHIFT_ENABLED,
    MACRO_WATCHDOG_ENABLED,
    MACRO_WATCHDOG_POLL_INTERVAL,
    MACRO_WATCHDOG_FEAR_GREED_THRESHOLD_LOW,
    MACRO_WATCHDOG_FEAR_GREED_THRESHOLD_HIGH,
)
from src.ai_engine import (
    fetch_fear_greed_index,
    fetch_news_sentiment,
)
from src.openai_evaluator import MacroEventResult, OpenAIEvaluator
from src.utils import get_logger

log = get_logger("macro_watchdog")

# Severity → emoji mapping for Telegram alerts
_SEVERITY_EMOJI: Dict[str, str] = {
    "LOW": "🟡",
    "MEDIUM": "🟠",
    "HIGH": "🔴",
    "CRITICAL": "🚨",
}

# Severities that get broadcast to the free subscriber channel in addition
# to the admin channel.  HIGH/CRITICAL events are subscriber-relevant
# breaking news (FOMC, regulatory action, exchange hacks, F&G extremes ≤10
# or ≥90).  MEDIUM/LOW stay admin-only — they're operational signal that
# would create noise on the free channel.
_FREE_CHANNEL_SEVERITIES: frozenset = frozenset({"HIGH", "CRITICAL"})

# Minimum Fear & Greed values for automatic alerts (before OpenAI classification)
_FG_EXTREME_LOW: int = MACRO_WATCHDOG_FEAR_GREED_THRESHOLD_LOW
_FG_EXTREME_HIGH: int = MACRO_WATCHDOG_FEAR_GREED_THRESHOLD_HIGH

# Tracked symbols for news monitoring – uses the most liquid pairs by default
_DEFAULT_WATCH_SYMBOLS: List[str] = ["BTC", "ETH", "SOL", "BNB"]

# Minimum seconds between duplicate-headline alerts (per headline hash)
_DEDUP_TTL: float = 3600.0  # 1 hour


class MacroWatchdog:
    """Async background service that monitors macro-events and sends Telegram alerts.

    Parameters
    ----------
    send_alert:
        Async callable that sends a string message to the admin Telegram channel.
        Typically ``TelegramBot.send_admin_alert``.
    send_to_free:
        Optional async callable that posts to the free subscriber channel.
        When provided, HIGH/CRITICAL severity events are broadcast to both
        admin and free channels (subscriber-visible breaking news).  When
        ``None`` (the default), all alerts go to admin only — backwards
        compatible with the original admin-only behaviour.  Typically
        ``TelegramBot.post_to_free_channel``.
    openai_evaluator:
        Optional :class:`~src.openai_evaluator.OpenAIEvaluator` instance.
        When ``None`` or disabled, events are still detected via the Fear & Greed
        index and CryptoPanic headlines but skipped through the AI classifier.
    poll_interval:
        Seconds between each polling cycle.  Defaults to the
        ``MACRO_WATCHDOG_POLL_INTERVAL`` config value.
    watch_symbols:
        Base coin names (e.g. ``["BTC", "ETH"]``) to monitor for news.
    """

    def __init__(
        self,
        send_alert: Callable[[str], Coroutine[Any, Any, bool]],
        send_to_free: Optional[Callable[[str], Coroutine[Any, Any, bool]]] = None,
        openai_evaluator: Optional[OpenAIEvaluator] = None,
        poll_interval: Optional[float] = None,
        watch_symbols: Optional[List[str]] = None,
    ) -> None:
        self._send_alert = send_alert
        self._send_to_free = send_to_free
        self._openai = openai_evaluator
        self._poll_interval: float = poll_interval if poll_interval is not None else MACRO_WATCHDOG_POLL_INTERVAL
        self._watch_symbols: List[str] = watch_symbols or _DEFAULT_WATCH_SYMBOLS
        self._task: Optional[asyncio.Task] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._seen_headlines: Dict[str, float] = {}  # headline_hash → timestamp
        self._last_fg_value: Optional[int] = None    # track F&G changes
        # Cooldown tracker for BTC big-move alerts — keyed by direction
        # ("up" | "down") so a sustained large move alerts once per leg.
        self._btc_move_last_alert: Dict[str, float] = {}
        # Phase 2b — last observed 1h-EMA21 trend direction per symbol
        # ("UP" or "DOWN").  None until the first observation is made
        # (so the very first cycle does NOT alert — we need a baseline
        # before a flip is meaningful).
        self._regime_last_direction: Dict[str, Optional[str]] = {}
        # Per-symbol cooldown — absorbs chop when price oscillates around
        # EMA21.  Same `None` sentinel pattern as `_btc_move_last_alert`.
        self._regime_last_alert: Dict[str, float] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the background polling loop."""
        if not MACRO_WATCHDOG_ENABLED:
            log.info("MacroWatchdog disabled by configuration – skipping start")
            return
        if self._task is not None and not self._task.done():
            log.debug("MacroWatchdog already running")
            return
        self._task = asyncio.create_task(self._poll_loop(), name="macro_watchdog")
        log.info(
            "MacroWatchdog started (poll_interval={}s, symbols={})",
            self._poll_interval,
            self._watch_symbols,
        )

    async def stop(self) -> None:
        """Cancel the polling loop and close HTTP session."""
        if self._task is not None and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self._session is not None and not self._session.closed:
            await self._session.close()
            self._session = None
        log.info("MacroWatchdog stopped")

    # ------------------------------------------------------------------
    # Main polling loop
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Routing helper
    # ------------------------------------------------------------------

    async def _broadcast(self, msg: str, severity: str) -> None:
        """Send `msg` to admin and (when severity warrants) the free channel.

        Severity HIGH or CRITICAL → admin + free.  Anything else → admin only.
        Free-channel post errors are logged but never re-raised — admin alert
        already succeeded and we don't want a free-channel issue to silence
        future admin alerts in the same poll cycle.
        """
        await self._send_alert(msg)
        if (
            self._send_to_free is not None
            and severity in _FREE_CHANNEL_SEVERITIES
        ):
            try:
                await self._send_to_free(msg)
            except Exception as exc:
                log.warning(
                    "MacroWatchdog free-channel post failed (severity={}): {}",
                    severity, exc,
                )

    async def _poll_loop(self) -> None:
        """Infinite loop: poll events, send alerts, sleep."""
        while True:
            try:
                await self._check_macro_events()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                log.warning("MacroWatchdog poll error: {}", exc)
            await asyncio.sleep(self._poll_interval)

    # ------------------------------------------------------------------
    # Event detection
    # ------------------------------------------------------------------

    async def _check_macro_events(self) -> None:
        """Run one full polling cycle: Fear & Greed + BTC move + news headlines."""
        session = await self._get_session()

        # 1) Fear & Greed Index extremes
        await self._check_fear_greed(session)

        # 2) BTC big-move check (Phase-2 free-channel content)
        try:
            await self._check_btc_price_move(session)
        except Exception as exc:
            log.debug("BTC price-move check failed: {}", exc)

        # 2b) BTC/ETH 1h regime-shift check (Phase-2b free-channel content)
        if MACRO_REGIME_SHIFT_ENABLED:
            for sym in ("BTCUSDT", "ETHUSDT"):
                try:
                    await self._check_regime_shift(sym, session)
                except Exception as exc:
                    log.debug("Regime-shift check failed for {}: {}", sym, exc)

        # 3) News headlines for each watched symbol
        for symbol in self._watch_symbols:
            try:
                await self._check_news(symbol, session)
            except Exception as exc:
                log.debug("News check failed for {}: {}", symbol, exc)

    async def _check_btc_price_move(self, session: aiohttp.ClientSession) -> None:
        """Alert when BTC moves ≥ MACRO_BTC_MOVE_THRESHOLD_PCT% over the last hour.

        Why this exists: BTC is the bellwether for the entire crypto market.
        A 3%+ hourly move precedes correlated moves on alts and is the kind
        of context subscribers want — informational, not a trade signal.
        Routes to admin + free channel via :meth:`_broadcast`.

        Severity policy:
          • |move| in [threshold, 5%) → HIGH
          • |move| ≥ 5%               → CRITICAL

        Cooldown: per-direction.  An UP move alerting at T does not suppress
        a subsequent DOWN move alert (legitimate market reversals deserve
        their own announcement); but the same direction will not re-alert
        within ``MACRO_BTC_MOVE_COOLDOWN_SEC`` seconds (default 1 h).

        Data source: Binance public klines REST (no API key needed).  Pulls
        the last two 1h candles and computes close-to-close % change.
        """
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": "BTCUSDT", "interval": "1h", "limit": 2}
        try:
            async with session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.debug("BTC kline fetch returned status {}", resp.status)
                    return
                data = await resp.json()
        except (asyncio.TimeoutError, aiohttp.ClientError) as exc:
            log.debug("BTC kline fetch network error: {}", exc)
            return

        if not isinstance(data, list) or len(data) < 2:
            return
        try:
            prev_close = float(data[-2][4])
            curr_close = float(data[-1][4])
        except (IndexError, TypeError, ValueError) as exc:
            log.debug("BTC kline parse error: {}", exc)
            return
        if prev_close <= 0:
            return

        pct_change = (curr_close - prev_close) / prev_close * 100.0
        abs_change = abs(pct_change)
        if abs_change < MACRO_BTC_MOVE_THRESHOLD_PCT:
            return

        direction = "up" if pct_change > 0 else "down"
        cooldown_key = f"btc_move_{direction}"
        now = time.monotonic()
        last_time = self._btc_move_last_alert.get(cooldown_key)
        # `None` sentinel = "no prior alert in this direction" — must NOT be
        # treated as last_time=0.0 because in a fresh process `time.monotonic()`
        # returns a small value, which would falsely trip the cooldown check
        # `now - 0 < cooldown` on the first alert.
        if last_time is not None and now - last_time < MACRO_BTC_MOVE_COOLDOWN_SEC:
            return
        self._btc_move_last_alert[cooldown_key] = now

        severity = "CRITICAL" if abs_change >= 5.0 else "HIGH"
        emoji = "🚀" if pct_change > 0 else "📉"
        direction_label = "UP" if pct_change > 0 else "DOWN"

        msg = (
            f"{emoji} *BTC {direction_label} {abs_change:.2f}% in last hour*\n\n"
            f"*Prev close (1 h ago):* ${prev_close:,.2f}\n"
            f"*Current price:* ${curr_close:,.2f}\n"
            f"*Severity:* {severity}\n\n"
            f"_Major BTC moves typically lead the broader crypto market.  "
            f"Watch for correlated moves on altcoins; existing positions may "
            f"need attention._"
        )
        await self._broadcast(msg, severity)
        log.info(
            "MacroWatchdog: BTC price-move alert ({:+.2f}%, severity={})",
            pct_change, severity,
        )

    async def _check_regime_shift(
        self, symbol: str, session: aiohttp.ClientSession
    ) -> None:
        """Alert when BTC or ETH crosses its 1h EMA21 (trend-direction flip).

        Why: 1h EMA21 cross on BTC/ETH is a meaningful trend-context shift
        for scalpers — correlated alts shift bias along with the leader.
        This is informational context for free subscribers, not a trade
        signal.  Routes via :meth:`_broadcast` (HIGH severity → admin + free).

        Detection: fetch the last 22 1h candles, compute EMA21, classify
        ``UP`` if last close > EMA21 else ``DOWN``.  On the first observation
        for a symbol the direction is recorded silently (we need a baseline
        before a flip is meaningful).

        Cooldown: per-symbol ``MACRO_REGIME_SHIFT_COOLDOWN_SEC`` (default 4h)
        absorbs chop when price hovers around EMA21.  ``None`` sentinel
        avoids the ``time.monotonic() - 0`` false-cooldown bug that bit
        the BTC big-move alert pre-fix.
        """
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": "1h", "limit": 22}
        try:
            async with session.get(
                url,
                params=params,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    log.debug("{} kline fetch returned status {}", symbol, resp.status)
                    return
                data = await resp.json()
        except (asyncio.TimeoutError, aiohttp.ClientError) as exc:
            log.debug("{} kline fetch network error: {}", symbol, exc)
            return

        if not isinstance(data, list) or len(data) < 22:
            return
        try:
            closes = [float(row[4]) for row in data]
        except (IndexError, TypeError, ValueError) as exc:
            log.debug("{} kline parse error: {}", symbol, exc)
            return
        if any(c <= 0 for c in closes):
            return

        # Wilder-style EMA21 over the 22-candle window — a simple iterative
        # EMA is sufficient for a coarse trend-direction signal and avoids
        # importing numpy / src.indicators (keeps macro_watchdog standalone).
        period = 21
        alpha = 2.0 / (period + 1.0)
        ema_val = sum(closes[:period]) / period  # SMA seed
        for c in closes[period:]:
            ema_val = (c - ema_val) * alpha + ema_val
        last_close = closes[-1]
        new_direction = "UP" if last_close > ema_val else "DOWN"

        prev_direction = self._regime_last_direction.get(symbol)
        self._regime_last_direction[symbol] = new_direction
        if prev_direction is None:
            log.debug(
                "MacroWatchdog: regime baseline recorded for {} → {}",
                symbol, new_direction,
            )
            return
        if prev_direction == new_direction:
            return

        # Direction flipped — check cooldown
        now = time.monotonic()
        last_time = self._regime_last_alert.get(symbol)
        if last_time is not None and now - last_time < MACRO_REGIME_SHIFT_COOLDOWN_SEC:
            return
        self._regime_last_alert[symbol] = now

        emoji = "📈" if new_direction == "UP" else "📉"
        coin = symbol.replace("USDT", "")
        msg = (
            f"{emoji} *{coin} regime shift — {prev_direction} → {new_direction}*\n\n"
            f"*Symbol:* {symbol}\n"
            f"*Last close:* ${last_close:,.2f}\n"
            f"*1h EMA21:* ${ema_val:,.2f}\n"
            f"*Severity:* HIGH\n\n"
            f"_{coin} just crossed its 1h EMA21 — short-term trend bias has "
            f"flipped {new_direction.lower()}.  Correlated alts often follow "
            f"the leader; setups against the new bias face stronger headwind._"
        )
        await self._broadcast(msg, "HIGH")
        log.info(
            "MacroWatchdog: regime shift alert {} {} → {}",
            symbol, prev_direction, new_direction,
        )

    async def _check_fear_greed(self, session: aiohttp.ClientSession) -> None:
        """Alert when the Fear & Greed index hits extreme territory."""
        try:
            fg = await fetch_fear_greed_index(session)
        except Exception as exc:
            log.debug("Fear & Greed fetch failed in MacroWatchdog: {}", exc)
            return

        value: int = fg.get("value", 50)
        classification: str = fg.get("classification", "Neutral")

        # Only alert on meaningful changes (avoid repeating the same extreme value)
        prev = self._last_fg_value
        self._last_fg_value = value
        if prev is not None and abs(value - prev) < 5:
            return  # no significant change

        if value <= _FG_EXTREME_LOW:
            emoji = "😱"
            severity = "HIGH" if value <= 10 else "MEDIUM"
            msg = (
                f"{emoji} *Macro Alert – Extreme Fear*\n\n"
                f"*Fear & Greed Index:* {value} ({classification})\n"
                f"*Severity:* {severity}\n\n"
                "_Extreme fear often precedes capitulation events or short-squeeze "
                "bounces.  Review open positions and tighten stop losses._"
            )
            await self._broadcast(msg, severity)
            log.info("MacroWatchdog: Fear & Greed extreme fear alert (value={})", value)

        elif value >= _FG_EXTREME_HIGH:
            emoji = "🤑"
            severity = "HIGH" if value >= 90 else "MEDIUM"
            msg = (
                f"{emoji} *Macro Alert – Extreme Greed*\n\n"
                f"*Fear & Greed Index:* {value} ({classification})\n"
                f"*Severity:* {severity}\n\n"
                "_Extreme greed historically precedes sharp corrections.  "
                "Consider tightening trailing stops on long positions._"
            )
            await self._broadcast(msg, severity)
            log.info("MacroWatchdog: Fear & Greed extreme greed alert (value={})", value)

    async def _check_news(self, coin: str, session: aiohttp.ClientSession) -> None:
        """Fetch recent headlines for *coin* and evaluate via OpenAI if available."""
        result = await fetch_news_sentiment(coin, session)
        headline = result.summary.strip()
        if not headline:
            return

        # De-duplicate: skip if we've sent this headline recently
        h_hash = hashlib.sha256(headline.encode()).hexdigest()
        last_seen = self._seen_headlines.get(h_hash, 0.0)
        now = time.monotonic()
        if now - last_seen < _DEDUP_TTL:
            return
        self._seen_headlines[h_hash] = now
        self._prune_seen_headlines()

        # Try to classify via OpenAI
        macro_result: Optional[MacroEventResult] = None
        if self._openai is not None and self._openai.enabled:
            try:
                macro_result = await asyncio.wait_for(
                    self._openai.evaluate_macro_event(headline, event_type="NEWS"),
                    timeout=8.0,
                )
            except Exception as exc:
                log.debug("OpenAI macro eval failed for '{}': {}", headline[:60], exc)

        # If OpenAI says it's not significant (or is unavailable and score is neutral), skip
        if macro_result is not None and not macro_result.is_significant:
            log.debug("MacroWatchdog: non-significant news skipped – {}", headline[:60])
            return

        # Determine severity (fall back to sentiment-based heuristic when no OpenAI)
        if macro_result is not None:
            severity = macro_result.severity
            impact = macro_result.impact
            ai_summary = macro_result.summary
        else:
            # Simple heuristic: very bearish or bullish sentiment → MEDIUM alert
            if abs(result.score) < 0.5:
                return
            severity = "MEDIUM"
            impact = "Significant sentiment movement detected – monitor closely."
            ai_summary = headline

        emoji = _SEVERITY_EMOJI.get(severity, "🔔")
        direction_label = "📈 Bullish" if result.score > 0 else "📉 Bearish"

        msg = (
            f"{emoji} *Macro Alert – {coin} News*\n\n"
            f"*Headline:* {ai_summary}\n"
            f"*Sentiment:* {direction_label} ({result.score:+.2f})\n"
            f"*Severity:* {severity}\n"
        )
        if impact:
            msg += f"*Expected Impact:* {impact}\n"
        msg += "\n_This is an AI-generated macro alert.  No trade signal has been generated._"

        await self._broadcast(msg, severity)
        log.info(
            "MacroWatchdog: {} news alert ({}, score={:.2f})",
            coin, severity, result.score,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _prune_seen_headlines(self) -> None:
        """Remove stale deduplicated entries to prevent memory growth."""
        now = time.monotonic()
        stale = [k for k, ts in self._seen_headlines.items() if now - ts >= _DEDUP_TTL]
        for k in stale:
            self._seen_headlines.pop(k, None)
