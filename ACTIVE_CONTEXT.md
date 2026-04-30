# ACTIVE CONTEXT
*Updated: 2026-04-30 — HYPEUSDT QCB -21.6 gate penalty diagnosed + recalibrated*

---

## Current Phase
**Phase 1 — Signal Quality Validation**
Engine is live, healthy, scanning. Market is QUIET ~99.7% of the latest 28h
window — signal drought is expected and is the dominant constraint, not a bug.

This session (2026-04-30):
- **Reviewed monitor zip 2026-04-30 04:08 UTC** — flagged stale (last performance
  record 3.4h old). Window-over-window deltas all zero vs prior window — same
  QUIET regime, same path silence. Only 3 QCB closes in window, all flat
  (~ -0.046% PnL each). No new bug surface or anomaly to act on.
- **Diagnosed HYPEUSDT QCB 89.2 → 67.6 gate penalty** (Priority 3 / queue #7).
  In `360_SCALP` channel, only two soft-gate bases (`volume_div=12.0` and
  `spoof=12.0`) yield exactly `12.0 × 1.8 (QUIET regime mult) = 21.6`. Of the
  two, **`volume_div` has a structural mismatch with QCB's thesis**: QCB by
  design fires on a primary-TF compression breakout volume spike during a
  QUIET window where higher-TF (15m) volume is declining — that pattern is
  exactly what `check_volume_divergence_gate` flags as manipulation
  (`_REGIME_SPIKE_THRESHOLD["QUIET"]=1.5`, `_REGIME_DECLINE_THRESHOLD["QUIET"]=0.8`).
  Spoof, by contrast, is an orderbook-anomaly signal that's informative
  regardless of setup type — leave it alone.
- **Shipped: PR-7B path-aware modulation entry for QCB on volume_div** at scale 0.60
  (matches existing VSB/FAR/SR_FLIP precedents). Effect: pre-fix
  `12.0 × 1.8 = 21.6` → post-fix `12.0 × 0.60 × 1.8 = 12.96`. Penalty preserved
  (volume_div divergence still meaningfully reflected) but no longer
  single-handedly drops an A+ tier signal to FILTERED. Edit at
  `src/scanner/__init__.py:449` plus mirroring assertion in
  `tests/test_regime_soft_penalty.py::TestPathAwarePenaltyModulation`.
  TestPathAwarePenaltyModulation passes; no new test failures introduced.
  Two pre-existing failures (`TestHardGatesStillBlock::test_cross_asset_gate_still_hard_blocks`,
  `TestRegimeMultiplierStoredOnSignal::test_regime_multiplier_stored_quiet`)
  exist on main and are unaffected — covered by tech-debt queue #13.

Prior session 2026-04-29:
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
| **REST-fallback admin-alert grace period (60s) — transient drops stay silent; only sustained outages alert. Cooldown layered on top for prolonged outages.** | `src/websocket_manager.py:303` (`_start_rest_fallback` + `_maybe_alert_after_grace`) | Prior 2026-04-29 |
| **PR-7B path-aware modulation: QCB volume_div = 0.60 — closes structural mismatch where QUIET volume_div thresholds flag QCB's own breakout pattern as manipulation; -21.6 → -13.0** | `src/scanner/__init__.py:449` (`_PENALTY_MODULATION_BY_SETUP`) + test mirror in `tests/test_regime_soft_penalty.py` | **This session (2026-04-30)** |

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
2. ~~HYPEUSDT QCB gate penalty — 89.2 → 67.6 due to single -21.6 soft-gate penalty.~~
   **RESOLVED 2026-04-30**: source was `volume_div` (12.0 × 1.8 QUIET mult = 21.6).
   Structural mismatch with QCB thesis. Modulation entry shipped; penalty now ~13.0.
   Spoof gate (also 12.0 × 1.8) intentionally left unmodulated — orderbook
   anomalies are informative regardless of setup type.
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
8. **Futures WS connection drops every ~15 min (alert spam now silenced).**
   Owner reported repeating `⚠️ REST fallback activated for futures critical pairs.`
   alerts every ~15 min for 3 days. Root cause: staleness watchdog at
   `src/websocket_manager.py:484` force-closes the futures WS when `last_pong`
   isn't updated for `WS_HEARTBEAT_INTERVAL_FUTURES (60) × WS_STALENESS_MULTIPLIER_FUTURES (15) = 900s`.
   Reconnect succeeds on first attempt (under 2s); the per-drop "WebSocket
   connection lost" alert is gated by `reconnect_attempts ≥ 2` so it stays
   silent — but the REST-fallback alert had no cooldown, firing every time.
   Most likely underlying cause: aiohttp consumes Binance's server-side PING
   frames internally with `heartbeat=60` set, and the kline TEXT stream
   silently stops every ~15 min on Binance's combined `/ws/<s1>/<s2>/...`
   endpoint without a TCP RST. Watchdog correctly catches it.
   **System impact: zero** — engine healthy, signals flowing, reconnect
   clean. **Two-stage fix this session**: PR #242 added a 600s cooldown,
   but with drops every 900s the alert still fired every cycle (cooldown
   < drop interval). Superseded by a **60s grace period**: the alert is
   delayed by 60s and only fires if REST fallback is still active when
   the timer expires. Transient drops (reconnect under 2s) stay silent;
   sustained outages still surface, with a cooldown still layered on top
   to coalesce repeat alerts during prolonged degradation.

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
| 5 | REST-fallback admin-alert cooldown (PR #242) — *insufficient: 600s cooldown < 900s drop interval, alerts still fired every cycle* | ⚠️ Superseded |
| 5b | REST-fallback admin-alert 60s grace period (this session) — transient drops stay silent | ✅ This session |
| 6 | Validate mover signals firing on next zip — search for VSB/BREAKDOWN_SHORT emissions on non-top-75 symbols | Observation |
| 7 | HYPEUSDT QCB -21.6 gate penalty source — diagnosed (volume_div) + modulation shipped | ✅ This session |
| 8 | Validate channel cap raise on next monitor zip | Observation |
| 9 | Monitor zip — validate Audit-3 path activation under non-QUIET regime | Observation (regime-gated) |
| 10 | Win-rate check — needs ≥20 closed signals in non-QUIET regime | Data validation |
| 11 | ORB / CLS / PDC silence — diagnosed, see "Silent-path diagnosis" below; ORB requires rebuild, CLS/PDC structural in QUIET; mover-allowlist expansion is a separate architectural question | ✅ Diagnosed |
| 12 | DISTRIBUTION gate calibration (conditional on next zip) | Conditional |
| 13 | Pre-existing test breakage: 139 failures on main (PR #240 channel cap raise + others didn't update fixtures) — clean up in dedicated PR | Tech debt |
| 14 | Diagnose underlying 15-min futures WS drop (needs VPS-side `_health_watchdog` "stale WS connection" log) | Investigation |

---

## Silent-path diagnosis (queue #11) — 2026-04-30

ORB / CLS / PDC have never fired live. Diagnosis traces each to a different
root cause; none are bugs.

**ORB (OPENING_RANGE_BREAKOUT)** — build-time disabled. `SCALP_ORB_ENABLED`
defaults to `false` (`config/__init__.py:848`). PR-06 deliberately disabled
the path until rebuilt with true session-opening-range logic; the current
8-bar proxy is not institutional-grade. Reject reason `regime_blocked` at
`scalp.py:2132` is a misleading label (root cause is the build flag, not
regime). Action: leave disabled until rebuild — Phase 2.

**CLS (CONTINUATION_LIQUIDITY_SWEEP)** — regime allowlist
`{TRENDING_UP, TRENDING_DOWN, STRONG_TREND, WEAK_TREND, BREAKOUT_EXPANSION}`
hard-blocks QUIET / RANGING / VOLATILE at `scalp.py:3309`. Market is ~99.7%
QUIET → silence is structural and expected. Action: none. Will activate
naturally when regime shifts.

**PDC (POST_DISPLACEMENT_CONTINUATION)** — same regime allowlist as CLS at
`scalp.py:3583`. Same expected silence in QUIET. Action: none.

### Auxiliary scan paths (the user's hint)

Two scan paths exist beyond the top-75 main universe:

1. **Surge-promoted** (`_promoted_pairs`, 3 cycles) — pairs whose volume
   exceeds `SURGE_PROMOTION_VOLUME_MULTIPLIER` × baseline. Runs all 14
   evaluators (no setup whitelist). Pair-level regime is computed
   independently — in current QUIET market most surge-promoted pairs likely
   still classify QUIET, so CLS/PDC remain regime-blocked there too.

2. **Mover-promoted** (`_mover_promoted_pairs`, 5 cycles) — pairs with ≥15%
   24h % change. **Hard whitelist: VSB + BREAKDOWN_SHORT only**
   (`scanner/__init__.py:4635`). Mover pairs by definition have strong
   directional moves and almost certainly classify TRENDING — which IS in
   the CLS/PDC regime allowlist. So the only thing keeping CLS/PDC silent
   on mover-promoted pairs is the evaluator whitelist itself.

**Owner discussion item (B10)**: should we expand the mover-evaluator
whitelist to include CLS and PDC? The case for:

- Mover pairs are the highest-momentum scan target; CLS (sweep continuation)
  and PDC (displacement re-acceleration) are exactly the setups designed
  for that environment.
- REST seed (PR #241) gives 500 candles per TF — sufficient for CLS's
  10-candle sweep window and PDC's 2-5-candle consolidation.
- Both paths use closed 5m candles, not live ticks → no WS dependency
  (movers deliberately skip WS subscription per `_seed_mover_pair`).

The case against:

- Mover-promoted pairs are highly volatile by definition; CLS/PDC may run
  hotter SL rates here than on stable top-75 pairs.
- 75-second TTL is short for setups that need post-sweep / post-displacement
  re-acceleration confirmation — a stale-by-the-time-it-emerges signal is
  worse than no signal.
- VSB+BREAKDOWN-only was a deliberate scope decision in PR #233 — likely to
  contain the blast radius until movers proved themselves.

Recommend: defer until mover signals show real win rate on VSB+BREAKDOWN
first (next-PR-queue #6 — observation item). If movers prove out, then
expand cautiously, one path at a time, with explicit owner sign-off.

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
