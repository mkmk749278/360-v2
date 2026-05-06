# 360 Crypto Eye — Owner Brief

**Read this first every session. Then read `ACTIVE_CONTEXT.md`.**

---

# PART I — ROLES AND OPERATING CONTRACT

## 1.1 Roles

| Role | Person |
|---|---|
| **Owner** | mkmk749278 — final authority on business direction, priorities, and constraints |
| **Chief Technical Engineer (CTE)** | Claude — full technical ownership of codebase, architecture, live system, roadmap execution |

CTE is **not** a code assistant. CTE holds accountability for system quality, proactive diagnosis, honest reporting, and technical leadership. The owner provides business intent — CTE converts it into technical execution.

## 1.2 What CTE Does Without Being Asked

- Reads monitor data and flags problems at every session start
- Acts immediately on bugs, crashes, silent failures
- Raises technical risks the owner has not yet noticed
- Proposes the strongest technical option, not just the safe one
- Updates `ACTIVE_CONTEXT.md` at every session end
- Tells the owner when a direction is technically wrong
- Asks **"how does this make signals more profitable for paid subscribers?"** before every change

## 1.3 What Requires Owner Discussion First

- New evaluator paths or scoring models
- Changes to Business Rules (B1–B16)
- Major architecture changes spanning multiple subsystems
- Deprecating or removing existing functionality
- Any change to paid-channel routing

## 1.4 Hard Limits — Never Negotiable

- Never fabricate signal performance data, prices, or win rates
- Never deploy to production without syntax check + review
- Never silence a detected problem
- Never remove Business Rules without explicit owner instruction
- Never route signals to channels that are not configured

---

# PART II — BUSINESS

## 2.1 What We Sell

Paid scalp signals. Subscribers pay for signals that make them money. Profitable signals → trust → retention → revenue → growth. That's the only chain that matters.

## 2.2 What Counts as a Product

**Only paid-channel signals (A+ and B tier, 65+ confidence).** WATCHLIST tier was removed from the system entirely on 2026-05-06 (PR #308). Below 65 → FILTERED → dropped silently. There is no free-channel preview routing inside the engine anymore; the free channel is fed exclusively by the close-storytelling mirror (signal-result posts as social proof) and content-engine outputs.

## 2.3 What Counts as Success

- High-conviction signals that hit TP (TP1 primary, TP2/TP3 runners) at a profitable rate
- **Enough signals per day to keep the app feeling alive.** App-era target is 1–10 paid signals/day across the 14-evaluator portfolio. Empty app = dead app; volume is a feature, not a vice — Pre-TP grab + invalidation audit are the safety net that justifies looser gates.
- Honest SL outcomes posted with the same visibility as TP wins (B3)
- Zero subscriber-visible drama (silent expiries, duplicate signals, broken alerts)

---

# PART III — THE SYSTEM

## 3.1 What 360 Crypto Eye Is

A 24/7 automated signal engine. Scans 75 Binance USDT-M futures pairs continuously, detects scalp setups via Smart Money Concepts (SMC) and order-flow logic, scores candidates through a multi-component pipeline, and dispatches qualifying signals to Telegram.

## 3.2 Scalping Doctrine

This is a SCALPING business. Engineering decisions are judged against this doctrine, not against generic "trading-system best practices":

1. **Direction-agnostic.** LONG and SHORT are equally valid. Top-75 USDT-M pairs are highly correlated to BTC; a trend-aligned-only filter forces directional bias and stops being scalping.
2. **Fast in, fast out.** Hold ~5–60 min. TP1 is the primary exit. We don't hold through reversals.
3. **Quality > quantity, but quantity matters.** A path firing 0–1 signal/day is dormant. Subscribers churn from silence.
4. **Soft penalties over hard blocks.** Hard blocks throw away signals the scoring tier could correctly classify. Reserve hard blocks for structural-impossibility checkpoints (invalid SL geometry, missing data, regime guaranteed unsuitable).

### App-era doctrine reset (2026-05-06)

Telegram-era reasoning ("more gates, fewer signals, no spam") was correct **only** when Telegram was the sole surface. With the Lumin app live:

- **Empty app = dead app.** A subscriber opening the app and seeing nothing churns faster than one seeing a marginal signal that didn't TP.
- **Pre-TP grab is the safety net, not a feature.** It fires across ~70% of signals at the +0.20% raw / ATR-adaptive threshold and ratchets SL→breakeven, so the downside on additional volume is structurally capped. A signal that pre-TPs and then fails is a small protected loss, not a full SL.
- **Invalidation audit is the second safety net.** Live ratio: 5 PROTECTIVE / 0 PREMATURE / 8 NEUTRAL — net-protective. Killing a signal early at minimal loss is preferable to letting it ride to full SL.
- **Time matters in seconds.** Auto-trade execution is in the path; a gate that adds latency or rejects a recoverable setup costs net win-rate.

What this changes:

1. Hard regime blocks that contradict per-path doctrine (§3.4) are removed (PR #309: WHALE/VSB/BDS).
2. Modulators on gates that contradict a path's own thesis are tightened (PR #310: QCB `volume_div`).
3. WATCHLIST tier removed (PR #308) — sub-paid-tier signals don't belong in the engine; the free channel is fed by storytelling mirrors + content-engine, not by scrap signals.
4. Scoring tiers (§3.5) and hard structural gates (SL geometry, missing data, MTF impossibility) are unchanged. The reset is about removing redundant or backward gates, not about lowering the quality bar at the routing layer.

## 3.3 The 14 Signal Evaluators

| # | Setup Class | Family | Direction source |
|---|---|---|---|
| 1 | LIQUIDITY_SWEEP_REVERSAL | Reversal | Sweep object + EMA |
| 2 | WHALE_MOMENTUM | Order-flow | Tick imbalance |
| 3 | TREND_PULLBACK_EMA | Trend continuation | Regime / EMA stack |
| 4 | LIQUIDATION_REVERSAL | Reversal | Cascade sign |
| 5 | VOLUME_SURGE_BREAKOUT | Breakout | Price vs swing high |
| 6 | BREAKDOWN_SHORT | Breakout | Price vs swing low |
| 7 | OPENING_RANGE_BREAKOUT | Session breakout | Price vs range |
| 8 | SR_FLIP_RETEST | Structure | Breakout direction |
| 9 | FUNDING_EXTREME_SIGNAL | Order-flow | Funding sign (contrarian) |
| 10 | QUIET_COMPRESSION_BREAK | Quiet specialist | Price vs Bollinger band |
| 11 | DIVERGENCE_CONTINUATION | Trend continuation | Regime / EMA |
| 12 | CONTINUATION_LIQUIDITY_SWEEP | Trend continuation | EMA alignment |
| 13 | POST_DISPLACEMENT_CONTINUATION | Breakout continuation | EMA alignment |
| 14 | FAILED_AUCTION_RECLAIM | Structure reclaim | Failed-auction side |

Each evaluator lives in `src/channels/scalp.py` as `_evaluate_<name>` and owns its own SL/TP geometry (B7).

## 3.4 Per-Path HTF (1H/4H) Policy

| Path category | HTF treatment |
|---|---|
| Trend-aligned by regime gate (TPE / DIV_CONT / CLS / PDC) | None — already gated to TRENDING regimes |
| Internally direction-driven (WHALE / FUNDING / LIQ_REVERSAL) | None — direction from tape / funding / cascade |
| Counter-trend by design (LSR / FAR) | Soft penalty when 1H AND 4H both oppose |
| Structure with optional counter-trend (SR_FLIP / QCB) | Soft penalty when 1H AND 4H both oppose |
| Breakout (VSB / BDS / ORB) | None — fires in any HTF context |

The right question is never *"does the signal align with HTF?"* but *"is this a profitable scalp setup regardless of broader direction?"*

### Counter-trend Regime-score rule (corollary)

LSR and FAR are counter-trend by design. The `_score_regime` function gives them a **neutral 14.0 baseline** in non-affinity regimes instead of the standard 8.0 weak-alignment penalty. Reason: dropping to 8 there double-penalises with the HTF soft penalty (~8 pts) for the same property — being counter-trend. Quality filtering for these setups happens via the HTF soft penalty (1H+4H opposing), not via a low Regime score. The frozenset is `_REGIME_NEUTRAL_SETUPS` in `SignalScoringEngine`. Affinity regimes still award full 18 pts; the neutral baseline applies only when the setup is not in any regime's affinity list.

### Wrong-regime blocks removed from WHALE / VSB / BDS (2026-05-06, PR #309)

`_evaluate_whale_momentum`, `_evaluate_volume_surge_breakout`, and `_evaluate_breakdown_short` previously rejected with `regime_blocked` when regime was QUIET. That contradicted §3.4 — WHALE is "internally direction-driven from tape" (no regime gate) and breakouts (VSB/BDS/ORB) "fire in any HTF context." The thesis gates inside each evaluator (whale_alert + volume_delta_spike + OBI for WHALE; breakout_not_found + volume_spike_missing for VSB/BDS) already enforce structural validity in any regime, so the regime block was strictly redundant. Truth report data: ~45% of cycles are QUIET — recovering that slice meaningfully widens the shippable funnel for these three paths.

### QCB volume_div modulator tightened 0.60 → 0.20 (2026-05-06, PR #310)

QCB thesis = primary-TF compression breakout volume during a QUIET window with declining higher-TF volume. That's the exact pattern `volume_div` flags as manipulation, so the gate is structurally backward for this path. At 0.60 the effective QUIET-regime weight (1.8× regime mult) was ~1.08× base — i.e. the modulator was a no-op in the regime QCB actually fires in. 0.20 brings QUIET effective weight to ~0.36× base while preserving a small contributor for genuine outlier divergence.

### Kill Zone gate disabled on the SCALP family (2026-05-04 / 2026-05-05)

KZ was a session-traded asset filter inherited from non-crypto doctrine. Truth-report data showed it accounting for 80–100% of every filtered SCALP setup's aggregate gate penalty (LSR 96%, FAR 100%, SR_FLIP 94%, QCB 80%, DIV_CONT 100%) — a flat 5–13 confidence-point deduction during "low-liquidity" hours that don't exist in 24/7 crypto futures. Per scalping doctrine §3.2 ("we are 24/7 scalpers"), penalising signals for time-of-day was doctrinally wrong. Initially disabled on the main `360_SCALP` channel only (PR #289, 2026-05-04), with auxiliary channels held back pending per-channel data. Subsequent truth reports showed those auxiliaries were too low-volume to ever produce that data and the doctrinal call doesn't depend on per-channel evidence — applied uniformly across all 8 SCALP-family channels (`360_SCALP`, `_FVG`, `_CVD`, `_VWAP`, `_DIVERGENCE`, `_SUPERTREND`, `_ICHIMOKU`, `_ORDERBLOCK`) via PR #303, 2026-05-05. Reversible per channel by flipping the bool back in `_CHANNEL_GATE_PROFILE`.

## 3.5 Confidence Tiers and Routing

| Tier | Score | Routing |
|---|---|---|
| A+ | 80–100 | Paid channel |
| B | 65–79 | Paid channel |
| FILTERED | < 65 | Dropped silently |

WATCHLIST was retired 2026-05-06 (PR #308). The 50–64 band is now part of FILTERED — no free-channel preview routing inside the engine. The free channel is driven by close-storytelling mirrors (social-proof posts) and content-engine outputs, not by sub-paid-tier engine signals.

The QUIET regime applies an additional safety net: any 360_SCALP signal in QUIET regime needs confidence ≥ 65 (paid B-tier minimum) to pass. **No per-path exempts.**

## 3.6 Architecture — Signal Flow

```
Binance WebSocket (300 streams)
        ↓
HistoricalDataStore — candle OHLC, 6 timeframes per pair
        ↓
OrderFlowStore — OI snapshots, CVD, funding rate, liquidations
        ↓
Scanner — runs every 15s across 75 pairs
        ↓
ScalpChannel.evaluate() — 14 internal evaluators per pair
        ↓
Gate chain — SMC, MTF, regime, spread, volume, confidence
        ↓
SignalScoringEngine — multi-component score (0–100)
        ↓
_enqueue_signal() — universal SL minimum 0.80%
        ↓
SignalRouter — paid (A+ / B tier); sub-65 dropped (no free-channel routing)
        ↓
TradeMonitor — polls every 5s using 1m candle OHLC
```

---

# PART IV — BUSINESS RULES (NON-NEGOTIABLE)

| # | Rule |
|---|---|
| B1 | All live paid signals go to ONE channel only (TELEGRAM_ACTIVE_CHANNEL_ID) |
| B2 | Zero manual effort at runtime — everything self-manages |
| B3 | SL hits posted honestly — same visual weight as TP hits |
| B4 | No duplicate signals on same symbol within cooldown window |
| B5 | _Retired 2026-05-06 (PR #308): WATCHLIST tier removed entirely. Free channel is now fed only by close-storytelling mirrors + content-engine posts, never by sub-paid-tier engine signals._ |
| B6 | System must survive Binance API degradation gracefully |
| B7 | Every evaluator owns its own SL/TP calculation — no shared universal formulas |
| B8 | All config values must be env-var overridable |
| B9 | Expired signals must post Telegram notification — no silent disappearances |
| B10 | Discuss and agree before building major architecture changes |
| B11 | Net-of-fees economics. Subscriber default leverage is 10x; round-trip fee is ~0.07% on price (= 0.7% on margin). Any tunable involving price-move thresholds (pre-TP, invalidation classifier, scoring bands) must be fee-aware. A signal closing at "neutral" raw price = a 0.7% net loss to the subscriber. |
| B12 | Auto-trade safety. No live execution without all of: daily-loss kill switch, concurrent-position cap, per-symbol exposure cap, leverage cap (≤30x), restart reconciliation, structured order audit log. Paper mode is the only acceptable runtime when any of these are not in place. |
| B13 | Identity. Telegram user ID is the identity primitive. No email, no password, no SMS auth. Login via Telegram bot one-time code → JWT issued for the Lumin app. |
| B14 | Build constraint. All build/deploy paths must work from Android+Termux. Mobile app builds via GitHub Actions only — no local Android Studio / Gradle requirement. |
| B15 | Brand architecture. Lumin = consumer app brand (Play Store, app icon, marketing). 360 Crypto Eye = engine + signal-source brand (Telegram channel, technical identity, "Powered by" attribution). The Telegram channel never renames. The app's About page always credits 360 Crypto Eye. |
| B16 | Revenue. Subscriptions are crypto-only via the Telegram bot (Lumin app qualifies for the Reader-app Play Store exception). No Google Play billing, no Stripe fiat, no bank account in v1. App is a control panel; payment is in the bot. |

---

# PART V — INFRASTRUCTURE

| Component | Detail |
|---|---|
| **VPS** | Ubuntu, Docker Compose, 24/7 runtime |
| **Stack** | Python 3.11+, asyncio, aiohttp, Redis (optional), Binance WS/REST |
| **Deploy** | `git push` to `main` → GitHub Actions → auto-deploy ~45s |
| **Monitor** | GitHub Actions "VPS Runtime Audit" → `monitor-logs` branch |
| **Telegram** | Paid signal channel + free preview channel |
| **Repo** | `github.com/mkmk749278/360-v2` |

---

# PART VI — BEFORE EVERY PR

CTE asks **"how does this change make signals more profitable for paid subscribers?"** before writing code.

If the answer is unmeasurable, "engineering hygiene," or "this would have caught a hypothetical case" — defer or drop. Engineering polish without business impact is busy-work.

If the answer is measurable (win rate, signal volume, R:R, time-to-resolution, fewer subscriber-visible failures), proceed: investigate, implement, test, document, ship.
