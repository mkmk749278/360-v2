# Auto-Trade Scaling: Per-IP Weight Ceiling + Multi-IP Egress — Design Plan

*Owner question 2026-07-18: "Can 1,000–2,000 members auto-trade? Any limits
from our system or from Binance IP whitelisting?" This doc is the written
capacity assessment + the phased fix. **Docs-first — no code in this change.**
Implementation is a follow-up and touches the money path (order egress), so it
ships DARK + owner sign-off per § Project Phase.*

---

## TL;DR

The blocker to scaling auto-trade is **not** member count. Each user is a
separate Binance account with its own order-rate budget, so per-account limits
never bind. The blocker is that **every user's order traffic egresses through
one VPS IP**, and Binance enforces a **per-IP request-weight ceiling** shared
across all of them. A popular signal taken by many users at once fans out
(`asyncio.gather`, no throttle) into a burst of weighted REST calls from a
single IP → HTTP 429 → escalating 418 IP ban → auto-trade freezes for
**everyone at once**.

Two fixes, in order:

1. **Weight-aware egress throttle** (prevents the crash) — build first.
2. **Multi-IP egress pool** (raises the ceiling) — build second.

The concurrency variable that matters is **simultaneous takers per signal**,
not registered members.

---

## Current state (as of 2026-07-18)

- **Egress:** single VPS IP. Users whitelist it at connect time
  (`src/security/binance_connect_validator.py` enforces `ipRestrict=true` +
  our IP present, withdraw disabled, futures enabled).
- **Fan-out:** `dispatch_signal_to_active_users` runs `_one_user` for every
  taker under `asyncio.gather` with **no concurrency limit and no pacing**
  (`src/execution/signal_dispatch.py:1379`).
- **Per take:** ~3–4 Binance REST calls — market entry
  (`/fapi/v1/order`), stop-loss + take-profit (`/fapi/v1/algoOrder`), and
  possibly a margin-type set (`src/execution/order_placer.py`).
- **Rate-limit handling:** none. Grep of `src/execution/` finds no 429, no
  418, no `-1003`, no `X-MBX-USED-WEIGHT` awareness, no backoff-on-rate-limit,
  no global semaphore. On hitting the ceiling the path fails hard.
- **Blast-radius tripwires** (`src/execution/tripwires.py`) are **per-user**
  for the two that bound load (rate limit 5/min·30/hr; position cap
  $500–$2,000). The only engine-wide breaker (`GlobalCircuitBreaker`) trips on
  **rejections**, not on accepted-order volume — so it does not pace a healthy
  burst.

## What does NOT block scaling (fine to thousands)

- **Per-account Binance limits.** Order-count limits (~300/10s, ~1,200/min)
  are **per-account (per-UID)**. One take = 3–4 orders; every user is far under
  their own account budget. Never the bottleneck.
- **Signing service.** Local Unix-socket HMAC — CPU-cheap, thousands/sec. Our
  own resource, not a Binance limit.
- **Market data.** Scanner WS/klines are shared streams (75 pairs), independent
  of user count.
- **Background reconcile reads.** The per-user `positionRisk` read fires only
  for users with a PENDING/open position
  (`src/execution/worker_manager.py:78`), so it scales with *users currently in
  a trade*, not total membership.

## What DOES break at 1,000–2,000 — all traces to the single IP

1. **Per-IP request-weight ceiling (the hard limit).** Binance USDⓈ-M Futures
   caps request **weight per IP** (published figure ≈ 2,400/min — **must be
   re-verified against the current Binance Futures docs**, per Real-Data-First
   Diagnosis). Order-count limits are per-account, but *weight* is per-IP and
   **all users share one IP**. 1,000 takers × ~3–4 calls = ~3,000–4,000
   weighted calls from one IP in a few seconds → over budget instantly.
2. **No graceful degradation.** With zero 429/418 handling, hitting the ceiling
   yields: 429 (orders delayed/dropped — a position can open while its stop
   is still queued) then escalating **418 IP ban** (2 min → up to days) that
   freezes **all** users and blocks every other REST call from that IP.
3. **Per-user user-data WS streams.** Each armed user runs a `PositionWorker`
   = one user-data WS + listenKey keepalive REST. 1,000–2,000 concurrent WS +
   keepalives from one IP; Binance also caps connections per IP.

## Where it breaks (must be measured, not guessed)

- Dozens–low-hundreds of **simultaneous** takers on one signal: likely fine
  today.
- 1,000–2,000 simultaneous takers on one signal: expected to trip 429 → 418
  and cascade-fail for everyone.
- The exact threshold depends on calls-per-take and the live per-IP weight
  budget. **Instrument `X-MBX-USED-WEIGHT-1M` under real load before pushing
  the count up.** Do not ship a hardcoded threshold from this doc.

---

## The fix

### Phase 1 — Weight-aware egress throttle (prevents the crash)

A single choke point in front of Binance REST that all order/reconcile traffic
passes through:

- **Global token-bucket / weight budget** sized to stay under the per-IP
  ceiling with headroom. The `gather` fan-out queues behind it instead of
  bursting.
- **429/418 backoff.** On 429, honor `Retry-After` / back off and re-queue. On
  418, hard-halt egress on that IP and alert — never keep hammering a banned
  IP.
- **Weight accounting from response headers** (`X-MBX-USED-WEIGHT-1M`) so the
  budget tracks Binance's real view, not a guess.
- **Fairness:** a hot signal's burst must not starve stop-loss placement or
  reconcile. Prioritize risk-reducing calls (SL placement, closes) ahead of new
  entries in the queue.

Effect: at high concurrency, takes *queue* (small added latency) instead of
IP-banning everyone. This is the safety-critical half and ships first.

### Phase 2 — Multi-IP egress pool (raises the ceiling)

"One VPS" ≠ "one IP." Acquire additional egress IPs and spread traffic:

- **Acquire IPs.** Buy 3–5 additional dedicated static IPv4s on the existing
  VPS (standard provider add-on, a few $/mo each). No new servers needed for
  the first step. (Egress-proxy nodes or managed cloud NAT are later options if
  we outgrow add-on IPs.) IPs must be **static and reputable** — Binance is
  sensitive to datacenter/shared-proxy IPs.
- **Whitelist all of them.** A Binance key's IP whitelist accepts multiple IPs
  (~30). The connect flow shows the **full list**; users whitelist all. Any
  listed IP is then valid for that user.
- **Source-IP binding.** One `aiohttp.TCPConnector(local_addr=(ip, 0))` per
  egress IP; the throttle load-balances order traffic across the pool
  (spread, not shard, so a hot signal's takers use all IPs). Per-IP weight
  budget multiplies by pool size.

Effect: aggregate weight budget = N × per-IP budget, lifting sustained
concurrent-take capacity roughly N-fold.

### Ordering rationale

Extra IPs *raise* the ceiling but do **not** prevent the ban — an unthrottled
burst can still exceed N × budget and ban all N IPs at once. The throttle
prevents the crash on any IP count. **Throttle first, then IPs.**

---

## Related: security concentration (separate change, see below)

The same "everyone behind one IP + one engine" shape is also a security
concentration risk, and the tripwire audit (2026-07-18) found the blast-radius
caps that bound *dollar* damage are per-user only — there is **no global
notional cap** and no global order-rate cap, and the one engine-wide breaker
fires on rejections, not on accepted-order volume. A rooted/buggy engine
placing *accepted* orders across all users sails through every green tripwire.

Multi-IP egress (Phase 2) reduces the single-IP concentration; a **global
notional / order-rate cap** is the complementary control. That work is tracked
separately as an owner-sign-off blast-radius change — this doc is capacity;
that one is security. They share the multi-IP payoff but ship independently.

---

## Open questions / to measure before implementation

1. **Live per-IP weight budget** and the true weight cost of each order/algo
   endpoint — from Binance's current Futures docs + observed
   `X-MBX-USED-WEIGHT-1M` headers under load.
2. **Calls per take** in the worst case (entry + SL + TP + margin-type set +
   any leverage set) — the burst multiplier.
3. **Binance per-IP WS connection cap** vs. projected armed-user count — does
   the user-data-stream fan-out need consolidation before the REST throttle
   matters?
4. **Spread vs. shard** distribution across the IP pool — spread maximizes
   headroom but requires whitelist-all; confirm the connect-flow UX cost.
5. **Provider IP reputation** — which add-on IPs Binance accepts without
   flagging many keys from one datacenter range.

## Non-goals of this doc

- No code, no config, no throttle constants. Those land in the follow-up PRs
  with real measured numbers.
- No change to the withdraw-disabled invariant — it stays absolute; it is the
  only protection that survives a full VPS compromise and is out of scope here.
