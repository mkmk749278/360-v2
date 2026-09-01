"""Redis key schema and serialisation helpers for API/engine process isolation.

When ``API_PROCESS_ISOLATED=true`` the engine publishes pre-computed snapshots
to these keys after each scan cycle; the ``api`` container reads them without
touching engine memory, eliminating the shared-event-loop bottleneck that caused
5-10 s timeouts on settings writes and stale-data on tab loads.

Key lifetime contract
─────────────────────
* TTL is sized against the writer's **measured period**, not its intended
  interval, and it is the LAST line of defence rather than the first.

  It was sized against the interval until 2026-08-18, on the sentence "TTL is
  2x that interval" — which was wrong twice over. The constants were 3-4x, not
  2x; and more importantly the writer's period is not the interval, because the
  work is not free. Measured on the box the day this was written:
  **75s per cycle typical, 188s worst, 5 of 7 cycles over budget** — against a
  60s TTL. The keys could not survive, so ``snapshot:signals_all`` was absent
  most of the time and a paying subscriber opening the Lumin app read
  **"No signals yet"**. The api container serves from these keys and nothing
  else; an expired key is not a stale page, it is an empty product.

  The ordering that matters: the ``snapshot_writer`` liveness probe detects a
  stalled writer in ~10 minutes. **The TTL must outlive that**, or the app goes
  blank before anyone is told it is going blank. A stale key serving
  ten-minute-old signals is strictly better than no key at all — signals live
  for hours, and the readers grade their own freshness.

  Raising the TTL does NOT make the writer fast; it stops a slow writer being a
  user-visible outage while the cost is measured and cut. ``SnapshotWriter``
  now times each payload individually so the next change is aimed rather than
  guessed.
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
#: {symbol: mark_price} for every symbol the engine is currently marking,
#: plus ``__stamped_at__``.  The api container has no mark-price feed of
#: its own (and no signing socket), so without this a per-user position
#: card either shows no live PnL at all or fetches a price ITSELF and
#: prints it beside engine state on a different clock — the defect ops
#: paid for on 2026-07-30.  The engine already subscribes to exactly the
#: symbols with open positions, so publishing them costs one small SET.
KEY_POSITION_MARKS = "snapshot:position_marks"  # {symbol: price}  — written every ~15 s
#: {uid: {symbol: exchange-position row}} — what BINANCE says each user
#: holds, from the exchange's own ACCOUNT_UPDATE push plus the reconciler's
#: positionRisk row. One key rather than one per user: the api container
#: serves only the caller's slice, the whole book is a handful of rows, and
#: N keys with N independent TTLs make "the engine stopped publishing" and
#: "this user has nothing" indistinguishable per user.
KEY_EXCHANGE_POSITIONS = "snapshot:exchange_positions"  # {uid: {symbol: row}}
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
# ── Diagnostic-catalog command channel (owner-approved 2026-08-19) ─────────
# Same request/response shape as the manual-take queue above, and for the same
# reason: the API container serves the route, the ENGINE container holds the
# objects a diagnostic reads, and the caller needs the answer back rather than
# fire-and-forget. A LIST the API LPUSHes, drained by the engine, result written
# to KEY_DIAG_RESULT_PREFIX + request_id.
#
# The payload carries a catalog KEY, never a command — `src/diag_catalog.py`
# owns what that key may do, and an unknown key is refused there. Nothing on
# this channel can reach an order, a secret or the kill switch by construction.
KEY_CMD_DIAG = "snapshot:cmd:diag"                # Redis LIST of JSON envelopes
KEY_DIAG_RESULT_PREFIX = "snapshot:diag_result:"  # + request_id → JSON outcome
TTL_DIAG_RESULT = 180   # outlives the API's poll window comfortably
DIAG_CMD_STALE_S = 60   # the engine rejects envelopes older than this

KEY_CMD_TAKE = "snapshot:cmd:take"                # Redis LIST of JSON envelopes
KEY_TAKE_RESULT_PREFIX = "snapshot:take_result:"  # + request_id → JSON outcome
TTL_TAKE_RESULT = 120   # result outlives the API's ~8s poll window comfortably
TAKE_CMD_STALE_S = 60   # engine rejects queue entries older than this

# ── TTLs (seconds) ────────────────────────────────────────────────────────
# Sized to outlive the ~10-minute detection time of the `snapshot_writer`
# liveness probe, against a measured worst cycle of 188s. See the key-lifetime
# contract above: these are a safety valve for a DEAD writer, not a freshness
# mechanism for a slow one, and at 60s they were neither.
_TTL_FEED = 900   # 15 min — the probe pages at ~10, so the app never blanks first

TTL_SIGNALS      = _TTL_FEED
TTL_ACTIVITY     = _TTL_FEED
TTL_AGENTS       = _TTL_FEED
TTL_TICKERS      = _TTL_FEED
TTL_ENGINE_STATE = _TTL_FEED
TTL_POSITIONS_DIAG = _TTL_FEED
TTL_DATA_INTAKE  = _TTL_FEED
TTL_ROUTER_DELIVERY = _TTL_FEED
TTL_TRAIL_GOVERNOR  = _TTL_FEED
TTL_DARK_PROMOTION  = _TTL_FEED
#: Deliberately SHORTER than _TTL_FEED.  A stale feed renders a stale
#: list, which is merely old; a stale mark renders a WRONG unrealized
#: PnL on a live position, which reads as fact.  Expiring lets the app
#: say "no live mark" instead of quoting a price from ten minutes ago.
TTL_POSITION_MARKS = 90
#: Same 90s reasoning as the marks above, and for the same reason: a stale
#: LIST is merely old, a stale POSITION reads as a holding the user does not
#: have. Expiring lets the card say "the engine stopped reporting" instead
#: of drawing a position from ten minutes ago as though it were current.
TTL_EXCHANGE_POSITIONS = 90
TTL_ALERTS       = _TTL_FEED
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
