# ACTIVE CONTEXT
*Updated: 2026-04-28 — Per-setup SL caps + mover pairs dashboard*

---

## Current Phase
**Phase 1 — Signal Quality Validation**
Engine is live and scanning. Market-wide QUIET regime as of 07:47 UTC today
— signal drought is expected, not a system failure.

This session shipped:
- 17 per-setup SL caps replacing the single channel-wide 2.5% cap
- EXHAUSTION_FADE moved to 0.9 R:R mean-reversion tier
- `/dashboard` now shows `Pairs monitored: 75 (+N mover)` when mover-promoted pairs are active
- Interim 360_SCALP cap raise 1.5% → 2.5% (now superseded by per-setup caps)

PR #236 open on `claude/read-owner-brief-ASkk2`.

---

## Current Priority (Do This First)

**Observe next monitor zip** — specifically:

1. **QCB / FAR no longer perpetually rejected** — the SL cap for QUIET_COMPRESSION_BREAK
   and FAILED_AUCTION_RECLAIM is now 3.0% (was 2.5% channel-wide). The perpetual
   `sl_cap_exceeded` rejection loops seen in live logs should be gone.
2. **Win-rate metric** — TP1_HIT / PROFIT_LOCKED rate post-Audit-3 still unvalidated.
3. **New paths firing** — LIQ_REV, DIV_CONT, FUNDING_EXT targeted by Audit-3 fixes.
4. **HYPEUSDT QCB 89.2 composite → 67.6 via -21.6 gate penalty** — single gate is
   nuking a quality signal. Source unknown; investigate in next session if owner
   wants to chase it (ask: which soft gate applied 21.6 penalty?).

---

## All Confirmed Bug Fixes (Deployed or in open PR)

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
| stop_loss field on SignalRecord | `src/performance_tracker.py` + `src/trade_monitor.py` | prior |
| LSR `build_signal_failed` telemetry | `src/channels/scalp.py:913` | Audit-2 |
| WHALE `build_signal_failed` telemetry | `src/channels/scalp.py:~1531` | Audit-2 |
| SR_FLIP TP1==TP2 collapse in 4h-data branch | `src/channels/scalp.py:~2475` | Audit-2 |
| TPE/DIV_CONT accept WEAK_TREND | `src/channels/scalp.py:~961/2920` | Audit-2 |
| TP-ladder monotonicity helper (5 sites) | `src/channels/scalp.py:259` | Audit-2 |
| deploy.yml: skip VPS deploy on doc-only commits | `.github/workflows/deploy.yml` | Audit-2 |
| `_check_invalidation` regime-flip & EMA-crossover creation-relative | `src/trade_monitor.py:555–615` | INV-1 |
| MOM-PROT: momentum invalidation profit-protection gate | `src/trade_monitor.py:617` | MOM-PROT |
| SR_FLIP + TPE TP1 ATR-adaptive cap (1.8–2.5× SL) | `src/channels/scalp.py` | Audit-3 |
| FUNDING_EXTREME remove QUIET regime block | `src/channels/scalp.py:2679` | Audit-3 |
| SL cap raised 0.80% → 1.20% across all 8 channel configs | `config/__init__.py` | Audit-3 |
| LIQ_REV ATR-relative cascade threshold (floor 1.5%, cap 3.5%) | `src/channels/scalp.py:~1294` | Audit-3 |
| DIV_CONT dual 10+20 candle CVD window | `src/channels/scalp.py:~3062` | Audit-3 |
| LSR momentum persistence 1-candle in QUIET/RANGING | `src/channels/scalp.py:~795` | Audit-3 |
| DISTRIBUTION soft gate −15pts on LONG signals | `src/scanner/__init__.py:~4105` | Audit-3 |
| Meme coin low-volume penalty 0.85× (<$150M 24h) | `src/scanner/__init__.py:~4124` | Audit-3 |
| CVD 24h starvation: boot seed from historical 1m candles | `src/historical_data.py` + `src/order_flow.py` | CVD-fix |
| **Mover pairs dashboard: `set_mover_pairs()` + `/dashboard` counter** | `src/telemetry.py` + `src/scanner/__init__.py` | **This session (PR #236)** |
| **360_SCALP channel SL cap raised 1.5% → 2.5% (interim)** | `src/signal_quality.py` | **This session (PR #236)** |
| **Per-setup SL caps: 17 values in `_MAX_SL_PCT_BY_SETUP`** | `src/signal_quality.py` | **This session (PR #236)** |
| **EXHAUSTION_FADE moved to 0.9 R:R mean-reversion tier** | `src/signal_quality.py` | **This session (PR #236)** |

---

## Per-Setup SL Cap Table (live as of PR #236)

| Setup | Cap | Policy |
|---|---|---|
| RANGE_REJECTION | 1.5% | compress |
| RANGE_FADE | 1.5% | compress |
| DIVERGENCE_CONTINUATION | 1.5% | reject |
| EXHAUSTION_FADE | 2.0% | compress |
| WHALE_MOMENTUM | 2.0% | compress |
| OPENING_RANGE_BREAKOUT | 2.0% | compress |
| LIQUIDITY_SWEEP_REVERSAL | 2.0% | compress |
| LIQUIDATION_REVERSAL | 2.0% | reject |
| VOLUME_SURGE_BREAKOUT | 2.0% | reject |
| BREAKDOWN_SHORT | 2.0% | reject |
| CONTINUATION_LIQUIDITY_SWEEP | 2.0% | reject |
| SR_FLIP_RETEST | 2.5% | reject |
| POST_DISPLACEMENT_CONTINUATION | 2.5% | reject |
| FAILED_AUCTION_RECLAIM | 3.0% | reject |
| QUIET_COMPRESSION_BREAK | 3.0% | reject |
| TREND_PULLBACK_EMA | 3.0% | reject |
| FUNDING_EXTREME_SIGNAL | 3.0% | reject |

Tighter of per-setup cap vs channel cap always wins (`_max_sl_pct_for_policy()`).

---

## Known Live Issues

1. **Win-rate still unvalidated** — need post-Audit-3 monitor zip.
2. **HYPEUSDT QCB gate penalty** — 89.2 composite → 67.6 due to single -21.6 soft-gate
   penalty. Source not yet identified. Not blocking, but high-quality signal lost.
3. **`cvd_candles=0` on some pairs** — ZBTUSDT, BSBUSDT, SWARMSUSDT. Low-volume pairs
   not covered by boot seed. CVD-gated evaluators silent on these until ~100 live 1m candles
   accumulate (~100 min post-start).
4. **`币安人生USDT` in scan universe** — Chinese-character symbol, likely a promo/test ticker.
   Burns a scan slot. Will fall out on next volume-sort cycle. No action needed.
5. **Entire market QUIET at 07:47 UTC 2026-04-28** — VSB, BREAKDOWN_SHORT, QCB explicitly
   blocked in QUIET. Low signal throughput is expected until regime shifts.
6. **DISTRIBUTION gate untested** — penalty fires but calibration unknown. Watch LONG
   suppression rate in next zip; reduce to 10pts if > 30% of LONGs suppressed.

---

## Phase 1 Scorecard (last known)

| Metric | Required | Status |
|---|---|---|
| Win rate (TP1 or better) | ≥ 40% | ~9% pre-Audit-3 — unvalidated post-fix |
| SL hit rate | ≤ 60% | **11.1%** ✅ |
| Signals per day | ≥ 5 | **~13.6/day** ✅ |
| Active paths | ≥ 6 | **6 of 14** ✅ |
| Fast failures | 0 | **0%** ✅ |
| Max consecutive SL losses | ≤ 5 | Non-consecutive ✅ |

Blocker: win rate. Per-setup SL caps + TP1 ATR-adaptive caps address structural causes.

---

## Next PR Queue

| Priority | Task | Status |
|---|---|---|
| 1 | Monitor zip — validate QCB/FAR no longer looping on SL cap | Observation |
| 2 | Monitor zip — validate Audit-3 path activation (LIQ_REV, DIV_CONT, FUNDING_EXT) | Observation |
| 3 | Investigate HYPEUSDT QCB -21.6 gate penalty source | Code investigation |
| 4 | Win-rate check — TP1_HIT/PROFIT_LOCKED rate post Audit-3 + SL cap fixes | Data validation |
| 5 | Investigate ORB / CLS / PDC silence (3 paths still untouched) | Code investigation |
| 6 | DISTRIBUTION gate calibration (conditional on next zip) | Conditional |

---

## Open Risks

- **New path signals untested** — LIQ_REV, DIV_CONT, FUNDING_EXT have never fired live.
  First signals from these paths must be manually reviewed.
- **Per-setup cap is tighter-wins** — if channel cap < setup cap, channel wins. Currently
  360_SCALP=2.5% channel cap is tighter than FAR/QCB/TPE/FUNDING 3.0% setup caps.
  Channel cap needs to be raised to 3.0% to unlock these paths' full headroom.
  **Action needed:** raise `360_SCALP` in `_MAX_SL_PCT_BY_CHANNEL` from 2.5 → 3.0.
- **DISTRIBUTION gate false positive** — ranging market may misclassify as DISTRIBUTION.
- **MOM-PROT SL exposure** — watch total SL rate.
- **CVD 10-candle divergence quality** — monitor DIV_CONT SL rate; revert if > 50%.

---

## Deferred (Not In Phase 1 Budget)

- T4.1 Daily BTC bias filter — cross-instrument dependency, Phase 2
- T4.2 Regime-adaptive TP1 multipliers — needs per-regime hit rate data first
- Pair universe expansion — validate current 75 first
- Orderblock detection (Q2) — Phase 2 spec

---

*Read alongside `OWNER_BRIEF.md` at every session start.*
*Update this file at every session end.*
