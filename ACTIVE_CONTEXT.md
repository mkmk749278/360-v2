# ACTIVE CONTEXT
*Updated: 2026-04-26 — INV-1 session end (regime-flip & EMA-crossover invalidation made creation-relative)*

---

## Current Phase
**Phase 1 — Signal Quality Validation**
Engine is live; this session shipped a critical invalidation-logic fix
that should unblock the win-rate metric. No paying subscribers yet.

Current focus: monitor the next zip to validate that counter-trend
setups (SR_FLIP, FAR, LIQ_REV, FUNDING_EXT) now reach TP1/SL on their
own terms instead of being killed at +0.09% PnL by the previously
over-aggressive `_check_invalidation` rules.

---

## Current Priority (Do This First)

**Run the VPS monitor** after 6–12 hours of the INV-1 fix running.
Share the zip in the Project chat.

What to look for in the next zip:

1. **`outcome_label` distribution shift** — pre-INV-1, 19 of 20 closed signals were `CLOSED` (= INVALIDATED). Post-INV-1 we expect counter-trend setups to start producing real `TP1_HIT`, `TP2_HIT`, `SL_HIT`, and `EXPIRED` outcomes instead of `CLOSED` dominating.
2. **`quality_by_setup.SR_FLIP_RETEST`** — should have non-zero `tp_rate` and a real `sl_rate` (rather than the previous 0%/0% with everything CLOSED).
3. **Median hold time** — should extend past 13 min (the prior median was 13 min because invalidation cut signals at 600s+).
4. **Trend-following setups (TPE / DIV_CONT)** — should be unaffected by INV-1 (their fixtures use TRENDING_UP/DOWN at creation, where INV-1's behaviour is unchanged). Watch for any unexpected SL-rate jumps as a regression signal.
5. **30–60s breach cluster** still < 20% (prior fixes hold).

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

---

## Known Live Issues (post INV-1)

1. **Win-rate metric still unproven** — pre-INV-1 monitor showed 0% TP-rate because invalidation killed 95% of signals at +0.09% PnL before TP1. INV-1 fixes the over-aggressive invalidation; awaiting data to confirm signals now reach TP1/SL on their own terms.
2. **CVD data sparsity** — present in only 5.3% of scanner cycles per the prior monitor. Structurally kills DIVERGENCE_CONTINUATION, LIQUIDATION_REVERSAL, and FUNDING_EXTREME. **Not yet fixed.** Highest-leverage pending observability item.
3. **WEAK_TREND emission rate** — Q7-A widened TPE/DIV_CONT to accept WEAK_TREND, but the prior monitor showed no signals tagged with WEAK_TREND (live regime classifier produced TRENDING_*, RANGING, DISTRIBUTION). Q7-A may be dead code until/unless the classifier emits WEAK_TREND.
4. **10 of 14 paths still silent at the funnel level** — Q7-A unblocked 2 paths' regime gate but emission still requires all other gates to pass.
5. **`outcome_label="CLOSED"`** — pre-INV-1 dominated; expect substantial drop post-INV-1.

---

## Next PR Queue (post INV-1)

| Priority | Task | Scope |
|---|---|---|
| 1 | Read next monitor zip — validate INV-1 produced real TP1_HIT / SL_HIT outcomes | Observation; data-driven decisions |
| 2 | **CVD pipeline investigation** — `cvd: presence[absent=35073, present=1981]` in last monitor (5.3% presence). Trace why CVD aggregation is starved. | Investigate before fixing |
| 3 | SR_FLIP geometry root-cause (if SL rate is now measurable and > 60% post-INV-1) | Conditional on INV-1 data |
| 4 | Decide on STRONG_TREND/BREAKOUT_EXPANSION widening for TPE/DIV_CONT | Needs WEAK_TREND data first |
| 5 | DRY cleanup: refactor FAR + SR_FLIP_RETEST to use the `_enforce_tp_ladder_monotonicity` helper | Low value, defer until Phase 1 exits |
| 6 | **Q2 — Implement orderblock detection** | Out of Phase 1 budget; Phase 2 spec |

---

## Open Risks

- SR_FLIP geometry: TP1==TP2 fix is partial. If structural SL is still too tight, the path's SL rate stays elevated even with monotonic TPs.
- WEAK_TREND widening for TPE/DIV_CONT is unmeasured — pullbacks/hidden-divergences may behave differently in WEAK_TREND than in TRENDING_*. Monitor must catch a high SL rate fast or revert.
- 10-silent-paths is structural — Q7-A only addresses 2. Remaining 8 silent paths need separate diagnosis (FVG-only gates per Q2, MTF gate suppressors per scanner config, ORB env-disabled by design).
- Low signal volume = slow feedback loop. Each shipped change takes 24–48h to validate.

---

## Audit-2 Findings That Did NOT Ship

- **Q1 (per-path SL stats API method)** — skipped: data already in truth-report via `build_quality_by_setup` (`src/runtime_truth_report.py:196`); no operational gap.
- **Q2 (orderblock detection)** — deferred to Phase 2; out of Phase 1 budget. Algorithm choice (institutional FTB vs engulfing+imbalance) needs spec.
- **Q6 (FAR scalar struct extrema)** — observation only; FAR's wick-anchored SL + tail/reclaim filters carry the structural load. Not a bug.
- **Q7-B (ORB env-disabled)** — intentional per PR-06; not a bug.

All other audit findings (Q4-A, Q4-B, Q5-A, Q5-B, Q7-A) are now shipped.

---

## How to Raise Issues in Project Chat

- Share monitor zip → CTE analyzes and responds with findings + action
- Share Telegram screenshots → CTE reads timing, prices, compares to chart
- Describe what you observed → CTE reads the actual code before proposing any fix

---

*Read alongside `OWNER_BRIEF.md` at every session start.*
*Update this file at every session end.*
