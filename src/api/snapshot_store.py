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
KEY_ALERTS         = "snapshot:alerts"         # List[Alert dict]         — written every ~30 s
KEY_DATA_INTAKE    = "snapshot:data_intake"    # data-intake X-ray         — written every ~15 s
KEY_ROUTER_DELIVERY = "snapshot:router_delivery"  # router drop census     — written every ~15 s
KEY_TRAIL_GOVERNOR = "snapshot:trail_governor"  # live trail-governor X-ray — written every ~15 s
KEY_DARK_PROMOTION = "snapshot:dark_promotion"  # promotion decide-counters — written every ~15 s
KEY_CMD_SET_MODE   = "snapshot:cmd:set_mode"   # str "off|paper|live"     — consumed once
KEY_CMD_RESET_SIGNALS = "snapshot:cmd:reset_signals"  # set to "1" by API; consumed once by engine
TTL_CMD_RESET = 120  # 2-min TTL — engine consumes before this; if engine is down, client must retry
# Owner-initiated purge of the SAR exit shadow ledger.  Same fire-and-forget
# shape as the reset command: the engine container owns the in-memory buffer,
# so the API container must not clear the file underneath it — the engine would
# simply persist its buffer back over the top on the next save.
KEY_CMD_CLEAR_SAR_LEDGER = "snapshot:cmd:clear_sar_ledger"

# ── Manual-take command channel (owner-approved 2026-07-17) ────────────────
# Unlike the two single-value command keys above, a manual take carries a
# per-user payload and multiple users can take concurrently — so this one is
# a Redis LIST used as a queue: the API container LPUSHes a JSON envelope
# {request_id, uid, signal_id, ts}; the engine's ManualTakeConsumer drains it
# with BRPOP (FIFO) and writes the outcome to KEY_TAKE_RESULT_PREFIX +
# request_id, which the API polls to answer the user's request synchronously.
# The queue itself carries no TTL (BRPOP consumes near-instantly; a dead
# engine leaves entries that the consumer drains on restart and rejects as
# stale via the envelope ``ts``), the result keys expire on their own.
KEY_CMD_TAKE = "snapshot:cmd:take"                # Redis LIST of JSON envelopes
KEY_TAKE_RESULT_PREFIX = "snapshot:take_result:"  # + request_id → JSON outcome
TTL_TAKE_RESULT = 120   # result outlives the API's ~8s poll window comfortably
TAKE_CMD_STALE_S = 60   # engine rejects queue entries older than this

# ── TTLs (seconds) — 2× the write interval ────────────────────────────────
TTL_SIGNALS      = 60
TTL_ACTIVITY     = 120
TTL_AGENTS       = 180
TTL_TICKERS      = 60
TTL_ENGINE_STATE = 60
TTL_POSITIONS_DIAG = 60
TTL_DATA_INTAKE  = 60
TTL_ROUTER_DELIVERY = 60
TTL_TRAIL_GOVERNOR  = 60
TTL_DARK_PROMOTION  = 60
TTL_ALERTS       = 120
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
