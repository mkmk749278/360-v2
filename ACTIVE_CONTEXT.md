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
- **VSB / BDS generated-but-not-emitted** — recent monitor showed 12 candidates generated, 0 emitted. Identify the downstream gate from the next truth report's confidence-component breakdown.
- **FAR `STRONG_TREND` regime block** — empirical conjecture ("low edge") rather than structural impossibility. Could be soft penalty per doctrine; needs win-rate data to revisit.
- **LSR hard 1H MTF reject in TRENDING/VOLATILE** — narrow filter (both 1H EMA AND RSI must oppose). Barely fires per recent telemetry. Could be soft per doctrine; revisit if data shows it's blocking 65+ paid candidates.

### Pending owner decision
- **OPENING_RANGE_BREAKOUT** — currently `feature_disabled`. Rebuild with proper session-anchored range logic, or delete the path entirely. Not a CTE call.

### Free-channel content rollout (in progress)

Goal: enrich the free channel as a paid-conversion funnel — market updates, major news, eventually charts and explanations.

**Phase 1 — Macro events to free channel** ✅ shipped
- `MacroWatchdog` now broadcasts HIGH/CRITICAL severity events (FOMC, regulatory action, exchange hacks, F&G ≤10 / ≥90, AI-classified breaking news) to both admin AND free channel
- MEDIUM/LOW stays admin-only (operational signal, not subscriber content)
- Backwards compatible: legacy `send_to_free=None` constructions stay admin-only
- 9 routing tests in `tests/test_macro_watchdog_routing.py`

**Phase 2 (next) — Event-driven market updates**
- Triggers for: BTC ±3% in 1h, regime shift on majors, BTC dominance ±2%
- AI-generated explanation + free-channel post
- Cooldown: max 1 per event-type per hour

**Phase 3 — Charts attached to scheduled posts**
- New `src/chart_renderer.py` using mplfinance
- Attached to morning brief, EOD wrap, event-driven alerts
- Uses existing `Telegram.send_photo`

**Phase 4 — Coin spotlights**
- Top mover / breakout watch daily posts with charts

**Phase 5 — Signal-close storytelling**
- Wire `generate_signal_closed_post` to TradeMonitor close events

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
