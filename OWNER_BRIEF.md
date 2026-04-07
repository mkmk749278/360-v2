# 360 Crypto Eye — Owner Operating Manual

> **This is the single source of truth for everything: system state, technical decisions, PR history, and how every Copilot session must behave.**
>
> ---
>
> ### How to Start Every New Copilot Session
>
> Paste this exactly:
> ```
> Read OWNER_BRIEF.md in mkmk749278/360-v2 on main branch.
> Today I want to: [describe what you need today]
> ```
>
> Copilot reads this file and operates as **technical engineer and system co-owner**, not a code assistant.

---

## ⚠️ Critical Instructions for Copilot — Read First, Every Session

| Rule | What It Means |
|---|---|
| **You are co-owner and technical engineer** | Full rights on this system. Drive technical decisions. Bring ideas proactively. Don't wait to be asked. |
| **System and data first** | Current phase is system building and validation only. No business strategy, no subscriber focus, no marketing — until the engine produces quality signals consistently for 4 weeks. |
| **Discuss first. Build second.** | Never jump straight to a PR. Discuss the problem, explore options, agree on solution, then implement. |
| **Understand before proposing** | Read the relevant code before suggesting anything. Never propose based on assumptions. |
| **One PR = one clear technical outcome** | Every PR must have a clear "what problem does this solve" answer before it is created. |
| **Review before merge** | After a PR is created, review it against spec. If it misses, revise — do not close and move on. |
| **Never reverse locked rules** | Rules in the Business Rules section are locked. Do not suggest removing them without explicit owner instruction. |
| **Never invent data** | GPT writes voice and tone. Engine provides numbers. Never fabricate prices, win rates, or signal data. |
| **Work ahead** | PR(N+1) spec must be ready before PR(N) merges. Never idle. |
| **Clean up mistakes immediately** | If a wrong file is created or a wrong change made, flag it and fix it in the same session. |

---

## 1. What This System Is

**360 Crypto Eye** is a 24/7 automated crypto trading signal engine. It scans 75 Binance USDT-M futures pairs continuously, detects institutional-grade setups using Smart Money Concepts + advanced signal techniques, and delivers only the highest-quality signals.

**Current phase: System validation. No subscribers. No business activity.**
The engine must prove itself against the testing scorecard before anything else happens.

**Owner:** mkmk749278
**Repo:** https://github.com/mkmk749278/360-v2
**Stack:** Python 3.11+, asyncio, aiohttp, Redis, Docker Compose, Telegram Bot API
**Deployment:** Single VPS, Docker Compose, GitHub Actions CD on push to `main`

---

## 2. System Architecture — Current State

### Active Signal Channels (paid)
| Channel | Status | What It Does |
|---|---|---|
| `360_SCALP` | ✅ Active | Sweep reversals, whale momentum (RANGE_FADE being removed in PR7) |
| `360_SCALP_FVG` | ✅ Active | Fair Value Gap retests |
| `360_SCALP_ORDERBLOCK` | ✅ Active | SMC order block bounces |
| `360_SCALP_DIVERGENCE` | ✅ Active | RSI/MACD divergence reversals |

### Radar Channels (free channel only)
| Channel | Status | What It Does |
|---|---|---|
| `360_SCALP_CVD` | 📡 Radar | Free channel alerts when conf ≥ 65 |
| `360_SCALP_VWAP` | 📡 Radar | Free channel alerts when conf ≥ 65 |
| `360_SCALP_SUPERTREND` | 📡 Radar | Free channel alerts when conf ≥ 65 |
| `360_SCALP_ICHIMOKU` | 📡 Radar | Free channel alerts when conf ≥ 65 |

### Removed Channels (deliberately, permanently)
| Channel | Reason |
|---|---|
| `360_SPOT` | Not in scope — deferred indefinitely |
| `360_GEM` | Not in scope — deferred indefinitely |
| `360_SWING` | Not in scope — deferred indefinitely |
| `360_SCALP_OBI` | REST order book depth caused scan latency — structural problem, full removal |

### Signal Generation Paths (inside ScalpChannel)
| Path | Status | Notes |
|---|---|---|
| `_evaluate_standard` — LIQUIDITY_SWEEP_REVERSAL | ✅ Active | Genuine SMC sweep detection |
| `_evaluate_range_fade` — BB mean reversion | ❌ Removing in PR7 | Retail strategy, fails SMC gate, no edge |
| `_evaluate_whale_momentum` | ✅ Active | Large volume spike + OBI |
| `_evaluate_trend_pullback` | ⏳ Adding in PR7 | EMA9/21 pullback in trending regime |
| `_evaluate_liquidation_reversal` | ⏳ Adding in PR7 | Cascade overshoot + CVD divergence |

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
| B11 | Discuss and agree before building. Always. |
| B12 | System and data focus only until 4-week validation scorecard passes |

---

## 4. Testing Phase Scorecard (Phase 1 Exit Criteria)

The system must pass ALL of these before Phase 2 begins. No exceptions.

| Metric | Minimum to proceed |
|---|---|
| Win rate (TP1 or better) | ≥ 60% |
| Entry reachability | ≥ 80% of signals gave a fair entry window |
| SL from wrong setup | ≤ 20% of all SL hits |
| Max concurrent open signals | ≤ 4 at any one time |
| Worst week drawdown | ≤ 10% of account |
| Signals with TP2+ reached | ≥ 40% of winning trades |

**Every SL hit gets categorised:**
- Setup was wrong
- Regime changed after entry
- Stop too tight
- Bad timing
- Genuine market event (news, cascade, macro shock)

---

## 5. Signal Quality Gates (13 layers)

Every signal survives all 13 before dispatch:
1. Market regime classification
2. Spread gate
3. Volume gate (regime-aware floor)
4. SMC structural basis — sweep, FVG, or orderblock required
5. Multi-timeframe alignment
6. EMA trend alignment
7. Momentum confirmation
8. MACD confirmation
9. Order flow — OI trend, CVD divergence, liquidation data
10. Cross-asset correlation (BTC/ETH macro gate)
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

## 6. Key Diagnosed Issues (From April 6th Incident + Deep Audit)

### Why Zero SHORT Signals Were Ever Fired
1. Sweep detection only catches reversal sweeps — no trend-continuation sweep detection
2. No `_evaluate_trend_pullback` path exists — being added in PR7
3. Cross-asset gate hard blocks BOTH directions when BTC dumps — bug, being fixed in PR7

### Why RANGE_FADE Dominated All Signals
1. BB touches happen multiple times per day on every pair — always has candidates
2. `mean_reversion: 1.2` weight boost gave it artificial advantage — being removed in PR7
3. LIQUIDITY_SWEEP_REVERSAL needs genuine sweep events — rare without correct detection

### Why Zero Signals After RANGE_FADE Removed
12+ sequential gates kill insufficient candidates:
- Cross-asset gate blocks most LONGs when BTC bearish (and incorrectly blocks SHORTs too)
- MTF min_score 0.6 too strict for TRENDING_DOWN SHORT entries
- SMC hard gate correct but needs better sweep candidate generation
- Global cooldown 1800s limits max 2–3 signals/hour across all 75 pairs

### Deep Audit Additional Findings
- 6 of 10 `PairProfile` fields defined but never consumed — infrastructure exists, not wired
- AI engine correlation features permanently dead code (`btc_correlation` always 0.0)
- Cross-asset gate treats PEPE (0.25 BTC corr) same as ETH (0.90 BTC corr) — wrong
- Performance tracker stores `market_phase` per signal but has zero query methods
- Session multipliers uniform across all pairs — PEPE outside London/NY should be hard blocked

---

## 7. PR Log

### PR1 — Signal Quality Overhaul ✅ MERGED
- SMC hard gate, trend hard gate, per-channel confidence thresholds
- ADX minimum raised, global 30-min cooldown, named signal headers
- 4 channels soft-disabled (CVD, VWAP, SUPERTREND, ICHIMOKU)
- Pairs expanded to 75

### PR2 — AI-Powered Engagement Layer ✅ MERGED
- Scheduled content (morning brief, session opens, EOD wrap, weekly card)
- Radar alerts — soft-disabled channels at conf ≥ 65 post to free channel
- Trade closed posts — every TP and SL auto-posts
- Smart silence breaker — 3hr silence during trading hours triggers market watch post
- GPT-4o-mini analyst voice, rotating variants, template fallback

### PR3 — Scan Latency Fix + 75-Pair Universe Unlock ✅ MERGED
- Indicator result cache — eliminates ~90% of thread pool work per cycle
- SMC detection deduplicated — 4 detections → 2 per symbol
- Scan latency reduced from 33–40s to 8–12s
- WS_DEGRADED_MAX_PAIRS default raised 50 → 75

### PR4 — User Interaction Layer ✅ MERGED
- Protective Mode Broadcaster — auto-posts when market volatile/unsuitable
- Commands revamped — /signals, /history, /market, /performance, /ask

### PR5 — Signal Safety ✅ MERGED
- Near-zero SL rejection (< 0.05% from entry)
- Failed-detection cooldown (3 consecutive failures → 60s suppression)
- Dynamic pair count in all subscriber-facing commands

### PR6 — Dead Channel Removal 🔄 IN PROGRESS — PR #51
**Branch:** `copilot/remove-dead-channel-code`
**What it does:**
- Remove 360_SPOT, 360_GEM, 360_SWING, 360_SCALP_OBI from entire codebase
- Delete `src/channels/scalp_obi.py`, `src/radar_channel.py`, `src/chart_generator.py`
- Fix radar/watchlist → unified free channel posting (scanner writes `_radar_scores`)
- Scope OrderManager to SCALP market orders only (limit order logic removed)
- Update all tests

**Status:** 17/17 source files cleaned. 3 tasks remaining:
- [ ] Fix `src/dca.py` — remove dead 360_SWING EMA200 block
- [ ] Fix 9 test files referencing dead channels
- [ ] Delete `src/chart_generator.py`
- [ ] Run full test suite → green

**Note:** Two junk files accidentally created on main during session — need deletion:
- `pulls/51/comments`
- `comments/pr_51.md`

### PR7 — Signal Architecture Overhaul ⏳ SPEC READY — raise after PR6 merges

#### 🔴 REMOVE
| # | What | File |
|---|---|---|
| 1 | `_evaluate_range_fade` entirely | `src/channels/scalp.py` |
| 2 | `mean_reversion: 1.2` weight boost | `src/channels/scalp.py` |

#### 🔴 FIX
| # | What | File | Change |
|---|---|---|---|
| 3 | Cross-asset gate direction | `src/cross_asset.py` | Graduated by correlation: >0.8 hard block, 0.5–0.8 = -10 penalty, 0.2–0.5 = -3 penalty, <0.2 = no penalty. BTC DUMPING + SHORT → allow + boost |
| 4 | Regime ADX lag | `src/regime.py` | EMA slope < -0.1% → TRENDING_DOWN immediately |
| 5 | MTF min_score TRENDING_DOWN | `src/scanner/__init__.py` | 0.6 → 0.45 |
| 6 | Global symbol cooldown | `config/__init__.py` | 1800s → 900s, make directional |
| 7 | HTF EMA rejection threshold | `src/channels/scalp.py` | 0.05% → 0.15% |
| 8 | EMA crossover invalidation age gate | `src/trade_monitor.py` | No check until signal age ≥ 300s |
| 9 | Momentum invalidation threshold | `src/trade_monitor.py` | Fixed 0.1 → ATR-adaptive per pair |
| 10 | Component score minimums | `src/scanner/__init__.py` | market < 8.0 for SHORT in TRENDING_DOWN (was 12.0) |
| 11 | AI engine correlation dead code | `src/ai_engine/predictor.py` | Wire rolling BTC correlation into btc_correlation feature |

#### 🟢 ADD
| # | What | File |
|---|---|---|
| 12 | `_evaluate_trend_pullback` | `src/channels/scalp.py` |
| 13 | `_evaluate_liquidation_reversal` | `src/channels/scalp.py` |
| 14 | Funding rate gate | `src/scanner/__init__.py` + `src/oi_filter.py` |
| 15 | Bearish continuation sweep detection | `src/smc.py` |
| 16 | Regime transition detection + signal boost | `src/regime.py` |
| 17 | `get_stats_by_regime()` | `src/performance_tracker.py` |
| 18 | `get_pair_stats(symbol)` | `src/performance_tracker.py` |

#### 🔵 IMPROVE
| # | What | File |
|---|---|---|
| 19 | Wire unused PairProfile fields | `src/channels/scalp.py` + sub-channels |
| 20 | Per-pair session multipliers | `src/kill_zone.py` |
| 21 | Track confidence decay per signal | `src/channels/base.py` |

### PR8 — Intelligence Layer ⏳ SPEC READY — raise after PR7 merges + 2 weeks data

- Symbol-specific PairProfile overrides (`PAIR_OVERRIDES` dict in config)
- Rolling BTC correlation calculation (50-candle + 200-candle Pearson)
- Graduate sneeze filter by correlation strength (replaces binary block)
- Per-pair × regime confidence offsets
- Per-pair circuit breaker daily drawdown limits
- Session performance tracking (`session_name` in SignalRecord)
- Extended performance metrics (Sharpe, profit factor, expectancy, MFE/MAE)
- Lead/lag detection — identify pairs that move before BTC

### PR9 — Method Expansion ⏳ CONCEPT — raise after PR8 merges + live data reviewed

New signal methods to add (each with tight per-method rules):
- `_evaluate_orb` — Opening Range Breakout at London/NY session opens
- `_evaluate_breakout_retest` — Broken key level retested from other side
- Funding Rate Extreme as signal source (upgrade from gate to signal emitter)
- CVD Divergence promoted from filter to primary signal path
- Orderblock channel fully activated and wired

**Full method coverage map (post-PR9):**
All market conditions covered — TRENDING, RANGING, VOLATILE, QUIET, TRANSITION — no dead zones.

### PR10 — Self-Optimisation ⏳ CONCEPT — raise after 50+ live signals exist
- Per-method win rate tracking by regime
- Auto-disable method if win rate < 50% over 30-day window
- Auto-weight methods based on live performance data

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
| Global symbol cooldown | 1800s → 900s in PR7 | `GLOBAL_SYMBOL_COOLDOWN_SECONDS` |
| Per-channel cooldown | 600s | `SCALP_SCAN_COOLDOWN` |
| Max correlated scalps | 4 | `MAX_CORRELATED_SCALP_SIGNALS` |
| Pairs scanned | 75 | `TOP50_FUTURES_COUNT` |
| ADX min SCALP | 20 | `ADX_MIN_SCALP` |
| Radar alert threshold | 65 | `RADAR_ALERT_MIN_CONFIDENCE` |
| Radar per-symbol cooldown | 900s | `RADAR_PER_SYMBOL_COOLDOWN_SECONDS` |
| Radar max per hour | 3 | `RADAR_MAX_PER_HOUR` |
| Silence breaker window | 3 hours | `SILENCE_BREAKER_HOURS` |
| GPT model | gpt-4o-mini | `CONTENT_GPT_MODEL` |

---

## 9. How We Work

```
1. COPILOT BRINGS IDEAS → proactively, before being asked
2. DISCUSS             → explore the problem deeply
3. AGREE               → owner approves direction
4. SPECIFY             → write exact PR spec before creating it
5. BUILD               → agent creates the PR
6. REVIEW              → review against spec together
7. REVISE              → fix anything that misses spec
8. MERGE               → only when fully correct
9. UPDATE              → this file updated to reflect new state
```

**Copilot responsibilities:**
- Monitor PR status, flag completion without being asked
- Bring technical ideas proactively
- Write next PR spec before current PR merges
- Flag risks before they become problems
- Keep this file current after every session

**Owner responsibilities:**
- Final say on direction and priorities
- Approve or challenge technical proposals
- Nothing technical unless desired

---

## 10. Current State Snapshot (2026-04-07)

| Item | Status |
|---|---|
| Engine running on VPS | ✅ Yes |
| PR6 | 🔄 Agent working — 3 tasks remaining |
| Deep research audit | ✅ Complete — findings incorporated into PR7/PR8 spec |
| PR7 spec | ✅ Ready — 21 items across 8 files |
| PR8 spec | ✅ Ready — 8 items |
| PR9 concept | ✅ Drafted |
| Junk files on main to delete | ⚠️ `pulls/51/comments` and `comments/pr_51.md` |
| Testing phase | ⏳ Not started — begins after PR7 merges |
| Subscribers | ❌ None — deliberately. System validation first. |

---

## 11. Notes Log

**2026-04-07 — Architecture decisions locked today:**
- Continue in existing repo — do not start fresh. Foundation is solid.
- RANGE_FADE removal confirmed — BB+RSI retail strategy, never had edge, fails SMC gate
- Cross-asset gate bug confirmed — hard blocks SHORTs when BTC dumps (wrong). Fixed in PR7.
- Deep audit confirmed 6 of 10 PairProfile fields unused — infrastructure wiring is PR8 item 19
- AI engine btc_correlation always 0.0 — dead code confirmed. Fixed in PR7 item 11.
- PR9 method stack agreed — ORB, Breakout Retest, Funding Extreme signal, CVD promotion, OB activation
- Copilot role clarified — technical engineer and system co-owner. Not a code assistant. Not a business consultant yet.

**2026-04-07 — April 6th incident root cause (fully diagnosed):**
- 8 LONG signals fired, zero SHORT signals, 33% win rate
- Root cause: no trend pullback path, cross-asset gate blocked SHORTs, ADX lag misclassified TRENDING_DOWN as RANGING
- All root causes addressed in PR7 spec

**2026-04-07 — PR5:**
- BULLAUSDT generating near-zero SL (0.017%) — dangerous signal caught and blocked
- Failed-detection infinite loop fixed — 3 consecutive failures → 60s suppression

**Permanent technical reminders:**
- Signal quality > signal quantity
- Every signal that fires must have genuine SMC basis
- Silence on dead market days is correct behaviour — not a bug
- Gates are correct — the problem has always been insufficient signal candidates
- The scanner has 2600 lines and 12+ gates. It works. Signal generation paths are what needed fixing.