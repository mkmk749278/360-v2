# Full-Universe Futures Scanning + A Second VPS IP — Research

**Date:** 2026-07-27
**Question from owner:** *"Can we add one more IP to the VPS and scan the full Binance
futures universe? What are the advantages and disadvantages? Binance minutes?"*
**Status:** Research only. Nothing shipped. No code changed.

---

## 1. Verdict up front

**Adding a second IP is cheap, safe-ish, and mildly useful — but it does not unlock
full-universe scanning, because Binance's rate limit is not what is stopping us.**

Three separate things get conflated in the phrase "scan the full universe". They have
different limits and different answers:

| Thing | Limited by | Second IP helps? | Verdict |
|---|---|---|---|
| **Knowing** what every pair is doing | `!ticker@arr` WS stream | Not needed | **Already done today** — full universe (~500+ pairs), 1 connection, zero REST |
| **Deep-scanning** every pair through 17 evaluators | Engine CPU (1.5 vCPU) + RAM (1 GB) + event loop | **No** | **This is the wall.** ~6–7× the compute we currently have |
| **Emitting** more signals | Router concurrency caps (5 per channel, 3 same-direction global) | **No** | **Hard-capped.** More pairs cannot produce more delivered signals |

And there is one genuine hazard that must be settled before any second IP goes near the
box — see **§6, the whitelist landmine**. Every paid auto-trade user has whitelisted
exactly one IP on their Binance key.

**Recommendation:** don't do the full-universe scan. Do the three things in **§12**
instead — they capture most of the upside for a fraction of the risk and cost, and two
of them are config changes, not rewrites.

---

## 2. What we actually scan today (read from the code, not from memory)

| Fact | Value | Source |
|---|---|---|
| Deep-scanned universe | **75** USDT-M perps | `TOP50_FUTURES_COUNT=75`, `config/__init__.py:1288` |
| Selection rule | Top 75 by 24 h quote volume, minus blacklists | `pair_manager.fetch_top_futures_pairs` |
| Universe refresh | every 3600 s | `TOP50_UPDATE_INTERVAL_SECONDS=3600` |
| Volume floor to scan at all | $1 M / 24 h | `SCAN_MIN_VOLUME_USD=1000000` |
| Mover promotion (extra pairs) | up to **+30** concurrent, 6 h hold | `MOVER_PROMOTION_MAX_PAIRS=30`, `MOVER_PROMOTION_TTL_SEC=21600` |
| **Effective max scanned set** | **~105 pairs** | 75 core + 30 promoted |
| Scan cadence | continuous loop, `sleep(1)` between cycles | `scanner/__init__.py:2548` |
| Concurrency | 20 symbols in flight | `_MAX_CONCURRENT_SCANS=20` |
| Engine container | **1 GB RAM, 1.5 vCPU** | `docker-compose.yml:80-81` |

**Measured production scan-cycle wall-time** (Session 18, post-#588, `ACTIVE_CONTEXT.md:5179`):

```
cycle=2.5–5.7s   {'indicators': 0.0, 'smc': 0.0}     ← most cycles, caches warm
cycle=12.4s      {'indicators': 97.1, 'smc': 0.0}    ← a 1m candle closed
cycle=16.0s      {'indicators': 136.4, 'smc': 45.6}  ← 1m + 5m both closed
```

That 16 s worst case, on 75 pairs, at 1.5 vCPU, is the number everything below scales from.

### We already have full-universe *awareness*

This is the most important thing to understand before spending anything.

`MOVER_IGNITION_ENABLED=true` (default) subscribes the engine to `!ticker@arr` — the
**all-market ticker array stream**: every changed symbol, once per second, on its own
dedicated WS connection. `bootstrap.py:955` calls it out explicitly:

> *"its `!ticker@arr` meta is the only full-universe (~600 pairs) mover source, so the
> scanner reads it to admit movers outside the top-75 pair_mgr scan set."*

So the engine **already sees every USDT-M perp every second**, for the cost of one
WebSocket connection and zero REST weight. What it does *not* do is run the 17-evaluator
stack on all of them — it runs a burst/ignition detector, and promotes the interesting
ones into the deep scan (capped at 30).

**That architecture is correct.** "Watch everything cheaply, deep-scan what's moving" is
strictly better than "deep-scan everything", because 90 % of the universe is flat on any
given cycle and burning CPU on a flat pair buys nothing.

---

## 3. "Binance minutes" — the actual per-minute budget

These are the real limits for USDⓈ-M futures (verified against Binance docs, July 2026):

### REST — **per IP address**

| Limit | Value | Notes |
|---|---|---|
| `REQUEST_WEIGHT` | **2,400 / minute / IP** | This is the one people mean by "Binance minutes" |
| `RAW_REQUESTS` | separate counter, per IP | Read live from `/fapi/v1/exchangeInfo` → `rateLimits[]` |
| Response header | `X-MBX-USED-WEIGHT-1M` | Authoritative — every response tells you your real usage |
| Breach → `429` | must back off | |
| Repeat breach → `418` | **automated IP ban, 2 minutes to 3 days**, scaling for repeat offenders | |

VIP tiers raise this substantially (600 M USDT 30-day volume → 72,000 req/min), but we
are on default tier, so **2,400/min/IP** is our number.

### Orders — **per account / API key, NOT per IP**

| Limit | Value |
|---|---|
| Orders | **300 / 10 s** |
| Orders | **1,200 / minute** |
| Sub-accounts | **share the parent UID's pool** — you cannot scale orders by adding accounts |

**This asymmetry is the whole answer to the IP question.** Weight is per-IP; orders are
per-key. A second IP therefore doubles market-data budget and adds **exactly zero** order
throughput.

### WebSocket — per IP

| Limit | Value |
|---|---|
| Streams per single connection | **1,024** |
| Connection attempts | **300 per 5 minutes per IP** |
| **Outgoing** messages (our SUBSCRIBE frames) | **10 / second** — exceed it and you're disconnected |
| Connection lifetime | **24 hours**, then forced disconnect |
| Server ping | every 3 min; no pong within 10 min → closed |

Note the 10 msg/s limit is on messages **we send**, not data we receive. Inbound market
data is unlimited by Binance — but not by our event loop (see §7).

### Is running two IPs against Binance allowed?

**Yes — it is explicitly recommended.** Binance's own documentation advises distributing
requests across multiple IPs when operating at scale. Weight limits are deliberately
per-IP for exactly this reason. This is not circumvention and carries no ToS risk.

One caveat learned in this session: Binance enforces **geographic eligibility per IP**.
A `curl` to `fapi.binance.com` from this sandbox returned:

```json
{"code":0,"msg":"Service unavailable from a restricted location according to
 'b. Eligibility' in https://www.binance.com/en/terms."}
```

So the second IP must be in a **jurisdiction Binance serves**, and ideally the *same*
region as the current VPS. A cheap IP from the wrong datacentre region is a dead IP.

---

## 4. What we currently spend of that 2,400/min

Our own limiter is configured correctly (`src/rate_limiter.py`):

```
Futures budget: 2,200 / min   (out of Binance's 2,400 hard cap)
Reserve:          200 / min   (WS reconnects, ad-hoc exchangeInfo)
Throttle flags:  70 % → pause Tier 3 · 85 % → pause Tier 2 · 90 % → WARN
```

Steady-state consumers, per minute, at 75 pairs:

| Consumer | Calls/min | Weight | Notes |
|---|---|---|---|
| `OIPoller` — `/fapi/v1/openInterest` + `/fapi/v1/premiumIndex` | 150 | ~150 | 2 calls/symbol/60 s, `order_flow.py:713` |
| Global `bookTicker` prefetch | ~3.3 | ~17 | Once per 18 s (TTL 20 s × 0.9), all symbols in one call |
| Kline gap-fill / WS fallback | bursty | variable | Only on WS gaps |
| Pair universe refresh | 1 / hour | 40 | `/fapi/v1/ticker/24hr` full |
| Signing service (orders, per user) | low | low | Order path, separate container |

**Steady-state is on the order of ~200 weight/min against a 2,200 budget — roughly
8–10 % utilisation.**

> ⚠️ **This is an estimate from reading call sites, not a measurement.** Per
> CLAUDE.md § Real-Data-First Diagnosis, get the real number before deciding anything.
> The engine already syncs from `X-MBX-USED-WEIGHT-1M`
> (`rate_limiter.update_from_header`). It is just never surfaced. See §11.

**Provisional conclusion: we are using under 10 % of one IP's weight budget. There is no
rate-limit problem to solve. A second IP would take us from ~10 % to ~5 %.**

### Two code-level notes found while measuring

1. **`src/api_limits.py` hardcodes the wrong limit and is dead code.**
   `BINANCE_WEIGHT_LIMIT_PER_MINUTE = 1200` is the *old spot* limit; futures is 2,400.
   `APIWeightTracker` and `BatchScheduler` are instantiated at `scanner/__init__.py:1425-1426`
   and then **never read** — every real rate decision goes through `src/rate_limiter.py`,
   which has the correct 2,400 figure. Harmless today (it gates nothing), but it is a
   trap for the next person who greps for the weight limit and finds 1200 first.
   *Suggested follow-up: delete the module or fix the constant. Off money path, ships normally.*

2. **`/fapi/v1/trades` is declared `weight=1` at `historical_data.py:144,150` but is
   fetched with `limit=1000`.** Binance weights klines/trades by the `limit` bracket, so
   the true cost is higher than declared. Under-declaring makes our local limiter
   *optimistic* — it thinks it has more budget than it does. At 10 % utilisation this is
   invisible; at 60 % utilisation (which full-universe seeding would hit) it is how you
   earn a 418 ban. *I could not verify the exact current weight bracket from primary
   Binance docs in this session — the doc pages did not render the tables. Verify on the
   VPS by reading `X-MBX-USED-WEIGHT-1M` before and after a seed.*

---

## 5. What a second IP actually buys

Honest accounting. Not nothing, but not much.

### Real advantages

1. **Boot / re-seed time roughly halves.** Every deploy re-seeds 7 timeframes × ~3,200
   candles per symbol (`SEED_TIMEFRAMES`, `config/__init__.py:1373`). At 75 pairs that is
   ~525 kline calls. It's the single largest weight burst we produce, and `main` auto-deploys
   in ~45 s — so seeding is on the critical path of every ship. Splitting the seed across
   two IPs halves the window where the engine is running on partial history.

2. **Headroom for the degraded-WS path.** When the futures WS drops, the scanner falls
   back to REST and the code has already been burned once by this
   (`scanner/__init__.py:2247` — *"the primary cause of the 100 % rate-limit exhaustion
   observed when the futures WS dropped"*). The mitigation today is to **cut the scan set
   to 75 pairs** (`WS_DEGRADED_MAX_PAIRS`). A second IP would let us ride out a WS outage
   without shrinking coverage.

3. **Blast-radius isolation on a 418 ban.** Today one runaway loop can get our only IP
   banned for up to 3 days — that takes down market data *and*, if egress is shared,
   order placement. Splitting read traffic from order traffic means a market-data ban
   cannot stop us from closing an open position. **This is the strongest argument for a
   second IP, and it is a safety argument, not a scale argument.**

4. **A/B and canary capacity.** A second egress lets a shadow measurement pull its own
   data without competing for the production budget.

### What it does *not* buy — be clear about this

- ❌ **No order throughput.** Orders are per-key. This is the money path. Zero gain.
- ❌ **No CPU.** Same 1.5 vCPU, same event loop. This is the actual constraint.
- ❌ **No RAM.** Same 1 GB.
- ❌ **No extra signals.** Router caps bind before anything else (§8).
- ❌ **It does not enable full-universe scanning.** Not even close.

---

## 6. ⚠️ The whitelist landmine — settle this before touching the network

**This is the part that can lose user money, so it goes in its own section.**

Every server-side auto-trade user has an API key with **IP whitelist enabled and our
single VPS IP on it**. This is enforced at connect time and is not optional:

- `src/security/binance_connect_validator.py:11` — *"IP whitelist must be enabled AND the
  engine VPS IP must be on it."*
- We **reject** keys without a whitelist (`binance_connect_validator.py:89`).
- The app shows the user the exact IP to paste, with a Copy button
  (`lumin-app/lib/features/settings/pages/server_side_execution_page.dart:439`).

**If order traffic ever egresses from the second IP, every user's key returns Binance
`-2014` (IP not whitelisted) and every order fails.** Including — and this is the part
that matters — **stop-loss placement on an open position.** That is a direct hit on the
naked-position invariant in CLAUDE.md § Hard Limits: *"Never let a position sit OPEN
without a stop."*

It would also fail silently from the user's perspective: their key is valid, their
balance is fine, and the engine just… can't trade. Then we would have to ask every paid
user to go re-edit their Binance whitelist. That is a trust event, not a config change.

### The safe shape, if we do this

The good news: the architecture already separates these. **Order signing lives in its own
container** (`360scalp-v2-signing`) with its own `aiohttp` session
(`signing_service/server.py:136`, `handler.py:368`). The engine reaches it over a Unix
socket, never over the network. So the split is at a container boundary, not scattered
through the code.

**Non-negotiable rules for any second-IP work:**

1. **Pin egress per container, at the OS/network layer** — iptables SNAT or a policy
   route per container IP. Do **not** try to do it in Python with
   `aiohttp.TCPConnector(local_addr=...)`: there are ~20 independent `ClientSession()`
   construction sites in `src/` (`binance.py`, `order_flow.py`, `websocket_manager.py`,
   `tier_manager.py`, `historical_data.py`, …) and missing one means an order silently
   leaves via the wrong IP. Per CLAUDE.md, a partial wiring is a scaffold, and scaffolds
   are banned.
2. **Signing container egress stays pinned to IP #1 forever.** Default-deny: if the
   pinning rule is absent or fails to load, the signing container must have **no**
   outbound route at all rather than fall back to the wrong source address. Fail closed,
   not fail open.
3. **Add a boot-time assertion**: signing container resolves its own public IP and refuses
   to start if it is not IP #1. A monitoring-agent detector for the same, in `360ce-ops`.
4. **Never document or display IP #2 to users.** The app's whitelist card must keep
   showing IP #1 only.
5. If we ever *do* need to migrate order egress, it is a **user-communication project**
   (in-app notice, grace period, dual-whitelist window), not a deploy.

---

## 7. What actually binds: CPU, RAM, and the event loop

### CPU

Scan cost is dominated by indicator + SMC recompute at candle closes, and it is
**roughly linear in symbol count**. Extrapolating the measured production numbers:

| Universe | Typical cycle | Worst case (1m + 5m close) |
|---|---|---|
| 75 pairs (today) | ~3 s | **~16 s** (measured) |
| 200 pairs | ~8 s | **~43 s** (projected) |
| 500 pairs | ~20 s | **~107 s** (projected) |

**A 1m candle closes every 60 seconds.** At ~500 pairs the worst-case cycle exceeds the
1m bar interval, so the scanner can never finish a cycle before the next bar invalidates
its cache. It enters permanent backlog. Concretely:

- Signals get computed on candles that are already 1–2 bars stale.
- The router's own **staleness gate** then drops most of them at dispatch — so we'd burn
  7× the CPU to produce signals that get thrown away at the last step.
- The scanner heartbeat stretches past the monitoring agent's `StaleSnapshotDetector`
  threshold (>90 s), so **the monitoring agent starts paging** on a healthy engine.

This is not a tuning problem. Scanning 500 pairs through a 17-evaluator stack is a
different machine.

### RAM

Per symbol we hold ~3,200 candles across 7 timeframes × 8 numpy arrays, plus up to 1,000
tick dicts, plus `OrderFlowStore` (CVD, OI, funding), plus `LevelBook`, `VolumeProfile`,
`StructureState`, plus the per-timeframe indicator cache and the SMC cache.

Rough order of magnitude: ~200 KB/symbol for raw candles alone, and the caches and tick
dicts on top are the larger share. Whatever the real per-symbol figure is, **it multiplies
by ~6.7× going from 75 to 500 pairs, against a hard `mem_limit: 1g`.** The likely outcome
is OOM-kill, and the engine restarts into a full re-seed, which is the most expensive
thing it does.

> **Measure, don't guess.** `docker stats 360scalp-v2-engine` gives current RSS. If we're
> at 400 MB today, 500 pairs is dead on arrival. If we're at 120 MB, 200 pairs might fit.
> This one number decides whether any expansion is even discussable.

### Event loop

- **Today:** 75 symbols × 4 kline streams = 300 kline streams ≈ 300 inbound messages/sec,
  plus `!ticker@arr`, plus 75 `forceOrder` streams.
- **At 500 symbols:** ~2,000 kline streams ≈ **2,000 msg/sec**, each requiring a JSON
  parse and a numpy append, on the *same single event loop* that is also running the
  scanner, the FSM, the reconciler and the mark-price feed.

The codebase has already been bitten by exactly this. From `bootstrap.py:912`:

> *"During Extreme Fear events, the flood of forceOrder events across 50 symbols creates
> event-loop pressure that delays `last_pong` updates on kline connections, causing false
> staleness detections."*

They had to give liquidations a **separate connection pool** to fix it — at 50 symbols.
At 500 symbols that pressure is permanent, not event-driven. The failure mode is nasty:
delayed pongs → WS marked unhealthy → scan gating kicks in → we scan *less* than we do
today. **The engine would go slower by trying to go wider.**

WS connection *count*, notably, is a non-issue: 2,000 streams is 2 connections at
Binance's 1,024/conn (we self-limit to 200/conn via `WS_MAX_STREAMS_PER_CONN`, which is
conservative and adjustable). The wall is message processing, not connections.

### The OI poller breaks first, and silently

`OIPoller._poll_loop` (`order_flow.py:707`) is sequential: for each symbol, 2 HTTP calls,
then `sleep(0.1)`, then `sleep(60)` between passes.

| Universe | Time per pass | Effective OI freshness |
|---|---|---|
| 75 (today) | ~30 s | ~90 s |
| 300 | ~120 s | ~180 s |
| 500 | ~200 s | **~260 s** |

At 500 pairs, **open-interest data feeding the evaluators is over four minutes stale** —
and nothing raises an error. It just gets quietly worse. This is the exact failure class
CLAUDE.md was written about after the SAR incident: a computation that keeps producing
confident numbers describing data that is no longer current.

---

## 8. The decisive business point: the router caps

Even granting infinite CPU and RAM, **the number of signals we deliver would not change.**

| Cap | Value | Source |
|---|---|---|
| `360_SCALP` concurrent signals | **5** | `MAX_CONCURRENT_SIGNALS_PER_CHANNEL`, `config:2128` |
| Each sub-channel (FVG, CVD, VWAP, DIV, STR, ICH, ORB) | **3** each | same |
| **Global same-direction cap** | **3** | `MAX_SAME_DIRECTION_GLOBAL`, `config:2149` |

That last one is a hard ceiling and it exists for a good reason. From the config comment:

> *"Top-75 USDT-M futures pairs are 0.85–0.95 correlated to BTC. When BTC dumps, every
> LONG alt SL fires simultaneously — 5 concurrent LONGs means 5 simultaneous full-SL
> losses on a single BTC move."*

On top of that, `SignalRouter._process` applies correlation lock, per-symbol cooldown,
per-channel cooldown, correlation-group limits, and a staleness check — and per CLAUDE.md
it **"drops most of what it dequeues."**

**So: at most 3 positions in the same direction can ever be live, no matter how many pairs
we scan.** Going from 105 → 500 pairs does not give us more signals. It gives the *same
number of slots* a larger candidate pool to choose from.

That is not worthless — a better selection pool is a real edge, if the additional
candidates are genuinely better. But it is a **selection-quality** change, not a
throughput change, and it must be justified and measured as one.

And here is the catch: the extra ~400 pairs are, by construction, **the ones with the
lowest volume** — we already scan the top 75 by volume, and the mover path already admits
anything with a >15 % move and >$5 M volume. What is left below that line is thin books,
wide spreads, and worse fills. The pair-quality gate (`spread too wide`) and
`SCAN_MIN_VOLUME_USD` exist precisely to keep those out. Expanding the universe means
either (a) they get suppressed anyway, so we burned 7× the CPU for nothing, or (b) they
displace a top-75 candidate for one of only 3 same-direction slots — **on worse
liquidity**. Option (b) is how you make PnL worse while feeling more thorough.

### Second-order cost: it dilutes Layer C

The Strategy×Context edge matrix needs `STRATEGY_EDGE_MIN_SAMPLES=15` per cell, and the
per-context emission policy needs `CONTEXT_EMISSION_MIN_SAMPLES=30`. Adding 400 illiquid
pairs adds samples — but they are samples from a *different liquidity regime* than the
one we trade. Cells fill faster with data that is less representative. Per CLAUDE.md, the
whole portfolio routes on this matrix. Polluting it is a money-path change, and it would
take a fresh measurement window to even detect.

---

## 9. Advantages of full-universe scanning — the honest case *for*

Steelmanning it, because there is a real case:

1. **Early listings.** A newly-listed perp has no volume history, so it never enters the
   top-75 — but new listings are often the most volatile, best-trending instruments on
   the exchange. *Partially covered today:* `!ticker@arr` sees it, and the ignition
   detector can promote it — but `MOVER_PROMOTION_MIN_VOLUME_USD=$5M` will gate a brand-new
   listing out for its first hours.
2. **Uncorrelated alpha.** Small caps decouple from BTC. Given that
   `MAX_SAME_DIRECTION_GLOBAL=3` exists *because* our universe is 0.85–0.95 BTC-correlated,
   genuinely uncorrelated pairs would let us safely hold more concurrent positions. This
   is the most interesting argument in the whole document.
3. **Larger candidate pool → higher-quality top-N.** If the scoring model is well
   calibrated, more candidates should raise the bar for what wins a slot.
4. **Richer edge-matrix coverage.** More strategy×context cells reach significance faster.
5. **Marketing / perception.** "We scan all 500+ pairs" is a stronger claim than "we scan
   75." (Weakest reason. Never let this drive architecture.)

Note that **#1 and #2 are the only ones that survive contact with §8**, and both are
better served by targeted admission rules than by brute-force scanning.

---

## 10. Disadvantages / risks — consolidated

| # | Risk | Severity |
|---|---|---|
| 1 | Scan cycle 16 s → ~107 s worst case; permanent backlog past the 1m bar | **Critical** |
| 2 | RAM ~6.7× against a hard 1 GB limit → OOM-kill → re-seed loop | **Critical** |
| 3 | Order egress via wrong IP → `-2014` on every user key → naked positions | **Critical** (only if IP work is done carelessly) |
| 4 | Event-loop saturation → delayed pongs → false WS-unhealthy → **scans less than today** | **High** |
| 5 | OI silently degrades to ~4 min stale, no error raised | **High** |
| 6 | Monitoring agent pages continuously (stale snapshot >90 s) on a healthy engine | **High** |
| 7 | Illiquid pairs displace liquid ones in only 3 same-direction slots | **High** (business) |
| 8 | Layer C edge matrix polluted with off-regime samples | **Medium** (business) |
| 9 | Boot seed ~7× longer; every `main` deploy runs degraded much longer | **Medium** |
| 10 | Weight utilisation ~10 % → ~60 %+; under-declared weights (§4.2) make 418 a live risk | **Medium** |
| 11 | Second IP in a Binance-restricted region = dead IP | **Low** (but wastes the spend) |
| 12 | More surface for TradFi-perp leakage (the `WDCUSDT` class of incident) | **Low** — `is_tradfi_perp` is structural and covers it |

---

## 11. What to measure before deciding anything

Per CLAUDE.md § Real-Data-First Diagnosis — get real numbers off prod first. All four are
minutes of work and all four are currently unknown:

```bash
# 1. Actual engine RSS against the 1 GB limit — this single number gates everything
docker stats --no-stream 360scalp-v2-engine

# 2. Real scan-cycle distribution over 24 h (not the Session-18 snapshot)
docker logs 360scalp-v2-engine --since 24h | grep "Scan stage timing" | tail -50

# 3. Real Binance weight utilisation — the "Binance minutes" answer
docker logs 360scalp-v2-engine --since 1h | grep -i "weight"

# 4. How often mover promotion is actually saturating its 30-pair cap
docker logs 360scalp-v2-engine --since 24h | grep -c "dynamically promoted"
```

**#3 has no ops surface today.** `rate_limiter.update_from_header` already parses the
authoritative `X-MBX-USED-WEIGHT-1M` header on every response and then discards it — it's
never published to Redis and there is no panel for it in `360ce-ops` (I checked all 24
route modules). We are flying without a fuel gauge on the one resource this whole question
is about.

**Concrete follow-up, off money path, ships normally:** publish
`futures_rate_limiter.usage_pct` into the engine snapshot and add a weight gauge to the
ops Pulse page. This is exactly the kind of thing the ops repo's `CLAUDE.md` means by
*"measured but nowhere to look is an unfinished change."* It should ship regardless of
what we decide about the universe.

---

## 12. Recommendation

### Don't do

- ❌ **Full-universe deep scanning on the current VPS.** It makes the engine slower,
  triggers false monitoring alerts, and risks OOM. The 1 GB / 1.5 vCPU container is the
  binding constraint and no IP fixes it.
- ❌ **A second IP framed as a scale unlock.** We use ~10 % of one IP's budget. It is not
  the bottleneck.

### Do — in this order

**1. Ship the weight gauge (this week, off money path, no gate).**
Publish `futures_rate_limiter.usage_pct` to the snapshot; add it to ops Pulse. We cannot
have a serious conversation about rate limits without it. Also fix or delete the dead
`api_limits.py` (§4.1) and correct the `weight=1` under-declaration on `/fapi/v1/trades`
(§4.2) — both are traps waiting for the next engineer.

**2. Widen mover promotion instead of the base universe (config change, dark-first).**
This captures ~80 % of the real upside for ~5 % of the cost, because it only pays deep-scan
cost on pairs that are *actually moving*:

| Setting | Now | Proposed | Why |
|---|---|---|---|
| `MOVER_PROMOTION_MAX_PAIRS` | 30 | 50 | Only binds when 50 pairs are genuinely igniting at once |
| `MOVER_PROMOTION_MIN_VOLUME_USD` | $5 M | $2 M | Lets fresh listings through (advantage #1) |
| `MOVER_IGNITION_MOVE_FLOOR_PCT` | 1.0 | tune from data | Sensitivity of the burst detector |

Peak scan set goes 105 → 125 — well inside current headroom — and it targets exactly the
pairs advantages #1 and #2 are about. Per CLAUDE.md § Project Phase this touches emission,
so: **measurement flag ON, user-visible effect OFF, shadow-measured on a real window,
owner sign-off to activate** — with the ops panel shipping alongside.

**3. Answer the uncorrelated-alpha question properly (research, not a config flip).**
Advantage #2 is the only argument that genuinely justifies more pairs, and it is testable
without scanning anything: we already compute rolling BTC correlation per symbol
(`_update_btc_correlation`). Measure which of the ~425 unscanned pairs are *persistently*
low-correlation to BTC. If there are 20 real ones, admit **those 20** by name — a
targeted +20 that raises the useful concurrent-position ceiling. If there are none, we
have closed the question with data instead of opinion. **This is the highest-value item
in the document.**

**4. Add the second IP — but for safety, not scale (optional, needs owner decision).**
The one argument that stands on its own is §5.3: a 418 ban on our only IP today can take
down market data *and* order placement simultaneously, for up to 3 days. Splitting read
traffic from order traffic removes that shared failure mode. If we do it, **§6's five
rules are mandatory and non-negotiable** — the signing container pins to IP #1, fails
closed, and asserts its own public IP at boot.

**5. If full-universe scanning is genuinely wanted — it's a hardware decision, not a
config one.** The honest shape is a dedicated scanner node: bigger box (4–8 vCPU, 8 GB+),
multiple engine processes sharded by symbol range, results into the existing Redis bridge.
That is a real project with a real monthly cost, and per § Cost Discipline it needs a
business case measured against §8's caps *first*. Given that the router can only deliver
3 same-direction positions regardless, **I do not think that case exists today.**

---

## 13. Open questions for the owner

1. **What is the actual goal** — more signals, better signals, or catching new listings
   early? Each has a different answer, and only the third one points at the universe size.
   (More signals is capped by the router; better signals is a selection problem.)
2. **Is the second IP already provisioned**, or is this a spend decision? If provisioned,
   what region — Binance geo-blocks by IP jurisdiction.
3. **Are we willing to raise `MAX_SAME_DIRECTION_GLOBAL`** if the correlation research
   (#3) finds genuinely uncorrelated pairs? Without that, even perfect universe expansion
   changes nothing downstream. This is an owner-sign-off item (blast-radius cap).
4. **What is the monthly budget ceiling** for VPS upgrade, if #5 is on the table?

---

## 14. Sources

Binance documentation, retrieved 2026-07-27:

- [USDⓈ-M Futures — General Info (rate limits, 418/429 bans)](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info)
- [Binance Futures Rate Limits — VIP Tiers, Sub-Accounts (2,400 req/min per IP; 1,200 orders/min per account; 300 orders/10 s)](https://www.binance.com/en/support/faq/detail/281596e222414cdd9051664ea621cdc3)
- [WebSocket Market Streams — Connect (1,024 streams/connection; 10 incoming msg/s; 24 h connection lifetime; 3 min ping)](https://developers.binance.info/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Connect)
- [Exchange Information — `rateLimits[]` (`REQUEST_WEIGHT` 2,400/min)](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information)
- [Rate Limiting and IP Bans — per-IP weight vs per-key order limits; multiple IPs recommended at scale](https://deepwiki.com/binance/binance-spot-api-docs/1.3-rate-limiting)
- [Kline Candlestick Data (limit-bracket weights — table did not render; unverified, see §4.2)](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data)
- [Binance Futures market statistics (~746 total futures pairs, all contract types)](https://www.coingecko.com/en/exchanges/binance_futures)

Engine sources: `config/__init__.py`, `src/scanner/__init__.py`, `src/rate_limiter.py`,
`src/api_limits.py`, `src/order_flow.py`, `src/pair_manager.py`, `src/bootstrap.py`,
`src/websocket_manager.py`, `src/historical_data.py`,
`src/security/binance_connect_validator.py`, `docker-compose.yml`,
`ACTIVE_CONTEXT.md` § Session 18, `lumin-app/lib/features/settings/pages/server_side_execution_page.dart`.

**Not verified in this session:** the exact current count of USDT-M perpetuals (Binance
is geo-blocked from this sandbox — CoinGecko's 746 covers all contract types). Get the
real number on the VPS:

```bash
curl -s https://fapi.binance.com/fapi/v1/exchangeInfo \
  | jq '[.symbols[] | select(.contractType=="PERPETUAL" and .quoteAsset=="USDT" and .status=="TRADING")] | length'
```
