# Handoff — Session 86 start

**Written:** 2026-07-27 · **From:** Session 85 (VPS capacity measurement + universe research)
**Read after** `OWNER_BRIEF.md` and `ACTIVE_CONTEXT.md`.
**Primary artefact:** `docs/UNIVERSE_EXPANSION_AND_SECOND_IP_2026_07_27.md`

---

## 0. Read this first — the 60-second version

The owner asked whether we could add a second VPS IP and scan the full Binance futures
universe. The answer is no, but the investigation turned up something better: **we had
the engine capped at 1.5 of the host's 4 cores and it was running at 87 % of that cap.**
Three cores were idle behind a limit we set ourselves.

Nothing about the universe question needs re-deriving — it is closed and code-grounded.
What is *open* is a deploy decision and one very specific QCB thread (§4), which is the
most valuable thing on this list.

---

## 1. Open PRs — state on handoff

| PR | What | State | Needs |
|---|---|---|---|
| [#803](https://github.com/mkmk749278/360-v2/pull/803) | Universe/second-IP research doc + `scripts/diag_capacity.sh` | **Draft, CI green, mergeable clean** | Owner merge decision |
| [#805](https://github.com/mkmk749278/360-v2/pull/805) | Engine container caps 1.5→2.5 cores, 1g→3g; redis capped | **Draft, CI pending** | **Owner deploy timing** — recreates engine, triggers re-seed |

Neither is auto-mergeable: #803 is the owner's call to read, #805 needs a quiet window
because applying it re-seeds 7 timeframes × ~3,200 candles × 75 pairs.

**Do not** merge #805 without confirming the owner has picked a deploy window.

---

## 2. What was measured (do not re-derive — run the script instead)

`scripts/diag_capacity.sh` (ships in #803) was run on production 2026-07-27:

| | Measured | Read |
|---|---|---|
| Host | **4 cores / 7.8 GB** | at **~25 % load** |
| Engine CPU | **130 % of a 150 % cap** | **~87 % of allowance** |
| Engine RAM | **459 MB / 1 GB** | 45 %, **zero OOM kills, 0 restarts** |
| Scan-cycle timing | **not logged** | `SCAN_STAGE_TIMING_ENABLED` is OFF |

**Safe pair ceiling: ~85 today → ~120–145 after #805.** Full universe (~500 pairs) needs
**8–9 cores** for the engine alone; this box has 4, so it stays a hardware project.

### Two corrections to earlier analysis — carry these forward

1. **RAM was never the constraint.** The first research draft called it a *Critical*
   risk ("6.7× against a 1 GB limit → OOM-kill → re-seed loop"). Measured: 459 MB, never
   OOM-killed. That was an arithmetic guess dressed as a finding. Marked measured-false
   in the doc.
2. **Extrapolating from scan wall-clock hides Docker throttling.** The original CPU
   projection was built from cycle times, and throttling lives *inside* cycle times.
   Measuring CPU consumption directly is what exposed the 87 %. **When capacity is the
   question, measure CPU, not latency.**

---

## 3. The universe question — closed, don't re-open

Three things get conflated in "scan the full universe". They have different answers:

- **Knowing** what every pair does → **already solved.** `!ticker@arr` gives full-universe
  awareness (~500+ pairs, 1/sec) on one WS connection for zero REST weight.
- **Deep-scanning** every pair → CPU-bound, see §2.
- **Emitting** more signals → **hard-capped and this is decisive.**
  `MAX_SAME_DIRECTION_GLOBAL=3`, `MAX_SCALP_SIGNALS=5`. More pairs cannot produce more
  delivered signals — only a different candidate pool for the same 3 slots. And the extra
  pairs are by construction the *least* liquid.

**Binance limits are not the bottleneck.** We run at ~10 % of one IP's 2,400/min futures
weight budget. Weight is per-IP; **order limits are per-account**, so a second IP buys
exactly zero order throughput.

### ⚠️ If anyone proposes a second IP, read §6 of the research doc first

Every server-side auto-trade user has whitelisted **exactly one VPS IP**. If order
traffic egresses from a second IP, every key returns `-2014` — **including stop-loss
placement on an open position.** Direct hit on the naked-position invariant. Egress
pinning must be OS-level per container (there are ~20 `ClientSession()` sites in `src/`)
and the signing container must **fail closed**.

---

## 4. 🔴 The QCB thread — highest-value item on this list

The owner asked: *"our concentration, we may get more chances for QCB path right?"*
The instinct is right; the mechanism is not what it looks like. **This is the thing to
pick up first.**

### The numbers

`QUIET_COMPRESSION_BREAK` is one of the few genuinely positive paths we have:

| Measure | Value | Source |
|---|---|---|
| Best cell | **+2.21R** (OVERLAP / QUIET / COMPRESSED) | `ACTIVE_CONTEXT.md:1498` |
| Live EV | **+0.17R** — one of only two positive live paths | `ACTIVE_CONTEXT.md:2600` |
| **Emission in that cell** | **0 out of 1,055** | `ACTIVE_CONTEXT.md:1498` |
| Cell sample count | **n = 29** | `ACTIVE_CONTEXT.md:1264` |
| Relax floor | **n ≥ 30** | — |

**QCB's best cell is one sample short of the threshold that would unlock it.**

### So does a wider universe give "more chances"?

**Yes, but not the way it sounds — and this reframes the whole ask.**

- More pairs → **proportionally** more QCB candidates. `VOL_COMPRESSED` is a *per-symbol*
  ATR percentile (bottom 20th, `market_context.py:144`), **not** an absolute volatility
  measure. So roughly 20 % of any pair set is COMPRESSED at any time regardless of
  liquidity. 75 → 125 pairs ≈ **+67 % QCB candidates**, linearly.
  *(Do not claim illiquid alts are "more often compressed" — the percentile normalises
  that away. I nearly asserted it; the code says otherwise.)*
- **But QCB's bottleneck is not candidate supply.** It converts **0 of 1,055**. Feeding
  more candidates into a 0/1055 converter yields 0/1,760.
- **The real benefit is measurement velocity.** More candidates fill that n=29 cell
  faster → it crosses n≥30 → the Layer G controller relaxes the floor → **QCB starts
  emitting.** That is a genuine, specific, defensible reason to widen the universe. It is
  not a throughput argument.

### The fix may already be in flight — check this first

Layer G (`src/emission_controller.py`) shipped specifically to self-promote
`QCB min_samples 30→25` (`ACTIVE_CONTEXT.md:1297`). Envelope:
`min_samples_ceiling=30`, `min_samples_step=5`, `min_samples_floor=15`. **One step
unlocks the cell.**

**First action of Session 86:**

```bash
git fetch origin monitor-logs
git show origin/monitor-logs:monitor/analysis/emission_controller.json
```

- **If QCB has been promoted to 25** → the cell is unlocked. Measure whether QCB is now
  actually emitting, and whether the +2.21R survives contact with live dispatch
  (remember: counterfactuals are optimistic, ~0.38R measured on MTP — never quote the
  cell R as an expected live result).
- **If it has not** → find out why. Boot-grace? K-cycle stability not met? EV-magnitude
  bar? That is a more valuable question than anything about universe size, because it
  gates a **+2.21R path that currently emits nothing.**

### Why this beats the universe work

Widening the universe is a ~67 % increase in candidates for a path converting at 0 %.
Unlocking the emission floor is the difference between **0 and non-zero**. Do the second
one first. If Layer G is already handling it, the universe work becomes a
"fill cells faster" optimisation — worth doing, but second.

---

## 5. Traps and follow-ups found while measuring

| # | Finding | Status |
|---|---|---|
| 1 | **`SCAN_STAGE_TIMING_ENABLED` is OFF** — we have *no* scan-cycle data. Every per-pair cost figure is inferred from a CPU snapshot. The 16 s number quoted throughout is from **2026-06-04** and predates substantial evaluator work | **Open — enable alongside #805 deploy** |
| 2 | **No Binance weight gauge anywhere.** `rate_limiter.update_from_header` parses the authoritative `X-MBX-USED-WEIGHT-1M` on every response and discards it. No ops panel across any of the 24 route modules in `360ce-ops` | **Open** — off money path, ships normally |
| 3 | **`src/api_limits.py` is dead code with a wrong constant.** `BINANCE_WEIGHT_LIMIT_PER_MINUTE = 1200` is the old *spot* limit (futures is 2,400). Instantiated at `scanner/__init__.py:1425-1426`, then never read. First hit when you grep for the weight limit | **Open** — delete or fix |
| 4 | **`/fapi/v1/trades` declared `weight=1`** at `historical_data.py:144,150` while fetched with `limit=1000`. Under-declaring makes our limiter *optimistic*. Invisible at 10 % utilisation; at 60 % it is how you earn a 418 ban | **Open** |
| 5 | **Three uncapped containers remain in the `360ce-ops` repo** (`360ce-ops`, `360ce-ops-agent`, `360ce-ops-redis` — all `cap=none`). #805 fixes the two in this repo. An unbounded leak there exhausts the host and takes the engine with it | **Open — separate PR in 360ce-ops** |
| 6 | **`OIPoller` is sequential and degrades silently.** 2 REST calls/symbol with a 0.1 s gap, then `sleep(60)`. OI freshness: ~90 s at 75 pairs → ~260 s at 500. Nothing raises an error — it just gets quietly worse | Documented; only matters if the universe grows |

---

## 6. Verified facts worth not re-checking

- Futures REST weight: **2,400/min per IP**. Orders: **300/10 s + 1,200/min per account**,
  and **sub-accounts share the parent pool**.
- WS: **1,024 streams/connection**, 24 h connection lifetime, **10 outgoing msg/s**
  (that limit is on frames *we send*, not inbound data).
- **Multiple IPs are explicitly recommended by Binance** at scale — not a ToS risk.
- **Binance enforces geo-eligibility per IP.** A `curl` from the CI sandbox returns
  *"Service unavailable from a restricted location."* Any second IP must be in a served
  jurisdiction.
- Exact USDT-M perp count is **unverified** — get it on the VPS:
  ```bash
  curl -s https://fapi.binance.com/fapi/v1/exchangeInfo \
    | jq '[.symbols[] | select(.contractType=="PERPETUAL" and .quoteAsset=="USDT" and .status=="TRADING")] | length'
  ```

---

## 7. Suggested order for Session 86

1. **Check Layer G / QCB promotion status** (§4). Highest value by a distance.
2. **Confirm #805 deploy window with the owner**, then apply and re-run
   `scripts/diag_capacity.sh` to verify the new caps took.
3. **Enable `SCAN_STAGE_TIMING_ENABLED`** in the same deploy; wait an hour; re-measure to
   replace the inferred per-pair cost with a real one.
4. **Ship the weight gauge** (trap #2) — off money path, no gate, and we cannot have an
   honest rate-limit conversation without it.
5. **Only then** consider widening `MOVER_PROMOTION_MAX_PAIRS` 30→50 — and per
   § Project Phase it touches emission, so: measurement flag ON, user-visible OFF,
   shadow window, owner sign-off, ops panel alongside.

**Do not** start the second-IP work, the universe expansion, or a VPS upgrade without
re-reading §8 of the research doc. The router caps mean none of them increase delivered
signal volume.
