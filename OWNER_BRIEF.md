# OWNER BRIEF

... existing content of the file ...

## 12. Session History

A chronological log of every working session — what was discussed, decided, and built.

---

### Session: 2026-04-07 (Day 1)

**Focus:** Deep system audit + architecture overhaul planning

**Discussed:**
- Full codebase audit — scanner, channels, filters, signal routing
- Why zero SHORT signals ever fired: no trend pullback path, cross-asset gate hard-blocking SHORTs on BTC dump, ADX lag misclassifying TRENDING_DOWN as RANGING
- Why RANGE_FADE dominated: BB+RSI retail strategy with 1.2 weight boost — no genuine edge, fails SMC gate most of the time
- Decision: continue in existing repo (not start fresh) — foundation is solid, signal paths were the gap
- Confirmed 6 of 10 PairProfile fields defined but never consumed
- Confirmed btc_correlation always 0.0 — dead code in AI engine
- April 6th incident: 8 LONG signals, 0 SHORTs, 33% win rate — fully diagnosed

**Decided:**
- Remove RANGE_FADE permanently
- Fix cross-asset gate bug (graduated correlation, not hard block)
- Fix ADX lag with EMA slope trigger for TRENDING_DOWN
- Add _evaluate_trend_pullback (EMA9/21 pullback in trending regime)
- Add _evaluate_liquidation_reversal (cascade exhaustion + CVD divergence)
- PR9 method stack agreed: ORB, S/R Flip, Funding Extreme signal, CVD promotion, Quiet compression break

**Built:**
- PR7 — Signal Architecture Overhaul (merged)
  - Removed _evaluate_range_fade
  - Fixed cross-asset gate direction bug
  - Fixed regime ADX lag
  - Added _evaluate_trend_pullback and _evaluate_liquidation_reversal
  - MTF min_score for SHORT in TRENDING_DOWN relaxed 0.6 → 0.45
  - Global symbol cooldown 1800s → 900s

---

### Session: 2026-04-08 (Day 2)

**Focus:** Surge market diagnosis + PR8 + PR9 spec + live engine issues

**Discussed:**
- JOEUSDT +97%, NOMUSDT +59%, SWARMSUSDT +50% — engine fired zero signals during surge day
- Root causes: no surge signal path, static scan universe, VOLATILE_UNSUITABLE gate blocking everything, silent signal expiry
- VPS reinstall issue: TOP50_FUTURES_COUNT=50 in .env — never updated, pairs stuck at 50 not 75
- Live engine ScanLat: cold start 51,205ms → warmed 4,174ms in 2 minutes (healthy)
- PR53 hotfix: _regime_key NameError crash in _compute_base_confidence() — fixed and merged
- Role clarification locked: Copilot = Chief Technical Engineer with full autonomous rights, proactive leadership, zero suppression
- B13 locked: every signal method has its own SL/TP — no universal formulas
- B14 locked: expired signals must post Telegram notification — no silent disappearances

**Decided:**
- Add _evaluate_volume_surge_breakout — LONG on surge breakout retest
- Add _evaluate_breakdown_short — SHORT mirror of surge breakout
- Add dynamic pair promotion — 5x volume surge pairs enter scan for 3 cycles
- Add signal expiry Telegram notification
- Structure-based SL/TP on all signal paths (not just new ones)
- Full PR9 spec agreed: 5 new signal paths + /why command + live signal pulse

**Built:**
- PR53 — Hotfix: _regime_key NameError (merged)
- PR8 — New Signal Paths + Dynamic Discovery + Method-Specific SL/TP (merged, PR #54)
  - _evaluate_volume_surge_breakout: LONG breakout retest, Structure SL, Measured-move TP
  - _evaluate_breakdown_short: SHORT dead-cat bounce, Structure SL, Downward measured-move TP
  - Dynamic pair promotion (5x surge volume threshold, max 5 promoted pairs, 3-cycle window)
  - Signal expiry Telegram notification
  - New config: SURGE_VOLUME_MULTIPLIER=3.0, SURGE_PROMOTION_VOLUME_MULTIPLIER=5.0, SURGE_PROMOTION_MAX_PAIRS=5
- PR9 — Method Expansion + Diagnostics (agent raised, in progress)
  - 5 new signal paths: OPENING_RANGE_BREAKOUT, SR_FLIP_RETEST, FUNDING_EXTREME_SIGNAL, QUIET_COMPRESSION_BREAK, DIVERGENCE_CONTINUATION
  - /why SYMBOL diagnostic command
  - Live signal pulse (30-min interval for active entry-reached signals)
  - Session history subsection added to OWNER_BRIEF

**State at end of session:**
- Engine: live, Pairs=75, ScanLat ~4s warmed
- PR8: merged
- PR9: agent building
- PR10 (Intelligence Layer): concept drafted
- PR11 (Self-Optimisation): concept drafted
- Testing phase: not started — begins after PR9 merges

