# Market-first signal methodology — spec for owner approval (2026-10-23)

**Owner's direction (2026-10-23):** *"What we need to fix is how signals need to
be produced for best results in the crypto market … are the paths correct, are
our strategies and gates strong enough, are we treating every day the same, are
we following any methodology … 100% clarity on the crypto market first, then we
decide. Changing something based only on signal history is not a good idea."*

**Status: PROPOSAL. Nothing in this document changes the engine.** It asks the
owner to approve a method, and the tests that decide each part of it, *before*
any code is written.

Labels: **[measured]** = a query or replay run in this session, reproducible with
`scripts/research/market_first_2026_10_23/`. **[inferred]** = reasoning from
measured facts. **[prior]** = an earlier research doc in this repo.

---

## Short answer

1. **The engine decides bottom-up.** 17 live paths each read one coin's own
   chart, every hour of every day, with the same thresholds. Market state reaches
   the decision only through a few narrow gates (§2). Nothing first asks *"what
   kind of market is this, and which strategies belong in it?"*
2. **The market is not one market.** Over 400 days, BTC spent 44% of days in a
   downtrend, 31% in an uptrend and 25% in a range, and each one behaves
   differently. Alts follow BTC (correlation ~0.65) and fall harder than they
   rise (§1).
3. **The same entry flips sign with the market.** Buying a pullback in a strong
   coin earns in BTC up and range markets and loses in BTC downtrends, **in both
   halves of the year** [measured, §1.4]. That is the October book.
4. **The proposal:** decide top-down in three layers — *market state → which
   playbook is allowed → time and coin* (§3) — and prove each piece on **400 days
   of market candles replayed through the engine's real evaluators** (§4), not on
   five months of our own signals.
5. **What this does not propose:** new scalp shorts. Two earlier studies and this
   one agree that shorting weakness does not pay after costs (§1.5).

---

## 1. What the market does [measured unless labelled]

Data: Gate.io USDT perpetuals, 1h candles, 2025-09-18 → 2026-10-23, BTC plus 29
large alts (ETH, SOL, XRP, BNB, DOGE, ADA, LINK, AVAX, SUI, LTC, DOT, NEAR, APT,
ARB, OP, INJ, TIA, SEI, WIF, PEPE, FET, RENDER, AAVE, UNI, HYPE, ENA, TAO, ONDO,
JUP). Regime label = **yesterday's** BTC daily close against its 20-day SMA, with
the SMA's 5-day slope: above and rising = UP, below and falling = DOWN, else
RANGE. Nothing reads the future.

### 1.1 Three regimes, and down lasts longest

| BTC regime | Days | Median run | BTC / day | Alt basket / day |
|---|---|---|---|---|
| DOWN | 168 (44%) | 7 days | −0.55% | **−0.76%** |
| UP | 119 (31%) | 3 days | +0.40% | +0.60% |
| RANGE | 95 (25%) | 3 days | +0.02% | **−0.33%** |

BTC fell 30% over the window. The alt basket fell in 10 of 14 calendar months,
while September 2026 alone was +40% — the month most of our profit comes from.
**Alts bleed even when BTC goes sideways.**

### 1.2 Alts follow BTC, harder on the way down

| | Correlation | Beta, BTC up | Beta, BTC down |
|---|---|---|---|
| Hourly | 0.63 | 1.24 | 1.41 |
| Daily | 0.68 | 1.05 | 1.38 |

Medians across the 29 alts. Consistent with the downside asymmetry found in
Finance Research Letters (NARDL study on ETH/XRP/LTC, 2020) [prior/external].

### 1.3 The next move is almost unpredictable from the last one

Correlation of the past move with the next move of the same length, pooled across
30 coins: 1h −0.002 · 4h −0.017 · 24h +0.040 · 3d −0.091 · 7d +0.050. **A pattern
alone carries almost no edge on these coins; context has to supply it.**
[inferred] Same conclusion as `REGIME_VALIDATION_2026_07_03.md`: the 5m regime
label has no forward directional information at 30 minutes.

### 1.4 Context flips the sign of an entry

Next-12h price move after the event, by yesterday's BTC regime. No stop, no fee.
The year is split at 2026-04-06 so each half is its own test.

| Event | Half | UP | RANGE | DOWN |
|---|---|---|---|---|
| **Pullback in strong coin** (−3% in 4h, +10% over 3d) | H1 | +0.23 (86) | +0.70 (76) | **−0.29** (262) |
| | H2 | +0.45 (488) | +0.93 (120) | **−0.19** (144) |
| **Oversold dip in weak coin** (−3% in 4h, ≤0 over 3d) | H1 | +0.17 (482) | −1.38 (1555) | **+0.55** (3673) |
| | H2 | +0.03 (990) | +0.96 (565) | **+0.71** (1546) |
| Bounce +3% in 4h | H1 | −0.22 | −0.48 | −0.13 |
| | H2 | +0.06 | +0.50 | +0.17 |
| Break below 24h low | H1 | −0.33 | −0.85 | −0.03 |
| | H2 | +0.16 | +0.25 | +0.33 |
| Break above 24h high | H1 | +0.17 | −0.87 | +0.03 |
| | H2 | +0.03 | −0.11 | +0.38 |

Only **two** results keep their sign in both halves:

- **Strong-coin pullbacks work in UP and RANGE and fail in DOWN.** That is
  `MOVER_TREND_PULLBACK`'s thesis, and the failure mode we saw in October.
- **Oversold dips in weak coins bounce in DOWN.** A mean-reversion long, not a
  short.

Breakouts, breakdowns and fading bounces flip between halves — no stable edge.

### 1.5 Shorts [prior + measured]

- `SHORTS_RESEARCH_2026_09_24.md`: 13 short mechanisms over 12 months; **none
  survives out-of-sample after costs.** Red days come from long continuation
  failures, not from a missing short.
- `SHORTS_MARKET_RESEARCH_2026_09_25.md`: one short edge survives — shorting the
  run-up to large insider unlocks, a two-week swing trade, already measured dark
  (`src/unlock_shorts.py`).
- This study: after a break below the 24h low in DOWN, the coin moved −0.03%
  in H1 (a short barely gains, less than the fee) and **+0.33%** in H2 (a short
  loses) — no edge.
- Our own book, June–October [measured]: shorts lost in **every** BTC regime,
  including DOWN (−0.13% per trade, n=352).

### 1.6 Time of day and weekday

BTC volatility relative to the average hour:

| UTC | IST | Relative volatility |
|---|---|---|
| 13:00–16:00 | 18:30–21:30 | **1.32–1.65×** (US open) |
| 04:00–08:00 | 09:30–13:30 | 0.82–0.83× |
| 10:00 | 15:30 | 0.74× (quietest) |

Saturday 0.57×, Sunday 0.75×, weekdays 1.11–1.17×. Direction by hour is noise.
External work agrees on lower weekend volatility and US-hours dominance (arXiv
2111.15351; Quantpedia, Bitcoin intraday anomalies) [prior/external].

Our book, June–October [measured]: 04–08 UTC is the only losing window
(**−$71** over 557 trades at $100/signal, fees included). Weekends **−$14**
(943 trades) against weekdays **+$287** (2,691).

---

## 2. What the engine does today [measured from code, `main` @ f8f317a]

| Layer | What exists | How much it decides |
|---|---|---|
| Paths | 17 live evaluators in `src/channels/scalp.py`, each on one pair's own candles | Everything starts here |
| Weekly BTC macro | `btc_state.macro_direction` (50-week MA + structure) | Hard gate, but **only** on `CT_LONG_MACRO_GATE_SETUPS` = LSR, SR_FLIP longs and `CT_SHORT_MACRO_GATE_SETUPS` = LSR, FAR, BDS shorts. **`MOVER_TREND_PULLBACK` — 60% of the book — is not in it** |
| Intraday BTC direction | `btc_direction` | 6-point confidence penalty, only when BTC 1h *and* 4h both oppose |
| Graded BTC state | `btc_state` haircut | **Stamped, OFF** (`BTC_STATE_HAIRCUT_ENABLED=false`; NO-GO 2026-07-03) |
| Session | `kill_zone` | **OFF** on `360_SCALP` |
| Market context | `market_context.py` (session × phase × volatility × rotation) | Keys the edge matrix; the per-context emission floor learns from **our own outcomes** |
| Per-pair regime | `regime.py` 5m label | Scoring points and compat gates; no forward validity [prior] |

So the engine *has* most of the parts. They are scattered, mostly soft or dark,
and none of them sits **above** the paths deciding which ones may run.

---

## 3. The method

Three layers, decided in this order, once an hour:

### Layer 1 — Market state

Output: `trend ∈ {UP, RANGE, DOWN}` × `vol ∈ {LOW, NORMAL, HIGH}`, stamped on
every signal.

**Which definition is a test, not a choice.** Four candidates, judged by
pre-registered criteria:

| Candidate | Source | Timescale |
|---|---|---|
| R1 | BTC daily close vs 20-day SMA + slope (used in §1) | days |
| R2 | `macro_direction` on BTC 1d (exists; today runs on 1w) | weeks |
| R3 | `btc_state` b, bucketed | hours |
| R4 | **Breadth:** share of the core 75 above their own 20-day SMA | days |

Selection criteria, fixed before the test runs:

1. **Separates the future, both halves:** next-24h alt-basket return differs
   UP vs DOWN with the same sign in H1 and H2.
2. **Stable enough to trade:** median run ≥ 3 days, ≤ 6 flips a month.
3. **Computable live** from data the engine already loads (1d is seeded for every
   pair).

Combinations (e.g. R1 ∧ R4) are allowed and count as extra candidates in the
familywise tally.

### Layer 2 — Playbook per state

A path runs in a state **only if its cell passes the Phase-1 test** (§4). The
starting hypotheses, from §1 and the live book:

| Path | UP | RANGE | DOWN | Evidence today |
|---|---|---|---|---|
| `MOVER_TREND_PULLBACK` LONG | **on** | test | **off?** | Market proxy: +/+ in UP, −/− in DOWN (§1.4). Live Jun–Oct: +0.26% UP, +0.03% RANGE, **+0.33% DOWN (n=409)** — **conflicts** with the proxy. Settling this is Phase 1's first job |
| `MOVER_AVWAP_SCALP` LONG | test | test | test | Live negative in all three (−0.10 / −0.07 / −0.28) |
| `QUIET_COMPRESSION_BREAK` | test | off? | test | Breakouts in RANGE: −0.87 / −0.11 (§1.4) |
| "Failed move up" shorts (SR_FLIP, BDS, FAR, LSR, TPE short) | test | test | test | [prior] the only short shape with positive live numbers; all thin |
| New: **oversold-dip long** in DOWN | — | off | **candidate** | +0.55 / +0.71 in both halves (§1.4); needs its own evaluator, stop and fees |
| Unlock short (swing) | dark lane | dark lane | dark lane | [prior] the one surviving short edge |
| Every other path | test | test | test | Too thin per cell today |

"off" means **diverted to the dark lane** (`path_retirement` pattern), never
deleted, so a path keeps measuring in the states it is barred from.

### Layer 3 — Time and coin

- **Time window:** ACTIVE (weekday 08–21 UTC) · QUIET (04–08 UTC) · WEEKEND.
  Hypothesis: QUIET and WEEKEND either skip or need a higher bar. Tested per cell
  like the regime.
- **Coin:** in DOWN, prefer coins with low downside beta to BTC (the coupling is
  already computed by `btc_state.compute_downside_coupling`).

### Fewer trades is part of the method

Fees took about half of October's loss (−$50 of −$106). Every layer above
removes trades; the test reports fee savings separately so a rule cannot look
good only because it trades less.

---

## 4. How it gets proved

### Phase 1 — replay on a year of candles (no engine change)

1. **Calibrate the replay first.** Run `src/backtester.py` (it replays
   `ScalpChannel` evaluators on candles) over Jun–Oct 2026 and compare per path
   with the recorded book. The replay covers evaluators, **not** the scanner gate
   chain, scoring or router, so it will over-produce; the check is that each
   path's per-trade sign and rough size match. A path that does not calibrate is
   reported as such and not judged.
2. **Replay 400 days** on the core 75 pairs, with each evaluator's own SL/TP and
   **0.07% round-trip fees**. Movers: reconstruct daily top-24h gainers from the
   same candles and label them — the live promotion history cannot be rebuilt
   exactly, and that limitation is stated, not hidden.
3. Stamp every replayed signal with all four Layer-1 candidates and the Layer-3
   window.
4. **Acceptance, per (path, side, state) cell** — the `STATISTICAL_CHANGE_POLICY`
   rules applied to a replay:
   - ≥ 200 trades in the cell
   - net-of-fees average > 0 **in both halves**
   - report n, dates, net expectancy with **95% CI**, win rate, profit factor,
     max drawdown
   - print the number of cells tested; a cell that passes only on the pooled
     window does not pass
5. **Output:** a filled playbook table and a written report. Owner reviews.

Data: Gate.io candles work from a cloud session; a confirmation run on Binance
klines from the VPS follows, because live trades fill on Binance.

### Phase 2 — dark, live (engine change, measurement only)

- Stamp the chosen market state and time window on every signal (**measurement
  ON**).
- A `playbook` shadow gate stamps `would_block` with the cell that blocks it; it
  blocks nothing (**effect OFF**).
- Ops panel the same day: blocked vs kept, by state and path, PnL % first.
- Runs ≥ 21 days and ≥ 200 signals (policy rule 1).

### Phase 3 — activation, per state, owner sign-off

Each state's playbook goes live separately. Diverted paths keep measuring in the
dark lane, so every decision can be re-read.

---

## 5. Known gaps

- §1 uses 30 large coins. Promoted movers are smaller and more volatile; Phase 1
  must test them separately.
- One year that mostly fell. A real bull leg is underrepresented (UP runs are
  short), so UP cells will be thinner than DOWN cells.
- The §1.4 events are proxies of our setups, not the setups. Only the Phase-1
  replay says what our actual evaluators do.
- The conflict on `MOVER_TREND_PULLBACK` LONG in DOWN (live +0.33% vs proxy
  −0.25%) is unresolved. It may be the regime definition, the proxy, or the
  September rally falling inside "DOWN" days. Phase 1 decides.

---

## 6. Decisions for the owner

1. **Approve the method** (three layers, top-down).
2. **Approve the four regime candidates and the selection criteria** in §3, as
   written, before the test runs.
3. **Approve the Phase-1 acceptance rules** in §4.
4. **Scope:** include the Layer-3 time-window test in Phase 1? (Recommended.)

Phase 1 changes nothing live and can start on approval.

## Sources

- `docs/SHORTS_RESEARCH_2026_09_24.md`, `docs/SHORTS_MARKET_RESEARCH_2026_09_25.md`,
  `docs/REGIME_VALIDATION_2026_07_03.md`, `docs/BTC_STATE_ACTIVATION_BRIEF.md`,
  `docs/STATISTICAL_CHANGE_POLICY.md`
- Bitcoin's asymmetric effect on altcoins (NARDL), Finance Research Letters 2020:
  https://research.tees.ac.uk/en/publications/the-asymmetric-effect-of-bitcoin-on-altcoins-evidence-from-the-no/
- Day-of-week volatility in Bitcoin: https://arxiv.org/pdf/2111.15351
- Quantpedia, intraday and overnight anomalies in Bitcoin:
  https://quantpedia.com/are-there-seasonal-intraday-or-overnight-anomalies-in-bitcoin/
- Momentum in crypto, summary of studies: https://tradingstrategy.ai/docs/learn/momentum.html
- Erasmus thesis, trend rules in crypto (long-only vs long-short):
  https://thesis.eur.nl/pub/44390/
