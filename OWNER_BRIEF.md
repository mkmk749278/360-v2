# 360 Crypto Eye — Owner Brief

> **This file is the single source of truth for business context, architecture decisions, and active priorities.**
> 
> At the start of every new Copilot session, paste this prompt:
> ```
> Read OWNER_BRIEF.md in mkmk749278/360-v2 — continue from where we left off.
> ```
> Copilot will read this file, understand the full context, and continue without needing re-explanation.

---

## 1. What This Business Is

**360 Crypto Eye** is a paid crypto signal service built on a self-hosted, fully automated trading signal engine (`360-v2`). The engine scans Binance USDT-M futures in real time, detects Smart Money Concepts (SMC) setups, scores them through a multi-layer confidence pipeline, and posts actionable trade signals to a Telegram channel.

**Revenue model:** Monthly subscription. Subscribers pay to receive trade signals via Telegram. Retention depends on:
1. Signal quality — subscribers must be able to make money following signals
2. Channel activity — channel must feel alive and professionally run, not go silent for hours
3. Trust — every signal must look like it was written by a human expert analyst, not a bot

**The system is fully automated.** No manual effort at runtime. All content (signals, market commentary, session briefs, radar alerts) must be AI-generated but feel human-written.

**Owner:** mkmk749278  
**Repo:** https://github.com/mkmk749278/360-v2  
**Stack:** Python 3.11+, asyncio, aiohttp, Redis, Docker Compose, Telegram Bot API  
**Deployment:** Single VPS, Docker Compose, GitHub Actions CD on push to `main`

---

## 2. Business Rules (Non-Negotiable)

These decisions are made and locked. Do not reverse them without explicit owner instruction.

| # | Rule | Reason |
|---|---|---|
| B1 | All signals go to ONE Telegram channel (`TELEGRAM_ACTIVE_CHANNEL_ID`) | Simplicity. Subscribers see everything in one place. |
| B2 | Zero manual effort at runtime | Owner is not monitoring 24/7. Everything must self-manage. |
| B3 | Content must feel human-written | AI-generated but with natural language, named setups, context. Not "Signal fired: conf=83.2" |
| B4 | No channel code deleted — only disabled via config | Instant re-enable via `.env`. No irreversible changes. |
| B5 | All new config values must be env-var overridable | Owner must be able to tune values without code changes or redeployment |
| B6 | SMC structural basis is non-negotiable | No signal fires without minimum SMC score — no pure momentum plays |
| B7 | System must survive Binance API degradation gracefully | Circuit breakers, fallbacks, no scan-blocking on depth timeouts |
| B8 | Subscribers must never receive duplicate signals on same symbol within 30 minutes | Global cross-channel per-symbol cooldown enforced |

---

## 3. Architecture Decisions (Already Made)

| Decision | What We Chose | Why |
|---|---|---|
| Signal universe | Top-75 USDT-M futures (was 50) | More coverage while staying high-liquidity |
| Channel count active | 4 active channels | SCALP, FVG, ORDERBLOCK, DIVERGENCE |
| Channel count soft-disabled | 4 disabled | CVD, VWAP, SUPERTREND, ICHIMOKU — kept in code, off by default |
| Volume floor | Regime-aware (not flat) | $1M QUIET → $5M VOLATILE. Flat $3M kills signals during slow sessions |
| Confidence thresholds | Per-channel | SCALP=80, FVG=78, ORDERBLOCK=78, DIVERGENCE=76 |
| Kill zone POST_NY_LULL | Penalty only (not hard block) | Channel must stay alive 20:00–24:00 UTC |
| Signal headers | Named setup type | "⚡ SWEEP REVERSAL" not "360_SCALP_FVG" |
| Global symbol cooldown | 1800s (30 min) cross-channel | No 3x BTC LONG in 10 minutes |
| SMC hard gate | smc_score ≥ 12.0 required | Structural basis non-negotiable |
| Trend hard gate | trend_score ≥ 10.0 on scalp channels | Opposing EMAs = no signal |
| ADX minimum | 20 for SCALP, 18 for FVG | Was 15 — too loose |

---

## 4. PR Log

### PR1 — Signal Quality Overhaul *(in progress / merged)*
**Branch:** Created by Copilot agent  
**Status:** Agent working — check open PRs in repo

**Changes:**
- [ ] Regime-aware volume floor (`REGIME_MIN_VOLUME_USD`)
- [ ] SMC hard gate (min smc_score=12)
- [ ] Trend hard gate (min trend_score=10 on scalp)
- [ ] Per-channel confidence thresholds (SCALP=80, FVG=78, OB=78, DIV=76)
- [ ] ADX minimum raised (SCALP=20, FVG=18)
- [ ] Global cross-channel per-symbol 30-min cooldown
- [ ] Named signal headers (`SIGNAL_TYPE_LABELS` mapping)
- [ ] 4 channels soft-disabled via env flags (CVD, VWAP, SUPERTREND, ICHIMOKU)
- [ ] Pairs expanded to 75
- [ ] POST_NY_LULL multiplier raised to 0.65 (no longer hard-blocks)
- [ ] MAX_CORRELATED_SCALP_SIGNALS reduced to 4
- [ ] `.env.example` updated with all new vars

---

### PR2 — AI-Powered Radar & Engagement Layer *(planned)*
**Status:** Design agreed, not started

**What it does:**
- Free Telegram channel (`TELEGRAM_FREE_CHANNEL_ID`) becomes a **lead generation funnel** for the paid channel
- 4 soft-disabled channels (CVD, VWAP, SUPERTREND, ICHIMOKU) are repurposed as **Radar alert generators** — they post "ON RADAR" watch alerts to the free channel when their `evaluate()` would have fired (confidence > 65, lower bar)
- **Session open messages** — automated, AI-written, posted at London open (07:00 UTC), NY open (13:30 UTC): 2–3 lines about current regime, pairs being watched
- **Daily regime briefing** — 08:00 UTC, AI-generated, "This is what the market looks like today and what we're watching for"
- **Weekly performance summary** — Monday 09:00 UTC, AI-generated: signals sent, win rate, avg R
- All content generated by OpenAI GPT-4o-mini. Prompts must produce natural, analyst-voice output
- Zero manual effort. Fully scheduled and automated.

**Architecture for PR2:**
- New module: `src/content_engine.py` — AI content generator (session briefs, radar alerts, weekly summaries)
- New module: `src/radar_channel.py` — evaluates soft-disabled channels at lower threshold, posts to free channel
- New background task in `src/main.py` — scheduled content poster (cron-style via asyncio)
- GPT-4o-mini prompts stored in `src/prompts/` as `.txt` template files for easy editing

---

### PR3 — Revenue & Subscriber Features *(planned after PR2)*
**Status:** Concept only

**Ideas:**
- Subscriber tier system (Free / Premium via Telegram payments or external checkout)
- Performance proof page (auto-generated weekly image with win rate chart)
- Signal history command for subscribers
- Referral tracking

---

## 5. Current Priorities (In Order)

1. ✅ PR1 merged and running on VPS
2. 🔄 Review PR1 signals for 48 hours — confirm signal count is 8–15/day
3. ⏳ PR2 — AI Radar + Engagement Layer (discuss design before starting)
4. ⏳ PR3 — Revenue features (after PR2 is stable)

---

## 6. System Thresholds Quick Reference

| Variable | Current Value | Env Var to Change |
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
| Global symbol cooldown | 1800s (30 min) | `GLOBAL_SYMBOL_COOLDOWN_SECONDS` |
| Per-channel cooldown | 600s | `SCALP_SCAN_COOLDOWN` |
| Max correlated scalps | 4 | `MAX_CORRELATED_SCALP_SIGNALS` |
| Pairs scanned | 75 | `TOP50_FUTURES_COUNT` |
| ADX min SCALP | 20 | `ADX_MIN_SCALP` |
| ADX min FVG | 18 | `ADX_MIN_FVG` |
| Depth CB threshold | 3 timeouts/30s | `DEPTH_CIRCUIT_BREAKER_THRESHOLD` |
| Depth CB cooldown | 90s | `DEPTH_CIRCUIT_BREAKER_COOLDOWN` |

---

## 7. Active Channels

| Channel | Status | Purpose |
|---|---|---|
| `360_SCALP` | ✅ Active | Liquidity sweep reversals, range fades, whale momentum |
| `360_SCALP_FVG` | ✅ Active | Fair Value Gap retests |
| `360_SCALP_ORDERBLOCK` | ✅ Active | SMC order block bounces |
| `360_SCALP_DIVERGENCE` | ✅ Active | RSI/MACD divergence reversals |
| `360_SCALP_CVD` | 🔇 Soft-disabled | CVD data already in order_flow_score; separate channel = duplicate signals |
| `360_SCALP_VWAP` | 🔇 Soft-disabled | Overlaps with FVG retests — same candle, same direction, two signals |
| `360_SCALP_SUPERTREND` | 🔇 Soft-disabled | Trend-follower lags; SCALP sweep channel catches the move first |
| `360_SCALP_ICHIMOKU` | 🔇 Soft-disabled | Works on 1h+; generates noise on 5m |

To re-enable any: set `CHANNEL_SCALP_CVD_ENABLED=true` (etc.) in `.env`, restart engine.

---

## 8. How to Continue a Session

Paste this at the start of any new Copilot chat:

```
Read OWNER_BRIEF.md in mkmk749278/360-v2 — this is my crypto signal business.
Continue from where we left off. Current priority: [describe what you want to do today].
```

Copilot will read this file and have full context within seconds.

---

## 9. Owner Notes

*(Add your own notes here as we work — business decisions, ideas, things to remember)*

- PR2 must be fully automatic. No manual posting. Ever.
- The free channel is a sales funnel, not charity. Every free message should make someone want to upgrade.
- Signal quality > signal quantity. 8 clean signals/day beats 30 noisy ones.
- The system needs to feel like there's a professional analyst watching 24/7. GPT must write like one.