# Autonomous System — Full Audit & Remediation Programme

**Status:** Design of record. Diagnosis complete; remediation not yet started.
**Author:** CTE session, 2026-07-22.
**Scope:** The autonomous measurement + control stack (Layers A–G) and why the
system is net-negative despite it. This document is the single source of truth for
the fix programme that follows. It supersedes ad-hoc "tune a gate" requests — those
are treated here as symptoms, not fixes.

> **Activation status (2026-07-22, owner directive):** the owner has directed
> **"make everything live, no darks."** W1's cost model and W2's reconciliation ship
> **live by default** (`EDGE_COST_MODEL_ENABLED=true`) rather than dark-first. The
> dark-first framing below documents the original plan; the owner has explicitly
> signed off on live activation for this programme after being briefed on the risk
> that the cost constants are still unvalidated (the W2 reconciliation validates them
> in-flight). Safety limits (blast-radius, kill switch, watchdog) remain fully
> enforced.

> **One-line finding:** every "edge" number in the system is measured **gross** —
> no fees, no funding, no slippage — so the whole autonomous brain optimises a
> proxy that is not money. The gross edge we harvest (~+0.08R) is **smaller than
> the per-trade cost drag we never subtract (~0.15–0.25R)**. Positive on the
> dashboard, negative in the account.

---

## 1. Purpose & scope

The owner's question: *"We built all of this — market-context engine, per-context
edge matrix, suppression audit, shadow strategies, geometry A/B, an autonomous
self-promoting controller — and we are still in negative edge. A newbie can make
money. Why?"*

This document answers that with **code-grounded evidence**, inventories what the
autonomous system actually is (and what is genuinely good about it), enumerates
**every** gap and bottleneck, and lays out the **complete** remediation programme —
all of it, sequenced, with acceptance criteria and doctrine compliance. No options,
no "phase N later": the fixes are ordered by dependency because some literally
cannot be trusted until an earlier one lands.

---

## 2. Executive summary — the coherent narrative

The individual components are well-built. The failure is **systemic and singular**:

1. **The measurement is cost-free.** The counterfactual classifier books a win as
   the full clean R-to-TP1 and a loss as exactly −1.0R, with **zero** fees/funding/
   slippage (`src/suppression_audit.py`). The realized arm divides raw PnL% by risk%
   with no fee subtraction (`src/trade_monitor.py:610`). The edge store stores
   whatever R it is handed and merely *labels* it "net-of-fees"
   (`src/strategy_edge.py:71`) — it applies no cost adjustment.

2. **Everything downstream inherits the optimism.** The Strategy×Context edge
   matrix, the per-gate KEEP/TUNE/DROP verdicts, and the autonomous emission
   controller (`src/emission_controller.py`) all consume that gross R. The brain
   steers by an instrument that cannot see the thing sinking the account.

3. **So the system distrusts itself and stalls in the dark.** The machinery to
   *act* on edge already exists — `context_emission_policy.py` relaxes/suppresses
   the emission floor per (strategy × context) from the matrix — but it is **DARK by
   default** and has never been promoted to live, because we have never had an edge
   signal trustworthy enough to sign off on. Result: near-zero emission (≈60–70
   signals across a multi-day window over 75 pairs), and the **highest-edge strategy
   in the book is the most suppressed** (`MEAN_REVERT`: +0.39R gross, **1 emitted**).

4. **Net result:** we harvest almost none of a gross edge that is, in any case,
   smaller than the costs we don't measure. That is the definition of the owner's
   observation.

**The unlock:** put real costs into the one measurement. Every edge number becomes
honest; roughly half the "positive" cells flip negative *and that is the point* —
for the first time the brain would be steering by money. Then, and only then, do the
already-built emission policy and controller earn the right to go live.

---

## 2a. Design principle: edge decay is the adversary (2026-07-22)

Markets are **adaptive systems, not fixed ones** (unlike physics, whose laws don't
fight back). A profitable pattern, once discovered and exploited — including **by us
and our own growing flow** — changes the market and stops working. We design around
three consequences:

1. **There may be no stable edge to "find."** The realistic goal is to harvest
   *transient* edges faster than they decay and net of costs — not to discover a law.
   This reframes the business honestly: we are risk/execution managers of decaying
   edges, not oracles.
2. **We are a source of our own decay.** Emitting a working pattern to real users'
   auto-trade, at scale, erodes it. Retail crypto scalping (15s scans, 5–60 min holds)
   is the most crowded, adaptive corner of the market — MM/HFT bots are the opponents —
   so **capacity is a real limit**: a signal that works at 100 users may not survive
   10,000.
3. **Not all edges decay equally.** Pure TA patterns (EMA cross, breakout-retest)
   decay fastest — most discovered. **Structural / microstructure edges** (funding
   extremes, liquidation cascades, forced-flow reversals) decay slowest, because they
   arise from mechanics (leverage, margin calls) that being *known* can't arbitrage
   away. Weight toward the slow-decay structural edges. (Tellingly, the truth report's
   strongest cells were VOLATILE_EXPANSION/CASCADE — forced flow — not quiet-range TA.)

**Design responses (some already in place):**
- Rolling per-context edge window (already do) — decay surfaces as a cell drifting
  STRONG → FLAT → NEGATIVE.
- The realized-vs-counterfactual reconciliation (W2) **doubles as a decay detector**:
  the gap between what our counterfactual predicts and what emitted trades realise *is*
  the market adapting to our emission.
- **Add an edge-decay trajectory monitor (W8)** — measure edge *slope* per cell, not
  just level, so we de-allocate a dying edge before it crosses negative.
- **Elevate faster adaptation (W7):** if edges decay in hours, a ~90-min promotion
  latency harvests already-dead patterns. Speed of adaptation is itself an edge.

## 3. Evidence & diagnosis

### 3.1 The counterfactual R is gross (root cause)

`src/suppression_audit.py`, `candidate_outcome()` and `suppression_value_delta_r()`:

- `WOULD_WIN` → `r_multiple = +r_to_tp1` (full target), `won = True`.
- `WOULD_LOSE` → `r_multiple = −1.0` exactly (ignores stop slippage).
- `WOULD_WIN` only requires price to **touch** TP1 once inside a 60-min window using
  `max(highs)` / `min(lows)` — an intrabar touch, not a fill.
- **No fee, funding, or slippage term anywhere in the module** (grep confirms: the
  only "cost" reference is a Cost-Discipline comment about Firestore I/O).

### 3.2 The realized arm is *also* cost-blind

`src/trade_monitor.py:610` — the emitted-trade feedback that populates the matrix as
`source="emitted"`:

```
_r_multiple = signal_quality_pnl / _risk_pct        # raw PnL% ÷ risk%, no fees
won         = signal_quality_hit_tp >= 1
```

So even the "ground truth" arm is gross. And it is statistically drowned: emitted
outcomes number in the dozens against ~48k cost-free counterfactual/shadow outcomes,
so every cell's `edge_r` is effectively the gross counterfactual.

### 3.3 The edge store only relabels

`src/strategy_edge.py` — `StrategyOutcome` fields are commented `# net-of-fees`
(lines 70–72), but `record()` stores the R it is given verbatim (line 127–139). The
"net-of-fees" claim is **aspirational, not enforced.** No cost math exists in the
store.

### 3.4 Fee constants already exist — just not here

`config/__init__.py` already defines `PRE_TP_FEE_PCT_ROUND_TRIP = 0.07%`,
`PRE_TP_FEE_FLOOR_PCT = 0.20%`, and a leverage assumption — but they are consumed
**only** by the pre-TP dispatcher's banking decision. The edge/allocation brain
never imports them. The fix has a ready anchor constant to reuse and extend.

### 3.5 The emission choke is a *dark stall*, by design

`src/context_emission_policy.py` docstring: it converts the single context-blind
`min_confidence` floor into a per-(strategy × context) floor — relaxing STRONG/
POSITIVE cells, hard-suppressing NEGATIVE cells. It is gated `CONTEXT_EMISSION_
POLICY_ENABLED` (measure) → `CONTEXT_EMISSION_LIVE` (apply after sign-off). It has
never gone live. The autonomous controller (`emission_controller.py`) can only move
two knobs (`suppress_negative`, `min_samples`) on `context_floor` gates, paced at
K=3 stability × 30-min cycles, blast radius 2 — and it, too, only trusts the gross
matrix.

### 3.6 The cost-drag arithmetic (why gross-positive = net-negative)

*Estimate — to be replaced by measured values in Workstream 1.* Sample-weighted
gross edge across the five big-n strategies (truth report) ≈ **+0.08R**. A Binance
USDⓈ-M taker round-trip ≈ 0.09% (fees) + ~0.05–0.10% (slippage on a scalp) + funding
≈ **0.15–0.20% per trade**. On a typical ~1% scalp stop (1R), that is
**~0.15–0.25R of drag per trade** the measurement discards. Gross +0.08R − ~0.20R
drag ⇒ **net negative**. The tail of gross-negative strategies (§3.7) makes it
worse.

### 3.7 Truth-report state (2026-07-22 window)

- **Volume:** a trickle. Cumulative emitted ≈ 60–70 signals across 75 pairs over a
  multi-day window. Scanner generated tens of thousands of candidates.
- **We suppress our best:** `MEAN_REVERT` +0.39R gross / 66% win / n=1154 → **1
  emitted**. Liveness probes ALERTING: `mean_revert_emission` (3,253 detections, 2
  emitted, 29 cycles), `range_fade_emission` (7,347 detections, 0 emitted, 98
  cycles).
- **A third of the portfolio is gross-negative** (before costs): MOVER_AVWAP_SCALP
  −0.65R, SHADOW_FUNDING_FADE −0.43R, VOLUME_SURGE_BREAKOUT −0.33R,
  TREND_PULLBACK_EMA −0.26R, LIQUIDITY_SWEEP_REVERSAL −0.19R, RANGE_FADE −0.11R,
  SR_FLIP_RETEST −0.10R.
- **Gross-positive core worth harvesting:** MOVER_TREND_PULLBACK +0.26R (n=13k),
  MEAN_REVERT +0.39R, BREAKDOWN_SHORT +0.32R, QUIET_COMPRESSION_BREAK +0.13R,
  FUNDING_EXTREME +0.18R, SHADOW_RANGE_FADE +0.17R.
- **Suppression audit already flags value destruction:** `context_floor:MEAN_REVERT`
  DROP (−1.36R), `dispatch_staleness` DROP (−0.63R, n=1661) — but note these are
  gross verdicts and must be re-derived on net R (§6, W3).
- **Regime mismatch:** 60.5% of cycles RANGING/QUIET; the strongest cells live in
  rare VOLATILE_EXPANSION/CASCADE contexts (RANGE_FADE +4.10R n=24, QUIET_COMPRESSION
  +2.21R n=29).

---

## 4. System inventory — what exists, and what is genuinely good

| Layer | Module | Role | Verdict |
|---|---|---|---|
| A | `market_context.py` | Session/phase/volatility/rotation context key | Sound |
| B | `strategy_portfolio.py` | Strategy registry | Sound |
| C | `strategy_edge.py` | Per-(strategy×context) Wilson-bounded edge matrix | **Cost-blind** |
| C | `suppression_audit.py` | Forward-measured suppression counterfactuals + shadow ledger | **Cost-blind (root)** |
| — | `shadow_strategies.py` | Shadow-only strategy units | Sound (but gross) |
| — | `geometry_ab.py` | Fixed-% vs ATR/structure stop A/B (observe-only) | Sound (but gross) |
| — | `tuned_variants.py` | `@TUNED` shadow variants | Sound (but gross) |
| — | `context_emission_policy.py` | Per-cell emission floor from the matrix | **Built, never live** |
| G | `emission_controller.py` | Autonomous self-promoting controller | Narrow + gross-fed |
| F | ops Strategy Lab | Human read surface | Sound |

**What is genuinely good and must be preserved:**

- The **instrumentation philosophy** is institutional-grade and rare: forward-
  measured per-context edge, suppression counterfactuals, shadow strategies,
  stop-geometry A/B, fail-open telemetry, a feature-liveness watchdog that pages when
  a pipeline flat-lines. Most retail signal shops have none of this.
- The **autonomous loop is architecturally clean**: pure decision cores, unit-tested,
  bounded blast radius, self-reverting hysteresis, master kill.
- **Safety discipline** is real: naked-position invariant, blast-radius caps, secret
  handling, withdraw-key rejection.
- Several strategies carry **real gross-positive edge** worth harvesting once we can
  trust the sign of the number.

The tragedy is not bad engineering — it is **world-class engineering pointed at a
cost-free target.** The remediation keeps the instrument and fixes what it measures.

---

## 5. Complete gap register

| # | Gap | Evidence | Type | Impact |
|---|---|---|---|---|
| G1 | No cost model in edge measurement | §3.1–3.4 | **Root** | Turns net-negative into apparent-positive; corrupts every downstream decision |
| G2 | No counterfactual-vs-realized reconciliation | §3.2; no such surface exists | Root | Optimism bias is invisible and uncorrectable |
| G3 | Near-zero emission; best strategy most suppressed | §3.7 | Bottleneck | Even gross-positive edge is not harvested |
| G4 | Emission policy built but dark/never live | §3.5 | Stall | The unblock exists but is untrusted (because of G1) |
| G5 | Controller action space trivially narrow (2 knobs, context_floor only) | `emission_controller.py` | Design | Cannot touch geometry, staleness, confidence floor, strategy on/off |
| G6 | Breadth over concentration (20 strategies, ~7 gross-negative) | §3.7 | Design | Capital/attention spread across measured losers |
| G7 | Regime/universe mismatch (scan dead markets) | §3.7 | Efficiency | Compute + emission budget spent where no edge exists |
| G8 | Actuation latency (~90 min to adapt, blast radius 2) | `emission_controller.py` bounds | Design | Slower than crypto regime shifts |
| G9 | Counterfactual structurally optimistic beyond fees (TP1-touch, no partial fills, −1.0 exact loss) | §3.1 | Root-adjacent | Even net-of-fee fix must model fill realism + stop slippage |

G1 and G2 are the roots. G3–G8 either descend from them or cannot be safely resolved
until they are fixed.

---

## 6. Remediation programme (complete, sequenced)

**Doctrine for every money-path workstream below:** ship the code **default-OFF**,
run it **observe-only / shadow** on a real data window, present the shadow result,
and activate **only on owner sign-off**. All of C/edge/emission/dispatch changes are
owner-sign-off items. Off-money-path parts (telemetry, docs, ops views) ship
normally.

### W1 — Cost-aware R (the keystone) · *owner-sign-off*

**Objective:** make every R the system records **net of realistic costs**.

**Changes:**
- New `src/trade_costs.py`: a pure `net_r(...)` helper computing R after
  `taker_fee_round_trip + funding_estimate + slippage_estimate`, sourced from config
  (extend `PRE_TP_FEE_PCT_ROUND_TRIP`; add `EDGE_SLIPPAGE_PCT_PER_SIDE`,
  `EDGE_FUNDING_PCT_ESTIMATE`, all env-overridable). Slippage may be tier/liquidity
  aware via `pair_cohort`.
- `suppression_audit.candidate_outcome()` + `suppression_value_delta_r()`: subtract
  costs from both the win term and the loss term (a loss becomes worse than −1.0R by
  the round-trip cost; a win pays target − cost).
- `trade_monitor.py:610` realized path: compute `_r_multiple` from **net** PnL.
- Keep the gross number too — record **both** gross and net on each outcome so the
  reconciliation (W2) can show the gap.

**Dark-first:** `EDGE_COST_MODEL_ENABLED` (default OFF) — when OFF, behaviour is
byte-for-byte today's. Turn ON in shadow: the matrix persists a parallel net-R view
without changing any live gate.

**Acceptance:** a fresh truth-report section shows gross-R vs net-R per strategy;
unit tests assert net < gross by exactly the modelled cost on constructed cases;
mypy/ruff clean; full suite green.

### W2 — Realized-vs-counterfactual reconciliation + truth-report surface · *off-money-path telemetry*

**Objective:** measure the optimism tax and keep it measured forever.

**Changes:**
- Extend the edge store / truth report with a per-strategy table:
  **counterfactual net-R vs realized net-R vs n_emitted**, and the delta.
- Add a feature-liveness probe that pages if realized net-R diverges from
  counterfactual net-R beyond a bound on a sufficient sample (the optimism-tax
  watchdog).

**Acceptance:** truth report renders the reconciliation table; probe registered and
green; no live behaviour changed.

### W3 — Re-verdict the matrix on net R + concentration policy · *owner-sign-off*

**Objective:** decide, on **net** R, which strategies live and which die.

**Changes:**
- Re-run all KEEP/TUNE/DROP gate verdicts and STRONG/POSITIVE/NEGATIVE cell verdicts
  on net R (falls out of W1 automatically once `EDGE_COST_MODEL_ENABLED` is on).
- Introduce an explicit **strategy on/off register** driven by net edge: strategies
  that are net-negative across all contexts on adequate sample are **retired from
  emission** (kept in shadow so they can earn their way back). Candidates on today's
  data: MOVER_AVWAP_SCALP, VOLUME_SURGE_BREAKOUT, TREND_PULLBACK_EMA, SHADOW_FUNDING_
  FADE — pending net re-measurement.

**Dark-first:** the register is computed and shown in shadow first; retirement
applies live only on sign-off.

**Acceptance:** net-R verdict table reviewed; retirement list explicit and
owner-approved before any live suppression.

### W4 — Activate the emission policy (harvest the net winners) · *owner-sign-off*

**Objective:** stop suppressing net-positive strategies; emit them where they win.

**Changes:**
- With trustworthy net edge, promote `context_emission_policy` from DARK to LIVE
  (`CONTEXT_EMISSION_LIVE`) for **net-positive** cells only, staged.
- Reconsider `dispatch_staleness` and the global `min_confidence` floor **on net R**
  — note the staleness DROP verdict is a signal-time counterfactual; live entries
  fill at the stale price, so its net re-measurement must use **entry-at-dispatch**,
  not entry-at-signal (do not simply drop it on the gross number).

**Dark-first:** staged per-strategy activation, each with its own shadow window and
sign-off; kill switch (`emission_controller_enabled` / `CONTEXT_EMISSION_LIVE`)
retained.

**Acceptance:** emission volume rises **on net-positive strategies specifically**;
realized net-R stays positive on a real window post-activation.

### W5 — Broaden the controller's action space · *owner-sign-off*

**Objective:** let the autonomous loop act on more than two knobs, safely.

**Changes:** extend `emission_controller.py`'s bounded action space to include
(each hard-clamped, each promoted only on stable net-R evidence): strategy
retirement/reinstatement (W3 register), stop-geometry selection (feed from
`geometry_ab.py` once it is net-R), and the confidence-floor relaxation the emission
policy already models. Keep the pure-core + envelope + blast-radius design.

**Acceptance:** new actions unit-tested in the pure core; each gated by boot-grace,
K-stability, EV bar, and blast radius; shadow-stamped before any live promotion.

### W6 — Regime/universe focus · *owner-sign-off (scanner scope)*

**Objective:** spend the scan + emission budget where net edge lives.

**Changes:** weight the pair universe / scan cadence toward contexts and pairs with
measured net-positive cells; deprioritise RANGING/QUIET dead zones where net edge is
absent. Measured, reversible, dark-first.

**Acceptance:** scan/emission distribution shifts toward net-positive contexts
without raising cloud cost (Cost Discipline check on any new per-scan read).

### W7 — Actuation-latency tuning · *owner-sign-off*

**Objective:** adapt closer to regime speed without oscillation.

**Changes:** revisit `stability_cycles`, cycle interval, and blast radius once net-R
evidence is trustworthy — faster promotion is only safe when the signal is honest.
Retain hysteresis and self-revert.

**Acceptance:** promotion latency reduced with no measured oscillation in shadow.

---

### W8 — Edge-decay trajectory monitor · *owner-sign-off (measurement first)*

**Objective:** detect a decaying edge *before* the rolling average crosses negative —
the direct operational response to §2a.

**Changes:** per (strategy × context) cell, retain timestamped edge_r buckets and
compute a trend/slope. Surface a `decaying` flag + the slope in the truth report and
the ops Strategy Lab. Feed it to the controller as an early de-allocation signal (a
fast-negative slope tightens/suppresses *ahead of* the level crossing), inside the
existing bounded envelope. Prefer this signal for the fastest-decaying (pure-TA)
strategies; structural strategies (funding / cascade / forced-flow) tolerate a slower
trigger.

**Dark/observe-first then live:** the slope is measured and shown first; it drives
actuation only after the net-R window validates that the trajectory signal is real and
not noise. Ships within the controller's blast-radius + kill-switch envelope.

**Acceptance:** truth report renders per-cell edge trajectory + a `decaying` flag; no
actuation until validated on net data.

## 7. Sequencing & dependencies

```
W1 (cost-aware R) ──┬── W2 (reconciliation surface)
                    ├── W3 (net re-verdict + concentration)
                    │      └── W4 (activate emission policy)
                    │             └── W5 (broaden controller)
                    │                    ├── W6 (regime/universe focus)
                    │                    └── W7 (latency tuning)
```

**W1 is the hard prerequisite for everything.** W3–W7 all consume net R; running
them on gross R would just automate the current mistake faster. W2 is parallel to W3
and should land alongside W1 so the optimism tax is visible from the first shadow
window.

---

## 8. Risk register & rollback

| Risk | Mitigation |
|---|---|
| Cost model wrong-way / mis-parameterised | Model is config-driven + shadow-measured; W2 reconciliation validates it against realized fills before any live use |
| Retiring a strategy that was actually net-positive | Retirement needs adequate sample + sign-off; retired strategies stay in shadow and can be reinstated |
| Activating emission raises live risk | Staged per-strategy, each with its own shadow window; blast-radius caps + kill switch unchanged |
| Dropping `dispatch_staleness` on the wrong basis | Explicitly re-measured with entry-at-dispatch, not entry-at-signal (W4) |
| Any new per-scan/tick read for cost/funding | Cost Discipline: cache + invalidation-gate; funding is a slow value, cache it |
| Regression in gross-mode behaviour | Every flag defaults OFF; OFF == today byte-for-byte; CI asserts it |

**Rollback:** every workstream is a default-OFF flag or a runtime tunable. Instant
revert to current behaviour at any step.

---

## 9. Definition of done

The programme is done when:

1. **Every recorded R is net of costs** (W1) and the truth report shows gross vs net.
2. **Realized net-R is continuously reconciled** against counterfactual net-R, with a
   watchdog on divergence (W2).
3. **Only net-positive strategies emit**, and they emit freely where they win (W3+W4).
4. **The autonomous controller acts on net R across a broadened, bounded action
   space** (W5), focused on the contexts/pairs where net edge exists (W6), at a
   latency matched to the market (W7).
5. **The measured system-level realized net edge is positive** on a real forward
   window — the only success metric that matters.

Until (5) holds on **net** numbers, the system is not fixed, regardless of how green
the gross dashboards look.

---

## 10. Doctrine compliance

- **Dark-flag-first:** W1, W3–W7 are money-path → default-OFF, shadow-measured,
  owner sign-off to activate. W2 is telemetry → ships normally.
- **Owner-sign-off items touched:** scoring model (edge R), evaluator emission paths,
  dispatch (staleness/floor), paid-channel routing (which signals emit). None
  auto-merge.
- **Cost Discipline:** any funding/slippage lookup added on a hot path must be cached
  and invalidation-gated; funding is slow-moving and cacheable.
- **No scaffolds:** each workstream ships wired end-to-end — measurement, consumption,
  and the truth-report surface together. Net R is not "stored but unconsumed"; W3+
  consume it in the same programme.
- **Change management:** each workstream is its own topic branch + PR with a shadow
  window in the body; `subscribe_pr_activity` on open.

---

## Appendix A — Key code references

- Cost-free counterfactual: `src/suppression_audit.py` — `candidate_outcome()`,
  `suppression_value_delta_r()`, `classify_suppressed_record()`.
- Cost-blind realized R: `src/trade_monitor.py:610`.
- Relabel-only edge store: `src/strategy_edge.py:70-72,120-141,150-168`.
- Existing (unused-here) fee constants: `config/__init__.py` —
  `PRE_TP_FEE_PCT_ROUND_TRIP`, `PRE_TP_FEE_FLOOR_PCT`.
- Built-but-dark emission policy: `src/context_emission_policy.py` (docstring §26-29).
- Narrow autonomous controller: `src/emission_controller.py` — `run_cycle()`,
  `ControllerBounds`.
- Controller integration + liveness: `src/main.py:1863` (`_emission_controller_cycle`),
  `src/main.py:2037` (probe).

## Appendix B — Truth-report figures cited (2026-07-22 window)

Edge (gross R, all-source): MOVER_TREND_PULLBACK +0.26 (n=13038), FAILED_AUCTION_
RECLAIM +0.09 (8724), SR_FLIP_RETEST −0.10 (8079), DIVERGENCE_CONTINUATION +0.06
(4208), QUIET_COMPRESSION_BREAK +0.13 (3438), MEAN_REVERT +0.39 (1154),
LIQUIDITY_SWEEP_REVERSAL −0.19 (1577), SHADOW_FUNDING_FADE −0.43 (1214),
VOLUME_SURGE_BREAKOUT −0.33 (660), TREND_PULLBACK_EMA −0.26 (497),
BREAKDOWN_SHORT +0.32 (237), MOVER_AVWAP_SCALP −0.65 (209). Regime split:
RANGING 32.0%, QUIET 28.5%, TRENDING_UP 17.9%, TRENDING_DOWN 17.7%, VOLATILE 3.9%.
Cost figures in §3.6 are estimates pending W1 measurement.
