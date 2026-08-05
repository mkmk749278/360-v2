# Price Action — What It Is, What We Have, and What We Are Building

**Status:** design of record. Written 2026-08-05, before any code.
**Owner request:** *"we need to Measure them as Live signals not as setups… what actually price action is, how we can predict signals using price action, and not only limited to one path where we can apply it and how… what actually we are reading data from Binance and what else needed."*

This document is the answer to those questions and the build plan that follows from
it. It commits to a specific program. There are no open "which one shall we build"
questions left in it by design — where a choice existed, this document makes it and
says why.

Two standing rules from `CLAUDE.md` govern everything below, and they are why this
document exists before the code:

- **Re-check the claim before you test it.** Every fact here is labelled
  **[verified]** (read from our source tree or an official vendor page during
  this session) or **[documented]** (taken from vendor docs I could read but not
  independently exercise) or **[inferred]**. An unlabelled inference reads exactly
  like a measurement.
- **A finding and a fix are separate deliverables.** Sections 1–5 are findings.
  Section 6 onward is the build.

---

## 0. Executive summary

1. **Price action is four layers, not one thing**: context (where are we in the
   auction), location (which prices matter), trigger (what happened at that
   price), confirmation (is anyone behind it).
2. **We have layers 1 and 2 and they are in good shape.** `LevelBook` is real,
   wired, multi-timeframe, and fed by volume profile. This was better than
   expected.
3. **We do not have layer 4 at all.** Our "CVD" is one delta number per closed
   bar, derived from the kline's taker-buy field. Our "order book" is one bid and
   one ask. The confirmation layer is the one the published evidence actually
   supports, and it is the one we cannot see.
4. **Layer 3 is half-built.** Two of its primitives are hollow: the order-block
   detector has never been implemented, and FVG detection sees twelve bars.
5. **The evidence is a warning, not an endorsement.** A controlled test of 54
   mechanical SMC rule variants over 2.5M bars produced a best win rate of 56.3%
   and **zero profitable variants after costs**. Our own book already loses ~10×
   its edge to fees. A price-action lane that produces 56% is a losing lane.
6. **Therefore we build the measurement before the signal**, and we build the
   missing data layer before the measurement. The order in §6 is not a
   convenience; reversing it produces an unfalsifiable lane.
7. **The Binance limits do not block this.** WebSocket market streams consume
   **no REQUEST_WEIGHT**. Both missing layers move to WebSocket. The binding
   constraint becomes our own CPU and memory, which we control, instead of a
   vendor quota, which we do not.

---

## 1. What price action actually is

Price action is not a pattern catalogue. It is a four-layer read, and every
credible framework — Smart Money Concepts, Auction Market Theory, Wyckoff — is a
different vocabulary over the same four layers.

| Layer | The question it answers | Primitives |
|---|---|---|
| **1. Context** | Where are we in the auction? | trend / range, HTF bias, value area, POC, session |
| **2. Location** | Which prices matter? | swing highs/lows, prior day & week H/L, round numbers, VAH/VAL, untested levels |
| **3. Trigger** | What just happened *at* that price? | break of structure (BOS), change of character (CHoCH), sweep + reclaim, failed auction, displacement |
| **4. Confirmation** | Is anyone actually behind it? | delta / CVD, absorption, volume expansion at price, follow-through |

The two vocabularies:

- **SMC / ICT** — order blocks, fair value gaps, BOS/CHoCH, liquidity sweeps.
  Better-defined *triggers*, weaker measurement discipline.
- **Auction Market Theory / Wyckoff** — POC, value area, HVN/LVN,
  accumulation/distribution. Better-defined *measurements*, vaguer triggers.

They are not rivals. AMT tells you which prices are worth watching; SMC tells you
what event at that price is worth acting on. A serious implementation uses AMT for
layers 1–2 and SMC-style events for layer 3 — which, as §3 shows, is close to what
our `LevelBook` plus the structural evaluators were already reaching for.

**Definitions used throughout this document** (so the code and the doc cannot
drift):

- **Swing high / low** — a bar whose high (low) is the local extreme within ±N
  bars. N is the confirmation width; a swing is not confirmed until N bars have
  closed after it. *A swing that is not yet confirmed does not exist.*
- **BOS (break of structure)** — price closes beyond the most recent confirmed
  swing in the direction of the prevailing trend. Continuation.
- **CHoCH (change of character)** — price closes beyond the most recent confirmed
  swing *against* the prevailing trend. The first structural evidence of a
  reversal.
- **Sweep** — price trades *through* a confirmed swing (or other level) and
  closes back on the originating side within a bounded number of bars. A sweep is
  a failed break, and it is the only trigger in this document with direct
  empirical support behind its premise (§2).
- **Reclaim** — after a sweep, price closes back beyond the swept level in the
  opposite direction. Sweep + reclaim is the entry event.
- **Displacement** — an impulsive move whose range is a large multiple of recent
  average range, indicating the break was not an accident.
- **Delta** — signed aggressive volume: taker-buy minus taker-sell.
- **CVD** — cumulative delta over time.
- **Absorption** — high volume at a price with little price movement; resting
  limit orders soaking up aggression. Requires per-price volume to see.

---

## 2. What the published evidence actually supports

This section exists because the industry literature on price action is largely
marketing, and building on the marketing would waste a quarter.

Reviewed during this session: an evidence survey aggregating peer-reviewed
microstructure work ([IndicatorEdge](https://indicatoredge.io/smart-money-research)),
practitioner critiques
([Power Trading Group](https://www.powertrading.group/options-trading-blog/truth-about-ict-smart-money-concepts-rebranded-principles),
[AlgoStorm](https://algostorm.com/ict-smc-realistic-overview/)), the structural
definitions ([LuxAlgo](https://docs.luxalgo.com/docs/algos/price-action-concepts/market-structures),
[DailyPriceAction](https://dailypriceaction.com/blog/smc-market-structure/)),
auction theory ([Trading Wyckoff](https://tradingwyckoff.com/en/auction-market-theory/),
[FinancialTechWiz](https://www.financialtechwiz.com/post/auction-market-theory/)),
and order-flow practice
([OrderFlow Labs](https://orderflowlabs.com/blogs/theblog/footprint-chart-guide),
[NinjaTrader](https://ninjatrader.com/futures/blogs/ninjatrader-order-flow/)).

| Component | Status | What the research says |
|---|---|---|
| **Round-number / swing-level stop clustering** | **Supported** | Among the most replicated microstructure findings. Osler (2000, 2003, 2005), Harris (1991), Bhattacharya et al. (2012), Brunnermeier & Pedersen (2005). Stops genuinely cluster at obvious levels and reaching a cluster genuinely triggers cascades. |
| **Session-time volatility clustering** | **Supported** | Wood et al. (1985), Harris (1986), Andersen & Bollerslev (1997, 1998). Robust across decades. **But** no evidence the pattern alone beats transaction costs. |
| **Signed order imbalance moves price** | **Supported** | Direct, measurable, and the foundation of layer 4. |
| **Fair value gaps** | **Unvalidated** | No peer-reviewed validation of the three-candle construct. The common "gaps always fill" claim is *contradicted* — gaps more often continue in their direction. |
| **Order blocks; BOS as a distinct construct** | **No validation found** | Not distinguishable in the literature from classic support/resistance. |
| **Accumulation → manipulation → distribution** | **Folklore** | Descriptive practitioner texts, no statistical testing of the intraday three-phase model. |
| **Fibonacci "optimal entry"** | **Failed testing** | Fibonacci zones performed no better than randomly chosen non-Fibonacci zones under controlled test. |

**The single most important number in this document** [documented]: a controlled
backtest over 2.5M EURUSD bars (2019–2025) tested **54 mechanical SMC rule
variations**. Best win rate **56.3%**. **Zero of 54 profitable after 0.5-pip
costs.** The stated conclusion was not that the patterns are absent — it was that
the patterns are real *and a precise mechanical rule built on them did not produce
an edge*.

### 2.1 What this means for us, concretely

Our own `/track-record` measured the owner's 30-day window at **−$3.21 gross and
−$34.57 net** at $100/signal — the cost of trading is roughly **10× the edge**. A
lane that produces a 56% win rate on 1:1 geometry is not marginal for us; it is
comfortably negative.

Three consequences, all binding on the build:

1. **We build on the supported column.** Levels where stops demonstrably cluster
   (layer 2, which we have), sweeps of those levels (layer 3), and order-imbalance
   confirmation (layer 4, which we lack). We do **not** build a lane whose
   trigger is "an order block exists" or "an FVG exists", because those constructs
   have no validation and we would be spending a quarter to reproduce a null.
2. **Cost is charged from the first measurement, not at the end.** Every figure
   this program produces is published gross *and* net of a round-trip fee, on the
   same screen. This is already the `/track-record` rule; it now applies to the
   price-action lane from day one, because a gross-only price-action number is
   precisely the artefact the 54-variant test warns about.
3. **The lane must be able to return "no edge".** The program is instrumented to
   produce a negative verdict and ship it. If the honest outcome is that
   structural triggers add nothing to this book, that is a successful outcome of
   this program and it saves the engineering that would otherwise follow.

---

## 3. What we read from Binance today — audit

All items in this section are **[verified]** by reading the source tree on
2026-08-05.

### 3.1 WebSocket streams we subscribe

| Stream | Coverage | Source |
|---|---|---|
| `{sym}@kline_1m` | every scanned pair | `bootstrap.py:909` |
| `{sym}@kline_5m` | every scanned pair | `bootstrap.py:910` |
| `{sym}@kline_15m` | conditional | `bootstrap.py:925` |
| `{sym}@kline_1h` | conditional | `bootstrap.py:926` |
| `{sym}@kline_4h` | conditional | `bootstrap.py:927` |
| `{sym}@forceOrder` | every scanned pair, separate pool | `bootstrap.py:933` |
| `!ticker@arr` | whole board, ~1/sec, own connection | `bootstrap.py:976` |

### 3.2 REST endpoints we call

`/fapi/v1/klines` (seeding and gap-fill) · `/fapi/v1/ticker/bookTicker` ·
`/fapi/v1/openInterest` (1/min poller) · `/fapi/v1/premiumIndex` (funding) ·
`/fapi/v1/exchangeInfo` · `/fapi/v1/depth` (**declared but not used on the scan
path** — see §3.5) · plus the trading endpoints, which are out of scope here.

Seeded timeframes (`config/__init__.py:1627`): **1m, 5m, 15m, 1h, 4h, 1d at 500
bars; 1w at 200**. Retention `_MAX_CANDLES_PER_BUCKET = 1_000`
(`historical_data.py:43`).

### 3.3 What is healthy — better than expected

**`LevelBook` is real and wired.** `scanner/__init__.py:4754` calls
`level_book.refresh(symbol, tf_inputs, volume_profile=vp_results or None)` with
`tf_inputs` drawn from **1w / 1d / 4h / 1h**, and with **two** volume profiles —
micro (1h) and macro (1d) — whose POC/VAH/VAL participate in level clustering and
confluence scoring.

That is a genuine auction-theory level engine already running in production. I
initially suspected `volume_profile` was another dead parameter of the
`candle_highs` kind and **checked the call site rather than assuming** — it is
live. Layers 1 and 2 are not the problem.

### 3.4 What is hollow — layer 3

**The order-block detector has never existed.** `SMCResult` declares
`orderblocks: List[Dict[str, Any]]` and
`orderblocks_detector_status: str = "not_implemented"` (`detector.py:79–80`), and
the field is **never assigned anywhere in `detector.py`** — the only three
occurrences are the declaration, the status default, and the `as_dict()` copy.

Consequence: every gate in `channels/scalp.py` of the form
`bool(fvgs) or bool(orderblocks)` — including `has_smc_support` at line 1822 and
`has_smc_context` at 2679 and 2949 — has **always** been `bool(fvgs)` alone. Half
of each of those structural checks has never had a writer.

**FVG detection sees twelve bars.** `detect_fvg(..., lookback: int = 10)`
(`smc.py:244`). On a 15m chart that is three hours. A gap from yesterday's
structure does not exist as far as any evaluator is concerned. `CLAUDE.md` already
records the consequence: the narrow lookback is what makes the deliberately loose
`bool(fvgs)` gate behave like a strict one, because any gap it can find is by
construction near price.

### 3.5 What is missing entirely — layer 4

**Our CVD is not order flow.** CVD is computed in `main.py:1451–1470` from the
*closed kline's* `Q` (taker-buy quote volume) and `q` (total quote volume), for
the 1m and 15m intervals. So what we call CVD is **one signed number per closed
bar** — no per-price-level volume, no trade-size distribution, no absorption, no
intra-bar sequencing. The comment at the call site is candid about why: it works
during REST fallback, which sends kline events and never trade events.

**But the tick plumbing is ~90% built and disconnected — and five consumers are
reading a stale snapshot through it.** This is the most consequential thing the
audit found and it was nearly missed:

- `main.py:1476–1483` has a **complete `trade` event handler** that builds
  `{price, qty, isBuyerMaker, time}` — exactly the footprint primitive — and
  appends it via `data_store.append_tick`.
- `historical_data.py:936` implements `append_tick` with a rolling
  `SEED_TICK_LIMIT` (1,000) cap.
- `websocket_manager.py:1116` defines `build_trade_stream()` → `{symbol}@trade`.
- **Nothing subscribes it.** There are exactly three `.start()` calls in
  `bootstrap.py` — kline streams (959), forceOrder streams (961),
  `!ticker@arr` (976). No trade stream, and `@aggTrade` appears nowhere. The
  handler is unreachable in production.

So `data_store.ticks[symbol]` is populated **once**, at seed time, by
`fetch_recent_trades` → `/fapi/v1/trades?limit=1000` (`historical_data.py:150`,
called from `_seed_symbol`'s `_fetch_ticks` at 218) — a one-shot snapshot of the
last 1,000 trades at whatever moment the symbol was seeded, and never refreshed.

**Five call sites read it as though it were live**: `scanner/__init__.py` at 1704,
3082, 3158 and 8681, and `trade_monitor.py:1083`. It reaches evaluators as
`smc_data["recent_ticks"]`, and `channels/scalp.py:2283–2288` gates on it with
`missing_recent_ticks` / `recent_ticks_empty` telemetry. The comment at
`scalp.py:124` describes a `$500k of cumulative tick volume` threshold — computed,
today, from trades captured when the symbol was seeded. For a core pair that is
boot time; for a promoted mover, promotion time.

This is the `is_tradfi_perp` class again: a mechanism that looks wired end to end,
has telemetry, has a gate reading it, and is fed by a source that stopped being
current the moment it was written. **It is a live correctness defect, not merely a
missing feature** — and it makes Phase 2 substantially cheaper than a greenfield
build, because the store, the cap, the consumers and the gate telemetry all exist.
What is missing is the subscription and a bar-aligned aggregation on top.

*(Related staleness, worth knowing before reading the file: `volume_profile.py`'s
own docstring closes with "Wiring (deferred) … this PR ships infrastructure only.
No scanner changes, no scoring side-effects." That sentence is **out of date** —
`scanner/__init__.py:4754` does pass volume profiles into `LevelBook.refresh`, as
§3.3 verifies. The code is live; the docstring is stale. I initially read that
docstring as evidence the module was dead and checked the call site instead of
trusting it.)*

**Our order book is one level deep.** `scanner/__init__.py:2981` builds the
order-book snapshot from `bookTicker`:

```python
self._order_book_snapshot_cache[symbol] = ({
    "bids": [[best_bid, bid_qty_f]],
    "asks": [[best_ask, ask_qty_f]],
    "source": "book_ticker",
    "depth_quality": "top_of_book_only",
}, now + _BOOK_TICKER_CACHE_TTL)
```

The snapshot literally carries `depth_quality: "top_of_book_only"`. This was a
deliberate choice — `binance.py:249` describes `bookTicker` as "the
weight-efficient alternative to per-symbol `/depth`" — and it was the right call
for a spread check. It is not a book. `entry_features.book_imbalance` therefore
divides best-bid quantity by best-ask quantity, which cannot see a wall, a
refill, or absorption.

**`volume_profile.py` says this about itself** (module docstring): the profile is
built by distributing each candle's volume uniformly across its `[low, high]`
range, and it is *"NOT precise enough for buy-vs-sell delta analysis, footprint
charts, or single-print imbalances. Those need tick data which we"* — the sentence
is cut off in the source, but the point stands and it is correct.

### 3.6 The audit in one table

| Layer | Needs | We have | Verdict |
|---|---|---|---|
| 1 Context | HTF candles, volume profile, regime | 1w/1d/4h/1h + micro & macro VP + `regime.py` | **healthy** |
| 2 Location | multi-TF levels, round numbers, VAH/VAL | `LevelBook`, wired, clustered | **healthy** |
| 3 Trigger | swings, BOS/CHoCH, sweeps, displacement | swings ✅ · FVG 12-bar · **order blocks absent** | **half-built** |
| 4 Confirmation | per-price volume, delta, absorption | bar-level delta only · top-of-book only · **tick store fed by a seed-time snapshot** | **absent, and actively misleading** |

**The honest read: we have the map and not the flow.** We can say precisely which
price matters and we cannot say whether anyone is defending it. That is the gap,
and it happens to be the layer with the strongest published support.

**And one thing in layer 4 is worse than absent.** An absent input fails loudly —
`recent_ticks_empty` would have been a rejection anyone could see. A *stale* input
does not: it returns plausible numbers of the right shape, so the gate passes or
rejects on trades from hours ago and nothing anywhere says so. Fixing that is not
part of the price-action program's upside; it is a correctness repair the program
happens to surface, and it is sequenced accordingly (§6, Phase 2).

---

## 4. Binance limits, and how this program stays inside them

### 4.1 The limits

| Limit | Value | Status |
|---|---|---|
| REST `REQUEST_WEIGHT` (USDⓈ-M futures, per IP) | **2,400 / minute** | [documented], and matches `binance.py:29` `_DEFAULT_FUTURES_WEIGHT_LIMIT = 2_400` |
| `/fapi/v1/depth` weight by limit | 5/10/20/50 → **2**; 100 → **5**; 500 → **10**; 1000 → **20** | [documented] |
| `/fapi/v1/aggTrades` weight | **20**, fixed regardless of limit | [documented] |
| `/fapi/v1/aggTrades` history | **24 hours only**; `startTime`–`endTime` window must be **< 1 hour** | [documented] |
| WS streams per connection | **1,024** | [documented] |
| WS messages *sent to Binance* per second | **10** | [documented] |
| WS connection lifetime | **24 hours**, then disconnect | [documented] |
| WS connection attempts | **300 per 5 minutes per IP** | [documented] |

I could not read the `/fapi/v1/klines` weight-by-limit table from the vendor docs
during this session, and the live `exchangeInfo` endpoint returns **HTTP 451** to
our build sandbox (geo-block), so it is not asserted here. It does not need to be
— see §4.3.

### 4.2 The decisive fact: WebSocket market streams cost no REQUEST_WEIGHT

REQUEST_WEIGHT is a REST quota. A market-data WebSocket stream consumes none of
it, at any message rate. This single fact determines the whole data plan.

Consider the REST alternatives for layer 4:

- **Depth via REST.** `/fapi/v1/depth?limit=20` is weight 2. At scan cadence (15s
  → 4×/min) across 75 pairs that is **600 weight/minute — 25% of the entire
  budget** for a 20-level snapshot four times a minute, which is far too coarse to
  see absorption anyway. At `limit=100` it is 1,500/min, **62% of budget**.
  Rejected.
- **Trades via REST.** `/fapi/v1/aggTrades` is weight 20 *per call*. Polling 75
  pairs once a minute is **1,500 weight/minute — 62% of budget** — for data that
  arrives up to a minute late and cannot be aligned to bar boundaries reliably.
  Rejected.

Both are affordable **only** over WebSocket, where they are free of weight.

### 4.3 Weight is enforced from the exchange's own header, not from a table

We already do the right thing here and it should be stated so nobody replaces it
with a doc table: `binance.py:161–167` reads `x-mbx-used-weight-1m` off every
response and **syncs the local counter from it**; `rate_limiter.py` is the shared
gate and `_DEFAULT_FUTURES_WEIGHT_LIMIT` is only the pre-first-response default.

That is why the missing klines table is not a blocker: **the budget is measured,
not assumed.** A weight table in a document is a mirror of the vendor's rules and
mirrors drift; the header is the vendor telling us the answer on every call.

**One defect found while auditing this** [verified]: `api_limits.py:21` declares
`BINANCE_WEIGHT_LIMIT_PER_MINUTE: int = 1200` — a **second, stale copy** of a
limit that is 2,400 in `binance.py`. Two readers of one fact, and this one is
wrong by half. It is fixed as item 0 of the build (§6), because a program about
staying inside a quota must not ship on top of a quota constant that disagrees
with itself.

### 4.4 The stream budget

Current subscriptions, at a nominal 75 scanned pairs:

| Streams | Count |
|---|---|
| klines (5 intervals × 75) | 375 |
| forceOrder × 75 | 75 |
| `!ticker@arr` | 1 |
| **Today** | **451** |
| `+ @aggTrade × 75` (Phase 2a) | 75 |
| `+ @depth20@100ms × 75` (Phase 2c) | 75 |
| **Program total** | **601** |

601 is inside the 1,024-per-connection ceiling, and we already run separate
connection pools (klines / liquidations / mover), so headroom is comfortable.
**Streams are not the constraint.**

### 4.5 What actually constrains us, and the mitigations

The real costs of Phase 2 are ours, not Binance's:

| Constraint | Reality | Mitigation (built, not assumed) |
|---|---|---|
| **Message volume** | `@aggTrade` on an active pair runs tens of messages/sec. 75 pairs is plausibly ~1–3k msg/s. | The handler does **no allocation per message**: it folds each trade into a pre-allocated per-symbol bar accumulator (price bin → buy/sell volume) and returns. No dict construction, no logging, no async hop on the hot path. |
| **Memory** | Per-price-level volume per bar per symbol is the largest structure we would have ever held. | Fixed bin count per bar, fixed bar ring (see §6 Phase 2 for the sizing), pre-allocated numpy arrays, and a hard cap that **refuses to grow** rather than silently trimming. |
| **Subscribe rate** | 10 messages/sec *to* Binance. Mover promotion churns symbols every 6h, and a 24h disconnect re-subscribes everything at once. | Subscriptions are **batched** into combined-stream frames and paced under the limit by the existing `websocket_manager`; re-subscribe after the 24h cycle is staged, not stampeded. |
| **24h forced disconnect** | Every connection dies daily. | Already handled by `websocket_manager`'s reconnect. The new accumulator must treat a reconnect gap as **a hole it names**, not as zero volume — see the freshness rule in §6. |
| **Bandwidth** | Continuous, unlike our current bursty kline traffic. | Phase 2 ships on a **bounded symbol set** first (§6), with the whole-universe rollout gated on the measured cost from the data-intake page we build in Phase 1. |

**Scope note, stated plainly:** `@aggTrade` gives us *aggressive* volume at price —
that is genuine footprint and it is what delta, absorption and imbalance are built
from. It does **not** give us resting liquidity; that needs the depth stream
(Phase 2c). Nothing in this program claims to see hidden or iceberg orders,
because nothing in this data can.

---

## 5. Where price action applies — six places, and we use it in one

The owner's question: *"not only limited to one path where we can apply it and
how"*. Price action is not a strategy slot. It is a lens that applies at six
distinct points in the pipeline, and we currently use it at one and a half.

| # | Application | What it does | Today | Population it can be tested on |
|---|---|---|---|---|
| 1 | **Universe / regime** | trade only symbols in a readable structure | not used | whole scan universe |
| 2 | **Trigger** | structure *generates* the signal | **0.62%** of enqueues | tiny — must be grown |
| 3 | **Entry timing** | wait for the retest/reclaim instead of entering at signal | not used | every delivered signal |
| 4 | **Geometry (SL/TP)** | stop behind structure, target at the next level | the structural snap — dark, ~zero measured effect | every enqueued signal |
| 5 | **Exit management** | trail on structure rather than ATR | not used | every open position |
| 6 | **Veto filter** | *do not* take an MA signal straight into a level | **not used** | **97% of the book, immediately** |

Measured on the 2026-08-05 export (2,418 stamped signals over 19 hours):
structurally-triggered paths produced **15 rows, 0.62%**, and **zero of them
delivered**. `SR_FLIP_RETEST`, `CONTINUATION_LIQUIDITY_SWEEP`,
`POST_DISPLACEMENT_CONTINUATION` and `RANGE_FADE` produced **nothing at all**.
Meanwhile indicator/MA/flow paths were **97.1%**.

**Application 6 is the one with leverage, and this program prioritises it**, for a
reason that is about measurement rather than taste: it needs no new signal, no new
delivery surface, and no user-visible change, and it can be tested on the *whole
delivered book* from the day it ships. Application 2 — a standalone price-action
signal — is the one everybody reaches for first and it is the one that takes
weeks to reach n=100 while the 54-variant result hangs over it.

We will build both. We build 6 first because it answers "does structure carry
information on this book" in days, and that answer is a precondition for 2 being
worth shipping.

---

## 6. The build

Seven phases. Each is a PR or a paired PR, each is fully wired end to end on
merge, and each ships its ops surface in the same change — a dark measurement with
nowhere to read it is an unfinished change (`CLAUDE.md`, § Project Phase).

**No phase ships a scaffold.** Specifically: nothing in this program stores a
value it does not consume, registers a flag nothing reads, or lands a "Phase N+1
will wire it" comment. Where a phase cannot be completed end to end in one change,
it is split so that each half is itself complete.

### Phase 0 — the stale quota constant

`api_limits.py:21` says 1,200; the futures limit is 2,400 and `binance.py` knows
it. One writer, one reader: `api_limits` imports the limit from the module that
syncs it from the exchange header, and a test pins that the two cannot disagree.

Small, and it goes first because §4 is load-bearing for everything after it.

### Phase 1 — `/diagnostics/data-intake`: see the pipe before changing it

**Engine:** `GET /api/data-intake` (owner-tier), assembled from state the engine
already holds — no new polling, no new vendor calls.

**Ops:** a page rendering it, so the owner never opens an SSH session to answer
"what are we actually reading".

Contents, and every one of these is a question this document had to read source
code to answer:

- **Per WS pool** — connected / degraded / down, stream count, last message age,
  messages/sec, reconnects in the last 24h, seconds until the 24h forced cycle.
- **Per symbol × timeframe** — bars held, newest bar age, whether the series is
  WS-streamed or REST-seeded-only (the promoted-mover case), and the gap count.
- **Derived inputs, with provenance** — CVD **source** (`kline taker_buy`, not
  ticks) and age; order-book **quality badge** (`top_of_book_only`); OI and
  funding age.
- **Primitive census** — FVG count and the lookback that produced it,
  `orderblocks_detector_status` rendered as its own row, swing counts per
  timeframe, LevelBook size, volume-profile POC/VAH/VAL freshness.
- **Weight** — live `x-mbx-used-weight-1m` against the 2,400 ceiling, and the
  per-endpoint call counts behind it.

Two rules the page holds, both paid for elsewhere in this repo:

- **The census renders whether or not anything is wrong.** A check that appears
  only when it trips teaches the reader that its absence means "fine", when it
  equally means the check stopped running.
- **A dead detector shows as a named zero, not an absence.**
  `orderblocks_detector_status: not_implemented` is a *row on the page*, because
  the entire reason that defect survived years is that a hollow primitive behind
  a passing gate looks identical to a working one.

### Phase 2 — the confirmation layer: a real footprint store

This is the largest phase and the one the program exists for. It is also **cheaper
than a greenfield build and carries a correctness fix**, per §3.5: the trade
handler, the tick store, its cap, five consumers and the gate telemetry all exist
already — nothing subscribes the stream, so the store serves a seed-time snapshot.

**Phase 2 therefore has two halves, and the repair ships first:**

**2a — connect the feed that already has a handler.** Subscribe
`{sym}@aggTrade`, route it into the existing `trade` handler path, and make the
tick store **live**. The moment it is live, `recent_ticks` stops being a
seed-time snapshot for the five consumers reading it and the `$500k cumulative
tick volume` gate starts measuring the present.

`@aggTrade` rather than `@trade`: aggTrade collapses fills of a single taker order
into one message, which is both lower volume and the semantically correct unit for
aggression — a 50-fill sweep is one aggressive act, not fifty. The `m` flag marks
the aggressor either way, so the buy/sell split is exact rather than inferred by
tick rule.

Because this changes what five live consumers see, it is **money-path and ships
dark-first**: the live series lands under its own key beside the seeded one, both
are stamped, ops shows the disagreement, and the switchover to the live series for
gating is a flag the owner flips on measured evidence. A gate that has been
reading stale data for months must not silently start reading fresh data in the
same deploy that makes it fresh.

**2b — the footprint on top.** Fold every trade into a per-symbol, per-bar,
per-price-bin accumulator: `{bar_open_time → {price_bin → (buy_vol, sell_vol)}}`.

From that structure, computed at bar close and stamped on the bar:

- **delta** and **CVD** — real, tick-derived, replacing nothing (the kline-derived
  series stays, under its own key, as a **detector**: a second computation of the
  same quantity is a detector rather than a duplicate, provided it never
  overwrites the first, and a disagreement counter goes on the liveness watchdog);
- **imbalance** — per price level, one side dominating by a configured ratio;
- **absorption** — high volume at a level with bounded price displacement;
- **exhaustion** — volume collapse at an extreme;
- **trade-size distribution** — so "large aggressive buyer" is a measurement
  rather than a story.

**Bounded by construction:** fixed bin count per bar, fixed bar ring per symbol,
pre-allocated arrays, and a hard cap that **refuses and counts** rather than
trimming silently. A reconnect gap is stamped as a named hole on the affected
bars — never zero volume — because zero volume and no data are different states
and only one of them is a market fact.

**Rollout is measured, not assumed.** Ships on a bounded symbol set, and the
whole-universe decision is taken from the Phase 1 page's own message-rate and
memory numbers.

**Ops:** the footprint lands on the data-intake page (health, coverage, memory)
and the per-bar values become columns on the measurement surfaces that follow.

### Phase 2c — depth

`{sym}@depth20@100ms`, maintaining a real 20-level book per symbol, replacing
`top_of_book_only` for the evaluator paths that consume `order_book`. Weight-free,
75 more streams.

Split from Phase 2 deliberately: aggTrade answers *who is aggressive*, depth
answers *who is resting*. The first is required by every trigger in this program;
the second improves them. Shipping them together would make one rollback
impossible without the other.

`entry_features.book_imbalance` is redefined to read real depth — and, per the
rule that restoring a dropped input silently redefines what depends on it, the
change is **stamped as a source change** (`book_source`) rather than schema-bumped,
so pre-change and post-change rows stay separable instead of being pooled.

### Phase 3 — repair layer 3

- **Order blocks**: implement the detector, or delete the branch. Both are
  acceptable; what is not acceptable is a third year of `bool(fvgs) or
  bool(orderblocks)` pretending to check two things. Given §2 — order blocks have
  no validation distinct from support/resistance — the default is **implement it
  as a measured candidate behind a dark flag**, stamped and never gating, and
  delete it if it does not discriminate. The gates that currently read it are
  rewritten to say what they actually check.
- **FVG lookback**: raise it to reach real structure, and — because that widens a
  gate that currently rejects — stamp the change and measure before it takes
  effect on emission.

**Money-path, so dark-first with owner sign-off to activate**, per § Project
Phase. Both changes alter what emits.

### Phase 4 — the structural veto (application 6)

The first application, and the one with a large-n test on day one.

A post-scoring stamp on **every** candidate: distance to the nearest opposing
LevelBook level, in ATR and in percent; whether that level has been swept
recently; whether price is inside or outside the value area; room to the next
level in the trade's direction.

**Measurement flag ON, veto flag OFF** — the exact split § Project Phase
requires. Ops renders the split: what the veto *would* have removed, its
performance, and the delivered book's own average beside it, with the removal
figure's colours inverted because a negative there is the rule looking right.

This is testable against the whole delivered book immediately, and it is the
cheapest possible answer to "does structure carry information here".

### Phase 5 — the standalone price-action lane (application 2)

Only now, and built on the supported column from §2:

> **a confirmed level from the LevelBook, swept and reclaimed, with delta
> confirmation from the Phase 2 footprint, sized and targeted from structure.**

Not "an order block exists". Not "an FVG exists". The trigger is the one event in
§2's supported column, and the confirmation is the layer we will by then actually
be able to see.

It emits through **`dark_emission`** — a real signal, diverted before the queue,
walked forward for an outcome — with **its own row budget**, because a dark lane
whose budget is consumed by the two highest-volume paths starves exactly the rare
paths it exists to measure. That has already happened to us once: the structural
snap ledger filled with 211 re-detections of one RIFUSDT setup.

**Its own page**, reporting volume per day, win rate, PnL % gross **and net**,
MFE and MAE, per structural trigger — never pooled with the MA book, because
pooling is how 15 rows disappear into 2,418.

### Phase 6 — retention, so the measurement survives

The structural-snap ledger is a 4,000-row ring evicting by recency, filled by
enqueues of which ~0.5% ever deliver. It reaches capacity roughly 32 hours after
deploy, after which every re-detection evicts a row that might have carried a
verdict.

Retention becomes **by delivery, not by recency**: a row the router confirmed is
never evicted; un-promoted rows evict freely. The engine already writes
`PROVENANCE_EMITTED` only from the router after confirmed delivery, so the hook
exists. Same rule applies to the Phase 5 lane from the start.

### Phase 7 — the verdict surface

One page that answers the owner's original question in the owner's own terms:

> *if we really follow price action — what is our signal volume, and what is its
> performance?*

Volume per day and accuracy per structural trigger, gross and net of fees, with
the decidable fraction and the distinct-outcome count beside every figure, and the
delivered denominator leading. It must be capable of rendering **"no edge
detected"** as its headline, and that is a supported outcome, not a failure of the
program.

---

## 7. What this program will not claim

Stated in advance so that no later result can quietly drift into claiming it:

- **We are not detecting institutional intent.** We are detecting aggressive
  volume at price levels where resting orders are known to cluster. The
  "accumulation → manipulation → distribution" narrative is not implemented and
  will not be cited in any surface this program builds.
- **We are not seeing hidden liquidity.** aggTrade shows executed aggression;
  depth shows displayed resting size. Icebergs and hidden orders are invisible to
  both, and no page will imply otherwise.
- **A pattern's presence is not an edge.** Every trigger ships stamped and dark,
  and earns emission on measured, cost-inclusive, forward outcomes on the
  delivered population.
- **A backtest is not a verdict.** Counterfactuals in this repo measure ~0.38R
  optimistic. Every number this program publishes states whether it is replayed or
  live, and no replayed figure is quoted as an expected live result.

---

## 8. Sequencing and dependencies

```
Phase 0  quota constant            ──┐
Phase 1  data-intake visibility    ──┼─→ every later phase reads its numbers
Phase 2a live tick feed (repair)   ──┼─→ fixes 5 consumers reading stale ticks
Phase 2b aggTrade footprint        ──┼─→ Phase 5 confirmation
Phase 2c depth                     ──┘   Phase 3 order-block measurement
Phase 3  repair layer 3            ─────→ Phase 5 trigger quality
Phase 4  structural veto           ─────→ answers "does structure inform this book"
Phase 5  standalone lane           ─────→ answers "what is our price-action volume"
Phase 6  retention                 ─────→ makes 4 and 5 measurable beyond 32h
Phase 7  verdict surface           ─────→ answers the owner's question
```

Phase 6 has no dependencies and must land before Phase 4's ledger fills — it is
sequenced late for narrative clarity only, and in practice ships alongside Phase 1.

**Owner sign-off gates:** Phase 3 (changes what emits), Phase 4's veto activation,
Phase 5's promotion to a delivered channel. Phase 2a is money-path (it changes what five live
consumers see) and ships dark-first. Phases 0, 1, 2b, 2c, 6 and 7 are
off-money-path and ship normally.

---

## 9. Sources

Structure and definitions: [LuxAlgo — Market Structure](https://docs.luxalgo.com/docs/algos/price-action-concepts/market-structures) ·
[DailyPriceAction — BOS/CHoCH](https://dailypriceaction.com/blog/smc-market-structure/) ·
[Alchemy Markets — BOS](https://alchemymarkets.com/education/strategies/break-of-structure-bos-trading/)

Evidence: [IndicatorEdge — SMC evidence review](https://indicatoredge.io/smart-money-research) ·
[AlgoStorm — ICT/SMC realistic overview](https://algostorm.com/ict-smc-realistic-overview/) ·
[Power Trading Group](https://www.powertrading.group/options-trading-blog/truth-about-ict-smart-money-concepts-rebranded-principles)

Auction theory: [Trading Wyckoff — Auction Market Theory](https://tradingwyckoff.com/en/auction-market-theory/) ·
[Trading Wyckoff — Volume Profile](https://tradingwyckoff.com/en/volume-profile-2/) ·
[FinancialTechWiz — AMT](https://www.financialtechwiz.com/post/auction-market-theory/)

Order flow: [OrderFlow Labs — footprint, delta, absorption](https://orderflowlabs.com/blogs/theblog/footprint-chart-guide) ·
[NinjaTrader — order flow](https://ninjatrader.com/futures/blogs/ninjatrader-order-flow/)

Vendor limits: [Binance — USDⓈ-M general info](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info) ·
[Binance — order book weights](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Order-Book) ·
[Binance — aggTrades](https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Compressed-Aggregate-Trades-List) ·
[Binance — WebSocket market streams](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams)
