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
    ALERTS_NEAR_LEVEL_COOLDOWN_SEC,
    ALERTS_PERSIST_PATH,
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
    ) -> None:
        self._data_store = data_store
        self._level_book_getter = level_book_getter
        self._symbols_getter = symbols_getter
        self._on_alert = on_alert
        self._persist_path = Path(persist_path)
        self._alerts: Deque[Alert] = deque(maxlen=ALERTS_BUFFER_MAX)
        # (symbol, alert_type, timeframe) -> wall-clock ts of last fire
        self._last_fired: Dict[str, float] = {}
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
        try:
            symbols = list(self._symbols_getter() or [])
        except Exception:
            log.exception("alerts: symbols_getter failed")
            return []
        fired: List[Alert] = []
        for i, symbol in enumerate(symbols):
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
        return [a for a in out if self._passes_cooldown(a)]

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

    def _passes_cooldown(self, alert: Alert) -> bool:
        key = f"{alert.symbol}|{alert.alert_type}|{alert.timeframe}"
        now = time.time()
        last = self._last_fired.get(key, 0.0)
        if now - last < _cooldown_seconds(alert.alert_type, alert.timeframe):
            return False
        self._last_fired[key] = now
        self._dirty = True
        return True

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
        if self._on_alert is not None:
            try:
                self._on_alert(alert)
            except Exception:
                log.exception("alerts: on_alert callback failed (non-fatal)")

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
            for raw in reversed(data.get("alerts", [])):
                alert = Alert.from_dict(raw)
                if alert is not None:
                    self._alerts.appendleft(alert)
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
