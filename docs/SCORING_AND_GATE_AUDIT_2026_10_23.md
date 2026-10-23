# Scoring and gate audit — pass by pass (2026-10-23)

**Owner:** *"look deep into scoring, and every gate pass by pass — is everything
acting correctly, or are there defects?"*

Method: every decision point between an evaluator returning a candidate and the
signal queue was read in `src/scanner/__init__.py` (`_prepare_signal`, the scan
loop, `_enqueue_signal`) and `src/signal_quality.py` (the scorer), on `main` @
f8f317a. Where a gate's effect could be measured, it was measured on the
Phase-1 replay (`docs/MARKET_FIRST_PHASE1_RESULTS_2026_10_23.md`: the engine's
real evaluators and scorer over 13 months of Binance klines, 1.13M scored
candidates). Labels: **[code]** read in the source, **[measured]** replay
output, **[inferred]** reasoning from both.

---

## Short answer

1. **A hidden cap of 4 open signals per direction, across all paths.**
   `MAX_CORRELATED_SCALP_SIGNALS = 4` hard-blocks any new candidate once four
   same-direction signals are active book-wide. On 2026-09-04 the owner ruled
   *"don't keep any cap on max signals of channel"*, the router caps were
   switched off and ops now reads `OFF — BOOK UNBOUNDED`. This cap sits
   upstream of the router, was not counted, and was not stamped. [code]
2. **Sixteen hard gates rejected candidates without stamping them**, including
   the composite-score floor, the most frequent reject. The Suppression Quality
   Audit could not measure any of them. **Fixed in this PR** (measurement only).
3. **The composite score ranks nothing below 80.** Bands from 0 to 80 all lose
   about −0.06% to −0.16% per trade; 80–85 is +0.04 / +0.08 and 85+ is
   **+0.28% per trade in both halves of the year**. The 65 floor separates
   nothing. [measured]
4. **Eleven confidence adjustments are dead code.** Funding, cross-asset, the
   narrative-pair bonus, both chart-pattern bonuses, the MTF ±3/−5, predictive
   confidence and confidence decay all write `sig.confidence` before it is
   overwritten by the composite score. [code]
5. **Several gates cannot do what their comments say:** the spoofing gate is
   always called with no order book, the meme-coin penalty names symbols that do
   not exist on Binance futures, the funding thresholds are 10–100× too large,
   and the SMC score's "recent sweep" bonus is always awarded and ignores
   direction. [code]
6. **The statistical filter's thresholds are applied to a Wilson lower bound**,
   so it blocks coins with normal win rates once they have 15 trades. It rarely
   arms today because restarts clear it. [code + measured]

---

## 1. The chain, in execution order [code]

"Stamped" is the state before this PR. Every row now stamps; pre-scoring stamps
are measurement-only (`pre_scoring=True`, so they never feed Layer C).

| # | Gate (scanner line on this branch) | Stamped before | Verdict |
|---|---|---|---|
| 1 | Conf-fail cooldown, 60 s per (symbol, channel), armed by QUIET floor fails (~7540) | no, not even counted | Works as written. Was silent. |
| 2 | Ranging low ADX / low ATR (7608, 7665) | no | Works. |
| 3 | Setup compatibility (7703) | yes | Works. |
| 4 | Execution quality (7733) | yes | Works. |
| 5 | MTF gate (7881) | no | Works. |
| 6 | Longs 15m-regime gate: blocks a long when 15m reads TRENDING_DOWN (7963) | no | **Owner decision.** The label has no measured forward validity (REGIME_VALIDATION_2026_07_03). |
| 7 | Counter-trend mover block (8005) | no | Works. |
| 8 | Cross-asset gate (8177) | no | Works. |
| 9 | CT macro gates, long and short (8391, 8413) | no | Works. |
| 10 | Risk plan: per-setup SL cap (8449) | no | Works. |
| 11 | **Correlated scalp cap: 4 active signals per direction, book-wide (8502)** | no, not counted | **Owner decision.** Contradicts the 2026-09-04 "no cap" ruling. |
| 12 | Base confidence floor (8525) | no | Works, but the confidence it reads is later overwritten (§3). |
| 13 | MTF hard block (8694) | no | Works. |
| 14 | Composite score floor, 65 (9005) | no | **Owner decision.** The 65 floor separates nothing (§2). |
| 15 | Stat filter: Wilson lower bound against 25% / 45% (9072) | no | **Defect.** §4. |
| 16 | Cohort edge (9170) | yes | Works. |
| 17 | Pair analysis critical (9213) | yes | Works. |
| 18 | SMC hard gate, smc ≥ 12 (9306) | no | Nearly inert because of the sweep defect (§2, §5). |
| 19 | Trend hard gate, indicators ≥ 10 (9336) | no | Works, including on MEAN_REVERT. Possible exception: MVAVW (§5). |
| 20 | Context edge RANGE_FADE, QUIET scalp block (9536, 9577) | yes | Works. |
| 21 | Layer C context floor, min-confidence (9741, 9775) | yes | Works. |
| 22 | Entry quality (9876) | yes | Works. |
| 23 | Global cooldown in the scan loop (10350) | no, DEBUG log only | Works. Was silent. |
| 24 | Scalp arbitration: one candidate per symbol per scan (10361, 10377) | no, DEBUG log only | Works. Was silent. |

Gates that do nothing at all, whatever their comments say:

- **Spoofing gate.** Called as `check_spoof_gate(direction, None, entry)`, so it
  never sees a book, while `smc_data["order_book"]` is available. [code]
- **Meme-coin penalty.** `_MEME_SYMBOLS` lists `PEPEUSDT`, `SHIBUSDT`,
  `BONKUSDT`, `FLOKIUSDT`. Binance futures lists them as `1000PEPEUSDT` and so
  on, so it never matches. [code]
- **Funding gate and funding score.** Thresholds of 0.01 / 0.02 compare against
  Binance's decimal rate (0.0001 is a normal 0.01%). `market_context` already
  treats 0.001 as extreme, so these fire only in a blow-off 10–100× beyond
  that. [code]
- **Kill-zone gate.** Off for `360_SCALP`. Intended, recorded here so nobody
  counts it as active. [code]

---

## 2. The composite score [measured]

Phase-1 replay, all paths, every candidate scored by the engine's own
`SignalScoringEngine`, the default exit (BE arm, full close at TP1), 0.07% round
trip charged.

| Score band | First half of the replay | Second half |
|---|---|---|
| every 5-point band from 0 to 80 | −0.06% to −0.16% / trade | −0.06% to −0.16% |
| 80–85 | +0.04% | +0.08% |
| 85+ | **+0.28%** | **+0.28%** |

By path at ≥ 80: MVRTP long +0.18% (H1 +0.15, H2 +0.20) against −0.12% at
65–80; MVRTP short +0.09%, positive in both halves; MEAN_REVERT strongly
positive and rare. Candidates overlap within a move, so n overstates
independent evidence. The CIs are in the Phase-1 results doc.

So the score does carry information, but only at the top. Raising the floor is
a scoring change and is owner sign-off. The replay is ~12× less selective than
live and ~0.4% / trade pessimistic, so the level does not transfer one-for-one;
the ranking is what transfers.

### SMC dimension (25 points)

- `sweeps[0].index >= -3` is meant to award "recent sweep" +5. `index` is an
  absolute bar position, never negative, so **every sweep gets the +5**. [code]
- Sweeps and MSS are scored without checking direction: a sweep that argues
  against the trade scores the same as one that argues for it. [code]

---

## 3. Confidence adjustments that are overwritten [code]

`sig.confidence` is written by each of these and then overwritten, first at
`sig.confidence = legacy_confidence` (~8508) and finally at
`sig.confidence = _score_result["total"]` (~8940). None of them reaches the
floor, the router, Layer C or the app:

funding ±, cross-asset adjustment, legacy confidence, setup-score total,
narrative-pair +2, `pattern_confidence_bonus`, chart-pattern bonus, MTF +3 / −5,
predictive `update_confidence`, confidence decay.

Level-confluence and structure bonuses ride inside `soft_penalty`, which is
applied only `if _total_soft_penalty > 0`, so a bonus with no penalty beside it
is dropped too.

None of this costs money today; the composite score is what decides. It costs
honesty: each of these reads as a live input in code review. The fix is either
to fold the ones that matter into the scorer (scoring change, sign-off) or
delete them.

---

## 4. The statistical filter [code + measured]

`stat_filter` blocks a (symbol, regime) once it has 15 recorded outcomes
(window 30) and the **Wilson lower bound** of its TP1 win rate is under 25%
(or 45% for the stricter tier). A lower bound is well below the point estimate
at n = 15: a pair winning 40% of 15 trades has a lower bound of about 20%, so
it is blocked. The thresholds read like win rates and are applied to something
much smaller.

It has no age expiry, and it lives in memory, so every restart clears it.
Measured footprint: 19 of 789 (pair, regime) cells reached 15 outcomes since
August, mostly BTC / ETH / BNB in QUIET. It does not explain October.

---

## 5. The SMC and trend hard gates

Component replay: the same harness with every score dimension stamped per
candidate, 25 pairs, 2026-05-01 → 2026-10-21, 140,203 candidates. Both gates
run after the 65 floor, so they are measured on candidates scoring ≥ 65. Net of
a 0.07% round trip. H1 / H2 are the two halves of the window by time.
Candidates overlap within a move, so n overstates independent evidence.
[measured]

**SMC hard gate (smc ≥ 12) is close to inert, and what it removes is not worse.**

| Path | Blocked (smc < 12) | Kept (≥ 12) |
|---|---|---|
| MVRTP long | 289 · +0.33% (H1 −0.05, H2 +0.68) | 31,857 · +0.02% |
| MVRTP short | 232 · +0.17% (H1 −0.08, H2 +0.45) | 25,049 · −0.13% |
| MVAVW long / short | 39 · +0.36% / 65 · +0.50% | −0.04% / −0.20% |
| LSR, MEAN_REVERT | 0 blocked | — |

It removes about 1% of candidates. That follows from §2: every sweep earns the
"recent" +5, so almost every candidate clears 12. The blocked slice reads
better than the kept one, but it is small and not consistent across halves on
MVRTP. **Not a lever either way.** Fix the sweep scoring first; then the gate's
threshold means something and can be measured again.

**Trend hard gate (indicators ≥ 10) is doing its job on most paths, including
mean reversion.** I expected it to be wrong on MEAN_REVERT, a counter-trend
idea. It is the opposite:

| Path | Blocked (< 10) | Kept (≥ 10) |
|---|---|---|
| MEAN_REVERT long | 1,381 · −0.09% | 1,329 · **+0.30%** (H1 +0.19, H2 +0.45) |
| MEAN_REVERT short | 1,889 · −0.17% | 2,025 · **+0.31%** (H1 +0.27, H2 +0.36) |
| MVRTP long | 3,510 · −0.09% | 28,636 · +0.04% |
| MVRTP short | 3,015 · −0.21% | 22,266 · −0.12% |
| LSR long / short | −0.28% / −0.16% | −0.06% / −0.04% |
| **MVAVW long** | 131 · **+0.45%** (H1 +0.16, H2 +0.69) | 4,318 · −0.05% |
| **MVAVW short** | 124 · **+0.37%** (H1 +0.79, H2 +0.03) | 3,832 · −0.20% |

So the gate stays. The one exception is MOVER_AVWAP_SCALP, where the slice it
blocks is positive in three of four half-windows while the kept one loses. That
is ~3% of the path's candidates and the gate is an owner sign-off item; it is a
candidate for a shadow arm, not a change.

**Which dimensions drive the ≥ 80 band** is answered by the same file and is
left for the scoring proposal; the band itself is in §2.
