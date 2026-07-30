# Handoff → Session 94

Written 2026-07-30, end of Session 93. Read `ACTIVE_CONTEXT.md` §Session 92 and
§Session 93 first — this document does not repeat them, it carries the *open*
work and the traps.

> **Before acting on any number in here, re-derive it.** This repo has already
> paid for the opposite (`CLAUDE.md`: *"a handoff's numbers are a snapshot, not
> a finding"* — every §4 figure in the Session-86 handoff was accurate when
> written and wrong ~12h later). Rolling per-cell windows keep moving, and
> **#834 merged today changes two of the inputs below on purpose.** Commands to
> re-derive are in §5.

---

## 1. What shipped this session

**PR [#834](https://github.com/mkmk749278/360-v2/pull/834) — merged, squashed as `bfbeb9b`.** Two things:

| | |
|---|---|
| **Scan-universe admission** | `symbol_filters.crypto_perp_admission` (fail-closed on Binance `contractType`) wired into `scanner._ensure_mover_pair`; `PairManager.hold_symbol`/`release_symbol` so no prune path evicts a mover mid-promotion; `Signal.pair_admission` → `SignalRecord` → `SignalDetail`; probes `promoted_pair_integrity`, `mover_admission_metadata` |
| **Cohort gate** | `CohortEdgeStore` evidence expiry (`COHORT_EDGE_MAX_AGE_DAYS=14`), `freshness()` / `frozen_cohorts()`, missing `_stamp_suppressed` on `cohort_edge` **and** `pair_analysis:critical`, probe `cohort_edge_gate` |

Owner merged on explicit sign-off. Auto-deploy on `main` ships in ~45s, so
**both are live on the VPS as of 2026-07-30 ~10:35 UTC.**

### Two consequences to verify first thing next session

1. **`cohort_edge` should now appear in the Suppression Quality Audit** with a
   KEEP/TUNE/DROP verdict. Before #834 it was the only live gate with no row.
   If it still has no row after a fresh window, the stamp is not reaching the
   audit — that is a bug, not a quiet market.
2. **Non-mover volume should recover as locked cohorts age out** — gradually,
   over up to 14 days, not at once. 9 of 11 armed cohorts were below the
   suppression threshold with no path back; they release as their evidence
   passes 14 days old. Track delivered/day and the MOVER share (§5).

---

## 2. ITEM 1 — MEAN_REVERT (owner-directed, do this first)

### The ask

`MEAN_REVERT` detects at **4.09%** of attempts (5,215 of 127,485 — the 4th
richest supply in the engine) and delivered **zero** signals in the 28-day book.
The truth report already pages about it:

> **ALERT** `mean_revert_emission` — 2400 detections since last emission
> (emitted_total=4) — and the blocked candidates measure **+0.58R over n=3085**,
> so the gating is **COSTING us**.

### ⚠️ STOP — there is a trap here, and it is the actual first task

**The engine holds two numbers for this strategy and they disagree in sign.**
From the same truth report:

| Row | n | emit/supp/shadow | Win% | Avg R |
|---|---:|---|---:|---:|
| `MEAN_REVERT` | 3085 | **0 / 3085 / 0** | **80%** | **+0.58** |
| `SHADOW_MEAN_REVERT` | 3414 | 0 / 0 / 3414 | **40%** | **−0.01** |

And the gate audit's verdict on the shadow arm is **DROP**:
`shadow_unit:SHADOW_MEAN_REVERT` — n=82, 50% WOULD_WIN, **−0.33 EV/suppression**.

Worse, the two are *wired to different consumers*:

- `context_emission_policy._CONTROL_ARM` maps `"MEAN_REVERT" → "SHADOW_MEAN_REVERT"`,
  so the **live gate decides on −0.01R / 40% win**.
- The liveness alert quotes the **+0.58R / 80% win** row.

So the engine's own alert says "the gating is costing us" while the engine's own
gate reads a number that says the opposite. **Unlocking MEAN_REVERT today means
picking the flattering arm**, which is precisely what `CLAUDE.md` forbids
(*"where two fills are defensible, publish both — collapsing them before the gap
is known is choosing the answer, and the one you would have chosen is the
flattering one"*).

### What to establish, in order

1. **Are the two arms even measuring the same setup?** Read
   `src/channels/scalp.py::_evaluate_mean_revert` against
   `src/shadow_strategies.py`'s mean-revert unit. If the shadow unit uses a
   looser/different extension definition, it is **not** a control arm for the
   live path and `_CONTROL_ARM` is wrong — that alone would be the finding, and
   it also affects `RANGE_FADE`, which is mapped the same way.
2. **Is 80% win at +0.58R arithmetically possible for this geometry?** Mean
   reversion targets TP1 at the 20-bar mean (`Signal.mean_revert_mean`), i.e.
   close to entry, with the stop beyond the extension — a *near* TP and a *far*
   SL. That shape gives a high hit rate with a small R per win: 80% × ~0.3R −
   20% × 1R ≈ **+0.04R**, not +0.58R. Reconcile or find the defect in how
   `strategy_edge` computes `r_multiple` for `source=SUPPRESSED` rows. Check
   whether it divides by the *original* stop distance or by something the
   noise-floor widening has already changed (this connects to §4.1).
3. **Only then** decide the unlock, and find which gate is actually killing it.
   `MEAN_REVERT`'s pre-scoring rejects were
   `setup_compat:regime_STRONG_TREND=4878`, `setup_compat:regime_WEAK_TREND=4352`,
   `execution:overextended=315` — i.e. it is mostly **setup-compat by regime**,
   not the confidence floor. Layer G has already written
   `suppress_negative: false` and `min_samples: 20` for `MEAN_REVERT` /
   `MEAN_REVERT@ATR` / `MEAN_REVERT@FIXED` (see
   `monitor-logs:monitor/report/analysis/emission_controller.json`), so the
   *context* side is already relaxed. The blocker is upstream of that.

**Doctrine:** money-path, evaluator-path → owner-sign-off item, ships
dark-first. Measurement flag ON when it ships, user-visible effect default-OFF
until the owner signs the shadow window.

---

## 3. ITEM 3 — per-path verdict on the near-dead detectors (owner-directed)

Attempts → generated, from the cumulative truth-report funnel. **The question
for each is the same, and the two answers need opposite treatments: is the
threshold wrong, or does this event genuinely not occur on our universe?**

| Evaluator | attempts | generated | rate | dominant no-signal reason |
|---|---:|---:|---:|---|
| `WHALE_MOMENTUM` | 118,642 | **0** | 0.000% | `momentum_reject=91535`, `recent_ticks_insufficient=18668` |
| `LIQUIDATION_REVERSAL` | 118,634 | **1** | 0.001% | `cascade_threshold_not_met=81677` (69%) |
| `BREAKDOWN_SHORT` | 146,897 | **4** | 0.003% | `breakout_not_found=80616` |
| `MA_CROSS_TREND_SHIFT` | 127,424 | **10** | 0.008% | `no_ma_cross=90667` (71%) |
| `POST_DISPLACEMENT_CONTINUATION` | 127,118 | **42** | 0.033% | `regime_blocked=67565` (53%) |
| `VOLUME_SURGE_BREAKOUT` | 146,854 | **79** | 0.054% | `breakout_not_found=80324` |

`OPENING_RANGE_BREAKOUT` and `CONTINUATION_LIQUIDITY_SWEEP` are **0 by flag**
(`feature_disabled`, `cls_disabled_merged_into_lsr`) — deliberate, leave alone.

### Method that will not fabricate an answer

- `WHALE_MOMENTUM` at **0 of 118,642** is not a tight threshold, it is a
  detector that cannot fire. `recent_ticks_insufficient=18668` suggests it may
  be starved of *input* (tick data), not of *signal* — check that before
  touching any threshold.
- `POST_DISPLACEMENT_CONTINUATION` is a different case: 53% `regime_blocked`
  means the regime gate, not the detector, is the wall. Its matrix cell is
  **n=67, 90% win, +0.75R** — thin, but the best positive in the matrix. Worth
  the look.
- `BREAKDOWN_SHORT` matrix cell is **n=299, 59% win, +0.33R** — positive, and it
  delivered 12 signals in 28 days. So its detector *does* fire sometimes; the
  counter window and the delivered book disagree (4 vs 12), which means **the
  cumulative counters and the 28-day book cover different windows**. Do not
  quote absolute rates from the table above as current; treat the *ranking* as
  solid and re-derive rates.
- Each relaxation must ship **stamp-and-shadow first** (`CLAUDE.md § Project
  Phase`): stamp the would-be effect on every candidate without applying it, so
  we confirm it touches the right candidates before it changes live output. A
  detector loosened by guess produces a path that fires constantly and loses.

**Do not add new paths.** 19 evaluators exist; 8 aren't running.

---

## 4. Open items carried (not started)

### 4.1 `sl_distance_pct_at_entry` is unusable — highest-value fix after 1 & 3

The field ops `/track-record` divides by to produce **every R the owner reads**:

- **Missing on 152 of 378** taken rows, and the missingness is
  **outcome-correlated**: `PROFIT_LOCKED` present on 39/42 rows and absent on 3;
  `FULL_TP_HIT` present on 2/8, absent on 6. A population selected like that is
  worse than none.
- **125 of 226 present values are exactly `3.00`** — that is
  `noise_floor_max_sl_pct`, the clamp, not a measurement.
- **Disagrees with the signal's own geometry** (`original_sl_distance / entry`)
  on **218 of 226** rows; median 0.63pp, max 18.6pp.

Cause: written only inside `scanner._apply_noise_floor_stop` (~`:8204`, `:8223`),
which is fail-open — an exception leaves it unset — while
`original_sl_distance` is stamped earlier in the evaluator (`scalp.py`, ~11
sites) and is **never updated when the noise floor widens the stop**. Three
quantities named like the same thing, no two agreeing, none authoritative.

**Consequence: no R figure anywhere in this system is currently verifiable.**
Fix to one value, recorded once, at the moment the shipped stop is known, and
**refuse rather than clamp** (`CLAUDE.md`). Both this field and the noise-floor
mechanism came from Session 43 (2026-07-07) — the same session as the cohort
gate.

### 4.2 `pair_admission` has no ops surface

#834 stamps `CORE` / `MOVER_IGNITION` / `MOVER_TOP24H` / `SURGE` on every
signal and record. **Nothing renders it.** Dark work must be observable
(`CLAUDE.md`), so this is an unfinished change: needs a `/track-record` and
Strategy-Lab split by admission in `mkmk749278/360ce-ops`. That is what makes
*"is MTP bad, or is MTP-on-promoted-pairs bad?"* answerable. **No backfill** —
the promotion expires long before the signal closes; pre-#834 rows stay `""`.

### 4.3 MTP entry quality

Do **not** demote MTP — the owner ruled on this and the data agrees (removing it
takes the feed from 12.4/day to 5.0/day). The finding to act on:

- 28d: n=147, **−0.543%/trade, −79.8% total**, 23.8% win, TP1 reached **2 of 147**.
- 7d (`real_pnl_pct`, trail-aware): **−0.176%**, and the whole book **+15.4%** — improving.
- **Two thirds of the stop-out loss never went favourable at all**: 55 of 85
  stop-outs never reached +1%, contributing −138.4% of a −212.9% total. An exit
  change cannot touch those.
- A **+1.0% first target** is the only variant improving MTP on *both* windows
  (28d +31pp, 7d +20pp); every other target improves one and degrades the other
  (noise). Even at +1.0%, MTP is still −48.7% over 28d. Non-movers realised
  **+32.78%** and beat *every* fixed target — the trail is correct there.
- If it ships, ship it **forward-measured on the money-path clock**
  (`sar_live_shadow.py` is the pattern), not off the replay.

### 4.4 Smaller, still open

- **`macro_dir` was `DECLINE` on all 29 live cohorts.** A BTC macro flip resets
  every cohort to n=0 and disarms the cohort gate in one step. Probe added
  (`cohort_edge_gate`); behaviour unchanged deliberately.
- **Surge promotion is effectively dead** under `TOP50_FUTURES_ONLY`:
  `_update_volume_baseline` only considers pairs in `pair_mgr.pairs` that are
  *not* in the scan set, and that map is now pruned to exactly the scan set plus
  held movers. Left alone; deleting it is its own change.
- Carried from Session 85 and still open: `SCAN_STAGE_TIMING_ENABLED` now
  defaults `true` so real stage timings should exist for the first time (the 16s
  figure everything extrapolates from is from **2026-06-04**); no Binance weight
  gauge in any of the 24 ops route modules (`rate_limiter.update_from_header`
  parses `X-MBX-USED-WEIGHT-1M` and discards it); `src/api_limits.py` is dead
  code with the wrong constant (1200 = old *spot* limit, futures is 2400);
  `/fapi/v1/trades` declares `weight=1` at `historical_data.py:144,150` while
  fetched with `limit=1000`; three uncapped containers in `360ce-ops`.
- **Session 85's QCB premise is stale** — QCB now emits (2621 generated / 689
  gated / **14 emitted**), and Layer G persisted `min_samples: 15` for
  `QUIET_COMPRESSION_BREAK@ATR` / `@FIXED`. Those are **arm** keys; the live
  unsuffixed key carries no override. Worth confirming the relaxation reached a
  routable key (#806/#807 pattern).

---

## 5. Re-deriving the numbers

```bash
# Truth report + gate audit + edge matrix (the source for §2 and §3)
git fetch origin monitor-logs
git show origin/monitor-logs:monitor/report/truth_report.md | less
git show origin/monitor-logs:monitor/report/analysis/emission_controller.json
git show origin/monitor-logs:monitor/report/signals_last100.json

# Delivered volume per day + MOVER share — the #834 recovery check
git show origin/monitor-logs:monitor/report/signals_last100.json | python3 -c "
import json,sys,collections
rows=json.load(sys.stdin)
by=collections.Counter(); bym=collections.Counter()
for r in rows:
    d=r['timestamp'][:10] if 'timestamp' in r else ''
    by[d]+=1
    if str(r.get('setup_class','')).startswith('MOVER'): bym[d]+=1
for d in sorted(by): print(d, by[d], 'MOVER', bym[d])"
```

**The two larger exports used this session were owner uploads and are gone** —
ask for fresh ones:

- **500-signal history** (`signal_history_*.json`) — the app-feed export.
  `pnl_pct` on it **is** the realised trail-aware number (verified: identical to
  the 7-day CSV's `real_pnl_pct` on all 87 overlapping IDs; `result_pct` is
  *not* — median 0.32 divergence, max 11.38).
- **7-day profit CSV** (`signal_profit_7d_*.csv`) — carries `real_pnl_pct`,
  `mfe_pct`, `giveback_pct`, `strategy_pct` (a TP1-exit sim) and a `degraded`
  flag the JSON does not.

Exclude `INVALIDATED` / `EXPIRED` / `CANCELLED` before computing anything — they
are **not trades** (122 of 500 in the last window, 24.4%), and counting them as
losses is the #685 fabrication class.

---

## 6. Traps this session hit, so the next one doesn't

1. **Two arms for one strategy will disagree, and one of them is wired to the
   gate.** §2 is the live example. Always ask *which* number the code actually
   reads before quoting either.
2. **The volume "decline" was a step, not a trend.** 43–55/day through 07-06,
   4–15/day from 07-08. Plotting per-day is what found it; means over halves
   hid it. Do that first for any "output is down" question.
3. **A 7-day window will happily contradict a 28-day one.** The MTP "exit is the
   problem" hypothesis looked strong at n=52 (+5.11pp for a flat TP1 exit) and
   died at n=147 (two thirds of the loss never went favourable). Validate on the
   larger sample before recommending.
4. **Check the denominator before computing R.** §4.1. 40% missing with
   outcome-correlated missingness and a clamp at 3.00 would have produced a
   confident, wrong R table.
5. **`_reject()` does not stamp** — every gate calls `_stamp_suppressed`
   itself. When output drops, list the live gates and check which have **no row**
   in the Suppression Quality Audit. That is how `cohort_edge` suppressed
   unmeasured for 23 days.
