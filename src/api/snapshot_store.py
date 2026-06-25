"""Redis key schema and serialisation helpers for API/engine process isolation.

When ``API_PROCESS_ISOLATED=true`` the engine publishes pre-computed snapshots
to these keys after each scan cycle; the ``api`` container reads them without
touching engine memory, eliminating the shared-event-loop bottleneck that caused
5-10 s timeouts on settings writes and stale-data on tab loads.

Key lifetime contract
─────────────────────
* Writer interval → TTL is 2× that interval so one missed write never evicts
  a warm cache — the API serves the last good snapshot rather than 503-ing.
* All values are plain JSON strings (``json.dumps``) so they stay
  human-inspectable via ``redis-cli GET snapshot:signals_all | python3 -m json.tool``.
"""
from __future__ import annotations

import json
from typing import Any, Optional

from src.utils import get_logger

log = get_logger("api.snapshot_store")

# ── Redis keys ─────────────────────────────────────────────────────────────
KEY_SIGNALS_ALL    = "snapshot:signals_all"    # List[SignalDetail dict]  — written every ~15 s
KEY_ACTIVITY_ALL   = "snapshot:activity_all"   # List[ActivityEvent dict] — written every ~30 s
KEY_AGENTS_ALL     = "snapshot:agents_all"     # List[AgentStat dict]     — written every ~60 s
KEY_TICKERS        = "snapshot:tickers"        # List[TickerItem dict]    — written every ~15 s
KEY_ENGINE_STATE   = "snapshot:engine_state"   # engine state dict        — written every ~15 s
KEY_POSITIONS_DIAG = "snapshot:positions_diag"  # PositionsDiagResponse    — written every ~15 s
KEY_CMD_SET_MODE   = "snapshot:cmd:set_mode"   # str "off|paper|live"     — consumed once
KEY_CMD_RESET_SIGNALS = "snapshot:cmd:reset_signals"  # set to "1" by API; consumed once by engine
TTL_CMD_RESET = 120  # 2-min TTL — engine consumes before this; if engine is down, client must retry

# ── TTLs (seconds) — 2× the write interval ────────────────────────────────
TTL_SIGNALS      = 60
TTL_ACTIVITY     = 120
TTL_AGENTS       = 180
TTL_TICKERS      = 60
TTL_ENGINE_STATE = 60
TTL_POSITIONS_DIAG = 60
TTL_CMD          = 60  # command expires if engine is down; client must retry


def encode(data: Any) -> str:
    """Serialise *data* to a compact JSON string.  ``datetime`` and similar
    non-JSON types are coerced to their ``str`` representation."""
    return json.dumps(data, default=str)


def decode(raw: Optional[str]) -> Optional[Any]:
    """Deserialise a JSON string.  Returns ``None`` on missing / corrupt data
    rather than raising so callers can fall back to a live build gracefully."""
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except Exception:
        log.warning("snapshot_store.decode: corrupt JSON payload — returning None")
        return None
