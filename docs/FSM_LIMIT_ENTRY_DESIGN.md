# FSM LIMIT-at-Zone Entry with Validity TTL — Implementation Design

*Owner decision 2026-07-03 (AskUserQuestion): "LIMIT at zone + TTL".
Ships DARK (`FSM_LIMIT_ENTRY_ENABLED=false`); activation = owner sign-off
after shadow. FSM entry shape = owner-sign-off item; direction approved,
activation pending evidence.*

---

## Problem

Auto-trade FSM entries are MARKET-at-dispatch (`place_market_entry`, fills
synchronously) while the signal book + manual subscribers use the limit entry
zone and (since #691) the advertised validity window. AUTO-tier users are IN
~⅓ of trades the book correctly counts as `EXPIRED_NO_FILL` — worse entries
than the product advertises, and a book that doesn't describe their P&L.

## Target semantics — one truth per signal

A signal means: *"enter within [entry_zone_low, entry_zone_high] within
valid_for_minutes; otherwise no trade."* Every consumer — signal book, paper
book, manual subscriber, auto-trade — gets exactly that.

## Wire plan (order of implementation)

1. **Field forwarding.** `SignalRouter` → `dispatch_signal_to_active_users` →
   `place_signal`: add `entry_zone_low`, `entry_zone_high`,
   `valid_for_minutes`. Zones absent/None → market-order semantics (unchanged
   path, exactly like the monitor's fill gate).
2. **OrderPlacer.place_limit_entry.** GTC LIMIT at the zone edge nearest the
   market (BUY → `zone_high`, SELL → `zone_low`) — fills the moment price
   touches the zone, mirroring `entry_zone_filled` (candle-overlap) semantics.
   If Binance rejects as immediately-marketable (price already inside/through
   the zone), fall back to MARKET — that's the "dispatch price already in
   zone" case and is honest.
3. **New FSM state `PENDING_ENTRY`.** Persist position with
   `entry_order_id`, target qty, `entry_expires_at` (dispatch time +
   valid_for_minutes), NO SL/TP yet. Excluded from open-position queries,
   pre-TP ticks, and the BE-shift path (all key off OPEN).
4. **Fill handling (position_worker, ORDER_TRADE_UPDATE).** On entry fill:
   re-anchor SL to actual fill (reuse the existing Step-1b logic), place SL
   FIRST (retry with the existing transient-reject backoff — the
   naked-position Hard Limit applies from the first filled contract), then
   TPs, then → OPEN. **Partial fills:** first partial places the SL for the
   filled qty (closePosition=true STOP covers any size); on TTL expiry the
   unfilled remainder is cancelled and the position continues with filled qty.
5. **TTL sweep (reconciler loop, 60s cadence).** For PENDING_ENTRY positions
   past `entry_expires_at`: cancel the entry order (tolerate already-filled
   race — re-check order status after cancel attempt), then terminal state
   `CANCELLED_NO_FILL` (new close_reason), zero P&L, no perf-record trade.
   Mirrors the book's `EXPIRED_NO_FILL`.
6. **Reconciler awareness.** The stale-position safety net must not
   market-close a PENDING_ENTRY (no position exists on Binance yet) — it
   cancels the resting order instead. The existing missing-SL emergency path
   is the backstop if the worker misses a fill event (verify it treats a
   filled-entry-no-SL position correctly — it should place the SL, not close).
7. **Shadow while dark.** With the flag OFF, at dispatch log
   `[SHADOW] FSM_LIMIT_ENTRY symbol=... in_zone={bool} zone=[lo,hi]
   valid_min=N` — measures, per real dispatch, whether the LIMIT would have
   filled instantly (dispatch price in zone) vs rested vs TTL'd. Read this
   before activation: expected result is "in_zone at dispatch" for the large
   majority (evaluators emit at the retest), with the no-fill tail matching
   the book's EXPIRED_NO_FILL rate.

## Config

```
FSM_LIMIT_ENTRY_ENABLED       bool   false   (dark master)
FSM_ENTRY_TTL_FALLBACK_MIN    int    15      (when sig.valid_for_minutes==0)
```

## Safety invariants (unchanged, re-asserted in tests)

- Never a filled position without a stop: SL placement is the FIRST action on
  any fill event; reconciler emergency-SL is the backstop.
- Blast-radius caps/tripwires run at placement time exactly as today
  (`_enforce_safety_gates` before the LIMIT is placed).
- Kill switch: PENDING_ENTRY orders are cancelled by the existing
  cancel-all path (verify it queries resting orders, not only positions).

## Test matrix

- dark default: dispatch unchanged, shadow line emitted
- limit placed at correct edge per side; marketable-limit fallback → MARKET
- fill → SL placed before TPs; SL retry on transient reject
- partial fill + TTL: remainder cancelled, SL sized correctly
- TTL sweep: cancel + CANCELLED_NO_FILL, already-filled race tolerated
- reconciler: PENDING_ENTRY never market-closed; missing-SL backstop
- kill switch cancels resting entries

## Activation (owner)

After ≥1 week of shadow: in-zone rate, would-TTL rate vs the book's
EXPIRED_NO_FILL rate. Flip `FSM_LIMIT_ENTRY_ENABLED=true`; watch the first
day's fills against the signal book 1:1.
