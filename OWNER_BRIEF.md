# 360 Crypto Eye — Owner Operating Manual

> **This is the single source of truth for everything: system state, technical decisions, PR history, business rules, and how every Copilot session must behave.**
>
> ---
>
> ### How to Start Every New Copilot Session
>
> Paste this exactly:
> ```
> Read OWNER_BRIEF.md in mkmk749278/360-v2 — this is my crypto signal business. First read your Role instructions and what rights you have and Continue from where we left off.
> ```
>
> Copilot reads this file and operates as **technical engineer and system co-owner with full rights** — not a code assistant.

---

## ⚠️ Critical Instructions for Copilot — Read First, Every Session

| Rule | What It Means |
|---|---|
| **You are co-owner and technical engineer** | Full rights on this system. Drive technical decisions proactively. Don't wait to be asked. Don't ask for approval before acting. |
| **Be proactive — act first** | Spot a bug? Fix it. Spot a risk? Raise a PR. Spot an improvement? Implement it. Do not wait for the owner to describe every task. |
| **System and data first** | Current phase: system building and validation. No business strategy, no subscriber focus, no marketing — until the engine produces quality signals consistently. |
| **Discuss first for major changes. Act immediately for bugs and obvious fixes.** | For architectural decisions, discuss and agree. For bugs, TypeErrors, heartbeat issues, signal path fixes — just do it. |
| **Understand before proposing** | Read the relevant code before suggesting anything. Never propose based on assumptions. |
| **One PR = one clear technical outcome** | Every PR must have a clear "what problem does this solve" answer. |
| **Review before merge** | After a PR is created, review it against spec. If it misses, revise — do not close and move on. |
| **Never reverse locked rules** | Business Rules are locked. Do not suggest removing them without explicit owner instruction. |
| **Never invent data** | GPT writes voice and tone. Engine provides numbers. Never fabricate prices, win rates, or signal data. |
| **Work ahead** | Always be thinking about what needs fixing next. Never idle. |
| **Keep this file current** | Update OWNER_BRIEF.md at the end of every session. This file is the memory of the system. |

---

## 1. What This System Is

**360 Crypto Eye** is a 24/7 automated crypto trading signal engine. It scans 75 Binance USDT-M futures pairs continuously, detects institutional-grade setups using Smart Money Concepts + advanced technical analysis, and sends trade signals to Telegram subscribers.

**Revenue model:** Monthly subscription via Telegram paid channel.

**Current phase: System validation. No subscribers yet. Engine must prove itself before launch.**

**Owner:** mkmk749278
**Repo:** https://github.com/mkmk749278/360-v2
**Stack:** Python 3.11+, asyncio, aiohttp, Redis, Docker Compose, Telegram Bot API
**Deployment:** Single VPS, Docker Compose, GitHub Actions CD on push to `main`

---

## 2. System Architecture — Current State

### Active Signal Channel (paid)
| Channel | Status | What It Does |
|---|---|---|
| `360_SCALP` | ✅ Active | 11 signal evaluation paths (see below) |
| `360_SCALP_FVG` | ✅ Active | Fair Value Gap retests |
| `360_SCALP_ORDERBLOCK` | ✅ Active | SMC order block bounces |
| `360_SCALP_DIVERGENCE` | ✅ Active | RSI/MACD divergence reversals |

### Soft-Disabled Channels (radar/free channel only)
| Channel | Status |
|---|---|
| `360_SCALP_CVD` | ❌ Disabled (`CHANNEL_SCALP_CVD_ENABLED=false`) |
| `360_SCALP_VWAP` | ❌ Disabled (`CHANNEL_SCALP_VWAP_ENABLED=false`) |
| `360_SCALP_SUPERTREND` | ❌ Disabled (`CHANNEL_SCALP_SUPERTREND_ENABLED=false`) |
| `360_SCALP_ICHIMOKU` | ❌ Disabled (`CHANNEL_SCALP_ICHIMOKU_ENABLED=false`) |

### Removed Channels (permanently)
| Channel | Reason |
|---|---|
| `360_SPOT` | Not in scope — deferred indefinitely |
| `360_GEM` | Not in scope — deferred indefinitely |
| `360_SWING` | Not in scope — deferred indefinitely |
| `360_SCALP_OBI` | REST order book depth caused scan latency — full removal (PR43) |

### Signal Generation Paths — ScalpChannel (11 active evaluators)
| # | Method | Setup Class | Key Requirements |
|---|---|---|---|
| 1 | `_evaluate_standard` | LIQUIDITY_SWEEP_REVERSAL | SMC sweeps + ADX + EMA alignment |
| 2 | `_evaluate_trend_pullback` | TREND_PULLBACK_CONTINUATION | EMA9/21 pullback in trending regime |
| 3 | `_evaluate_liquidation_reversal` | LIQUIDATION_REVERSAL | Liquidation cluster data from smc_data |
| 4 | `_evaluate_whale_momentum` | WHALE_MOMENTUM | Large tick volume + recent_ticks data |
| 5 | `_evaluate_volume_surge_breakout` | VOLUME_SURGE_BREAKOUT | Volume 3× avg + breakout level retest 0.2–3% |
| 6 | `_evaluate_breakdown_short` | BREAKDOWN_SHORT | Mirror of surge breakout for shorts |
| 7 | `_evaluate_opening_range_breakout` | OPENING_RANGE_BREAKOUT | London (07–09 UTC) / NY (12–14 UTC) only |
| 8 | `_evaluate_sr_flip_retest` | SR_FLIP_RETEST | S/R flip within 8 candles + 0.5% retest zone |
| 9 | `_evaluate_funding_extreme` | FUNDING_EXTREME_SIGNAL | Extreme funding rate (optional — degrades gracefully) |
| 10 | `_evaluate_quiet_compression_break` | QUIET_COMPRESSION_BREAK | BB squeeze — QUIET/RANGING regime only |
| 11 | `_evaluate_divergence_continuation` | DIVERGENCE_CONTINUATION | CVD hidden divergence — TRENDING regime only |

**REMOVED:** `_evaluate_range_fade` (BB mean reversion) — deleted in PR7. No SMC basis, dominated signals artificially.

---

## 3. Business Rules (Non-Negotiable)

| # | Rule |
|---|---|
| B1 | All live signals go to ONE paid channel (`TELEGRAM_ACTIVE_CHANNEL_ID`) |
| B2 | Zero manual effort at runtime — everything self-manages |
| B3 | Content must feel human-written — never robotic |
| B4 | All config values must be env-var overridable |
| B5 | SMC structural basis is non-negotiable — no signal fires without minimum SMC score |
| B6 | System must survive Binance API degradation gracefully |
| B7 | No duplicate signals on same symbol within cooldown window |
| B8 | SL hits posted honestly, same visual weight as TP hits |
| B9 | Radar alerts go to FREE channel ONLY |
| B10 | GPT failure must never cause a missed post or crash — always template fallback |
| B11 | Discuss and agree before major architectural changes |
| B12 | System and data focus only until 4-week validation scorecard passes |
| B13 | Every signal method has its own SL/TP calculation — no universal formulas |
| B14 | Signal expiry notifications sent when signal max hold time reached |

---

## 4. Testing Phase Scorecard (Phase 1 Exit Criteria)

The system must pass ALL of these before Phase 2 (subscribers) begins.

| Metric | Minimum to proceed |
|---|---|
| Win rate (TP1 or better) | ≥ 60% |
| Entry reachability | ≥ 80% of signals gave a fair entry window |
| SL from wrong setup | ≤ 20% of all SL hits |
| Max concurrent open signals | ≤ 4 at any one time |
| Worst week drawdown | ≤ 10% of account |
| Signals with TP2+ reached | ≥ 40% of winning trades |

---

## 5. Signal Quality Gates (13 layers)

Every signal passes all 13 before dispatch:
1. Market regime classification
2. Spread gate
3. Volume gate (regime-aware floor)
4. SMC structural basis — sweep, FVG, or orderblock required
5. Multi-timeframe alignment
6. EMA trend alignment
7. Momentum confirmation
8. MACD confirmation
9. Order flow — OI trend, CVD divergence, liquidation data
10. Cross-asset correlation (BTC/ETH macro gate — direction-aware, graduated by correlation)
11. Kill zone session filter
12. Risk/reward validation — structural SL, minimum R:R enforced
13. Composite confidence scoring — component minimums AND total minimum

**Confidence tiers:**
| Tier | Score | Action |
|---|---|---|
| A+ | 80–100 | Fire to paid channel |
| B | 65–79 | Fire to paid channel |
| WATCHLIST | 50–64 | Post to free channel only |
| FILTERED | < 50 | Reject — never reaches any channel |

---

## 6. PR Log — Full History

### PR1 — Signal Quality Overhaul ✅ MERGED (PR#44, 2026-04-06)
- SMC hard gate (smc_score ≥ 12), trend hard gate (trend_score ≥ 10)
- Per-channel confidence thresholds (SCALP=80, FVG=78, OB=78, DIV=76)
- ADX minimum raised, global 30-min cooldown, named signal headers
- 4 channels soft-disabled (CVD, VWAP, SUPERTREND, ICHIMOKU)
- Pairs expanded to 75

### PR2 — AI-Powered Engagement Layer ✅ MERGED (PR#45, 2026-04-06)
- Scheduled content (morning brief, session opens, EOD wrap, weekly card)
- Radar alerts — soft-disabled channels at conf ≥ 65 post to free channel
- Trade closed posts — every TP and SL auto-posts
- Smart silence breaker — 3hr silence during trading hours triggers market watch post
- GPT-4o-mini analyst voice, rotating variants, template fallback

### PR2-bugfix — Fix scheduler routing + BTC price + digest misclassification ✅ MERGED (PR#46, PR#47, 2026-04-06)
- Fixed /digest win/loss misclassification for INVALIDATED trades
- Fixed scheduler routing, BTC price, silence breaker, radar scores

### PR3 — Scan Latency Fix + 75-Pair Universe ✅ MERGED (PR#48, 2026-04-07)
- Indicator result cache — ~90% reduction in thread pool work
- Scan latency reduced from 33–40s → 8–12s
- WS_DEGRADED_MAX_PAIRS raised 50 → 75

### PR4 — Protective Mode Broadcaster + Subscriber Commands ✅ MERGED (PR#49, 2026-04-07)
- Auto-posts when market volatile/unsuitable
- /signals, /history, /market, /performance, /ask commands revamped

### PR5 — Signal Safety ✅ MERGED (PR#50, 2026-04-07)
- Near-zero SL rejection (< 0.05% from entry)
- Failed-detection cooldown (3 consecutive failures → 60s suppression)
- Dynamic pair count in all subscriber-facing commands

### PR6 — Dead Channel Removal ✅ MERGED (PR#51, 2026-04-07)
- Removed 360_SPOT, 360_GEM, 360_SWING, 360_SCALP_OBI from entire codebase
- Depth fetches and depth circuit breaker fully removed (PR#43)

### PR7 — Signal Architecture Overhaul ✅ MERGED (PR#52, 2026-04-07)
- **REMOVED** `_evaluate_range_fade` (BB mean reversion — no SMC basis, retail strategy)
- **FIXED** Cross-asset gate — now direction-aware and graduated by correlation strength
- **FIXED** Regime ADX lag — EMA9 slope fast-path for TRENDING_DOWN detection
- **FIXED** HTF EMA rejection threshold 0.05% → 0.15%
- **FIXED** EMA crossover invalidation age gate (≥ 300s)
- **FIXED** Momentum threshold — ATR-adaptive per pair
- **ADDED** `_evaluate_trend_pullback` (TREND_PULLBACK_CONTINUATION)
- **ADDED** `_evaluate_liquidation_reversal` (LIQUIDATION_REVERSAL)
- **ADDED** `detect_continuation_sweep()` in smc.py
- **ADDED** Regime transition boost (RANGING→TRENDING_DOWN boosts SHORTs +6)
- **ADDED** Per-pair session multipliers in kill_zone.py
- Global symbol cooldown: 1800s → 900s, made directional (symbol+direction keyed)

### PR7-bugfix — _regime_key NameError fix ✅ MERGED (PR#53, 2026-04-08)
- Fixed `_regime_key` NameError in `_compute_base_confidence`

### PR8 — Volume Surge Signal Paths + Dynamic Discovery ✅ MERGED (PR#54, 2026-04-08)
- **ADDED** `_evaluate_volume_surge_breakout` (VOLUME_SURGE_BREAKOUT) — breakout + retest entry
- **ADDED** `_evaluate_breakdown_short` (BREAKDOWN_SHORT) — mirror for shorts
- **ADDED** Dynamic pair promotion — 5× volume surge promotes pair for 3 scan cycles
- **ADDED** Signal expiry notifications via Telegram
- **FIXED** Structural SL/TP for `_evaluate_standard` and `_evaluate_trend_pullback`
- Blocked in VOLATILE_UNSUITABLE for QUIET only — fires in all other regimes

### PR9 — Method Expansion + Diagnostics ✅ MERGED (PR#55, 2026-04-08)
- **ADDED** `_evaluate_opening_range_breakout` (London 07–09 UTC / NY 12–14 UTC)
- **ADDED** `_evaluate_sr_flip_retest` (S/R flip + rejection candle)
- **ADDED** `_evaluate_funding_extreme` (contrarian on extreme funding rates)
- **ADDED** `_evaluate_quiet_compression_break` (BB squeeze — QUIET/RANGING only)
- **ADDED** `_evaluate_divergence_continuation` (CVD hidden divergence — TRENDING only)
- **ADDED** Live signal pulse loop (every 30min posts PnL update per open signal)
- **ADDED** `diagnose_pair(symbol)` dry-run diagnostic method in scanner
- **ADDED** `/why <symbol>` Telegram command

### PR10 — VPS Monitor Workflow ✅ MERGED (PR#56–#63, 2026-04-08)
- Manual GitHub Actions workflow to SSH into VPS and collect live system state
- Writes output to `monitor-logs` branch (`monitor/latest.txt`) for autonomous Copilot access
- Sections: Container status, resource usage, heartbeat check, signal telemetry, signal performance history, engine logs, error scan, Redis info
- Multiple bugfixes to heredoc/YAML syntax and signal performance history rendering

### PR10-hotfix — Circuit breaker grace + volatile bypass ✅ MERGED (PR#58, 2026-04-08)
- Private repo auth fix for VPS deploy
- Circuit breaker grace period on startup (178s)
- Volatile_unsuitable bypass for surge/breakdown paths

### PR11 — Heartbeat Path Fix ✅ MERGED (PR#64, 2026-04-08)
- Fixed heartbeat monitoring permanently blind due to named volume path mismatch
- Container was showing UNHEALTHY despite engine running fine

### PR12 — Snapshot I/O Async Fix ✅ MERGED (PR#65, 2026-04-09)
- Fixed `save_snapshot()` blocking I/O — 30–55s ScanLat spikes every 5 min
- Wrapped `np.savez_compressed()` in `loop.run_in_executor(None, self._save_snapshot_sync)`
- 550 symbol-timeframe combos now saved non-blocking
- ScanLat confirmed stable at 3,400–4,000ms post-merge ✅

### PR13 — Heartbeat YAML Fix ✅ MERGED (PR#66, 2026-04-09)
- Base64-encoded heartbeat Python block to resolve YAML syntax error in vps-monitor.yml

---

## 7. Current System State (2026-04-09)

| Item | Status |
|---|---|
| Engine running on VPS | ✅ Yes — 13 min uptime at last monitor run |
| Container health | ⚠️ UNHEALTHY — heartbeat file not being written (path issue still active despite PR11) |
| ScanLat | ✅ Fixed — 3,400–4,000ms (was 30–55s spikes) |
| WS streams | ✅ 300 streams healthy |
| Pairs scanning | ✅ 75 pairs |
| Market conditions | ⚠️ Extreme Fear (F&G=14), tariff shock, 44/75 pairs spread-blocked |
| Signal output | ⚠️ Only RANGE_FADE in history (old engine) — new engine 13 min old, no new-path signals yet |
| Active signals | 1 (BTCUSDT LONG fired 05:05 UTC) |
| trade_monitor TypeError | 🐛 OPEN — `float - datetime` on signal close in `_post_signal_closed` line 978 |
| PR in progress | 🔄 Signal path analysis + fixes being raised |
| Deep research | 🔄 Running — full 11-evaluator pipeline audit |

### Known Open Bugs (2026-04-09)
| # | Bug | File:Line | Impact |
|---|---|---|---|
| 1 | `float - datetime` TypeError on signal close | `src/trade_monitor.py:978` | Signal-closed Telegram posts fail silently |
| 2 | Heartbeat not written → container UNHEALTHY | `src/scanner/__init__.py` — `_HEARTBEAT_PATH` resolves outside container `/app/data/` | Healthcheck always failing |
| 3 | `_evaluate_volume_surge_breakout` retest zone too tight | `src/channels/scalp.py` | Was 0.5–2%, relaxed to 0.2–3.0% in fix PR |
| 4 | `_evaluate_sr_flip_retest` flip recency too strict | `src/channels/scalp.py` | Was 5 candles + 0.3%, relaxed to 8 candles + 0.5% |
| 5 | `funding_rate` mandatory blocks `_evaluate_funding_extreme` | `src/channels/scalp.py` | Made optional — degrades gracefully |

---

## 8. System Thresholds Quick Reference

| Variable | Value | Env Var |
|---|---|---|
| Min confidence SCALP | 80 | `MIN_CONFIDENCE_SCALP` |
| Min confidence FVG | 78 | `MIN_CONFIDENCE_FVG` |
| Min confidence ORDERBLOCK | 78 | `MIN_CONFIDENCE_ORDERBLOCK` |
| Min confidence DIVERGENCE | 76 | `MIN_CONFIDENCE_DIVERGENCE` |
| SMC hard gate | 12.0 | `SMC_HARD_GATE_MIN` |
| Trend hard gate | 10.0 | `TREND_HARD_GATE_MIN` |
| Volume floor QUIET | $1M | `VOL_FLOOR_QUIET` |
| Volume floor RANGING | $1.5M | `VOL_FLOOR_RANGING` |
| Volume floor TRENDING | $3M | `VOL_FLOOR_TRENDING` |
| Volume floor VOLATILE | $5M | `VOL_FLOOR_VOLATILE` |
| Global symbol cooldown | 900s (directional) | `GLOBAL_SYMBOL_COOLDOWN_SECONDS` |
| Per-channel cooldown | 600s | `SCALP_SCAN_COOLDOWN` |
| Max correlated scalps | 4 | `MAX_CORRELATED_SCALP_SIGNALS` |
| Pairs scanned | 75 | `TOP50_FUTURES_COUNT` |
| ADX min SCALP | 20 | `ADX_MIN_SCALP` |
| ADX min RANGING floor | 12 | `_ADX_RANGING_FLOOR` |
| MTF min score (general) | 0.6 | — |
| MTF min score (SHORT, TRENDING_DOWN) | 0.45 | `MTF_MIN_SCORE_TRENDING_SHORT` |
| Funding rate extreme threshold | 0.001 | `FUNDING_RATE_EXTREME_THRESHOLD` |
| Signal pulse interval | 1800s | `SIGNAL_PULSE_INTERVAL_SECONDS` |
| Surge volume multiplier | 3.0× | `SURGE_VOLUME_MULTIPLIER` |
| Surge promotion multiplier | 5.0× | `SURGE_PROMOTION_VOLUME_MULTIPLIER` |
| Surge max promoted pairs | 5 | `SURGE_PROMOTION_MAX_PAIRS` |
| Radar alert threshold | 65 | `RADAR_ALERT_MIN_CONFIDENCE` |
| Silence breaker window | 3 hours | `SILENCE_BREAKER_HOURS` |
| GPT model | gpt-4o-mini | `CONTENT_GPT_MODEL` |
| Snapshot interval | 300s | `asyncio.sleep(300)` in `_snapshot_loop` |
| Snapshot combos | 550 | symbol-timeframe combos |

---

## 9. How We Work

```
1. COPILOT ACTS PROACTIVELY  → spots issues, fixes bugs, raises PRs without being asked
2. DISCUSS                   → for major architecture decisions, explore options first
3. AGREE                     → owner approves direction on major changes
4. BUILD                     → agent creates the PR
5. REVIEW                    → review against spec together
6. MERGE                     → only when correct
7. UPDATE                    → this file updated immediately after session
```

**Copilot responsibilities:**
- Act immediately on bugs and obvious fixes — no waiting
- Monitor PR status, flag completion without being asked
- Bring technical ideas proactively
- Flag risks before they become problems
- Keep this file fully current after every session

**Owner responsibilities:**
- Final say on direction and priorities
- Approve major architectural proposals
- Nothing technical unless desired

---

## 10. Session History

### Session — 2026-04-06 (System Inception + PR1/PR2)
- System architecture established, 360-v2 repo set up
- PR1 merged: signal quality overhaul, SMC hard gate, 75 pairs
- PR2 merged: AI engagement layer, scheduled content, radar alerts, trade closed posts
- Business rules B1–B14 locked

### Session — 2026-04-07 (Deep Audit + PR3–PR7)
- Deep audit completed — 6 unused PairProfile fields, dead cross-asset gate, ADX lag, zero SHORTs
- RANGE_FADE confirmed as having no edge — scheduled for removal
- PR3: scan latency 33–40s → 8–12s
- PR4: protective mode broadcaster + subscriber commands
- PR5: signal safety (near-zero SL rejection, failed-detection cooldown)
- PR6: dead channel removal (OBI, SPOT, GEM, SWING)
- PR7: signal architecture overhaul — RANGE_FADE removed, 2 new paths added, cross-asset gate fixed
- Architecture decisions locked: continue in existing repo, RANGE_FADE removal confirmed

### Session — 2026-04-08 (Signal Paths + ScanLat + VPS Monitor)
- PR8 merged: volume surge breakout + breakdown short paths, dynamic pair promotion, expiry notifications
- PR9 merged: 5 new evaluator methods (ORB, SR flip, funding extreme, compression break, divergence continuation)
- PR10 merged: VPS monitor workflow (multi-step bugfix process)
- PR11 merged: heartbeat path fix
- VPS monitor run — ScanLat spikes diagnosed (30–55s every 5min)
- PR12 spec agreed: snapshot I/O async fix (run_in_executor)
- Session closed — PR12 to be raised next session

### Session — 2026-04-09 (PR12/13 Merged + Signal Analysis)
- PR12 merged: snapshot I/O fix — ScanLat confirmed fixed (3,400–4,000ms stable) ✅
- PR13 merged: heartbeat YAML syntax fix ✅
- VPS monitor run: F&G=14 (Extreme Fear), 44/75 pairs spread-blocked, engine 13 min uptime
- Discovered: RANGE_FADE signals in history are from OLD engine run — new engine paths not yet producing
- Analysed: 11 evaluator paths — most silent due to: extreme market conditions, SMC B5 gate, retest zones too tight, funding_rate data optional
- trade_monitor TypeError identified: `float - datetime` on signal close
- Heartbeat still writing outside container path — container showing UNHEALTHY
- Deep research session launched: full 11-evaluator pipeline audit
- Signal path fix PR raised: relaxed retest zones, fixed TypeError, fixed heartbeat path, added per-evaluator debug logging
- OWNER_BRIEF.md fully rebuilt — previous sessions had stripped it to single-session entry only

### Next Actions
- Monitor deep research results — review findings, raise additional fix PRs immediately
- Merge signal path fix PR — confirm new evaluator paths start producing signals
- Run VPS monitor after fixes — confirm container HEALTHY, TypeError gone
- Watch for first new-path signals as market normalises post tariff-shock
- Continue signal pipeline analysis — ensure all 11 paths have clear route to fire
