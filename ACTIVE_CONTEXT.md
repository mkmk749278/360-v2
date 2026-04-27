# ACTIVE CONTEXT
*Updated: 2026-04-27 — MOM-PROT session end (momentum profit-protection gate shipped)*

---

## Current Phase
**Phase 1 — Signal Quality Validation**
Engine is live. INV-1 fix (regime-flip & EMA-crossover creation-relative) confirmed working —
fast failures eliminated, hold times extended, 1 PROFIT_LOCKED win (SEIUSDT +0.84%).
This session diagnosed and fixed the remaining CLOSED domination: momentum invalidation
was killing profitable signals immediately after the 10-min age gate opened.
No paying subscribers yet.

---

## Current Priority (Do This First)

**Run the VPS monitor** after 6–12 hours of MOM-PROT running.

What to look for in the next zip:

1. **`outcome_label` distribution shift** — CLOSED should drop substantially. Signals that previously consolidated at profit (SOONUSDT +1.36%, DOGEUSDT +0.70%, WUSDT +0.32%) should now hold past consolidation and reach TP1 or trail to PROFIT_LOCKED.
2. **`quality_by_setup.SR_FLIP_RETEST` win rate** — should start approaching or exceeding 10%. Even a small improvement is validation MOM-PROT is working.
3. **`outcome_label="SL_HIT"` rate** — watch that it doesn't spike. The protection only activates when price is >0.5× SL distance in favor, so losing signals should still be killed normally.
4. **Median terminal duration** — should extend beyond 907s (current) as signals survive consolidation.
5. **30–60s breach cluster** — should still be 0% (existing candle OHLC fix unaffected).

---

## All Confirmed Bug Fixes (Deployed to main branch)

| Fix | File | Session |
|---|---|---|
| MIN_LIFESPAN 180s → 30s | `config/__init__.py` | prior |
| WS fallback limit=2, raw[0] | `src/websocket_manager.py` | prior |
| EXPIRED outcome label | `src/performance_metrics.py` | prior |
| OI readiness present=count>0 | `src/scanner/__init__.py` | prior |
| Indicator cache includes candle count | `src/scanner/__init__.py` | prior |
| OI backfill at boot (30 snapshots) | `src/order_flow.py` | prior |
| TREND_PULLBACK_EMA confirmation entry | `src/channels/scalp.py` | prior |
| Universal SL minimum 0.80% | `src/scanner/__init__.py` (_enqueue_signal) | prior |
| SL minimum (0.50, 0.80) all channels | `config/__init__.py` | prior |
| TP confirmation buffer 0.05% | `src/trade_monitor.py` | prior |
| WATCHLIST spam disabled | `src/signal_router.py` | prior |
| SL/TP uses 1m candle HIGH/LOW | `src/trade_monitor.py` | prior |
| ATR minimum SL in evaluators | `src/channels/scalp.py` | prior |
| stop_loss field on SignalRecord | `src/performance_tracker.py` (line 64) + `src/trade_monitor.py:329` | prior |
| **Q5-A: LSR `build_signal_failed` telemetry** | `src/channels/scalp.py:913` | **Audit-2 (5d81b23)** |
| **Q5-B: WHALE `build_signal_failed` telemetry** | `src/channels/scalp.py:~1531` | **Audit-2 (5d81b23)** |
| **Q4-A: SR_FLIP TP1==TP2 collapse in 4h-data branch** | `src/channels/scalp.py:~2475/2479` | **Audit-2 (5d81b23)** |
| **Q7-A: TPE/DIV_CONT accept WEAK_TREND (conservative widening)** | `src/channels/scalp.py:~961/2920` | **Audit-2 (759b7fc)** |
| **Q4-B: TP-ladder monotonicity helper across LSR/TPE/LIQ_REV/FUNDING_EXT/CLS** | `src/channels/scalp.py:259` (helper) + 5 wire-up sites | **Audit-2 (75f5556 / #226)** |
| **deploy.yml: skip VPS deploy on ACTIVE_CONTEXT.md doc-only commits** | `.github/workflows/deploy.yml` | **(44ca45b / #227)** |
| **INV-1: `_check_invalidation` regime-flip & EMA-crossover rules creation-relative** | `src/trade_monitor.py:555–615` | **INV-1 (750e067 / #228)** |
| **MOM-PROT: momentum invalidation profit-protection gate** | `src/trade_monitor.py:617` | **MOM-PROT (this session)** |

---

## Known Live Issues (post MOM-PROT)

1. **Win-rate metric still unvalidated** — MOM-PROT just deployed; awaiting first monitor zip. Multiple signals (SOONUSDT +1.91% MFE, DOGEUSDT +0.78%, WUSDT +0.54%) were killed by momentum invalidation while in profit. Expect these to now reach TP1 or PROFIT_LOCKED.
2. **CVD data sparsity RESOLVED in current monitor** — Previous monitor showed 5.3% CVD presence. Current monitor shows **97.3%**. Unknown cause — no code change. DIVERGENCE_CONTINUATION still 0 signals because divergence condition not met (`cvd_divergence_failed=31392`), not because data is missing. No action needed on CVD infrastructure.
3. **WEAK_TREND emission rate** — Q7-A widened TPE/DIV_CONT to accept WEAK_TREND, but live regime classifier produces TRENDING_*, RANGING, DISTRIBUTION — no WEAK_TREND observed. Q7-A may be dead code until classifier changes. No action.
4. **10 of 14 paths still silent at funnel level** — 6 of 14 now emitting (Phase 1 path threshold met ✅). Remaining 8 need separate diagnosis.
5. **BASEDUSDT SL_HIT: LONG in TRENDING_DOWN / ATR%ile=100** — SR_FLIP went LONG against TRENDING_DOWN at maximum volatility. Signal may be technically valid as counter-trend SR_FLIP but high-ATR TRENDING_DOWN is hostile for LONG entries. Worth watching if this pattern repeats — could add ATR%ile gate to SR_FLIP (but not now; only 1 data point).

---

## Phase 1 Scorecard (current)

| Metric | Required | Status |
|---|---|---|
| Win rate (TP1 or better) | ≥ 40% | ~9% (1 PROFIT_LOCKED of ~11 recent) — MOM-PROT expected to improve |
| SL hit rate | ≤ 60% | **11.1%** ✅ |
| Signals per day | ≥ 5 | **~13.6/day** ✅ |
| Active paths | ≥ 6 | **6 of 14** ✅ |
| Fast failures | 0 | **0%** ✅ |
| Max consecutive SL losses | ≤ 5 | Non-consecutive ✅ |

Blocker: win rate. Everything else passing.

---

## Next PR Queue (post MOM-PROT)

| Priority | Task | Scope |
|---|---|---|
| 1 | Run monitor in 6–12h — validate MOM-PROT produced `TP1_HIT` / `PROFIT_LOCKED` instead of CLOSED on profitable signals | Observation; data-driven |
| 2 | SR_FLIP geometry diagnosis — if SL rate rises above 30% post-MOM-PROT (signals holding longer means more SL exposure) | Conditional on next zip |
| 3 | Investigate DIVERGENCE_CONTINUATION: CVD data is now available (97.3%) but divergence condition never triggers (`cvd_divergence_failed=31392`). Likely the divergence thresholds or lookback need calibration. | Code investigation |
| 4 | Decide on STRONG_TREND/BREAKOUT_EXPANSION widening for TPE/DIV_CONT | Needs WEAK_TREND data first — defer |
| 5 | DRY cleanup: refactor FAR + SR_FLIP_RETEST to use `_enforce_tp_ladder_monotonicity` helper | Low value, defer until Phase 1 exits |
| 6 | **Q2 — Implement orderblock detection** | Out of Phase 1 budget; Phase 2 spec |

---

## Open Risks

- **MOM-PROT SL exposure**: Signals now holding through consolidation means more signals reaching SL if direction was wrong. The 0.5× SL threshold is conservative (requires meaningful profit before protection activates) but SL rate must be watched carefully in the next zip.
- SR_FLIP geometry: TP1==TP2 fix is partial. Structural SL may still be too tight on some pairs.
- WEAK_TREND widening for TPE/DIV_CONT unmeasured — monitor must catch a high SL rate fast or revert.
- 8 still-silent paths need separate root-cause work (regime gates, FVG gates, MTF gate suppressors).
- Low signal volume = slow feedback loop. Each shipped change takes 24–48h to validate.

---

## Audit-2 Findings That Did NOT Ship

- **Q1 (per-path SL stats API method)** — skipped: data already in truth-report via `build_quality_by_setup`; no operational gap.
- **Q2 (orderblock detection)** — deferred to Phase 2; out of Phase 1 budget.
- **Q6 (FAR scalar struct extrema)** — observation only; not a bug.
- **Q7-B (ORB env-disabled)** — intentional per PR-06; not a bug.

All other audit findings (Q4-A, Q4-B, Q5-A, Q5-B, Q7-A) are shipped.

---

## How to Raise Issues in Project Chat

- Share monitor zip → CTE analyzes and responds with findings + action
- Share Telegram screenshots → CTE reads timing, prices, compares to chart
- Describe what you observed → CTE reads the actual code before proposing any fix

---

*Read alongside `OWNER_BRIEF.md` at every session start.*
*Update this file at every session end.*
