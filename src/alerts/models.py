"""Alert dataclass + type taxonomy for the Pulse → Alerts feed."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class AlertType(str, Enum):
    """Detector taxonomy.  Values are wire-format strings consumed by the
    Lumin app (icon/colour mapping) — renaming one is an app-visible
    breaking change, treat like an API field rename."""

    RSI_OVERBOUGHT = "RSI_OVERBOUGHT"
    RSI_OVERSOLD = "RSI_OVERSOLD"
    RSI_BULLISH_DIVERGENCE = "RSI_BULLISH_DIVERGENCE"
    RSI_BEARISH_DIVERGENCE = "RSI_BEARISH_DIVERGENCE"
    ABNORMAL_VOLATILITY = "ABNORMAL_VOLATILITY"
    VOLUME_SPIKE = "VOLUME_SPIKE"
    NEAR_SUPPORT = "NEAR_SUPPORT"
    NEAR_RESISTANCE = "NEAR_RESISTANCE"


#: Human titles, mirroring 100eyes' card headings.
ALERT_TITLES: Dict[AlertType, str] = {
    AlertType.RSI_OVERBOUGHT: "RSI Extremely Overbought",
    AlertType.RSI_OVERSOLD: "RSI Extremely Oversold",
    AlertType.RSI_BULLISH_DIVERGENCE: "RSI Bullish Divergence",
    AlertType.RSI_BEARISH_DIVERGENCE: "RSI Bearish Divergence",
    AlertType.ABNORMAL_VOLATILITY: "Abnormal Volatility",
    AlertType.VOLUME_SPIKE: "Abnormal Volume",
    AlertType.NEAR_SUPPORT: "Near Horizontal Support",
    AlertType.NEAR_RESISTANCE: "Near Horizontal Resistance",
}

#: Directional lean of the observation (display only — alerts are
#: informational, never trade directives).
ALERT_BIAS: Dict[AlertType, str] = {
    AlertType.RSI_OVERBOUGHT: "BEARISH",
    AlertType.RSI_OVERSOLD: "BULLISH",
    AlertType.RSI_BULLISH_DIVERGENCE: "BULLISH",
    AlertType.RSI_BEARISH_DIVERGENCE: "BEARISH",
    AlertType.ABNORMAL_VOLATILITY: "NEUTRAL",
    AlertType.VOLUME_SPIKE: "NEUTRAL",
    AlertType.NEAR_SUPPORT: "BULLISH",
    AlertType.NEAR_RESISTANCE: "BEARISH",
}

#: Seconds per supported alert timeframe (cooldown arithmetic).
TF_SECONDS: Dict[str, int] = {
    "15m": 15 * 60,
    "1h": 60 * 60,
    "4h": 4 * 60 * 60,
}


@dataclass
class Alert:
    """One fired detector event, exactly as served by ``/api/alerts``."""

    alert_type: str
    symbol: str
    timeframe: str
    price: float
    title: str
    message: str
    bias: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    alert_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["Alert"]:
        try:
            known = {f for f in cls.__dataclass_fields__}
            return cls(**{k: v for k, v in data.items() if k in known})
        except Exception:
            return None


def make_alert(
    alert_type: AlertType,
    symbol: str,
    timeframe: str,
    price: float,
    message: str,
    metrics: Optional[Dict[str, Any]] = None,
) -> Alert:
    return Alert(
        alert_type=alert_type.value,
        symbol=symbol,
        timeframe=timeframe,
        price=float(price),
        title=ALERT_TITLES[alert_type],
        message=message,
        bias=ALERT_BIAS[alert_type],
        metrics=metrics or {},
    )
