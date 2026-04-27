# ACTIVE CONTEXT
*Updated: 2026-04-27 — Full market-reality audit batch deployed*

---

## Current Phase
**Phase 1 — Signal Quality Validation**
Engine is live. MOM-PROT profit-protection gate shipped last session.
This session completed a full market-reality audit and shipped 8 targeted fixes
across 3 files to unlock 6 previously silent paths.

---

## Current Priority (Do This First)

**Run the VPS monitor** after 6–12 hours of this batch running.

What to look for in the next zip:

1. **New paths firing** — LIQUIDATION_REVERSAL and DIVERGENCE_CONTINUATION should
   produce first signals (ATR threshold + 10-candle CVD window now accessible).
2. **FUNDING_EXTREME_SIGNAL** — should now fire in QUIET regime (block removed).
   Watch that funding_rate extreme condition is real, not noise.
3. **LSR signal volume up** — momentum_reject=106,547 was dominating; QUIET/RANGING
   now requires only 1-candle persistence. Should see more LSR signals.
4. **TP1_HIT rate** — SR_FLIP and TREND_PULLBACK_EMA TP1 caps (1.8–2.5× SL in
   low-ATR) make TP1 reachable. Expect more TP1_HIT vs CLOSED/EXPIRED.
5. **DISTRIBUTION+LONG penalty** appearing in soft_gate_flags — confirms gate firing.
6. **SL rate** — SL cap raised to 1.20%: signals in high-ATR pairs should now
   have structurally valid SLs instead of getting clipped at 0.80%.

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
| **MOM-PROT: momentum invalidation profit-protection gate** | `src/trade_monitor.py:617` | **MOM-PROT** |
| **T1.1: SR_FLIP + TREND_PULLBACK_EMA TP1 ATR-adaptive cap (1.8–2.5× SL)** | `src/channels/scalp.py` | **Audit-3 (this session)** |
| **T1.2: FUNDING_EXTREME remove QUIET regime block** | `src/channels/scalp.py:2679` | **Audit-3 (this session)** |
| **T1.3: SL cap raised 0.80% → 1.20% across all 8 scalp channel configs** | `config/__init__.py` | **Audit-3 (this session)** |
| **T2.1: LIQUIDATION_REVERSAL ATR-relative cascade threshold (floor 1.5%, cap 3.5%)** | `src/channels/scalp.py:~1294` | **Audit-3 (this session)** |
| **T2.2: DIVERGENCE_CONTINUATION dual 10+20 candle CVD window** | `src/channels/scalp.py:~3062` | **Audit-3 (this session)** |
| **T2.3: LSR momentum persistence 1-candle in QUIET/RANGING (was 2)** | `src/channels/scalp.py:~795` | **Audit-3 (this session)** |
| **T3.1: DISTRIBUTION soft gate −15pts on LONG signals** | `src/scanner/__init__.py:~4105` | **Audit-3 (this session)** |
| **T3.2: Meme coin low-volume penalty 0.85× (<$150M 24h)** | `src/scanner/__init__.py:~4124` | **Audit-3 (this session)** |

---

## Known Live Issues (post Audit-3)

1. **Win-rate metric still unvalidated** — awaiting first post-Audit-3 monitor zip.
2. **DISTRIBUTION gate untested** — penalty fires but may be too aggressive (−15pts)
   if volume_profile=="DISTRIBUTION" triggers frequently. Watch for LONG signal
   suppression rate in next zip.
3. **FUNDING_EXTREME quality gate** — removing QUIET block exposes the path to
   markets with no real funding extremes. Watch for false positives — funding_rate
   threshold is the real gate, but if extreme funding events are rare, path still silent.
4. **CVD 10-candle window** — shorter divergence may produce lower-quality signals.
   Monitor DIV_CONT SL rate carefully in first 24h.
5. **10 of 14 paths still silent at funnel level (pre-fix)** — Audit-3 targets
   LIQ_REV, DIV_CONT, FUNDING_EXT, LSR. Expect 4 more paths to activate.
   Remaining 4 (ORB, QCB, CLS, PDC) need separate diagnosis.

---

## Phase 1 Scorecard (current)

| Metric | Required | Status |
|---|---|---|
| Win rate (TP1 or better) | ≥ 40% | ~9% pre-Audit-3 — TP1 cap + MOM-PROT expected to improve |
| SL hit rate | ≤ 60% | **11.1%** ✅ |
| Signals per day | ≥ 5 | **~13.6/day** ✅ |
| Active paths | ≥ 6 | **6 of 14** ✅ (target: remain ≥ 6 post-Audit-3) |
| Fast failures | 0 | **0%** ✅ |
| Max consecutive SL losses | ≤ 5 | Non-consecutive ✅ |

Blocker: win rate. Audit-3 addresses the two main structural causes
(TP1 unreachable, profitable signals dying at consolidation).

---

## Next PR Queue (post Audit-3)

| Priority | Task | Scope |
|---|---|---|
| 1 | Run monitor in 6–12h — validate Audit-3 path activation (LIQ_REV, DIV_CONT, FUNDING_EXT, LSR volume) | Observation; data-driven |
| 2 | Win-rate check — TP1_HIT/PROFIT_LOCKED should increase as TP1 caps take effect | Data validation |
| 3 | SR_FLIP SL rate post-1.20%-cap — wider SL should reduce premature SL hits | Data validation |
| 4 | Investigate ORB / QCB / CLS / PDC silence — 4 paths still untouched | Code investigation |
| 5 | DISTRIBUTION gate calibration — if LONG suppression rate > 30%, reduce penalty to 10pts | Conditional on next zip |
| 6 | **Q2 — Implement orderblock detection** | Out of Phase 1 budget; Phase 2 spec |

---

## Open Risks

- **New path signals untested** — LIQ_REV, DIV_CONT, FUNDING_EXT have never fired live.
  First signals from these paths must be manually reviewed (price, SL geometry, direction quality).
- **DISTRIBUTION gate false positive** — if volume_profile=="DISTRIBUTION" is misclassified
  in ranging markets, legitimate LONG setups get penalized.
- **CVD 10-candle divergence quality** — shorter window means weaker divergence signal.
  Monitor DIV_CONT SL rate; revert 10-candle window if SL rate > 50% in first 20 signals.
- **MOM-PROT SL exposure** — signals holding through consolidation means more SL exposure.
  Watch total SL rate carefully.
- **FUNDING_EXTREME noise** — path was blocked for reason; removing the block is validated
  only by the funding_rate threshold. If threshold is too loose, false signals will appear.

---

## Audit-3 Findings That Did NOT Ship

- **T4.1 Daily BTC bias filter** — directional bias from 4h/1d BTC trend. Deferred:
  requires reading BTC data in per-pair evaluators, cross-instrument dependency.
  Phase 2 architectural change.
- **T4.2 Regime-adaptive TP1 multipliers** — per-regime dynamic R-multiple scaling.
  Framework exists but needs measurement of per-regime TP hit rates first.
  Deferred until Phase 1 exits or data is available.
- **Pair universe expansion** (BNB, AVAX, NEAR, APT, SUI) — deferred; current 75
  pairs need quality validation before expanding.

---

## How to Raise Issues in Project Chat

- Share monitor zip → CTE analyzes and responds with findings + action
- Share Telegram screenshots → CTE reads timing, prices, compares to chart
- Describe what you observed → CTE reads the actual code before proposing any fix

---

*Read alongside `OWNER_BRIEF.md` at every session start.*
*Update this file at every session end.*
