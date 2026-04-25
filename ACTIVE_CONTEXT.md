# ACTIVE CONTEXT
*Updated: 2026-04-25 — Audit-2 session end (Q4-A + Q5-A + Q5-B + Q7-A shipped)*

---

## Current Phase
**Phase 1 — Signal Quality Validation**
Engine is live; this session shipped one telemetry-loss class fix, one
TP-collapse fix, and one regime-widening change. No paying subscribers yet.

Current focus: monitor the next zip to validate (a) the SR_FLIP TP1==TP2
collapse fix moved its SL rate off 100%, and (b) TPE/DIV_CONT now produce
signals in `WEAK_TREND` regime.

---

## Current Priority (Do This First)

**Run the VPS monitor** after 6–12 hours of the new commits running.
Share the zip in the Project chat.

What to look for in the next zip:

1. **SR_FLIP_RETEST** in `quality_by_setup`: SL rate moves off 100% (target ≤ 60% over 20+ signals).
2. **TREND_PULLBACK_EMA / DIVERGENCE_CONTINUATION** in `quality_by_setup`: at least one signal each tagged with `market_phase` containing `WEAK_TREND` (was zero-possible before this session). If their `WEAK_TREND` SL rate > 60% in the first 24h window, revert the WEAK_TREND elif branch in both evaluators.
3. **Reject-reason histogram** in `path_funnel_truth`: `build_signal_failed` counts now appear under LIQUIDITY_SWEEP_REVERSAL and WHALE_MOMENTUM (previously hidden — telemetry was being dropped).
4. **30–60s breach cluster** still trending below 20% (the candle OHLC fix held).
5. **FAILED_AUCTION_RECLAIM** still the strongest path.

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

---

## Known Live Issues (post Audit-2)

1. **30–60s breach cluster** — was 88.9% pre candle-OHLC fix. Awaiting fresh data to confirm post-fix.
2. **SR_FLIP_RETEST 100% SL rate** — TP1==TP2 collapse fixed (Q4-A). Still need data to confirm SL rate moved off 100%; geometry-tightness root cause (Priority 2 in roadmap) still open.
3. **10 of 14 paths silent** — Q7-A unblocks 2 (TPE, DIV_CONT) in `WEAK_TREND` regime. Need 6+ active paths for Phase 1 exit.
4. **Signal volume ~0.45/hour** — low but consistent with current market conditions.
5. **Per-path SL stats** — already in monitor zip (`quality_by_setup` and `post_correction_focus.sl_rate`); no API method on `PerformanceTracker` yet but operationally unblocked.

---

## Next PR Queue (post Audit-2)

| Priority | Task | Scope |
|---|---|---|
| 1 | Read next monitor zip — validate Q4-A, Q7-A | Observation; data-driven decisions |
| 2 | **Q4-B — Generalize TP monotonicity guard** across LSR, TPE, LIQ_REV, FUNDING_EXT, CLS | Same FAR/Q4-A pattern; ~25 LOC + 10 tests |
| 3 | SR_FLIP geometry root-cause (if still > 60% SL post-Q4-A) | Investigate before any further fix |
| 4 | Decide on STRONG_TREND/BREAKOUT_EXPANSION widening for TPE/DIV_CONT | Needs WEAK_TREND data first |
| 5 | **Q2 — Implement orderblock detection** | Out of Phase 1 budget; Phase 2 spec |

---

## Open Risks

- SR_FLIP geometry: TP1==TP2 fix is partial. If structural SL is still too tight, the path's SL rate stays elevated even with monotonic TPs.
- WEAK_TREND widening for TPE/DIV_CONT is unmeasured — pullbacks/hidden-divergences may behave differently in WEAK_TREND than in TRENDING_*. Monitor must catch a high SL rate fast or revert.
- 10-silent-paths is structural — Q7-A only addresses 2. Remaining 8 silent paths need separate diagnosis (FVG-only gates per Q2, MTF gate suppressors per scanner config, ORB env-disabled by design).
- Low signal volume = slow feedback loop. Each shipped change takes 24–48h to validate.

---

## Audit-2 Findings That Did NOT Ship This Session

- **Q1 (per-path SL stats API method)** — skipped: data already in truth-report via `build_quality_by_setup` (`src/runtime_truth_report.py:196`); no operational gap.
- **Q4-B (generalize TP monotonicity guard)** — queued for next session; same FAR pattern across 5 more evaluators.
- **Q2 (orderblock detection)** — deferred to Phase 2; out of Phase 1 budget.
- **Q6 (FAR scalar struct extrema)** — observation only; FAR's wick-anchored SL + tail/reclaim filters carry the structural load. Not a bug.
- **Q7-B (ORB env-disabled)** — intentional per PR-06; not a bug.

---

## How to Raise Issues in Project Chat

- Share monitor zip → CTE analyzes and responds with findings + action
- Share Telegram screenshots → CTE reads timing, prices, compares to chart
- Describe what you observed → CTE reads the actual code before proposing any fix

---

*Read alongside `OWNER_BRIEF.md` at every session start.*
*Update this file at every session end.*
