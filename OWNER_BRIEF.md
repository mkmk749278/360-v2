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
- Never push to `main` directly or bypass the PR workflow (see `CLAUDE.md § Change-management protocol`)

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

For deep diagnostic access — truth-report viewing, per-signal confidence decomposition, geometry-vs-reality dumps, invalidation classifications — a separate web ops console (**360 CE Ops**, repo `github.com/mkmk749278/360ce-ops`) is in design. See `docs/360CE_OPS_PLAN.md`. Until that ships, diagnostics are accessed via SSH + the `scripts/diag_*` scripts + the `monitor-logs` branch directly.

## 3.2 Scalping Doctrine

This is a SCALPING business. Engineering decisions are judged against this doctrine, not against generic "trading-system best practices":

1. **Direction-agnostic.** LONG and SHORT are equally valid. Top-75 USDT-M pairs are highly correlated to BTC; a trend-aligned-only filter forces directional bias and stops being scalping.
2. **Pre-TP is the primary exit. TP1 is the bonus tail.** Most signals partially close at the pre-TP threshold, banking real profit on a user-chosen fraction (minimum 30%, see B17). The residual rides toward TP1 with SL ratcheted to breakeven and tight thesis-broken invalidation. Hold ~5–60 min. We don't hold through reversals.
3. **Quality > quantity, but quantity matters.** A path firing 0–1 signal/day is dormant. App users churn from silence.
4. **Soft penalties over hard blocks.** Hard blocks throw away signals the scoring tier could correctly classify. Reserve hard blocks for structural-impossibility checkpoints (invalid SL geometry, missing data, regime guaranteed unsuitable).

### 3.2a Capital Preservation Doctrine (2026-05-17)

**Protecting capital outranks chasing TPs.** A full SL hit costs subscribers ~7.9% on margin at 10×; a small banked partial + breakeven exit costs ~−0.5% even if the residual flatlines. The asymmetry is decisive: 10 small breakevens cost less than one full SL.

Consequences for engineering:
- **Pre-TP fires real partial close** (not a "moved SL to entry" Telegram message dressed as a fill — that was the pre-2026-05-17 mechanism, see ACTIVE_CONTEXT for the audit). When threshold hits, broker actually closes the user-configured fraction at market. The residual position then has SL at entry; the realised partial is locked in.
- **Invalidation must prefer early thesis-broken exit over riding to full SL.** Tight mode adds an ATR-trailing kill at MFE ≥ 0.3R (close at 50% retracement of MFE peak). Loose / Standard / Tight is a per-user setting (see B17); engine default is Standard.
- **The unique product position:** instead of "one-shot TP/SL signals," we give users small high-frequency banked wins with low downside variance. They control the partial-close fraction and the invalidation aggressiveness per-user. No other Telegram-channel signal provider can replicate that surface.

### App-era doctrine reset (2026-05-06)

Telegram-era reasoning ("more gates, fewer signals, no spam") was correct **only** when Telegram was the sole surface. With the Lumin app live:

- **Empty app = dead app.** A subscriber opening the app and seeing nothing churns faster than one seeing a marginal signal that didn't TP.
- **Pre-TP grab** — see §3.2 #2 + §3.2a above for the post-2026-05-17 doctrine. Pre-2026-05-17 the line read "the safety net, not a feature"; the new doctrine inverts that — pre-TP IS the product mechanism.
- **Invalidation audit is the structural safety net behind tight-mode trailing.** Live ratio (24h window): PROTECTIVE 56.7% / PREMATURE 7.5% / NEUTRAL 35% — net-protective on the audit's threshold, but per-signal data (see ACTIVE_CONTEXT) shows ~9% of invalidations kill signals with MFE ≥ 0.5R. The post-2026-05-17 fix: MFE-protection rule on momentum-loss kills (no kill when `pre_tp_hit=True` and price between entry and MFE peak).
- **Time matters in seconds.** Auto-trade execution is in the path; a gate that adds latency or rejects a recoverable setup costs net win-rate.

What this changes:

1. Hard regime blocks that contradict per-path doctrine (§3.4) are removed (PR #309: WHALE/VSB/BDS).
2. Modulators on gates that contradict a path's own thesis are tightened (PR #310: QCB `volume_div`).
3. WATCHLIST tier removed (PR #308) — sub-paid-tier signals don't belong in the engine; the free channel is fed by storytelling mirrors + content-engine, not by scrap signals.
4. Scoring tiers (§3.5) and hard structural gates (SL geometry, missing data, MTF impossibility) are unchanged. The reset is about removing redundant or backward gates, not about lowering the quality bar at the routing layer.

## 3.3 The 15 Signal Evaluators

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
| 15 | MA_CROSS_TREND_SHIFT | Discrete trend-shift event | EMA50/200 4h or EMA21/50 1h crossover |

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

## 3.4a Structure Detection Doctrine — "HTF Structure, LTF Entry" (2026-05-17)

**HTF (1H/4H) identifies the structure — the level, the trend, the divergence, the auction failure. LTF (5m) refines the entry timing only.**

A 5m candle never identifies structure. It identifies *when* to enter the structure already identified at HTF. Any evaluator that reads structural meaning from a 5m candle is misusing 5m — that's noise interpreted as signal. This doctrine is the missing piece that explains why §3.4 alone wasn't sufficient: §3.4 dictates *what HTF treatment each path category gets*; this section dictates *where each evaluator must source its structure detection*.

| Concern | Detect on | Confirm on | Enter on |
|---|---|---|---|
| Swing levels (S/R, role-flip references) | 1H/4h LevelBook pivots + VP zones | 1H close acceptance / rejection | 5m retest candle |
| Trend (TPE / DIV_CONT pullback continuation) | 1H EMA21/50 slope + structure state | 1H pullback to EMA21 within ATR | 5m EMA9 reclaim + momentum candle |
| Divergences (CVD-div) | 15m aggregated CVD bars | 15m hidden-divergence detection | 5m FVG fill in divergence window |
| Failed auctions / swing failures | 1H struct level | 1H probe-and-reclaim | 5m reclaim candle |
| BB compression | 15m bands (width < 1.5% of close) | 15m squeeze persistence ≥ 3 bars | 5m breakout candle with volume |
| Liquidity sweeps (LSR) | SMC sweep at LevelBook entry (ATR×2 of CLUSTERED/VP_ANCHORED level) | 5m MSS in sweep direction | 5m post-sweep candle |
| Order blocks / FVGs | Consume at HTF | — | Refine entry at 5m |

**Exception — tape-driven and event-driven paths.** WHALE / LIQUIDATION_REVERSAL / FUNDING_EXTREME are direction-driven by realtime order flow (tick imbalance, cascade detection, funding-rate extremes). These are LTF-by-design and the doctrine doesn't apply — they read structure from the tape, not from candle structure.

**Existing infrastructure that implements this doctrine** (per §3.5): `src/level_book.py`, `src/structure_state.py`, `src/volume_profile.py`, and the `_classify_htf_trend(indicators, candles, "1h"/"4h")` helper. The doctrine makes consumption of these mandatory for structure detection, not optional.

**Why this doctrine was needed:** truth-report data (2026-04-21 → 2026-05-17, 654 closed signals) showed direction-call quality (MFE=0 rate, i.e., engine called direction and price never moved that way) was 39–78% on every non-LSR emitting path. LSR — the only path with HTF-anchored detection (SMC sweep) — had 24% MFE=0, the best in the portfolio. The other paths were detecting "structure" inside 5m noise windows (e.g., SR_FLIP using 41 5m candles for a "swing level" = 3.4 hours of local extremes, not a structural level). Forensic in `ACTIVE_CONTEXT.md § In-session checkpoint 2026-05-17`.

### Counter-trend Regime-score rule (corollary)

LSR and FAR are counter-trend by design. The `_score_regime` function gives them a **neutral 14.0 baseline** in non-affinity regimes instead of the standard 8.0 weak-alignment penalty. Reason: dropping to 8 there double-penalises with the HTF soft penalty (~8 pts) for the same property — being counter-trend. Quality filtering for these setups happens via the HTF soft penalty (1H+4H opposing), not via a low Regime score. The frozenset is `_REGIME_NEUTRAL_SETUPS` in `SignalScoringEngine`. Affinity regimes still award full 18 pts; the neutral baseline applies only when the setup is not in any regime's affinity list.

### Wrong-regime blocks removed from WHALE / VSB / BDS (2026-05-06, PR #309)

`_evaluate_whale_momentum`, `_evaluate_volume_surge_breakout`, and `_evaluate_breakdown_short` previously rejected with `regime_blocked` when regime was QUIET. That contradicted §3.4 — WHALE is "internally direction-driven from tape" (no regime gate) and breakouts (VSB/BDS/ORB) "fire in any HTF context." The thesis gates inside each evaluator (whale_alert + volume_delta_spike + OBI for WHALE; breakout_not_found + volume_spike_missing for VSB/BDS) already enforce structural validity in any regime, so the regime block was strictly redundant. Truth report data: ~45% of cycles are QUIET — recovering that slice meaningfully widens the shippable funnel for these three paths.

### QCB volume_div modulator tightened 0.60 → 0.20 (2026-05-06, PR #310)

QCB thesis = primary-TF compression breakout volume during a QUIET window with declining higher-TF volume. That's the exact pattern `volume_div` flags as manipulation, so the gate is structurally backward for this path. At 0.60 the effective QUIET-regime weight (1.8× regime mult) was ~1.08× base — i.e. the modulator was a no-op in the regime QCB actually fires in. 0.20 brings QUIET effective weight to ~0.36× base while preserving a small contributor for genuine outlier divergence.

### Kill Zone gate disabled on the SCALP family (2026-05-04 / 2026-05-05)

KZ was a session-traded asset filter inherited from non-crypto doctrine. Truth-report data showed it accounting for 80–100% of every filtered SCALP setup's aggregate gate penalty (LSR 96%, FAR 100%, SR_FLIP 94%, QCB 80%, DIV_CONT 100%) — a flat 5–13 confidence-point deduction during "low-liquidity" hours that don't exist in 24/7 crypto futures. Per scalping doctrine §3.2 ("we are 24/7 scalpers"), penalising signals for time-of-day was doctrinally wrong. Initially disabled on the main `360_SCALP` channel only (PR #289, 2026-05-04), with auxiliary channels held back pending per-channel data. Subsequent truth reports showed those auxiliaries were too low-volume to ever produce that data and the doctrinal call doesn't depend on per-channel evidence — applied uniformly across all 8 SCALP-family channels (`360_SCALP`, `_FVG`, `_CVD`, `_VWAP`, `_DIVERGENCE`, `_SUPERTREND`, `_ICHIMOKU`, `_ORDERBLOCK`) via PR #303, 2026-05-05. Reversible per channel by flipping the bool back in `_CHANNEL_GATE_PROFILE`.

### Top-emitter OI softening (2026-05-06, PR #314)

LSR / SR_FLIP / FAR were over-suppressed by the OI gate (truth-report data: 91–100% of soft-penalty stack). OI base × 1.8 (QUIET regime mult) = 27 pts — enough to push a B-tier candidate (65) below paid threshold. Modulators added: `LSR oi=0.30`, `FAR oi=0.30`, `SR_FLIP oi=0.50`. Counter-trend paths (LSR/FAR) get the aggressive 0.30 modulator because OI flipping against direction is the crowd we're trading against — exactly the thesis. SR_FLIP gets the milder 0.50.

## 3.5 Chartist-Eye World Model (PRs #314–#321, 2026-05-06)

A shared "world model" every evaluator can consult, closing the gap between rule-based scoring and what a human chartist sees at a glance.

| Component | Module | Role |
|---|---|---|
| **LevelBook** | `src/level_book.py` | Multi-TF S/R levels (1d/4h/1h swing pivots + round numbers + VP zones), scored by touches × tf_weight × age_decay. Top 60 retained per symbol, 1 h refresh TTL. |
| **Confluence bonus** | `scanner._prepare_signal` | When entry sits in a band where ≥2 distinct LevelBook zones cluster, subtract a soft-penalty bonus: 2→3, 3→6, 4+→9. Saturated; cannot lift sub-50 candidate to paid. |
| **StructureTracker** | `src/structure_state.py` | Per (symbol, tf) classification: BULL_LEG (≥75% HH+HL in last 4 pivots), BEAR_LEG (≥75% LH+LL), or RANGE. Refreshes 30 min TTL. |
| **Structure-align bonus** | `scanner._prepare_signal` | TPE / DIV_CONT / CLS / PDC paths earn `−3` soft-penalty bonus when entry direction matches the 4h structure leg. Counter-trend / break-event / tape-driven paths intentionally do **not** consume this. |
| **VolumeProfile** | `src/volume_profile.py` | POC + Value Area High/Low per symbol. Approximate VPVR from candles (volume distributed uniformly across `[low, high]`). POC/VAH/VAL injected into LevelBook with `source_tf="vp"` so they participate in confluence scoring automatically. |
| **MA_CROSS_TREND_SHIFT** | `_evaluate_ma_cross_trend_shift` | 15th evaluator. Discrete EMA50/200 (4h) or EMA21/50 (1h) crossover trigger. 24h cooldown per (symbol, direction). Specialist role; ~1-3 signals/day expected. |
| **Pattern catalog** | `src/chart_patterns.py` | Bull flag, bear flag (continuation) + double top/bottom + triangles + H&S/inverse-H&S (reversal) + bollinger squeeze + candlestick zoo. Wired into `pattern_confidence_bonus` (±3 pts). |

### Doctrine guardrails

- **Hard structural gates unchanged.** SL geometry validation, missing-data rejection, and structural-impossibility checks are untouched. The chartist-eye stack is purely a *scoring* layer — it never invents a setup.
- **Soft-penalty bonus magnitudes are bounded.** `confluence ≤ 9 pts`, `structure_align = 3 pts`. Combined max lift is ~12 pts; calibrated so a sub-50 candidate cannot reach paid (65) by these alone.
- **Per-path doctrine respected.** Counter-trend paths (LSR/FAR) and tape-driven paths (WHALE/FUNDING/LIQ_REV) deliberately do not consume `STRUCT_ALIGN`. Break-event paths (VSB/BDS/ORB/QCB/SR_FLIP/MA_CROSS) similarly excluded — see `_STRUCTURE_ALIGN_PATHS` in `src/scanner/__init__.py`.
- **Cost accounted.** All three caches refresh on per-symbol TTL (1 hr LevelBook+VP, 30 min StructureTracker). Combined < 50 ms/refresh × 75 pairs / 1 hr = ~1 s/hr CPU amortised.

## 3.6 Confidence Tiers and Routing

| Tier | Score | Routing |
|---|---|---|
| A+ | 80–100 | Paid channel |
| B | 65–79 | Paid channel |
| FILTERED | < 65 | Dropped silently |

WATCHLIST was retired 2026-05-06 (PR #308). The 50–64 band is now part of FILTERED — no free-channel preview routing inside the engine. The free channel is driven by close-storytelling mirrors (social-proof posts) and content-engine outputs, not by sub-paid-tier engine signals.

The QUIET regime applies an additional safety net: any 360_SCALP signal in QUIET regime needs confidence ≥ 65 (paid B-tier minimum) to pass. **No per-path exempts.**

## 3.7 Architecture — Signal Flow

```
Binance WebSocket (300 streams)
        ↓
HistoricalDataStore — candle OHLC, 6 timeframes per pair
        ↓
OrderFlowStore — OI snapshots, CVD, funding rate, liquidations
        ↓
Scanner — runs every 15s across 75 pairs
        ↓
ScalpChannel.evaluate() — 15 internal evaluators per pair
        ↓
Gate chain — SMC, MTF, regime, spread, volume, confidence
        ↓
Chartist-eye stack — LevelBook + VolumeProfile + StructureTracker
                      contributes soft-penalty bonuses (CONFLUENCE×N,
                      STRUCT_ALIGN:BULL_LEG/BEAR_LEG)
        ↓
SignalScoringEngine — multi-component score (0–100)
        ↓
_enqueue_signal() — universal SL minimum 0.80%
        ↓
SignalRouter — paid (A+ / B tier); sub-65 dropped (no free-channel routing)
        ↓
TradeMonitor — polls every 5s using 1m candle OHLC
```

## 3.8 Paper-book lifecycle (operator doctrine — added 2026-05-16)

Paper trading shares the live-mode doctrine that **reset never orphans an open position**, even though paper positions are in-memory simulation with no broker risk. This keeps live and paper operationally symmetric and forces an explicit user action to flatten — never a side effect of a counter/equity reset.

| Action | Endpoint | Effect |
|---|---|---|
| **Flatten paper book** | `POST /api/auto-mode/paper/close-all` (in-flight PR `feat/paper-close-all-positions`) | Snapshot-iterates `PaperOrderManager._positions`, closes each at entry price (zero-move close), records `close_reason="user_close_all"`, returns `{closed_count, realized_pnl_total}` |
| **Zero PnL + equity baseline** | `POST /api/auto-mode/paper/reset` (PR #401) | Refuses while open positions exist (B12 lifecycle guard), zeros cumulative paper PnL, resets equity baseline to $1000, archives `paper_trades` per-trade rows |
| **Live-mode equivalent** | `/reset_full` Telegram command | Preserves in-flight signals to avoid orphaning real Binance positions; **not coordinated with paper-mode reset** by design |

Two-step user flow for a clean paper-book reset: **close-all → reset.** This is why reset is "practically unreachable" on the Lumin Paper sub-tab today (subscribers almost always have open positions) — the resolution is to expose close-all as a button in the app, not to weaken reset's preservation guarantee.

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
| B12 | Auto-trade safety. No live execution without all of: daily-loss kill switch, concurrent-position cap, per-symbol exposure cap, leverage cap (≤30x), restart reconciliation, structured order audit log. Paper mode is the only acceptable runtime when any of these are not in place. **Paper-book lifecycle** (see §3.8): `/api/auto-mode/paper/reset` refuses while open positions exist; flattening requires the separate `POST /api/auto-mode/paper/close-all` action — reset never closes positions as a side effect, mirroring the live-mode `/reset_full` preservation doctrine. |
| B13 | Identity & auth. **Primary signin:** phone + SMS OTP (universal — works for any user without prerequisites, via AuthKey.io or equivalent DLT-registered provider). **Optional upgrade:** users opt-in from in-app Settings to bind their `@LuminProBot` chat_id; future OTPs and ongoing bot interactions route via Telegram DM (free, branded). **Identity primitive for paid-tier features remains `telegram_user_id`** (billing webhook per B16, ops console access, paid signal routing). No email, no password. Doctrine amended 2026-05-12 (was: Telegram-only) once Lumin became a real consumer app — strict-Telegram excluded ~5-15% of even crypto-aware audiences and gated growth on a prerequisite the app shouldn't impose. Re-amended 2026-05-15 (PRs #397/#398, Lumin #20/#21): Firebase is now the primary identity issuer (Google sign-in on Android); Telegram-DM OTP remains an opt-in upgrade for free-code delivery and bot-DM features. Legacy phone-OTP user-id JWTs accepted during cutover; deprecation post-Phase-4. |
| B14 | Build constraint. All build/deploy paths must work from Android+Termux. Mobile app builds via GitHub Actions only — no local Android Studio / Gradle requirement. |
| B15 | Brand architecture. Lumin = consumer app brand (Play Store, app icon, marketing). 360 Crypto Eye = engine + signal-source brand (Telegram channel, technical identity, "Powered by" attribution). The Telegram channel never renames. The app's About page always credits 360 Crypto Eye. |
| B16 | Revenue. Subscriptions are crypto-only via the Telegram bot (Lumin app qualifies for the Reader-app Play Store exception). No Google Play billing, no Stripe fiat, no bank account in v1. App is a control panel; payment is in the bot. |
| B17 | Pre-TP partial close + invalidation are per-user. **Pre-TP grab fraction** is user-configurable with a hard floor of **30%** (no user can configure 0%, which would collapse to the pre-2026-05-17 broken "SL-to-BE only" behaviour) and a ceiling of 100%. Engine default is 50%. When threshold hits, broker executes a real partial close on the configured fraction; the residual gets SL ratcheted to entry. **Invalidation aggressiveness** is user-selectable (Loose / Standard / Tight); engine default is Standard. Tight adds ATR-trailing kill at MFE ≥ 0.3R (close at 50% retracement of MFE peak). All per-user values stored in `user_pretp_settings` (with new `grab_fraction` column) and `user_invalidation_settings` tables; NULL = use engine default. Per §3.2 + §3.2a doctrine — capital preservation outranks TP chasing, and the user controls the preservation aggressiveness. |

---

# PART V — INFRASTRUCTURE

| Component | Detail |
|---|---|
| **VPS** | Ubuntu, Docker Compose, 24/7 runtime |
| **Stack** | Python 3.11+, asyncio, aiohttp, Redis (optional), Binance WS/REST |
| **Deploy** | `git push` to `main` → GitHub Actions → auto-deploy ~45s. Pushes to `main` happen only via merged PR (see `CLAUDE.md § Change-management protocol`). |
| **Monitor** | GitHub Actions "VPS Runtime Audit" → `monitor-logs` branch |
| **Telegram** | Paid signal channel + free preview channel |
| **Engine repo** | `github.com/mkmk749278/360-v2` |
| **Lumin app repo** | `github.com/mkmk749278/lumin-app` |
| **Ops dashboard repo** | `github.com/mkmk749278/360ce-ops` — web ops console live at `https://ops.luminapp.org` since 2026-05-12. Auto-deploy on push to `main` (build → GHCR → SSH-deploy to VPS). Owner-only password gate, FastAPI + Jinja2 + HTMX, read-only consumer of engine artifacts. See `docs/360CE_OPS_PLAN.md`. |

---

# PART VI — BEFORE EVERY PR

CTE asks **"how does this change make signals more profitable for paid subscribers?"** before writing code.

If the answer is unmeasurable, "engineering hygiene," or "this would have caught a hypothetical case" — defer or drop. Engineering polish without business impact is busy-work.

If the answer is measurable (win rate, signal volume, R:R, time-to-resolution, fewer subscriber-visible failures), proceed: investigate, implement, test, document, ship.

Mechanics of the PR itself are codified in `CLAUDE.md § Change-management protocol` — fresh topic branch off `main`, design-summary body, never push directly to a long-lived session branch.
