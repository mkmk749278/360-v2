# Session handoff — paper trading mode

_Last updated: 2026-05-16_

This document captures live context for a Claude Code session resuming the
paper-trading-mode workstream. Read this **before** making changes.

---

## Recently shipped

### PR #401 — `POST /api/auto-mode/paper/reset`
- Zeros cumulative paper PnL counter
- Resets paper equity baseline to $1000
- Archives `paper_trades` table snapshot
- **Does NOT** close open positions in `PaperOrderManager._positions` (deliberate — see doctrine below)

---

## In flight

### `feat/paper-close-all-positions` (PR TBD)
User-facing action to flatten the in-memory paper book without touching reset doctrine.

Adds:
- `PaperOrderManager.close_all_open_positions(reason="user_close_all") -> dict`
  - Iterates snapshot of `_positions` keys
  - Calls `close_full(current_price=position.entry, reason=...)` per position (zero-move close)
  - Returns `{closed_count, realized_pnl_total}`
- `POST /api/auto-mode/paper/close-all` endpoint
  - Returns `PaperCloseAllResponse` (new Pydantic model in `src/api/schemas.py`)
  - Auth/wiring mirrors `/reset` endpoint

Tests: `tests/test_paper_close_all.py` — opens 3 positions, asserts close-all behavior + idempotency.

**Reset endpoint and `/reset_full` Telegram handler are UNCHANGED.**

---

## Doctrine: live vs paper reset

| Mode  | Reset behavior                                                          |
|-------|-------------------------------------------------------------------------|
| LIVE  | `/reset_full` **preserves** in-flight signals to avoid orphaning real Binance positions on the exchange |
| PAPER | Positions are pure in-memory simulation, so flattening is safe — but it's exposed as a **separate user-triggered action**, not bundled into reset |

The owner explicitly opted out of coordinating `/reset_full` Telegram with paper mode reset. Users get a two-step flow instead:

1. `POST /api/auto-mode/paper/close-all` → flatten in-memory positions
2. `POST /api/auto-mode/paper/reset` → zero equity + PnL + archive

This avoids the half-reset state where equity reads $1000 fresh but old positions still track against pre-reset entries.

---

## Key files

| Path | Role |
|------|------|
| `src/paper_order_manager.py` | `_positions` dict, `close_full()`, `place_market_order()` — paper-only simulation |
| `src/api/paper_trade_routes.py` | All `/api/auto-mode/paper/*` endpoints |
| `src/api/schemas.py` | Pydantic request/response models |
| `src/auto_trade/trade_records.py` | `close_reason` enum values |
| `src/trade_monitor.py` | Signal lifecycle — **DO NOT TOUCH** for paper-only changes |
| `src/commands/` | Telegram command handlers (including `/reset_full` doctrine) |

---

## Guardrails for follow-up work

- **Never modify `OrderManager`** (the live broker manager) for paper-only fixes.
- **Never change `trade_monitor.py`** signal lifecycle to coordinate paper position cleanup — `close_full` is idempotent and the right seam.
- **Never change the `/reset_full` Telegram doctrine** of preserving in-flight signals. That preservation is a live-broker safety property.
- For new paper-mode operations, mirror the auth/response pattern of the existing `/reset` endpoint.

---

## Open questions for next session

- Should the Lumin app surface a "Close all paper positions" button on the Trade tab that consumes the in-flight `/close-all` endpoint? Currently no UI consumer exists.
- Should `close_reason="user_close_all"` be displayed differently in the archived `paper_trades` history view?
