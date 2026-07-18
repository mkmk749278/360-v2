# Server-Side Manual Trade Builder (Alerts + manual Signal takes) — Implementation Design

*Owner decisions 2026-07-18 (AskUserQuestion):*
- *Compulsory SL applies ONLY to unattended auto-dispatch of our signals.
  Manual takes — signals AND alerts — may be entry-only, no forced stop.*
- *Tier gate: `can_assist` (Assist ₹1000/mo and up), same as one-tap signal take.*
- *Sizing: per-user fixed notional (the "Position notional (live)" knob), not %-equity.*

*Ships DARK (`MANUAL_TRADE_BUILDER_ENABLED=false`); activation = owner sign-off
after shadow. New dispatch path + FSM transitions + business-rule change =
owner-sign-off items; direction approved 2026-07-18, activation pending
evidence.*

---

## Problem

Taking a trade from an **alert** today (`take_alert_trade_sheet.dart` →
`OrderExecutor.placeAlertEntry`) is **client-side**: the phone signs Binance
REST with device keys. Two hard failures for real users:

1. **Mobile IP churn.** Device keys must be IP-whitelisted at Binance. Mobile
   networks reassign IPs constantly, so a phone-signed order is rejected
   unless the user re-whitelists on every IP change — unusable. The engine key
   is already whitelisted to the stable VPS IP; server-side execution removes
   the problem entirely.
2. **Entry-only, no protection, no adjustability.** The alert take places a
   naked market entry with no SL/TP and no way to set geometry at take time or
   adjust it afterward.

Goal: take an alert (or a signal) **server-side** through the engine key, with
the user setting **entry / SL / TP interactively on the chart** — or taking
entry-only now and attaching SL/TP later — same custody and IP stability as
auto-trade.

## Target semantics

A manual take is a **user-directed** order on the engine-connected key:
- Entry is **MARKET** (take at market) or **LIMIT** at a user-chosen price
  (the "slide the entry line" gesture) with a validity TTL — reusing the
  `FSM_LIMIT_ENTRY` machinery (`docs/FSM_LIMIT_ENTRY_DESIGN.md`).
- SL and TP are **optional**, user-supplied. Absent → not placed (allowed for
  manual takes per the owner decision above).
- Size is the user's fixed notional (same knob auto-trade uses).

## The naked-position invariant, re-scoped

Hard Limit today: *"Never let a position sit OPEN without a stop."* This exists
to protect **engine-managed** positions (auto-dispatched from our signals) —
where the engine is fully responsible for the exit. It was never meant to
forbid a user from holding their own stop-less discretionary trade.

Moving manual takes server-side makes the engine the *custodian* of positions
that are intentionally stop-less. To keep the invariant meaningful without
crying wolf, every Position carries a **`protection_mode`** stamp set at
placement:

| `protection_mode` | Set by | SL compulsory? | Naked-position detector | Reconciler / FSM backstop |
|---|---|---|---|---|
| `managed` | auto signal dispatch | **Yes** (unchanged) | active | active |
| `user_owned` | manual take (signal or alert) | No | **exempt** | **exempt** (never force-closes for missing SL) |

Consequences wired in the SAME change (no scaffold):
- **Engine FSM / naked-position invariant** checks `protection_mode == managed`
  before requiring/placing a backstop stop.
- **Ops naked-position Tier-0 detector** (`360ce-ops`, `app/agent/`) filters out
  `user_owned` positions — the alarm only ever fires for auto positions.
- **Reconciler** treats a `user_owned` position with no stop as a legitimate
  live state, not an orphan to close.

Default for any position missing the field (older rows / pre-upgrade) is
`managed` — fail safe toward *more* protection, never less.

## Endpoint contract

### Phase 1 — `POST /api/manual-trade/take`
Auth: Firebase bearer. Gate: `can_assist` (fails closed).
```
{
  "source": "alert" | "signal",
  "ref_id": "<alert_id | signal_id>",     # idempotency key + clientOrderId seed
  "symbol": "1000PEPEUSDT",
  "direction": "LONG" | "SHORT",
  "entry_type": "market" | "limit",
  "entry_price": 0.0027070,                # required iff entry_type=limit
  "valid_for_minutes": 15,                 # limit TTL; 0/absent → engine default
  "sl_price": 0.0026800,                   # optional
  "tp_prices": [0.0027600]                 # optional, 0..3 legs
}
```
Behaviour:
- Sizes at `resolve_notional_usd(uid, default)` — the same path signal-take
  uses (NO `risk_scale` shrink; manual takes are full-notional).
- Stamps `protection_mode=user_owned`.
- `entry_type=limit` → `place_limit_entry` at `entry_price` with TTL (rests;
  immediately-marketable → MARKET fallback, per FSM_LIMIT_ENTRY §2).
- SL/TP placed only for supplied legs. No legs → entry only.
- Idempotent on `(uid, ref_id)` with the existing manual-take dup guard
  (`position_state.get_position`), fails **closed** on a store error.
- Returns the same `TakeSignalResult` shape the app already parses
  (`outcome: placed|rejected`, reject_class/detail, entry_price, total_qty).

### Phase 2 — `POST /api/positions/{position_id}/amend`
```
{ "sl_price": 0.0026900, "tp_prices": [0.0027700] }   # either/both, null = leave as-is
```
- New FSM amend transition: cancel + replace the SL and/or TP reduce-only
  orders on an OPEN `user_owned` position. Owner-sign-off (FSM transition).
- Powers "adjust SL/TP later from the chart."

## App changes (`lumin-app`)

- **Chart order lines.** The TradingView Lightweight Charts webview
  (`assets/chart/`, `lib/features/charts/`) gains draggable **entry / SL / TP**
  lines; dragging updates a review panel (side, notional, qty, R:R). "Take
  trade" from an alert opens this instead of the client-side sheet.
- **Repository seam.** New `LuminRepository.placeManualTrade(...)` on both
  `HttpRepository` (→ `/api/manual-trade/take`) and `MockRepository`.
- **Retire client-side alert execution.** `OrderExecutor.placeAlertEntry` and
  `take_alert_trade_sheet.dart`'s device-key path are removed; the "needs a
  non-IP-locked device key" wall disappears.
- Renders engine state as source of truth (position open/closed, protection
  mode) — never optimistic.

## Phasing (each phase ships fully wired, no scaffolds)

- **Phase 1** — take-with-geometry end-to-end: entry (market/limit) + optional
  SL + optional TP, `protection_mode` stamp + detector/reconciler scoping, app
  chart trade-builder, dark flag. Complete on its own.
- **Phase 2** — amend SL/TP on an open `user_owned` position from the chart.

## Open items / shadow before activation

- Confirm `protection_mode` back-fill default (`managed`) against live position
  rows before enabling.
- Shadow the LIMIT-entry fill/expiry behaviour for manual takes on a real
  window (reuses FSM_LIMIT_ENTRY shadow instrumentation).
- Entry-only (no-SL) `user_owned` positions: verify the ops detector filter and
  reconciler exemption on a real position before flag-on.
