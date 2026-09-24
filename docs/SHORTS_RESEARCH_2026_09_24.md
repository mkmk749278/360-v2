# Shorts research — can a short-only path save the red days? (2026-09-24)

**Owner's question:** *"We have at least MVRTP longs … some edge for longs, but
there is [no] path for saving red days. We need a good strategy for shorts,
separate path for shorts only. Go deep research on this."*

**Short answer.**

- **The data does not support building a new short path to save red days.**
- **Red days are not market-down days.** They are days when mover longs fail
  to follow through. The alt market's sharpest down days were green for the
  book.
- **Every short that enters after weakness lost after costs**, out-of-sample
  wherever a year of data allowed one. That covers breakdowns, flushes, trend
  breaks, BTC dumps and failed movers.
- **The one robust bearish signal is already priced.** Negative funding
  predicts a decline, and the funding a short pays is roughly that decline.
- **Our existing shorts made red days worse.** Over 60 days the short side
  broke even on green days (−0.9%) and lost 65.5% on red days.

**The recommended moves:**

1. Stop the losing shorts. Divert `MOVER_AVWAP_SCALP` SHORT, one click on
   Control → Routing.
2. Keep and measure the only short structure with positive live evidence:
   the "failed move up" family.
3. Look for red days on the **long** side, where they come from, using the
   entry-feature lane.

Everything below is labelled **[measured]** (a query or backtest on real data
in this session) or **[inferred]** (reasoning from measured facts).

---

## 1. Data and method

| Source | What | Span |
|---|---|---|
| Delivered book (the audit's export of the public track record) | 1,678 closed signals: symbol, side, setup, outcome, `pnl_pct`, close time. **No entry time.** | 2026-07-26 → 2026-09-24 (60 days) |
| Binance archive (`data.binance.vision`, USDT-M) | 1h klines for all 864 USDT perps. **565 crypto perps after exclusions.** | 2025-09-01 → 2026-09-23 |
| Binance archive | 15m klines, 309 symbols (the book's symbols plus liquid ones) | 2026-07-01 → 2026-09-23 |
| Binance archive | 15m klines, the 78 liquid core symbols | 2025-09-01 → 2026-09-23 |
| Binance archive | Funding-rate history, 221 liquid perps | 2025-09 → 2026-08 |

**Rules applied everywhere:**

- **TradFi perps are excluded.** There are 50 of them: equities, ETFs, metals
  and oil. The live API is geo-blocked here (451), so `contractType` could not
  be read. They are detected structurally instead: weekend volume below 0.35×
  weekday volume, where every crypto major is at or above 0.40. The engine
  refuses them via `crypto_perp_admission`, so a backtest must too.
- **Liquidity floor:** $10M trailing 24h quote volume; $5M on the 15m book
  replica.
- **Costs:** 0.07% round-trip fee plus 0.05% adverse slippage per fill. Funding
  carry is charged hourly wherever a hold spans a settlement.
- **Fill rules:**
  - entry at the next bar's open;
  - the stop is checked before the target, so a bar touching both is booked as
    a stop;
  - a mandatory stop on every trade (naked-position invariant).
- **Two out-of-sample tests:**
  - **in-sample** 2025-09-08 → 2026-04-30 vs **out-of-sample** 2026-05-01 →
    2026-09-23;
  - day-clustered bootstrap CIs on backtests, symbol-clustered on the live
    book.
- **PnL % leads.** Positions are fixed-notional, so R would mislead (see
  `CLAUDE.md`, ops).

**The simulator was calibrated before it was trusted [measured].**

- **At 1h it failed.** In-sample, the MVRTP approximation gave longs −0.35%
  and shorts −0.05%, the opposite of the book.
- **At 15m it passed.** The exact MVRTP rules (SMA 7/25/99, 3% separation,
  pullback-reclaim, 1.0/1.6R ladder with BE) over the book window gave
  **LONG +0.24% / SHORT −0.22%** per trade. The book shows +0.42% / −0.93%.
- **Sign and ranking match.** The magnitude doesn't, because the replica has
  no scoring or router layer. It fires about 6× more often.
- So: **15m results are read for direction, never quoted as expected live
  PnL.**

---

## 2. What a red day actually is

**2.1 Red days are not BTC-down or alt-down days [measured].**

- Of the 60 days with market data, 25 were red, totalling **−227.8%** (sum
  of per-trade net %), against +612.4% on green days.
- **Correlation of long-book daily net with:**
  - BTC day return +0.08;
  - equal-weight alt index +0.22;
  - breadth (share of alts up on 24h) +0.05.
- **The sharpest alt-down days were green for the book:**

| Day | Alt index | Book |
|---|---|---|
| 28 Aug | −3.5% | +37% |
| 9 Sep | −4.4% | +18% |
| 15 Sep | −3.6% | +47% |

- **19–20 Aug:** BTC rose +7% and +5%, and both days were red.

**2.2 What does move with red days: movers that stop following through
[measured].**

| Measured over the day | Red days | Green days |
|---|---|---|
| Return of the previous day's top-20 movers by 72h | −0.22% | +0.70% |
| Return of the bottom-20 by 72h | −1.36% | +0.23% |

The book's long engine (MVRTP, ~63% of trades) buys continuation. It loses on
days when continuation fails, which is not the same thing as "the market
fell".

**2.3 Intraday flushes stop the longs out, but a flush pause is the wrong
fix [measured].**

- **Long stops cluster in flush hours.** 28.7% of long `SL_HIT`s close in an
  hour where the alt index fell more than 0.5%. Only 12.7% of hours are like
  that.
- **Short TP1s are the mirror:** 49.4% land in those hours.
- **Pausing long entries during flushes would remove the better longs.** In
  the 15m replica, longs entered *during* a flush did better than the rest:
  +0.64% (n=592) vs +0.20%. The CI of that difference is wide, but it gives
  no support for a pause.
- **Stop clusters don't make red days.** 17 hours had ≥3 long stops at once
  (−148% in total), but only **4 of the 25 red days** had one.

**2.4 Our shorts made red days worse [measured].**

- Over 60 days the short side lost **−66.4%**: **−65.5% on red days** and
  −0.9% on green days. That is 29% of all red-day damage.
- Part of that split is mechanical, because a losing short leg helps turn a
  day red. The point stands anyway: the short leg earned nothing on green days
  to pay for it.

| Short path (60d) | n | Mean/trade | 95% CI (symbol-clustered) | Total | On red days | Status |
|---|---|---|---|---|---|---|
| MOVER_TREND_PULLBACK | 72 | −0.93% | [−1.71, −0.20] | −67.2% | −36.5% | retired (last 13 Aug) |
| **MOVER_AVWAP_SCALP** | 78 | **−0.47%** | [−0.98, +0.02] | −36.5% | −17.1% | **still live** — 36 since 10 Sep |
| QUIET_COMPRESSION_BREAK | 113 | −0.11% | [−0.43, +0.17] | −12.7% | −12.0% | live, not proven either way |
| LIQUIDITY_SWEEP_REVERSAL | 36 | +0.04% | [−0.58, +0.62] | +1.4% | +9.1% | live |
| FAILED_AUCTION_RECLAIM | 47 | +0.14% | [−0.47, +0.71] | +6.3% | +1.8% | live |
| MEAN_REVERT | 12 | +0.24% | [−0.70, +1.24] | +2.8% | −0.8% | live |
| BREAKDOWN_SHORT | 27 | **+0.92%** | [−0.14, +2.01] | +24.8% | −8.5% | live |
| SR_FLIP_RETEST | 6 | +1.78% | [+0.16, +3.64] | +10.7% | 0.0% | live |
| TREND_PULLBACK_EMA | 4 | +1.73% | [−0.07, +3.53] | +6.9% | −0.1% | live |

**Counterfactual since 14 Aug**, the day after the last MVRTP SHORT closed
[measured]:

| | Red days (of 42) | Book | Red-day loss | Worst day |
|---|---|---|---|---|
| As delivered | 16 | +326.0% | −147.9% | −25.6% |
| MVAVW SHORT off | 16 | **+359.5%** | −134.2% | −25.6% |
| MVAVW + QCB SHORT off | 15 | +370.2% | −135.4% | **−29.6%** |

Diverting MVAVW SHORT is supported. Diverting QCB SHORT is **not** yet: it
adds little, and it makes the worst day worse.

---

## 3. Every short mechanism tested

Each result is net per trade after fees, slippage and (where held) funding.
IS is in-sample and OOS out-of-sample (split in §1). A mechanism counts only if
it is positive in **both** halves.

| # | Mechanism (fixed before testing) | TF | IS | OOS | Verdict |
|---|---|---|---|---|---|
| 1 | Breakdown of 24h low on 2× volume, stop above 6h high | 1h | −0.01% | −0.18% | no |
| 2 | Same, only when alts are weak (index < EMA24, breadth < 45%) | 1h | −0.02% | −0.14% | no; the gate adds nothing |
| 3 | Failed mover: ran +25%, 8% off peak, fresh 6h low | 1h | **+0.32%** | **−0.49%** | no; did not survive OOS |
| 4 | Relative weakness: bottom decile of 24h return, weak market | 1h | −0.02% | −0.22% | no |
| 5 | Pump fade: 24h ≥ +30% with a bearish wick bar | 1h | −0.32% | −0.41% | no |
| 6 | Negative funding ≤ −0.05%, down day, below EMA20 (24h hold) | 1h | −0.13% | −0.06% | no; see §4 |
| 7 | Random liquid-alt short, 24h hold (baseline) | 1h | +0.23% | −0.18% | alt drift, not edge |
| 8 | Trend short: below 20-day average, 7d return < 0 | 1h | +0.20% | **0.00%** | no |
| 9 | Flush continuation: short a fresh 4h low during an alt flush | 15m | −0.52% (PF 0.50) | (book window) | no |
| 10 | Failed mover at 15m: prior up-mover closes back under SMA99 | 15m | −0.39% to −0.47% | (book window) | no |
| 11 | BTC-led: BTC 15m ≤ −0.5%, short the weakest alts | 15m | −1.03% | (book window) | no; alts bounce |
| 12 | MVRTP SHORT, exact rules, full year | 15m | −0.57% | −0.31% | no |
| 12a | … only in alt-bear regime | 15m | −0.50% | −0.36% | no; a regime gate won't save it |
| 13 | BREAKDOWN_SHORT replica (break, then dead-cat retest) | 15m | −0.15% | −0.18% (PF 0.62) | no, as a raw pattern |
| 14 | Upside trap: sweep of a 6h high that closes back under | 15m | −0.15% | −0.19% | no |
| 14a | … plus seller absorption (taker-buy share ≤ 42%) | 15m | −0.12% | −0.15% | helps a little, still negative |

**Two structural facts explain the table [measured, rows 9–14; reading
inferred]:**

- **In this market, intraday down-moves in alts snap back and up-moves
  persist.** Any short that enters *after* weakness is buying into the snap
  back: flush continuation, BTC-led shorts, failed movers, MVRTP SHORT. The
  mirror of our winning long is the wrong shape.
- **Where the entry shape is right, cost decides the result.** The
  failed-upside shorts (rows 13–14) are roughly flat gross on stops 0.6–0.9%
  wide. The 0.17% round trip is then the difference between flat and a loss.
  The live versions of these paths may clear it through the engine's
  selection layers, which a backtest cannot replicate [inferred]. Their
  samples are still too thin to prove it (§2.4).

---

## 4. The one real bearish signal, and why it doesn't pay

**Forward return after the funding rate, across all liquid perps [measured].**
Sampled every 4h. Entry is at the next open; a negative number is good for a
short. The CI is day-clustered on the 24h figure.

| Funding (per 8h) | n | Symbols | Next 24h (IS / OOS) | 95% CI 24h | Next 72h | Next 168h |
|---|---|---|---|---|---|---|
| ≥ +0.10% | 3,358 | 68 | **+1.15%** (+0.34 / +2.28) | [−0.20, +2.48] | +2.07% | +5.33% |
| all liquid (baseline) | 340,694 | 517 | −0.27% (−0.34 / −0.12) | [−0.63, +0.06] | −0.80% | −1.85% |
| ≤ −0.05% | 20,269 | 195 | **−0.61%** (−0.58 / −0.69) | [−1.06, −0.15] | −1.85% | −4.67% |
| ≤ −0.10% | 13,225 | 176 | −0.91% (−0.95 / −0.84) | [−1.49, −0.37] | −2.58% | −6.41% |

**What this shows:**

- **High positive funding is bullish, not bearish.** Fading "crowded longs" is
  the wrong direction here.
- **Negative funding predicts a decline.** The sign and size hold in both
  halves (−0.58% in-sample, −0.69% out-of-sample over 24h), and the full-year
  CI excludes zero. The out-of-sample CI alone just touches it. The effect
  spans 195 symbols, and no single symbol contributes more than 6% of the
  samples in either half.
- **Why it doesn't pay:** a short in that state *pays* the funding. Simulated
  as a real trade, the 24h hold earned **+0.56% gross and paid −0.52% carry**.
  Held 72h, out-of-sample: +1.72% gross against −1.50% carry.
- **The market prices it** [inferred]: persistent negative funding is the fee
  for a crowded hedge. It is not an edge.

Listing decay (shorting young listings) was also measured. Its buckets are
inconsistent between halves: days 1–7 flip sign, and days 60–120 go from
+0.17% to −0.90%. It is noise, not a mechanism.

---

## 5. Recommendations

1. **Divert `MOVER_AVWAP_SCALP` SHORT now.** It is one click on Control →
   Routing (already signed off). It is the only still-live short whose CI
   sits almost entirely below zero ([−0.98, +0.02]). Since 14 Aug it cost the
   book **33.5%** and deepened red days.
2. **Do not build a mirror, breakdown, flush or funding short path.** Thirteen
   mechanisms (plus a random baseline) were tested over 12 months, and none
   survives out-of-sample after costs. Shipping one would add a second losing
   leg on the same red days, not a hedge.
3. **Keep the "failed move up" shorts live and let them earn evidence.**
   These are SR_FLIP_RETEST, BREAKDOWN_SHORT, FAILED_AUCTION_RECLAIM,
   LIQUIDITY_SWEEP_REVERSAL and the TREND_PULLBACK_EMA SHORT side.
   - They are the only short structure with positive live numbers.
   - They short *at a high*, after the up-move fails, with a tight stop. That
     is the right shape given §3.
   - Only SR_FLIP (n=6) has a CI clear of zero, so nothing gets promoted on
     this.
   - If more short flow is wanted, the evidence-first way is to read these
     paths' **SHORT** rows on the dark feed (`/signals/dark-live`) and promote
     through Control → Promotions only where the dark evidence holds up.
4. **Hunt red days on the long side, where they come from.**
   - Red days are MVRTP-long continuation failures (§2.2), and stop clusters
     are not the driver (§2.3).
   - The next research step needs **entry timestamps and entry features**. The
     public book lacks them; the engine's closed-signal record and the
     entry-feature lane (`/signals/entry-features`) carry them.
   - The question to answer: *what distinguishes a long entered on a day the
     movers stop following through?* Candidates: stack separation, time since
     ignition, the mover's 72h run, breadth at entry.
5. **Know the long edge is period-dependent.**
   - On the 78 liquid core symbols, the MVRTP-long replica was **−0.16%**
     from Sep 2025 to Apr 2026 and **+0.50%** from May to Sep 2026.
   - No short tested here would have offset a return to the first period.
     That risk has to be watched on the long side (edge-matrix verdicts, the
     path scorecard), not hedged with a short that has no edge.

---

## 6. What was not tested, and why

- **Minute-scale mechanisms** (BTC→alt lead-lag, liquidation cascades): the
  archive has no forced-order history, and 1m data for the whole universe was
  out of scope. These are the most plausible *untested* short edges. They
  would need the live `@forceOrder` and `@aggTrade` streams, measured forward
  in a dark lane.
- **Order-book depth:** there is no history, and `DEPTH_LIVE_FOR_CONSUMERS` is
  off.
- **The engine's selection layers** (scoring, gates, router) cannot be
  replicated offline. That is why the 15m replica fires 6× more often than
  the book, and why its numbers are read for direction only.
- **Movers over the full year:** the 12-month 15m run covers the liquid core
  78. The mover universe is covered at 1h for 12 months and at 15m for the
  book window only.

Scripts: `scripts/research/shorts_2026_09_24/` (fetch, panel, simulator,
every experiment above). The raw data is not committed; `fetch.py` rebuilds
it from the public archive.
