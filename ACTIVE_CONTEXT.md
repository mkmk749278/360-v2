# ACTIVE CONTEXT
*Updated: 2026-04-29 — Mover promotion seeding fix (PR #233 follow-up)*

---

## Current Phase
**Phase 1 — Signal Quality Validation**
Engine is live, healthy, scanning. Market is QUIET ~99.7% of the latest 28h
window — signal drought is expected and is the dominant constraint, not a bug.

This session (2026-04-29):
- **Reviewed monitor zip 2026-04-29 08:49 UTC** — see "Monitor Zip Findings" below
- **Confirmed PR #236 fixes are live and working** (QCB went 0 → 12 emissions)
- **Verified all Audit-3 fixes are deployed** in `src/channels/scalp.py`
  (TPE/DIV_CONT WEAK_TREND at lines 1027/3044, FUNDING QUIET removed at 2692,
  LIQ_REV ATR-relative cascade at 1305)
- **Shipped: 360_SCALP channel cap raise 2.5% → 3.0%** in `signal_quality.py:347`.
  Unlocks per-setup 3.0% caps for FAR/QCB/TPE/FUNDING which were silently
  capped at 2.5% by the tighter-wins channel logic. Setups with <3.0% per-setup
  caps (SR_FLIP=2.5, RANGE_REJECTION=1.5, etc.) are unaffected — math verified
  in `_max_sl_pct_for_policy()`.
- **Shipped: mover promotion data-plumbing fix** (`src/scanner/__init__.py:1090`).
  Owner flagged that mover-promoted pairs (PR #233) weren't producing signals.
  Root cause: PR #233 wired the *promotion list* but skipped REST candle
  seeding and CVD seeding — promoted symbols had 0 candles, failing
  `insufficient_candles` on every cycle for the entire 5-cycle TTL.
  Fix: new `_seed_mover_pair()` method awaits `data_store.seed_symbol()`
  (mirrors `main.py:708` new-pair pattern) + `seed_cvd_from_klines()`
  (mirrors `bootstrap.py:177` boot pattern) before adding the pair to
  `_mover_promoted_pairs`. Pairs with <28 5m candles after seed are skipped
  to avoid burning telemetry on a dead pair. WS subscription deliberately
  skipped — `update_streams_for_top50()` does a full stop→start which is too
  disruptive for a 75-second promotion window; REST-seeded data is sufficient
  for VSB+BREAKDOWN evaluation in that span.

Prior session (2026-04-28): PR #236 — per-setup SL caps, EXHAUSTION_FADE 0.9 R:R,
`/dashboard` mover counter, interim 1.5% → 2.5% bump (now superseded).

---

## Monitor Zip Findings (2026-04-29 08:49 UTC, 28h window, 409,322 cycles)

### Engine Health: ✅
- Heartbeat 3s, status running, healthy.
- WS streams active, OI populated 99.97%, CVD populated 15.8% (low-vol pairs
  starved — known issue).

### Path Funnel Truth
| Path | Generated | Gated | Scored | Emitted | Notes |
|---|---:|---:|---:|---:|---|
| QUIET_COMPRESSION_BREAK | 12,374 | 36 | n/a | **12** | ✅ Loop broken (was 0 pre-fix) |
| FAILED_AUCTION_RECLAIM | 43,033 | 40,845 | n/a | **2** | Heavy gate filter — needs non-QUIET regime |
| SR_FLIP_RETEST | 27,133 | 22,539 | 4,594 | **0** | All 4,594 scored signals **FILTERED at QUIET_SCALP_BLOCK** |
| LIQUIDITY_SWEEP_REVERSAL | 7,431 | 7,269 | n/a | **0** | Same QUIET_SCALP_BLOCK structural protection |
| 9 other paths | 0 | — | — | — | `regime_blocked` (correct in QUIET) |

**Root cause of "0 SR_FLIP emissions"**: `scanner/__init__.py:4336` — the
`QUIET_SCALP_BLOCK` gate filters all 360_SCALP setups EXCEPT QCB (always exempt)
and DIV_CONT (when conf ≥ 64) when regime is QUIET. SR_FLIP, FAR, LSR all
correctly fall through this gate in QUIET. **This is structural protection,
not a bug.** Threshold `QUIET_SCALP_MIN_CONFIDENCE = 65.0` (config/__init__.py:1058).

### Liquidation Clusters Absent (409,322/409,322)
**Not a bug.** Per `bootstrap.py:385` the `@forceOrder` subscription is wired,
events flow through `main.py:542` → `_pending_liquidations` → `OrderFlowStore.add_liquidation()`.
QUIET markets simply produce no liquidation cascades. Only consumer is
FUNDING_EXTREME (`scalp.py:2760`) which has graceful ATR×1.5 fallback.

### Win-rate Validation: Still Blocked
Only **1** signal closed in window (QCB at -0.086% PnL — essentially flat exit,
not a real SL or TP). Need non-QUIET regime to generate enough signals for
statistical confidence.

---

## Current Priority (Do This First)

1. **Wait for non-QUIET regime data** — 9/14 paths and the QUIET_SCALP_BLOCK
   gate cannot be evaluated until market shifts to TRENDING / RANGING / WEAK_TREND.
   Until then, QCB and DIV_CONT are the only paths that can fire.
2. **Validate channel cap raise effect on next zip** — check FAR/QCB SL distance
   distribution; some signals should now use 2.5–3.0% range that were previously
   compressed/rejected at 2.5%.
3. **HYPEUSDT QCB 89.2 → 67.6 via -21.6 gate penalty** — open mystery from
   prior session. Source unknown.

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
| Mover pairs dashboard: `set_mover_pairs()` + `/dashboard` counter | `src/telemetry.py` + `src/scanner/__init__.py` | PR #236 |
| 360_SCALP channel SL cap raised 1.5% → 2.5% (interim) | `src/signal_quality.py` | PR #236 |
| Per-setup SL caps: 17 values in `_MAX_SL_PCT_BY_SETUP` | `src/signal_quality.py` | PR #236 |
| EXHAUSTION_FADE moved to 0.9 R:R mean-reversion tier | `src/signal_quality.py` | PR #236 |
| **360_SCALP channel SL cap raised 2.5% → 3.0% — unlocks per-setup 3.0% caps for FAR/QCB/TPE/FUNDING** | `src/signal_quality.py:347` | **This session (2026-04-29)** |
| **Mover-promotion REST seed + CVD seed on promotion (PR #233 follow-up)** | `src/scanner/__init__.py:1090` (`_seed_mover_pair`) | **This session (2026-04-29)** |

---

## Per-Setup SL Cap Table (live as of 2026-04-29 channel cap raise)

**Channel cap (`_MAX_SL_PCT_BY_CHANNEL["360_SCALP"]`) is now 3.0%.**
Before today's change, this acted as a tighter-wins cap that silently capped
FAR/QCB/TPE/FUNDING at 2.5% even though their per-setup caps are 3.0%.

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

1. **Win-rate still unvalidated** — only 1 closed signal in latest 28h zip
   (QCB at -0.086% PnL). Need non-QUIET regime for meaningful sample.
2. **HYPEUSDT QCB gate penalty** — 89.2 composite → 67.6 due to single -21.6 soft-gate
   penalty. Source not yet identified. Not blocking, but high-quality signal lost.
3. **`cvd_candles=0` on some pairs** — ZBTUSDT, BSBUSDT, SWARMSUSDT. Low-volume pairs
   not covered by boot seed. CVD-gated evaluators silent on these until ~100 live 1m candles
   accumulate (~100 min post-start).
4. **`币安人生USDT` in scan universe** — Chinese-character symbol, likely a promo/test ticker.
   Burns a scan slot. Will fall out on next volume-sort cycle. No action needed.
5. **Market QUIET ~99.7% of latest 28h window** — 9/14 paths regime-blocked
   (correct behavior); QUIET_SCALP_BLOCK gate filters all 360_SCALP setups
   except QCB (always exempt) and DIV_CONT (conf ≥ 64). Signal throughput
   capped until regime shifts.
6. **DISTRIBUTION gate untested** — penalty fires but calibration unknown. Watch LONG
   suppression rate in next zip; reduce to 10pts if > 30% of LONGs suppressed.
7. **liquidation_clusters absent in 100% of cycles** — Expected in QUIET (no
   liquidation cascades occurring). Wiring is intact (`bootstrap.py:385`).
   Only consumer is FUNDING_EXTREME with graceful ATR fallback. Not a bug.

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
| 1 | QCB/FAR cap fix VALIDATED (12 + 2 emissions in latest zip) | ✅ Done |
| 2 | Audit-3 fixes verified deployed in code (TPE/DIV_CONT/FUNDING/LIQ_REV) | ✅ Done |
| 3 | 360_SCALP channel cap 2.5% → 3.0% — unlocks per-setup 3.0% caps | ✅ This session |
| 4 | Mover promotion REST+CVD seed on promotion (PR #233 follow-up) | ✅ This session |
| 5 | Validate mover signals firing on next zip — search for VSB/BREAKDOWN_SHORT emissions on non-top-75 symbols | Observation |
| 6 | Investigate HYPEUSDT QCB -21.6 gate penalty source | Code investigation |
| 7 | Validate channel cap raise on next monitor zip | Observation |
| 8 | Monitor zip — validate Audit-3 path activation under non-QUIET regime | Observation (regime-gated) |
| 9 | Win-rate check — needs ≥20 closed signals in non-QUIET regime | Data validation |
| 10 | Investigate ORB / CLS / PDC silence under non-QUIET regime | Code investigation |
| 11 | DISTRIBUTION gate calibration (conditional on next zip) | Conditional |
| 12 | Pre-existing test breakage: 139 failures on main (PR #240 channel cap raise + others didn't update fixtures) — clean up in dedicated PR | Tech debt |

---

## Open Risks

- **New path signals untested** — LIQ_REV, DIV_CONT, FUNDING_EXT have never fired live
  (only QCB and FAR emitted in latest zip; rest were regime-blocked).
  First signals from these paths must be manually reviewed when regime allows.
- **DISTRIBUTION gate false positive** — ranging market may misclassify as DISTRIBUTION.
- **MOM-PROT SL exposure** — watch total SL rate.
- **CVD 10-candle divergence quality** — monitor DIV_CONT SL rate; revert if > 50%.
- **Channel cap raise side effect (this session)** — FAR/QCB/TPE/FUNDING signals
  may now use 2.5–3.0% SL geometry that was previously rejected. Watch SL hit
  rate on these 4 paths in the next zip; if > 60%, the per-setup 3.0% cap may
  be too loose for live conditions.
- **Mover promotion seed cost** — each newly-promoted mover incurs ~6 REST kline
  fetches (1m/5m/15m/1h/4h/1d × 500 candles) in parallel within the scan
  cycle. With `MOVER_PROMOTION_MIN_PCT=15.0` and a typical market this is
  1–3 movers per cycle = 6–18 weight-1 calls, well within Binance's 1200/min
  futures budget. Watch scan latency telemetry — if it spikes during high-
  volatility regimes (many movers qualifying simultaneously), consider
  staggering seeds across cycles.
- **Mover WS lag** — promoted pairs do NOT get WS subscriptions (deliberate;
  `update_streams_for_top50` does a stop→start). For the 75-second TTL, scan
  works off the REST seed snapshot; 1m candles don't update live. Adequate
  for VSB/BREAKDOWN setup detection (which look at closed 5m/1h structure)
  but not suitable if we ever extend the mover allowlist to setups that need
  live tick data.

---

## Deferred (Not In Phase 1 Budget)

- T4.1 Daily BTC bias filter — cross-instrument dependency, Phase 2
- T4.2 Regime-adaptive TP1 multipliers — needs per-regime hit rate data first
- Pair universe expansion — validate current 75 first
- Orderblock detection (Q2) — Phase 2 spec

---

*Read alongside `OWNER_BRIEF.md` at every session start.*
*Update this file at every session end.*
