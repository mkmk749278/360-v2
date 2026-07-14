# ACTIVE CONTEXT

*Live operational state. Updated at every session end.*

---

## 🔴 SESSION 56 2026-07-14 — Numpy-truthiness fail-open class: geometry A/B was DEAD, global context degraded, §2.1 BTC_DIR penalty never fired (branch `claude/pr-history-analysis-l3o9on`, 360-v2)

**Owner ask:** read briefs, review 4-day PR history, analyse the Strategy Lab PDF
(2026-07-14 07:00 UTC). Analysis found one production bug class with three victims.

### The bug class (code-verified + repro'd)

`HistoricalDataStore.get_candles()` returns `Dict[str, np.ndarray]`; `arr or []` /
`if not arr` on a multi-element numpy array raises `ValueError`. Three call sites
read the data store directly — bypassing the scanner's `_normalize_candle_dict`
list boundary (which exists because this class bit us before) — and swallowed the
raise in fail-open `except` handlers at DEBUG. Result: each feature silently did
nothing in production while all list-fixture tests stayed green:

1. **`Scanner._stamp_geometry_ab` (#722) — stop-geometry A/B stamped ZERO pairs
   in its first ~25h live.** Strategy Lab card + truth report both "no pairs yet"
   while the suppression audit classified hundreds through the same 5-min loop
   (that asymmetry was the tell). Fixed: None-checks, arrays passed through.
2. **`CryptoSignalEngine._build_global_market_context` (#721)** — ATR-percentile
   + HTF-prior inputs of the *published global* context silently None every cycle
   (per-signal contexts were fine — different, list-fed path). Allocator was
   routing on a coarser vector than the matrix cells it matches. Fixed.
3. **`check_btc_direction_gate` (OWNER_BRIEF §2.1 soft penalty) — never fired in
   production.** `_classify_btc_4h` raised on the numpy `close`; truth-report
   BTC_Dir column all-zero across ~2.8k scored samples while the structurally
   identical list-fed Sym_Dir gate fires. Repro: identical bearish inputs —
   list-fed returns the penalty, numpy-fed raises.

### Shipped

- `src/btc_direction.py` — `_classify_btc_4h` numpy-safe at the source (hardens
  sym-dir + countertrend-mover callers too).
- `src/scanner/__init__.py` — geometry stamp extracts arrays with None-checks;
  **BTC_DIR application ships DARK (owner decision, AskUserQuestion)**: new
  runtime tunable `btc_dir_penalty_apply` (Signal gating, default **OFF**) — while
  OFF every would-fire is shadow-logged (`btc_dir_shadow:*` suppression counter +
  `BTC_DIR_SHADOW` INFO line with the would-be points); ON applies as designed.
  Re-arming changes live scoring → owner flips after reviewing a real window.
- `src/main.py` — global-context candle reads numpy-safe.
- `config/__init__.py` + `src/runtime_tunables.py` — `BTC_DIR_PENALTY_APPLY`.
- `tests/test_incident_2026_07_14_numpy_truthiness.py` — 7 regressions driving
  the REAL production shape (real `HistoricalDataStore` seeded via
  `update_candle`); 4 of them fail on pre-fix code. Dark default pinned.

### Strategy Lab analysis verdicts (2026-07-14 07:00 UTC window)

- **`dispatch_staleness`: S54's DROP verdict is dead** — regressed to TUNE
  (n=961, 38% would-win, −0.06R EV). Do NOT loosen; the 75.6% read was an
  early-window artifact. Sample-floor discipline validated.
- **`min_confidence` KEEP** (+0.12R EV, n=1977; saved 881R vs missed 638R);
  `quiet_scalp_block` KEEP (+0.17R).
- **Shadow leader flipped:** SHADOW_MEAN_REVERT +0.44R avg, 54% win, n=290;
  S54's RANGE_FADE lead reversed (−0.07R, n=62). FUNDING_FADE confirmed bad.
- **Counterfactual sinks contained by gates:** MOVER_AVWAP_SCALP 0%/−0.95R
  (n=88), VOLUME_SURGE_BREAKOUT 2%/−0.64R (n=53), MOVER_TREND_PULLBACK −0.25R
  (n=2685, 4 emitted). Pruning evidence, not an emergency.
- **Emission drought persists:** ~10 emitted vs ~9,000 measured candidates;
  only QCB (+0.17R) and FUNDING_EXTREME (+0.57R) positive live. Volume-knob
  decision (S53 deferral) is becoming due.

### Follow-up sweep (same session, owner directive: "find ALL the bugs and test errors")

**Full audit of every `HistoricalDataStore.get_candles` consumer + every
boolean-context OHLCV array pattern in src/.** Four more numpy-truthiness
victims found and fixed (PR #727):

4. `trade_monitor._btc_opposes_direction` — BTC-correlation invalidation read
   fail-opened on every call (the env-gated adverse-tightening overlay AND its
   shadow logging were dead even where enabled). Data path repaired by #726's
   btc_direction fix; regression-pinned with a real numpy store. NOTE: the
   overlay stays dark (`INVALIDATION_BTC_CORRELATION_ENABLED` default false,
   has its own shadow branch) — no live behaviour change.
5. `trade_observer._get_reference_price` — returned None on every call.
6. `/market` Telegram command — BOTH primary and fallback branch broken; BTC
   price permanently "—". Fixed both.
7. `main._get_engine_context` — content-engine BTC price/1h/24h-change blanked
   forever. Fixed.
8. `scanner.diagnose_pair` — raised for any symbol WITH data (diagnosis broken
   exactly when there was something to diagnose). Fixed.
   Library hardening (same class, defense in depth): suppression_audit +
   invalidation_audit classify guards, volume_divergence inputs.
   Verified-safe (list-fed or len-guarded): all scalp.py evaluator sites,
   snapshot.py, alerts, kill switch, btc_state, cross-asset, macro gates.

**Test-suite debt cleared — the non-strict-xfail rot class.** 44 xfail markers
audited; every one was either contamination-blaming, stale-premised, or hiding
real rot:
- **Reload contamination fixed at the root**: test_pr04/test_pr06 rewrote
  reload-free (they deleted/re-imported config AND src.scanner mid-suite;
  their "default" assertions were circular — set the env then asserted it).
  All 28 cross-test-contamination xfails removed; suites green in CI order.
- **5 rotted tests found hiding under the blanket markers** (failing even in
  isolation, invisible because xfail): stale KZ-penalty expectations (kill_zone
  is profile-disabled), a 2-tuple patch of the 3-tuple cross-asset gate
  (which STILL hard-blocks — the xfail's "now soft-penalises" was a
  misdiagnosis), retired WATCHLIST tier, retired 360_SWING premise. Fixed or
  deleted with rationale.
- **pr01 "identity rewrite in dispatch" investigated: NO BUG** — FVG/ORDERBLOCK
  are `radar_only` by PR-04 governance so they never reach the queue; identity
  survives verbatim when rollout state is test-patched live. Tests fixed.
- Re-authored to current contracts: predictive SL-widening rejection
  (`sl_distance_widened` — new coverage), WHALE_MOMENTUM compress-cap
  telemetry, DIV_CONT TP1/TP2 dual-window geometry, SR_FLIP relative-penalty
  invariants, FUNDING_EXTREME QUIET non-block, min-SL floors via
  `_min_sl_distance_pct_for_setup`, lifespan/valid-for tables, "risk distance
  too tight" guard re-anchored to the reachable LSR protected-SL path.
- Deleted (premise retired, coverage exists elsewhere): SPOT/SWING channel
  tests (5), WATCHLIST reclassify, 360_SWING QUIET multiplier, two vacuous
  "no AI in pipeline" tests.

### NEXT

1. Owner: **verify kill switch re-enabled** from ops Control (S55 action;
   truth report shows last performance record ~3.7h old).
2. After a real window: review `BTC_DIR_SHADOW` would-fires (grep VPS logs /
   `btc_dir_shadow:*` counters) → flip `btc_dir_penalty_apply` from ops if the
   touched set looks right.
3. Geometry A/B now measuring for real — give it days before reading leaders
   (both arms ≥15 samples per strategy).
4. Unchanged: Telegram→app decouple (owner), volume knobs as live tunables
   (dark-first), Phase 4 master-arm (owner), `dispatch_staleness` action only
   if a fuller window re-sours.

---

## 🔴 SESSION 55 2026-07-13 — Engine-wedge → watchdog restart-storm → kill-switch incident fixed (branch `claude/pr-crypto-audit-review-a303z5`, 360-v2)

**Owner reported** (6 WATCHDOG Telegram screenshots, ~07:51–08:22 IST): repeating
`UNHEALTHY`, `scanner heartbeat 934s old`, `pricing-freshness 642s old`, then
`engine restart budget exhausted (3/h) … Escalating to kill switch — auto-trade
HALTS` firing every ~60s for 20+ minutes. **The kill switch is STILL engaged —
trading is halted until the owner re-enables it (owner-only by doctrine).** Engine
itself recovered 08:22; monitor-logs 04:15 UTC + Strategy Lab PDF 05:03 UTC confirm
healthy since.

### What actually happened (code-verified root cause)

1. **Primary — blocking Firestore read on the single asyncio event loop.**
   `RuntimeTunables._doc_values()` did a **synchronous** `.get()` on 5s-TTL expiry.
   Since #721 the scan loop calls `_rt.get(...)` per cycle, so a Firestore/network
   stall (client retry deadline = minutes) froze the **whole loop** — scanner
   heartbeat AND trade-monitor pricing publisher stopped **together**, exactly the
   observed twin-stall signature.
2. **Watchdog restart storm** — no boot grace; the `scanner_heartbeat` mtime
   **persists on the data volume across restarts**, so after its own restart the
   watchdog re-read the *pre-restart* age and re-killed the booting engine every 60s
   until the 3/h budget burned → kill switch.
3. **Page spam** — the budget-exhausted CRITICAL called `_page()` directly, bypassing
   the `dispatch_pages` cooldown → one identical page per loop.
4. **Contributor** — `StrategyEdgeStore.record()` did a full-store JSON dump *per
   record*; the 5-min classify batch (hundreds of records post #721/#722) ran
   hundreds of sync dumps + candle-copies on the loop thread.
5. **Healthcheck** — 180s grace vs a multi-minute REST re-seed of 75 pairs → UNHEALTHY
   flapping mid-boot → autoheal pile-on.

### Fixes shipped (all off the money path; kill-switch ENGAGE logic untouched)

- **`src/runtime_tunables.py`** — TTL expiry now **serves the stale cache instantly**
  and refreshes in a **single-flight daemon thread**; only the cold boot read fetches
  inline; failed refresh keeps last-known values; `set_values` merges into cache
  (no cold-fetch drop). Warns once/60s when the served cache is >60s stale.
- **`scripts/watchdog.py`** — `container_state()` returns `started_at` (parsed
  `State.StartedAt`); heartbeat/pricing ages **floored at engine StartedAt**; new
  `WATCHDOG_BOOT_GRACE_SEC` (600) disables the heartbeat-restart + blind-restart
  actions during warmup; budget-exhausted page is **cooldown-gated + silent while
  the kill switch is engaged** (engage still retried every loop until it lands);
  recovery re-arms the escalation page.
- **`src/strategy_edge.py` + `src/main.py`** — `record(..., persist=False)` + public
  `save()`; all three classify batches (invalidation, suppression, geometry) run via
  `await asyncio.to_thread(...)` with **one save per cycle** — the 5-min loop can
  never block the event loop again.
- **`healthcheck.py`** — grace 180→480s; a heartbeat mtime **older than the engine
  process** is treated as *warming up*, not stale (a genuine in-flight wedge — age ≤
  uptime — still fails). Made `main()` importable for tests.
- Tests: `tests/test_incident_2026_07_13.py` (new) + 11 new `test_watchdog.py`
  cases. Full suite green; ruff clean.

### ⚠️ OWNER ACTION REQUIRED
After this deploys and the engine shows healthy in ops, **re-enable auto-trade from
the ops Control page** (kill switch is owner-only to disengage — the watchdog has no
disengage path by design). Resting SL/TP on Binance protected open positions
throughout.

### Still open
- Issue **#714** — nightly encrypted backup failing since 2026-07-10 (no fresh
  off-site copy of the data volume). Separate item, high severity, untouched here.
- The exact 02:12-UTC first-trigger (what stalled Firestore) needs VPS logs, but the
  loop-blocking defect is real and fixed regardless of the trigger.

---

## 🟢 SESSION 54 2026-07-13 — Plan-vs-shipped audit + Stop-Geometry A/B wired (branch `claude/pr-crypto-audit-review-a303z5`, 360-v2 + 360ce-ops)

**Owner ask:** audit yesterday's PRs (#720/#721 + ops #62) against
`PLAN_AUTONOMOUS_PORTFOLIO.md`, the Crypto Market Doctrine, and the Strategy Lab
PDF (2026-07-13 05:03 UTC), and attend to the data.

### Audit verdict (verified in code, not PR bodies)

- Layers A–D + F, the 4 shadow units, tunables and truth-report sections: **all
  shipped and wired** as claimed.  Acknowledged deferrals stand: Telegram→app
  decouple (owner sign-off), volume knobs as live tunables (dark-first), Phase 4
  master-arm (owner).
- **One real gap found: Phase 3 item 8** — the fixed-% vs ATR/structure stop A/B
  for the *existing* evaluators (the plan's "single biggest edge lever") had only
  shipped for the 4 shadow units.  → closed this session (below).

### Strategy Lab first read (~12h window — directional only, sample floors rule)

- `dispatch_staleness` = **DROP** (n=717, **75.6% would-win**, 393R missed vs 66R
  saved, −0.46R/suppression) — the standout; acting on it is money-path →
  dark-first + owner sign-off, after a fuller window.
- `min_confidence` = TUNE (n=2202, ~neutral EV); `quiet_scalp_block` +
  `level_still_in_play` = KEEP (validated).
- SHADOW_RANGE_FADE 77%/+1.14R (31) — doctrine's range thesis leading;
  SHADOW_FUNDING_FADE 16%/−0.72R; FAILED_AUCTION_RECLAIM (live) −0.36R over ~438
  counterfactuals.  Allocator honestly cold in ASIA/QUIET/NORMAL/BTC_FALLING.

### Stop-Geometry A/B shipped (observe-only, Phase 3 item 8 measurement half)

- **`src/geometry_ab.py`**: pure ATR/structure stop math (`max(ATR14×1.5,
  pool_dist+buffer)` beyond the 20-bar swing extreme, 5% sanity clamp) +
  `stamp_geometry_pair` — every post-scoring candidate (emitted AND suppressed)
  stamps `X@FIXED` (live stop) + `X@ATR` pairs into a **dedicated ledger**
  (`data/geometry_ab_candidates.json`, own bound — can't evict gate records),
  per-(symbol,setup,side) 10-min pair cooldown, fail-open.
- Scanner: `_stamp_geometry_ab` hooks in `_stamp_suppressed` (own tunable — runs
  even with the suppression audit off) and on successful enqueue; the would-be
  stop is stamped on the signal (`Signal.geo_atr_stop`, consumed by nothing).
- 5-min audit loop classifies the pair ledger with the same TP1-before-SL
  classifier → edge matrix rows (`source="shadow"`).  **Allocator excludes
  `@FIXED`/`@ATR` rows** — measurement arms are never activatable.
- Truth report: `## Stop-Geometry A/B` (per-strategy pooled arms, ΔR, leader —
  leader named only when BOTH arms ≥15 samples); strategy rollups exclude
  variants (no double-counting).  Tunable `geometry_ab_enabled` ("Measurement").
- Ops `/strategy-lab`: new **Stop-geometry A/B card** (`reduce_geometry_ab`,
  engine-parity port; per-strategy rollup also excludes variants now).
- Tests: engine **6383 passed** (+22, incl. the doctrine scenario: wick to 98.7
  clips the 99.0 fixed stop, the 98.5 ATR stop survives to TP), ruff clean, mypy
  103 (< 113 baseline); ops **345 passed** (+3).  Fixture-ran
  `scripts/build_truth_report.py` — section renders with a real leader row.

### Follow-ups

- **Geometry application half** (owner sign-off, dark-first): wire the measured
  winner into live SL placement + `risk_scale` sizing once a real window names
  leaders per strategy/context.
- `dispatch_staleness` gate action after a fuller window (money-path, owner).
- Unchanged from S53: Telegram→app decouple; volume knobs as live tunables;
  Phase 4 master-arm.

---

## 🟢 SESSION 53 2026-07-12 — Autonomous Portfolio Phases 1–3 wired end-to-end: shadow ledger live, 4 shadow strategy units, allocator (recommendation mode), ops Strategy Lab (branch `claude/realtime-strategy-testing-ops-r318yu`, 360-v2 + 360ce-ops)

**Owner directive:** "use the time — try different strategies with real data in real
time with ops."  Foundation PR #720 (market_context / strategy_edge /
suppression_audit modules) was open-unmerged with nothing wired; merged it first
(CI green, observe-only), then wired the whole measurement pipeline.  **Everything
this session is observe-only / off the money path — zero change to which signals
emit or how they score.**  Scope selections (owner): core + allocator observe-only +
new strategy families.

### Engine (360-v2) — the measurement pipeline

- **Shadow ledger wired end-to-end:** `Scanner._stamp_suppressed` (fail-open,
  tunable-gated) stamps full geometry at all 8 post-scoring suppression gates
  (quiet_scalp_block, min_confidence/component floors, active_dup real branch only,
  dispatch_cooldown, data_stale, dispatch_staleness, level_still_in_play,
  regime_kill).  The 5-min `_invalidation_audit_loop` piggybacks
  `classify_pending()` (same in-memory `fetch_ohlc_since`) and feeds resolved
  outcomes into `StrategyEdgeStore` (`source="suppressed"`).
- **Latent bug fixed while relocating the mc stamp:** the #720 market-context stamp
  ran BEFORE `_populate_signal_context`, so `entry_regime` was always empty →
  Wyckoff phase always AMBIGUOUS.  Populate + mc stamp now both run above the QUIET
  gate; every suppressed candidate carries real regime + context key.
- **Real emitted outcomes feed the same matrix:** `trade_monitor._record_outcome`
  records into `StrategyEdgeStore` (`source="emitted"`, R from
  `original_sl_distance` — un-ratcheted risk), skipping EXPIRED_NO_FILL.
  `StrategyOutcome` gained provenance (`emitted|suppressed|shadow`); matrix rows
  expose `n_emitted/n_suppressed/n_shadow` so counterfactual vs realised edge is
  never conflated.
- **4 shadow-only strategy units** (`src/shadow_strategies.py`): SHADOW_RANGE_FADE,
  SHADOW_MEAN_REVERT, SHADOW_FUNDING_FADE, SHADOW_CASCADE_REVERSAL — pure functions,
  ATR-sized stops beyond the trigger extreme (doctrine §4), NO path to the signal
  queue; stamped as `gate_name="shadow_unit:*"` → classified → matrix
  (`source="shadow"`).  Per-(unit,symbol) 30-min stamp cooldown (monotonic,
  None-sentinel — a 0.0 sentinel silently swallowed all stamps for the first 30 min
  after boot; caught by test).
- **Strategy registry** (`src/strategy_portfolio.py`): context-affinity tags
  (phases/sessions) for all 27 SetupClass values + 4 shadow units;
  `is_context_aligned()`; single source of truth persisted to ops.
- **Allocator, RECOMMENDATION MODE** (`src/strategy_allocator.py`): every audit
  cycle reads current context × matrix verdicts → would-activate list (weights
  proportional to edge, alignment bonus ×1.2/×0.8) bounded by the safety envelope
  IN the math (`ALLOCATOR_MAX_CONCURRENT_STRATEGIES`=6,
  `ALLOCATOR_MAX_STRATEGY_WEIGHT`=0.35; capped surplus stays unallocated) + a
  would-demote list (NEGATIVE cells).  Persisted to
  `data/strategy_allocations.json`; **consumed by nothing** — Phase 4 master-arm is
  a later owner decision.
- **Publishers (5-min loop):** `data/market_context.json` (global BTC-anchored
  vector + affinity map) and `data/strategy_allocations.json`, atomic writes.
- **Truth report:** new `## Suppression Quality Audit` (per-gate WOULD_WIN% / EV-R /
  KEEP-TUNE-DROP) and `## Strategy × Context Edge Matrix` sections;
  `vps-monitor.yml` fetches `suppressed_candidates.json` + `strategy_edge_store.json`.
- **Tunables ("Measurement" category):** `market_context_enabled`,
  `suppression_audit_enabled`, `shadow_strategies_enabled`,
  `allocator_recommend_enabled` — all observe-only, live-flippable from ops.
- Tests: 6361 passed full suite; ruff clean; mypy at/below baseline.  New suites:
  portfolio registry, shadow units, allocator caps/floors, suppression wiring
  (incl. classify→edge end-to-end), trade-monitor edge feed, truth-report sections.

### Ops (360ce-ops) — Strategy Lab page

- New `/strategy-lab` (+ 60s HTMX partial): current context vector card (with
  staleness badge), Strategy×Context edge matrix (Wilson edge + verdict badges +
  emitted/suppressed/shadow split + in/out-of-design-context fit badges),
  per-strategy rollup, suppression-gate KEEP/TUNE/DROP table, and the allocator's
  "what it would do now" panel (mode RECOMMENDATION_ONLY, caps shown).  Data from
  the read-only volume (4 new accessors); engine math ported (~40 pure lines,
  thresholds displayed in footer); affinity comes from the engine-persisted map —
  zero hardcoding.

### Cost discipline

Stamps are O(1) in-memory appends; shadow units are pure list scans on already-warm
candles with per-symbol cooldowns; classification + all file writes batched on the
existing 5-min loop; tunables reads are the existing 5s-TTL cache.  No new network
or Firestore reads anywhere.

### Follow-ups (out of scope this session)

- Telegram→app-push decouple in `signal_router.py` — **owner sign-off (routing)**.
- Making QUIET-penalty / cooldown / min-confidence live tunables — money-path
  consumption change, dark-first.
- Phase 4 master-arm — owner flips only after the allocator's recommendations prove
  out in Strategy Lab on a real data window.
- Matrix/report verdicts need a fresh data window before they mean anything —
  don't judge the shadow units or gate verdicts until cells pass sample floors.

---

## 🟢 SESSION 52 2026-07-11 — 100eyes-parity Alerts v3: universe gate, honest touch counts, zone charts, card thumbnails (branch `claude/eye-scanner-alerts-charts-8xddta`, 360-v2 + lumin-app)

**Owner report (screenshots, 12:25 IST — one hour after S51 merged):** feed still
too busy ("look at exactly 100eyes"), small caps alerting (SKYAI/NAORIS/GRASS/GUN),
"(523 touches)" junk levels, alert-tap "still opens a normal chart", "still no auto
trade entry from chart".  Two causes: (a) S51 curated PUSH but left the FEED open to
all 75 pairs and the LevelBook's chop-inflated touch counts; (b) the owner's phone
runs a build predating S51's app PR #117 — the overlay + Take-trade button exist but
were never installed (in-app update banner is manual; told owner to update).

**Owner decisions (AskUserQuestion):** universe = majors+midcaps (≥$50M/day 24h vol,
tunable); NO global feed cap — fix junk quality floors instead; Take Trade stays
entry-only as S51 built it; alert cards get native mini-chart thumbnails.

### Engine (360-v2 PR #718 — off the money path, LevelBook untouched)

- **Universe gate:** `ALERTS_MIN_VOLUME_24H_USD` (50M default, ≤0 disables) —
  AlertService takes `volume_24h_getter` (PairManager dict lookup, no I/O);
  fail-closed on unknown volume.
- **Near-level honesty:** `_distinct_touch_events` state machine — consecutive
  in-band bars = ONE touch; re-arm needs `ALERTS_NEAR_LEVEL_MIN_SEPARATION_BARS` (3)
  out-of-band bars AND a close ≥ `ALERTS_NEAR_LEVEL_MIN_LEAVE_PCT` (0.5%) away.
  Chop rejection: > `ALERTS_NEAR_LEVEL_MAX_IN_BAND_FRAC` (25%) of lookback in-band →
  it's a range, no alert.  Enumerates `get_levels()` (not score-biased
  `nearest_level`) so junk can't shadow a clean level.
- **Zone geometry on the wire:** `zone_low/zone_high/touch_count/
  first_touch_bars_ago/last_touch_bars_ago` in metrics; back-compat keys kept,
  `touches` now honest (fixes "523×" titles on old app builds too).
- **Feed hygiene:** `_load` drops pre-v3 NEAR_* junk; first sweep lazily purges
  restored sub-gate symbols (can't purge in `_load` — PairManager volumes only
  exist after boot `refresh_pairs()`).
- Tests 57 (14 new); full suite 6240 passed.

### Lumin app (same branch, second PR)

- **100eyes chart from an alert:** shaded zone RECTANGLE via lightweight-charts
  ISeriesPrimitive (`attachPrimitive` verified in the bundled v4.2.3 standalone);
  divergence trend line mirrored on the RSI band (`priceScaleId: "rsi"`, values
  from `rsi_first/rsi_second`); `focus` visible-range zoom to the setup window
  (no more fitContent's 500 bars).  `AlertChartOverlay.fromAlert(chartTf:)` only
  emits time-anchored geometry on the alert's own TF (fixes latent wrong-TF draw).
- **Card thumbnails:** `AlertThumbnail` CustomPainter (no webview) — candles +
  zone box + divergence line + fired marker; `KlinesThumbnailService` (Binance
  public REST direct from phone, zero engine/GCP cost) with memory TTL cache,
  in-flight dedup, 3-fetch concurrency gate, SharedPreferences LRU disk layer;
  per-alert-id memo so scroll-back never refetches.  Alerts feed converted to
  `ListView.builder` (was eager ListView — 100 thumbnail cards must be lazy).

### Owner action required

**Install the app update** (in-app update banner / latest GitHub release APK) —
the S51 + S52 app features are invisible on the pre-#117 build on the phone.

---

## 🟢 SESSION 51 2026-07-11 — Alert spam cut + alert→chart setup sync + entry-only Take Trade (branch `claude/alerts-spam-chat-sync-pqemei`, 360-v2 + lumin-app)

**Owner directive (with screenshots):** the day-one Alerts feed spams (same
symbol firing volume+volatility+RSI at once, "1 touches" junk levels, every
15m wiggle buzzing the phone); tapping an alert must open the chart on the
ALERT's timeframe with the alert's indicators and the exact setup drawn, no
manual effort; and an alert-detail "Take trade" that places ENTRY ONLY (owner
explicit: no SL, no TP).

### Engine (all off the money path — scoring/dispatch/FSM/paid-routing untouched)

- **Quality floor:** `ALERTS_NEAR_LEVEL_MIN_TOUCHES` (default 3) — near-S/R
  alerts on 1-2-touch "levels" no longer fire (the worst spam class in the
  owner's screenshots).
- **Same-event coalescing:** volume spike + abnormal volatility from the same
  (symbol, TF) sweep = one market event → keep the volume card (it carries the
  move %), drop the volatility echo.
- **Per-symbol cross-type budget:** `ALERTS_SYMBOL_MAX_PER_WINDOW` (2) per
  `ALERTS_SYMBOL_WINDOW_SEC` (3600) — one violent candle can't stack cards for
  the same coin. Priority when the budget binds: divergence > near-level >
  RSI extreme > volume > volatility, and 4h > 1h > 15m. Budget rejections do
  NOT consume the type cooldown (the alert can still fire later).
- **Push curation (the real "spam" fix):** feed keeps everything (pull-based,
  filterable in-app, mirrors 100eyes); the PHONE only gets
  `ALERTS_PUSH_TIMEFRAMES` (default `1h,4h`) capped at
  `ALERTS_PUSH_MAX_PER_HOUR` (12). 15m alerts are feed-only now.
- **Divergence pivot geometry on the wire:** `pivot_a/b_bars_ago` +
  `pivot_a/b_price` in divergence metrics so the app draws the actual
  divergence line. Additive metrics — older apps unaffected.
- Tests: `tests/test_market_alerts.py` grown to 39 (floor, coalescing, budget
  priority, cooldown-not-consumed, push TF gate, push hourly budget).

### Lumin app (same branch)

- **Alert→chart sync:** `ChartPage(alert:)` opens on the alert's timeframe,
  auto-enables RSI for RSI-class alerts (session-only, saved prefs untouched),
  and draws the setup via the new `setAlertOverlay` JS bridge: solid S/R level
  line titled "Support · 43×" + alert-price reference, divergence pivot
  segment, alert-candle marker. `AlertChartOverlay`
  (`lib/features/charts/models/alert_overlay.dart`) owns the math (bars-ago →
  bar times). Alert context bar under the chart shows what fired + Take trade.
- **Feed filters (100eyes UX):** chip row on the Alerts tab — family
  (RSI / Divergence / S/R / Volume) + timeframe, client-side, session-only.
- **Take trade (entry-only):** `TakeAlertTradeSheet` →
  `OrderExecutor.placeAlertEntry` — market entry ONLY on the user's own
  device-key custody (same class as Take Signal manual trades; engine never
  manages the position). Sizing = Auto-trade settings (pct × leverage on live
  equity). Side pre-seeded from alert bias; NEUTRAL alerts force a pick.
  Idempotent on alert_id (log + broker clientOrderId). Unmissable no-SL/no-TP
  warning in the sheet; confirm button itself says "no SL / no TP".
  **CTE note for owner:** this is deliberately outside the engine's
  naked-position invariant (that guards ENGINE-managed positions); an
  alert-take is a user-initiated manual trade the user must close themselves.
  The engine-side pre-TP `protect_manual_entries` passive watcher still
  applies where auto-trade is connected. If we see users leaving these naked
  overnight, next step is an optional default-ON emergency stop % in the
  sheet.

---

## 🟢 SESSION 50 2026-07-11 — Market Alerts (Pulse → Alerts tab) + full FCM push (branch `claude/alerts-app-new-tab-ojlkps`, 360-v2 + lumin-app)

**Owner directive:** Pulse gets two top tabs — Dashboard (existing) + **Alerts**,
a 100eyes-Crypto-Scanner-class informational feed; detectors fire on their
NATURAL timeframe (some 4h, some 1h, some 15m, per the owner's screenshots);
and **full production FCM for all alerts and signals**.

### Engine (all off the money path — scoring/dispatch/FSM/paid-routing untouched)

- **`src/alerts/`** — detector pack + service:
  - Detectors (`detectors.py`, pure numpy on in-memory candles — **zero
    network I/O per sweep**): RSI Extremely Overbought/Oversold (15m/1h/4h,
    80/20), RSI Bullish/Bearish Divergence (1h/4h; strict fractal pivots +
    RSI zone gates + recency gate), Abnormal Volatility (15m, TR ≥ 3×prior
    ATR(14)), Abnormal Volume (15m, ≥5× 20-candle mean), Near Horizontal
    Support/Resistance (1h, LevelBook `nearest_level` ≤0.3%).
  - `AlertService` (`service.py`): own asyncio task (60s sweep, launched in
    bootstrap — can never slow the scanner), per-(symbol,type,TF) cooldowns
    (TF-relative for RSI types, wall-clock for hover-prone types), stale-feed
    guard (never alerts on frozen candles — S44/S49 class), closed-candle
    dedupe, ring buffer 300, persistence to `data/alerts.json` (feed AND
    cooldowns survive deploys — no re-push storm on restart).
  - All thresholds env-tunable (`ALERTS_*` block in config).
- **`/api/alerts`** — auth-gated, filters (type/symbol/limit), Cache-Control.
  Isolated mode fully wired: SnapshotWriter publishes `snapshot:alerts` every
  ~30s → RedisEngineFacade `published_alerts()` → route prefers the snapshot
  (mirrors positions_diag pattern).
- **`src/push_notifications.py`** — FCM via firebase-admin (already a dep;
  same service account as Phone Auth). **Topic-based** (`alerts`, `signals`)
  so there is NO device-token registry server-side. Contract: never blocks
  (send on worker thread), never raises, global rate cap
  (`FCM_MAX_SENDS_PER_MIN` 60), silent no-op when Firebase isn't initialised.
  Hooks: SignalRouter post-delivery (new signal), TradeMonitor
  `_record_outcome` (terminal outcomes, EXPIRED_NO_FILL excluded). Per-class
  gates: `FCM_PUSH_ALERTS/SIGNALS/OUTCOMES_ENABLED`.
- **Tests:** 40 new (detectors incl. divergence geometry + zone/recency
  gates, service cooldown/staleness/persistence, push contract, route +
  snapshot plumbing). Full suite **6215 passed**, ruff clean, mypy delta 0.

### Lumin app (same branch)

- **Pulse → two top tabs**: Dashboard (existing content, untouched) +
  **Alerts** — card feed (bias-coloured icon, symbol, TF chip, relative age),
  SWR-cached `/api/alerts` (30s TTL + disk persist), pull-to-refresh,
  keep-alive, empty/error states; tap a card → the symbol's Chart page.
  Mock mode has fixture alerts.
- **FCM end-to-end** (`lib/data/notification_service.dart`): topic
  subscribe on boot from persisted prefs (default both ON), Android 13
  permission request, foreground pushes → SnackBar with VIEW action
  (background/killed display is automatic via notification payload),
  tap routing — `signals` → Signals tab, `pulse_alerts` → Pulse → Alerts
  top tab (cold-start taps included). **Menu → Notifications** page with
  per-class toggles (off = unsubscribe: delivery stops at FCM).
- **CI:** `build-apk.yml` injects `POST_NOTIFICATIONS` into the manifest
  (same pattern as INTERNET). `firebase_messaging ^15.1.0` added.
- Analyzer 0 errors; **169 app tests pass** (9 new MarketAlert tests).

### Ship notes / owner verify after deploy

1. Engine logs: `AlertService started`, first `ALERT <SYM> ...` lines;
   `redis-cli GET snapshot:alerts` non-empty; app Pulse → Alerts populates.
2. FCM: needs `FIREBASE_SERVICE_ACCOUNT_PATH`/`FIREBASE_PROJECT_ID` set (they
   already are for Phone Auth). Watch for `push: Firebase Admin not
   initialised` warnings — that means pushes are off.
3. First **release build** must include the google-services secret as usual;
   verify a real device receives a signal push + an alert push, and that the
   Menu → Notifications toggles stop delivery.
4. Alert volume: watch a day of `ALERT` lines; if noisy, raise cooldowns via
   env (`ALERTS_*_COOLDOWN_*`, `ALERTS_RSI_OVERBOUGHT/OVERSOLD`, multipliers)
   — no redeploy of code needed beyond env.

---

## 🔴 SESSION 49 2026-07-10 — P1: TAIKO SL overshoot root-caused — Binance decommissioned our legacy WS URLs (branch `claude/taiko-sl-overshoot-6lds39`)

**Owner report (screenshot):** TAIKOUSDT LONG (MVRTP-8ABCA1F2, entry 0.09074,
SL 0.09060) still ACTIVE at 0.08721 — **3.7% past the stop, never closed**.
Same state on APEUSDT + POWERUSDT (issue #712; the new S48 F-07 pager fired
correctly on both GitHub and the alert Telegram bot — the detection layer works).

### Root cause (real-data-first: probe → vendor changelog → ecosystem confirmation)

Binance's **2026-03-06 USDⓈ-M Futures WebSocket System Upgrade** split WS
traffic into routed base paths (`/public`, `/market`, `/private`) and
**decommissioned legacy unrouted URLs after 2026-04-23**. Legacy connections
still complete the TCP+WS handshake but *market/private-category streams never
push a single frame* — silent death, no exception, so reconnect/backoff never
fires. Enforcement evidently reached our long-lived connections recently.

- `websocket_manager` / `BINANCE_FUTURES_WS_BASE` were **already migrated**
  (2026-05-14 incident) → scanner klines healthy, which masked the rest.
- `src/execution/mark_price_feed.py` was **missed**: still
  `wss://fstream.binance.com/ws/!markPrice@arr@1s` → feed "connected" with an
  **empty price map**. Everything downstream starved silently: the #706
  stale-candle→mark-price SL/TP fallback (blind on out-of-universe symbols —
  TAIKO's kline age was None after the day's deploy restarts), **pre-TP
  dispatch, trailing, funding-exit watcher** (`missing_funding_rate=264` in the
  truth report is the same outage).
- `src/execution/user_data_stream.py` was **also missed**: legacy
  `/ws/<listenKey>` → **FSM order-fill events (real money) not delivered**;
  only the REST Reconciler was compensating.
- The Lumin app polls `fapi/v1/premiumIndex` REST directly — that's why the
  owner's phone showed the real price while the engine was blind.

### Shipped on this branch

1. `mark_price_feed`: routed URL (`/market/ws/!markPrice@arr@1s`,
   env `MARK_PRICE_FEED_WS_URL`) + legacy-override auto-correct (same defence
   websocket_manager has) + **silence watchdog** — the @1s stream ticking
   nothing for `MARK_PRICE_FEED_SILENCE_TIMEOUT_SEC` (30s) now ERROR-logs and
   force-reconnects: silence can never look like health on the SL/TP path again.
2. `user_data_stream`: routed private URL
   `/private/ws?listenKey=<key>&events=<all legacy event types>` — the
   `events` param is REQUIRED in production (omitting it delivers nothing;
   field-confirmed by unicorn-binance-websocket-api). Default list mirrors
   legacy implicit-all, so parser behaviour is unchanged.
3. Regression pins: routed-URL contracts for both modules, legacy-path
   normalisation, silence-watchdog raise + healthy-path no-raise. Full suite
   green; ruff/mypy clean.

### On deploy (expected behaviour — tell the owner)

Engine restart → feed connects routed → mark prices flow → the blind ACTIVE
signals (TAIKO/APE/POWER) get repriced via the #706 fallback and **close
immediately at the real mark price**, recording the true overshot loss (TAIKO
≈ −3.9%, not the −0.15% SL). That is honest telemetry, not a bug. Verify in
logs: `mark_price_feed: receiving (N symbols in first frame)` and
`user_data_stream: connecting to wss://fstream.binance.com/private/ws?...`.

### Open follow-ups

1. **Verify user-data stream live after deploy** — watch for ORDER_TRADE_UPDATE
   events on the next real fill (Reconciler covers the gap meanwhile).
2. **REST `premiumIndex` fallback as third pricing tier** for the monitor when
   both kline + mark feed are dead (the app already proves it works) — new
   money-path pricing source, so dark-first + owner sign-off; not shoved in here.
3. Owner NEXT items from S48 unchanged (alert-bot secrets done per screenshot;
   healthchecks.io + host setup + drill still pending).

---

## 🟢 SESSION 48 2026-07-10 — Autonomous self-healing ops stack (branch `claude/audit-report-implementation-knx1h1`)

**Owner directive:** "we need an autonomous system — I'm only the one handling
all this, one can't observe all: self checks, self heal-up, self restart,
freezing issues, VPS issues. First go through the web to find what we can do."
Plus: **Telegram is fully operational in India again** → Telegram is the
paging channel (not ntfy/FCM).

**Researched first** (web): the standard single-node self-healing pyramid —
deep healthchecks → autoheal → custom supervisor → phone paging → external
dead-man's switch → host self-maintenance. Full design + rollout in
**`docs/AUTONOMOUS_OPS.md`** (the doc to read before touching any of this).

### Shipped (all off the money path — scoring/dispatch/FSM untouched)

- **Authority doctrine:** the autonomous machinery takes *risk-reducing
  actions only* — page / restart / prune / ENGAGE kill switch. It can never
  disengage, reset a breaker, or re-enable trading (source-level test pins
  the no-disengage property).
- **Layer 1:** redis + api containers got real healthchecks (ping /
  `/api/health` HTTP round-trip); engine already probed heartbeat freshness.
- **Layer 2:** `autoheal` sidecar (pinned 1.2.0) restarts any
  `autoheal=true` container that goes unhealthy — the "alive but frozen"
  class (S44/45/46) now self-recovers. Watchdog deliberately not labeled.
- **Layer 3:** new `watchdog` container (`scripts/watchdog.py`, stdlib-only,
  60s loop, docker.sock + data volume): container states, wedged scan loop
  (→ budgeted engine restart, 3/h), **audit F-07 blind-open-position pager**
  (stale 1m kline AND no mark price → page; persisting → engine restart,
  which re-seeds candles = the manual MVLLUSDT fix automated), breaker-trip
  paging (never resets), disk 85%/92% (page/auto-prune), memory pressure,
  budget-exhausted → **kill-switch engage** via API owner token + CRITICAL
  page. Dedupe 30min/key + ✅ recovery notices; audit JSONL + persisted state.
- **Engine feed for F-07:** trade monitor publishes
  `data/pricing_freshness.json` every 30s (`PRICING_FRESHNESS_PUBLISH_SEC`,
  local disk, hot-path clean); `monitor_heartbeat.py` gained
  `check_pricing_freshness()` → INVARIANT_WARN (hourly path pages too).
- **Layer 4:** `scripts/notify_telegram.py` (stdlib, never raises, never
  leaks token; `ALERT_TELEGRAM_CHAT_ID` else `TELEGRAM_ADMIN_CHAT_ID`);
  `vps-liveness.yml` + `vps-backup.yml` now page Telegram (problems AND
  recovery) alongside the auto-detected issue. **Owner chose a dedicated
  alert bot** → set `ALERT_TELEGRAM_BOT_TOKEN` + `ALERT_TELEGRAM_CHAT_ID`
  (repo secrets AND `.env`); falls back to `TELEGRAM_BOT_TOKEN` /
  `TELEGRAM_ADMIN_CHAT_ID` when unset. In-engine alerts
  (tripwires/breaker/kill-switch via telegram_alerts.py) stay on the
  engine bot by design.
- **Layer 5:** healthchecks.io dead-man pings from the watchdog loop
  (`HEALTHCHECKS_PING_URL`) + a host cron — external phone page when the
  whole box dies (~5 min). Also fixes audit F-20 (GitHub-only alerting).
- **Layer 0:** `deploy/host/setup_host.sh` (idempotent, as-code — audit
  S-7): swap, earlyoom, unattended-upgrades, fail2ban, ufw,
  `360scalp.service` (stack up after reboot via deploy.sh), nightly prune,
  dead-man cron.

**Tests:** 6168 passed (was 6120) — new: watchdog decision ladder,
notifier contract, F-07 publisher contract, heartbeat pricing checks.
Ruff clean, mypy delta zero, compose config validates (both profiles).
The dedupe test caught a real bug (fresh findings suppressed inside the
first cooldown window) — fixed before ship.

### Ops dashboard upgrade (same session, 360ce-ops branch `claude/audit-report-implementation-knx1h1`)

- **/audit** — audit-findings board: F-01..F-20 + S48 extras with colour-badged
  done/partial/open/owner status, needs-attention-first sort, summary-counter
  filters. Backed by `app/audit_findings.py` — **update it at session end**
  whenever a finding's status changes (same discipline as this file).
- **/data** — full read-only file browser of `/engine-data` (size + colour-coded
  write recency as a liveness readout) + raw downloads via `/data/raw/{path}`
  (resolve-then-contain traversal guard, tested).
- **Coloured badges** (signal lifecycle, severity, audit status) + **sortable
  tables site-wide** (`static/sort.js`, numeric-aware) + Signals lists open
  positions first (engine `is_open` stamp, heuristic fallback).
- Ops suite 327 passed (was 311).

### NEXT (owner, ~20 min total — the paging is inert until 1+2 are done)

1. Create the alert bot (@BotFather), DM it once, get the chat id from
   `getUpdates`; add `ALERT_TELEGRAM_BOT_TOKEN` + `ALERT_TELEGRAM_CHAT_ID`
   as repo secrets AND in the VPS `.env`.
2. healthchecks.io: two free checks → `HEALTHCHECKS_PING_URL` in `.env` +
   URL for setup_host.sh; install their app (or Telegram integration).
3. `bash deploy.sh` (brings up autoheal + watchdog), then
   `sudo REPO_DIR=$(pwd) bash deploy/host/setup_host.sh`.
4. **Drill it**: `docker pause 360scalp-v2-engine` → expect unhealthy →
   autoheal restart → phone page within ~2 min. An untested pager is a hope.
5. Session-46/47 open items unchanged (diag_paper_health root-cause on VPS;
   BACKUP_PASSPHRASE secret + first restore drill; ops TOTP enroll).

---

## 🟢 SESSION 47 2026-07-10 — Institutional audit + production-grade remediation sweep (branch `claude/crypto-audit-institutional-tic0ix`, all 3 code repos)

**Owner asked:** full institutional-grade audit of the whole stack, then "fix
everything actually what you can like production grade."

### Delivered part 1 — the audit

`docs/INSTITUTIONAL_AUDIT_2026_07_10.md` — 16-section audit across all four
repos (architecture, security, trading engine, signal quality, exchange
integration, auto-trade, mobile, infra, compliance, continuity, competitive
benchmark, findings table F-01..F-20, priority roadmap, scores). Verdict:
**Early Production**; risk HIGH; the three blockers to Production Ready are
(1) unproven net edge, (2) no backups/DR + bus factor 1, (3) no legal
entity/counsel. All figures sourced from our own telemetry.

### Delivered part 2 — remediations shipped on this branch

**360-v2** (all off-money-path: docs, infra, telemetry, API perimeter):
- **F-02 backups/DR:** `scripts/backup_data.sh` (WAL-safe SQLite snapshot via
  stdlib backup API → tar → AES-256-CBC pbkdf2 encrypt → verify → rotate 14)
  + `scripts/restore_data.sh` (refuses under a running engine; preserves
  prior state in `.pre_restore_<stamp>`) + nightly `vps-backup.yml` (SSH,
  pulls encrypted artifact off-box 30d, files `severity:high` auto-detected
  issue on failure, self-closes on success). **Needs new repo secret
  `BACKUP_PASSPHRASE`** (same value into the password manager).
- **F-02/F-04 docs:** `docs/DR_RUNBOOK.md` (RTO 2h/RPO 24h, scenarios A–D,
  drill log), `docs/SAFE_HALT_RUNBOOK.md` (non-engineer kill-switch
  procedure), `docs/CONTINUITY_PACK_TEMPLATE.md` (vault checklist),
  `docs/STATISTICAL_CHANGE_POLICY.md` (n≥200/21d bar, frozen control,
  proof-window discipline — binds future sessions).
- **F-14 API rate limiting:** `src/api/rate_limit.py` + wired in
  `server.py` — per-client (Bearer-hash else first-hop XFF IP) sliding
  window, 240/min default, health paths exempt, bounded memory, 429 +
  Retry-After. Env: `API_RATE_LIMIT_ENABLED/_PER_MIN/_MAX_CLIENTS`.
  18 new tests; full api suite green.
- **F-11 signing socket:** 0666 → **0660 + chgrp appgroup** (both containers
  share the image so the group exists; env `SIGNING_SERVICE_SOCKET_GROUP`);
  dev/test fallback to 0666 with loud warning. ⚠️ **Owner-sign-off item
  (signing service) — merge of this branch is the sign-off; verify engine
  connects after deploy** (`test -S` + a signed request in logs).
- **F-09 paper-silence paging:** `monitor_heartbeat.py` rewritten (env
  `ENGINE_DATA_DIR`, testable) + new check — engine perf file fresh (<6h)
  while ALL paper ledgers frozen (>24h) → `INVARIANT_WARN` line;
  `vps-liveness.yml` now pages on ANY `INVARIANT_WARN:` (future checks
  need no workflow change). 10 new tests.

**360ce-ops** (same branch): **F-08 TOTP 2FA** — stdlib RFC 6238
(`app/totp.py`, RFC test vectors), ±1-step drift, replay-protected,
enabled via `OPS_TOTP_SECRET` (enroll: `python scripts/generate_totp_secret.py`),
wired into BOTH login paths (web form field appears when enabled;
`/api/v1/auth/login` takes `totp`); failures return the same generic
message on either factor. Unset env = password-only (safe rollout).
Full ops suite green (311).

**lumin-app** (same branch): **F-12 obfuscation** — `--obfuscate
--split-debug-info` on BOTH the APK and AAB builds in `build-apk.yml`;
symbol maps uploaded as 90-day artifact (`flutter symbolize` for crash
traces). ⚠️ First obfuscated release: smoke-test Phone Auth + Play Billing
on a real device before promoting (reflection-adjacent plugins).

### Deliberately NOT done here (and why)

- **F-05 FSM LIMIT-at-zone / F-06 portfolio cap** — money-path FSM/dispatch
  design work, owner-sign-off items with their own spec docs; not
  shove-in-able alongside a hardening sweep.
- **F-13 remove in-app updater** — the GitHub-release APK path may still be
  a real distribution channel for pre-Play installs; removal is a
  distribution decision for the owner (audit recommends retiring it).
- **F-15 JSON→transactional store, F-10 owner-key split** — need design;
  JWT crypto itself verified sound (constant-time, alg-pinned, exp-checked).
- Legal entity / counsel / second operator — not code.

### NEXT

1. Owner: add `BACKUP_PASSPHRASE` secret → run backup workflow once → do the
   first restore drill (DR_RUNBOOK) + fill the continuity vault.
2. Owner: enroll TOTP (`generate_totp_secret.py` → env → redeploy ops).
3. Verify after deploy: signing socket 0660 connect OK; rate limiter logs
   sane; first liveness run shows the paper-books line.
4. S46 open item unchanged: run `diag_paper_health.py` on the VPS to
   root-cause the paper freeze (the new invariant only *detects* it).
5. Then the S46 verify-on-live-data list (mover re-seed, BE arm, is_open).

---

## 🟢 SESSION 46 2026-07-10 — Day-after-#707 production incident sweep (frozen mover price, dead BE arm, open/closed display truth, frozen paper book)

**Owner reported 7 symptoms** (screenshots + ops PDFs): paper trading frozen
~24h; actives should sort first; MVLLUSDT "reached >TP3 but shows closed at
TP1"; volume down to ~12/24h; Signals(12) vs Profit(7) mismatch; "TPs/SLs hit
but nothing happens"; "+2% runs going back to full −2.5% SL, no BE, no trail".
Branch (all three repos): `claude/paper-trade-frozen-signals-pamcw8`.

### Root causes found (code-verified)

1. **MVLLUSDT frozen price / blind SL-TP-trail** — promoted movers have NO WS
   kline subscription; their only candle writes are REST seeds, and seeds
   never stamped `_last_kline_update_ts`. `last_kline_age_seconds()` = None
   forever → BOTH staleness protections (scanner dispatch gate #359 +
   trade_monitor mark-feed fallback #706) fail-open on None. MVLL's close
   froze at 38.1800 for 11+ h with an open TP1_HIT runner: PnL/MFE pinned at
   +4.63%, TP2/TP3 detection blind, trail immobile, SL backstop dead. This is
   ALSO the "TPs/SLs hit but nothing happens" complaint, and it means mover
   evaluators were reading up-to-6h-frozen candles for their whole hold.
   **FIXED:** REST seeds/gap-fills stamp freshness; `_candle_stale` treats
   age-None as stale after a post-boot grace; scanner re-seeds active movers
   when 1m age > `MOVER_CANDLE_REFRESH_SEC` (120s, bounded/throttled).
2. **BE never armed on wide-stop signals** — #702's arm = max(flat 1%, 1R of
   own stop, 0.75×noise) double-counts the #702 noise-floor stop WIDENING: 1R
   of a widened 2.4-2.7% stop ≈ at/above TP1 → unreachable under the TP1
   full close. Exactly the owner's "+2% → full SL" trades (EPIC/CLO/POWER/
   TIA). **FIXED:** arm capped at `be_arm_tp1_cap_fraction` (0.5, runtime
   tunable) × the trade's own TP1 distance, floored at the flat trigger;
   wired in BOTH trade_monitor and pretp_dispatcher. **BE-shift = owner-
   sign-off item — merge of this branch is the sign-off.**
3. **TP1_HIT is ambiguous since #707** — a non-mover CLOSES at TP1_HIT
   (BE_THEN_TP1) while a runner mover at TP1_HIT/TP2_HIT is still OPEN.
   EIGENUSDT (closed) showed "open 8h"; MVLLUSDT (open runner) read "closed
   at TP1" (app shows the locked bestTp result for TP-hit statuses); the
   API's `status=="ACTIVE"` open filter dropped open runners from the Open
   tab. **FIXED:** `is_open` (active-book membership minus terminal
   statuses) on `/api/signals` + snapshot cache; lumin-app maps it to
   `MockSignal.effectiveIsOpen` and every widget uses it (labels, fade,
   live-PnL vs banked result, price polling); All feed sorts open-first
   (stable partition).
4. **Signals(12) vs Profit(7)** — NOT a bug: the ops Profit 24h window reads
   `signal_performance.json` = closed signals only (7 closed; EPIC/DELL/APT/
   MVLL still open); actives are live-window only. The "0 active · 7
   stopped" header is just misleading copy.
5. **Volume drop (~48/day Jul-06 → 9 Jul-08 → ~12/24h)** — began BEFORE
   #707: it is the intended compounding of owner-approved gates — #702 cohort
   edge gate + CT_LONG/CT_SHORT macro gates + #705 expiry-OFF (signals now
   occupy the book for hours: DELL open 13h) + #707 dup guard blocking
   re-entry while a same-key signal sits open + loss-streak escalation.
   Mover emissions also collapsed (truth report: MVRTP 35388 generated → 2
   emitted). No code change — knobs are on the ops panel if volume is the
   priority; the stale-candle fix may itself restore some mover volume
   (fresh data instead of frozen).
6. **Paper book frozen at the #707 deploy (~Jul 9 12:02 IST)** — engine book
   kept dispatching/closing signals with ZERO paper counterparts after the
   restart (BABAUSDT 09:22 IST was the last paper close; OP/CLO/EIGEN/TIA/
   POWER all closed with no paper rows). NOT root-caused statically: the
   open path has many silent-skip exits (empty paper cohort, per-user PAPER
   eligibility, risk gate, qty/notional floors, fan-out exceptions).
   **SHIPPED the decisive diagnostic:** `scripts/diag_paper_health.py`
   (+ ops Diag page button) — joins boot config, paper cohort modes/prefs,
   per-user book ledgers, and recent signals into per-signal × per-user
   verdicts. **NEXT SESSION: run it on the VPS**, plus:
   `docker logs 360scalp-v2-engine --since 30h 2>&1 | grep -E "paper_trade_skip|paper fanout|Auto-execution|risk_gate"`

### Shipped (this branch, owner to merge)

- 360-v2: staleness fix (seed stamping + boot-grace + mover re-seed, 20 new
  tests), BE arm TP1 cap (7 tests, sign-off item), `/api/signals is_open`
  (4 tests), `diag_paper_health.py`. Full suite green, ruff clean.
- 360ce-ops: Diag page "paper book health" tool (allowlist + route + 3 tests).
- lumin-app: `isOpen`/`effectiveIsOpen` everywhere, open-first All feed,
  "runner riding" label, live-PnL for open runners (1 new test file).

### Verify on live data (next session)

- MVLL-class: evicted-mover signals reprice off the mark feed (log
  `SL backstop via mark price` / trail moving); no more 11h-frozen closes.
- Mover re-seed logs (`mover candle refresh: re-seeded`) and that mover
  emissions are not blocked by the now-armed dispatch staleness gate.
- BE arm: `be_shift` triggers appearing on wide-stop signals around ~50% of
  the way to TP1; "+2% → full SL" round-trips should disappear.
- Paper: run the new diag; identify and fix the actual gate.

---

## 🟢 SESSION 45 2026-07-09 — PR #702 verdict + mover-path profitability package (owner-approved ACTIVE)

**Owner asked:** analyse PR #702's live effect (3d Profit CSV + PDF vs the
Jun-01→Jul-05 range CSV), deep-dive the mover paths, then implement fixes.

### Verdict on #702 (85 signals, small window — caveats below)

- Book flipped: **−0.39%/day gross (35d before) → +6.0%/day gross / +12.1% net
  (3d after)**. Win rate flat (41→42%) — the gain is exits, exactly what #702
  targeted: TP-hit rate 9%→21%, SL rate 34%→27%, MFE capture −3%→+10%.
- **Exit leak collapsed:** the BE@1%→TP1 simulator beat engine real exits by
  +36.5% total before; after, +2.74% — and ALL of it from 2 VSB signals. Every
  other path's real exits now match the ideal-BE sim.
- Caveats: 3d window straddles the merge (~1.3d pre), n=85, one KORU +5.5%
  outlier; NEW_LISTING stamps not visible in the export yet (36/85 UNKNOWN).

### Movers are the remaining drag (deep dive)

- MVRTP: −0.14%/trade (n=97, before) → **−0.46%/trade (n=18, after)**; volume
  doubled to 6/day. MVAVW: 20 signals across both windows, **zero TP hits,
  zero SL hits, 100% expired** — pure fee drag as shaped.
- 42% of after-window movers reached ≥1% MFE but realised ≤0 (68% MFE
  forfeited in 3d): HMSTR +31.3% MFE→0, TRIA +12.3%→0. Part of this is the
  Session-44 stale-candle bug (#706 fixed, needs a data window); the rest is
  exit shape — the 1R full-close inverts a momentum path's payoff.
- Cohort gate cold-start: store persists only since #702, no cohort has 10
  fresh samples → known-toxic cohorts (MVRTP LONG/RANGING) still dispatch.
- MONUSDT MVRTP LONG: 6 dispatches/−3.7% in 3d (cooldown metronome);
  SPCXUSDT MVRTP SHORT emitted twice 7min apart, identical entry/SL (dup
  guard gap across restarts).

### Shipped (branch `claude/pr-702-signal-analysis-c9zbsb`, PR #707) — ACTIVE

**Owner sign-off in-session: "make it live, no dark flags"** — the Profit
tracker's measured MFE/give-back over both windows is the counterfactual
evidence (mirrors the #702 activation). Every flag stays ops-reversible; the
OFF state shadow-logs so a rollback keeps measuring.

1. **Mover runner exit** (`mover_runner_exit_enabled`, **ON**) —
   `src/execution/runner_policy.py` + trade_monitor: movers bank 40% at TP1,
   30% at TP2 (stop→TP1), and the last 30% rides the phase-tightened ATR
   trail with **NO fixed TP3 cap** (owner directive, from the 4-5%-MFE
   screenshot rows: crossing TP3 stamps+posts but does not close — the trail
   is the only exit for the final slice). Banked slices credited honestly in
   `_set_realized_pnl`. Engine signal book only — the FSM/user-position
   runner is a separate owner-sign-off change.
2. **Ops live/shadow switches per mover path** (`mover_trend_pullback_live` /
   `mover_avwap_scalp_live`, default = env = ON) — flip a path to shadow-only
   from ops, no redeploy. Candidate: MVAVW → shadow on its 0-conversion record
   (owner call, not flipped).
3. **Loss-streak cooldown escalation** (`loss_streak_escalation_enabled`,
   **ON**; cap `loss_streak_cap_hours` 12h) — consecutive losses on the same
   symbol×setup×direction double the lifecycle cooldown extension (1h→2h→4h…).
   Streaks persist to `data/loss_streaks.json`.
4. **Active-duplicate dispatch guard** (`active_dup_guard_enabled`, **ON**) —
   blocks dispatch when the live book already holds the same
   symbol×setup×direction; restart-proof.

Tests: `tests/test_mover_runner_exit.py` (25); mover shadow tests updated to
the tunable-based switch. Full suite 6,064 passed, ruff/mypy clean.

### Verify on live data (next session)

- Mover exits: TP1 posts should read "banked 40%, runner riding"; watch
  PROFIT_LOCKED / TP2+/TP3 outcomes appearing on MVRTP; mover give-back and
  capture on the Profit page vs this window's −14% capture baseline.
- `loss_streak escalate` + `active_dup skip` log lines / suppression counters
  behaving (MONUSDT-style churn dropping, no duplicate live signals).
- Ops action needing NO code: `cohort_edge_gate_min_n` 10→5 to arm the cohort
  gate sooner while the persisted store fills.
- Verify #706 restored mover TP detection (no more 4-5% MFE movers expiring
  at 0 on stale candles) and NEW_LISTING stamps appearing in exports.

---

## 🟢 SESSION 44 2026-07-08 — Stale-candle price freeze on dropped-universe movers (peak stuck, SL/TP backstop blind)

**Owner-reported symptom:** CAPUSDT SHORT on the app showed **Live PnL +1.42%**
next to **Peak so far +0.05%** — impossible, a peak can't sit below the live gain.
Ops Profit tab had it right: candle-replay **Max profit +3.24%** (max price
0.019710) vs the engine's stored `max_favorable_excursion_pct` of **+0.05%**.

### Root cause (branch `claude/performance-metrics-analysis-h7cjxk`)

`_latest_price` returns the last 1m candle close from the scan store. When a
surge-promoted MOVER (or intermittently re-scanned Tier-3 pair) drops out of the
active scan universe, the store keeps serving a **stale, non-None** close near
entry. The pre-existing mark-feed fallback only fired on `None`, so it never
engaged — pinning `sig.current_price`, and with it `pnl_pct`, the running MFE
(peak) and the **SL/TP/invalidation backstop** (`_candle_extremes` reads the same
frozen high/low), all on an hours-old price. Same class as the BEATUSDT −6.52%
blown-stop; that fix only covered the None case, not stale-but-present.

### Fixed

- **Engine (360-v2):** `_latest_price` + `_candle_extremes` now check the store's
  1m kline age (`last_kline_age_seconds`, the same signal the scanner's dispatch
  gate uses). Older than the bound → price the signal off the all-symbols mark
  feed (1s cadence). `age is None` (seed-loaded / pre-first-WS-frame) counts as
  fresh, mirroring the scanner, so nothing diverts post-boot. Behaviour unchanged
  when the candle is fresh or the feed lacks the symbol. Wired through the #702
  runtime-tunables control plane: `mark_feed_staleness_enabled` (default ON) +
  `mark_feed_staleness_max_age_sec` (default 120s, range 30–600), ops-panel
  adjustable, reversible without redeploy. Tests: `test_trade_monitor_stale_price.py`
  (7 cases). Touches SL/TP evaluation → **owner-sign-off item, held from auto-merge.**
- **Lumin app** (branch same name): detail-sheet "Peak so far" can no longer render
  below the app's own live PnL — clamps the peak up to at least the current gain
  (live signals); closed signals keep the engine's recorded historical max. This
  removes the visible contradiction but can't reconstruct the true 3.24% on its own;
  the engine fix above is what restores the accurate peak end-to-end.

### Verify on live data (next session)

- Confirm a dropped-universe MOVER's snapshot `pnl_pct` / MFE now track the mark
  feed (not frozen near entry); Peak so far on the app matches ops Max profit.
- Watch for any signal whose SL/TP now fires off the mark-price point estimate
  (high=low=mark) when its candle is stale — expected, but confirm no premature
  stops on healthy pairs (the age bound should keep in-universe pairs on candles).

---

## 🟢 SESSION 43 2026-07-07 — Noise-aware exits + cohort gate ACTIVE (owner-approved), ops runtime tunables

**Owner sign-off in-session:** "approved everything, activate everything while
shipping itself, no manual env changes" — the four fixes from the 7-day signal
study ship ACTIVE with every knob runtime-controlled from the ops panel.

### The study that drove this (200 shorts CSV + 300 tracked signals vs real 1m klines)

- **52% of SL hits crossed back through entry within 1h** of stopping out (75%
  within 3h); avg post-SL favourable move 1.80% vs 1.00% median stop → stops sat
  inside hourly noise. 62% of SLs hit within 30min of creation.
- **84% of BREAKEVEN_EXIT scratches reached ≥1% profit within 3h** — flat 1% BE
  arm + exact-entry park scratched winners systematically (38 scratches/wk).
- **Score-band inversion:** conf 75+ ran −0.107%/trade vs +0.088% for 65–70.
  Cause: mover paths stamp `htf_trend_aligned=True` + surge-volume scoring →
  near-max scores by construction. MVRTP: 74 signals, conf 76.2, −19.9% total.
- **"UNKNOWN" regime = empty market_phase** (regime_context None at scan; fresh
  listings). That cohort was **+26.3% vs −26.1%** for stamped signals.
- LONGs −18.1% vs SHORTs +18.4% on the window.

### Shipped (branch `claude/signal-analysis-lag-ej2pyr`)

1. **Runtime tunables control plane** — `src/runtime_tunables.py`, Firestore doc
   `control/runtime_tunables`, 5s-cached reads, env boot defaults, owner-gated
   `GET/POST /api/tunables`. Ops panel renders the registry; changing engine
   behaviour no longer requires .env edits or redeploys.
2. **Noise-floor stops (ACTIVE)** — scanner widens every stop to ≥1.0×ATR(1h)%
   (cap 3%), widen-only, TPs untouched; `signal_router` passes `risk_scale` so
   `signal_dispatch` shrinks notional by the widen factor (risk-constant).
   Stamps: `noise_floor_pct`, `noise_floor_widen_factor`, `sl_distance_pct_at_entry`.
3. **BE ratchet re-tune (ACTIVE)** — shared `src/execution/be_policy.py`; arm =
   max(flat 1%, 1R of own stop, 0.75×noise floor); armed stop parks 0.15% on the
   loss side of entry (wick-immune). Wired in BOTH trade_monitor (signal book)
   and pretp_dispatcher (real positions).
4. **Cohort-edge STEP 2 (ACTIVE)** — scanner suppresses when cohort n≥10 and
   WLB expectancy ≤ −0.05%/trade (`REASON_COHORT_EDGE` telemetry). Store now
   persists to `data/cohort_edge_store.json` so deploys don't wipe measurements.
5. **NEW_LISTING regime stamp** — regime_context None now stamps NEW_LISTING
   (thin 1h history) / UNCLASSIFIED; `_record_outcome` backfills empty phases.
   The best-performing cohort is now visible instead of "UNKNOWN".

### Verify on live data (next session)

- Suppression telemetry: `cohort_edge` rejections appearing once cohorts arm.
- NOISE_FLOOR log lines: widen factors sane (1–3×), not pinned at cap.
- BE scratch rate falling in Profit page; SL-hit shakeout share falling.
- One open question: app showed `EXPIRED held 59m` cards ~7h before the ops
  screenshot with expiry DISABLED — confirm no new EXPIRED (non-NO_FILL) at
  ≈60m post-disable; if they appear, the toggle write isn't reaching the
  monitor.

---

## 🟢 SESSION 42 2026-07-04 — Paper trades execute again + Scoring STEP 1 (PR #696)

**Owner mandate (loop continued):** profitable signals first → volume second; scoring
redesign STEP 1; SR_FLIP long re-enable pending ≥1 week shadow data.

### Critical bug fixed: paper trading never executing active signals

**Root cause:** `build_channel_signal()` in `src/channels/base.py` always populates
`entry_zone_low/high` (display band) but never set `entry_zone_filled = True`.
`entry_never_filled` returns `True` any time the zone is set but unfilled.
The auto-execute gate in `trade_monitor.py` skips execution when `entry_never_filled`.

The zone fill check in `_evaluate_signal` races with favorable price movement: once
price moves above `zone_high`, all subsequent 1m candle lows are above it →
`_c_low <= zone_high` never passes → `entry_zone_filled` stays `False` forever.
Both HMSTRUSDT (MOVER_TREND_PULLBACK LONG) and 1000BONKUSDT (DIVERGENCE_CONTINUATION
LONG) visible in the Signals tab were silently blocked for 14+ hours.

**Fix:** `sig.entry_zone_filled = True` immediately after zone computation in
`build_channel_signal()`. All evaluators pass `close=current_price` so
`zone_center ≈ close` and entry is inside the zone by construction. Evaluators
needing true limit-order semantics (entry at a future level) must reset to `False`
explicitly after calling this function.

### Wiring bug fixed: StatisticalFilter outcomes were never recorded

`TradeMonitor` was constructed without `stat_filter=` in `main.py`, so
`self._stat_filter = None` and the recording block in `_record_outcome` was
always a no-op. The rolling win-rate store was permanently empty → always
fail-open → the stat_filter had zero effect in production.

**Fix:** `main.py` now passes `stat_filter=_scanner_stat_filter` and
`cohort_edge_store=_scanner_cohort_edge_store` to `TradeMonitor.__init__()`.
Both share the same singleton instances created at scanner module load time.

### Scoring STEP 1 shipped (observe-only, ships normally per STEP 1 doctrine)

Per `docs/SCORING_AUDIT_2026_07_03.md` rollout:

1. **`CohortEdgeStore`** (`src/stat_filter.py`) — new rolling outcome store keyed
   by `(setup_class, side, regime_family, macro_dir)`:
   - `regime_family`: "QUIET" if local regime ∈ {QUIET/CHOPPY/LOW_VOL/RANGING_LOW_ADX},
     else "ACTIVE" — collapses the 5m rear-view labels into the validated binary
   - `macro_dir`: BTC weekly macro at signal emit (BULL/RECOVERY/NEUTRAL/DECLINE)
   - Expectancy formula: `WilsonLowerBound(WR) × avg_win + (1−WR) × avg_loss` —
     small samples penalised rather than trusted
   - Zero new I/O; pure in-memory dict (same pattern as `RollingWinRateStore`)

2. **`SignalOutcome` extended** with `side` and `macro_dir` fields (defaults
   `""` / `"NEUTRAL"` preserve backward compatibility with existing test callers).

3. **Signal gets cohort edge fields** (`src/channels/base.py`):
   - `cohort_edge_key`: `"SETUP/SIDE/REGIME_FAMILY/MACRO"` stamped at emit
   - `cohort_edge_expectancy`: Wilson-bounded expectancy at emit time (None = no history)
   - `cohort_edge_samples`: sample count in cohort at emit time
   Carried through lifecycle so the truth report and perf records can show the
   cohort context without additional lookups at resolution time.

4. **Scanner shadow-logs `[SHADOW] COHORT_EDGE`** after the existing
   `_stat_filter.check()` block — logs `would-emit/would-suppress:edge=X%:n=N`
   per-signal in debug. No confidence change, no suppression — telemetry only.

5. **`TradeMonitor._record_outcome`** now records outcomes to BOTH stores when a
   signal resolves (excluding `EXPIRED_NO_FILL` non-trades, per existing rule).
   The `macro_dir` at resolution is taken from the emit-time `cohort_edge_key`
   so the store records the market context at entry, not at exit.

6. **12 new `CohortEdgeStore` tests** in `tests/test_stat_filter.py`: fail-open,
   positive/negative expectancy, regime_family bucketing, shadow verdicts,
   sample count, all_stats, window caps, backward-compat defaults.

**All 6001 tests pass.** PR #696 updated to cover both commits.

### What STEP 1 enables

Starting from the next signal resolution, every outcome is recorded with the
correct cohort key. After ≥2 weeks of clean data, read the shadow verdicts
in debug logs:
```bash
docker logs 360scalp-v2-engine --since 2w 2>&1 | grep '\[SHADOW\] COHORT_EDGE'
```
Group by verdict and join against realised P&L. If the would-suppress cohorts
have negative measured expectancy → proceed to STEP 2 activation (owner sign-off).

### NEXT (standing mandate, in order)

1. **PR #696 review** — owner-sign-off item (position_state.py FSM touch). CI green.
2. **SR_FLIP long re-enable** — read `[SHADOW] SR_FLIP_LONG_V2_WOULD_FIRE` counts
   after ≥1 week (armed since Session 41). Re-enable only if V2 candidates show
   ~45%+ implied win rate. Owner sign-off required.
3. **Scoring STEP 2** — after ≥2 weeks shadow data, review COHORT_EDGE verdicts
   against realised P&L. Activate `COHORT_EDGE_RANKER_ENABLED=true` on owner
   sign-off. Owner-sign-off item (new scoring model).
4. **FSM LIMIT entry machinery** (`position_state.py` done; rest pending):
   `order_placer.py` → `place_limit_entry()` GTC LIMIT; `position_fsm.py` →
   PENDING_ENTRY→SL-first→OPEN path; `reconciler.py` → skip PENDING_ENTRY from
   market-close detection + TTL sweep. Owner sign-off (Position FSM transition).
5. **CT_SHORT gate monitoring** — daily: `grep -c "CT_SHORT_MACRO_SUPPRESS"` in logs,
   short-side P&L trend, confirm shorts return when weekly macro turns down.
6. **Expiry tune** — re-audit after ≥5 days of clean (post-phantom-fix) data.
   FAR was the premature-kill hotspot but #685 data was contaminated.
7. **MOVER_AVWAP_SCALP entry geometry** — zero real fills ever (all phantoms pre-#685).
   On clean data: widen entry zone / market-entry variant / drop.

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

### Research: regime classifier forward-validated — only QUIET is real

2,052 point-in-time checkpoints (12 symbols x 4 days, archive candles, engine's
own detector): **QUIET genuinely identifies dead markets** (half the forward
|drift|/range of every other label). But **TRENDING_DOWN's forward drift is
POSITIVE**, RANGING is statistically indistinguishable from TRENDING_UP, and
after the market-beta control NO label predicts forward direction at the 30-min
horizon (all |t| <= 1.05). The 5m regime label is a rear-view instrument; the
macro_direction classifier is the validated forward tool. Full study +
implications: `docs/REGIME_VALIDATION_2026_07_03.md`. Direct consequence for
the cohort-ranker key: regime_family collapses to {QUIET, ACTIVE}; BTC-macro
carries the directional context. Also explains the scorer's regime dimension
(8-vs-18 pts on a distinction with no forward validity). Gate-chain ordering
review (wiring pass 3): clean; one CPU-only note (cooldowns checked at enqueue,
after scoring).

### Research: LevelBook levels fail the placebo test

10 symbols x 4 days, book rebuilt point-in-time every 6h (engine's own
refresh): qualifying CLUSTERED/VP levels rejected 62.9% of touches — the SAME
level set offset +1.85% (structurally meaningless) rejected 65.4%. Price
"respects" any line at this horizon (mean-reversion base rate); the structural
selection added nothing measurable. `docs/LEVELBOOK_VALIDATION_2026_07_03.md`
(incl. the three-study pattern table: SMC half-blind, regime rear-view,
LevelBook ~placebo, while setup x side x macro cohorts separated outcomes
twice). Caveats recorded — longer-span + break-and-retest-specific re-run
before acting on structure-dependent paths.

### NEXT (the standing mandate, in order)

1. **BUILD: FSM LIMIT-at-zone + TTL entries** — owner chose "LIMIT at zone +
   TTL" (AskUserQuestion, 2026-07-03). Full implementation spec in
   `docs/FSM_LIMIT_ENTRY_DESIGN.md` (dark flag, PENDING_ENTRY state,
   SL-first fill handling, TTL sweep, reconciler awareness, shadow line,
   test matrix). Ships dark; activation = owner sign-off on shadow.
1a. **FSM LIMIT entry: shadow phase SHIPPED** — flags + zone/TTL field
   forwarding through dispatch + per-dispatch `[SHADOW] FSM_LIMIT_ENTRY`
   (in_zone / would_rest / market_semantics). Next: the PENDING_ENTRY
   machinery per the spec, then owner activation on shadow data.
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
