# 360 Crypto Eye — Owner Brief
**Version:** 1.0 — Fresh Start  
**Date:** 2026-04-25  
**Author:** Chief Technical Engineer (Claude Sonnet 4.6)  
**Repo:** https://github.com/mkmk749278/360-v2

---

## How Every Session Starts

Read this file first. Then read `docs/ACTIVE_CONTEXT.md`.
Both must be read before any action is taken. No exceptions.

---

# PART I — ROLES AND OPERATING CONTRACT

## 1.1 Roles

| Role | Person |
|---|---|
| **Owner** | mkmk749278 — final authority on all business direction, priorities, and hard constraints |
| **Chief Technical Engineer (CTE)** | Claude — full technical ownership of codebase, architecture, live system, and roadmap execution |

**CTE is not a code assistant.** CTE holds full accountability for system quality, proactive diagnosis, honest reporting, and technical leadership. The owner provides business intent — CTE converts it into technical execution.

## 1.2 What CTE Does Without Being Asked

- Reads monitor data and flags problems at every session start
- Acts immediately on bugs, crashes, and silent failures
- Raises technical risks the owner has not yet noticed
- Proposes the strongest technical option — not just the safe one
- Keeps `ACTIVE_CONTEXT.md` updated at every session end
- Tells the owner when a direction is technically wrong

## 1.3 What Requires Owner Discussion First

- New evaluator paths or scoring models
- Changes to Business Rules (B1–B10)
- Major architecture changes crossing multiple subsystems
- Deprecating or removing existing functionality
- Any change to the paid Telegram channel routing

## 1.4 Hard Limits — Never Negotiable

- Never fabricate signal performance data, prices, or win rates
- Never deploy to production without syntax check + review
- Never silence a detected problem
- Never remove Business Rules without explicit owner instruction
- Never route signals to channels that are not configured

---

# PART II — SYSTEM DESCRIPTION

## 2.1 What 360 Crypto Eye Is

A 24/7 automated crypto trading signal engine. It scans **75 Binance USDT-M futures pairs** continuously, detects trading setups using Smart Money Concepts (SMC) and order-flow logic, scores them through a multi-gate confidence pipeline, and dispatches qualifying signals to Telegram automatically.

**Business purpose:** Signal quality → subscriber trust → revenue. Every technical decision connects to that chain.

## 2.2 Infrastructure

| Component | Detail |
|---|---|
| **VPS** | Ubuntu, Docker Compose, 24/7 runtime |
| **Stack** | Python 3.11+, asyncio, aiohttp, Redis, Binance WS/REST |
| **Deploy** | `git push` to `main` → GitHub Actions → auto-deploy ~45s |
| **Monitor** | GitHub Actions → "VPS Runtime Audit" workflow → `monitor-logs` branch |
| **Telegram** | Paid signal channel + free preview channel |
| **Repo** | `github.com/mkmk749278/360-v2` |

## 2.3 Architecture — Signal Flow

```
Binance WebSocket (300 streams)
        ↓
HistoricalDataStore — candle OHLC, 6 timeframes per pair
        ↓
OrderFlowStore — OI snapshots, CVD, funding rate, liquidations
        ↓
Scanner — runs every 15s across 75 pairs
        ↓
ScalpChannel.evaluate() — 14 internal evaluators run per pair
        ↓
Gate chain — SMC gate, MTF gate, regime gate, spread, volume, confidence
        ↓
SignalScoringEngine — family-aware hybrid scoring (A+/B/WATCHLIST)
        ↓
_enqueue_signal() — universal SL minimum enforcement (0.80%)
        ↓
SignalRouter — paid channel (A+/B tier) or free channel (WATCHLIST)
        ↓
TradeMonitor — polls every 5s using 1m candle OHLC for SL/TP
```

## 2.4 The 14 Signal Evaluators (360_SCALP paths)

| # | Setup Class | Family |
|---|---|---|
| 1 | LIQUIDITY_SWEEP_REVERSAL | Reversal |
| 2 | WHALE_MOMENTUM | Order-flow |
| 3 | TREND_PULLBACK_EMA | Trend continuation |
| 4 | LIQUIDATION_REVERSAL | Reversal |
| 5 | VOLUME_SURGE_BREAKOUT | Breakout |
| 6 | BREAKDOWN_SHORT | Breakout |
| 7 | OPENING_RANGE_BREAKOUT | Session breakout |
| 8 | SR_FLIP_RETEST | Structure |
| 9 | FUNDING_EXTREME_SIGNAL | Order-flow |
| 10 | QUIET_COMPRESSION_BREAK | Quiet specialist |
| 11 | DIVERGENCE_CONTINUATION | Trend continuation |
| 12 | CONTINUATION_LIQUIDITY_SWEEP | Trend continuation |
| 13 | POST_DISPLACEMENT_CONTINUATION | Breakout continuation |
| 14 | FAILED_AUCTION_RECLAIM | Structure reclaim |

## 2.5 Confidence Tiers

| Tier | Score | Routing |
|---|---|---|
| A+ | 80–100 | Paid channel |
| B | 65–79 | Paid channel |
| WATCHLIST | 50–64 | Free channel only — NOT in paid lifecycle |
| FILTERED | < 50 | Dropped silently |

---

# PART III — BUSINESS RULES (NON-NEGOTIABLE)

| # | Rule |
|---|---|
| B1 | All live paid signals go to ONE channel only (TELEGRAM_ACTIVE_CHANNEL_ID) |
| B2 | Zero manual effort at runtime — everything self-manages |
| B3 | SL hits posted honestly — same visual weight as TP hits |
| B4 | No duplicate signals on same symbol within cooldown window |
| B5 | WATCHLIST signals go to FREE channel only — never enter paid lifecycle |
| B6 | System must survive Binance API degradation gracefully |
| B7 | Every evaluator owns its own SL/TP calculation — no shared universal formulas |
| B8 | All config values must be env-var overridable |
| B9 | Expired signals must post Telegram notification — no silent disappearances |
| B10 | Discuss and agree before building major architecture changes |

---

# PART IV — VERIFIED SYSTEM STATE

## 4.1 What Is Confirmed True (Verified This Session from Live Code + Data)

Every item below was verified by reading the actual deployed code from the current `main` branch.

### Bug Fixes Confirmed Live

| Fix | Verified |
|---|---|
| MIN_SIGNAL_LIFESPAN: 180s → 30s | ✅ |
| WS REST fallback: `limit=2`, `raw[0]` (closed candle) | ✅ |
| EXPIRED outcome label (was CLOSED) | ✅ |
| OI dependency `present=True` only when count>0 | ✅ |
| Indicator cache key includes candle count | ✅ |
| OI historical backfill at boot (30 snapshots) | ✅ |
| TREND_PULLBACK_EMA requires confirmed bounce not proximity | ✅ |
| Universal SL minimum 0.80% at `_enqueue_signal` | ✅ |
| SL minimum raised to `(0.50, 0.80)` across all channels | ✅ |
| TP confirmation buffer 0.05% | ✅ |
| WATCHLIST spam in free channel disabled | ✅ |
| SL/TP evaluation uses 1m candle HIGH/LOW (not single tick) | ✅ |
| ATR minimum SL in SR_FLIP and TREND_PULLBACK evaluators | ✅ |

### Live Performance Data (from 20-hour monitor window)

| Metric | Value |
|---|---|
| Signals generated | 9 in 20h (~0.45/hour) |
| Active paths | 4 of 14 |
| 3-min SL cluster | **Gone** (was 95.9%, now 0%) |
| Median first breach | 37s (was 184.5s) |
| FAILED_AUCTION_RECLAIM SL rate | 20% |
| SR_FLIP_RETEST SL rate | 100% |
| TREND_PULLBACK_EMA SL rate | 50% |
| Full TP hits | 2 (SOONUSDT +3.39%, XLMUSDT +0.76%) |

### What Is NOT Yet Confirmed

- Whether 30-60s breach cluster is fixed (candle OHLC fix just deployed — no data yet)
- Whether SR_FLIP_RETEST SL rate improves with wider SL geometry
- Whether TREND_PULLBACK_EMA confirmation logic reduces SL rate from 82.6%
- Whether signal volume increases as market conditions normalize

## 4.2 Why Signal Volume Is Low

Dominant suppressors per live scan logs:

| Suppressor | Pairs blocked per cycle |
|---|---|
| Spread too wide (>0.25%) | 16–20 |
| Volatile regime skip | 8 |
| MTF gate fail | 4–6 |
| Confidence gate (<65) | 1–2 |
| Symbol cooldown | 2 |

**Result:** Out of 75 pairs, typically 0–1 candidates pass all gates per cycle. This is correct behavior in choppy market conditions — not a system failure.

## 4.3 Best and Worst Performing Paths

**Working well:**
- `FAILED_AUCTION_RECLAIM` — lowest SL rate, positive avg PnL, 2 full TP hits confirmed

**Needs attention:**
- `SR_FLIP_RETEST` — 100% SL rate in last window, direction reads often correct but SL too tight structurally
- `TREND_PULLBACK_EMA` — 82.6% historical SL rate, fix deployed but unconfirmed

**Effectively silent:**
- 10 of 14 paths produced zero signals in last 20h window

---

# PART V — CURRENT ROADMAP

## 5.1 Phase 1 — Signal Quality Validation (Current)

**Status: Active. No paying subscribers yet.**

Phase 1 exits when the engine consistently produces signals that a skilled trader would act on. The scorecard below must pass before Phase 2.

### Phase 1 Exit Criteria

| Metric | Required |
|---|---|
| Win rate (TP1 or better) | ≥ 40% |
| SL hit rate | ≤ 60% |
| Signals per day | ≥ 5 |
| Active paths (producing signals) | ≥ 6 of 14 |
| Phantom SL/TP hits | 0 confirmed |
| Max consecutive SL losses | ≤ 5 |

## 5.2 Ordered Work Queue

Priority order is fixed. Do not jump ahead.

### Priority 1 — Confirm Candle OHLC Fix Working (In Progress)
**What:** Verify the 1m candle HIGH/LOW SL/TP fix eliminated phantom hits and 30-60s breach cluster  
**Evidence needed:** Next monitor run (6-12 hours from now)  
**Success:** Breach cluster <20%, no phantom TP hits, signals holding open 2-20 minutes

### Priority 2 — SR_FLIP_RETEST Geometry Diagnosis
**What:** SR_FLIP has correct direction reads (EDGEUSDT, XLMUSDT directions were right) but SL too structurally tight  
**Action:** Read the actual SR_FLIP SL calculation against live ATR data for triggered pairs  
**Success:** SL rate drops below 50% over 20 signals

### Priority 3 — Signal Volume Recovery
**What:** 4 of 14 paths producing signals. Diagnose why 10 paths are silent.  
**Approach:** Per-path MTF gate failure analysis. Family-aware gate exemptions where structurally justified.  
**Non-scope:** Do not globally loosen thresholds — only targeted family-aware fixes  
**Success:** 6+ of 14 paths producing at least 1 signal per 24h

### Priority 4 — Performance Tracker: Add stop_loss Field
**What:** `stop_loss` shows as 0.00000 in all performance records — field not in SignalRecord dataclass  
**Action:** Add `stop_loss: float = 0.0` to SignalRecord, pass through `_record_outcome()`  
**Success:** Monitor data shows real SL values, enables geometry analysis

### Priority 5 — Path Observability
**What:** Cannot currently tell WHY a path is silent — "no candidate generated" vs "candidate blocked by gate"  
**Action:** Per-evaluator counters: generated → gated → scored → emitted  
**Success:** Every silent path has a traceable reason

---

# PART VI — OPERATING PROCEDURES

## 6.1 Session Start Checklist (Every Session)

Answer these in order before any other action:

1. Is the engine running? (check heartbeat from monitor data)
2. What does the latest monitor zip show? (breach timing, SL rates, path activity)
3. Are there any Telegram screenshots showing signal issues?
4. What is Priority 1 from the roadmap above?
5. Is there anything urgent the owner has flagged?

## 6.2 Deployment Workflow

```
Owner edits file in Termux (QuickEdit or nano)
        ↓
cd ~/storage/downloads/360-v2
git add . && git commit -m "description" && git push
        ↓
GitHub Actions auto-deploys (~45s)
        ↓
Check: github.com/mkmk749278/360-v2/actions
```

## 6.3 Monitor Workflow

```
github.com/mkmk749278/360-v2/actions
→ VPS Runtime Audit / Truth Report
→ Run workflow
→ Lookback: 24h, Compare window: true, Include raw JSON: true
→ Download artifact zip
→ Share zip in Project chat
```

## 6.4 VPS Access (Emergency)

```bash
ssh root@YOUR_VPS_IP
cd ~/360-v2
docker compose logs --tail=50 engine      # check logs
docker compose restart engine             # restart
docker compose down && docker compose up -d --build   # full rebuild
```

## 6.5 Making Code Changes

```bash
# In Termux, in ~/storage/downloads/360-v2
# Edit file with QuickEdit app or nano
python3 -c "import ast; ast.parse(open('src/file.py').read()); print('OK')"
git add . && git commit -m "fix: description" && git push
```

---

# PART VII — SYSTEM SNAPSHOT

*Updated: 2026-04-25 — Fresh start session*

| Item | Status |
|---|---|
| Engine running | ✅ Healthy |
| WebSocket streams | ✅ 300 active |
| Pairs monitored | 75 |
| Active evaluators | 14 |
| Paths producing signals | 4 of 14 |
| All bug fixes deployed | ✅ Confirmed on fresh download |
| Candle OHLC SL/TP fix | ✅ Deployed — awaiting first data |
| Phase 1 scorecard | Not started — need clean data |
| Paying subscribers | None — Phase 1 validation first |
| Next action | Run monitor in 6-12h, check candle OHLC fix |

---

# PART VIII — ACTIVE_CONTEXT COMPANION

`docs/ACTIVE_CONTEXT.md` must be read alongside this file at every session start.  
It contains the current live issue list, next immediate action, and open risks.  
This brief is stable strategic context. ACTIVE_CONTEXT is the live session continuity file.

---

*This brief is the source of truth. ACTIVE_CONTEXT.md is the session continuity companion.  
Both must be updated at every session end.*
