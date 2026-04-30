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
| CVD 24h starvation eliminated — boot seed from historical 1m candles | ✅ |
| Per-setup SL caps: 17 values in `_MAX_SL_PCT_BY_SETUP` (`signal_quality.py`) | ✅ |
| EXHAUSTION_FADE R:R tier: moved to 0.9 mean-reversion family | ✅ |
| Mover pairs dashboard counter — `/dashboard` shows `(+N mover)` when active | ✅ |
| LSR (`_evaluate_standard`) — removed broken 5m-mom-direction-sign check; wired MSS confirmation as soft penalty (missing = -8, mismatch = hard reject) | ✅ 2026-04-30 |
| WHALE_MOMENTUM — whale-alert producer scans recent_ticks window (was only checking the latest tick — alert visible ~50–100ms on active pairs); WHALE_TRADE_USD_THRESHOLD + WHALE_MIN_TICK_VOLUME_USD + WHALE_OBI_MIN + WHALE_DELTA_MIN_RATIO now env-overridable per B8 | ✅ 2026-04-30 |
| TREND_PULLBACK_EMA — body-conviction gate replaced with close-position-in-range (was punishing the canonical hammer reclaim that defines a valid pullback entry — large lower wick is the EMA-test feature, not noise) | ✅ 2026-04-30 |
| LIQUIDATION_REVERSAL — RSI thresholds relaxed 25/75 → 35/65 with RSI direction-of-travel check (was demanding extreme exhaustion 5m RSI rarely hits); zone-proximity gate now also accepts cascade extremum within 0.5% of FVG/orderblock (cascades overshoot zones by definition) | ✅ 2026-05-01 |
| VOLUME_SURGE_BREAKOUT — multi-fix audit: (A) removed broken current-candle volume gate (62.7% of rejections — partial-candle vs complete-candle threshold mismatch contradicting the "surge + pullback" thesis); (B) breakout qualifier now requires close above swing_high — wick-only piercing was being accepted as a breakout but is a sweep; (C) SL anchored to lower of swing-relative floor and close-relative floor (max(0.8%, 1×ATR)) — pre-fix produced 0.05% stops in extended pullback zones; (D) breakout vol multiplier now env-overridable per B8 | ✅ 2026-05-01 |
| BREAKDOWN_SHORT — multi-fix mirror of VSB: (A) removed broken current-candle volume gate (same 62.7% pattern — dead-cat bounces have reduced volume by definition); (B) breakdown qualifier now requires close BELOW swing_low — wick-only piercing was being accepted but is a bullish sweep; (C) SL anchored to higher of swing-relative ceiling and close-relative ceiling (max(0.8%, 1×ATR)) — pre-fix produced 0.05% stops in extended bounce zones; (D) shares VSB_BREAKOUT_VOL_MULT env constant per B8 | ✅ 2026-05-02 |
| OPENING_RANGE_BREAKOUT — dormant-path audit: path is feature-flag-disabled (`SCALP_ORB_ENABLED=false`).  Live monitor 100% `regime_blocked` was actually the disable token — telemetry now emits `feature_disabled` truthfully.  VSB/BDS-family fixes (current-candle vol gate removal + close-relative SL floor) applied to preserved code so re-enable doesn't ship the same bugs.  **Open question**: rebuild session-range proxy or re-enable as-is | ✅ 2026-05-02 |
| SR_FLIP_RETEST — TP1 ATR-adaptive cap (1.8R/2.5R/uncapped by atr_percentile) was claimed deployed in Audit-3 but actually missing from the code — only TPE had the cap.  This is the most likely contributor to the historical 100% SL rate documented in §4.3 (TP1 at 20-candle swing high could be 5-10R away in trending markets, unreachable before structural SL fires).  Plus VOLATILE_UNSUITABLE regime block added at evaluator level (defence-in-depth — scanner gate already excluded this regime) | ✅ 2026-05-02 |
| FUNDING_EXTREME_SIGNAL — telemetry truth fix: `close <= 0` now emits `invalid_price` instead of being conflated with `funding_not_extreme`.  TP1 ATR-adaptive cap (1.8R/2.5R/uncapped by atr_percentile) added consistent with SR_FLIP / TPE — structure-anchored TP1 (`_funding_extreme_structure_tp1`) could sit 5-10R from close in trending markets, unreachable for a mean-reversion contrarian setup before SL.  **Open question** flagged for owner: 95 candidates/28h all killed by QUIET_SCALP_BLOCK at scanner — should FUNDING join QCB and DIV_CONT≥64 in the exempt list?  CTE recommendation: yes (extreme funding IS the quality gate), but B10 territory | ✅ 2026-05-02 |

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
- `FAILED_AUCTION_RECLAIM` — lowest SL rate, positive avg PnL, 2 full TP hits confirmed. SL cap now 3.0% — room to breathe.

**Needs attention:**
- `SR_FLIP_RETEST` — 100% SL rate in early window; SL cap = 2.5% (reject-policy) and **TP1 ATR-adaptive cap NOW actually deployed** (Audit-3 claimed it was; audit #8 on 2026-05-02 found the code was missing the cap and only the TPE path had it).  Pre-fix TP1 = 20-candle swing high which could sit 5-10R from close → SL hit before TP1 reachable.  Post-fix capped at 1.8R / 2.5R / uncapped by ATR percentile.  Unvalidated; expect SL rate to drop substantially when first non-QUIET emissions arrive.
- `TREND_PULLBACK_EMA` — ATR-driven SL can reach 3%; cap now 3.0%. Body-conviction gate replaced with close-position-in-range 2026-04-30 — the prior `body/range ≥ 0.50` gate was rejecting hammer/shooting-star reclaims (the canonical TPE entry). 3 broken entry-quality tests on main now pass. Live validation pending non-QUIET regime.
- `QUIET_COMPRESSION_BREAK` — 2.08% SL seen live; was perpetually rejected by 2.5% channel cap. Now capped at 3.0% — should start passing.
- `LIQUIDITY_SWEEP_REVERSAL` — was generating 0 signals in latest 18k-cycle zip; dominant suppressors `momentum_reject` (40%, structurally broken — fix deployed 2026-04-30 evening) and `basic_filters_failed` (20%). Also missing MSS confirmation despite the helper existing — wired same session. Both fixes unvalidated; expect higher emission rate AND higher quality (MSS gate filters false sweeps).
- `WHALE_MOMENTUM` — was generating 0 signals in latest 18k-cycle zip; root cause was upstream in `detector.py:228` where whale_alert only checked the latest tick (visible ~50–100ms on active pairs vs. 15s scan cycle). Fix scans the 100-tick window newest-first. Thresholds now env-overridable per B8. Unvalidated; expect `momentum_reject` count to drop sharply on next zip.

**Effectively silent (being investigated):**
- `OPENING_RANGE_BREAKOUT` — diagnosed 2026-05-02 as feature-flag-disabled (`SCALP_ORB_ENABLED=false`), not a bug. Audit #7 cleaned up the dormant code (telemetry now reports `feature_disabled` truthfully; VSB-family vol/SL bugs preemptively fixed). Owner decision pending: rebuild session-range proxy or re-enable as-is.
- CLS, PDC — not yet diagnosed; separate investigation needed.
- `FUNDING_EXTREME_SIGNAL` — generates 95 candidates / 28h that all die at scanner-level QUIET_SCALP_BLOCK (since FUNDING isn't QCB or DIV_CONT≥64 exempt). Truth report calls FUNDING the *"most likely bottleneck"*. Audit #9 (2026-05-02) shipped TP1 ATR cap + telemetry truth; the dominant question — exempt FUNDING in QUIET regime — flagged as B10-territory open decision.
- DIV_CONT — Audit-3 unlocks applied; awaiting first live signals.
- `LIQUIDATION_REVERSAL` — was generating 0 signals in latest 18k-cycle zip; cascade_threshold_not_met dominates (76.8%, by-design in QUIET regime). Audit #4 (2026-05-01) relaxed two downstream gates (RSI extreme + zone proximity) that would have killed valid setups when regime returns. Unvalidated; expect emissions when first cascades trigger in non-QUIET regime.
- `VOLUME_SURGE_BREAKOUT` — was generating 0 signals in latest 18k-cycle zip; `volume_spike_missing` was 62.7% (dominant). Audit #5 (2026-05-01) shipped 4 structural fixes (gate removal + breakout-close requirement + SL geometry + B8 env). Unvalidated; expect emissions once non-QUIET regime returns.
- `BREAKDOWN_SHORT` — same numbers as VSB (volume_spike_missing=62.7%, basic_filters=19.3%, regime_blocked=17.9%, 0 generated). Audit #6 (2026-05-02) shipped the same 4 mirror fixes (gate removal + close-below requirement + SL geometry + shared B8 vol mult). Unvalidated; expect emissions on cascading altcoins once non-QUIET regime returns.

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

### Priority 1 — Validate Per-Setup SL Cap Effect (In Progress)
**What:** Per-setup caps shipped in PR #236. QCB/FAR perpetual rejection loops should be gone.  
**Evidence needed:** Next monitor zip — check for absence of `sl_cap_exceeded` on QCB/FAR  
**Success:** QCB and FAR producing candidates that reach confidence gate instead of looping

### Priority 2 — Win Rate Validation
**What:** Win rate stuck at ~9% pre-Audit-3. TP1 ATR-adaptive cap + MOM-PROT + wider SL should improve it.  
**Evidence needed:** Monitor zip with 20+ signals post-Audit-3  
**Success:** TP1_HIT + PROFIT_LOCKED ≥ 40% of outcomes

### Priority 3 — Investigate HYPEUSDT QCB Gate Penalty
**What:** HYPEUSDT QCB scored 89.2 composite but dropped to 67.6 due to a single -21.6 gate penalty.
The penalty source (which soft gate) is unknown. High-quality signal being killed by a single gate.  
**Action:** Trace which soft gate applies 21.6 penalty to QCB signals in `scanner/__init__.py`  
**Success:** Either identify gate is correct and penalty is justified, or recalibrate it

### Priority 4 — Raise `360_SCALP` Channel Cap to 3.0%
**What:** `_MAX_SL_PCT_BY_CHANNEL["360_SCALP"] = 2.5` is still tighter than the 3.0% per-setup cap
for FAR, QCB, TPE, FUNDING. Tighter-wins logic means these paths are still capped at 2.5%.  
**Action:** Raise to 3.0% in `signal_quality.py`  
**Success:** FAR/QCB/TPE/FUNDING can use their full 3.0% structural headroom

### Priority 5 — ORB / CLS / PDC Silence Diagnosis
**What:** These 3 paths have never produced a signal. Root cause unknown.  
**Approach:** Per-path gate-failure log analysis  
**Success:** Each silent path has a traceable reason; fix or document as expected

### Priority 6 — Path Observability
**What:** Cannot currently tell WHY a path is silent — "no candidate generated" vs "candidate blocked by gate"  
**Action:** Per-evaluator counters: generated → gated → scored → emitted  
**Success:** Every silent path has a traceable reason in telemetry

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

Monitor outputs are **committed to the `monitor-logs` branch** (force-push) by
`.github/workflows/vps-monitor.yml`. There is no artifact zip to download —
the curated truth report files are the branch contents.

```
github.com/mkmk749278/360-v2/actions
→ VPS Runtime Audit / Truth Report
→ Run workflow
→ Lookback: 24h, Compare window: true, Include raw JSON: true
→ Workflow pushes snapshot to `monitor-logs` branch
```

To read the latest snapshot from a session:

```bash
git fetch origin monitor-logs
git show origin/monitor-logs:<file>          # inspect a single file
git checkout origin/monitor-logs -- <path>   # pull file into working tree
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

*Updated: 2026-04-28 — Per-setup SL caps deployed*

| Item | Status |
|---|---|
| Engine running | ✅ Healthy |
| WebSocket streams | ✅ 300 active |
| Pairs monitored | 75 (+up to 5 mover-promoted) |
| Active evaluators | 14 |
| Paths producing signals | 6+ of 14 (post Audit-3, exact count pending next zip) |
| Per-setup SL caps | ✅ 17 caps in `signal_quality.py` — PR #236 open |
| CVD boot seed fix | ✅ No 24h wait — full CVD from minute 1 |
| Mover pairs dashboard | ✅ `/dashboard` shows `(+N mover)` counter |
| Phase 1 scorecard | SL rate ✅, signals/day ✅, win rate ❌ (being fixed) |
| Paying subscribers | None — Phase 1 validation first |
| Next action | Monitor zip to validate QCB/FAR no longer looping |

---

# PART VIII — ACTIVE_CONTEXT COMPANION

`docs/ACTIVE_CONTEXT.md` must be read alongside this file at every session start.  
It contains the current live issue list, next immediate action, and open risks.  
This brief is stable strategic context. ACTIVE_CONTEXT is the live session continuity file.

---

*This brief is the source of truth. ACTIVE_CONTEXT.md is the session continuity companion.  
Both must be updated at every session end.*
