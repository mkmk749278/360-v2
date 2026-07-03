# ACTIVE CONTEXT

*Live operational state. Updated at every session end.*

---

## 🟢 SESSION 41 2026-07-03 — SR_FLIP long V2: the thesis repair, shipped dark (issue #674)

**Owner mandate (loop):** "enable SR_FLIP longs in correct manner + deep research on
strategies/paths/gates/regimes/wiring + scoring system — profitable signals first,
then volume." This session delivered part 1; parts 2–3 continue next iterations.

### Diagnosis (deep code read of `_evaluate_sr_flip_retest`)

The long/short code is **symmetric** — retest zones, wick/RSI/EMA gates, SL/TP
geometry all mirror. The LONG side bled (19% win, losing in EVERY regime incl.
9% in TRENDING_UP) for thesis-level reasons the code couldn't see:

1. **Flip confirmation was pure price** — one break-and-close above resistance.
   In leveraged crypto an upside break is disproportionately a **bull trap**
   (breakout-chasing longs provide the exit liquidity; their flush IS the
   retest V1 bought). Downside breaks are cascade-driven — that's why the
   mirror-image SHORT side is +5.1% at 52% win on identical code.
2. **No acceptance requirement** — a single poke above the level counted.
3. **LONG had if-priority on whipsaws** — a window where price broke BOTH
   levels (chop) silently resolved LONG.
4. **No macro protection** — SR_FLIP wasn't in the CT_LONG gate scope
   (it was "already off").

### V2 (shipped DARK — merge is behavior-neutral, longs stay off)

- **Volume-backed break**: breakout candle ≥ `SR_FLIP_LONG_BREAK_VOL_MULT`
  (1.5) × prior-20 mean volume. Traps break thin; acceptance prints volume.
- **Acceptance hold**: ≥ `SR_FLIP_LONG_MIN_HOLD_CLOSES` (2) closed 5m candles
  above the level between break and retest.
- **Whipsaw guard**: both-direction confirmation in one window → reject
  `whipsaw_flip` (behavior-neutral today; protective on re-enable).
- **Macro scope**: `SR_FLIP_RETEST` added to `CT_LONG_MACRO_GATE_SETUPS` —
  inert while the side is off; protects re-enabled longs from the steamroll.
- **Shadow**: V2-passing longs log `[SHADOW] SR_FLIP_LONG_V2_WOULD_FIRE`
  (symbol, level, vol evidence, hold count) then reject `long_disabled`.
- New reject reasons: `long_break_volume_thin`, `long_acceptance_not_held`,
  `whipsaw_flip`. SHORT side deliberately untouched (no volume gate — it's
  the profitable side and cascade breaks are legitimately thin sometimes).

### Re-enable criteria (owner sign-off when met)

Read `[SHADOW] SR_FLIP_LONG_V2_WOULD_FIRE` counts after ≥1 week; join outcomes
via the backfill validator on the shadow candidates. Re-enable
(`SR_FLIP_LONG_ENABLED=true`) only if the V2 candidate set clears ~45%+
implied win on the counterfactual — the point of V2 is fewer, better longs.

### Wiring audit — pass 1 (setup-registration maps): one dead path found + invariant locked

Systematic diff of every emitted `setup_class` against every setup-keyed map:

- **`MA_CROSS_TREND_SHIFT` was silently dead since it shipped** — in the enum
  but registered in NO channel set, NO regime set, and not `_SELF_CLASSIFYING`
  (the exact #634 bug class): hard-rejected at `_prepare_signal` before scoring
  in every regime, while its evaluator burned ~190k attempts/window. Fixed:
  registered in `360_SCALP` + STRONG_TREND/WEAK_TREND/BREAKOUT_EXPANSION (a
  trend-shift entry; ranges whipsaw MA crosses) + self-classifying. First real
  emissions will be watched by the daily loop.
- **6 emitted setups had no `SIGNAL_TYPE_LABELS` entry** (FAR, LIQUIDATION_REVERSAL,
  MA_CROSS, MOVER_AVWAP, POST_DISPLACEMENT, TREND_PULLBACK_EMA) — subscriber
  messages fell back to raw enum names. Labels added.
- **Invariant test added** (`test_setup_registration_audit.py`): every emitted
  setup must be in ≥1 channel set, ≥1 regime set, and have a display label —
  the whole bug class is now unreintroducible.
- Verified clean: `_MAX_SL_PCT_BY_SETUP` (19 keys), `ACTIVE_PATH_PORTFOLIO_ROLES`
  (17), the `INVALIDATION_*_BY_SETUP` maps (sparse by design — per-setup
  overrides over channel defaults).

### Scoring audit (mandate part 3) — verdict + redesign design written

**Verdict: the confidence score cannot rank signals BY DESIGN** — it is an
uncalibrated presence-checklist (any sweep=10, MSS=8, FVG=2…), distributions
compress post-evaluator-gates so penalties do the real separating, and its
largest dimension (SMC) runs half-blind (`orderblocks` source `not_implemented`,
order book top-of-book only, spoof penalty has never fired). r≈0 and the band
inversion are the expected output, not a tuning problem.

**Key discovery: the measured-edge machinery already exists** —
`StatisticalFilter` (Wilson-bound rolling win rates, wired at emit) — but is
neutered by (1) the wrong key `(channel, pair, regime)`: channel is constant,
per-pair samples never clear min_samples, and `setup_class`/side are discarded;
(2) contaminated pre-#685 data; (3) veto-only (can't rank).

**Redesign (owner sign-off): `docs/SCORING_AUDIT_2026_07_03.md`** — two-layer
finalisation: checklist becomes a pass/fail sanity floor; ranking/finalising by
**measured cohort edge** (Wilson-bounded expectancy per setup × side ×
regime_family × BTC-macro), emit-if-positive-edge / probation-cap-if-unknown /
suppress-if-negative. Generalises the SR_FLIP-long disable, CT_SHORT gate, and
S19 setup-identity finding into a self-updating table. Rollout dark-first:
STEP 0 (this PR) `EXPIRED_NO_FILL` excluded from the stat store; STEP 1
observe-only cohort stamps + [SHADOW] COHORT_EDGE; STEP 2 activation on
sign-off after ≥2 weeks clean shadow.

### Wiring audit — pass 2 (stamped-field consumption): validity window was display-only

Traced every field stamped on a Signal to its consumers. `entry_regime_15m`,
`atr_value_at_entry` (FSM trail rate), `market_phase`, `btc_state_factor` — all
consumed correctly. **`valid_for_minutes` was consumed by NOTHING but the
Telegram card**: subscribers are told "valid 15 minutes" while the engine's
fill gate kept waiting up to the 1h max-hold — the engine/paper book could
"fill" a stale setup at minute 55 that rule-following subscribers abandoned at
minute 15 (book-vs-experience divergence + stale-thesis entries). **Fixed:**
`ENTRY_FILL_WINDOW_ENFORCED` (default ON, env-reversible) — an unfilled limit
signal finalises as `EXPIRED_NO_FILL` the moment its advertised validity
lapses.

**Open design question for owner (FSM, sign-off): auto-trade entries are
MARKET-at-dispatch** while the signal book + manual subscribers use the limit
entry zone — AUTO-tier users are IN trades the book correctly counts as
never-filled (~1/3 of signals in the last clean window). Options: (a) FSM
places LIMIT at entry zone with validity-window TTL (matches the book exactly,
users miss nothing the book doesn't), (b) keep MARKET entries and accept the
divergence, (c) hybrid: MARKET only when dispatch price is inside the zone.
Recommend (a) — one truth for every consumer of a signal. Not changed in code;
FSM entry shape is an owner-sign-off item.

### NEXT (the standing mandate, in order)

1. **Owner call: FSM entry shape** (see pass-2 finding above) — LIMIT-with-TTL
   vs MARKET-at-dispatch for auto-trade entries.
1b. **Wiring pass 3** — gate-chain order in the scanner; pre-TP/FSM allowlist
   resolution vs config defaults.
2. **Scoring STEP 1 (observe-only)** — extend the outcome store key to
   (setup, side, regime_family, macro); stamp cohort edge + checklist
   components into perf records; [SHADOW] COHORT_EDGE decisions. Ships
   normally (observe-only). STEP 2 activation = owner sign-off per the doc."
3. Daily check-in items (CT_SHORT gate watch, expiry tune, MOVER_AVWAP, scorer
   data accumulation) continue.

---

## 🟢 SESSION 40 2026-07-03 — Fresh-window validation + phantom-trade accounting bug + tokenized stocks back via movers

**Owner trigger:** "look for signal quality, where things get bad and what's wrong now"
→ "monitor truth data is ready, analyse + PR history" → "look at MOVER paths not
closing at TPs or SLs".

### Fresh 72h truth window (Jul 1–3, 100 closed signals) — June fixes VALIDATED

- **Long bleed is dead:** LONG 40 signals **−0.71% (flat)** vs −25.1%/month pre-fix.
  `long_disabled` = 17,380 SR_FLIP evaluator rejections in 72h — #672 holding.
- **SR_FLIP shorts-only working:** 26 shorts, 50% win, −0.44% ≈ breakeven (was the
  −16.6% biggest single drag).
- **BE@+1% visible:** 12 BREAKEVEN_EXITs that used to round-trip to SL (RIF LONG
  +4.35% MFE → closed 0.00). Real TP hits back: 13 TP1 + 2 FULL_TP.
- **MOVER_TREND_PULLBACK now the top P&L contributor** (+2.05% / 18 longs) —
  excluding it from the macro gate was right. (Truth report's "most suspicious
  degradation: MOVER_TREND_PULLBACK" headline is a heuristic artifact — it keys
  off win-rate/emit ratios, not P&L. Ignore.)
- **THE BLEED SWITCHED SIDES:** SHORT 60 signals **−8.53%**. Regime flipped
  (TRENDING_UP 45.4% of cycles, was 20.9%); counter-trend SHORTs (LSR SHORT −3.75%,
  BREAKDOWN −3.18%, FAR SHORT −2.33%) now mirror the June long bleed. The live
  #683 gate is longs-only by design → activation path is the graded haircut, below.
- Scorer still non-monotonic mid-band (70–75 worst: 25% win, −0.33%/signal; 80+
  only positive band). Rebuild still deferred — n=100 and (see next) data was dirty.

### Root-cause find #1 — phantom no-fill trades (FIXED this session)

All 36 EXPIRED closes in the window had **hold=0s, MFE=MAE=0, no dispatch ts** —
limit signals whose entry zone was NEVER visited. `trade_monitor` skips them each
tick (fill gate), then `router.cleanup_expired` → `main._handle_signal_expiry`
stamped a perf record with **mark-vs-entry P&L for a position that never existed**
(AGLD "−1.25%", WHALE "−0.79%" — fabrications) and fed them into the invalidation
audit as `expired` kills. **36% of the book was phantom.** Consequences: the audit's
"21 PREMATURE expiry kills" verdict is unreliable → the planned expiry tune is
DEFERRED until clean data accumulates; scorer band tables + ops Profit page were
polluted the same way; MOVER_AVWAP_SCALP has in fact **never filled once** — all
its "trades" were phantoms (its entry geometry needs review on clean data).

**Fix (this session's PR):** no-fill expiries now record `EXPIRED_NO_FILL` with
zero P&L on BOTH expiry paths, are excluded from the invalidation audit, skip the
broker close, and the router-path record finally carries create/dispatch/terminal
timestamps (tolerating restart-restored ISO-string `dispatch_timestamp`, which
`_signal_from_dict` never converts back — that string-vs-datetime quirk is still
unfixed, only tolerated). New `Signal.entry_never_filled` property is the single
predicate.

### Root-cause find #2 — tokenized stocks re-entered via mover promotion (FIXED)

#666 admits movers straight off `!ticker@arr` (whole board) and
`_ensure_mover_pair` checked **no blacklist** → SAMSUNG/HOOD/COIN/QCOM/PLTR/SNDK/
RKLB/LITE/ASTS/AXTI equity perps were promoted, scanned, **emitted to the paid
channel** (6× SAMSUNGUSDT in the window), and dominated the phantom EXPIRED sweep.
Fix: `_ensure_mover_pair` now honours `pair_manager._PAIR_BLACKLIST` +
`SCAN_SYMBOL_BLACKLIST`; both blacklists extended with the 13 observed symbols
(incl. ARMUSDT/MRVLUSDT seen in QUIET blocks, XPTUSDT = platinum). Static-list
rot remains a known weakness — Binance keeps listing new xStocks; consider an
exchangeInfo `underlyingType`-based structural filter as the durable fix.

### Root-cause find #3 — "paper skips trades when app unopened" (owner report, FIXED)

The paper book is server-side (single shared PaperOrderManager; the app's
client-side AutoTradeWatcher was removed 2026-05-19), so app-open can't gate it
directly — but the skip was real: `_process_signal` opened the engine-book
position **at dispatch, before the entry-fill gate**. A no-fill signal's paper
position could then NEVER close (SL/TP checks are fill-gated; expiry was
default-off for stretches) → stuck positions accumulated in the risk manager's
**max_concurrent=5** slots → later signals rejected (`risk-gate concurrent-cap`).
Left unattended longer = more stuck slots = more skips; the owner's close-all /
resets on app-open freed slots, creating the "app not open → skips" correlation.
Fix: engine-book auto-execution now waits for `entry_zone_filled` (market-order
signals unaffected); the no-fill expiry path keeps a defensive `close_full` to
drain any pre-fix stranded positions. Same root family as find #1 — dispatch-time
fill fabrication.

### Docs gap closed — the missing macro-direction session (2026-06-30, #677–#683)

Between S38's doc and S39, one undocumented arc shipped: **#677** production-phase
doctrine (dark-flag-first restored) · **#678** graded BTC-State haircut
(`compute_haircut_factor`, stamps `btc_state_factor` on every signal since
2026-06-30, `BTC_STATE_HAIRCUT_ENABLED=false` dark) · **#679** coupling P&L
counterfactual · **#681/#682** directional weekly macro classifier (slope +
structure, quick to de-risk / patient to re-risk, replay-proven on 2021–24) ·
**#683** `CT_LONG_MACRO_GATE_ENABLED=true` LIVE — suppresses counter-trend LONGs
(scope: LSR; MOVER excluded as trend-continuation; SR_FLIP longs already off).

### Root-cause find #4 — the short bleed is MACRO-counter, not intraday-counter (haircut NO-GO; mirror gate shipped dark)

Ran the #675 validator on the clean window (64 real trades; klines from
data.binance.vision — fapi is geo-blocked from the session sandbox, the public
archive isn't). **The intraday BTC-State haircut FAILED its acceptance test:**
the bleeding shorts were BTC-*aligned* at 5m/15m/1h (bucket `4_short`: 22
shorts, 14% win, −0.396 avg = the whole bleed) while counter-trend shorts were
fine; every counterfactual cut made the book worse. The real pattern: shorts
fire into intraday BTC dips inside the weekly-BULL recovery — 36/36 bled shorts
were against `macro_direction` weekly-BULL; the book without them is **+0.42%**
(vs −7.66%). One weekly regime state ≠ a validated gate, so per dark-first:
**`BTC_STATE_HAIRCUT_ENABLED` stays OFF** (verdict recorded in the brief), and a
**CT_SHORT macro mirror** of #683 shipped **DARK** — `CT_SHORT_MACRO_GATE_ENABLED`
(false), scope `LIQUIDITY_SWEEP_REVERSAL,FAILED_AUCTION_RECLAIM,BREAKDOWN_SHORT`
(the 0–20%-win bleeders; QUIET_COMPRESSION 67%-win and SR_FLIP-breakeven shorts
excluded), flag-independent predicate + `[SHADOW] CT_SHORT_MACRO_SUPPRESSED`
telemetry (#597 pattern).

### CT_SHORT gate ACTIVATED (2026-07-03, explicit owner sign-off)

Owner answered "Activate now" (AskUserQuestion, after "proceed with fix") —
`CT_SHORT_MACRO_GATE_ENABLED` default flipped to `true` the same day #687
shipped it dark, accepting the single-regime-window caveat. Env-reversible;
auto-restores shorts when the weekly macro turns down; profitable short
cohorts (QUIET_COMPRESSION, SR_FLIP) out of scope. Daily loop check-in now
watches `CT_SHORT_MACRO_SUPPRESS` counts + short-side P&L on the clean window.

### NEXT (priority order)

1. **Watch the activated CT_SHORT gate** — daily: suppression counts
   (`grep -c "CT_SHORT_MACRO_SUPPRESS"`), short-side P&L trend, and that short
   volume returns when the macro genuinely turns down. Roll back via env if
   live data disagrees with the window evidence.
2. **Expiry tune** — re-audit `expired` kills after ≥5 days of post-fix (no-phantom)
   data; FAR was the premature-kill hotspot but the numbers were contaminated.
3. **MOVER_AVWAP_SCALP entry geometry** — zero real fills ever; on clean data
   decide: widen entry zone / market-entry variant / drop.
4. **Scorer rebuild** — still blocked on clean data volume (band×side, post-fix).
5. Truth-report heuristic: "most suspicious degradation" should weight avg P&L,
   not just win-rate deltas (it flagged the best performer). Low priority.

---

## 🟢 SESSION 39 2026-07-02 — Market Charts audit + Phase 2 shipped (lumin-app #112)

**Owner trigger:** "look at Charts implementation in app side … audit and what we can
add more features and wire everything, implement everything."

**Audit of the v1 Charts feature (lumin-app #108–#111) found four real gaps; all
fixed + Phase 2 shipped in one PR — lumin-app #112** (display-only, no money-path
surface, ships normally):

- **Fix: price-axis precision** — Lightweight Charts defaults to 2 decimals; every
  sub-dollar perp rendered in ~9% axis steps and overlay labels collapsed. Precision
  now derived from price magnitude (`chartPrecisionFor`, ~5 sig figs, clamp [2,8]).
- **Fix: design §10 never wired** — Charts tab now badges live-signal pairs
  (LONG/SHORT pill), floats them to top, and opens their chart WITH the overlay.
  Reads the SWR-cached open-signals stream (same key as Signals tab → no new engine
  load).
- **Fix: poll didn't pause on background** — 2s kline poll stops on pause, resumes
  with catch-up tick (`WidgetsBindingObserver`).
- **Fix: static overlay** — signal re-read every 30s (SWR list); BE-shift moves the
  stop line to entry live, status changes propagate; redraw only on payload change.
  Also TF-switch race-guarded (load generation + poll cancel).
- **Phase 2:** EMA 21/50 + SMA 7/25/99 (the owner's mover MA stack) + RSI 14
  (bottom band, swaps with volume — vendored LWC 4.2.3 has no panes); indicator
  math Dart-side + unit-tested; toggles/TF persisted. Older-history pagination
  (endTime paging, ≤3000 bars, viewport preserved). Crosshair OHLC legend.
  Direction-coloured volume.
- **Deferred with reasons:** Signals-list sparklines (changes the owner-approved
  signal-card layout — owner design call; plus per-row Binance fetches want a
  caching design). `setTheme` bridge dormant (app is dark-only).
- **Verification:** `flutter analyze` clean on touched files; full app suite green
  (156, incl. 22 new). `pubspec.lock` untouched.

**Open at session end:** lumin-app #112 (CI running, self-check armed). No engine
changes this session. Session-38 queue (BTC-State backfill run on VPS → wiring
design) still pending — untouched here.

---

## 🟢 SESSION 38 2026-06-30 — The long bleed is the BTC macro downtrend, not broken longs → BTC-State soft-confirmation design + validation harness (360-v2 #675 merged, #676 open; 360ce-ops #51 open)

**Owner trigger:** "we've been negative for over a month, even a blind trader profits sometimes — why?" Analysed the live Profit export (305 signals, ~1mo) + the ops Profit PDF.

**Diagnosis — the story CHANGED from S34–37 (exit work is DONE; it's entries/selection now):**
- The what-if simulator's **perfect exit (TP1-full, no machinery) still nets −35.65%** (engine real −42.83%, ~7% apart, down from the ~19–25% gap of S34). **The exit fix landed — more exit tuning won't move the book.** The remaining loss is entry/selection edge.
- **Math:** win rate **42%**, avg win +1.14% ≈ avg loss −1.00% (**~1:1 realized R:R**), expectancy **−0.10%/signal**, breakeven needs **47%**. We're structurally ~5 pts of win-rate underwater. BE@+1% + expiries cut winners to ~1:1 while losses run full SL.
- **Scorer band inversion:** win-rate FALLS as confidence rises — 65-70→42%, 70-75→39%, **75-80→30% (−23.6%, worst)**, 80+→41% (only positive band). The score can't rank our own signals; the 75-80s are our worst.

**Owner's correction (the real root cause, backed by his BTC weekly chart):** longs aren't broken — they're **fighting a BTC macro downtrend** (BTC broke its **200-week MA in June 2026**, mirroring June 2022). Alts couple to BTC **harder on the downside than the upside**, so counter-trend longs get steamrolled while shorts work.
- **Confirmed in our data:** LONG **−25.1%** (34% win) vs SHORT **+9.65%** (46% win). The three counter-trend reversal-LONG cohorts — **SR_FLIP_RETEST long −21.75% (19% win), MOVER_TREND_PULLBACK long −12.78% (24%), LIQUIDITY_SWEEP_REVERSAL long −10.19% (26%)** — carry −44.7% over just **63 signals (21% of book)**. **Cutting only those flips the book −15.45% → +29.27%** on the same window. LONGs lose in EVERY regime; every SHORT cohort is flat-to-positive. The SAME paths on the SHORT side are fine. Keep-engine: VOLUME_SURGE_BREAKOUT long +10.8%/67% win, FAILED_AUCTION_RECLAIM both sides, DIVERGENCE long.

**Research (3 parallel agents, owner asked for "2-3 parallel different thinkings") — CONVERGED on one design:** a **graded BTC-State soft-confirmation**, NOT a 200MA on/off gate (owner rejected the slow "6mo shorts/6mo longs" binary):
- **Layer 1 — BTC-State score b∈[−1,+1]:** 5m/15m/1h EMA(8/21/55) stack + ATR-normalised slope + RSI (v1 price-only), vol-shrunk in chop; BTC.D dominance (rising-BTC.D + falling-BTC = max long penalty) + structure/VWAP deferred to v2.
- **Layer 2 — per-pair downside coupling w_pair∈[0,1]:** downside-beta × downside-corr on 15m returns; decoupled pairs (memecoins/own-catalyst) ≈0 auto-exempt, exemption REVOKED the instant BTC dumps.
- **Layer 3 — wiring:** `factor = 1 − k·|b|·w_pair·A_side` haircut at EMIT (not a gate); floor (never zero) + recompute-every-dispatch ⇒ **auto-restores longs when BTC flips** (owner's "if BTC moves up longs brighten"); counter-trend LONG penalised ~2× counter-trend SHORT (the downside asymmetry).
- **Code reality found:** engine ALREADY has `src/btc_direction.py::check_btc_direction_gate` — but it's binary AND only fires when BTC **1H AND 4H both** oppose, so it's silent during relief bounces / TRENDING_UP (where our longs bled). Plus `src/correlation.py` (corr-magnitude only, direction-blind). New design SUBSUMES both. **This wiring is OWNER-SIGN-OFF (scoring model + routing) — bring design after backfill confirms.**

**Shipped this session:**
- **360-v2 #675 (MERGED):** `scripts/btc_state_backfill.py` — read-only point-in-time validator (no look-ahead). Reconstructs BTC-State + per-pair downside coupling per historical signal, stratifies outcomes by side × BTC_STATE × coupling band. 14 unit tests (synthetic, no network). Acceptance test: long win-rate collapses as BTC turns hostile, concentrated in BTC-LED pairs while DECOUPLED longs survive, shorts don't collapse.
- **360-v2 #676 (OPEN, CI running):** fix — backfill must read `dispatch_timestamp` (emit), NOT the perf record's generic `timestamp` (close time) which would corrupt the reconstruction. Also passes through signal_id/confidence/mfe so output joins into ops. +1 test (15 total).
- **360ce-ops #51 (OPEN, CI running):** Profit-page **Direction what-if dropdown** (All / Shorts only / Longs only / Exclude counter-trend longs) — orthogonal to exit-strategy, makes the −15%→+29% counterfactual a 2-click knob. No BTC/Binance dep (keys on recorded side+setup). 6 tests.

**NEXT SESSION — do in order:**
1. **Run the backfill on the VPS** (after #676 merges + ~45s deploy): `docker exec 360scalp-v2-engine python scripts/btc_state_backfill.py --signals /app/data/signal_performance.json --out /app/data/btc_state_backfill.csv`. Read the verdict table against the acceptance test.
2. **If thesis confirms:** bring owner the graded soft-confirmation **wiring design** (owner-sign-off) — replace the coarse binary `check_btc_direction_gate` with the graded `factor` in `confidence.py`/scoring, env off-switch default ON, stamp `btc_state` on every signal. If it doesn't confirm, retune the design first.
3. **Layer-2 ops:** add **BTC-State-conditioned** filter options to the Profit Direction dropdown (drop counter-trend longs only when BTC hostile AND pair BTC-led), reading `btc_state_backfill.csv` from the data volume — ready once step 1 generates the CSV. (Owner asked whether to pre-wire this; left pending his call.)
4. **Scorer calibration** (separate lever): the 75-80 band inversion — likely dissolves once the counter-trend longs are cut; confirm band×side on fresh data before touching the scorer.

**Open PRs to check at session start:** 360-v2 #676, 360ce-ops #51 (both were in CI at session end; self-checks armed). 360-v2 #675 already merged. Pre-existing unrelated: 360ce-ops `tests/test_alerts.py` + `app/agent/*` ruff debt fail on clean main (redis/env), not ours.

---

## 🟢 SESSION 37 2026-06-29 — Mover pipeline made to actually fire + exit-model default fix + SR_FLIP shorts-only (merged: 360-v2 #666–#672, 360ce-ops #48/#49/#50)

One long arc: get the promoted movers to actually trade, then fix the exit logic that was bleeding the whole book, then cut the worst-bleeding direction. Built the diagnostic that found each wall, fixed each in turn.

**Mover pipeline — from "Promoting (0)" to signals firing:**
- **#666** — admit outside-top-75 movers into the promotion universe. With `TOP50_FUTURES_ONLY=true`, `pair_mgr.pairs` is capped at the top ~75 by volume and both promotion sources keyed off `pair_mgr.pairs.get(symbol)` → real movers (GUAUSDT −23%, SKYAIUSDT −44%) resolved to `None` and were silently dropped. The `!ticker@arr` detector sees the whole board; now it captures `(24h %change, quote_vol)` per symbol and the scanner admits outside movers as synthetic TIER3 pairs (`_ensure_mover_pair`), evicted on promotion expiry.
- **#667 / #668 / #670** (engine) + **ops #48 / #49 / #50** — per-pair "Why not firing" column on the ops Pairs page. Built incrementally: in-evaluator reason capture (#667) → scanner-side pre-eval skip capture (#668, the all-`—` was telling us movers were skipped *before* evaluation) → specific skip reasons instead of generic `channel_skipped` (#670). This diagnostic is what surfaced every subsequent root cause.
- **#669 — THE mover bug.** The mover spread gate compared `ctx_for_chan.spread_pct` (a **percent**, 0.5 == 0.5%) against the literal `0.005` — i.e. 0.005%, ~100× too tight — so it skipped **every** promoted mover before evaluation. Its own log said "> 0.5% — skip", so 0.5% was always the intent; written as a fraction by mistake. Fixed via env-tunable **`MOVER_MAX_SPREAD_PCT`** (default 0.5). After this, movers reached the evaluators and MOVER_TREND_PULLBACK started firing (TURBO, RIF, US, BEL, PENDLE all `✓ fired`).
- Note for next session: **MOVER_AVWAP_SCALP has not fired yet** — every mover signal so far is MOVER_TREND_PULLBACK. Watch whether the AVWAP rider's anchor+slope+pullback gate is too strict.

**Exit model — the −18% leak (#671, owner-sign-off, owner-directed):**
- Profit-Lab (233 closed signals, ops Profit page): engine real exits net **−18.13%** while "SL→entry once +1% in profit, then close 100% at TP1" nets **−0.23%** (+17.89% edge). Avg MFE +1.55% — signals go green then give it back. **The leak is the exit logic, not the entries.**
- Root cause: the Session-34 model (BE@+1%, TP1-full, pre-TP off, loose invalidation) was wired into the **execution FSM** only. **`trade_monitor`** — the signal tracker that drives the Profit page + what a signal-follower experiences — still ran the OLD model: 40% partial at TP1 + TP2/TP3 runner, BE only on TP1 hit, structural/trailing invalidation kills. That mismatch was the −18%.
- Fixed: `trade_monitor` engine-default exit now = BE→entry at +1% MFE (ratchet-only, pre-TP1) + full close at TP1 (`_close_full_at_tp1`) + no engine-wide invalidation. Gated by **`BE_THEN_TP1_DEFAULT_ENABLED`** (default on, env-reversible). **Per-user opt-in for pre-TP / invalidation preserved** (handled by `_check_per_user_invalidation` + FSM) — this flag governs only the engine's default book. Tradeoff: TP1-full forgoes the occasional TP2/TP3 runner; backtest still nets +17.89%.

**SR_FLIP shorts-only (#672, owner-sign-off, owner-directed stopgap):**
- SR_FLIP_RETEST is the biggest single drag (−16.6% / 85 signals) — but one-sided: SHORT +5.11% (52% win), **LONG −21.75% (19% win)**, losing in every regime (9% win even in TRENDING_UP). Win rate is exit-independent → an entry-quality problem the #671 exit fix only half-addresses (SR_FLIP → ~−8.8% under the new exit).
- Gated longs off by default via **`SR_FLIP_LONG_ENABLED`** (env-reversible); shorts unaffected. **Explicitly a tourniquet, not a cure** — owner's words. Follow-up tracked as a GitHub issue: investigate *why* SR_FLIP long flips fail and fix-or-drop the long thesis (do it on a fresh post-#671 data window, not stale numbers).

**New env tunables this session:** `MOVER_MAX_SPREAD_PCT` (0.5), `BE_THEN_TP1_DEFAULT_ENABLED` (true), `SR_FLIP_LONG_ENABLED` (false).

**Watch next (fresh data window — counters are cumulative, old closed signals reflect old exits):** Profit page "engine real exits" should converge from −18% toward the simulator's −0.23%; mover givebacks (POWRUSDT-type +5% MFE → invalidated) should convert to BE/TP1; SR_FLIP drag should drop with longs gone.

---

## 🟢 SESSION 36 2026-06-27 — Referral/invite-a-friend + manual tier-grant control (merged: 360-v2 #654/#655, lumin-app #106, 360ce-ops #43)

**Two features shipped end-to-end this session, both across multiple repos:**

1. **Referral / invite-a-friend (Phase 1).** Engine-side code generation, claim, and stats API (360-v2 PR #654) + app-side share sheet, repository methods, and onboarding capture (lumin-app PR #106). Both merged.

2. **Manual tier-grant (owner comp for testers/influencers).** Built per owner instruction *after* the referral PRs merged, with a default expiry (no permanent comp via this path):
   - **360-v2 PR #655** (engine): `GET /api/admin/users/lookup` + `POST /api/admin/grant-tier`, owner-gated (`owner_required` dependency, same as kill-switch/reset-signals). Reuses the existing `UserStore.aset_tier()` write path — the same one the Play Billing verify flow and the `/internal/billing/grant` webhook use, so this is a third caller onto one source of truth, not a parallel entitlement system. `tier` accepts `free` / `assist` / `auto` (the current two-tier automation paywall, B16) — **not** a single legacy "pro" tier; this was caught mid-implementation after pulling 45 commits of upstream drift and correctly rescoped before writing code. `duration_days` defaults to 30, range 1–365; `tier=free` revokes immediately and ignores duration. 11 new tests, full suite 5828 passed.
   - **360ce-ops PR #43** (ops UI): `EngineApiClient.user_lookup()` / `.grant_tier()`, a new `/control/users` route + template (lookup form → current tier display → grant form with tier/duration/reason), wired into nav next to Control. Same control doctrine as every other write surface here: owner-gated via the static Bearer token, audited via `app/audit.py` (best-effort, non-blocking), PRG + JS confirm before the grant POST. 9 new tests, full suite 232 passed.

**Both judged not owner-sign-off items** (no Position FSM / signing-service / scoring / paid-channel-routing touch) — auto-merged once CI was green and review threads were empty, per the Change-management Protocol.

**Environment note (360ce-ops):** the sandbox this session ran in had a stale dependency set (`itsdangerous` and `python-multipart` missing, wrong `jinja2`/`starlette` versions resolved). Reinstalling from the repo's own `requirements.txt` fixed it — not a code issue, just a reminder that `pip install -r requirements.txt` should be step zero in a fresh container before trusting a red test run.

---

## 🟢 SESSION 35 2026-06-25 — Mark-price-triggered BE SL shift at +1% MFE (engine, merged PR #646)

**Owner trigger:** simulation in `ops.luminapp.org/profit` showed that signals often move 1%+ in our favour then reverse to the stop, giving back the unrealised gain. With the new TP1/SL-only default (Session 34 PR #645), there is no pre-TP to bank profit early — the loss is taken in full when SL hits.

**Simulation evidence (499 closed signals, live window, `exit_sim.py`):**
| Strategy | Total PnL | Edge vs engine real exits |
|---|---|---|
| Engine real exits (mixed legacy) | −29.28% | — |
| TP1-only (current default) | −11.51% | +17.77% |
| **BE at +1.0% → TP1** | **−10.62%** | **+18.67% (+0.89% vs TP1-only)** |
| BE at +0.5% → TP1 | −6.53% | +22.75% |

Owner signed off: **"keep at 1%"** (1.0% chosen over 0.5% to avoid scratching signals that dip briefly then continue to TP1; avg TP1 distance is 2.29%).

Also shipped in this session (360ce-ops):
- **PR #37** (`feat/be-stop-tp1-diagnostic`): BE simulation strategy + TP1-miss diagnostic banner on the profit tab — merged.
- **PR #38** (`fix/be-tp1-namefix`): hotfix `NameError` in `_build_rows` — merged.

### Shipped — PR #646 (360-v2, engine, owner-sign-off: BE shift + FSM)

| Change | File | Why |
|---|---|---|
| `BE_SHIFT_TRIGGER_PCT = 1.0` (env-overridable) | `config/__init__.py` | Single-source trigger threshold |
| `be_shift_fired: bool = False` on `Position` + Firestore serde | `src/execution/position_state.py` | Prevents double-fire across ticks + survives restart |
| `maybe_fire_be_shift()` async function | `src/execution/pretp_dispatcher.py` | Cancel original SL, place STOP_MARKET at entry via `coid_sl_be`; wired into `_on_tick()` after `maybe_fire_pretp` |
| 8 unit tests | `tests/test_be_shift.py` | LONG/SHORT fire, below-threshold no-fire, double-fire guard, sl_order_id==0 guard, pretp_fired guard, placement-failure retry |

**Cost:** zero additional Firestore reads per tick — reuses the existing in-memory live-position index. One `put_position` write per position when the shift fires (one-time per signal life).

**FSM integration (existing infrastructure):**
- When BE-SL fires, the FSM routes via `coid_sl_be` → `_apply_sl_be_fill()` → `close_reason="SL_BE"` → CLOSED ✓
- When TP1 fires (full close): `sl_order_id == 0` (already zeroed at BE-shift time) → skip cancel; Binance auto-cancels the resting BE-SL (`closePosition=true`) when position reaches zero ✓
- Pre-TP users unaffected: `pretp_fired=True` guard + PRE_TP_FIRED state excluded from OPEN-position query ✓

### VPS action required

On next `main` deploy (auto ~45s after merge), the engine image will include the BE-shift logic. No env vars required — `BE_SHIFT_TRIGGER_PCT=1.0` is the default.

To verify it is live after the first position crosses +1% MFE:
```bash
docker logs 360scalp-v2-engine --since 1h | grep "be_shift: triggering"
docker logs 360scalp-v2-engine --since 1h | grep "be_shift: placed BE-SL"
```

### REMAINING (from Session 34)
1. **lumin-app (PR 2):** outcome-summary card redesign per owner's reference mockup — highlight positive result + "Max profit reached before SL", faded-but-visible closed-signal bars, active-signal trade button; copy aligned to the new model. **In progress.**
2. **360ce-ops:** Profit-Lab data window still maturing after Session-34 default flip. Wait for fresh window before judging the TP1-only + BE-shift real-book edge.
3. **VPS:** verify `.env` does not pin old pre-TP / invalidation defaults (`PRE_TP_GRAB_FRACTION`, `INVALIDATION_MODE_DEFAULT`, `PRE_TP_ENABLED`) — clear them if so.

---

## 🟢 SESSION 34 2026-06-24 — Default exit reversed to TP1-full + fixed SL (pre-TP & invalidation now opt-in)

**Owner trigger (Profit-Lab screenshots, `ops.luminapp.org/profit`):** "pre-TP and
invalidations aren't working and are making more losses; taking full profit at TP1
makes more sense. No pre-TP, no invalidations — pure signals with TPs and SL, and
Max profit reached before hitting SL." Plus an app redesign brief (see lumin-app).

**Data basis (the Profit-Lab, 494 closed live signals, net of 0.07% fee):**
| Exit method (TP/SL only) | Total P/L | Edge over engine real exits |
|---|---|---|
| **TP1-full (100% @ TP1)** | **−6.65%** | **+19.14%** |
| 50% @ +1% · 50% TP1 | −14.09% | +11.70% |
| 50% TP1 · 50% TP2 | −16.44% | +9.35% |
| TP1/TP2/TP3 thirds | −19.70% | +6.09% |
| Flat +1% (100%) | −21.53% | +4.26% |
| **Engine real exits (pre-TP + invalidation)** | **−25.79%** | baseline |

Every simple exit beat the engine's machinery; **TP1-full beat it most**. The exit
logic, not the entries, was giving back the edge. *Honest caveat told to owner:
TP1-full is still slightly net-negative (−6.65%) — it stops most of the bleed but
the residual gap is entry quality + fees, the next lever. UI must not imply green.*

**Owner decisions (AskUserQuestion):** exit shape = **TP1-full @ 100%**; backstop =
**TP-or-SL only + 2h reconciler** (no timed exit; naked-SL invariant + caps stay);
per-user pre-TP/invalidation dials **remain usable**, engine **default** = TP1+SL.

### Shipped — PR 1 (360-v2, engine, owner-sign-off: FSM + B-rules)
Three env-overridable default flips + the FSM fix that makes them safe:
| Change | File | Why |
|---|---|---|
| `PRE_TP_GRAB_FRACTION` 0.50 → **0.0** (pre-TP disabled by default) | `config/__init__.py` | no banking on the default path |
| `INVALIDATION_MODE_DEFAULT` `tight` → **`loose`** (loose short-circuits to SL/TP-only) | `config/__init__.py`, `trade_monitor.py` | the "TP/SL only" lab method |
| New `TP{1,2,3}_CLOSE_FRACTION` (default **1.0/0.0/0.0** = TP1-full); dispatch reads them lazily | `config/__init__.py`, `signal_dispatch.py` | TP1 closes 100%; ladder restorable via env (B8) |
| **`_apply_tp1_fill` terminal-close fix** — on a full TP1 close go CLOSED + cancel SL, place NO breakeven-SL | `position_fsm.py` | without this, TP1=100% stranded the position in TP1_HIT with an orphaned BE-SL on zero qty (only the 2h reconciler clearing it) |
| Monitor `_check_pre_tp_grab`: grab ≤ 0 → return False (no engine-book banking) | `trade_monitor.py` | grab=0 must truly disable, not clamp up to 0.30 |
| `PretpSettings.grab_fraction` `ge=0.30` → **`ge=0.0`**; `_coerce_pretp` preserves 0 (disabled), clamps positives into [0.30,1.0] | `api/schemas.py`, `api/user_overrides.py` | the resolved view for a fresh user is now 0.0 — was a 422 (real end-to-end bug, not a test issue) |

Per-user opt-in still fully wired: a user who sets `grab_fraction>0` /
`invalidation_mode∈{standard,tight}` gets it forwarded at dispatch (tests prove it).

**Tests:** +6 new (TP1-full terminal close; default-grab-disables-pre-TP;
loose-default-suppresses-invalidation; env-override-restores-ladder; full-mgmt
default-no-pretp + user-opt-in). Updated the mechanics suites (pre-TP, dispatch,
trade-monitor invalidation, audit, btc-overlay) to pin their opt-in mode rather
than assume the old default. Full suite green. ruff clean on `src/`+`config/`.
Doctrine: OWNER_BRIEF §2.3/§3.2/§3.9/B17 rewritten; profile **D (TP1-full)** is
the new default.

### REMAINING
1. **lumin-app (PR 2):** outcome-summary card redesign per owner's reference mockup
   — highlight positive result + **"Max profit reached before SL"**, faded-but-visible
   closed-signal bars, active-signal trade button; copy aligned to the new model
   (drop "Pre-TP banked / SL→BE" as the default framing). **In progress.**
2. **360ce-ops:** Profit-Lab already exposes the exit-method comparison; once the
   new default has a fresh data window, re-read to confirm the live book tracks the
   −6.65% sim (don't judge early — counters are cumulative).
3. **VPS:** new default ships live on `main` deploy. If `.env` pins the old values
   (`PRE_TP_GRAB_FRACTION`, `INVALIDATION_MODE_DEFAULT`, `PRE_TP_ENABLED`), clear
   them so the code defaults take effect.

---

## 🟢 SESSION 33 2026-06-24 — Monetization corrected to two-tier auto-trade model (signals free)

**Owner correction mid-rollout:** the product is NOT "pay to see signals." Signals +
entry/SL/TP + analysis are **FREE**. The paywall is **trade automation**, two monthly
Play subscriptions:
- **Assist** `lumin_assist_monthly` **₹1000/mo** — one-tap "take trade" (app places
  the order client-side on the user's own Binance keys).
- **Auto** `lumin_auto_monthly` **₹2000/mo** — hands-off server-side auto-execution.

Tier hierarchy `free < assist < auto`. This reworks the Session-32 Play Billing landing
(which wrongly locked levels behind a single `paid` tier).

### Shipped (engine — two-tier rework, owner-sign-off PR)
- `auth.py`: `ASSIST_TIER`/`AUTO_TIER` + `tier_rank`/`can_assist`/`can_auto` hierarchy.
- **`signal_dispatch` money-path gate**: hands-off execution runs ONLY for `auto`
  users (`_resolve_user_tier`, 30s cache, expiry-aware, **fails closed**). Reversible
  via `AUTO_TRADE_TIER_GATE_ENABLED` (default ON). End-to-end test proves a free user
  is skipped, an auto user dispatched.
- `billing_play`: product→tier map (`GOOGLE_PLAY_PRODUCT_TIERS`); `entitlement_for`
  returns assist/auto by product. `server.py` expiry-downgrade covers both tiers.
- Tests: 53 dispatch + 40 billing/tier green; ruff clean.
- Doctrine: B16 rewritten (two-tier automation paywall), B1/§2.2 — signals free.

### Owner / business status (2026-06-24)
- Engine billing armed on VPS (`configured=True`); Firebase SA granted Android
  Publisher access.
- **Payments KYC submitted via BillDesk** (individual a/c, Finance category — accurate
  for crypto auto-trade; NOT "Education"). Awaiting Google/BillDesk payout approval
  (days). Min ₹1000 / max ₹3000 ticket; income ₹750k.

### REMAINING
1. **lumin-app**: stop locking levels (free); gate one-tap take-trade by ≥assist; gate
   live auto-trade by =auto; subscription page → two plans (₹1000/₹2000).
2. **Play Console**: create `lumin_assist_monthly` + `lumin_auto_monthly`; Internal
   testing release; license tester; Financial features declaration.
3. ⚠️ **Legal**: charging for automated crypto execution — keep a legal sanity-check
   current (Play financial-services + Indian regulatory exposure).

---

## 🟢 SESSION 32 2026-06-23 — Monetization pivot: Google Play Billing (Telegram payment retired); engine entitlement core shipped

**Owner trigger:** Play Console granted **production access** (screenshot). Owner: "we
need to proceed with Google Play billing, because Telegram is presently banned in
India." Approved the full plan + "update owner brief."

### Doctrine decision (owner-approved — Business Rule change, owner-sign-off)
- **B16 rewritten:** Google Play Billing is the v1 purchase path; **Telegram-bot
  payment retired** (a bot paywall reaches no one in a Telegram-banned region).
  Subscription positioned as **education / market-analytics content**, never
  "trading signals" — Google Play Payments policy bars *investment-consulting*
  services from Play billing, so the framing is load-bearing.
- **B1 reconciled:** paid signals deliver **in-app first** (Lumin Signals feed,
  paid-tier-gated). Telegram paid channel = optional single mirror only.
- Policy basis (verified against Google's own pages): Payments policy
  ("stock trades, investment consulting … should not use Google Play's billing
  system") + Financial Services declaration + India alternative-billing (−4%).

### Key finding — the entitlement plumbing already existed
Delivery is **already in-app** (`signals_page.dart`, free-tier gate locks
entry/SL/TP). The engine already had `UserStore(tier, paid_until)` +
`aset_tier()` + `mint_user_token(tier, paid_until)` + JWT tier-claim enforcement.
The ONLY missing link was: **Play purchase → server-side verify → set_tier**.
Grep confirmed zero pre-existing Play/billing code.

### Shipped this session (engine — fully wired, no scaffold)
| Area | What |
|---|---|
| Config | `GOOGLE_PLAY_*` env (package name, service-account JSON, allowed product IDs, RTDN audience, feature flag) — all env-overridable, SA key never logged. |
| `src/api/billing_play.py` | `PlayBillingVerifier` — service-account OAuth2 token (RS256 via google-auth, cached) → Google Play Developer API `purchases.subscriptionsv2.get`; derives entitlement (ACTIVE/GRACE/CANCELED→paid until expiry; ON_HOLD/PAUSED/EXPIRED/REVOKED→free); acknowledges pending purchases; parses RTDN Pub/Sub envelopes. |
| `src/api/play_purchases.py` | `PlayPurchaseStore` — maps `purchase_token → user_id` (so RTDN, which has no JWT, resolves the user); tracks product/expiry/state; handles `linkedPurchaseToken` on upgrade/resignup. |
| `src/api/server.py` | `POST /api/billing/play/verify` (user-JWT authed) + `POST /api/billing/play/rtdn` (Pub/Sub push, audience-verified). Refresh path consults UserStore so an expired sub downgrades to free on next JWT refresh. |
| `main.py` + `bootstrap.py` | construct + thread `PlayBillingVerifier` + `PlayPurchaseStore` (both isolated + single-process boot sites). |
| Tests | verifier entitlement mapping, acknowledge, RTDN parse + re-fetch, token→user resolution, endpoint auth, refresh downgrade. |

### REMAINING (next increments)
1. **lumin-app:** `in_app_purchase` plugin; replace `subscription_page.dart`
   Telegram CTA with Play purchase + restore-purchases; education/analytics copy;
   drop reader-app language; verify→JWT-refresh.
2. **lumin-legal:** auto-renew / billing terms + data-safety alignment.

### OWNER ACTIONS (Play Console / GCP — only owner can do; blocks app increment)
- Create subscription products (IDs → into `GOOGLE_PLAY_PRODUCT_IDS`); base plans + pricing.
- File **Financial features declaration**; reframe listing + data-safety as education/analytics.
- GCP **service account** w/ Android Publisher access, linked to Play Console → env `GOOGLE_PLAY_SA_JSON`.
- **RTDN**: Pub/Sub topic + push subscription → engine `/api/billing/play/rtdn`.

---

## 🟢 SESSION 31 2026-06-20 — Per-user PATH + REGIME live eligibility (shipped); paper-per-user + Full/Entry sequenced

**Owner trigger:** "We give per-user symbol choice but not which paths / which
regime — make those flexible too, neatly in auto-trade settings, paper + live
each individual, with reset to default. Reset-to-default also missing on
Invalidation + Pre-TP. Signals tab: tapping a symbol → take signals **full**
(entry+exit+pre-TP+invalidation) vs **entry-only** (engine places entry, user
manages). Add to CLAUDE.md: no shortcuts / scaffolds / fast-tracks, production-
grade only. No dark flags (we're testing, no users)."

### Doctrine + decisions
- **CLAUDE.md** operating-standard strengthened: no scaffolds / no fast-tracks /
  no stub-now-wire-later — a setting the engine *stores but doesn't consume* is a
  banned scaffold; money-path features ship storage + dispatch/FSM consumption +
  UI together. (No-dark-flags was already doctrine in § Project Phase.)
- Owner decisions (via AskUserQuestion): **entry-only on LIVE = entry + protective
  SL (never naked) then skip pre-TP/TP/invalidation**; **Full/Entry saved per
  symbol**; **make paper per-user** (so paper selectors are real, not a scaffold).

### Shipped this session (fully wired + tested)
| Area | What |
|---|---|
| Engine | `user_auto_trade_settings.path_preference` + `.regime_preference` (JSON; NULL=all, []=block-all) — schema, idempotent migration, coerce (path uppercase; regime via `_normalise_regime_input`), persistence, `resolve_auto_trade_preferences_uid` resolver. |
| Engine | LIVE gate in `dispatch_signal_to_active_users` — skips user silently (pre-signing) when `setup_class` ∉ path pref or `regime_label` ∉ regime pref. Symbol gate (position_fsm) unchanged. |
| Engine | `GET /api/auto-trade/runtime-status` now returns `allowed_paths` (from `ACTIVE_PATH_PORTFOLIO_ROLES` — single source of truth, no app drift) + `regime_options`. |
| App | `AutoTradeSettings` model + `AutoTradeRuntimeStatus` carry path/regime; new `eligibility_preference_page.dart` (shared Path + Regime picker, preset all/custom/block); "What auto-trades for me" card in Auto-trade settings (Symbols/Paths/Regimes rows + one **Reset to default**). |
| App | Pre-TP + Invalidation **Reset-to-default** now always visible (was hidden via `if (!_usingDefaults …)` → looked missing on a default page). |
| Tests | +11 engine tests (store 8, dispatch 3); affected suites green: 197 pass (user_overrides 91, signal_dispatch 50, status_routes 20, tripwires + others). |

| Engine | **Per-symbol Full / Entry-only** (Signals-tab tap): `user_symbol_management` table + `resolve_symbol_management_uid`; entry-only reuses tested levers at dispatch (`grab_fraction=0` + `invalidation_mode='loose'` + `management_mode='entry'`) and `place_signal` lays NO TP ladder. **Entry + protective SL still placed** — never naked (B12/B18). `GET/PUT /api/settings/user/symbol-management`. |
| App | Signals-tab detail sheet: "AUTO-TRADE {SYMBOL}" section, two highlightable tiles (Take full / Entry only), persisted per symbol; repo `fetchSymbolManagement`/`setSymbolManagement`. |
| Tests | +9 more (store/resolver 6, dispatch 2, FSM bracket-skip 1) → 329 pass across affected suites incl. API smoke. |

Scope note: path/regime + per-symbol management are the **LIVE** filters today
(live dispatcher is per-user). Paper selectors + per-symbol management on paper
land with Increment 2.

### Per-user paper engine — Phase 3 (PR #636, owner-sign-off, NOT merged)
Owner decisions this session: **isolated paper registry** (not in-FSM); **namespace
per user, one source** (no duplication; engine-wide paper = aggregate of per-user
books); **per-user only** (paper fires only for paper/both opt-in — operator opts in
like any user; no always-on operator book).

**Built + unit-tested (inert — every change additive/defaulted; existing suites pass
unchanged; 46 tests green):**
- `paper_symbol/path/regime_preference` columns + migration + coerce +
  `resolve_paper_preferences_uid` (independent of the live triple).
- `PaperOrderManager` per-user `pnl_path` / `trades_db_path` / `pnl_history_mode`
  (default = legacy shared paths → inert).
- `trade_records`: every helper takes optional `db_path` (per-user SQLite files);
  `iter_user_db_paths` + `list_trades_all_users` / `count_trades_all_users` aggregate.
- `src/execution/paper_book_registry.py` — `PaperBookRegistry` (one book/user) +
  `PaperBookFanout` (drop-in for the single `PaperOrderManager`; fans lifecycle out
  to eligible users; entry-only skips pre-TP/TP, survives invalidation, closes on SL).

**ACTIVATION LANDED — gated behind `PAPER_PER_USER_BOOKS` (default OFF), atomic
write+read flip, both flag states fully wired (owner approved "gated, default OFF"
2026-06-20). Engine #1/#2 below DONE; app + ops (#3/#4) still pending.**
- `config.PAPER_PER_USER_BOOKS` (default `false`) + `PAPER_BOOKS_DIR` — kill switch,
  not a dark flag. OFF = legacy shared-book path untouched; ON = per-user fanout.
- `main.py._build_paper_order_manager()` builds the fanout at BOTH construction sites
  (boot + `set_auto_execution_mode`); `PaperBookRegistry` now threads position sizing +
  a **per-user RiskManager factory** (each book gets its own daily-loss/concurrency
  limits — no shared global paper cap).
- `pnl_history` aggregate readers (`get_*_aggregate("paper")` / `reset_aggregate`) sum
  `paper:*`; fanout gains `positions_for_user` / merged `_positions` / `pnl_history_mode_for`
  / `trades_db_path_for`.
- Read repoint (gated; OFF → unchanged window path): `build_pulse`, `build_positions`,
  `build_auto_mode` header + engine-wide aggregate, `build_pnl_history` read per-user;
  `/api/trades` lists the user's own DB via `list_trades(db_path=…)`; paper reset wipes
  every `paper:<uid>` bucket.
- **First unit coverage for the (previously untested) snapshot builders** — per-user
  isolation (no cross-user PnL leak) + OFF-path fallback. 61 tests green.

**VALIDATION GATE (before promoting ON to default):** merge to `main` (deploys OFF, no
behavior change) → set `PAPER_PER_USER_BOOKS=true` + restart paper engine on the VPS →
confirm per-user snapshots populate + `data/paper_books/paper_*_user_<uid>.*` files
appear → then flip ON as the default.

**REMAINING:**
3. App **paper** eligibility selectors + per-symbol management on paper (lumin-app).
4. 360ce-ops engine-wide paper reads → `paper:*` aggregate.

Sign-off flags raised to owner: (a) per-user RiskManagers = no global paper risk cap;
(b) operator paper-reset wipes all users' buckets. Both deemed correct defaults.

---

## 🟢 SESSION 30 2026-06-19 — Raw-Edge diagnostic tab + 60-min invalidation window; MOVER_TREND_PULLBACK gate root-caused

**Owner trigger:** "performance still negative — suspect pre-TP and invalidation;
add an ops view of how signals do WITHOUT them; widen the invalidation window;
and what about that new path (MOVER_TREND_PULLBACK) still firing nothing."
Worked off the attached `signal_performance` (365 closed, Jun 15–19),
`signal_history` (500), `invalidation_records` (154), and a fresh truth report.

### Shipped + MERGED this session
| PR | Repo | What |
|---|---|---|
| [#16](https://github.com/mkmk749278/360ce-ops/pull/16) | 360ce-ops | **Raw Edge** tab — signal edge *without* pre-TP & invalidation: MFE reach, exit attribution (true SL vs pre-TP vs invalidation vs expiry), capture (realized÷MFE), give-back, + invalidation PREMATURE/missed-R per family. Read-only. |
| [#628](https://github.com/mkmk749278/360-v2/pull/628) | 360-v2 | Invalidation-audit observation window **30→60 min** (`INVALIDATION_AUDIT_WINDOW_SEC` 1800→3600). Our scalps run 5–60 min, so 30 min judged kills before the hold elapsed. Observation-only; no FSM change. |

### Diagnosis from the Raw Edge data (the honest answer to the owner's suspicion)
- **Pre-TP IS capping winners.** Book-level *capture* = **6%** (avg MFE 0.53% vs
  avg realized 0.033%); avg give-back **0.51%/signal**. 175 pre-TP signals banked
  +0.39% avg vs +0.85% true peak; 30% reached MFE ≥ 1% and banked a sliver — the
  residual "runner" (§3.2) is dying at break-even instead of running.
- **The 80+ band is the worst** — capture **−7%** (only negative band). High-conviction
  signals reach the biggest MFE (one SR_FLIP +2.11% MFE banked 1.05; a DIV_CONT
  +1.61% MFE realized 0.65) and pre-TP+BE caps them hardest, while the few losers
  take full adverse. Asymmetry inverted exactly where conviction is highest.
- **Invalidation is mostly PROTECTIVE — NOT the main drag.** 113 PROTECTIVE vs 22
  PREMATURE; `momentum_loss` +0.33R/kill (68 prot vs 10 prem). PREMATURE give-back
  (37.8R total) concentrates in `trailing_invalidation` (27% premature rate) and
  `adverse_excursion` — tunable, but gutting invalidation loses money. Told owner
  the invalidation half of the suspicion is largely **not** supported by data.
- **Book context:** raw +12.2% / 365 = +0.033%/sig → net-negative after ~0.07%
  raw round-trip fee. BUT RANGING bleed is gone (+0.029 avg) and SR_FLIP is now
  ~breakeven (−0.012, was −4.80) — Session-29's 3 flags worked. FAR (+0.096) /
  DIV (+0.111) / BDS (+0.277) are the profitable engine — leave alone.

**Next lever (owner-sign-off, FSM):** regime-per-exit (§3.2b) — pre-TP HIGH/OFF for
trend-aligned + the 80+ band, let the residual run. Slice the Raw Edge tab by
`entry_regime` first, bring owner a design before any FSM code.

### MOVER_TREND_PULLBACK (16th path) — root-caused: 0 emissions = a GATE block, not the evaluator
Truth report: ~58k generated, **99.9% gated, 0 emitted**, never reaches the
confidence gate. The evaluator is sound and returns real signals; candidates die
inside `_prepare_signal`'s gate chain.
- **Root cause:** the path is mapped to family **`trend_following`** (PR #627), and
  `trend_following` is in `_SCALP_RANGING_LOW_ADX_BLOCKED_FAMILIES`
  (`scanner/__init__.py:4667-4694`) — any 360_SCALP signal is hard-rejected when
  the entry-TF context is RANGING with ADX < 15. A trend-pullback fires *at* the
  pullback, which reads RANGING/low-ADX on the 5m entry TF **by design**, so the
  gate kills it before scoring. Same failure-mode as the §3.6a scoring bugs, but
  at the **gate** layer (the scoring side was already fixed in #621 via
  `htf_trend_aligned`). **TPE corroborates** — also `trend_following`, 7,742
  generated → 4 emitted.
- **Proposed fix (owner-sign-off — gate + new path; NOT shipped):** exempt
  trend-pullback setups carrying `htf_trend_aligned=True` (MOVER_TREND_PULLBACK's
  MA stack IS its HTF trend; TPE sets it on the 1H-trend path) from the
  RANGING-low-ADX family block — mirrors the #621 doctrine. Narrower option: a
  MOVER_TREND_PULLBACK-only carve-out. Also consider adding it to
  `_SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS` (§3.4: mover continuation fires in any HTF
  context). **Awaiting owner decision before shipping.**

---

## 🟢 SESSION 29 2026-06-18 — SR_FLIP/RANGING bleed remedies ACTIVATED on VPS (3 dark flags flipped live)

**Owner trigger:** "analyse signals quality after yesterday's PRs — where are we lagging."
Pulled a **fresh** truth report (monitor-logs, 2026-06-18 07:34 UTC — post-Session-28)
+ the attached `signal_performance` (277 closed sigs, Jun 15–18), `signal_history`
(500), `invalidation_records` (118).

### Finding: yesterday's work didn't touch the bleed
Session 27–28 (#614–#621) was all **scoring/generation on the dead paths**
(VSB/BDS/MA_CROSS/TPE) — correct work, but those paths are a volume rounding error
(VSB n=2, BDS n=7, TPE n=4 in the 277). The actual P&L drag is **unchanged since
Session 24**:
- **SR_FLIP_RETEST −4.80 (n=108 = 39% of all signals).** Upside-down R:R: avg win
  +0.33 vs avg loss −0.42, 63 SL hits. Concentrated in **RANGING −5.50 (60 sigs,
  36 SL)**.
- **RANGING regime −2.22** (47% of volume) — the one losing regime besides tiny VOLATILE.
- **LONGs −2.50 (n=142)** vs SHORTs +7.43; 7 of 8 worst losers are LONG in
  RANGING/UP/VOLATILE — the slice #615's TRENDING_DOWN gate does NOT catch.
- Book gross +4.94% raw (~thin); 24 full-SL events (−25.6 raw) wipe most of the
  +49.4 pre-TP banking. Net ≈ breakeven-to-negative after fees.
- Profitable engine (leave alone): DIVERGENCE_CONTINUATION +6.94, FAILED_AUCTION_RECLAIM +4.37.
- Invalidation audit healthy (76% PROTECTIVE, momentum_loss +0.36R/kill) — the
  KILLS aren't the problem; RANGING SR_FLIP entry quality + exit geometry is.

**The disconnect:** the remedies for this bleed (#603/#604/#608/#613) were merged
and shipped **dark up to 11 days ago and never activated**. We'd been adding
scoring polish to paths that barely fire while the fix for 39% of our volume sat
switched off.

### Owner decision: activate the dark flags (one-shot, owner ran on VPS)
Three flags flipped live + engine `--force-recreate` (verified True×3):
| Flag | Effect |
|---|---|
| `RANGING_LOW_ATR_LOSER_SUPPRESS_ENABLED=true` | drops low-ATR RANGING SR_FLIP/LSR entries (pctile ≤25) — cuts the −5.50 slice at the gate |
| `SR_FLIP_PRETP_R_SCALING_ENABLED=true` | floors pre-TP at SL_dist×0.35R so wide-SL SR_FLIPs stop banking at 0.2R |
| `INVALIDATION_TRAILING_ARM_RSCALE_ENABLED=true` | trailing kill arms at min(0.80, 0.30+0.15×SL%) not flat 0.30R (global) |

`.env` backed up to `.env.bak.<ts>` before the change; one-line revert documented.
**No code shipped this session** — env-only activation. Expect signal VOLUME to drop
(RANGING SR_FLIP was 39% of flow) — intended trade, not a fault.

### NEXT SESSION — judge at +48h on a FRESH truth report (don't judge early):
| Metric | Baseline (this session) | Target |
|---|---|---|
| SR_FLIP `Avg PnL%` | −0.044 | → toward/above 0 |
| RANGING SR_FLIP slice | −5.50 (60 sigs) | → shrinking, fewer sigs |
| `trailing_invalidation` EV/kill | +0.09R (TUNE) | → above +0.10R (KEEP) |
| DIV + FAR | +6.94 / +4.37 | → unchanged (regression = back out) |

Shadow-confirm the drop volume:
`docker logs 360scalp-v2-engine --since 48h 2>&1 | grep -c "RANGING_LOW_ATR_LOSER_SUPPRESS"`

### Built this session (shadow-first): MOVER_TREND_PULLBACK — the mover continuation path
Owner studied live mover charts (AGT +108%, BTW −28%) and identified a real gap:
VSB/BDS are **one-shot ignition** detectors (swing-break + single retest; #1 reject
`breakout_not_found` 89k) — they catch the breakout candle and go silent for the rest
of the move. The recurring edge on a strong mover is the **continuation**: ride the MA
stack and re-enter every pullback to the MA. TPE is that logic but is locked out of
movers (mover allowlist = VSB+BDS only) and gated on a 1H structure young movers lack.

**New evaluator `_evaluate_mover_trend_pullback` (16th path), owner-approved:**
- Mover-only (self-gates on `smc_data['is_mover_promoted']`, stamped by scanner).
- 15m MA stack (SMA 7/25/99 — the owner's chart) decides direction; LONG gainers,
  SHORT losers. Entry = pullback tags fast-MA band + reclaim candle. SL beyond mid-MA,
  ATR-buffered. R-multiple TP ladder (1.0/1.6/2.5R). `htf_trend_aligned=True` (the stack
  IS the higher-context trend) → full regime affinity + volume-floor via
  `_FAMILY_TREND_PULLBACK` (§3.6a).
- **Ships LIVE** (`MOVER_TREND_PULLBACK_ENABLED=true` default — testing phase, no
  subscribers; see CLAUDE.md § Project Phase). Set the flag false for shadow-only
  fallback. CPU-only, no new reads/writes. Added to `_mover_evaluators` so it runs
  alongside VSB/BDS → the head-to-head the owner asked for (ignition vs continuation).
- 5 new tests; full local suite green (5,329 pass; 42 pre-existing env/dep failures
  confirmed on the stashed tree, none mine). Files: `config/__init__.py`,
  `channels/scalp.py`, `scanner/__init__.py`, `signal_quality.py`,
  `tests/test_mover_trend_pullback.py`, `tests/test_scanner.py` (count 15→16).

**Activation (after shadow window):** read `[SHADOW] MOVER_TREND_PULLBACK_WOULD_FIRE`
counts on the VPS to size opportunity, then `MOVER_TREND_PULLBACK_ENABLED=true` +
engine recreate. Compare VSB/BDS vs MOVER_TREND_PULLBACK on the truth report; keep the
winner(s).

### Session 29 follow-up — mover gate was too narrow (fixed)
First live check (VPS logs) showed the path live + registered but **0 emissions** —
root cause: the real movers (BTW −28%, ESPORTS +109%) enter the scan as
**universe/young pairs**, not via mover-promotion, so the `is_mover_promoted` gate
locked the path out of its own targets (BTW was logged as `young_pair_restriction`,
ESPORTS in the critical-pairs set; zero `MOVER PROMOT` lines in 3h). Fix: define
"mover" by **MA7↔MA99 stack separation ≥ `MOVER_TP_MIN_STACK_SEP_PCT` (3%)** instead
of promotion bookkeeping, and add the path to `_YOUNG_PAIR_EVALUATORS` so young
movers can run it. Now fires on a strong run wherever the pair sits; gently-trending
majors stay TPE's domain. Removed the now-dead `is_mover_promoted` scanner stamp.
Confirm live: `docker logs 360scalp-v2-engine --since 1h | grep -c MOVER_TREND_PULLBACK`.

### Still open after this (next levers, in order)
1. **LONG bleed** — −2.50, worst losers are LONG in RANGING/UP/VOLATILE; #615 only
   gates TRENDING_DOWN. Investigate extending the longs regime gate (shadow-first).
2. **SR_FLIP entry-quality re-tighten** (#612 kill-switch never merged; #613 dark
   re-tighten) — only if the 3 flags above don't pull RANGING SR_FLIP to ~breakeven.
3. **TPE generation gate** (82.6%-SL guard) — still deferred, shadow-first.

---

## ⏳ SESSION 28 CLOSE 2026-06-17 — scoring corrections shipped, NOW WAITING FOR DATA

**Do not re-diagnose VSB / BDS / TREND_PULLBACK_EMA / MA_CROSS_TREND_SHIFT off the
current truth report.** The latest `monitor-logs` truth report has **cumulative
counters that predate today's merges** — it still shows the *old* (pre-change)
emission. The four scoring/filter PRs below all merged today and auto-deployed;
their effect will only appear after a fresh data window accumulates. Next session:
**pull a fresh truth report first**, then judge.

**Merged today (all on `main`):**
| PR | Path(s) | Change |
|---|---|---|
| #618 | VOLUME_SURGE_BREAKOUT, BREAKDOWN_SHORT | regime floor 8→14; score volume off the validated breakout candle |
| #619 | MA_CROSS_TREND_SHIFT, TREND_PULLBACK_EMA | MA_CROSS regime 8→14; TPE volume floored at neutral 7.5 |
| #620 | MA_CROSS_TREND_SHIFT | HTF trend-alignment gate (1h cross must agree with 4h trend; 4h cross price-vs-EMA200 confirm) |
| #621 | TREND_PULLBACK_EMA | regime scored on the HTF (1H) trend via `htf_trend_aligned` → 18, not the 5m label |

Durable lesson promoted to `OWNER_BRIEF.md §3.6a` (Scoring Doctrine).

**Path emission snapshot (PRE-change, from stale truth report — for reference only):**
- Producing: SR_FLIP_RETEST 165, FAILED_AUCTION_RECLAIM 115, LIQUIDITY_SWEEP_REVERSAL 82, DIVERGENCE_CONTINUATION 32, VOLUME_SURGE_BREAKOUT 3, POST_DISPLACEMENT_CONTINUATION 1, QUIET_COMPRESSION_BREAK 1.
- 0-emit (today's targets): TREND_PULLBACK_EMA (571 gen), BREAKDOWN_SHORT (2225 gen), MA_CROSS (15 gen), + WHALE_MOMENTUM / FUNDING_EXTREME / LIQUIDATION_REVERSAL.
- Disabled: OPENING_RANGE_BREAKOUT (feature_disabled), CONTINUATION_LIQUIDITY_SWEEP (merged into LSR), TREND_PULLBACK_CONTINUATION (legacy).

**Open items / next levers (after data confirms):**
1. **TPE generation bottleneck still deferred** — the over-tight entry-quality gate (`no_prev_high_break` + `ema21_not_tagged`, the 82.6%-SL guard). Today's PRs fix TPE *scoring*, not *generation*. Do it shadow-first if data shows survivors scoring well but volume still low.
2. **kept-vs-emitted gap** — across all paths, confidence-"kept" is 10–30× "emitted". Likely expected dedup of the same signal across 15s cycles; **confirm dedup-vs-cull** before assuming a bug. Potentially the highest-leverage cross-path investigation.
3. **MA_CROSS will stay near-zero by nature** (15 gen; crosses are rare; #620 filter cuts further) — not a bug, don't loosen.
4. **WHALE_MOMENTUM / FUNDING_EXTREME / LIQUIDATION_REVERSAL** — 0-emit, low gen, not yet diagnosed this session.

---

## Session 28 checkpoint 2026-06-17 — TPE regime scored on the wrong timeframe (HTF-aware fix, research-backed, owner-approved)

### Owner trigger
Owner asked about the regime score for the TREND_PULLBACK_EMA path, then: "go
through deep research on crypto trend-pullback conditions / which timeframes
give best, then we decide."

### Research finding (web, multi-source)
Pullbacks are a **trending-market** setup ("step aside" in ranges). Canonical
multi-timeframe doctrine: **trend is defined on the HIGHER timeframe; entry is
timed on the LOWER** (HTF=trend → MTF=structure → LTF=entry). Rule repeated
everywhere: *"never trade against the HTF trend; always time entry on the LTF."*
EMA21 = canonical pullback-retest level, EMA50 = trend filter — our 1H EMA21/50
usage matches. This validates the evaluator's post-2026-05-17 redesign (trend on
1H, entry on 5m; the old 5m-trend version scored 78% MFE=0).

### Diagnosis
`_score_regime` judges TPE on `ctx.regime_result.regime` — the **5m label**, the
*entry* TF. During the pullback the 5m label reads RANGING/QUIET, so TPE dropped
to **8** even though it only fires when the **1H is trending** (evaluator
precondition). Scoring the trend on the entry timeframe is the exact multi-TF
error the research warns against.

### Owner decision: HTF-aware regime score (the doctrinally-ideal option, not the quick 14-floor)
### Shipped (branch `feat/tpe-htf-regime-score`)
| Change | File |
|---|---|
| New `Signal.htf_trend_aligned` flag | `channels/base.py` |
| TPE stamps `sig.htf_trend_aligned = bool(_uses_1h_trend)` (True only on the 1H-trend path) | `channels/scalp.py` |
| New `ScoringInput.htf_trend_aligned` | `signal_quality.py` |
| `_score_regime`: trend-pullback family with `htf_trend_aligned` → full affinity **18** in any regime (scoped to `_FAMILY_TREND_PULLBACK`; legacy 5m-fallback path keeps the label score) | `signal_quality.py` |
| Scanner passes `sig.htf_trend_aligned` into `ScoringInput` | `scanner/__init__.py` |
| 5 scorer tests (`TestTrendPullbackHtfRegimeScore`) + 2 evaluator tests (`TestTrendPullbackHtfFlag`, incl. fires-under-RANGING-label) | `tests/test_signal_quality.py`, `tests/test_channels.py` |

CPU-only; no new reads/writes/hot-path cost. Full suite passes.
Still secondary to TPE's real generation bottleneck — the over-tight entry-quality
gate (82.6%-SL guard, `no_prev_high_break` + `ema21_not_tagged`) deferred in #619;
that's the next lever if we want TPE *generation* up (shadow-first).

---

## Session 28 checkpoint 2026-06-17 — MA_CROSS: filter is the edge, not the period (research-backed, owner-approved)

### Owner trigger
Owner: "understand crypto market and which ema works… go through research and
actually what works implement that."

### Research finding (web, multi-source — quant-signals, QuantifiedStrategies, hyrotrader, et al.)
**The EMA *periods* are second-order; the FILTER is the edge.** Consistent across
sources: raw MA crosses LOSE money in crypto (~60% of time ranging → whipsaws;
lag eats the move). 50/200 is the most robust *structural* pair (~40% win rate,
trend-following payoff — beat BTC buy-and-hold 2017-25 on 4h/6h); 9/21 etc. are
faster but whipsaw more. **Adding a higher-timeframe trend filter improves results
far more than tuning periods.** → Our existing periods (4h 50/200, 1h 21/50) are
already the research-favoured choices; the gap was the *filter*.

### Owner decision: HTF-alignment gate (periods unchanged)
Did NOT touch periods (research says don't). Added the filter that actually drives
the edge.

### Shipped (branch `feat/ma-cross-htf-alignment`)
| Change | File |
|---|---|
| 1h 21/50 cross now fires only when it agrees with the **4h structural trend** (ema50_4h vs ema200_4h); fails closed (`ma_cross_htf_unconfirmed`) if 4h unavailable, rejects (`ma_cross_htf_misaligned`) if counter-HTF | `channels/scalp.py` |
| 4h 50/200 cross gets a light **price-vs-EMA200 confirmation** (rejects failing/reverted crosses; fail-open if EMA200 missing) | `channels/scalp.py` |
| 5 tests (`TestHtfAlignmentGate`) | `tests/test_ma_cross_trend_shift.py` |

CPU-only; reuses 4h indicators already in scope — no new reads/writes/hot-path
cost. Reduces generation (filters do) in exchange for higher win quality — the
right trade for a paid A+/B-only channel. Full suite 5,618 pass.
Synergy with #619: the regime-neutral 14 + HTF gate together mean a 1h cross is
no longer regime-penalised AND is confirmed by the 4h trend.

### Declined (told owner, per "tell me when a direction is wrong")
Adding a faster 9/21 tier for more signals — research does not support it
(faster pairs whipsaw more). Quality over quantity.

---

## Session 28 checkpoint 2026-06-17 — TREND_PULLBACK + MA_CROSS scoring deficits (scoring-only fix, owner-approved)

### Owner trigger
Owner: "trend pull back and ma cross trend shift — concentrate on them." Same
data-first deep dive as VSB/BDS, off the live truth report.

### Root cause (per-path)
- **MA_CROSS_TREND_SHIFT** (15 generated, 0 emitted): generation is **inherently
  sparse and correct** — a golden/death cross is a once-in-days event
  (`no_ma_cross` 69%); the 24h cooldown is right. The fixable bug: MA_CROSS was
  **absent from every `_REGIME_SETUP_AFFINITY` list and the neutral set** →
  `_score_regime` returned a flat **8.0** in all regimes. A cross fires AT the
  regime turn (5m label still RANGING) → penalised for doing its job.
- **TREND_PULLBACK_EMA** (571 generated, 0 emitted): two layers.
  (1) Volume dimension scored the quiet pullback entry candle 3/15 — a healthy
  pullback is low-volume BY DESIGN. (2) The "entry-quality tightening" block
  (scalp.py ~1580-1609) demands a near-unicorn candle that both deep-wicks to
  tag EMA21 (`ema21_not_tagged`) AND closes above the prior high
  (`no_prev_high_break`) — crushing generation. (2) was added to fix an 82.6%
  SL rate, so it's money-risky to loosen.

### Owner decision: "scoring fixes only"
Shipped the two safe scoring corrections; **left the TPE entry gates untouched**
(TPE stays low-generation by choice — relaxing those gates re-imports the
82.6%-SL risk and would need shadow measurement first).

### Shipped (branch `feat/trendpullback-macross-scoring`)
| Change | File |
|---|---|
| `MA_CROSS_TREND_SHIFT` added to `_REGIME_NEUTRAL_SETUPS` → regime 8→14 (fires at the transition, like a counter-trend setup) | `signal_quality.py` |
| `_score_volume` floors the `_FAMILY_TREND_PULLBACK` family at neutral 7.5 — quiet pullback volume no longer scored 3/15; high-volume reclaims still earn more | `signal_quality.py` |
| 5 tests (`TestTrendPullbackAndMaCrossScoring`) | `tests/test_signal_quality.py` |

CPU-only scorer change; no hot-path reads/writes. Full suite 5,613 pass.

### Deferred (owner-gated, NOT done)
- **TPE entry-gate de-contradiction** (the `no_prev_high_break` + `ema21_not_tagged`
  double-bind). Highest lever for TPE *generation*, but money-risky — do it
  shadow-first if/when the owner wants the volume back.

---

## Session 27 checkpoint 2026-06-17 — top-mover breakout/breakdown paths were dying in the SCORER, not the gates (VSB/BDS)

### Owner trigger
Owner: "why are the remaining paths not producing signals" → "we have two special
paths for shorts and longs top movers, separate from the regular 75 — VSB and BDS
— go deep on them." Diagnosis driven off the live truth report (monitor-logs).

### Architecture recap
Movers (24h %-change ≥ `MOVER_PROMOTION_MIN_PCT`, vol ≥ `MOVER_PROMOTION_MIN_VOLUME`)
are promoted into the scan for `MOVER_PROMOTION_CYCLES` (5) with a **restricted
evaluator set: VSB (long, top gainers) + BDS (short, top losers) only**.

### Root cause (truth report, path-funnel + scoring-dimension tables)
Both evaluators correctly **removed their regime gate** (§3.4 "fire in any HTF
context") and the broken current-candle volume gate — but those fixes were
**never applied at the SCORING layer**, so the composite scorer kept punishing
them for the exact things that define them:
- **VSB dies on the Regime dimension (8 vs 18 kept).** `_score_regime` gives 8
  when the regime is known but the setup isn't in its affinity list. VSB/BDS are
  in TRENDING/VOLATILE affinity but NOT RANGING/QUIET — and a top gainer
  mid-pullback often reads RANGING/QUIET on 5m (market is 64% RANGING+QUIET). 10-pt
  deficit → lands ~61 vs the 65 floor. (My #614 unification increased the RANGING
  share, slightly worsening this.)
- **BDS dies on the Volume dimension (3 vs 12 kept).** `_score_volume` scores the
  current candle, but the BDS entry is a dead-cat bounce (low volume by design);
  the surge already fired on the breakdown candle, which the scorer never saw.

### Shipped (branch `feat/mover-breakout-scoring`, owner approved "both fixes, neutral floor")
| Change | File(s) |
|---|---|
| `_score_regime`: floor breakout-surge setups (`_BREAKOUT_SURGE_SETUPS` = VSB/BDS/ORB) at neutral 14 in non-affinity regimes instead of 8 | `signal_quality.py` |
| `_score_volume`: for those setups, score off the validated breakout-candle ratio (`breakout_volume_ratio`) instead of the low-volume entry candle; falls back to the entry ratio when unset | `signal_quality.py` |
| Evaluators stamp `sig.breakout_volume_ratio = breakout(/down)_vol / rolling_avg` | `channels/scalp.py` |
| New `Signal.breakout_volume_ratio` + `ScoringInput.breakout_volume_ratio` fields; scanner passes it through | `channels/base.py`, `signal_quality.py`, `scanner/__init__.py` |
| 8 scoring tests (`TestBreakoutSurgeScoring`) | `tests/test_signal_quality.py` |

Expected: VSB recovers ~10 regime pts, BDS ~9 volume pts → both clear 65 when
otherwise structurally sound, without touching any hard gate. No new hot-path
reads/writes (CPU-only scorer change). Owner-sign-off item (scoring model).

### Watch next session
- Truth report: VSB/BDS `Emitted` column should rise from ~0–3; confirm the
  `Regime`/`Volume` filtered-vs-kept gaps close for these two setups.
- The current truth report predates #614–#617 + this change — next report is the
  first to reflect all of them.

---

## Session 26 checkpoint 2026-06-17 — MTF trend definition unified + longs HTF-regime gate (PRs #614, #615 MERGED)

### Owner trigger
Continuing the signals-quality work: the 496-signal audit's losing bucket was
LONGs fired while the higher timeframe was rolling over. Owner approved the
"Option 2" fix (unify the trend definition, then gate longs on it).

### Root cause
Two contradictory definitions of "trend":
- **5m (`AdaptiveRegimeDetector._decide_adaptive`)** stamped TRENDING in the weak
  ADX zone (between the tier's ranging/trending floors) on EMA separation alone
  — even with ADX *decaying* — manufacturing trends from fading moves.
- **15m (`detect_regime_from_arrays`)** used a flat ADX≥25 floor, no weak zone,
  no tier profile — so a midcap at ADX 22 read TRENDING on 5m and RANGING on 15m
  *by construction*, making any MTF comparison meaningless.

### Shipped (branch `claude/google-services-cost-analysis-w61lnc`)
| PR | Change | File(s) |
|---|---|---|
| **#614 MERGED** | Weak-zone trends now require ADX **rising** (`adx_slope>0`); unknown slope → RANGING. `detect_regime_from_arrays` made **tier-aware** + same weak-zone rule, so 5m and 15m mean the same thing by "trend". | `regime.py`, `scanner/__init__.py`, `tests/test_regime_mtf_unification.py` (9 tests) |
| **#615 MERGED** | **Filter 1b** in `_prepare_signal`: drop a LONG when the unified 15m regime is TRENDING_DOWN. Env toggles `MTF_LONGS_REGIME_GATE_ENABLED` (default on) + `MTF_LONGS_REGIME_GATE_DARK` (measure-only). Telemetry: `mtf_longs_regime_eval/block/would_block`. | `scanner/__init__.py`, `tests/test_scanner.py` (`TestLongsRegimeGateInScanner`) |
| **follow-up (this session, in PR)** | **§3.4 doctrine bypass for Filter 1b**: breakout/tape/liquidation-reversal longs (`_SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS`) are NOT HTF-vetoed — a breakout into a down 15m IS the regime change. Owner chose "exempt them". Telemetry: `mtf_longs_regime_doctrine_bypass:360_SCALP:<setup>`. | `scanner/__init__.py`, `tests/test_scanner.py` |

Per the owner's audit, removing the losing longs bucket flipped the audited
book from **−14.1 to +3.0** (owner-supplied figure, not re-measured here).

### Watch next session
- **`/suppressed` → `mtf_longs_regime_block` vs `mtf_longs_regime_doctrine_bypass`**:
  confirm the live block volume tracks the audit, and see how many longs the
  §3.4 exemption preserves. Flip `MTF_LONGS_REGIME_GATE_DARK=true` to pull back
  to measure-only without a code redeploy.
- Shorts are intentionally ungated; only 15m is used (not 1h/4h) — both deliberate.

### Follow-up (not done)
- **Pre-existing API test red** (FastAPI `204` + `response_model` at app
  construction) is failing on `main` in CI's container — unrelated to these PRs,
  but a possible live `api`-container risk. Worth confirming the live FastAPI pin.

---

## Session 25 checkpoint 2026-06-16 — GCP cost spike was Firestore reads, not auth (PR #609, MERGED)

### Owner trigger
Owner shared the `lumin-app` GCP/Firebase billing screens: ₹4,558/mo with a
climbing forecast, asking why "phone-number authentication only" was costing
so much. The "App Engine" line dominated despite **no App Engine services
deployed**.

### Root cause (confirmed on live billing data)
- **99.9% of the bill is Cloud Firestore — ₹4,552 — and specifically READS.**
  Writes/deletes sat inside the free tier; the read free-tier quota was
  exceeded daily. **Phone Auth / SMS = ₹0 (0% of quota).** Auth was never the
  cost — it was a red herring.
- **Why "App Engine" with no App Engine services:** Firestore-in-Datastore-mode
  bills under the "App Engine" SKU grouping in GCP. Confirmed via Billing →
  SKU breakdown (Cloud Firestore ₹4,552.25, non-Firebase ₹5.88) + the Firebase
  Usage tab ("Reads: limit exceeded").
- **The leak:** `pretp_dispatcher._on_tick` ran a Firestore collection-group
  query on *every* mark-price tick (~1/sec × open symbols, 24/7) to find OPEN
  positions. The module header already flagged it as `O(N) per tick` debt.

### Shipped (branch `claude/google-services-cost-analysis-w61lnc`, PR #609 — MERGED to main)
| Change | File(s) | Notes |
|---|---|---|
| `_write_generation` counter, bumped on `put_position`/`delete_position`; `get_write_generation()` | `position_state.py` | the freshness signal |
| Per-symbol OPEN-positions cache gated on that generation (+ defensive 10s TTL) | `pretp_dispatcher.py` | removes Firestore from the per-tick hot path |
| Cache tests (generation invalidation, TTL expiry, per-symbol, put/delete bump) | `tests/test_pretp_dispatcher_cache.py` | 5 new; 325 in the exec suite pass; ruff clean |

Correctness: the cache cannot serve a stale `pretp_fired`/`state` and double-fire
— every mutation funnels through `put_position`/`delete_position`, both of which
bump the generation and invalidate. No change to pre-TP threshold/firing logic.

### Process changes (this session)
- **`CLAUDE.md` gained a "Cost Discipline" section** + a Hard Limit ("never add
  an uncached Firestore/network read to a hot loop") + an operating-standard
  bullet ("cost is a first-class concern"). Every future change is reviewed for
  cost the way it's reviewed for correctness.

### Follow-up (not done)
- **Full in-memory open-positions index** would eliminate even the cold-path
  query (zero reads). The generation-gated cache is the lower-risk first step;
  the index is the next optimisation if reads still register.
- **No PR-level CI exists** in this repo (only `deploy.yml` on push-to-main +
  manual `vps-monitor`). Local test/lint runs are the only pre-merge gate today
  — worth adding a PR test workflow.
- Confirm the bill drops after the engine redeploys with #609 (reads keep
  accruing until the new image is live).

---

## Session 24 checkpoint 2026-06-15 — signals-quality audit: the bleed is RANGING SR_FLIP/LSR, not the trending exits

### Owner trigger
Owner reported sustained losses (paper P&L 7d −$34.74) and asked for a full
audit "per path / per regime / per market / per pair" — why the auto engine
lags a manual trader.

### Root-cause findings (live data, last-100 signals Jun 13–15)
- **The bleed is RANGING, not trending.** RANGING = 67% of volume and −7.22%
  of the −8.7% aggregate. TRENDING_DOWN ≈ flat (−0.12%). The two exit flags
  that ARE on (`TRENDING_PRETP_SUPPRESSED=True`, `RETRACE_REGIME_AWARE=True`)
  only touch the ~26% trending slice — they cannot fix a RANGING bleed. That
  is why flipping them never moved P&L.
- **Concentrated in two setups:** SR_FLIP_RETEST −4.36% (45 sigs, +0.25/−0.38)
  and LIQUIDITY_SWEEP_REVERSAL −3.77% (20 sigs, +0.47/−0.73). Both ~1:2
  win:loss. FAILED_AUCTION_RECLAIM (+0.71, 67% win) and DIVERGENCE_CONTINUATION
  (+0.42, 60% win) are profitable — leave alone.
- **0 TP hits / 45 full SL / 55 pre-TP-or-invalidation** across 100. Wins are
  capped small while losers run to wide structural stops → upside-down R:R.
- **`entry_regime` is EMPTY on the monitor's signals_last100.json** even with
  #606 in the tree. signals_last100.json is monitor-augmented (carries
  non-dataclass fields), so this is NOT authoritative for live FSM state —
  but it is suspicious. AUTHORITATIVE CHECK PENDING (see open items): read
  `data/signal_history.json` (raw vars(sig) dump) on the VPS. If empty there,
  the Session-23 bug is back / engine image predates #606 → rebuild engine.
- Tokenized-stock blacklist confirmed working (none in last 100).

### Shipped this session (branch `claude/signals-quality-audit-yn1a1f`, NOT yet PR'd to main)
| Change | File(s) | Default | Reversible |
|---|---|---|---|
| Micro-cap momentum-kill bug fix — sub-$0.001 coins no longer get a 10×-tighter kill threshold (momentum is scale-invariant); `INVALIDATION_MOMENTUM_MICROCAP_MULT` default 1.0 | `config`, `trade_monitor.py` | **LIVE (1.0)** | env → 0.1 |
| `entry_regime`/`entry_regime_15m` stamped into `dispatch_log.json` | `signal_router.py` | live (telemetry) | n/a |
| RANGING low-ATR loser-suppression gate (SR_FLIP/LSR only, ATR%ile ≤ 25) | `config`, `scanner` | **DARK** + `[SHADOW]` | flag |

All tests green (913 passed in the scanner/quality/invalidation sweep; 4 + 8
new cases). No PR to main opened yet (owner batching the full package).

### Geometry rebuild (C) — DONE on branch (dark), owner sign-off to activate
- **SR_FLIP:** already built (#603 pre-TP R-scaling, #604 trailing-arm R-scale)
  — activation only.
- **LSR (this session):** win-side `LSR_PRETP_R_SCALING_ENABLED` (pre-TP
  R-scaling, mirror of #603) + loss-side `LSR_SL_TIGHTEN_ENABLED`
  (`LSR_MAX_SL_PCT_TIGHT` 1.5%). LSR is reject-not-compress, so the tighten
  DROPS wide-stop LSRs (no wick-out risk). Both dark + shadow.

### Remaining work (owner)
1. **Run the authoritative `entry_regime` check** (signal_history.json) + rebuild
   engine if empty — settles whether the trending exit-flags are actually live.
2. **Activation sequence (A)** — see runbook below, after merge + 48h shadow.

### Activation runbook (owner — after the entry_regime check + engine rebuild)
```bash
cd /root/360-v2
# AUTHORITATIVE entry_regime check (settles whether the trending flags are live):
docker exec 360scalp-v2-engine python -c "import json; d=json.load(open('data/signal_history.json')); r=sorted(d,key=lambda x:x.get('timestamp',0))[-6:]; [print(x.get('symbol'),repr(x.get('entry_regime'))) for x in r]"
# If empty -> rebuild so #606 is actually running:
docker compose -f docker-compose.yml --profile isolated up -d --no-deps --force-recreate engine
```
Then, once this branch is merged to main + deployed, read 48h of shadow counts
before flipping each flag:
```bash
docker logs 360scalp-v2-engine --since 48h 2>&1 | grep -c "\[SHADOW\] RANGING_LOW_ATR_LOSER_SUPPRESS"
docker logs 360scalp-v2-engine --since 48h 2>&1 | grep -c "\[SHADOW\] MICROCAP_MOMENTUM_SPARED"
```
Activation order (one at a time, measure between): SR_FLIP R-scaling (#603) →
trailing-arm R-scale (#604) → RANGING low-ATR suppression → revisit LSR geometry.

---

## Session 23 checkpoint 2026-06-10 — entry_regime empty bug found and fixed (PR #606)

### Root cause finding (drove the session)

`TRENDING_PRETP_SUPPRESSED` shadow telemetry (`DARK_FLAG_SHADOW_TELEMETRY=true`) returned
**0 hits after 48h** despite signals dispatching normally. Diagnosis: `sig.entry_regime`
was always `""` at dispatch time for every signal.

Bug in `_populate_signal_context` (`src/scanner/__init__.py`): `sig.entry_regime = rc.label`
was inside a `try` block that ran `float(rc.atr_percentile)` and `float(rc.adx_slope)` in
f-strings **above** it. When either `float()` raised `TypeError` or `ValueError`, the
`except` clause silently dropped the entire block — `entry_regime` was never written,
leaving the `Signal` default of `""`.

### Impact (two features were dead letters in production)

| Feature | PR | Effect |
|---|---|---|
| `TRENDING_PRETP_SUPPRESSED` shadow + real flag | #594 | `regime_label=""` → suppress condition always False; 0 shadow hits since deploy |
| Regime-per-exit FSM gating | #578 | `entry_regime=""` → all FSM regime checks silently bypassed on every dispatched position |

### Fix — PR #606 (merged 2026-06-10)

`sig.entry_regime = rc.label` hoisted above the `try` block. Pure string assignment,
cannot raise. The `float()` calls that may fail remain inside `try/except` as before.

### Action required on VPS after merge

```bash
# Rebuild engine image with the fix:
cd /root/360-v2
docker compose -f docker-compose.yml --profile isolated up -d --no-deps --force-recreate engine

# Confirm shadow telemetry now fires (within hours of next TRENDING signal dispatch):
docker logs 360scalp-v2-engine -f | grep "\[SHADOW\] TRENDING_PRETP_SUPPRESSED"

# Confirm entry_regime is now populated on dispatched positions:
docker exec 360scalp-v2-redis redis-cli hgetall snapshot:<uid> 2>/dev/null | grep entry_regime
```

### Open items (priority order)

1. **Deploy PR #606 on VPS** — `docker compose ... up -d --no-deps --force-recreate engine` after merge.
2. **Confirm shadow telemetry fires** — grep `[SHADOW] TRENDING_PRETP_SUPPRESSED` post-deploy; expect counts within hours.
3. **Re-verify regime-per-exit live (PR #578)** — with `entry_regime` now populated, confirm it is non-empty in Redis snapshot and FSM trail/cancel paths are actually being reached.
4. **TRENDING_PRETP_SUPPRESSED activation** — blocked on 7 days of shadow data post-#606 deploy. Do not activate blind.
5. **Change A activation on VPS** — `SR_FLIP_CONSECUTIVE_REQUIRED=3`; commands in Session 22 section below.
6. **#604 shadow telemetry → activation** — read `TRAILING_RSCALE_WOULD_SUPPRESS` count after 48h, then activate `INVALIDATION_TRAILING_ARM_RSCALE_ENABLED=true`.
7. **Google Play approval** — awaiting email (submitted 2026-06-06, ≤7 days). Complete store listing + data-safety form while waiting.
8. **Scoring-model rebuild** — blocked on data accumulation in Ops score-band view.

---

## Session 22 checkpoint 2026-06-07 — SR_FLIP premature-kill audit + trailing R-scale arm

### Root cause finding (drove the session)

Owner ran `invalidation_records.json` audit on VPS. Among 16 PREMATURE SR_FLIP kills:

| Kill family | Count | Premature % |
|---|---|---|
| trailing_invalidation | 7 | **44%** |
| momentum_loss | 4 | 16% |
| other | 5 | — |

Root cause of `trailing_invalidation` dominance: the trailing kill **arms at a flat 0.30R** regardless of SL width. SR_FLIP structural SLs are 1.6–2.5% wide. At 0.30R × 1.6% SL ≈ 0.48% absolute, normal reversal pullbacks (>50% retrace) fire the kill near breakeven before the position has established real profit. EDGEUSDT was the canonical proof: entry 0.6472 SHORT, SL 1.63%, MFE 0.56% (+0.36% R) → killed at 0.06% by a retrace.

### What shipped this session (2 PRs merged)

| PR | What | Flag (default) | Shadow telemetry |
|---|---|---|---|
| [#603](https://github.com/mkmk749278/360-v2/pull/603) | **Change A**: SR_FLIP momentum-kill grace — per-setup `INVALIDATION_CONSECUTIVE_THRESHOLD` key (`360_SCALP::SR_FLIP_RETEST`) requires 3 vs 2 consecutive bad-momentum readings | `SR_FLIP_MOMENTUM_GRACE_ENABLED` (false) | `[SHADOW] SR_FLIP_GRACE_WOULD_SUPPRESS` |
| [#603](https://github.com/mkmk749278/360-v2/pull/603) | **Change B**: SR_FLIP pre-TP R-scaling — floors pre-TP threshold at `SL_dist_pct × 0.35R` so wide-SL signals don't bank at 0.20R | `SR_FLIP_PRETP_R_SCALING_ENABLED` (false) | `[SHADOW] SR_FLIP_RSCALE_WOULD_RAISE` |
| [#604](https://github.com/mkmk749278/360-v2/pull/604) | **R-scaled trailing-kill arm** — arm threshold becomes `min(0.80, 0.30 + 0.15 × sl_dist_pct)` globally for all setups; fixes the EDGEUSDT premature kill class | `INVALIDATION_TRAILING_ARM_RSCALE_ENABLED` (false) | `[SHADOW] TRAILING_RSCALE_WOULD_SUPPRESS` |

Both PRs ship **completely dark** — no live behavior change on merge. 5566 tests pass, 0 failures.

### Change A activation (owner task — do now)

Owner decided to activate Change A immediately (momentum-kill grace for SR_FLIP, `SR_FLIP_CONSECUTIVE_REQUIRED=3`). Commands on VPS:

```bash
cd /root/360-v2
grep -q '^SR_FLIP_CONSECUTIVE_REQUIRED=' .env \
  && sed -i 's/^SR_FLIP_CONSECUTIVE_REQUIRED=.*/SR_FLIP_CONSECUTIVE_REQUIRED=3/' .env \
  || echo 'SR_FLIP_CONSECUTIVE_REQUIRED=3' >> .env
docker compose -f docker-compose.yml --profile isolated up -d --no-deps --force-recreate engine
# Verify:
docker exec 360scalp-v2-engine python -c \
  "from config import INVALIDATION_CONSECUTIVE_THRESHOLD as c; print(c.get('360_SCALP::SR_FLIP_RETEST'))"
# → should print 3
```

### Activation sequence for #604 (read shadow data first)

After 48h with the new engine image deployed, check shadow counts:

```bash
docker logs 360scalp-v2-engine --since 48h 2>&1 | grep -c "\[SHADOW\] TRAILING_RSCALE_WOULD_SUPPRESS"
docker logs 360scalp-v2-engine --since 48h 2>&1 | grep -c "\[SHADOW\] SR_FLIP_GRACE_WOULD_SUPPRESS"
docker logs 360scalp-v2-engine --since 48h 2>&1 | grep -c "\[SHADOW\] SR_FLIP_RSCALE_WOULD_RAISE"
```

When confident in shadow count, activate #604:
```bash
echo 'INVALIDATION_TRAILING_ARM_RSCALE_ENABLED=true' >> /root/360-v2/.env
docker compose -f docker-compose.yml --profile isolated up -d --no-deps --force-recreate engine
```

### New config constants (all in `config/__init__.py`)

```
SR_FLIP_CONSECUTIVE_REQUIRED          = 2       (3 when activated)
SR_FLIP_MOMENTUM_GRACE_ENABLED        = false
SR_FLIP_PRETP_R_SCALING_ENABLED       = false
SR_FLIP_PRETP_R_FACTOR                = 0.35
INVALIDATION_TRAILING_ARM_RSCALE_ENABLED  = false
INVALIDATION_TRAILING_ARM_R_PER_SL_PCT    = 0.15
INVALIDATION_TRAILING_ARM_R_MAX           = 0.80
```

### Open items (priority order)

1. **Change A activation on VPS** — owner task, commands above. Verify 3 is live before enabling #604.
2. **#604 shadow telemetry** — read `TRAILING_RSCALE_WOULD_SUPPRESS` count after 48h, then activate `INVALIDATION_TRAILING_ARM_RSCALE_ENABLED=true`.
3. **Google Play approval** — awaiting email (≤7 days from 2026-06-06). Complete store listing / data-safety form while waiting.
4. **Scoring-model rebuild** — still blocked on data accumulation in the Ops score-band view.
5. **PR #594 (regime-aware exit)** — owner sign-off required. Do not auto-merge. Touches position FSM / regime-per-exit doctrine (§3.2b).
6. **Dark-flag shadow telemetry (session-19/20 flags)** — read counts before enabling `TRENDING_PRETP_SUPPRESSED`, `PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED`, `INVALIDATION_BTC_CORRELATION_ENABLED`:
   ```bash
   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] TRENDING_PRETP_SUPPRESSED"
   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] PRETP_FULLGRAB_ON_CANCEL"
   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] INVALIDATION_BTC_CORRELATION"
   ```

---

## Session 21 checkpoint 2026-06-06 — Play Store submitted + universe/reset-defaults complete

### What shipped this session

| PR | Repo | What | Status |
|---|---|---|---|
| [#599](https://github.com/mkmk749278/360-v2/pull/599) | 360-v2 | Scan blacklist sweep: CRCL/MU/INTC/CL/EWY added to `SCAN_SYMBOL_BLACKLIST` | Merged |
| [#600](https://github.com/mkmk749278/360-v2/pull/600) | 360-v2 | All 9 tokenized stocks added to `_NON_CRYPTO_BLACKLIST` (selection-time) — guarantees 75 real crypto pairs | Merged |
| [#601](https://github.com/mkmk749278/360-v2/pull/601) | 360-v2 | `DELETE /api/settings/user/pretp` + `DELETE /api/settings/user/invalidation` — reset per-user settings to engine defaults | Merged |
| [#93](https://github.com/mkmk749278/lumin-app/pull/93) | lumin-app | Reset-to-engine-defaults button on Pre-TP and Invalidation settings pages; Pre-TP page redesign (headline controls + collapsed Advanced) | Merged |
| [#94](https://github.com/mkmk749278/lumin-app/pull/94) | lumin-app | `LUMIN_DISTRIBUTION` compile-time flag + `kSelfUpdateEnabled` const — gates Play AAB off the self-updater | Merged |
| [#95](https://github.com/mkmk749278/lumin-app/pull/95) | lumin-app | `build-apk.yml` AAB step adds `--dart-define=LUMIN_DISTRIBUTION=play` — defense in depth | Merged |
| [#96](https://github.com/mkmk749278/lumin-app/pull/96) | lumin-app | `docs/PLAYSTORE_SUBMISSION.md` — paste-ready Play Console answers, data-safety table | Merged |

### Google Play production application — SUBMITTED

Applied today 2026-06-06 at 18:06. Confirmation screen: "We have your application for production access." Google will email within 7 days.

**Remaining Play Console steps (complete while waiting for approval):**
1. Data safety form — use table in `docs/PLAYSTORE_SUBMISSION.md`
2. Store listing — name, short/full description, screenshots, feature graphic
3. Content rating — IARC questionnaire (answer truthfully; paper trading is not gambling)
4. Upload Play AAB — trigger tag push or `flutter build appbundle --release --dart-define=LUMIN_DISTRIBUTION=play`
5. Pricing & distribution — set regions matching the in-app region gate

### Universe fix — confirmed complete

Two-layer blacklist now in place:
- **Scan-time** (`SCAN_SYMBOL_BLACKLIST`): 9 tokenized stocks excluded before scanning
- **Selection-time** (`_NON_CRYPTO_BLACKLIST`): same 9 excluded before the `[:75]` slice

Result: the 75-pair slot always fills with real crypto. No tokenized stocks reach subscribers.

### Open items (priority order)

1. **Google Play approval** — awaiting email (≤7 days). Complete store listing / data-safety while waiting.
2. **Scoring-model rebuild** — still blocked on data accumulation in the Ops score-band view.
3. **PR #594 (regime-aware exit)** — owner sign-off required. Do not auto-merge. Touches position FSM / regime-per-exit doctrine (§3.2b).
4. **Dark-flag shadow telemetry** — read `[SHADOW]` counts before enabling TRENDING_PRETP_SUPPRESSED:
   ```bash
   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] TRENDING_PRETP_SUPPRESSED"
   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] PRETP_FULLGRAB_ON_CANCEL"
   docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] INVALIDATION_BTC_CORRELATION"
   ```

---

## Session 20b checkpoint 2026-06-06 — universe cleanup + dark-flag measurability

Continuation of session 20. Two follow-ups from the list below cleared, plus
the companion lumin-app production-UI pass.

### What shipped this session (3 PRs merged)

| PR | Repo | What | Live effect |
|---|---|---|---|
| [#596](https://github.com/mkmk749278/360-v2/pull/596) | 360-v2 | Tokenized-stock blacklist — AVGOUSDT/QQQUSDT/SKHYNIXUSDT/DRAMUSDT added to `SCAN_SYMBOL_BLACKLIST` | **Live on merge.** Those 4 pairs no longer scanned. |
| [#597](https://github.com/mkmk749278/360-v2/pull/597) | 360-v2 | Shadow telemetry for the 3 dark exit flags — logs `[SHADOW]` lines when a flag *would* fire while off | **Live on merge** (log-only, trade-neutral). `DARK_FLAG_SHADOW_TELEMETRY=true` default. |
| [#92](https://github.com/mkmk749278/lumin-app/pull/92) | lumin-app | Production UI: paper-first journey, removed engine-internal "75 pairs" copy, wired Telegram subscribe deep link, prominent paper-reset button | Merged. |

**#596 evidence (verified, not assumed):** pulled `origin/monitor-logs`
`signals_last100.json` + `dispatch_log.json` — all 4 symbols were actively
firing to the paid channel (AVGO 8×, QQQ 6×, SKHYNIX 3×, DRAM 1× of last
100), quotes track equity prices ($55–$1366), near-exclusively SHORT. Class-C
misfit per `docs/SYMBOL_CLASS_RESEARCH_2026_05_23.md`.

**#597 design:** flag-independent predicates shared by the real apply-funcs
and the shadow path (count can't drift from the gate); BTC shadow eval only on
the adverse-excursion path, TTL-cached, skipped entirely when master flag off.
49 tests pass.

### Now measurable from prod logs (before flipping the real flags)

```bash
# Count how often each dark flag WOULD have fired in recent logs:
docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] TRENDING_PRETP_SUPPRESSED"
docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] PRETP_FULLGRAB_ON_CANCEL"
docker logs 360scalp-v2-engine --since 24h 2>&1 | grep -c "\[SHADOW\] INVALIDATION_BTC_CORRELATION"
```

Read these counts before enabling `TRENDING_PRETP_SUPPRESSED` (the first flag
in the activation sequence below) so the blast radius is known in advance.

### Open follow-up from #596 (owner call)

Research doc also lists older tokenized stocks `CRCL/MU/INTC/CL/EWY` (already
100% QUIET-blocked). Not added — couldn't re-verify them in the current
100-signal window. Fold into the blacklist as a complete sweep, or leave them?

---

## Session 20 checkpoint 2026-06-06 — regime-aware exit (TRENDING runner fix)

### Research finding (drove the session)

Binance realized P&L analysis of 107 closed positions proved the profit/loss split is almost entirely explained by HOW LONG a position runs:

| Hold duration | Count | Net P&L | Win rate |
|---|---|---|---|
| > 40 minutes | 9 | **+$1.049** | 67% |
| < 40 minutes | 98 | **-$0.492** | 39% |

Pearson r(hold_minutes, PnL) = **+0.379**. The top-4 realized winners (NEAR +$0.348, NEAR +$0.291, WIF +$0.213, XPLV2 +$0.183) ran 47–68 minutes. The signal book had already PROFIT_LOCKEd those signals at 2–6 min while the Binance bracket kept running.

**Root cause split:**
- RANGING/QUIET markets: pre-TP + tight trailing-kill work correctly — contain chop losses, bank small wins
- TRENDING markets: the same mechanisms cut the exact positions that generate all profit. Pre-TP banks 50% at +0.35%; trailing-kill at 50% MFE retrace fires on normal continuation pauses (pullbacks routinely retrace 50-65% of a trend leg without reversing)

### What shipped this session (1 PR, owner sign-off required)

| PR | Repo | What | Flag (default) |
|---|---|---|---|
| [#594](https://github.com/mkmk749278/360-v2/pull/594) | 360-v2 | Regime-aware exit: suppress pre-TP + widen trailing-kill in TRENDING | see below |

**PR #594 — owner sign-off required.** Do not auto-merge. Touches position FSM / regime-per-exit doctrine (§3.2b).

### New env flags — activation when ready

| Flag | Default | Effect when `true` |
|---|---|---|
| `TRENDING_PRETP_SUPPRESSED` | `false` | Zero grab fraction for TRENDING_UP/DOWN signals → full position rides the trend |
| `INVALIDATION_TRAILING_RETRACE_REGIME_AWARE` | `false` | TRENDING signals use wider retrace threshold (default 0.70 vs 0.50 baseline) |
| `INVALIDATION_TRAILING_RETRACE_PCT_TRENDING` | `0.70` | Override the TRENDING retrace threshold (tune after observing) |

**Recommended activation sequence:**
1. Merge PR #594 (owner sign-off)
2. Enable `TRENDING_PRETP_SUPPRESSED=true` first — measurable via whether TRENDING signals run longer on Binance
3. After a week of data, enable `INVALIDATION_TRAILING_RETRACE_REGIME_AWARE=true`
4. Compare hold-time distribution + net P&L against session 20 baseline

### Also confirmed this session

- `PRE_TP_REGIME_ALLOWLIST = "QUIET,RANGING,VOLATILE"` (config) is enforced by `trade_monitor.py` for the signal book, but the **server-side FSM dispatch path** (`resolve_pretp_allowlists_uid`) returns allow-all by default when no user DB setting exists — TRENDING regime signals WERE getting pre-TP fired via the FSM. PR #594 fixes this at the dispatch level.

### Open follow-ups (carry-forward from session 19)

1. **Scoring-model rebuild** — blocked on data accumulation in the new Ops score-band view
2. ~~**Tokenized stock exclusion**~~ — ✅ **DONE** in PR #596 (session 20b). AVGOUSDT/QQQUSDT/SKHYNIXUSDT/DRAMUSDT added to `SCAN_SYMBOL_BLACKLIST`.
3. ~~**Shadow telemetry for dark flags**~~ — ✅ **DONE** in PR #597 (session 20b). `DARK_FLAG_SHADOW_TELEMETRY=true` default; `[SHADOW]` lines now in prod logs.

---

## Session 19 checkpoint 2026-06-05 — scoring research + BTC-in-invalidation + CANCEL-path fee fix

### Research finding (drove the whole session)

Owner supplied a 107-signal Ops report pairing **confidence score with outcome**. Decisive result: **Pearson r(confidence, PnL) = −0.027** — the confidence score has **no predictive power** over outcome. Raising the score threshold only cuts volume, it does **not** improve quality (the "trade 80+ only" idea = 4 signals, still net-negative). The real discriminators are **setup identity** (FAILED_AUCTION_RECLAIM / FUNDING positive; SR_FLIP_RETEST / LSR / BREAKDOWN negative) and **exit geometry**, not the score. Owner direction: do **not** pause setups — research paths, fix structurally, consider BTC correlation.

### What shipped this session (3 PRs merged)

| PR | Repo | What | Flag (default) |
|---|---|---|---|
| #591 | 360-v2 | BTC correlation in the **invalidation** system — tightens adverse-excursion exit when BTC 1H+4H oppose an open position | `INVALIDATION_BTC_CORRELATION_ENABLED` (false) |
| #592 | 360-v2 | **Full-grab pre-TP on CANCEL-bound regimes** — closes full position at the pre-TP LIMIT instead of partial+market-close (2 maker fees not 3, no residual slippage) | `PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED` (false) |
| #11 | 360ce-ops | Performance page: **score-band table + live Pearson r(confidence, PnL)**; fixed `PROFIT_LOCKED` not counted as a win | — (read-only) |

**All three engine changes ship DARK** — merges were behavior-neutral. Nothing changes live until the flags are flipped on the VPS.

### New env flags — how to A/B them on the VPS

| Flag | Effect when `true` | Companion tunables |
|---|---|---|
| `INVALIDATION_BTC_CORRELATION_ENABLED` | Open position that is losing **and** fighting BTC's 1H+4H trend exits earlier (adverse fraction × mult). Tape-driven setups exempt; fail-open on missing BTC data. | `INVALIDATION_BTC_ADVERSE_FRACTION_MULT` (0.70), `INVALIDATION_BTC_DIRECTION_CACHE_TTL_SEC` (60) |
| `PRETP_FULLGRAB_ON_CANCEL_REGIME_ENABLED` | RANGING/QUIET-entry pre-TP closes 100% at the LIMIT (fee win, ~76% of cycles). Identical exit, 1 fewer fee. | — |

Validate enabling either against the truth report's PROTECTIVE/PREMATURE classifier + the new Ops score-band view.

### Open follow-ups (next session)

1. **Scoring-model rebuild** — "each score point should filter." Blocked on data: let the new Ops score-band view + per-setup outcomes accumulate (~days), then rebuild scoring on the components that actually discriminate (MTF/SMC look strongest; needs confirmation from real per-component outcome data — do **not** rebuild blind).
2. **SRFLIP/LSR geometry** — the small-win/big-loss asymmetry is the core bleed; the CANCEL fee fix (#592) trims fees but does not flip profitability. Investigate SL placement vs known liquidity clusters + pre-TP threshold sizing.
3. **Settings reset to defaults** — one-time VPS SQLite/API op when owner wants a clean baseline (pre-TP on, grab 0.50, threshold 0.35% ATR-adaptive, invalidation `tight`).
4. **Shadow telemetry for #591/#592** — optional: log when the dark overlays *would* fire so impact is measurable before flipping the flags live.

---

## Session 18 checkpoint 2026-06-04 — monitoring agent live + scan latency fixed (64s → ~3s) + Positions tab fixes

### What shipped this session (8 PRs merged to `main`)

| PR | Repo | What | Type |
|---|---|---|---|
| #583 | 360-v2 | `/internal/diag/tasks` endpoint (owner-tier) | feat, auto-merged |
| #584 | 360-v2 | Engine task census published to Redis (D2 re-enable) | feat, auto-merged |
| #585 | 360-v2 | Signing-client 16 MiB socket read buffer (reconciler overflow fix) | fix, auto-merged |
| #586 | 360-v2 | Per-stage scan timing instrumentation | feat, auto-merged |
| #587 | 360-v2 | SMC result cache + indicator fingerprint (insufficient — see #588) | fix, auto-merged |
| #588 | 360-v2 | Per-timeframe indicator caching (the real scan-latency fix) | fix, auto-merged |
| #589 | 360-v2 | `monitor_running` from task census in isolated mode (false-negative fix) | fix, auto-merged |
| #590 | 360-v2 | Positions X-ray populated in isolated mode via engine-published diag | fix, auto-merged |
| #6/#7/#9/#10 | 360ce-ops | Monitoring agent deployed (Tier 0 + Tier 2 healthchecks.io) | feat, merged |

### Monitoring agent (360ce-ops) — fully operational

24/7 monitoring agent deployed as a separate Docker container (`360ce-ops-agent`) on the VPS.

**Architecture:**
- **Tier 0** — 7 deterministic detectors polling every 60s, paging Telegram on money-path failures
- **Tier 2** — healthchecks.io dead-man switch (Period=1min, Grace=2min), green since 08:02

**Active detectors:**

| ID | Name | Fires when |
|---|---|---|
| D1 | NakedPositionDetector | Position with `entry>0`, valid symbol, `stop_loss≤0` for >1 cycle |
| D2 | BackgroundTaskDetector | Any of `trade_monitor / reconciler / mark_price_feed / funding_exit_watcher` absent from task census |
| D3 | AutoModeDisabledDetector | `auto_mode=false` for >15 min |
| D4 | StaleSnapshotDetector | Engine snapshot not updated in >90s |
| D6 | BinanceKeyMissingDetector | Binance key disconnected |
| D7 | PositionCountAnomalyDetector | Open position count changes by >5 in one cycle |
| D8 | RedisIdleDetector | `snapshot:tickers` Redis key idle >120s |

**False positives eliminated:**
- D1: requires `symbol != ""` and `entry > 0.0` — ignores Redis-facade signal-tracking placeholders
- D2: empty census (unavailable) treated as `[]` skip, not "all dead"
- D5 (heartbeat_stale): removed entirely — file mtimes don't correlate with scan cycles

**Known limitation (D1):** reads `sig.stop_loss` geometry, cannot detect the real case (valid SL price, Binance stop order not yet confirmed). Proper fix requires engine to publish `sl_order_id` per position to Redis snapshot. Tracked as follow-up.

### PR #585 — reconciler positionRisk overflow (confirmed fixed)

Root cause: `asyncio.open_unix_connection` default 64 KiB `readline` limit raised
`ValueError: Separator is not found, and chunk exceed the limit` when
`/fapi/v2/positionRisk` returned >64 KiB of JSON (all symbols, no filter).
Fix: raised `_SOCKET_READ_LIMIT` to 16 MiB. Confirmed working — empty grep for
`Separator is not found` in VPS logs post-deploy.

### Scan latency — root cause + fix (#587 then #588), CONFIRMED FIXED

**Production timing that drove the work (`smc_indicators` summed / cycle wall-clock):**
```
{'smc_indicators': 758.51, ...}  cycle=71.8s
{'smc_indicators': 866.61, ...}  cycle=75.3s
```

**Two distinct bugs, fixed across two PRs:**

1. **SMC never cached** (#587) — `smc_detector.detect` ran fresh every cycle even though
   sweeps / FVGs / orderblocks are deterministic on completed candles. Added `_smc_cache`
   keyed on closed 5m+ candle counts. **This part worked.**

2. **Indicator cache used one whole-dict fingerprint including 1m** (#587 got this wrong;
   #588 fixed it). A new 1m candle closes ~every cycle, so the combined fingerprint
   changed every cycle and invalidated indicators for ALL 7 timeframes — 5m..1w were
   recomputed needlessly. #587 showed **no improvement in prod** (541-822s) because the
   single timing bucket lumped SMC + indicators, masking the working SMC cache.

**#588 fix (the real win):** indicator cache keyed PER TIMEFRAME — `symbol → {tf: (len, ind)}`.
Only timeframes whose candle count changed recompute. 1m recomputes every cycle (scalping
needs the live bar); 5m..1w hit ~95%. Telemetry split into separate `smc` / `indicators`
buckets to make it self-verifying.

**Confirmed in production (post-#588):**
```
cycle=2.5–5.7s   {'indicators': 0.0, 'smc': 0.0}            ← most cycles, fully cached
cycle=12.4s      {'indicators': 97.1, 'smc': 0.0}           ← 1m candle closed
cycle=16.0s      {'indicators': 136.4, 'smc': 45.6}         ← 1m + 5m closed
```
**Cycle wall-clock 64s → ~3s typical, ~16s worst-case** (at candle boundaries). `smc` is
0 on every cycle except 5m closes — proving the #587 SMC cache was working all along.

### Positions tab — two isolated-mode false-negatives (#589, #590), FIXED

Both surfaced from owner screenshots of the dashboard Positions tab. Root cause in both
cases: the isolated `api` container serves from `RedisEngineFacade`, which lacks the live
engine objects the single-process build assumes are present.

1. **`monitor_running: NO` false-negative (#589).** The diag derived liveness from
   `getattr(engine, "monitor", None)._running`. The facade has no `.monitor` object, so it
   always read `None` → "NO" — even though the Redis task census showed `trade_monitor
   ALIVE: True`. Fix: when no `.monitor` object exists, derive `monitor_running` from the
   published task census (`get_background_task_census()` → any name containing
   `trade_monitor`). Single-process path unchanged.

2. **Blank/zero Positions X-ray rows (#590).** `build_positions_diag` needs live
   `router.active_signals` (full signal geometry: SL/TP, entry) AND `data_store` candle
   wicks to compute the SL-breach / candle-age columns. In isolated mode the facade only
   carries `_MockSignal` stubs (signal_id + timestamps) and `data_store is None`, so active
   positions rendered as blank-symbol, all-0.0 rows. Fix: the engine computes the diag
   itself (it has the real objects) and publishes the rendered rows to a new Redis key
   `snapshot:positions_diag` (TTL 60s) via `SnapshotWriter._write_positions_diag`; the API
   handler serves `engine.published_positions_diag()` when present, falling back to a live
   build in single-process mode. Mirrors the task-census pattern from #584.

   Files: `src/api/snapshot_store.py` (key + TTL), `src/api/snapshot_writer.py` (writer),
   `src/api/redis_engine.py` (`published_positions_diag()` + refresh), `src/api/server.py`
   (handler). 444 API tests green.

**Telemetry silenced:** `SCAN_STAGE_TIMING_ENABLED=false` written to VPS `/root/360-v2/.env`.
NOT yet applied (engine env is baked at container creation; deploy is `paths-ignore` for
`.env`/docs). **Takes effect on the next code deploy** — until then the timing line still
logs every ~3s. Deferred deliberately to keep the telemetry through high-volatility
conditions for confidence.

### Open items (priority order)

1. **Telemetry auto-silences on next code deploy** — `SCAN_STAGE_TIMING_ENABLED=false`
   already in `/root/360-v2/.env`; the next PR-to-main deploy recreates the engine and
   applies it. No action needed unless the ~3s log cadence becomes a problem sooner
   (then `docker compose --profile isolated up -d --no-deps --force-recreate engine`).
2. **Verify Positions X-ray post-#590 deploy** — confirm the Positions tab renders active
   signals with real symbol / SL / TP / candle-wick columns (not blank-0.0 rows), and
   `monitor_running: YES`. `snapshot:positions_diag` should be present in
   `redis-cli KEYS "snapshot:*"`; the same code deploy also applies
   `SCAN_STAGE_TIMING_ENABLED=false`.
3. **D1 NakedPositionDetector upgrade** — currently geometry-only (`stop_loss≤0`).
   Real naked-position detection (Binance stop order not placed) requires engine to
   publish `sl_order_id` per position in the Redis snapshot. Design needed.
4. **Verify regime-per-exit live** (PR #578) — `place_trailing_stop_market`/`trail_sl`
   in engine logs on TRENDING-aligned exits; `entry_regime`/`atr_value_at_entry`
   non-empty on dispatched positions; clean RANGING/QUIET market-closes.
5. **Verify funding-exit watcher live** (PR #581) — grep `funding_exit_watcher: exiting`;
   confirm `get_funding_info` populated near a settlement cycle.

---

## Session 17 checkpoint 2026-06-04 — regime-per-exit FSM + signing healthcheck + funding-exit watcher

### What shipped this session (5 PRs merged to `main`)

| PR | What | Type |
|---|---|---|
| #577 | Hurst gate + ATR trail width + multi-TF regime stamp | merged |
| #578 | Regime-per-exit FSM (TRAIL/VOLATILE/CANCEL) | owner sign-off, merged |
| #579 | ACTIVE_CONTEXT correction | docs, auto-merged |
| #580 | Signing service Docker healthcheck fix | ops, auto-merged |
| #581 | Funding-exit watcher (real funding data) | owner sign-off (delegated), merged |

#### PR #580 — signing container healthcheck (`c7c9081`)

`360scalp-v2-signing` shared the engine image whose Dockerfile HEALTHCHECK checks
for a `src.main` process + scanner heartbeat — neither exist in the signing
container, so it reported `unhealthy` after the 180s grace period despite serving
correctly. Fixed with a `healthcheck:` override in `docker-compose.yml`:
`test -S /app/sock/signing.sock` (socket created after KMS+Firestore init; stale
sockets unlinked on startup). **The long-standing "signing unhealthy" open item is
now resolved** — verify `docker ps` shows healthy after next redeploy.

#### PR #581 — funding-exit watcher (`2e99d7d`)

Exits positions that would PAY material funding within the pre-funding window.
Research (Binance docs) drove two key design choices:
- **Funding interval is not always 8h** (4h/8h/1h per pair) → read the real
  `nextFundingTime` per symbol from the mark-price stream.
- **The mark-price stream already carries `r` + `T`** — `MarkPriceFeed` was
  discarding them. Now captured via `get_funding_info(symbol)`.

Exit rule: `next_funding − now ≤ PRE_FUNDING_EXIT_WINDOW_SEC` (120s) AND paying
side AND `|rate| ≥ PRE_FUNDING_MIN_RATE` (0.05%). TRAILING positions skipped.
`close_reason="FUNDING_EXIT"`. Disable with `PRE_FUNDING_EXIT_WINDOW_SEC=0`.

#### Regime-per-exit FSM (PR #578) — full implementation

Owner-approved exit matrix (§3.2b):

| Post-pre-TP regime | Exit path |
|---|---|
| TRENDING + 15m confirm + aligned | **TRAIL** — Binance native `TRAILING_STOP_MARKET` |
| TRENDING (any condition mismatched) | **CANCEL** — immediate market close |
| RANGING / QUIET | **CANCEL** — immediate market close |
| VOLATILE | **VOLATILE** — tighten static SL by 20% |

Bugs fixed bundled:
1. `_apply_close_fill` — "close" phase fills were silently ignored (no dispatch table entry)
2. `_apply_tp2_fill` — when `tp3_qty == 0`, FSM was stranding in TP2_HIT forever

---

## Session 16 checkpoint 2026-06-03 — monitor watchdog + signing service aiohttp fix

**360-v2 PR #573** merged to main:

1. **`src/bootstrap.py` — `_resilient_monitor_loop` watchdog** — wraps `TradeMonitor.start()`
   in a self-healing loop; 5s backoff on exit, cleans up on normal `stop()`.
2. **`src/security/signing_service/server.py` — aiohttp chunk limit** raised from 8 KB
   to 64 KB. Fixes Reconciler WARNING on large `positionRisk` responses.

---

## Session 14 checkpoint 2026-06-03 — isolation cutover LIVE + post-cutover bug sweep

`API_PROCESS_ISOLATED=true` live on VPS. Engine runs `SnapshotWriter` only; separate
`api` container serves HTTP via `RedisEngineFacade`. Scanner-contention symptom resolved.

PRs #565 / #567 / #568 / #569 all merged. Three root causes fixed:
1. Missing `API_PROCESS_ISOLATED` in VPS `.env` → SnapshotWriter never started
2. Missing `init_keystore()` in api container → Binance key always ❌
3. Missing `init_kill_switch()` in api container → engine-wide enabled always ❌

**Policy adopted (owner standing authorisation, 2026-06-03):** CTE auto-merges PRs
once CI green / no conflicts / not an owner-sign-off item.
