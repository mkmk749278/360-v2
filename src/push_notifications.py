"""FCM push notifications — topic-based, fire-and-forget, never blocking.

Design contract (production, phones behind this):

* **Topics, not tokens.**  The Lumin app subscribes client-side to the
  ``alerts`` and ``signals`` FCM topics; the engine addresses topics only,
  so there is no server-side device-token registry to store, sync, or leak.
  A user muting a class = client-side unsubscribe.
* **Never on the hot path.**  Callers get a synchronous, instantly-returning
  function that schedules the blocking ``messaging.send`` on a worker
  thread.  A push can be dropped; a scan/dispatch cycle can never stall.
* **Never raises.**  Any failure (Firebase not initialised, network,
  quota) logs and drops the push — signal delivery and alert publication
  do not depend on FCM health.
* **Rate-guarded.**  A global sliding-window cap
  (``FCM_MAX_SENDS_PER_MIN``) makes phone-spam from a pathological loop
  structurally impossible.

Firebase Admin is initialised at boot by ``src.api.firebase_auth`` (same
service account as Phone Auth).  When that init didn't happen (env vars
unset, tests) this module quietly no-ops.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections import deque
from typing import Any, Deque, Dict, Optional

from config import (
    FCM_ALERTS_TOPIC,
    FCM_MAX_SENDS_PER_MIN,
    FCM_PUSH_ALERTS_ENABLED,
    FCM_PUSH_ENABLED,
    FCM_PUSH_OUTCOMES_ENABLED,
    FCM_PUSH_SIGNALS_ENABLED,
    FCM_SIGNALS_TOPIC,
)
from src.utils import get_logger

log = get_logger("push")

#: Android notification channels — must match the ids the Lumin app
#: registers in its NotificationService.
_CHANNEL_ALERTS = "market_alerts"
_CHANNEL_SIGNALS = "signals"

_send_times: Deque[float] = deque()
_send_lock = threading.Lock()

#: Re-probe Firebase availability at most this often once found missing,
#: so a mis-deployed engine doesn't pay an import/probe on every signal.
_UNAVAILABLE_RECHECK_S = 300.0
_unavailable_until = 0.0


def _firebase_ready() -> bool:
    """True when firebase_admin has an initialised default app."""
    global _unavailable_until
    if time.monotonic() < _unavailable_until:
        return False
    try:
        import firebase_admin  # type: ignore[import-not-found]

        if firebase_admin._apps:
            return True
    except Exception:
        pass
    _unavailable_until = time.monotonic() + _UNAVAILABLE_RECHECK_S
    log.warning(
        "push: Firebase Admin not initialised — FCM pushes disabled for {}s",
        int(_UNAVAILABLE_RECHECK_S),
    )
    return False


def _rate_ok() -> bool:
    now = time.time()
    with _send_lock:
        while _send_times and now - _send_times[0] > 60.0:
            _send_times.popleft()
        if len(_send_times) >= FCM_MAX_SENDS_PER_MIN:
            return False
        _send_times.append(now)
    return True


def _send_blocking(topic: str, title: str, body: str, data: Dict[str, str], channel_id: str) -> None:
    """Runs on a worker thread — the only place that touches the network."""
    from firebase_admin import messaging  # type: ignore[import-not-found]

    message = messaging.Message(
        topic=topic,
        notification=messaging.Notification(title=title, body=body),
        data=data,
        android=messaging.AndroidConfig(
            priority="high",
            notification=messaging.AndroidNotification(
                channel_id=channel_id,
                # Collapse per symbol+class so a burst edits one shade entry
                # instead of stacking ten.
                tag=data.get("collapse_tag") or None,
            ),
        ),
    )
    message_id = messaging.send(message)
    log.debug("push: sent {} → topic={} id={}", title, topic, message_id)


def _dispatch(topic: str, title: str, body: str, data: Dict[str, str], channel_id: str) -> None:
    """Schedule a push without ever blocking or raising in the caller."""
    if not FCM_PUSH_ENABLED:
        return
    if not _firebase_ready():
        return
    if not _rate_ok():
        log.warning("push: rate cap {}per-min hit — dropping '{}'", FCM_MAX_SENDS_PER_MIN, title)
        return
    # Data payload values must be strings on the FCM wire.
    data = {k: str(v) for k, v in data.items()}

    async def _run() -> None:
        try:
            await asyncio.to_thread(_send_blocking, topic, title, body, data, channel_id)
        except Exception as exc:
            log.warning("push: send failed for '{}': {}", title, exc)

    try:
        asyncio.get_running_loop().create_task(_run())
    except RuntimeError:
        # No running loop (sync caller / tests) — send inline; the contract
        # of never raising still holds.
        try:
            _send_blocking(topic, title, body, data, channel_id)
        except Exception as exc:
            log.warning("push: sync send failed for '{}': {}", title, exc)


# ---------------------------------------------------------------------------
# Push classes
# ---------------------------------------------------------------------------


def push_alert(alert: Any) -> None:
    """Market alert (Pulse → Alerts feed) — e.g. '[BTCUSDT] RSI Extremely
    Overbought (1h)', mirroring the 100eyes card format."""
    if not FCM_PUSH_ALERTS_ENABLED:
        return
    title = f"[{alert.symbol}] {alert.title} ({alert.timeframe})"
    _dispatch(
        FCM_ALERTS_TOPIC,
        title,
        alert.message,
        {
            "kind": "alert",
            "alert_type": alert.alert_type,
            "symbol": alert.symbol,
            "timeframe": alert.timeframe,
            "route": "pulse_alerts",
            "collapse_tag": f"alert:{alert.symbol}:{alert.alert_type}",
        },
        _CHANNEL_ALERTS,
    )


def push_signal_published(signal: Any) -> None:
    """New paid signal went live (post-delivery hook in SignalRouter)."""
    if not FCM_PUSH_SIGNALS_ENABLED:
        return
    direction = getattr(signal.direction, "value", str(signal.direction))
    title = f"New Signal: {direction} {signal.symbol}"
    body = (
        f"Entry {signal.entry:g} · SL {signal.stop_loss:g} · TP1 {signal.tp1:g}"
        f" · Confidence {signal.confidence:.0f}"
    )
    _dispatch(
        FCM_SIGNALS_TOPIC,
        title,
        body,
        {
            "kind": "signal",
            "signal_id": getattr(signal, "signal_id", "") or "",
            "symbol": signal.symbol,
            "direction": direction,
            "route": "signals",
            "collapse_tag": f"signal:{getattr(signal, 'signal_id', signal.symbol)}",
        },
        _CHANNEL_SIGNALS,
    )


def push_signal_outcome(signal: Any, outcome_label: Optional[str] = None) -> None:
    """A signal reached a terminal outcome (TP/SL/expiry/invalidations).

    ``outcome_label`` overrides ``signal.status`` because not every close
    path in TradeMonitor stamps ``status`` before recording the outcome.
    """
    if not FCM_PUSH_OUTCOMES_ENABLED:
        return
    direction = getattr(signal.direction, "value", str(signal.direction))
    status = (outcome_label or getattr(signal, "status", "") or "CLOSED").replace("_", " ")
    pnl = float(getattr(signal, "pnl_pct", 0.0) or 0.0)
    title = f"{signal.symbol} {direction} closed — {status}"
    body = f"Result: {pnl:+.2f}%"
    _dispatch(
        FCM_SIGNALS_TOPIC,
        title,
        body,
        {
            "kind": "signal_outcome",
            "signal_id": getattr(signal, "signal_id", "") or "",
            "symbol": signal.symbol,
            "status": outcome_label or getattr(signal, "status", "") or "",
            "pnl_pct": f"{pnl:.2f}",
            "route": "signals",
            "collapse_tag": f"signal:{getattr(signal, 'signal_id', signal.symbol)}",
        },
        _CHANNEL_SIGNALS,
    )


def _reset_rate_window_for_tests() -> None:
    global _unavailable_until
    with _send_lock:
        _send_times.clear()
    _unavailable_until = 0.0
