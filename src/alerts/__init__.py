"""Market Alerts — 100eyes-class informational detector events.

Single-condition, non-directional market observations (RSI extremes,
RSI divergence, abnormal volatility, near horizontal S/R, volume
anomaly) surfaced in the Lumin app's Pulse → Alerts tab and pushed
via FCM.  Entirely off the money path: nothing in scoring, dispatch,
the FSM, or paid-channel routing reads alert state.
"""

from .models import Alert, AlertType
from .service import AlertService

__all__ = ["Alert", "AlertType", "AlertService"]
