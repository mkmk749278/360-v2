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

**Only paid-channel signals (A+ and B tier, 65+ confidence).** Watchlist-tier signals (50–64) routed to the free channel are scrap from a revenue standpoint and are not a goal. Don't optimize for them.

## 2.3 What Counts as Success

- High-conviction signals that hit TP (TP1 primary, TP2/TP3 runners) at a profitable rate
- Enough signals per day to keep subscribers engaged (target 1–10 paid signals/day across the 14-evaluator portfolio)
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

### Kill Zone gate disabled on the SCALP family (2026-05-04 / 2026-05-05)

KZ was a session-traded asset filter inherited from non-crypto doctrine. Truth-report data showed it accounting for 80–100% of every filtered SCALP setup's aggregate gate penalty (LSR 96%, FAR 100%, SR_FLIP 94%, QCB 80%, DIV_CONT 100%) — a flat 5–13 confidence-point deduction during "low-liquidity" hours that don't exist in 24/7 crypto futures. Per scalping doctrine §3.2 ("we are 24/7 scalpers"), penalising signals for time-of-day was doctrinally wrong. Initially disabled on the main `360_SCALP` channel only (PR #289, 2026-05-04), with auxiliary channels held back pending per-channel data. Subsequent truth reports showed those auxiliaries were too low-volume to ever produce that data and the doctrinal call doesn't depend on per-channel evidence — applied uniformly across all 8 SCALP-family channels (`360_SCALP`, `_FVG`, `_CVD`, `_VWAP`, `_DIVERGENCE`, `_SUPERTREND`, `_ICHIMOKU`, `_ORDERBLOCK`) via PR #303, 2026-05-05. Reversible per channel by flipping the bool back in `_CHANNEL_GATE_PROFILE`.

## 3.5 Confidence Tiers and Routing

| Tier | Score | Routing |
|---|---|---|
| A+ | 80–100 | Paid channel |
| B | 65–79 | Paid channel |
| WATCHLIST | 50–64 | Free channel only — scrap from a revenue standpoint |
| FILTERED | < 50 | Dropped silently |

The QUIET regime applies an additional safety net: any 360_SCALP signal in QUIET regime needs confidence ≥ 65 (paid B-tier minimum) to pass. **No per-path exempts** — sub-65 in QUIET is scrap routing and is filtered.

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
SignalRouter — paid (A+ / B tier) or free (WATCHLIST)
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
| B5 | WATCHLIST signals go to FREE channel only — never enter paid lifecycle |
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
