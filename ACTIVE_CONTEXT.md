# ACTIVE CONTEXT

*Live operational state. Updated at every session end.*

---

## Current Phase

**Per-path entry-quality audit.** Reviewing each of the 14 evaluators for entry-generation mechanics through the scalping doctrine lens (`OWNER_BRIEF.md` §3.2).

---

## What's Currently Working

- **Engine** healthy, scanning 75 pairs continuously, deploying via GitHub Actions
- **Monitor** runtime truth report on `monitor-logs` branch — regime distribution, gate metrics, confidence component breakdown, invalidation quality audit
- **Risk-component scoring** calibrated for scalp R-multiples (max credit at 2.0R)
- **Regime classifier** BB-width VOLATILE threshold at 8.0% (env-overridable)
- **HTF mismatch policy** soft penalty (not hard block) for SR_FLIP / QCB / FAR
- **QUIET-block doctrine** uniform 65 paid-tier floor — no scrap-routing exempts
- **Universal 0.80% SL floor** plus per-setup caps active
- **Invalidation quality audit** classifying every kill as PROTECTIVE / PREMATURE / NEUTRAL post-30-min
- **Phase 2 entry-quality audit checklist** in working memory (ten dimensions: pattern detection, direction logic, HTF, entry zone, confirmation candle, indicator gates, SMC inputs, risk plan, telemetry truth, invalidation compatibility)

---

## Open Queue

### Ready to work
- **Continue per-path entry-quality audit** through the remaining evaluators. Done so far: SR_FLIP_RETEST, QUIET_COMPRESSION_BREAK, FAILED_AUCTION_RECLAIM. Remaining: LSR / WHALE / TPE / LIQ_REVERSAL / VSB / BDS / ORB / FUNDING / DIV_CONT / CLS / PDC.

### Pending data
- **TP1 ATR cap re-derivation** — caps (1.8R / 2.5R / uncapped) on SR_FLIP / FUNDING / DIV_CONT / CLS were shipped before risk recalibration. Wait for Phase 1 invalidation-audit data on TP1 hit rates per setup × ATR-bucket before deciding.

### Pending owner decision
- **OPENING_RANGE_BREAKOUT** currently `feature_disabled`. Rebuild with proper session-anchored range logic, or delete the path entirely. Not a CTE call.

---

## Working Pattern (per-path audit)

1. Read evaluator end-to-end
2. Score against the audit checklist
3. For each defect: ask **"would fixing this make signals more profitable for paid subscribers?"**
   - If no → defer, document, move on
   - If yes → implement, tests, OWNER_BRIEF entry, ACTIVE_CONTEXT note, PR
4. After PR merges, branch off fresh `main`, audit next path

---

## Key Files for the Current Phase

| Concern | File |
|---|---|
| 14 evaluators | `src/channels/scalp.py` |
| Confidence scoring | `src/signal_quality.py` |
| Regime classifier | `src/regime.py` |
| Scanner gate chain | `src/scanner/__init__.py` |
| Trade lifecycle | `src/trade_monitor.py` |
| Truth report parser | `src/runtime_truth_report.py` |
| Invalidation audit | `src/invalidation_audit.py` |

---

## Reference: HTF Policy Cheat Sheet

| Path category | HTF treatment |
|---|---|
| Trend-aligned by regime gate (TPE / DIV_CONT / CLS / PDC) | None |
| Internally direction-driven (WHALE / FUNDING / LIQ_REVERSAL) | None |
| Counter-trend by design (LSR / FAR) | Soft penalty when 1H AND 4H both oppose |
| Structure with optional counter-trend (SR_FLIP / QCB) | Soft penalty when 1H AND 4H both oppose |
| Breakout (VSB / BDS / ORB) | None |
