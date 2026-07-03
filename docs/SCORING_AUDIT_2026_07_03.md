# Scoring System Audit + Redesign Design (S41, owner sign-off)

*Owner mandate: "more scored signals also losing… not actually based on score we
can't say good signals — sorting and finalising the signals does matter.
Profitable signals first, then volume."*

---

## Verdict

**The confidence score cannot rank our signals, and the audit shows this is the
expected output of its design, not a tuning problem.** r(confidence, PnL) ≈
−0.03 (107 signals, S19); the 70–75 band is the *worst* performer while 80+ is
the only positive band (fresh clean window). Raising the threshold cuts volume
without improving quality — measured twice.

## Why — three structural findings

**1. It is an uncalibrated checklist.** Every dimension awards points for the
*presence* of textbook features: any liquidity sweep = 10 pts, MSS = 8, FVG = 2
(SMC, max 25); regime affinity = 8/10/14/18 by category; volume tiers by ratio.
No weight anywhere was fit to measured outcomes. A checklist measures "how
textbook does this look," never "how often does this win."

**2. The distributions compress, so penalties do the real work.** Every signal
reaching the scorer already passed its evaluator's structural gates, so most
candidates collect similar base points (kept ≈ 69–78, filtered ≈ 52–59 across
all setups). The kept/filtered separation comes mostly from soft *penalties*
(OI flip, vol-CVD divergence, VWAP overextension). The additive base score is
close to a constant plus noise — which is exactly what an r ≈ 0 looks like.

**3. Its biggest input is half-blind.** SMC is the largest dimension (~20–25 of
~100) yet the `orderblocks` dependency source is `not_implemented` (100% absent
in every truth window) and `order_book` is top-of-book only, absent ~28% of
readings. The spoof penalty has never fired (0.00 in every window). We weight
most what we measure worst.

## What already exists (and why it doesn't work yet)

`StatisticalFilter` (src/stat_filter.py) is the *right idea already wired in*:
rolling win rates with Wilson lower bounds, hard-suppress < 25% WR, soft
penalty < 45%, fail-open on no history, checked at emit in the scanner.
Three defects neuter it:

1. **Wrong key.** It aggregates by `(channel, pair, regime)` — channel is the
   constant `360_SCALP`, and per-pair samples on a 75-pair scalp book are too
   sparse to ever clear `min_samples`. It discards `setup_class` (carried on
   the outcome object but unused) and has no `side`. Every edge we have proven
   this month lives at **setup × side × macro-context** (SR_FLIP short +5.1%
   vs long −21.8%; counter-macro shorts −8.1% vs aligned; MOVER long +2.05%).
2. **It ate contaminated data.** Until #685, phantom no-fill "trades" were
   recorded as losses. (Fixed; and as of this PR `EXPIRED_NO_FILL` is excluded
   from the stat store.)
3. **It can only veto, not rank.** It suppresses bad cohorts but contributes
   nothing to choosing *among* passing signals.

## Redesign — "sorting and finalising" by measured edge

Two-layer finalisation, exactly matching the owner's framing:

**Layer 1 — structural validity (keep, demote).** Evaluator gates + the
existing checklist score stay as a *sanity floor* (they encode real domain
rules — regime compatibility, geometry, penalties). The score stops being the
ranking; it becomes pass/fail plumbing.

**Layer 2 — measured cohort edge (new, the ranker).** For every candidate at
emit, look up its cohort — **(setup_class, side, regime_family, BTC-macro
direction)** — in a rolling outcome store (clean post-#685 data only):

- `edge = Wilson-lower-bound(win rate) × avg_win + (1−WR) × avg_loss`
  (expectancy, pessimistically bounded — small samples are *penalised*, not
  trusted).
- **Emit policy:** positive measured edge → emit; insufficient samples →
  emit with a per-cohort probation cap (N/day) so new cohorts can earn
  history without bleeding the book; negative measured edge with adequate
  samples → suppress (the SR_FLIP-long / counter-macro-short class, caught
  automatically instead of by monthly forensics).
- The Telegram/app **display confidence becomes the cohort's measured stats**
  (win rate + sample size), not the checklist number — honest by
  construction (Hard Limit: never fabricate performance numbers).

This generalises everything we hand-built this month: the SR_FLIP long
disable, the CT_SHORT macro gate, and the S19 "setup identity is the real
discriminator" finding all become *rows in a table the engine maintains
itself* — self-updating as regimes change, instead of owner-triggered
firefights per cohort.

## Rollout (dark-first, per production doctrine)

1. **STEP 0 (this PR, ships normally):** exclude `EXPIRED_NO_FILL` from the
   stat store (non-trades are not losses).
2. **STEP 1 (next, ships normally — observe-only):** extend the outcome store
   key to (setup, side, regime_family, macro); stamp each emitted signal's
   cohort edge + sample count into the perf record; log
   `[SHADOW] COHORT_EDGE` decisions (would-emit / would-cap / would-suppress)
   without acting. Also stamp the per-dimension checklist scores into perf
   records so the checklist itself can be calibrated against outcomes later.
3. **STEP 2 (owner sign-off):** after ≥2 weeks of clean shadow data, review
   the shadow verdicts against realised P&L. If the cohort ranker separates
   winners from losers where the checklist couldn't, activate
   (`COHORT_EDGE_RANKER_ENABLED=true`).
4. **STEP 3 (later, separate):** either implement the `orderblocks` source or
   remove its weight from SMC; recalibrate checklist weights on the
   component×outcome joins from STEP 1.

## Cost note

The cohort store is in-memory with JSON persistence (same pattern as the
existing RollingWinRateStore); lookups are dict reads at emit — zero new
network/Firestore I/O on any hot path.
