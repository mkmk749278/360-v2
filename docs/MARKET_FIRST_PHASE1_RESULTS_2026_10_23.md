# Market-first methodology — Phase 1 results (2026-10-23)

Companion to `MARKET_FIRST_METHODOLOGY_2026_10_23.md`, which fixed the tests
before this replay ran. The owner approved starting Phase 1 the same day.

Labels: **[measured]** = output of `scripts/research/market_first_2026_10_23/`
on the data below. **[inferred]** = reasoning from measured facts.

---

## Short answer

1. **The method's central bet did not survive.** None of the five market-state
   definitions tested says which way altcoins go next, in both halves of the
   year. The pre-registered test (§3 of the spec, criterion (a)) fails for every
   candidate, so **no state-gated playbook is justified** by this evidence.
2. **The Phase-0 headline did not survive either.** "Pullback longs fail in BTC
   downtrends" came from a price proxy. Replayed through the engine's real
   `MOVER_TREND_PULLBACK` evaluator, real stop geometry and real exit, the
   DOWN-state results are −0.003%, −0.047%, +0.030% and +0.028% per trade under
   the four definitions: no consistent sign.
3. **October was not a broken strategy on the main pairs.** On the 75 replayed
   core pairs, every live October Mover Trend Pullback long was reproduced by
   the replay, and those trades made **+0.13% per trade** live (126 trades). The
   month's loss sat in 145 trades on smaller pairs outside that set,
   **−0.47% per trade**. §6 has what the replay of those pairs shows.
4. **What did hold:** Mover Trend Pullback longs are the only path at or above
   zero over 13 months. Its edge is small and episodic, concentrated in
   January, August and September 2026. Several paths rank below it across
   every state (§5).

---

## 1. What was run

- **Data:** Binance USDT-M public archive klines (5m, 15m, 1h, 4h, 1d) for the
  first 75 pairs of the engine's regular universe as listed on ops `/pairs`
  on 2026-10-23, from Jun 2024 (1d warm-up) to 2026-10-21. 14,097 files.
- **Window:** every closed 5m bar from 2025-09-20 to 2026-10-21, ~114,000 bars
  per pair.
- **Per bar** (`replay.py`): the engine's `ScalpChannel.evaluate`, fed the
  inputs `_build_scan_context` builds, with every timeframe aligned by close
  time. Then the scanner's own post-evaluator steps: `build_risk_plan` (the
  per-setup stop cap and the target rebuild), the noise-floor widener, the
  0.8% / 1×ATR clamp, and the composite score (`SignalScoringEngine`, inputs
  assembled as the scanner does).
- **Exit:** the engine default (`BE_THEN_TP1_DEFAULT_ENABLED`): break-even arm,
  then full close at TP1, walked on 5m bars. A bar touching both the stop and
  TP1 counts as the stop.
- **Book** (`book.py`): the router's per-symbol lock, the 600 s scan cooldown,
  the per-path budget of 3 per direction, and the score floor of 65.
- **Fees:** 0.07% round trip on every trade.
- **Result:** 716,679 candidates, 72,391 booked trades.

Three defects were found and fixed while building the replay. Each would
have produced a confident wrong answer:

1. **`src/backtester.py` misaligned timeframes.** It sliced every timeframe by
   the same bar index, so a 5m evaluator read 1h and 4h bars from other dates.
   The `/backtest` admin command feeds it the live store, so this was live.
   Fixed in this PR (aligns on `open_time`, refuses what it cannot align;
   `tests/test_backtester_tf_alignment.py`). The replay does its own alignment.
2. **The replay skipped `build_risk_plan` at first.** Its stops sat at 6–17%
   where live stops lose ~3%. Caught by the first calibration check; the run
   was restarted.
3. **The replay's first scorer-free book** let through candidates live never
   sends, which then held the per-symbol lock against the trades live did
   send. The scorer was added; the run was restarted again.

## 2. Calibration — how far the replay can be trusted [measured]

Recorded book, Jun 1 – Oct 20 2026, core pairs:

| Check | Result |
|---|---|
| Live Mover Trend Pullback longs the replay also produced (same symbol and side, entry within 15 min) | **480 of 507 (95%)** |
| Same trades: outcome correlation | **0.84** |
| Same trades: average gross PnL | live **+0.68%**, replay **+0.30%** |
| Replay trades per live trade, Mover Trend Pullback long | **12×** |
| Score floor 65: share of live-taken trades kept / share of all candidates kept | 76% / 64% |

Read it this way:

- **Entries reproduce.** The strategy code, fed real candles, fires where live
  fired.
- **The exit simulation is ~0.4% per trade pessimistic** on identical trades.
  It cannot see the order of moves inside a 5m bar, and it does not model the
  live profit-lock. Absolute replay levels therefore read low. Comparisons
  between states use the same exit on both sides and are still valid.
- **Live is much more selective than the replay.** The score floor removes only
  about a third of candidates. Most of live's selectivity sits in the gates
  after scoring (cohort edge, entry quality, soft penalties), which candles
  cannot reproduce. So **this replay judges each path's idea across a year of
  markets, not the shipped filter**. The shipped filter is what Phase 2 would
  measure.

## 3. Market-state definitions — criterion (a) fails for all [measured]

Spread of next-day alt-basket return, UP-labelled days minus DOWN-labelled
days, in %. Criterion (a) requires the same positive sign in both halves.

| Candidate | H1 | H2 | Median run | Flips / month | (a) | (b) |
|---|---|---|---|---|---|---|
| R1 BTC vs 20-day SMA + slope | −1.021 | +0.183 | 3 d | 4.8 | ✗ | ✓ |
| R2 `macro_direction` on BTC 1d | −0.985 | +0.508 | 3 d | 4.0 | ✗ | ✓ |
| R3 `btc_state` b, hourly | −0.878 | +1.223 | 1 d | 17.1 | ✗ | ✗ |
| R4 breadth (share of the 75 above own 20-day SMA) | +0.079 | −0.167 | 2 d | 6.5 | ✗ | ✗ |
| R1 ∧ R4 | −0.563 | +0.149 | 3 d | 5.5 | ✗ | ✓ |

In H1 the sign is **inverted** for four of five: after a day labelled UP, the
next day was worse than after a day labelled DOWN. A label describes the move
that already happened. `REGIME_VALIDATION_2026_07_03.md` found the same at 30
minutes on the 5m label; this extends it to days, and to BTC- and
breadth-based labels.

## 4. Cells — what passes [measured]

380 (path, side, state) cells across the six labellings. A cell passes on
n ≥ 200 and net > 0 in both halves.

| Labelling | Cells with n ≥ 200 | Pass | Pass with 95% CI above 0 |
|---|---|---|---|
| R1 | 51 | 3 | 0 |
| R2 | 49 | 3 | 1 — MVRTP long, RANGE, +0.123% |
| R3 | 51 | 5 | 0 |
| R4 | 48 | 7 | 0 |
| R1 ∧ R4 | 50 | 3 | 0 |
| Time window | 60 | 4 | 2 — MVRTP long and short, QUIET (04–08 UTC), +0.158% / +0.211% |

**Three cells with a CI above zero, out of 380, is about what chance alone
produces** [inferred]. None of them is a basis for a rule:

- The R2 RANGE cell has no matching UP/DOWN pattern around it.
- The QUIET-window cells **contradict the live book**, where 04–08 UTC was the
  only losing window (−$71 over 557 trades, Jun–Oct). The replay cannot see
  live's filters, and the live sample is five months. Unresolved.

Mover Trend Pullback long, by R1, for reference:

| State | n | Net / trade | 95% CI | H1 | H2 |
|---|---|---|---|---|---|
| DOWN | 6,085 | −0.003% | −0.081 … +0.070 | +0.012 | −0.023 |
| RANGE | 3,539 | +0.089% | −0.010 … +0.183 | +0.032 | +0.140 |
| UP | 5,515 | +0.027% | −0.048 … +0.105 | −0.069 | +0.061 |

## 5. Paths over the whole year [measured]

Net per trade, all states, 13 months. Absolute levels read ~0.4% low (§2);
the ranking is the useful part.

| Path | Side | n | Net / trade | 95% CI |
|---|---|---|---|---|
| MOVER_TREND_PULLBACK | LONG | 15,139 | **+0.029** | −0.016 … +0.074 |
| MEAN_REVERT | SHORT | 6,063 | +0.005 | −0.040 … +0.053 |
| SR_FLIP_RETEST | SHORT | 2,240 | −0.005 | −0.050 … +0.042 |
| MOVER_TREND_PULLBACK | SHORT | 9,572 | −0.015 | −0.068 … +0.038 |
| FAILED_AUCTION_RECLAIM | SHORT | 3,734 | −0.016 | −0.078 … +0.045 |
| MOVER_AVWAP_SCALP | SHORT | 3,548 | −0.019 | −0.097 … +0.056 |
| MOVER_AVWAP_SCALP | LONG | 4,686 | −0.066 | −0.134 … +0.006 |
| LIQUIDITY_SWEEP_REVERSAL | SHORT | 4,743 | −0.056 | −0.109 … −0.006 |
| LIQUIDITY_SWEEP_REVERSAL | LONG | 4,888 | −0.098 | −0.150 … −0.043 |
| MEAN_REVERT | LONG | 4,124 | −0.103 | −0.155 … −0.052 |
| SR_FLIP_RETEST | LONG | 699 | −0.124 | −0.215 … −0.039 |
| QUIET_COMPRESSION_BREAK | SHORT | 906 | −0.155 | −0.301 … −0.006 |
| FAILED_AUCTION_RECLAIM | LONG | 3,829 | −0.176 | −0.232 … −0.119 |
| QUIET_COMPRESSION_BREAK | LONG | 905 | −0.274 | −0.422 … −0.120 |

Mover Trend Pullback long by month (replay, net per trade):
Sep 2025 −0.07 · Oct −0.07 · Nov −0.01 · Dec −0.13 · **Jan 2026 +0.28** ·
Feb −0.06 · Mar −0.01 · Apr +0.06 · May −0.01 · Jun −0.10 · Jul −0.06 ·
**Aug +0.25** · **Sep +0.12** · Oct +0.01. This matches
`SHORTS_RESEARCH_2026_09_24.md` §5: the MVRTP-long edge is period-dependent.

**By coin volume** (30-day average quote volume at entry), Mover Trend
Pullback long shows no consistent tier effect across the two halves; the
most liquid tier (> $250M/day) is the weakest in both (−0.07 / −0.17).

## 6. October [measured]

Live Mover Trend Pullback longs on core pairs, entries Oct 1–19 (the archive
ends Oct 21):

| Group | Trades | Live net / trade |
|---|---|---|
| On the 75 replayed pairs — all reproduced by the replay | 126 | **+0.13%** |
| On smaller pairs outside the 75 | 145 | **−0.47%** |

The smaller pairs swung harder in both directions: in the live record the
under-$25M/day tier was the best tier in August (+1.13%) and September
(+0.74%), and the worst in October (−0.45%). [inferred] That is market beta,
not a data or engine fault.

_Replay of the 99 smaller pairs for Sep 15 – Oct 21: see §6a._

## 7. What this means

- **Do not build the state-gated playbook as specified.** Phase 2 as written
  would have shipped a gate whose input does not predict.
- **The edge to protect is Mover Trend Pullback long, and it is thin.** Fees
  are ~0.07% of a ~0.03–0.4% edge. Fewer, better trades matter more than which
  day they are taken on.
- **The paths that rank below it in every state** (QUIET_COMPRESSION_BREAK both
  sides, FAILED_AUCTION_RECLAIM long, LIQUIDITY_SWEEP_REVERSAL long,
  MEAN_REVERT long) are candidates for a dark-lane retirement review **on live
  data**. The replay's exit bias means it cannot by itself say they lose live.
- **The QUIET-window conflict** (replay best, live worst) should be measured,
  not acted on.

## 8. Known gaps

- Universe is today's top 75. Pairs that left the list are missing
  (survivorship), and mover-promoted pairs are not replayed.
- Order flow, funding, open interest, order blocks and the post-score gates are
  not in the candles. Evaluators that need them took their fallback branches.
- The CT macro gates that run before `build_risk_plan` are not replayed.
- Exit simulation is ~0.4% per trade pessimistic on matched trades.
- One year that mostly fell (BTC −30%).

## Reproduce

```bash
S=/path/to/work
# klines: data.binance.vision, futures/um, 5m 15m 1h 4h 1d (see replay.py)
python scripts/research/market_first_2026_10_23/replay.py --zips $S/zip --out $S/rp --symbol SOLUSDT
python scripts/research/market_first_2026_10_23/book.py --replay $S/rp --out $S/book.csv
python scripts/research/market_first_2026_10_23/judge.py --book $S/book.csv --zips $S/zip \
    --live trades.csv --out $S/report   # trades.csv = ops /track-record per-trade export
```
