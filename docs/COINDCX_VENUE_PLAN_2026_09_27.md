# CoinDCX as a second trading platform — research, measurements and plan

*2026-09-27 · status: **IMPLEMENTED DARK** (engine: `src/venues/coindcx/`),
switch `COINDCX_EXECUTION_ENABLED` **OFF**.  Owner decisions taken the same day:
D1 CoinDCX first · D2 one engine, one lane per platform · D3 INR margin default
with a USDT option · D4 **attest + verify**.  Going live is gated on the §6
checklist, run by the owner's self-test (§10).  Touches the signing service,
connect-time validation and dispatch — owner-sign-off items per `CLAUDE.md`.*

Owner's ask (2026-09-27): *"find which app most Indians use for crypto trading …
scan that app universe separately … run parallel to our Binance system with same
paths … user selects platform, signals and Auto Trade go to that platform"*, and
*"we can send signals USDT or INR — how do most Indian users do futures?"*

This document records what was measured, what was only inferred (labelled), the
design it leads to, and the checks that must pass before a subscriber's money
goes near it.

---

## 0. Decisions the owner is asked to make

| # | Decision | Recommendation |
|---|---|---|
| D1 | First Indian platform | **CoinDCX** (§1) |
| D2 | A second, independent CoinDCX engine, or one signal engine with a CoinDCX **lane** | **One engine, one lane per platform** (§3, §4) |
| D3 | USDT or INR | **Signals are quoted in USDT prices on every platform** (it is the contract's price). **Margin is a per-user choice; INR margin is the default for CoinDCX users** (§2.4) |
| D4 | CoinDCX keys cannot be checked by API for withdraw permission or IP binding (§5.3) — accept with a manual attestation, or refuse? | Owner call — B18 change |
| D5 | Delta Exchange India as platform #3 (own order book, real venue diversification) | Later, after CoinDCX is measured |

---

## 1. Which platform Indians use

| Platform | Scale | Futures | Public trading API |
|---|---|---|---|
| CoinSwitch | 2.5 crore registered users, the largest ([The Week, 2025-09](https://www.theweek.in/wire-updates/business/2025/09/22/dcm16-coinswitch.html)) | Yes (PRO) | Not verified |
| **CoinDCX** | **2.2 crore** users, +3M in H1 2026; trading value **−37%** in the same half ([Business Standard](https://www.business-standard.com/companies/news/coindcx-user-base-rises-16-in-h1cy26-as-trading-value-declines-37-126062400921_1.html)) | **503 USDT perps**, USDT- and **INR-margined** | **Yes, documented** ([docs.coindcx.com](https://docs.coindcx.com/)) |
| Delta Exchange India | Futures/options specialist, launched June 2024 ([user guide](https://guides.delta.exchange/delta-exchange-india-user-guide)) | 220 perps (API-measured), USD-settled via INR banking, fees 0.02/0.05% | Yes |
| Mudrex | 30 lakh+ users, INR-margined futures ([The Wire](https://m.thewire.in/article/ptiprnews/mudrex-rolls-out-inr-margined-crypto-futures-simplifying-digital-assets-for-indian-traders)) | 300+ | Not checked |

Futures are **70–80% of volume** on Indian exchanges
([Moneycontrol via TradingView](https://www.tradingview.com/news/moneycontrol:2cc09dfe3094b:0-crypto-futures-driving-70-80-trading-volumes-say-indian-exchanges/)),
which fits a futures-signal product.

**Why CoinDCX first:** the largest user base with a **documented futures trading
API**, the widest futures list, and it covers **73 of our top-75** pairs
(Delta India: 50 of 75).

---

## 2. Measured facts (2026-09-27)

All from CoinDCX's public API, called from outside India. Binance and Bybit
refuse this container by region (HTTP 451/403), so Binance-side figures come from
the engine itself (via ops guest) or CoinGecko, as marked.

### 2.1 CoinDCX's futures list is Binance's

- `active_instruments`: **503** USDT perps. **497** are Binance USDT-M symbols;
  the other 6 (XAU, XAG, CL, BZ, NATGAS, COPPER) are commodities our universe
  excludes by rule (`crypto_perp_admission`).
- Every contract names its Binance twin: `B-AVA_USDT` carries `"mkt":"AVAUSDT"`.
- Funding rate equal to Binance's on **337 of 504** pairs at one snapshot
  (Binance side from CoinGecko, which lags — the rest are most likely timing).
- **Inference, not confirmed with CoinDCX:** the `B-` series is Binance-linked.
  Consequence: CoinDCX adds **no pairs** our scanner does not already see, and
  probably **no protection** against a Binance outage (see §8).

### 2.2 Coverage of what we scan

| | On CoinDCX |
|---|---|
| Binance top-25 USDT perps | 25 / 25 |
| **Top-75 (≈ core scan set)** | **73 / 75** (missing: two Chinese-character tickers) |
| Top-110 (core + promotions) | 107 / 110 |
| **Last 50 delivered signals (ops, 2026-09-27)** | **49 / 50** (`牛来USDT` not listed) |

### 2.3 Contract limits (sampled over our top-75)

| Field | Value |
|---|---|
| Minimum notional | 6 USDT on 67 pairs · 24 USDT on 5 · **60 USDT on BTC** |
| Fees | maker **0.0236%** · taker **0.059%** (reads as 0.02/0.05 + 18% GST); ≈0.083% round trip vs the 0.07% our pages assume |
| Leverage | BTC up to 20×; set **per order** (`leverage` field). Note: our Binance live path never sets leverage (it inherits the account's) |
| Order types | `market_order`, `limit_order`, `stop_market`, `take_profit_market`, `stop_limit`, `take_profit_limit` |
| Public data | candles, order book (`@orderbook@50-futures`), trades, prices, funding. **No open interest and no liquidation feed** in the docs |

### 2.4 USDT or INR — how Indian users trade futures

- **INR margin trades the same contracts.** `active_instruments` with
  `margin_currency_short_name[]=INR` returns the **identical 503 pairs**, and the
  instrument reads `quote_currency=USDT`, `settle_currency=USDT`,
  `margin_currency=INR`. Price, min-notional, leverage and fees are the same.
- CoinDCX: *"your INR is automatically converted to USDT at the applicable
  conversion rate when you place your order … Any profit or loss (PnL) … is
  settled and reflected in INR"*
  ([support](https://support.coindcx.com/articles/margin-types-inr-margin-usdt-margin/how-does-inr-margin-work-in-futures-trading/6a6215251916c514c7087ee1)).
  The API exposes the order's and position's conversion price.
- Why it matters to users: no USDT purchase first, so no double fee and no
  USDT-buy leg ([CoinDCX launch post](https://coindcx.com/blog/crypto-futures-trading/coindcx-launches-inr-margin-futures/)).
  Mudrex and Pi42 also sell INR-margined/settled futures; Delta India funds in INR.
- **Not measured:** no public source gives the INR-vs-USDT split of users. The
  direction of the market (every Indian futures venue now offers INR funding) is
  clear; "most" is not a number anyone publishes.

**So the answer to "send signals in USDT or INR" is: both, in different places.**
The **signal** (entry / SL / TP) is a USDT price, because that is what the
contract trades at on every platform — converting it to rupees would produce a
number no order form accepts. What changes with INR is the **margin, the size
and the P&L**, which the app shows in ₹ for an INR-margin user.

---

## 3. Live check: our last 50 signals against CoinDCX's own candles

Method: the engine's own signal records (ops `/signals` + each signal's detail,
read through the guest tier) for entry, **original** stop, TP1 and dispatch time;
CoinDCX 1-minute futures candles from the dispatch minute; walk the candles to
the first touch of the original SL or TP1.

**One trap, recorded because it nearly produced a false finding:** the ops CSV
export's `sl` column is the stop **as it is now** — on a TP1 winner that is the
breakeven-shifted stop (QUSDT: `sl == entry`). The first pass walked those and
reported 11 Binance winners as CoinDCX losses. The original stop is in the detail
payload (`original_stop_loss`). This is `CLAUDE.md`'s #848 (mutated denominator)
arriving at an export; a design that compares platforms must read the original
geometry.

| Result | Value |
|---|---|
| Signals listed on CoinDCX | 49 / 50 |
| Decided outcomes (TP1/SL) that match on CoinDCX | **28 / 32** |
| Differ | 4 — SOONUSDT, QNTUSDT, FILUSDT: Binance SL, CoinDCX TP1 first; BEATUSDT: Binance SL, CoinDCX not yet |
| Signal entry vs CoinDCX close of the dispatch minute | median **0.35%**, p90 1.17%, max 2.20% |
| Our entry inside CoinDCX's dispatch-minute high–low | 20 / 49 |
| Live price, same moment, 3 open signals (engine vs CoinDCX) | −0.17% · −0.40% · +0.09% |

How to read it:

- **The same signal does not always end the same way on CoinDCX** — 4 of 32 in
  one day. So CoinDCX needs **its own recorded track record**; Binance's cannot
  be shown to CoinDCX users as theirs.
- The 0.35% entry gap is **not purely a platform difference**: our signal's entry
  is a reference price that already drifts from the live Binance price
  (`/track-record` entry-fidelity panel). The live comparison (3 samples, 0.1–0.4%)
  is the platform gap, and it is too small a sample to size a tolerance.
- 14 breakeven exits are left out of the comparison: the walk uses the original
  stop, and a BE exit is a stop that moved.
- 1-minute candles cannot order an SL and a TP1 touched in the same minute;
  none occurred here.

Per-signal evidence:

| Symbol | Side | Path | Admission | Binance outcome | CoinDCX walk | Entry gap |
|---|---|---|---|---|---|---|
| 牛来USDT | SHORT | LIQUIDITY_SWEEP_REVERSAL | CORE | open | not listed | — |
| PYTHUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_TOP24H | open | OPEN | +0.63% |
| CLOUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_TOP24H | open | OPEN | +0.47% |
| UNIUSDT | LONG | MOVER_AVWAP_SCALP | CORE | open | OPEN | +0.88% |
| SOONUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_TOP24H | TP1 | TP1 | −0.08% |
| KITEUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_TOP24H | TP1 | TP1 | +0.05% |
| QUSDT | LONG | TREND_PULLBACK_EMA | CORE | TP1 | TP1 | −0.25% |
| SOONUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_TOP24H | SL | **TP1** | +1.25% |
| RUNEUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_TOP24H | TP1 | TP1 | +0.21% |
| USUSDT | LONG | MOVER_TREND_PULLBACK | CORE | SL | SL | +0.99% |
| CLOUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_TOP24H | SL | SL | +0.51% |
| ZECUSDT | LONG | DIVERGENCE_CONTINUATION | CORE | TP1 | TP1 | +0.14% |
| QNTUSDT | LONG | MOVER_TREND_PULLBACK | CORE | SL | **TP1** | +0.08% |
| RUNEUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_TOP24H | SL | SL | −0.12% |
| BEATUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_TOP24H | SL | **OPEN** | +0.18% |
| CCUSDT | LONG | MOVER_TREND_PULLBACK | CORE | SL | SL | +0.55% |
| SOLUSDT | LONG | QUIET_COMPRESSION_BREAK | CORE | SL | SL | +0.10% |
| XLMUSDT | LONG | QUIET_COMPRESSION_BREAK | CORE | SL | SL | +0.17% |
| ICPUSDT | LONG | MOVER_AVWAP_SCALP | CORE | TP1 | TP1 | −0.09% |
| JTOUSDT | LONG | MOVER_TREND_PULLBACK | CORE | TP1 | TP1 | +0.98% |
| RAREUSDT | LONG | MOVER_TREND_PULLBACK | CORE | SL | SL | −1.17% |
| KMNOUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_IGNITION | TP1 | TP1 | +0.90% |
| BRUSDT | LONG | MOVER_TREND_PULLBACK | CORE | TP1 | TP1 | +2.16% |
| UNIUSDT | LONG | FAILED_AUCTION_RECLAIM | CORE | SL | SL | −0.11% |
| DASHUSDT | LONG | MOVER_AVWAP_SCALP | CORE | TP1 | TP1 | +0.20% |
| FILUSDT | LONG | MOVER_TREND_PULLBACK | CORE | TP1 | TP1 | −0.02% |
| ONDOUSDT | LONG | MOVER_TREND_PULLBACK | CORE | TP1 | TP1 | +0.40% |
| QNTUSDT | LONG | MOVER_TREND_PULLBACK | CORE | TP1 | TP1 | +1.30% |
| BRUSDT | LONG | MOVER_TREND_PULLBACK | CORE | SL | SL | +0.55% |
| FILUSDT | LONG | MOVER_TREND_PULLBACK | CORE | SL | **TP1** | −0.54% |
| PUMPUSDT | LONG | MOVER_TREND_PULLBACK | CORE | SL | SL | −0.74% |
| ACEUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_IGNITION | TP1 | TP1 | −0.28% |
| VELODROMEUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_TOP24H | SL | SL | +0.10% |
| CCUSDT | LONG | MOVER_TREND_PULLBACK | MOVER_TOP24H | TP1 | TP1 | −0.33% |
| BTWUSDT | LONG | MOVER_TREND_PULLBACK | CORE | SL | SL | −0.50% |
| WLDUSDT | LONG | DIVERGENCE_CONTINUATION | CORE | SL | SL | +0.09% |

(14 breakeven exits omitted, see above.)

---

## 4. Why not a separate CoinDCX engine

The owner's idea — scan the CoinDCX universe separately and run the same paths
in parallel — was checked against the data, and it does not buy what it costs:

1. **No new pairs.** CoinDCX's crypto list is a subset of Binance's (§2.1).
2. **Worse inputs.** No open interest and no liquidation feed in CoinDCX's
   public API, so the funding / liquidation-reversal / OI-gated logic would go
   dark or change meaning on CoinDCX data.
3. **The VPS cannot carry a second scanner.** The engine is already
   CPU-quota-bound (the 2026-08-19 restart loop).
4. **Every path's evidence restarts at zero.** The edge matrix, gate audits and
   track record are all measured on Binance data.

What the owner actually wants — *a user picks a platform and gets that
platform's signals and Auto Trade* — is delivered by the lane design below. A
fully separate engine becomes worth building only for a platform with its **own
order book** (Delta India is the candidate, D5).

---

## 5. Design: one signal engine, one lane per platform

```
Binance data → scanner → same 17 live paths → gates → router  (unchanged)
                                                        │
             ┌──────────────────────────────────────────┴─────────────┐
             │ Binance lane (today, untouched)   │ CoinDCX lane (new)  │
             │                                   │  eligibility:       │
             │                                   │   listed & active   │
             │                                   │   not exit_only     │
             │                                   │   min notional OK   │
             │                                   │   live CoinDCX price│
             │                                   │   within tolerance  │
             │                                   │  feed · push        │
             │                                   │  auto-trade adapter │
             │                                   │  own track record   │
             └───────────────────────────────────┴─────────────────────┘
```

### 5.1 Components (engine)

| Component | Role | Notes |
|---|---|---|
| `venue_registry` | Per-platform instrument map, refreshed from `active_instruments` + `instrument` (6h, like `symbol_filters`) | Keyed by **(base, quote, contract multiplier)**, never by string. No confident match ⇒ **refuse**, counted and named (fail-closed, as `crypto_perp_admission`) |
| `venue_eligibility` | Per signal, per platform: listed, active, not `exit_only`, min-notional vs the user's size, live-price gap within tolerance | Stamped on the signal (`venues: {coindcx: {eligible, reason, price, gap_pct}}`) |
| `ExecutionVenue` interface | `place_entry`, `place_stop`, `place_tp_leg`, `cancel`, `positions`, `open_orders`, `set_leverage`, `set_margin_type`, `instrument` | `BinanceVenue` = today's `order_placer`/reconciler calls moved behind it, **behaviour byte-identical** |
| `CoinDCXVenue` | Adapter over the CoinDCX futures endpoints (§5.4) | Native code, no CCXT on the money path |
| Signing service | New verb `venue_signed_request{venue, method, path, body}`; each platform's signer lives **inside** the signing service | The secret still never leaves that process. Old `binance_signed_*` verbs kept |
| Private stream | CoinDCX socket.io `coindcx` channel, `df-order-update` / `df-position-update` → normalised `OrderEvent` / `PositionEvent` → FSM | Reconciler per venue as the backstop, as today |
| Venue track record | Outcome of every CoinDCX-eligible signal walked on **CoinDCX** prices, CoinDCX fees charged | Recorded, never reconstructed — the `/track-record` rule |

**Levels on CoinDCX.** The SL/TP are absolute USDT prices. Where CoinDCX's live
price differs from our entry, the order is placed against CoinDCX's price with
the signal's **distances** preserved (rebased), and the signal refused if the
gap exceeds a tolerance to be set from the Phase-1 data — not from §3's three
samples.

### 5.2 Data model

| Store | Change |
|---|---|
| SQLite `user_auto_trade_settings` | `venue TEXT DEFAULT 'binance'`, `margin_currency TEXT DEFAULT 'USDT'` |
| Firestore keys | `users/{uid}/exchange_keys/{venue}`; keep reading `binance_key/current` for existing users. One roster **index document per venue** (`control/active_uids_{venue}`) — no per-user reads (cost rule, 1,000-member target) |
| Position state, `dispatch_log`, closed-signal record | add `venue`, `venue_symbol`, `margin_currency`, `conversion_price` |

### 5.3 Key custody (B18) on CoinDCX

- Binance lets us **prove** withdraw is disabled and our IP is bound. **CoinDCX
  has no endpoint that reports a key's permissions or IP binding**; binding is
  an option at key creation. The docs show no withdrawal endpoint in the API,
  but that is a property of their API today, not of the key.
- A signed call from our VPS succeeding proves the key works; it does not prove
  the key is bound to our IP.
- Options for D4: (a) require the user to bind our IP and attest it, with a
  screenshot reviewed once; (b) refuse CoinDCX Auto Trade until CoinDCX exposes
  key metadata; (c) accept unverified. **(c) weakens B18 and is not recommended.**

### 5.4 Our intents → CoinDCX calls

| Intent | Binance today | CoinDCX |
|---|---|---|
| Entry | MARKET `/fapi/v1/order` | `POST /exchange/v1/derivatives/futures/orders/create` (`market_order`, `leverage`) |
| Stop | `STOP_MARKET closePosition` algo | `stop_market`, or `POST .../positions/create_tpsl` |
| TP ladder | reduce-only TP legs | `take_profit_market` / `take_profit_limit` legs — **reduce-only semantics unverified (§6)** |
| Cancel | `DELETE` order / algo | `POST .../orders/cancel` |
| Close | reduce-only MARKET | `POST .../positions/exit` |
| Positions | `positionRisk` | `POST .../positions` |
| Leverage / margin | not set / `marginType CROSSED` | `.../positions/update_leverage`, `.../positions/margin_type` |
| Fills | listenKey user stream | socket.io `df-order-update`, `df-position-update` |
| Auth | HMAC query, `X-MBX-APIKEY` | HMAC-SHA256 of the JSON body, `X-AUTH-APIKEY` / `X-AUTH-SIGNATURE` |

---

## 6. Must be proven on a real account before Phase 3

CoinDCX documents **no testnet**, so these run on the owner's account at minimum
size, and each result is written back into this file:

1. **Reduce-only.** The docs contain no `reduce_only` flag. Prove a TP leg can
   neither open nor flip a position after the stop has closed it. If it can,
   the TP ladder must be `create_tpsl` only, and the ladder shape changes.
2. A resting stop and a resting TP ladder coexist on one position (Binance's
   -4130 lesson: a vendor can refuse a second protective order).
3. `client_order_id` on futures create — accepted, unique, echoed on the
   socket events (the FSM maps fills by it).
4. Stop placement failure path → the naked-position force-close works.
5. Error-code catalogue for: insufficient margin, below min notional, bad tick /
   step, rate limit, `exit_only` instrument.
6. Futures rate limits (not documented) — measure, then set a per-IP budget
   shared with Binance traffic.
7. INR margin: conversion price at order time, and how P&L and fees appear.

---

## 7. Phases

Each phase is its own PR. Measurement ON when it ships; anything a subscriber
sees or any order stays OFF until the owner signs off on measured data.

| Phase | What | User-visible? | Flag |
|---|---|---|---|
| **1 — Measure (≈2 weeks)** | `venue_registry` + `venue_eligibility` stamp on every delivered signal + CoinDCX-price outcome walk + ops page `/signals/venues` | No | measurement ON |
| **2 — Seam** | `ExecutionVenue` with `BinanceVenue` only; signing-service verb; test proving Binance orders are byte-identical | No | — (pure refactor, owner sign-off) |
| **3 — Adapter** | `CoinDCXVenue` + stream + reconciler; owner's account only | Owner only | `COINDCX_EXECUTION_ENABLED` OFF |
| **4 — App + legal** | Platform picker; CoinDCX connect guide (IP binding, permissions); per-platform feed, track record, live status; ₹ display for INR margin; Terms/Risk naming CoinDCX | Yes, allow-listed users | per-user `venue` |
| **5 — Widen** | Remove allow-list after a watched window | Yes | — |

**Cost of Phase 1 (per the "count the vendor calls" rule):** instruments ×1 and
instrument detail ×~110 every 6h; one price snapshot per delivered signal
(~15–50/day); one candle fetch per open venue row per resolve cycle, bounded by
the open-row count. No Firestore reads. All public, unsigned endpoints — no key,
no custody change.

**Blast radius, stated for each money-path phase:** if the CoinDCX adapter is
wrong, CoinDCX users' positions are affected and Binance users are not;
`COINDCX_EXECUTION_ENABLED=false` stops new CoinDCX orders, and the kill switch
covers both.

---

## 8. Risks

| Risk | Why it matters | Mitigation |
|---|---|---|
| CoinDCX is (likely) Binance-linked | A Binance problem probably hits both; CoinDCX is not venue diversification | Delta India (own book) if diversification is the goal (D5) |
| Key custody weaker than B18 | Permissions and IP binding unverifiable (§5.3) | D4 |
| Reduce-only unknown | A TP leg could open a position after a stop | §6 item 1 before any order |
| Outcomes differ from Binance | 4 of 32 in one day (§3) | Separate CoinDCX track record; never show Binance's as CoinDCX's |
| Fees higher | ≈0.083% vs 0.07% round trip, on a thin edge | Charge CoinDCX fees in its track record |
| Min notional | 60 USDT on BTC; small users skipped more | Eligibility stamps it; app says why |
| Contract multiplier | A wrong map is a 10×–1000× size error | Map by (base, multiplier); refuse on doubt |
| Shared IP, two venues | Rate-limit bans hit both | One per-IP budget across venues |
| CoinDCX volume falling | −37% trading value H1 2026 | Watch; Phase 1 measures liquidity per signal |
| Regulatory / Play | Naming a second exchange changes Terms and the financial-features declaration | Legal PR in Phase 4, owner sign-off |

---

## 9. Testing

- One contract suite every venue adapter must pass; fixtures recorded from
  CoinDCX's **real** responses, never hand-written (`CLAUDE.md`: a fixture
  chooses a shape and then agrees with you).
- Naked-position invariant per venue; stop-rejection → market close per venue.
- Stream drop → reconciler catch-up; restart with open CoinDCX positions.
- Symbol-map tests for multiplier and renamed tickers; unknown ⇒ refusal.
- The §6 checklist on a real account before Phase 3.

## Sources

CoinDCX: [API docs](https://docs.coindcx.com/) ·
[INR margin](https://support.coindcx.com/articles/margin-types-inr-margin-usdt-margin/how-does-inr-margin-work-in-futures-trading/6a6215251916c514c7087ee1) ·
[INR margin launch](https://coindcx.com/blog/crypto-futures-trading/coindcx-launches-inr-margin-futures/) ·
[H1 2026 users](https://www.business-standard.com/companies/news/coindcx-user-base-rises-16-in-h1cy26-as-trading-value-declines-37-126062400921_1.html).
Market: [CoinSwitch 2.5 Cr](https://www.theweek.in/wire-updates/business/2025/09/22/dcm16-coinswitch.html) ·
[Futures 70–80% of volume](https://www.tradingview.com/news/moneycontrol:2cc09dfe3094b:0-crypto-futures-driving-70-80-trading-volumes-say-indian-exchanges/) ·
[Mudrex INR futures](https://m.thewire.in/article/ptiprnews/mudrex-rolls-out-inr-margined-crypto-futures-simplifying-digital-assets-for-indian-traders) ·
[Delta India guide](https://guides.delta.exchange/delta-exchange-india-user-guide).


---

## 10. What was built (2026-09-27)

Everything below ships **dark**: `COINDCX_EXECUTION_ENABLED=false`, so no
CoinDCX order, roster read or stream exists until the owner arms it.

### Facts from CoinDCX's own spec that changed the design

Read from `docs.coindcx.com` while implementing, after §5.4 was written:

* **The futures order-create call has no `client_order_id` and no
  `reduce_only`.**  So the Binance FSM's phase-by-client-order-id model cannot
  map CoinDCX fills, and a standalone take-profit could open a reverse
  position after the stop closed the trade.  The venue therefore uses **only
  the position-level TP/SL** (`positions/create_tpsl`, stage `tpsl_exit`),
  which closes the entire position — exactly the engine's default exit
  profile (TP1-full against a fixed stop; `PRE_TP_GRAB_FRACTION=0`, TP1
  fraction 1.0).  Pre-TP, TP2/TP3 and the trail governor stay Binance-only,
  and the app says so.
* **Cross margin exists only for USDT margin**, so INR positions are
  isolated.  Every CoinDCX position is placed isolated (one rule).
* **One position per pair per margin currency** (fixed position id).  An
  entry is refused unless the pair is flat.
* The rate limit is **16 req/s, 960/min per key**; the INR conversion is a
  published fixed price (`/api/v1/derivatives/futures/data/conversions`,
  ₹102/USDT on 2026-09-27); the feed's glossary names `btST` the
  **third-party exchange's** tick time.

### Architecture as built

```
signal_router ─┬─ signal_dispatch (Binance) ── skips users whose venue = coindcx
               └─ venues.coindcx.dispatch  ─── only users whose venue = coindcx
                    same gates, same order: venue · mode · tier · auto-pause ·
                    path/regime prefs · notional + B18 cap · shared safety chain
                    (global enable, kill switch, per-user disable, symbol
                    allow-list, user symbol pref, both breakers, rate limit)
                  → CoinDCXExecutor.open_position
                    plan (pure) → pair flat? → record (INSERT OR IGNORE) →
                    leverage → market entry → wait fill → create_tpsl →
                    liquidation-vs-stop check → OPEN   (else exit at market)
                  → signing service  verbs coindcx_signed_post/get,
                    coindcx_stream_auth — allow-list + attestation enforced
                    IN the signing process
CoinDCXReconciler (30s + stream nudges): exchange is truth; finalise closes
  with the exchange's own exit order; repair a missing stop (or exit); adopt /
  retire uncertain entries; same 2h age cap as Binance; count orphans, never
  touch them.  Budget spent per user examined.  No live record → no call.
Stream: Engine.IO v3 on aiohttp (no new dependency), one socket per user with a
  live record; events only nudge the reconciler — latency, never safety.
```

| Piece | File |
|---|---|
| Signing (pure) + endpoint allow-list | `src/venues/coindcx/signing.py` |
| Instruments, symbol map (feed `mkt`), INR rate | `src/venues/coindcx/instruments.py` |
| Encrypted keys + attestation + roster | `src/venues/coindcx/keystore.py` (Firestore `users/{uid}/coindcx_key/current`, `control/coindcx_active_uids`) |
| Connect-time validation | `src/venues/coindcx/connect_validator.py` |
| Exchange client (typed errors → shared breakers) | `src/venues/coindcx/client.py` |
| Position records (SQLite, engine writes / api reads) | `src/venues/coindcx/positions.py` → `data/coindcx_positions.sqlite` |
| Lifecycle | `src/venues/coindcx/execution.py` |
| Reconciler + status file | `src/venues/coindcx/reconciler.py` → `data/coindcx_status.json` |
| Private stream | `src/venues/coindcx/stream.py` |
| Fan-out + signal close | `src/venues/coindcx/dispatch.py` |
| Owner self-test | `src/venues/coindcx/self_test.py` → `data/coindcx_self_test.json` |
| API | `src/api/coindcx_routes.py` |
| Venue settings | `user_venue_settings` table in `src/api/user_overrides.py` |

### Invariants, each with a test that fails when it is removed

1. **Never naked** — stop refused twice ⇒ market exit.
2. **Never merged** — pair not flat ⇒ refused, nothing sent.
3. **Never twice** — record inserted before the order; a second dispatch stops.
4. **Never liquidated before stopped** — leverage lowered until liquidation is
   ≥ 2 stop-distances away; the reported liquidation price is re-checked.

Mutation-checked: removing each one turns exactly its test red.

### Cost

No Firestore reads per signal: the roster is one cached document invalidated
by a Redis generation (`coindcx_active_uids`), key blobs are cached against
`coindcx_key_blobs`, and positions live in SQLite.  Exchange calls happen only
for users with a live position.

### Go-live, in order (owner)

1. Connect your own CoinDCX key in the app (the attestation is required).
2. Set `COINDCX_EXECUTION_ALLOWED_UIDS=<your uid>`.
3. Run the self-test from ops (`/control/coindcx`, Control → CoinDCX; 360ce-ops #231).  It spends one minimum round trip
   (~6 USDT notional) and records every §6 answer.  **Continue only on
   `verdict: pass`.**
4. Set `COINDCX_EXECUTION_ENABLED=true`, choose CoinDCX in the app, and watch
   one real signal end to end on the ops CoinDCX tab.
5. Merge lumin-legal #11 (terms/risk/privacy name CoinDCX), THEN clear the
   allow-list — users must not be offered CoinDCX before the documents say so.  Switching back is setting the flag to false: open
   positions keep their exchange-resident stop and the reconciler keeps
   running.
