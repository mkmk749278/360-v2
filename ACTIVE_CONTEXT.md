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

### Lumin app initiative — kicked off
- **Brand:** consumer app = "Lumin", engine + signal source = "360 Crypto Eye". Two-tier branding (B15).
- **Distribution:** GitHub Releases APK (v1) → Play Store (v2 after policy site live).
- **Stack:** Flutter (Termux + GitHub Actions APK build), FastAPI backend in `360-v2`, three repos (engine + lumin-app + lumin-site).
- **Subscription:** Crypto-only via Telegram bot (Reader-app Play Store exception). No Google Play billing, no fiat.
- **Auth:** Telegram bot login token → JWT (no email/password/SMS).
- **Phase A1 ✅ shipped:** `PaperOrderManager` provides simulated execution behind `AUTO_EXECUTION_MODE=paper`. Powers the app's Demo mode and our own auto-trade testing before live. 15 tests, full interface parity with `OrderManager`.
- **Phase A2 ✅ shipped:** `src/auto_trade/risk_manager.py` enforces 6 gates (daily-loss kill, min equity floor, concurrent cap, per-symbol cap, leverage cap, setup blacklist) plus owner-driven manual pause. Wired into both OrderManager and PaperOrderManager. 23 tests. All env-overridable: `RISK_DAILY_LOSS_LIMIT_PCT`, `RISK_MAX_CONCURRENT`, `RISK_MAX_LEVERAGE`, `RISK_MIN_EQUITY_USD`, `RISK_SETUP_BLACKLIST`.
- **Counter-trend Regime double-penalty fix** (2026-05-03): truth-report data showed LSR / FAR were stuck at Regime score 8 even with near-max SMC scores, while ALSO eating ~8 pts via HTF soft penalty (#268) for being counter-trend. Doctrinally a double-penalty since their non-affinity IS the thesis. New `_REGIME_NEUTRAL_SETUPS` frozenset in `SignalScoringEngine` gives LSR + FAR a 14.0 baseline in non-affinity regimes (still 18 in affinity, soft-penalty for HTF mismatch unchanged). 6 new tests confirm scope.
  - **Outcome (2026-05-03 09:00 UTC, 6h post-merge):** Fix landed and worked as designed (LSR Regime 8.0 → ~10.2 weighted, ~14.0 in QUIET specifically). BUT total penalty surged from 2.60 → 10.28 (4×) for unrelated market reasons → LSR avg final actually DROPPED 60.69 → 52.36. Paid volume unchanged (still 1 signal/24h). My +5–10× volume estimate was wrong — I underestimated penalty subsystem reaction to QUIET-heavy markets and the QUIET_SCALP_BLOCK 65-floor.
- **Soft-penalty per-type instrumentation** (2026-05-03): `confidence_gate` log line now appends `soft_penalties(vwap=X,kz=Y,oi=Z,spoof=W,vol_div=V,cluster=C)` so the truth report can attribute WHICH gate caused the penalty surge. New "Soft-penalty per-type breakdown" section in the truth report. Backward-compatible — old log lines parse cleanly.
- **Kill Zone gate disabled on 360_SCALP** (2026-05-04, B10 owner-approved): Truth-report 04:16 UTC populated the new soft-penalty breakdown — KZ accounted for 80–100% of every filtered SCALP setup's penalty (LSR 96%, FAR 100%, SR_FLIP 94%, QCB 80%, DIV_CONT 100%). KZ was inherited from session-traded asset doctrine; doctrinally wrong for 24/7 crypto. Disabled via `_CHANNEL_GATE_PROFILE["360_SCALP"]["kill_zone"] = False`. Expected effect: LSR avg final 49.42 → 62.58 (clears watchlist with margin), FAR kept 59.25 → 64.00 (very close to paid B). Auxiliary SCALP_* channels keep KZ pending per-channel data. Reversible. 9 tests in `tests/test_kill_zone_disable.py` lock in the doctrinal contract.
- **Phase A3 ✅ shipped:** `src/auto_trade/position_reconciler.py` detects drift between exchange positions and engine signal state. `reconcile_on_boot()` runs once at start (auto-close orphans optional via `RECONCILER_AUTO_CLOSE_ORPHANS`); `periodic_drift_check()` runs every `RECONCILER_PERIODIC_INTERVAL_SEC` (default 300s) for mid-flight drift. Live-mode only — paper has no exchange state. 21 tests covering classification, alerting, auto-close, and resilience.
- **`/automode` runtime control ✅ shipped:** Telegram command lets owner switch auto-execution mode at runtime without redeploy. `/automode` shows current mode + open positions + daily PnL + paper session PnL. `/automode paper` flips to paper mode (zero risk). `/automode off` disables. `/automode live confirm` (extra confirmation token required) flips to live. Refuses mode change when open positions exist. Live mode requires EXCHANGE_API_KEY/SECRET set. Ephemeral — engine restart reverts to AUTO_EXECUTION_MODE env var. 14 tests in `tests/test_automode_command.py`.
- **Phase A4 next:** live with own keys, $50 USDT cap. All safety scaffolding (A1+A2+A3) now in place; B12 doctrine fully satisfied.
- **Lumin app ✅ first APK shipped** (v0.0.1 bootstrap): GitHub Actions builds signed-when-keystore-set release APKs on every push to `lumin-app` repo. Splash with brand theme + "Powered by 360 Crypto Eye" attribution rendering correctly on owner's phone. Pipeline: phone → CI → APK → phone, fully automated.
- **Domain registered:** `luminapp.org` for backend API + Privacy/ToS hosting (cheap; users see app name not URL — backend plumbing decision per CTE call).
- **Next on app track:** 5-tab navigation scaffold (Pulse / Signals / Agents / Trade / Settings) — placeholder layouts that fill in as backend endpoints land.
- **Then:** FastAPI backend in `360-v2` for the app to read.

### Pre-TP grab — Phase A ✅ shipped + ENABLED in production
- `TradeMonitor._check_pre_tp_grab` fires when a signal moves favourably by an **ATR-adaptive threshold** within 30 min, in a non-trending regime, on a non-breakout setup
- Resolved threshold = `max(PRE_TP_FEE_FLOOR_PCT, PRE_TP_ATR_MULTIPLIER × atr_pct)` where `atr_pct = atr_last / entry × 100`
  - Low-vol pair (5m ATR ≈ 0.30%) → 0.20% floor → +1.30% net @ 10x
  - Mid-vol (5m ATR ≈ 0.50%) → 0.25% → +1.80% net @ 10x
  - High-vol alt (5m ATR ≈ 1.00%) → 0.50% → +4.30% net @ 10x
- Falls back to static `PRE_TP_THRESHOLD_PCT` (0.35%) when ATR unavailable — soft-penalty doctrine
- Symbolic + breakeven SL — no broker partial; subscriber sees the message and chooses
- Posts to active + free channels with raw and net-of-fees math at 10x
- Free-channel post emits `free_channel_post source=pre_tp` marker for truth-report attribution
- Feature flag: `PRE_TP_ENABLED` (default false). All thresholds env-overridable per B8.
- Setup blacklist: VSB / BDS / ORB (built for bigger moves — pre-TP would cap thesis)
- Regime allowlist: QUIET / RANGING / VOLATILE
- 27 tests in `tests/test_pre_tp_grab.py` (21 mechanism + 6 ATR-adaptive)
- **`PRE_TP_ENABLED=true` set in `docker-compose.yml`** — flag is now live in production
- **Truth-report instrumentation:** new `## Pre-TP grab fire stats` section parses `pre_tp_fire` log markers and reports total fires, threshold-source distribution (atr / atr_floored / static), per-setup × source breakdown, top symbols, avg net @ 10x, avg time-to-fire. The next monitor truth-report run is the empirical validation: if the section is empty after one cycle, either no signals matched all gates or the flag didn't propagate; populated rows confirm fire rate and net economics match design.

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
