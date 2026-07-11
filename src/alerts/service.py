"""AlertService — sweeps the pair universe for detector events.

Runs as its own asyncio task (launched from ``bootstrap.launch_runtime_tasks``)
so it can never slow the scanner hot path.  Reads only in-memory candle
arrays and the scanner's LevelBook — a full sweep performs zero network
or Firestore I/O (Cost Discipline: nothing new on any hot loop).

Refire control is a per ``(symbol, type, timeframe)`` cooldown persisted to
``data/alerts.json`` together with the recent feed, so a deploy restart
neither drops the feed nor re-pushes every condition that is still true.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections import deque
from pathlib import Path
from typing import Any, Callable, Deque, Dict, List, Optional

from config import (
    ALERTS_BUFFER_MAX,
    ALERTS_COOLDOWN_TF_MULT,
    ALERTS_EVAL_INTERVAL_SEC,
    ALERTS_MIN_VOLUME_24H_USD,
    ALERTS_NEAR_LEVEL_COOLDOWN_SEC,
    ALERTS_PERSIST_PATH,
    ALERTS_PUSH_MAX_PER_HOUR,
    ALERTS_PUSH_TIMEFRAMES,
    ALERTS_SYMBOL_MAX_PER_WINDOW,
    ALERTS_SYMBOL_WINDOW_SEC,
    ALERTS_VOLATILITY_COOLDOWN_SEC,
    ALERTS_VOLUME_COOLDOWN_SEC,
)
from src.utils import get_logger

from . import detectors
from .models import TF_SECONDS, Alert, AlertType

log = get_logger("alerts")

#: If a timeframe's most-recent kline is older than this many timeframe
#: periods, the feed for that (symbol, tf) is considered dead and its
#: detectors are skipped — never alert off frozen data (S44/S49 class).
_STALE_TF_PERIODS = 3.0

#: Persist at most this often (seconds) — the feed is a convenience, not
#: a ledger; losing a few seconds of it on a crash is acceptable.
_PERSIST_MIN_INTERVAL_S = 10.0

#: Information-value order used when a symbol's per-window budget binds:
#: structural observations (divergence, S/R) beat state observations
#: (RSI extreme) beat single-candle event echoes (volume, volatility).
_TYPE_PRIORITY: Dict[str, int] = {
    AlertType.RSI_BULLISH_DIVERGENCE.value: 0,
    AlertType.RSI_BEARISH_DIVERGENCE.value: 0,
    AlertType.NEAR_SUPPORT.value: 1,
    AlertType.NEAR_RESISTANCE.value: 1,
    AlertType.RSI_OVERBOUGHT.value: 2,
    AlertType.RSI_OVERSOLD.value: 2,
    AlertType.VOLUME_SPIKE.value: 3,
    AlertType.ABNORMAL_VOLATILITY.value: 4,
}

#: Timeframe rank so a 4h observation outranks the same type on 15m when
#: the symbol budget binds.
_TF_RANK: Dict[str, int] = {"4h": 0, "1h": 1, "15m": 2}


def _cooldown_seconds(alert_type: str, timeframe: str) -> float:
    """Refire cooldown for one (type, timeframe).

    Timeframe-relative for candle-shape detectors (an RSI-extreme on 4h
    stays true across many 4h candles — refire only after
    ``ALERTS_COOLDOWN_TF_MULT`` periods); wall-clock for the hover-prone
    types (near-level, volatility, volume).
    """
    if alert_type in (AlertType.NEAR_SUPPORT.value, AlertType.NEAR_RESISTANCE.value):
        return float(ALERTS_NEAR_LEVEL_COOLDOWN_SEC)
    if alert_type == AlertType.ABNORMAL_VOLATILITY.value:
        return float(ALERTS_VOLATILITY_COOLDOWN_SEC)
    if alert_type == AlertType.VOLUME_SPIKE.value:
        return float(ALERTS_VOLUME_COOLDOWN_SEC)
    tf_sec = TF_SECONDS.get(timeframe, 3600)
    return ALERTS_COOLDOWN_TF_MULT * tf_sec


class AlertService:
    """Detector sweep + feed buffer + persistence + push fan-out."""

    def __init__(
        self,
        data_store: Any,
        level_book_getter: Callable[[], Any],
        symbols_getter: Callable[[], List[str]],
        on_alert: Optional[Callable[[Alert], Any]] = None,
        persist_path: str = ALERTS_PERSIST_PATH,
        volume_24h_getter: Optional[Callable[[str], Optional[float]]] = None,
    ) -> None:
        self._data_store = data_store
        self._level_book_getter = level_book_getter
        self._symbols_getter = symbols_getter
        self._on_alert = on_alert
        self._volume_24h_getter = volume_24h_getter
        # The restored feed may hold alerts for symbols the universe gate
        # now excludes.  Volume data isn't available until the boot
        # refresh_pairs(), so the purge runs lazily on the first sweep.
        self._restored_feed_purged = False
        self._persist_path = Path(persist_path)
        self._alerts: Deque[Alert] = deque(maxlen=ALERTS_BUFFER_MAX)
        # (symbol, alert_type, timeframe) -> wall-clock ts of last fire
        self._last_fired: Dict[str, float] = {}
        # symbol -> recent fire timestamps (per-symbol cross-type budget).
        # In-memory only: the window is short-lived, so a restart resetting
        # it costs at most one extra alert per symbol.
        self._symbol_fires: Dict[str, Deque[float]] = {}
        # Push-side sliding window (wall-clock ts of alerts we pushed).
        self._push_times: Deque[float] = deque()
        # (symbol, timeframe) -> last kline-update ts already evaluated,
        # so each closed candle is judged exactly once.
        self._last_eval_ts: Dict[str, float] = {}
        self._last_persist: float = 0.0
        self._dirty = False
        self._load()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        log.info(
            "AlertService started — sweeping every {}s (buffer={})",
            ALERTS_EVAL_INTERVAL_SEC, ALERTS_BUFFER_MAX,
        )
        while True:
            await asyncio.sleep(ALERTS_EVAL_INTERVAL_SEC)
            try:
                await self.sweep()
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("alert sweep failed — next interval retries")

    async def sweep(self) -> List[Alert]:
        """One pass over the universe.  Returns the alerts fired this pass."""
        self._purge_restored_feed_once()
        try:
            symbols = list(self._symbols_getter() or [])
        except Exception:
            log.exception("alerts: symbols_getter failed")
            return []
        fired: List[Alert] = []
        for i, symbol in enumerate(symbols):
            if not self._universe_ok(symbol):
                continue
            try:
                fired.extend(self._evaluate_symbol(symbol))
            except Exception:
                log.exception("alerts: evaluation failed for {}", symbol)
            if i % 10 == 9:
                await asyncio.sleep(0)  # yield — never hog the loop
        for alert in fired:
            self._publish(alert)
        if fired or self._dirty:
            await self._persist_maybe()
        return fired

    def _universe_ok(self, symbol: str) -> bool:
        """Universe gate: alerts only for liquid pairs (majors + midcaps).

        Fail-closed on unknown volume — volume is only missing before the
        boot ``refresh_pairs()`` (fatal on failure), and sweeps start after
        it; the cost of a wrong skip is one missed informational card."""
        if self._volume_24h_getter is None or ALERTS_MIN_VOLUME_24H_USD <= 0:
            return True
        try:
            vol = self._volume_24h_getter(symbol)
        except Exception:
            return False
        return vol is not None and vol >= ALERTS_MIN_VOLUME_24H_USD

    def _purge_restored_feed_once(self) -> None:
        """Drop restored-feed alerts for symbols the universe gate now
        excludes.  Runs on the first sweep (not in ``_load``) because the
        PairManager has no volume data until the boot refresh."""
        if self._restored_feed_purged:
            return
        self._restored_feed_purged = True
        if self._volume_24h_getter is None or ALERTS_MIN_VOLUME_24H_USD <= 0:
            return
        kept = [a for a in self._alerts if self._universe_ok(a.symbol)]
        dropped = len(self._alerts) - len(kept)
        if dropped:
            # deque iterates newest-first; rebuilding from the kept list
            # preserves that order (index 0 stays the newest alert).
            self._alerts = deque(kept, maxlen=ALERTS_BUFFER_MAX)
            self._dirty = True
            log.info(
                "alerts: purged {} restored alerts below the "
                "{:.0f} USD 24h-volume universe gate",
                dropped, ALERTS_MIN_VOLUME_24H_USD,
            )

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def _evaluate_symbol(self, symbol: str) -> List[Alert]:
        out: List[Alert] = []
        for tf in detectors.RSI_EXTREME_TIMEFRAMES:
            candles = self._fresh_candles(symbol, tf)
            if candles is None:
                continue
            out.extend(self._run_tf_detectors(symbol, tf, candles))
        out = self._coalesce_same_candle(out)
        # Priority order BEFORE cooldown + budget, so when the symbol's
        # window budget binds it's the low-information types that drop.
        out.sort(
            key=lambda a: (
                _TYPE_PRIORITY.get(a.alert_type, 9),
                _TF_RANK.get(a.timeframe, 9),
            )
        )
        kept: List[Alert] = []
        for a in out:
            # Both gates are checked BEFORE either is stamped, so a
            # budget rejection can't consume the type cooldown (which
            # would silently mute the alert for the whole cooldown).
            if not self._cooldown_ok(a) or not self._symbol_budget_ok(a):
                continue
            self._stamp_fire(a)
            kept.append(a)
        return kept

    @staticmethod
    def _coalesce_same_candle(found: List[Alert]) -> List[Alert]:
        """A volume spike and an abnormal-volatility alert fired by the
        same candle are one market event, not two — the volume card
        already carries the move %.  Keep volume, drop volatility."""
        has_volume = {
            (a.symbol, a.timeframe)
            for a in found
            if a.alert_type == AlertType.VOLUME_SPIKE.value
        }
        return [
            a for a in found
            if not (
                a.alert_type == AlertType.ABNORMAL_VOLATILITY.value
                and (a.symbol, a.timeframe) in has_volume
            )
        ]

    def _run_tf_detectors(self, symbol: str, tf: str, candles: dict) -> List[Alert]:
        found: List[Alert] = []
        alert = detectors.detect_rsi_extreme(symbol, tf, candles)
        if alert:
            found.append(alert)
        if tf in detectors.DIVERGENCE_TIMEFRAMES:
            alert = detectors.detect_rsi_divergence(symbol, tf, candles)
            if alert:
                found.append(alert)
        if tf == detectors.VOLATILITY_TIMEFRAME:
            alert = detectors.detect_abnormal_volatility(symbol, tf, candles)
            if alert:
                found.append(alert)
        if tf == detectors.VOLUME_TIMEFRAME:
            alert = detectors.detect_volume_spike(symbol, tf, candles)
            if alert:
                found.append(alert)
        if tf == detectors.NEAR_LEVEL_TIMEFRAME:
            try:
                book = self._level_book_getter()
            except Exception:
                book = None
            alert = detectors.detect_near_level(symbol, tf, candles, book)
            if alert:
                found.append(alert)
        return found

    def _fresh_candles(self, symbol: str, tf: str) -> Optional[dict]:
        """Candles for (symbol, tf) — but only when a new CLOSED candle has
        arrived since the last evaluation, and the feed isn't frozen."""
        candles = self._data_store.get_candles(symbol, tf)
        if not candles:
            return None
        age = None
        try:
            age = self._data_store.last_kline_age_seconds(symbol, tf)
        except Exception:
            pass
        tf_sec = TF_SECONDS.get(tf, 3600)
        if age is not None:
            if age > _STALE_TF_PERIODS * tf_sec:
                return None  # dead feed — never alert on frozen data
            update_ts = time.time() - age
            key = f"{symbol}|{tf}"
            if update_ts - self._last_eval_ts.get(key, 0.0) < 1.0:
                return None  # same closed candle we already judged
            self._last_eval_ts[key] = update_ts
        return candles

    def _cooldown_ok(self, alert: Alert) -> bool:
        key = f"{alert.symbol}|{alert.alert_type}|{alert.timeframe}"
        last = self._last_fired.get(key, 0.0)
        return time.time() - last >= _cooldown_seconds(
            alert.alert_type, alert.timeframe
        )

    def _symbol_budget_ok(self, alert: Alert) -> bool:
        """Cross-type per-symbol budget: at most
        ``ALERTS_SYMBOL_MAX_PER_WINDOW`` alerts per symbol per rolling
        ``ALERTS_SYMBOL_WINDOW_SEC`` — one violent candle must not turn
        into a card stack for the same coin."""
        now = time.time()
        fires = self._symbol_fires.setdefault(alert.symbol, deque())
        while fires and now - fires[0] > ALERTS_SYMBOL_WINDOW_SEC:
            fires.popleft()
        return len(fires) < ALERTS_SYMBOL_MAX_PER_WINDOW

    def _stamp_fire(self, alert: Alert) -> None:
        now = time.time()
        self._last_fired[
            f"{alert.symbol}|{alert.alert_type}|{alert.timeframe}"
        ] = now
        self._symbol_fires.setdefault(alert.symbol, deque()).append(now)
        self._dirty = True

    # ------------------------------------------------------------------
    # Publish + read side
    # ------------------------------------------------------------------

    def _publish(self, alert: Alert) -> None:
        self._alerts.appendleft(alert)
        self._dirty = True
        log.info(
            "ALERT {} {} ({}) — {}",
            alert.symbol, alert.alert_type, alert.timeframe, alert.message,
        )
        if self._on_alert is not None and self._should_push(alert):
            try:
                self._on_alert(alert)
            except Exception:
                log.exception("alerts: on_alert callback failed (non-fatal)")

    def _should_push(self, alert: Alert) -> bool:
        """Push curation: the feed takes every published alert, the phone
        only buzzes for higher-timeframe observations, inside an hourly
        budget.  A dropped push is invisible spam-prevention, not a lost
        alert — the card is still in the feed."""
        allowed = {
            tf.strip() for tf in ALERTS_PUSH_TIMEFRAMES.split(",") if tf.strip()
        }
        if allowed and alert.timeframe not in allowed:
            return False
        now = time.time()
        while self._push_times and now - self._push_times[0] > 3600.0:
            self._push_times.popleft()
        if len(self._push_times) >= ALERTS_PUSH_MAX_PER_HOUR:
            log.debug(
                "alerts: push budget ({}h⁻¹) exhausted — feed-only for {}",
                ALERTS_PUSH_MAX_PER_HOUR, alert.symbol,
            )
            return False
        self._push_times.append(now)
        return True

    def recent(
        self,
        limit: int = 100,
        alert_type: Optional[str] = None,
        symbol: Optional[str] = None,
    ) -> List[dict]:
        """Newest-first feed slice as JSON-ready dicts."""
        out: List[dict] = []
        for alert in self._alerts:
            if alert_type and alert.alert_type != alert_type:
                continue
            if symbol and alert.symbol != symbol.upper():
                continue
            out.append(alert.to_dict())
            if len(out) >= limit:
                break
        return out

    # ------------------------------------------------------------------
    # Persistence — best-effort, throttled, never raises
    # ------------------------------------------------------------------

    def _load(self) -> None:
        try:
            if not self._persist_path.exists():
                return
            data = json.loads(self._persist_path.read_text())
            near_types = {AlertType.NEAR_SUPPORT.value, AlertType.NEAR_RESISTANCE.value}
            dropped_junk = 0
            for raw in reversed(data.get("alerts", [])):
                alert = Alert.from_dict(raw)
                if alert is None:
                    continue
                # Pre-v3 near-level alerts (no distinct-touch geometry) are
                # the "523 touches" junk cohort — drop them so the feed
                # cleans on the first post-deploy restart.
                if (
                    alert.alert_type in near_types
                    and "touch_count" not in (alert.metrics or {})
                ):
                    dropped_junk += 1
                    continue
                self._alerts.appendleft(alert)
            if dropped_junk:
                self._dirty = True  # rewrite the file without the junk
                log.info(
                    "alerts: dropped {} pre-v3 near-level alerts from the "
                    "restored feed (no distinct-touch geometry)", dropped_junk,
                )
            fired = data.get("last_fired", {})
            if isinstance(fired, dict):
                self._last_fired = {
                    str(k): float(v) for k, v in fired.items()
                    if isinstance(v, (int, float))
                }
            log.info(
                "alerts: restored {} alerts + {} cooldown entries from {}",
                len(self._alerts), len(self._last_fired), self._persist_path,
            )
        except Exception:
            log.exception("alerts: persistence load failed — starting empty")

    async def _persist_maybe(self) -> None:
        now = time.monotonic()
        if now - self._last_persist < _PERSIST_MIN_INTERVAL_S:
            return
        self._last_persist = now
        self._dirty = False
        payload = {
            "alerts": [a.to_dict() for a in self._alerts],
            "last_fired": self._last_fired,
        }
        try:
            await asyncio.to_thread(self._write_atomic, payload)
        except Exception:
            log.exception("alerts: persistence write failed (non-fatal)")

    def _write_atomic(self, payload: dict) -> None:
        self._persist_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._persist_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload))
        tmp.replace(self._persist_path)
