"""Per-user execution layer for server-side trading.

This package implements the always-on, per-user infrastructure that
the OWNER_BRIEF §3.2a doctrine (pre-TP partial close + BE shift)
depends on.  Components:

* :mod:`src.execution.events` — typed event dataclasses for Binance
  User Data Stream messages.  Pure parsing; no IO.
* :mod:`src.execution.listen_key` — Binance listenKey lifecycle
  (create + 30-min keepalive + close).  Talks to Binance via the
  signing service from PR-4.
* :mod:`src.execution.user_data_stream` — WebSocket consumer that
  subscribes to ``wss://fstream.binance.com/private/ws?listenKey=...``,
  parses each message into the typed events from
  :mod:`src.execution.events`, and dispatches to a caller-supplied
  handler.  Includes automatic reconnect on disconnect.
* :mod:`src.execution.position_worker` — per-user asyncio task
  that ties listen_key + user_data_stream together.  In PR-5 it's
  a scaffold that logs events; PR-6 will wire the Position FSM as
  the event handler.

What this package does NOT do (yet):

| Capability | Lands in |
|---|---|
| Position FSM (state transitions on events) | **PR-6** |
| Pre-TP partial close + BE shift on TP1 fill | **PR-7** |
| Anomaly tripwires (rate limit, position cap, symbol allowlist) | **PR-8** |
| Reconciliation loop (60s diff vs Binance) | **PR-9** |
| Worker lifecycle manager (start/stop per active user) | **PR-9 or PR-11** |

The B18 non-negotiables still apply: orders are signed via the
signing service from PR-4 (engine main process never sees plaintext);
withdraw-disabled keys are enforced at connect time per PR-2.  This
package is the EVENT layer that the order-placement layer (PR-6)
reacts to.
"""
