# How a crypto short actually earns — market-structure research (2026-09-25)

**Owner's ask:** *"Don't only depend on our data and paths. Deeply understand
the crypto market and its reality. How can we actually achieve good signals in
shorts? Purely research on the crypto market; don't compare anything to
existing data."*

**Ground rules.**
- Only the public Binance archive (`data.binance.vision`) and DefiLlama's public
  unlock-schedule dataset are used.
- Nothing from the engine is read: no ledger, no book, no path. Nothing here
  is compared against our own results.
- Ten hypotheses were written down from market structure and committed
  **before any data was read** (`HYPOTHESES.md`, commit `cd92f95`).
- Results are labelled **[measured]** (run in this session) or
  **[literature]** (a cited source). Reasoning from either is **[inferred]**.

## Short answer

1. **In crypto, a short is paid by a *scheduled* seller, not by a price
   pattern.**
   - Of ten pre-registered ideas, **one survives: shorting the run-up to large
     insider token unlocks.**
     - Team and investor tokens vest on a published date.
     - Holders who paid next to nothing for them sell, and the market leans
       on the price for two weeks beforehand.
   - A second idea, shorting liquidation cascades, looked like an edge
     (+0.16%/trade over 26,000 trades) until I found that the archive's
     open-interest stamps run five minutes ahead of the price. Timed honestly,
     the hour after a cascade is flat: **once you can see a cascade, it is
     over.**
   - New-listing decay also has a scheduled seller. It passes on raw numbers,
     then disappears once BTC is hedged out or any stop is applied.
   - Everything that reads price, positioning or flow and bets on weakness
     failed after costs: breakdowns, funding, premium, retail crowding,
     perp-led rallies, loser momentum and time of day.
2. **The surviving short is a two-week swing trade, not a scalp.**
   - It needs two squeeze filters, and with them it earned **+3.2% per trade
     with a 20% stop** and **+3.7% hedged against the alt market** (no stop).
     Both are after all costs.
   - Those filters were exploratory, so the numbers are a hypothesis for
     forward measurement, not a validated result.
   - It fires about once a day across ~50 tokens.
   - Unfiltered, one trade in ten first moves 40% against the position.
3. **The market charges for every obvious bearish story.**
   - It charges through funding: crowded shorts pay the longs.
   - It charges through squeezes: low-float tokens run several-fold before
     they fall.
   - A stop tight enough for a scalp is taken out by the squeeze before the
     drift pays. **Squeeze risk is the price of the edge.** It is managed by
     not shorting crowded or running names, by position size and by
     diversification. A tight stop does not manage it.

---

## 1. The reality of the short side

### 1.1 Who sells in crypto, and when is it knowable?

| Seller | Why they must sell | Knowable in advance? | Evidence |
|---|---|---|---|
| **Insiders at unlock** (team, investors, advisors) | Vested tokens have a cost basis near zero; funds must return capital | **Yes**: vesting schedules are public | [literature] Keyrock, 16,000+ unlocks: ~90% show negative price pressure, starting ~30 days before; team unlocks worst (≈ −25%); bigger unlocks hit 2.4× harder |
| **New-listing distribution** (airdrop recipients, early backers, market makers on loan + call deals) | Low float, high FDV; market makers hold loaned tokens with a call option and every incentive to sell into listing demand | **Yes**: the listing date is public | [literature] Empirica, Binance 2024 listings: −22.7% at 3 months, −37.6% at 6 months, only 5.5% positive at 6 months; 2025 listings: 24 of 27 negative |
| **Force-liquidated longs** | The exchange sells their position at market | **Partly**: only once it starts; OI and price show it in real time | [literature] 10 Oct 2025: $19B liquidated in a day, OI −43%, alts −58% intraday |
| **Arbitrageurs** (basis) | Sell the perp when it trades above spot | Yes, but priced | [literature] carry profitability collapsed after 2024 and turned negative in 2025 |
| Discretionary sellers | News, macro | No | — |

**The first rule this implies [inferred]:** an edge exists where the seller is
*forced* or *scheduled* and the timing is public, but the size of the selling is
not yet in the price. A pattern that merely shows the market has *already* sold
tells you the selling happened. It does not tell you more is coming.

### 1.2 Why the short side is harder than the long side

- **Squeeze asymmetry.**
  - A long's worst case is −100%. A short's is unbounded, and in low-float
    perps several-fold squeezes are routine.
  - In this research [measured]: one unlock short went 4.7× against the
    position within 16 days (RIVER). Among the new-listing shorts, a quarter
    went ≈2× against first.
- **Crowding is charged through funding.**
  - When a bearish story is public, shorts crowd, funding goes negative and
    the shorts pay the longs.
  - [measured] Unlock shorts paid −1.2% funding over 16 days on average;
    new-listing shorts paid −6.1% over 53 days. One (COAI) paid **165% of
    notional** in funding alone.
  - [literature] MYX's funding reached −1.09% per interval during a squeeze.
- **Short-horizon reversal after aggressive flow.**
  - [literature] At 15 minutes, 90% of 183 Binance pairs reverse direction
    after taker-driven moves, against 2.7% of US stocks.
  - That is liquidity provision: whoever sells into a fast drop is paid by the
    bounce.
  - It is too small to trade (≈1.3 bp gross against 5 bp of cost). It is large
    enough to punish anyone who shorts *after* an ordinary dip.
- **High positive funding is bullish, not bearish.** [measured, H6 below]
  Price keeps rising into high-funding settlements. "Longs are crowded, fade
  them" is the wrong direction in this market.

---

## 2. Method

**Data:**
- Binance USDT-M perps, Sep 2025 – Aug 2026: daily, 1h and 5m klines;
- 5-minute metrics: open interest, top-trader and global long/short ratios,
  taker ratio;
- 1h premium index; 1h spot klines (spot taker flow); funding history;
- DefiLlama `emissionsIndex`: 340 insider cliff unlocks ≥ 0.5% of max supply
  on 61 tokens with a Binance perp.

**Universe:**
- 589 perps that were ever liquid (trailing-7d mean quote volume ≥ $10M) and
  trade like crypto;
- TradFi perps are excluded by the weekend-volume rule;
- liquidity is re-checked point-in-time at every entry.

**Costs:** 0.07% fee plus 0.05% slippage per fill (0.17% round trip), plus
**actual funding** for every hold that spans a settlement.

**Split and pass bar:**
- in-sample Sep 2025 – Apr 2026; out-of-sample May – Aug 2026;
- the net short PnL must be positive in **both** halves;
- the day-clustered 95% interval must exclude zero;
- each hypothesis is read against a **control** differing only in its
  condition.

**Amendment:** OOS ends 31 Aug instead of 23 Sep, because September funding
is not yet in the archive.
- It was written before any test ran.
- It was **committed** only in `f9cf494`, after H1 had run, so the git record
  alone cannot prove the order.
- It removes three weeks from every hypothesis alike, and no result was
  looked at on the longer window.

---

## 3. Results — ten hypotheses

Net short PnL per trade, after costs and funding. A positive number means the
short made money.

| # | Hypothesis (mechanism) | n | Net/trade | 95% CI | IS / OOS | Verdict |
|---|---|---|---|---|---|---|
| **H1** | **Insider cliff unlock ≥0.5% of supply: short T−14d → T+2d** | 319 (56 tokens) | **+5.66%** | [+2.03, +8.54] | +6.38 / +4.26 | **passes**; BTC-hedged +3.83% [+0.31, +6.60] |
| H2 | New perp listing: short day +7 → +60 | 142 | +14.0% | [+3.1, +24.1] | +16.5 / +1.3 (n=23) | passes raw; **fails hedged** (+2.6% [−7.2, +11.7]); dies with any stop |
| H3 | OI builds while price is flat, then a 24h-low break (trapped longs) | 294 | +0.59% | [−0.19, +1.58] | +0.77 / +0.10 | fails (right direction; control −0.04%) |
| H4 | Perp-led rally with no spot buying, then first lower bar | 166 | −0.74% | [−2.15, +0.47] | −0.53 / −1.17 | fails: these rallies **continue** |
| H5 | Perp premium ≥0.25% and ≥ its 99th pct | 2,870 | +0.03% | [−0.65, +0.63] | −0.07 / +0.24 | fails |
| H6 | High funding: short the hour into settlement | 7,049 | −0.25% | [−0.38, −0.11] | −0.20 / −0.38 | fails: **price rises** into high-funding settlements |
| H7 | Retail accounts crowded long, top traders reducing | 7,717 | +0.23% | [−0.21, +0.73] | +0.34 / −0.06 | fails |
| H8 | Weekly: short the bottom decile by 14d return | 880 | +1.72%/wk | [−1.63, +4.91] | +1.58 / +2.10 | fails; market-neutral +0.88% [−0.99, +2.66] |
| H9 | Short alts 13:30–15:30 UTC (US open) | 256 days | −0.09% | [−0.25, +0.07] | −0.09 / −0.08 | fails: +0.08% gross, eaten by costs |
| H10 | Long-liquidation burst (OI −1.5% and price −2% in 15m): short next bar, hold 1h | 27,664 | −0.21% | [−0.31, −0.10] | −0.20 / −0.23 | fails: gross **−0.01%**. The first run "passed" at +0.16% by reading OI five minutes early (§5) |

**Notes on the table:**
- **H3, H4, H7 and H10 read open interest**, and are shown after re-timing it
  (§5). The first runs read it five minutes early. H3/H4/H7 barely moved;
  H10 flipped from a pass to a fail.
- **H6 was first run with a look-ahead flaw of my own**, and is reported here
  corrected.
  - The first run selected on the funding rate *settled* at T, which is set by
    the premium during the hold itself.
  - Re-run on the previous settled rate (known at entry): −0.25%, as shown.
  - The flawed version read −0.67%.
  - Either way the hypothesis fails in the same direction.
- **H2 passes the registered bar and is still not an edge.** The raw drift is
  the alt bear market plus new-token decay. Hedged against BTC, its interval
  crosses zero. With a 15%, 25% or 40% stop it reads −2.1% / +1.7% / +0.4%,
  every interval crossing zero, because a quarter of these shorts went ≈2×
  against first.

---

## 4. The unlock short (H1) — the slow edge

### 4.1 What survives, and what doesn't [measured]

- **The raw result is partly the market.**
  - The **control** (the same tokens, entered ≥45 days from any unlock, same
    16-day hold) also made **+2.93%** raw. These tokens bled all year.
  - BTC-hedged, the control is **+0.97%** [−0.64, +2.55], while the unlock
    trades are +3.83%.
  - The unlock-specific difference is **+2.85 pp**, interval **[−1.03, +6.06]**:
    the right sign, not proven on its own.
- **Stops kill the naive version.**
  - The median trade first went **10.6%** against the short, one in ten
    went 40%+, and one in twenty went 50%+.
  - A 20% hard stop takes it to +2.07% [−0.38, +4.42], with OOS +0.13%.
- **Size matters, as the literature says.** Unlocks ≥2% of max supply:
  **+8.8%** [+4.3, +12.9], both halves positive (n=89, 30 tokens). This is one
  of three size buckets, so it is exploratory.
- **The mapping holds.**
  - Tokens are matched to perps by ticker, and only one H1 token (HFT, 11
    trades) disagrees with DefiLlama's price.
  - Excluding it *strengthens* the result: +6.16% raw, +4.31% hedged, OOS
    +5.65% raw.

### 4.2 Making it collectable: avoid the squeezes, not the drift

Four filters were declared in writing *before* running them (`HYPOTHESES.md`,
commit `f9cf494`). They come from §1.2, not from the losing rows. **They are
exploratory:** about ten cells were read, and none of this is validated.

| Variant | n | No stop | 20% stop | 40% stop |
|---|---|---|---|---|
| H1 as registered | 319 | +5.66% [+2.0, +8.5] | +2.07% [−0.4, +4.4] | +4.35% [+1.7, +6.8] |
| E1: skip if funding ≤ −0.03% (already crowded) | 290 | +5.06% | +1.86% [−0.5, +4.2] | +4.31% |
| E2: skip if the token rose >20% in the 14d before entry | 292 | +7.20% | **+3.38% [+1.1, +5.7]** | +5.39% |
| **E3 = E1 + E2** | 266 | +6.89% | **+3.23% [+1.0, +5.6]**; IS +4.38 / OOS +1.20 | +5.29% [+2.9, +7.7] |
| E3, hedged with an equal-weight liquid-alt basket (not BTC) | 266 | **+3.70% [+1.4, +5.9]**; IS +4.53 / OOS +2.24 | — | — |

**How to read it [inferred]:**
- The drift is real. What makes it unusable is the squeeze. Not shorting
  names that are already crowded, or already running, removes enough of the
  squeezes that a 20% stop survives.
- The alt-basket hedge strips out the bear market. **+3.7% per two-week trade
  is the estimate of what the unlock itself is worth.**
- The worst trade even after filtering still went **+378%** against the short
  (HFT). Risk is controlled by **position size and diversification**, never by
  the stop alone.

---

## 5. The liquidation-cascade short (H10) — an edge that was a timestamp

**As first run, H10 passed** [measured]:
- +0.16% net per trade over 26,365 trades on 570 symbols, interval
  [+0.07, +0.26];
- in-sample +0.09%, out-of-sample +0.38%;
- it survived dropping the 5 best days, symbol clustering, and 15m, 30m and
  2h holds;
- the long side of the same event lost −0.50%. It read like a textbook
  cascade continuation.

**One check broke it.** Entering one 5-minute bar later flipped it to
**−0.17%** [−0.26, −0.07]. A real edge does not change sign over five minutes.
A leak does.

**The cause, measured** (`oi_stamp_check.py`, 16 liquid symbols):

| An OI change stamped at *s* correlates with the price bar … | mean corr |
|---|---|
| ending 5m before *s* | 0.018 |
| **ending at *s*** (what the stamp claims) | 0.024 |
| **starting at *s*** | **0.093**, highest for every one of the 16 symbols |
| starting 5m after *s* | −0.014 |

So an archive metrics row stamped *s* describes the state at *s* + 5 minutes.
Read at its stamp, it tells a rule what open interest will be during the very
bar the rule then trades.

**Re-timed honestly** (`load.metrics` now shifts every row +5m):
- the short loses −0.21% net and the long loses −0.13%;
- gross is **−0.01% / +0.01%**, i.e. nothing either way.
- By the time a cascade is visible in the data, the move is over. The next
  hour is a coin flip that pays the fee.

**What it teaches [inferred]:**
- Forced sellers are real, but you cannot short *behind* them. Only someone
  already short when the cascade starts collects it.
- The useful rule for every short is **do not chase a dump.**
  - Timed honestly, the control (the same −2% drop with no liquidation)
    bounces: a short loses **−0.16% gross, −0.33% net** over the next hour.
  - After a real liquidation burst the next hour is merely flat.

**For anyone using this archive again:** `data.binance.vision` futures
`metrics` rows lead the price by one bucket. Re-time them before anything
reads them at their stamp.

## 6. How to build good short signals — design

**Principle 1: short a scheduled seller, not a shape.**
- Enter where selling is known before it happens (unlocks).
- Do not enter where price has merely fallen, or where a cascade has already
  hit (§5).
- Breakdowns, "failed" rallies, premium fades, funding fades, crowding
  contrarians and loser momentum all failed here, before any engine layer
  touched them.

**Principle 2: match the holding period to the seller.** Insiders distribute
over about two weeks around the unlock. A scalp around an unlock is a
different trade, and it was not tested.

**Principle 3: squeeze risk is the cost of the edge, so manage it
structurally.**
- Do not short names whose shorts are already crowded (funding ≤ −0.03%).
- Do not short names already running (+20% in 14 days).
- Size so that the stop is a tolerable loss. Diversify across many unrelated
  tokens.
- For the swing short, hedge with a liquid-alt basket if the aim is the
  unlock rather than the bear market.

**Principle 4: measure forward, dark, before anyone trades it.**
- **Unlock short.**
  - Ingest DefiLlama's `emissionsIndex` once a day (one public request; no
    per-user cost).
  - Stamp every qualifying unlock at T−14 with the E3 filters.
  - Walk each row to T+2 with a 20% stop.
  - About one candidate a day [measured: ~27 events/month over 12 months].
  - **Two to three months** gives a forward sample of 60–80.
- **What it would take in our product [inferred from the engine's config, not
  from its data].**
  - A 16-day swing short does not fit the current exit machinery. The TP
    ladder, the breakeven shift and the reconciler's 2-hour stale-close
    (`RECONCILER_MAX_POSITION_AGE_SEC`) would all close it long before the
    unlock pays.
  - It needs its own exit policy (time exit at T+2, a wide stop, no stale
    close) and its own sizing guidance.
  - The user must be able to see the funding carry.
  - It is a new evaluator path with a new exit shape, so owner sign-off
    applies twice.
- **Cascade rule for every short path:** do not open a short within the hour
  after a −2% / 15m drop. After a liquidation burst the short earns nothing
  gross; after an ordinary drop it loses to the bounce (§5).

**What not to build:** see the failures table. None of those mechanisms paid
after costs over twelve months, in either half.

---

## 7. Risks and what is not known

- **One year, one regime.** It contains the 10 Oct 2025 crash, a long alt
  decline and the Aug 2026 short squeeze. Unhedged results inherit that
  regime, which is why the hedged figures are the ones to plan on.
- **Unlock data quality.**
  - DefiLlama schedules can be revised after the fact, so a missed or
    postponed unlock could leak hindsight.
  - A second source (Tokenomist; paid API) should confirm the calendar before
    anything goes live.
- **Fills.** Slippage is modelled at 0.05% per fill. That is realistic for a
  daily-close swing entry on a liquid perp, and optimistic for the thinnest
  names.
- **Funding on the alt hedge basket** is not charged in E4. It is small next
  to the effect, but not zero.
- **Exploratory is exploratory.** E1–E4 and the ≥2% size bucket were read
  after H1's primary result. Only forward measurement can promote them.

## Sources

- [Keyrock — From Locked to Liquidity: what 16,000+ token unlocks teach us](https://keyrock.com/from-locked-to-liquidity-what-16000-token-unlocks-teach-us/)
- [Empirica — The Binance Effect: a 7-year analysis](https://empirica.io/blog/the-binance-effect-a-7-year-analysis-for-token-founders/)
- [BeInCrypto — 2025 Binance listings: 89% negative](https://beincrypto.com/binance-listed-tokens-negative-return/)
- [Flowdesk — Market-making models: retainer vs loan/call](https://www.flowdesk.co/insights/crypto-market-making-retainer-vs-loan-call-model)
- [Wublock — Inside market-maker token loans](https://wublock.substack.com/p/inside-the-black-box-of-market-maker)
- [CoinDesk Research — Inside crypto's $19B liquidation event](https://www.coindesk.com/research/market-spotlight-the-19-billion-liquidation-that-shook-crypto)
- [Short-horizon mean reversion in crypto markets (2026)](https://pith.science/paper/2608.21888)
- [Dobrynskaya — Cryptocurrency momentum and reversal](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3913263)
- [Wen et al. — Intraday return predictability in crypto](https://www.sciencedirect.com/science/article/abs/pii/S1062940822000833)
- [Cryptocurrency as an investable asset class (carry profitability)](https://arxiv.org/pdf/2510.14435)
- [CCN — MYX short squeeze](https://www.ccn.com/analysis/crypto/myx-finance-myx-all-time-high-price/)
- [DefiLlama emissions dataset](https://defillama-datasets.llama.fi/emissionsIndex)
- [Binance public data archive](https://data.binance.vision)

Reproduce: `scripts/research/shorts_market_2026_09_25/README.md`.
