# 360 Crypto Eye — Owner Operating Manual

> **This is the single source of truth for everything: business vision, how we make decisions, what is built, what is planned, and how every Copilot session must behave.**
>
> ---
>
> ### How to Start Every New Copilot Session
>
> Paste this exactly:
> ```
> Read OWNER_BRIEF.md in mkmk749278/360-v2 — this is my crypto signal business.
> Today I want to: [describe what you need today]
> ```
>
> Copilot reads this file and operates as a **business co-owner**, not a code assistant.

---

## ⚠️ Critical Instructions for Copilot — Read First, Every Session

These rules govern how every Copilot session must behave. No exceptions.

| Rule | What It Means |
|---|---|
| **Think like a business owner** | You are not here to write code. You are here to help build a business. Every suggestion must serve revenue, subscriber retention, or system reliability. |
| **Discuss first. Build second.** | Never jump straight to a PR. Always discuss the problem deeply, explore options, agree on the best solution, then implement. |
| **Understand before proposing** | Read the relevant code before suggesting anything. Never propose changes based on assumptions. |
| **One PR = one clear business outcome** | Every PR must have a clear "what problem does this solve for the business" answer before it is created. |
| **Review before close** | After a PR is created, review whether it actually delivers what was agreed. If not, revise it. Do not close PRs that miss the brief. |
| **Never reverse business rules** | Rules in Section 3 are locked. Do not suggest removing them without explicit owner instruction. |
| **Never invent data** | GPT writes voice and tone. Engine provides numbers. Never let AI fabricate prices, win rates, or signal data. |
| **Fail safe always** | GPT outage, Redis down, Binance degraded — none of these should crash the engine or cause a missed post. Always template fallback. |

---

## 1. What This Business Is

**360 Crypto Eye** is a paid crypto signal service. The engine (`360-v2`) scans Binance USDT-M futures in real time, detects Smart Money Concepts (SMC) setups, and sends trade signals to a Telegram channel. Subscribers pay monthly to receive these signals.

**Revenue model:** Monthly subscription via Telegram.

**Retention depends on three things:**
1. **Signal quality** — subscribers must be able to make money following signals
2. **Channel activity** — the channel must feel alive and professionally run, never silent for hours
3. **Trust** — every message must look like a human expert analyst wrote it, not a bot

**The system is fully automated.** The owner is not monitoring 24/7. Everything must self-manage from signal detection to post formatting to scheduled content.

**Current status:** In testing. No subscribers yet. Building and validating the full system before public launch.

**Owner:** mkmk749278
**Repo:** https://github.com/mkmk749278/360-v2
**Stack:** Python 3.11+, asyncio, aiohttp, Redis, Docker Compose, Telegram Bot API
**Deployment:** Single VPS, Docker Compose, GitHub Actions CD on push to `main`

---

## 2. The Product — What Subscribers Experience

There are two Telegram channels:

### Paid Channel (`TELEGRAM_ACTIVE_CHANNEL_ID`)
What subscribers pay for. Contains:
- ✅ Live trade signals (entry, SL, TP1/TP2/TP3, confidence, setup name)
- ✅ Trade closed posts (TP hit or SL hit — honest, same weight for both)
- ✅ Silence breaker market watch posts (if 3+ hours silent during trading hours)
- ✅ Weekly performance card (Monday 09:00 UTC)

**Does NOT contain:**
- ❌ Radar alerts (those go free channel only)
- ❌ Session open / morning brief posts (those go free channel only)
- ❌ Any promotional content

### Free Channel (`TELEGRAM_FREE_CHANNEL_ID`)
Lead generation funnel. Every post makes someone want to upgrade. Contains:
- 📡 Radar alerts from 4 soft-disabled channels (max 3/hour, analyst voice)
- 📰 Morning brief (07:00 UTC)
- 🔔 London open (08:00 UTC)
- 🔔 NY open (13:30 UTC)
- 🌙 EOD wrap (21:00 UTC)
- 📊 Weekly performance card (Mon 09:00 UTC)

---

## 3. Business Rules (Non-Negotiable)

These are locked. Do not reverse without explicit owner instruction.

| # | Rule | Reason |
|---|---|---|
| B1 | All live signals go to ONE paid channel (`TELEGRAM_ACTIVE_CHANNEL_ID`) | Subscribers see everything in one place |
| B2 | Zero manual effort at runtime | Owner is not monitoring 24/7. Everything self-manages. |
| B3 | Content must feel human-written | Natural language, named setups, real context. Never "Signal fired: conf=83.2" |
| B4 | No channel code deleted — only disabled via config | Instant re-enable via `.env`. No irreversible changes. |
| B5 | All config values must be env-var overridable | Owner tunes without code changes or redeployment |
| B6 | SMC structural basis is non-negotiable | No signal fires without minimum SMC score — no pure momentum plays |
| B7 | System must survive Binance API degradation gracefully | Circuit breakers, fallbacks, no scan-blocking |
| B8 | No duplicate signals on same symbol within 30 minutes | Global cross-channel per-symbol cooldown enforced |
| B9 | Simple. Minimalistic. Eye-catching. | Every message looks clean, not robotic. Less is more. |
| B10 | SL hits posted honestly, same visual weight as TP hits | Transparency is a competitive advantage. Never go silent after a loss. |
| B11 | Radar alerts go to FREE channel ONLY | Paid channel gets live signals only. Free channel is the funnel. |
| B12 | GPT failure must never cause a missed post or crash | Always fall back to template. Engine stability is sacred. |
| B13 | Scheduled content goes to FREE channel only (except weekly card) | Paid subscribers receive signals, not market commentary |
| B14 | Discuss and agree before building. Always. | No surprise PRs. Owner approves direction before implementation begins. |

---

## 4. Message Formatting Design (Locked)

Every single message — signals, radar, scheduled posts — follows these rules:

1. Maximum 10 lines per message
2. One emoji maximum, always at the start of the message
3. Numbers aligned vertically using spaces
4. One separator style only — the `·` dot
5. No labels that shout — `TP1` not `🎯 TARGET 1:`
6. Confidence bar only on live signals — `████████░░`
7. SL posts carry the same visual weight as TP posts
8. GPT writes commentary only — all numbers come from engine data
9. Variant selection is context-driven — urgency, time of day, recent post frequency
10. Template fallback is production-quality — good enough to post without GPT

### Content Type Visual Identities

| Type | Channel | Style |
|---|---|---|
| Live Signal | Paid | Columns, conf bar, setup emoji, 3 rotating variants |
| Radar Alert | Free | Flowing analyst text, 6 rotating variants |
| Trade Closed TP | Paid | Clean fields, TP number, running W/L record |
| Trade Closed SL | Paid | Honest, same format as TP, no shame |
| Morning Brief | Free | 2–3 lines GPT + pairs, clean header |
| Session Open | Free | 2 lines max, no frame, immediate feel |
| EOD Wrap | Free | Reflective tone, 2–4 lines, what happened today |
| Market Watch | Paid | Short, patience tone, 3 variants |
| Weekly Card | Both | Stats table, clean columns |

---

## 5. PR Log

### PR1 — Signal Quality Overhaul ✅ MERGED
**PR:** [#44](https://github.com/mkmk749278/360-v2/pull/44) — merged 2026-04-06

- ✅ Regime-aware volume floor
- ✅ SMC hard gate (smc_score ≥ 12)
- ✅ Trend hard gate (trend_score ≥ 10 on scalp)
- ✅ Per-channel confidence thresholds (SCALP=80, FVG=78, OB=78, DIV=76)
- ✅ ADX minimum raised (SCALP=20, FVG=18)
- ✅ Global 30-min cross-channel symbol cooldown
- ✅ Named signal headers
- ✅ 4 channels soft-disabled (CVD, VWAP, SUPERTREND, ICHIMOKU)
- ✅ Pairs expanded to 75
- ✅ POST_NY_LULL no longer hard-blocks (0.65× penalty only)
- ✅ MAX_CORRELATED_SCALP_SIGNALS = 4

---

### PR2 — AI-Powered Engagement Layer ✅ MERGED

**Business goal:** The engine must never feel silent. Free channel generates leads. Paid channel stays active.

**5 pillars:**
1. **Scheduled content** — Morning brief, session opens, EOD wrap, weekly card → free channel. Weekly card → both.
2. **Radar alerts** — 4 soft-disabled channels run at conf ≥ 65, post to free channel only. 6 dynamic variants. Max 3/hour.
3. **Trade closed posts** — Every TP and SL auto-posts to paid channel. Honest. Running W/L record.
4. **Smart silence breaker** — No post for 3+ hours during 08:00–22:00 UTC → auto market watch post to paid channel.
5. **Dynamic presentation** — Rotating variants, GPT-4o-mini analyst voice, emoji pools, template fallback.

**PR2 fixes applied (merged with PR2):**
- ✅ Fix 1: Scheduler channel routing corrected — `morning_brief`, `london_open`, `ny_open`, `eod_wrap` now post to `["free"]` only; `weekly_card` keeps `["active", "free"]` (Business Rule B13)
- ✅ Fix 2: `_get_engine_context()` now reads live BTC price/change from `data_store.get_candles("BTCUSDT", "5m")` with `"—"` fallback if data unavailable
- ✅ Fix 3: `update_last_post()` now called from `_remove_and_archive()` so silence breaker resets correctly when a signal lifecycle ends
- ✅ Fix 4: `_radar_scores` now declared in `Scanner.__init__()` and populated during per-symbol scan via a separate radar evaluation pass for soft-disabled channels (fail-safe, never crashes scan loop)

**New modules:**
- `src/content_engine.py` — GPT wrapper + template renderer
- `src/formatter.py` — all message formatting and variants
- `src/scheduler.py` — asyncio cron scheduler
- `src/radar_channel.py` — radar alert evaluator
- `src/prompts/` — all GPT prompt templates as `.txt` files

---

### PR3 — Scan Latency Fix + 75-Pair Universe Unlock ✅ MERGED
**Business goal:** Reduce scan cycle latency from 33–40s to 8–12s. Unlock the 75-pair universe that was capped at 50 by a config mismatch.

**Changes:**
- ✅ `WS_DEGRADED_MAX_PAIRS` default raised from 50 → 75 — pairs now scan correctly
- ✅ Indicator result cache added to Scanner — skips recomputation when candles unchanged (eliminates ~90% of thread pool work per cycle)
- ✅ Per-channel SMC re-detect deduplicated — 4 detections per symbol → 2 (shared by TF set)
- ✅ `_BOOK_TICKER_PREFETCH_TIMEOUT_S` reduced from 8s → 3s — eliminates up to 5s per slow Binance cycle

---

### PR4 — User Interaction Layer ✅ MERGED
**Business goal:** Turn engine silence during crashes into trust signals. Replace robotic command output with subscriber-facing human-voiced responses.

**Changes:**
- ✅ Protective Mode Broadcaster — auto-posts to free + paid channels when volatile_unsuitable ≥ 10 or spread too wide ≥ 20. 2hr cooldown. Recovery post when conditions normalise.
- ✅ Commands revamped — `/signals`, `/history`, `/market`, `/performance`, `/ask` now human-voiced and available to all subscribers
- ✅ Dead stubs removed — `/subscribe`, `/unsubscribe`, `/free_signals`, `/last_update`, `/info` removed
- ✅ `/signal_stats` and `/tp_stats` moved to admin-only
- ✅ Welcome message updated — accurate pair count, real channels, no false promises

### PR5 — Revenue & Subscriber Features ⏳ PLANNED (after PR4 stable)

---

## 6. How We Work — The Decision Process

**This is how every piece of work must be handled:**

```
1. DISCUSS   → Owner describes the problem or idea
2. EXPLORE   → Copilot reads the relevant code, understands the full picture
3. PROPOSE   → Copilot presents options with business trade-offs, not just tech options
4. AGREE     → Owner selects the direction
5. SPECIFY   → We write down exactly what the PR must do before it is created
6. BUILD     → Copilot agent creates the PR
7. REVIEW    → We review the PR together against the spec
8. REVISE    → If it misses the spec, we revise — not close and move on
9. MERGE     → Only when it fully delivers the agreed outcome
10. UPDATE   → This file (OWNER_BRIEF.md) is updated to reflect the new state
```

**No step is skipped. Ever.**

---

## 7. Current Priorities (In Order)

1. ✅ PR1 merged and running on VPS
2. ✅ PR2 — AI engagement layer merged and monitored
3. ✅ PR3 — Scan latency fix + 75-pair unlock merged
4. 🔄 PR4 — User interaction layer (in progress)
5. ⏳ Monitor signal volume after PR4 (target: 10–20 signals/day)
6. ⏳ PR5 — Revenue features (after PR4 is confirmed stable)

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
| Global symbol cooldown | 1800s | `GLOBAL_SYMBOL_COOLDOWN_SECONDS` |
| Per-channel cooldown | 600s | `SCALP_SCAN_COOLDOWN` |
| Max correlated scalps | 4 | `MAX_CORRELATED_SCALP_SIGNALS` |
| Pairs scanned | 75 | `TOP50_FUTURES_COUNT` |
| ADX min SCALP | 20 | `ADX_MIN_SCALP` |
| ADX min FVG | 18 | `ADX_MIN_FVG` |
| Radar alert threshold | 65 | `RADAR_ALERT_MIN_CONFIDENCE` |
| Radar watching closely | 70 | `RADAR_ALERT_WATCHING_CLOSELY_CONFIDENCE` |
| Radar per-symbol cooldown | 900s | `RADAR_PER_SYMBOL_COOLDOWN_SECONDS` |
| Radar max per hour | 3 | `RADAR_MAX_PER_HOUR` |
| Silence breaker window | 3 hours | `SILENCE_BREAKER_HOURS` |
| GPT model | gpt-4o-mini | `CONTENT_GPT_MODEL` |
| Depth CB threshold | 3 timeouts/30s | `DEPTH_CIRCUIT_BREAKER_THRESHOLD` |
| Depth CB cooldown | 90s | `DEPTH_CIRCUIT_BREAKER_COOLDOWN` |
| WS degraded scan cap | 75 | `WS_DEGRADED_MAX_PAIRS` |

---

## 9. Active Channels

| Channel | Status | Purpose |
|---|---|---|
| `360_SCALP` | ✅ Active | Sweep reversals, range fades, whale momentum |
| `360_SCALP_FVG` | ✅ Active | Fair Value Gap retests |
| `360_SCALP_ORDERBLOCK` | ✅ Active | SMC order block bounces |
| `360_SCALP_DIVERGENCE` | ✅ Active | RSI/MACD divergence reversals |
| `360_SCALP_CVD` | 📡 Radar only | Free channel radar alerts (conf ≥ 65) |
| `360_SCALP_VWAP` | 📡 Radar only | Free channel radar alerts (conf ≥ 65) |
| `360_SCALP_SUPERTREND` | 📡 Radar only | Free channel radar alerts (conf ≥ 65) |
| `360_SCALP_ICHIMOKU` | 📡 Radar only | Free channel radar alerts (conf ≥ 65) |

To re-enable any as a live signal channel: set `CHANNEL_SCALP_CVD_ENABLED=true` in `.env`, restart engine.

---

## 10. Owner Notes (Running Log)

*Add decisions, ideas, and observations here as we work. Most recent at the top.*

**2026-04-07 (PR4)**
- Engine silence during April 7 crash exposed need for protective mode broadcaster
- Subscribers need interactive commands — not just signal posts
- PR4: protective mode broadcaster + full command revamp
- New subscriber commands: /market, /performance, /ask — all wired to live engine data
- Dead stubs removed, admin-only commands properly gated

**2026-04-07**
- Scan latency was 33–40s due to indicator recomputation on every cycle for every symbol (7,650 indicator calculations per cycle on 75 pairs × 6 TF × 17 indicators)
- Engine was capped at 50 pairs despite TOP50_FUTURES_COUNT=75 — WS_DEGRADED_MAX_PAIRS defaulted to 50 and spot WS partial degradation was triggering the cap every cycle
- PR3 merged: indicator cache + SMC dedup + pair cap fix + bookTicker timeout reduction
- Expected latency after fix: 8–12s per cycle

**2026-04-06**
- Copilot must always think as a business co-owner, not a code assistant
- Discussion must happen before any PR is created — this is now rule B14
- PR2 known issues identified: scheduled content routing, BTC price wiring, silence breaker awareness, radar score population
- Signal quality target set: 10–20/day (not 8–15)
- EOD wrap confirmed: 21:00 UTC

**Permanent reminders:**
- Signal quality > signal quantity. 10 clean signals beats 30 noisy ones.
- The free channel is a sales funnel. Every free post should make someone want to upgrade.
- The channel must never go silent. Silence breaker is non-negotiable.
- Every loss gets posted honestly. Transparency retains subscribers long-term.
- GPT writes the voice. Engine provides the numbers. Never let AI invent data.
- The system must feel like a professional analyst is watching 24/7. That is the product.
- We build the business, not just fix bugs. Every PR must move the business forward.