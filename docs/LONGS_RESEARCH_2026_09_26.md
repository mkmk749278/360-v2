# Longs research — how the long side really does, path by path (2026-09-26)

**Owner's question:** *"Special investigation of Longs actually how we did for
shorts, so how are paths are doing good what to improve what we are doing
wrong."* The long-side companion to `SHORTS_RESEARCH_2026_09_24.md`.

**Short answer.**

- **The long side carries the book, and one path carries the long side.**
  `MOVER_TREND_PULLBACK` (MVRTP) is 74% of long trades and more than all of
  their profit. The other thirteen long paths together are flat.
- **About two-thirds of the long edge is lost at entry, before any exit rule
  acts.** Longs read +0.35%/trade on book prices over 30 days. The recorded
  entry drift is ~0.23–0.25%/trade, so on the tape the long book is roughly
  +0.10–0.12%.
- **The exits are not the problem.** Three changes were tested on Binance's
  1m tape: no break-even move, a wider stop, and a TP1 runner. Each is worth
  ≤0.03%/trade on the book, and every interval spans zero. Do not change MVRTP's
  exits.
- **The MVRTP long edge is fat-tailed and period-dependent.** Its best 50
  trades (4%) earn more than its total. It lost money in July and only turned
  positive in August.
- **Red days are long days.** Over 30 days the long book alone accounts for
  −99.5% of the −105.5% red-day loss. The worst days are MVRTP stop clusters.
- **No live long path has a retirement-grade result today.** The only long path
  whose interval sits below zero (SR_FLIP_RETEST) last delivered on 29 June.

Everything below is labelled **[measured]** (a query or tape walk run in this
session), **[recorded]** (a figure measured in an earlier session and not
re-measured here) or **[inferred]**.

---

## 1. Data and method

| Source | What | Span |
|---|---|---|
| Delivered book, the engine's public `/api/track-record/signals`, one call per UTC day (no day truncated) | **2,622 closed signals**: symbol, side, setup, `regime` at entry, outcome, `entry`, `closed_at`, `pnl_pct`, `net_pct`. **No entry or dispatch time.** | 2026-06-25 → 2026-09-26 06:00 UTC |
| Binance archive (`data.binance.vision`), USD-M 1m klines | Close day and next day for every long closed in the last 62 days: 1,503 of 1,555 symbol-days | 2026-07-25 → 2026-09-25 |

**Rules:**

- `net_pct` is the engine's own `pnl_pct − 0.07%` round trip. These are
  **book prices** (the stamped entry), not the tape.
- **Entry drift is not re-measured here.** The public record carries no
  dispatch time, so drift uses the recorded figures:
  - 0.226% mean over 605 rows to 6 Sep (`src/entry_fidelity.py` docstring);
  - 0.254% over 687 rows, 9–23 Sep (`AUDIT_2026_09_24` #12).
  Where a column says "≈ on the tape", it subtracts 0.23% and is
  **[inferred]**. The drift was measured on the whole book, which is
  ~75% long and ~62% MVRTP; its split by path and side is unmeasured.
- **Confidence intervals are 95% symbol-clustered bootstraps.** One symbol's
  repeated entries into one move are not independent evidence.
- **PnL % leads** (fixed-notional sizing, see ops `CLAUDE.md`).
- **Windows are measured back from 2026-09-26 06:00 UTC.**
- **`regime = UNPLACED` means the row closed before #817 started stamping the
  regime at entry (~28 Jul).** So a regime split is partly a time split.

Scripts: `scripts/research/longs_2026_09_26/` reproduce every table.

---

## 2. Long vs short, the whole book [measured]

| Window | Side | n | Mean net/trade | 95% CI | Total | Win |
|---|---|---|---|---|---|---|
| 93d (all) | LONG | 1,701 | **+0.247%** | [+0.08, +0.40] | +420.9% | 35.4% |
| | SHORT | 921 | −0.087% | [−0.22, +0.04] | −80.5% | 35.0% |
| 60d | LONG | 1,316 | **+0.374%** | [+0.18, +0.58] | +491.6% | 37.1% |
| | SHORT | 417 | **−0.259%** | [−0.48, −0.04] | −108.1% | 25.7% |
| 30d | LONG | 972 | **+0.352%** | [+0.13, +0.58] | +342.1% | 36.3% |
| | SHORT | 306 | **−0.234%** | [−0.46, −0.03] | −71.6% | 25.2% |
| 14d | LONG | 491 | **+0.545%** | [+0.21, +0.87] | +267.8% | 39.3% |
| | SHORT | 141 | **−0.346%** | [−0.69, −0.00] | −48.8% | 21.3% |

- **The two sides have the same win rate over 93 days, 35%.** What separates
  them is payoff: longs average +3.84% per win against −1.72% per loss, and
  shorts +1.79% against −1.10%.
- **On the tape [inferred], the 30d long book is roughly +0.12%/trade.** The
  shorts' drift is unmeasured.

---

## 3. Long paths, one by one [measured]

"≈ tape" = mean − 0.23% **[inferred]**. "Last" is the last close date.

| Long path | n (93d) | Mean | 95% CI | Total | ≈ tape | 30d n / mean | Last |
|---|---|---|---|---|---|---|---|
| **MOVER_TREND_PULLBACK** | 1,253 | **+0.339%** | [+0.14, +0.54] | **+424.7%** | +0.11% | 791 / +0.406% | live |
| FAILED_AUCTION_RECLAIM | 102 | +0.300% | [+0.01, +0.60] | +30.6% | +0.07% | 20 / +0.268% | 09-22 |
| QUIET_COMPRESSION_BREAK | 72 | +0.188% | [−0.22, +0.58] | +13.5% | −0.04% | 67 / +0.198% | live |
| MOVER_AVWAP_SCALP | 92 | −0.027% | [−0.47, +0.44] | −2.5% | −0.26% | 59 / +0.102% | live |
| DIVERGENCE_CONTINUATION | 63 | +0.004% | [−0.32, +0.36] | +0.3% | −0.23% | 13 / +0.435% | live |
| VOLUME_SURGE_BREAKOUT | 30 | −0.518% | [−1.26, +0.23] | −15.5% | — | — | retired (08-10) |
| SR_FLIP_RETEST | 27 | **−0.875%** | **[−1.58, −0.45]** | −23.6% | — | 0 | **06-29** |
| LIQUIDITY_SWEEP_REVERSAL | 19 | −0.606% | [−1.19, +0.02] | −11.5% | — | 0 | **06-30** |
| TREND_PULLBACK_EMA | 19 | −0.561% | [−1.40, +0.39] | −10.7% | — | 9 / −0.515% | 09-14 |
| FUNDING_EXTREME_SIGNAL | 10 | +0.530% | [−0.40, +2.86] | +5.3% | — | 1 / −3.07% | 09-02 |
| MEAN_REVERT | 7 | +0.719% | [+0.05, +1.29] | +5.0% | — | 7 / +0.719% | live |
| MA_CROSS_TREND_SHIFT | 5 | +0.935% | [−4.02, +6.44] | +4.7% | — | 4 / −1.992% | live |

**3.1 One path is the long product.**

- MVRTP earns +424.7%. The long side as a whole earns +420.9%.
- **The other thirteen long paths together: n=448, −0.008%/trade, total −3.8%.**
  In the last 30 days they are n=181, +0.117% [−0.19, +0.41]. That is
  ≈ −0.11% on the tape [inferred].
- So about 180 non-MVRTP longs a month reach subscribers without
  measurably earning [inferred].

**3.2 The two clearly negative long paths are not live problems.**

- **SR_FLIP_RETEST LONG** (CI [−1.58, −0.45]) and **LSR LONG** delivered every
  one of their rows between 25 and 30 June, and nothing since.
- SR_FLIP LONG's rows include QCOM, AMD, LITE and SNDK: stock perps that
  `crypto_perp_admission` now refuses.
- Retiring on three-month-old rows would be acting on a population that no
  longer exists.

**3.3 The paths to watch rather than act on.**

- **MOVER_AVWAP_SCALP LONG** reads −0.03% on the book (≈ −0.26% tape). Its
  SHORT half was retired on the same kind of evidence. The long CI is
  [−0.47, +0.44]: not proven either way.
- **TREND_PULLBACK_EMA LONG** wins 10.5% over 19 rows. Its TP1 is nearer than
  its stop (designed R:R ~0.79, see engine `CLAUDE.md`). Too thin to act on.
- **FAILED_AUCTION_RECLAIM LONG** is the only non-MVRTP long with a book CI
  above zero, and ≈ flat on the tape. Keep it.

---

## 4. MVRTP LONG, taken apart

**4.1 The edge arrived in August [measured].**

| Close month | n | Mean | 95% CI | Total | Win |
|---|---|---|---|---|---|
| June (from 25th) | 21 | −0.015% | [−1.02, +1.36] | −0.3% | 33% |
| July | 158 | **−0.174%** | [−0.68, +0.33] | −27.4% | 28% |
| August | 353 | **+0.470%** | [+0.03, +0.91] | +165.8% | 41% |
| September | 721 | **+0.398%** | [+0.14, +0.65] | +286.6% | 36% |

- The 24 Sep shorts research found the same shape on a 12-month 15m replica
  of MVRTP's rules **[recorded]**: −0.16% from Sep 2025 to Apr 2026, and +0.50%
  from May to Sep 2026.
- **The long edge depends on the period.** July on the live book was
  negative, and the replica says most of the past year was too [inferred].
- **This is the largest strategic risk in the book.** There is no second long
  engine to carry a month like July.

**4.2 The edge lives in the tail [measured].**

- **Total +424.7%. The best 50 trades (4% of 1,253) sum to +431.5%.** Without
  them the path is −6.7%.
- **The best ten** run +9.4% to +18.2% each.
- Stops: median −3.00% gross. **62% sit at or beyond −2.9%**, which is the 3%
  noise-floor cap, and the worst 5% reach −5.5% (gap-through).
- TP1 exits: median +3.98%.
- Two consequences:
  1. Any rule that clips the upper tail removes the edge, however good it
     looks on the median trade.
  2. A 30-trade cell of this path is mostly noise, because a single mover
     can swing it.

**4.3 Regime at entry [measured]** (UNPLACED = rows before #817, i.e. mostly July)

| Regime | n | Mean | 95% CI | Aug mean (n) | Sep mean (n) |
|---|---|---|---|---|---|
| VOLATILE | 226 | **+0.881%** | [+0.25, +1.48] | +0.67 (80) | **+0.93 (138)** |
| RANGING | 465 | +0.310% | [+0.04, +0.57] | +0.66 (140) | **+0.11 (317)** |
| TRENDING_UP | 404 | +0.304% | [−0.04, +0.68] | +0.12 (128) | +0.47 (259) |
| UNPLACED | 146 | −0.317% | [−0.75, +0.13] | — | — |

- **VOLATILE is the best cell in both months.**
- **RANGING is the largest cell in September (317 trades) and is ≈ flat on
  the book, so negative on the tape [inferred].** It was +0.66% in August.
  One month flipping is not grounds for a regime gate. The cohort-edge gate
  exists for exactly this, and it is the owner's switch.

**4.4 Outcome mix [measured].** Of 1,253 MVRTP longs:

| Outcome | n | Mean |
|---|---|---|
| SL_HIT | 490 | −3.12% |
| TP1_HIT | 219 | +4.50% |
| PROFIT_LOCKED | 218 | +4.39% |
| BREAKEVEN_EXIT | 281 | −0.07% |
| EXPIRED | 41 | +0.29% |

The BE share is rising: 16% in July, 22% in August, 24% in September. §5
tests whether that is costing money.

**4.5 Things tested and not significant [measured]:**

- **Entry price < $0.01:** −0.27% (n=133, CI [−0.93, +0.46]).
- **Close weekday:** Sunday −0.04%, with Friday and Saturday +0.66–0.68%.
  Every CI overlaps.
- **Close hour (4h buckets):** no pattern.

None is a filter candidate.

---

## 5. The exits, tested on the tape [measured]

**Method.**

- Each test starts at the trade's **actual** exit and walks Binance 1m bars
  forward for 24 hours. At that moment the alternative rule's state is known
  exactly:
  - **BREAKEVEN_EXIT → no BE move.** Price is back at entry. The original stop
    was never touched, because the BE stop sat above it. TP1 was never
    touched, or the row would read TP1. So without BE the trade is simply
    still open, with its original stop and target.
  - **SL_HIT → wider stop.** Price is at the old stop. The walk uses a stop
    further away, the current BE rule (arm at +2%, park at entry) and the same
    target.
  - **TP1 → runner.** Half closes at TP1, as now. The other half walks on
    toward 2× TP1, with its stop at entry, or at half the TP1 gain.
- **Levels the public record lacks** are set from the book's own medians:
  stop 3.0% and TP1 4.0%. The BE test is repeated at TP 3.0%.
- A bar touching both levels books the stop.
- The fee cancels, because both arms are one round trip.
- 1,109 MVRTP longs closed in the last 60 days; 41 had no archive coverage.

| Change | Trades it touches | Δ per touched trade | 95% CI | Δ total | ≈ Δ per book trade |
|---|---|---|---|---|---|
| **No break-even move** (TP 4%) | 246 BE exits | +0.13pp | [−0.28, +0.52] | +31.4pp | **+0.03%** |
| No break-even move (TP 3%) | 246 | +0.11pp | [−0.25, +0.44] | +28.0pp | +0.03% |
| **Stop 1pt wider** | 422 stop-outs | −0.01pp | [−0.22, +0.23] | −2.8pp | 0.00% |
| Stop 2pt wider | 422 | +0.06pp | [−0.24, +0.41] | +26.3pp | +0.02% |
| Stop 3pt wider | 422 | −0.01pp | [−0.38, +0.40] | −3.7pp | 0.00% |
| **50% runner after TP1**, stop at entry | 400 TP1 exits | +0.07pp | [−0.16, +0.29] | +26.5pp | +0.02% |
| 50% runner, stop at +½ TP1 | 400 | +0.08pp | [−0.09, +0.24] | +32.5pp | +0.03% |

- **The break-even move is roughly neutral.** Of 246 scratched trades, 107
  went on to +4% before −3%, and 134 hit the stop first.
- **78% of stopped-out MVRTP longs traded back up to their entry within 24
  hours.** That is the statistic that makes a wider stop look obvious, and the
  test says it does not pay. The ones that come back are offset by the ones
  that fall the extra points. The engine's own `CLAUDE.md` asks for exactly
  this check: *check the direction of every recommendation, not only its
  premise*.
- **Every exit change is worth ≤0.03%/trade on the book. The entry drift is
  ~0.23%, seven to eight times larger** [inferred from recorded drift].

---

## 6. Red days are long days [measured]

| Window | Whole book | Longs only |
|---|---|---|
| 30d | 11 red days, −105.5% | 11 red days, **−99.5%** |
| 60d | 26 red days, −220.8% | 25 red days, −190.6% |

Diverting MVAVW SHORT (done 24–25 Sep) removed the biggest short
contributor. What remains of red-day damage is almost all long-side.

**The worst long days are MVRTP stop clusters:**

| Day | Longs | Total | Stops | MVRTP |
|---|---|---|---|---|
| 1 Sep | 26 | −25.9% | 58% | 19 |
| 2 Sep | 28 | −17.5% | 39% | 22 |
| 1 Aug | 14 | −16.4% | 50% | 14 |
| 6 Sep | 25 | −12.6% | 52% | 19 |

The 24 Sep research found the cause **[recorded]**: red days are days the
previous day's movers stop following through (−0.22% vs +0.70% on green days),
not days the market falls.

**A lagged mover-activity gradient [measured]:**

- **The feature:** MVRTP long closes in the window **t−30h to t−6h**. It is
  lagged so that it cannot contain the trade itself, and can be known before
  entry. The rows are MVRTP longs over 60 days.

  | Closes in lagged window | n | Mean | 95% CI |
  |---|---|---|---|
  | 0–9 | 193 | +0.20% | [−0.41, +0.83] |
  | 10–19 | 249 | +0.34% | [−0.08, +0.77] |
  | 20–34 | 464 | +0.42% | [+0.09, +0.74] |
  | 35+ | 203 | **+0.79%** | [+0.25, +1.29] |

- **The gradient is monotonic.** A busy mover market pays better.
- **Adjacent intervals overlap,** so it is a hypothesis, not a filter. On the
  tape the quiet bucket is ≈ flat [inferred].
- **The lagged book result is not monotonic** (+0.17 / +0.74 / +0.13 /
  +0.58). So "pause after a bad day" has no support in this data.

---

## 7. Re-entries on the same symbol [measured, ordering inferred]

MVRTP re-enters a trending mover on every pullback. Rows are ordered by close
time, because the public record has no entry time. So "previous trade" means
the previous close. That trade may not have closed before this one was
entered.

| Entry on the same symbol within 24h | n | Mean | 95% CI |
|---|---|---|---|
| 1st | 691 | +0.18% | [−0.02, +0.39] |
| 2nd | 239 | +0.23% | [−0.24, +0.74] |
| 3rd | 124 | +0.50% | [−0.25, +1.21] |
| 4th+ | 199 | **+0.92%** | [+0.19, +1.48] |
| after a **win** on that symbol | 256 | **+0.95%** | [+0.45, +1.44] |
| after a stop | 157 | +0.44% | [−0.27, +1.13] |
| after a BE / other | 149 | −0.10% | [−0.79, +0.55] |

**Reading [inferred]:**

- **The first pullback on a fresh mover is the weakest entry.** It is 55% of
  MVRTP trades and ≈ −0.05% on the tape.
- The count of prior signals on a symbol is knowable at entry. Whether the
  previous one had *closed* needs the engine's own record, which carries entry
  time.
- **Not a filter yet.** Dropping first entries would raise the mean and lower
  the book total (+424.7% → +297.5%). On the tape it would be roughly +30pp
  better.

---

## 8. Shorts since the 24 Sep report [measured]

**Last 7 days, by path:**

| Path | n | Mean | 95% CI | Win |
|---|---|---|---|---|
| BREAKDOWN_SHORT | 11 | +1.08% | [−0.45, +2.75] | 36% |
| MOVER_AVWAP_SCALP | 17 | −0.30% | [−1.43, +0.83] | 29% |
| QUIET_COMPRESSION_BREAK | 15 | −0.40% | [−1.35, +0.39] | 13% |
| **LIQUIDITY_SWEEP_REVERSAL** | 9 | **−1.14%** | [−1.74, −0.63] | **0%** |
| **FAILED_AUCTION_RECLAIM** | 7 | **−1.81%** | [−2.42, −1.04] | **0%** |

**Over 30 days:**

- **LSR SHORT** is **−0.56% [−1.08, −0.10]** (n=39). That is the retirement
  case already put to the owner on 25 Sep.
- **FAR SHORT** is −0.29% [−0.82, +0.25] (n=40), against +0.02% over 93 days.
  It is deteriorating.
- **Removing LSR SHORT** takes the 30-day book from +0.212% to **+0.236%**
  per trade (+270.5% → +292.2%).
- **MVAVW SHORT's last delivered close is 24 Sep**, which is consistent with
  it being diverted on 24–25 Sep.

---

## 9. What to do, ranked by expected effect on subscriber PnL

1. **Research entry drift by path and side, before any exit or path change.**
   - It is ~0.23%/trade. That is seven to eight times any exit lever
     measured here, and about two-thirds of the long book's edge.
   - The obvious gate (refuse drifted signals) was measured and withdrawn
     on 7 Sep. It drops rows carrying −91.4% of book PnL but +20% of real
     PnL.
   - The unmeasured question is **how** the order is placed. A resting
     limit at the stamped entry, instead of market, sounds free. It is
     adversely selected: it fills the trades that come back and misses the
     ones that run, and §4.2 says the ones that run are the whole edge.
   - It needs dispatch timestamps: the engine's closed-signal record plus
     `read.entry_fidelity`, replayed on the 1m tape.
   - Research only; nothing on the money path.
2. **Leave MVRTP's exits alone** (§5). No break-even, stop-width or runner
   change clears 0.03%/trade. This saves a money-path change the
   78%-came-back statistic would otherwise have argued for.
3. **Retire LSR SHORT and set its promotion rule's direction to LONG.** This is
   the owner's two clicks from 25 Sep; §8 adds a 0-for-9 week.
4. **Stamp three entry features on MVRTP long, measurement only:**
   - the signal's index on its symbol within 24h (§7);
   - the outcome of the previous signal on that symbol, if it has closed
     (§7);
   - MVRTP enqueues over the prior 24h, the lagged activity of §6.

   They go through the entry-feature lane (`src/entry_features.py`). The
   stamps are measurement: ON and dark. Any gate built on them is a separate,
   owner-signed change. **Not built in this PR.**
5. **Retire no long path today.** No live long path has a CI below zero.
   Watch MOVER_AVWAP_SCALP LONG (≈ −0.26% on the tape) and
   TREND_PULLBACK_EMA LONG (10.5% win), and re-read them at 60 rows each.
6. **Track MVRTP LONG's rolling 30-day mean on the tape as the business KPI.**
   The long edge was negative in July and on most of the past year's replica
   (§4.1). If it rolls over, the book has nothing behind it. That is the case
   for keeping the non-MVRTP paths measured rather than cutting them to zero.

## 10. What this report cannot answer

- **Drift by path or side.** The public record has no dispatch time.
- **Exact per-trade stop and TP1 levels.** §5 uses the book's medians, and
  says so.
- **Whether the "previous trade" of §7 had closed before the next entry.**
- **Anything about the dark feed.** This report is the delivered book only.
