# ACTIVE CONTEXT

*Live operational state. Updated at every session end.*

---

## Current Phase

**Data-driven tuning.** Per-path entry-quality audit complete under the scalping doctrine (`OWNER_BRIEF.md` §3.2). All 14 evaluators reviewed; doctrine-corrections shipped where applicable. Next changes are gated on empirical data from the Phase 1 invalidation audit and the runtime truth report — no further structural per-path work without measurable business-chain justification.

---

## What's Currently Working

- **Engine** healthy, scanning 75 pairs continuously, deploying via GitHub Actions
- **Monitor** runtime truth report on `monitor-logs` branch — regime distribution, gate metrics, confidence component breakdown, invalidation quality audit
- **Risk-component scoring** calibrated for scalp R-multiples (max credit at 2.0R)
- **Regime classifier** BB-width VOLATILE threshold at 8.0% (env-overridable)
- **HTF mismatch policy** soft penalty (not hard block) on SR_FLIP / QCB / FAR
- **QUIET-block doctrine** uniform 65 paid-tier floor — no scrap-routing exempts
- **Universal 0.80% SL floor** plus per-setup caps active
- **Invalidation quality audit** classifying every kill as PROTECTIVE / PREMATURE / NEUTRAL post-30-min

---

## Open Queue

### Pending data
- **TP1 ATR cap re-derivation** (1.8R / 2.5R / uncapped on SR_FLIP / FUNDING / DIV_CONT / CLS) — wait for Phase 1 invalidation audit data on TP1 hit rates per setup × ATR-bucket.
- **VSB / BDS generated-but-not-emitted** — diagnosed against latest truth report (1.77M attempts window):
  - VSB: **647 generated → 314 reach scoring → 0 emit, 0 watchlist.** All 314 filtered at `min_confidence`. Avg final confidence 46.78 vs threshold 80 (gap 33). Component sum (Market 20.70 + Execution 20.00 + Risk 20.00 + ThesisAdj 0.50) = 61.20 — implies a ~14-point implicit deduction not surfaced in the truth report's component breakdown. Even un-penalised, VSB candidates would still land 19 below the paid B-tier (65) and 4 below WATCHLIST (50), explaining zero routing of any kind.
  - BDS: **1 generated total** — structurally silent. Funnel rejects 99.999% upstream of scoring (`regime_blocked` 38%, `breakout_not_found` 37%, `basic_filters_failed` 13%, `retest_proximity_failed` 11%). Not a scoring problem — gate chain is doing its job; BDS is just rare in current QUIET-dominated regime mix.
  - **Instrumentation step shipped:** `confidence_gate` log line now emits the actual `SignalScoringEngine` dimensions (smc/regime/volume/indicators/patterns/mtf) alongside the legacy `market/execution/risk/thesis_adj` group. The engine dimensions are what actually sum to `final` — the legacy group was a different scorer, which is why the original 14-point gap was unattributable. New "Scoring engine breakdown" section in the truth report will surface per-dimension averages by setup × decision; populates after next deploy.
- **FAR `STRONG_TREND` regime block** — empirical conjecture ("low edge") rather than structural impossibility. Could be soft penalty per doctrine; needs win-rate data to revisit.
- **LSR hard 1H MTF reject in TRENDING/VOLATILE** — narrow filter (both 1H EMA AND RSI must oppose). Barely fires per recent telemetry. Could be soft per doctrine; revisit if data shows it's blocking 65+ paid candidates.

### Pending owner decision
- **OPENING_RANGE_BREAKOUT** — currently `feature_disabled`. Rebuild with proper session-anchored range logic, or delete the path entirely. Not a CTE call.

### Pre-TP grab — Phase A ✅ shipped (gated OFF; awaiting first runtime validation)
- `TradeMonitor._check_pre_tp_grab` fires when a signal moves favourably ≥0.35% raw within 30 min, in a non-trending regime, on a non-breakout setup
- Symbolic + breakeven SL — no broker partial; subscriber sees the message and chooses
- Posts to active + free channels with raw and net-of-fees math at 10x (`+0.35% raw → +2.80% net @ 10x after 0.7% fees`)
- Free-channel post emits `free_channel_post source=pre_tp` marker for truth-report attribution
- Feature flag: `PRE_TP_ENABLED` (default false). All thresholds env-overridable per B8.
- Setup blacklist: VSB / BDS / ORB (built for bigger moves — pre-TP would cap thesis)
- Regime allowlist: QUIET / RANGING / VOLATILE
- 21 tests in `tests/test_pre_tp_grab.py`. **Plan: turn on after one truth report verifies fire rate and timing match expectations.**

### Free-channel content rollout (in progress)

Goal: enrich the free channel as a paid-conversion funnel — market updates, major news, eventually charts and explanations.

**Phase 1 — Macro events to free channel** ✅ shipped
- `MacroWatchdog` now broadcasts HIGH/CRITICAL severity events (FOMC, regulatory action, exchange hacks, F&G ≤10 / ≥90, AI-classified breaking news) to both admin AND free channel
- MEDIUM/LOW stays admin-only (operational signal, not subscriber content)
- Backwards compatible: legacy `send_to_free=None` constructions stay admin-only

**Phase 2 — BTC big-move alert** ✅ shipped (in progress for additional triggers)
- `MacroWatchdog._check_btc_price_move()` polls BTC 1h klines from Binance every cycle
- Move ≥ 3% (env: `MACRO_BTC_MOVE_THRESHOLD_PCT`) → HIGH severity
- Move ≥ 5% → CRITICAL
- Per-direction cooldown 1h (env: `MACRO_BTC_MOVE_COOLDOWN_SEC`) — UP doesn't suppress DOWN
- Routes via existing `_broadcast` helper → admin + free channel for HIGH/CRITICAL
- Network errors (timeout, non-200, malformed payload) degrade silently
- 11 tests in `tests/test_macro_watchdog_btc_move.py`

**Phase 2b — BTC/ETH regime-shift alert** ✅ shipped
- `MacroWatchdog._check_regime_shift()` polls 22 1h klines for BTCUSDT and ETHUSDT each cycle
- Computes EMA21; classifies UP (`close > EMA21`) or DOWN (`close < EMA21`)
- First observation records baseline silently — only flips alert
- Per-symbol cooldown (env: `MACRO_REGIME_SHIFT_COOLDOWN_SEC`, default 4h) absorbs chop near EMA
- Routes via `_broadcast` HIGH severity → admin + free channel
- Feature flag: `MACRO_REGIME_SHIFT_ENABLED` (default true)
- 12 tests in `tests/test_macro_watchdog_regime_shift.py`

**Phase 2 (still open) — additional event triggers**
- BTC dominance ±2% (requires extra data source)

**Phase 3 — Charts attached to scheduled posts**
- New `src/chart_renderer.py` using mplfinance
- Attached to morning brief, EOD wrap, event-driven alerts
- Uses existing `Telegram.send_photo`

**Phase 4 — Coin spotlights**
- Top mover / breakout watch daily posts with charts

**Phase 5 — Signal-close storytelling** ✅ shipped
- `TradeMonitor._post_signal_closed` mirrors paid-tier closes (TP3 / SL) to the free channel with a `📣 Paid Signal Result` header
- WATCHLIST tier skipped (defensive guard); free-send failure does not break active-send (best-effort)
- B3 honoured: SL hits get the same free-channel visibility as TPs (trust > vanity)
- Skips when free == active (misconfig) or `TELEGRAM_FREE_CHANNEL_ID` empty
- 7 tests in `tests/test_signal_close_storytelling.py`

---

## Working Pattern

For any future code change:
1. Ask: **"how does this make signals more profitable for paid subscribers?"**
2. If answer is unmeasurable, "engineering hygiene," or speculative — **defer or drop**.
3. If answer is measurable (win rate, signal volume, R:R, time-to-resolution, fewer subscriber-visible failures), proceed: investigate, implement, test, document, ship.

---

## Key Files

| Concern | File |
|---|---|
| 14 evaluators | `src/channels/scalp.py` |
| Confidence scoring | `src/signal_quality.py` |
| Regime classifier | `src/regime.py` |
| Scanner gate chain | `src/scanner/__init__.py` |
| Trade lifecycle | `src/trade_monitor.py` |
| Truth report parser | `src/runtime_truth_report.py` |
| Invalidation audit | `src/invalidation_audit.py` |

---

## Reference: HTF Policy Cheat Sheet

| Path category | HTF treatment |
|---|---|
| Trend-aligned by regime gate (TPE / DIV_CONT / CLS / PDC) | None |
| Internally direction-driven (WHALE / FUNDING / LIQ_REVERSAL) | None |
| Counter-trend by design (LSR / FAR) | Soft penalty when 1H AND 4H both oppose |
| Structure with optional counter-trend (SR_FLIP / QCB) | Soft penalty when 1H AND 4H both oppose |
| Breakout (VSB / BDS / ORB) | None |
