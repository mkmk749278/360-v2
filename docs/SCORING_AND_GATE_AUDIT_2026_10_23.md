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

_See §1 table (filled below)._
