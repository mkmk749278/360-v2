# Signal-Path Audit + Toggle Checklist — 2026-08-29

Deep audit of every signal-generation lane, reconciled against the **live
Control-panel state** (owner-provided PDF snapshot, 2026-08-29) and the live
production truth report (`monitor-logs/monitor/latest.txt`). Companion to the
code fixes shipped in the same PR (core-pair dead-stream reseed, disabled-
evaluator skip, coverage-probe core paging).

---

## 1. Bottom line

The engine was starved of signals by **four stacked causes**, in order of
measured impact:

| # | Cause | Status |
|---|-------|--------|
| 1 | **18 dead Tier-1 core kline streams** (incl. BTCUSDT) — no mechanism existed to re-seed a core pair after boot | **FIXED in this PR** (`_refresh_stale_core_candles` + coverage-probe paging) |
| 2 | **Mover-promotion evaluator confiscation** — promoted pairs ran only ~2.5 effective paths (`_MOVER_EVALUATORS`) | **DONE by owner** — dual universe is ON per Control panel |
| 3 | **Global same-direction throttle** — `DIRECTION_CAP_MODE=global` (cap 3) lets MVRTP monopolize all slots; router historically drops 91–97% of dequeued signals | **OPEN — toggle below** |
| 4 | **Correctly suppressed negative-edge paths** (FUNDING −0.55R, LIQ_REV −1.06R, RANGE_FADE −0.66R) | Working as designed — do NOT force these open |

MEAN_REVERT (+0.64R, 81% win, n=570 dark) is the biggest *wrongly-throttled
positive edge* — it is live-enabled but emits ~2/window because of walls #1
and #3.

---

## 2. Toggle checklist (live panel state → recommended state)

Legend: ✅ = already correct on the live panel, 🔧 = flip recommended,
👁 = review first, then decide.

### 🔧 Flip now

| Tunable | Live state | Recommended | Why |
|---|---|---|---|
| `direction_cap_mode` | `global` | **`per_path`** | The single biggest remaining emission wall. With `global`, 3 same-direction signals engine-wide lock out every other path the moment MVRTP fires. `per_path` keeps the anti-pile-on protection (3 per setup class) while letting MEAN_REVERT / LSR / BDS emit alongside movers. Read `/signals/router-drops` for one window after flipping to confirm the drop mix shifts away from `same_direction_throttle`. |

### 👁 Review, then likely flip

| Tunable | Live state | Recommended | Why |
|---|---|---|---|
| Emission controller → **enforce routability** | OFF (measure-only) | ON after one clean window | The controller measured **16 dead overrides** live — signals emitted into slots the router provably cannot route. Enforcing turns wasted emissions into deferred ones. Dark-first doctrine satisfied: measurement has been ON and is showing consistent data. |
| `refuse_stale_tf` (staleness V2 refuse) | OFF | ON **after** this PR's core reseed has run ≥24h clean | With 18 dead core streams, refusing stale 15m would have silenced most of the universe — correct to keep OFF until freshness is repaired. Once `core_reseed:*` counters show the sweep holding age near zero, flipping this stops scoring on frozen data. |

### 👁 Review only (no flip yet)

| Tunable | Live state | Note |
|---|---|---|
| Cohort-edge gate | OFF (min samples 5) | Keep OFF. The absorbing-state lesson (a path gated off can never earn samples to re-qualify) still applies. If re-enabled later, raise min samples to ≥30 and pair with a dark re-qualification lane. |
| BTC-direction penalty | OFF | Keep OFF until its shadow counters show a consistent sign. No live evidence yet that counter-BTC signals underperform after regime gating. |
| Mover paths (MVRTP / AVWAP / MEAN_REVERT / RANGE_FADE live flags) | ON | RANGE_FADE measures −0.66R — consider returning it to shadow; the others keep their current state. MVRTP:SHORT and VSB:* stay retired (measured losers, divert-to-dark). |

### ✅ Already correct — leave alone

| Tunable | Live state |
|---|---|
| Dual universe | **ON** (this was audit finding F2 — owner already fixed) |
| Per-setup TF correction | ON |
| Context emission policy + apply-live | ON |
| Staleness V2 apply-live (deprioritize) | ON |
| Emission controller (measure) | ON |
| Dark→live promotion master | ON |
| Path retirement | ON (`MOVER_TREND_PULLBACK:SHORT`, `VOLUME_SURGE_BREAKOUT:*`) |
| Kill switch / auto-trade / mode | Disengaged / enabled / PAPER — unchanged, owner's call |

**Recommended flip order** (one change per observation window, per repo
doctrine): ① `direction_cap_mode → per_path` → watch one window →
② enforce routability ON → watch → ③ `refuse_stale_tf` ON once core
freshness is proven repaired.

---

## 3. What this PR fixes in code

### F1 — Core-pair dead-stream recovery (`src/scanner/__init__.py`)

**Fault:** Nothing ever re-seeded a Tier-1 core pair after boot. The mover
sweep (`_refresh_stale_mover_candles`) covers only promoted pairs; `seed_all`
runs once at boot; the WS manager can restore a connection without
backfilling the gap. Result on the live box: 18 Tier-1 pairs — including
BTCUSDT — with frozen candles for days, every evaluator reading dead data and
the dispatch staleness gate (rightly) blocking the remainder.

**Fix:** `_refresh_stale_core_candles()` — runs every scan cycle next to the
mover sweep. Re-seeds any Tier-1 futures pair whose 1m kline age exceeds
`CORE_CANDLE_REFRESH_SEC` (default **300s** = five missed 1m closes =
unambiguous stream death, not jitter). Per-symbol attempt throttle, per-cycle
budget `CORE_CANDLE_REFRESH_MAX_PER_CYCLE` (default **4**), shortfall counted
(`core_reseed:deferred`) rather than silently dropped, fail-soft, heartbeat
beat per completed re-seed. No-op while the WS is healthy.

Counters to watch on the ops panel: `core_reseed:wanted / refreshed / deferred`.
A persistently non-zero `wanted` is a WS-layer fault being papered over — the
sweep is recovery, not a substitute for live streams.

### F1b — `candle_coverage` pages on unusable core pairs (`src/main.py`)

**Fault:** The probe *named* the 18 dead core pairs in its detail string
while asserting healthy — the pooled 70% ratio was diluted by promoted movers
whose staleness is a different, budgeted fault.

**Fix:** Core pairs now fail the probe on their own absolute rule:
`len(core_bad) > max(2, len(core_syms) // 15)` → unhealthy, regardless of the
pooled ratio. At the 75-pair Tier-1 set that pages at 6+ dead pairs; the
floor of 2 tolerates a single flapping stream. Pooled thresholds unchanged.

### F12 — Disabled evaluators skipped, not invoked (`src/channels/scalp.py`)

**Fault:** ORB (`SCALP_ORB_ENABLED=false`) and CLS
(`CLS_DISABLED_2026_05_17=true`) are dormant by doctrine, but `evaluate()`
still called both for every pair every cycle — ~59k no-op calls each per
truth-report window — just to receive a flag-check rejection.

**Fix:** `evaluate()` consults `_disabled_evaluator_rejects()` (reads the
flags at call time, so env re-enables and test patches keep working) and
records the rejection without the call. **Telemetry contract preserved
exactly**: same `attempts` / `no_signal` / `no_signal_reason` counters, same
tokens (`feature_disabled`, `cls_disabled_merged_into_lsr`) — the truth
report still distinguishes "disabled by doctrine" from "no candidates". The
in-evaluator flag checks remain as a safety net for direct calls.

---

## 4. Condensed audit findings (per lane)

### Lane A — 19 core scalp evaluators (`ScalpChannel.evaluate`)
17 live, ORB disabled pending rebuild, CLS merged into LSR. Per-evaluator
internals are mostly healthy; the funnel dies downstream: basic filters →
setup_compat regime matrix → confidence floor 65 → **router second layer**
(correlation lock, cooldowns, same-direction throttle = 91–97% of dequeue
drops historically). Fix #3 (direction cap) is the lever.

### Lane B — Aux channels
FVG / ORDERBLOCK radar-only, DIVERGENCE limited-live, CVD / VWAP / SUPERTREND
/ ICHIMOKU disabled. `orderblocks` dependency measured **100% absent** in
SMC data — any evaluator soft-scoring on it silently loses points. Order-flow
coverage capped at 40 symbols (`AGGTRADE_MAX_SYMBOLS` / `DEPTH_MAX_SYMBOLS`)
against a 75-pair Tier-1 set — delta/CVD-dependent paths are blind on the
bottom half of the universe. Not changed in this PR (REST/WS weight budget
decision — owner call).

### Lane C/D — Dark emission + promotion
Armed and correct, but starved: dark candidates require surviving the same
upstream data-freshness walls. With F1 fixed, expect dark sample rates to
rise across all paths within days — re-read the edge matrix after ~1 week
before further path decisions.

### Lane E — Price-action lane
Dark-only, functioning, low volume for the same freshness reasons.

### Mover subsystem
Ignition + retention healthy; REST reseed sweep keeping pace (8/120s budget vs
30-pair cap). With dual universe ON, dual-core/dual-volume pairs now run the
full evaluator union — the "~2.5 effective paths" constraint is materially
relaxed. Seed depth (500 bars × 6 TFs) is sufficient; `insufficient_candles`
≈ 0.1% of rejections. **Data depth was never the problem; data freshness was.**

### Edge matrix (dark, at audit time)
| Path | R avg | Win% | n | Verdict |
|---|---|---|---|---|
| MEAN_REVERT | +0.64 | 81% | 570 | Wrongly throttled — the prize unlocked by fixes #1/#3 |
| MVRTP LONG | +0.21 | 62% | 410 | Live, dominant (was the only emitter) |
| LSR | +0.11 | 58% | 890 | Modest positive, held back by router walls |
| RANGE_FADE | −0.66 | 31% | 205 | Consider re-shadowing |
| FUNDING | −0.55 | 35% | 88 | Correctly suppressed |
| LIQ_REV | −1.06 | 28% | 60 | Correctly suppressed |

*(Numbers from the truth-report snapshot at audit time; re-read after the
fixes bed in — n will grow quickly once core freshness is restored.)*

---

## 5. Verification plan after deploy

1. **Hour 1:** `core_reseed:refreshed` > 0 while any core pair is stale;
   coverage probe detail shows the unusable-core list shrinking to 0.
2. **Day 1:** `candle_coverage` green with `core_bad = 0`; truth-report
   attempts per path roughly unchanged (F12 changes CPU, not counts).
3. **After flipping `direction_cap_mode`:** router drop mix shifts away from
   `same_direction_throttle`; MEAN_REVERT / LSR emissions rise.
4. **Week 1:** re-read the dark edge matrix with the larger n before any
   further path enable/retire decisions.
