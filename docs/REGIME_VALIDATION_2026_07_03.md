# Regime Classifier Forward-Validation (S41 research)

*Question: does the 5m regime label predict what happens NEXT — the thing
every gate, affinity score, and exit branch assumes — or does it only
describe what already happened?*

## Method

12 liquid symbols × 4 days (2026-06-29 → 07-02), regime classified at every
30-minute checkpoint using the engine's own `detect_regime_from_arrays` on
point-in-time candles (public archive data, no look-ahead). Forward measure:
the NEXT 30 minutes' signed drift, |drift|, and realized range. 2,052
checkpoints.

## Results

| Label | n | fwd drift % | fwd \|drift\| % | fwd range % | demeaned drift % (t) |
|---|---:|---:|---:|---:|---:|
| TRENDING_UP | 647 | +0.046 | 0.466 | 0.976 | +0.013 (t 0.47) |
| TRENDING_DOWN | 585 | **+0.026** | 0.409 | 0.841 | −0.004 (t −0.13) |
| RANGING | 484 | +0.035 | 0.477 | 1.025 | +0.001 (t 0.03) |
| QUIET | 336 | +0.007 | **0.254** | **0.567** | −0.020 (t −1.05) |
| VOLATILE | <20 | — | — | — | rarely fires |

(De-meaned column removes each symbol's window drift — the market-beta
control.)

## Findings

1. **QUIET is real.** Half the forward movement and range of every other
   label. The QUIET gates (scalp block, compression logic) stand on solid
   ground.
2. **TRENDING_DOWN has zero forward validity** — raw forward drift is
   *positive*; the label describes the leg that already happened.
3. **RANGING ≈ TRENDING_UP in forward behaviour** (drift, |drift|, range all
   statistically indistinguishable) — yet the scorer awards 8 vs 18 pts on
   this distinction, compat gates branch on it, and regime-per-exit picks
   TRAIL-vs-CANCEL from it.
4. After the market-beta control, **no label carries meaningful forward
   directional information at the 30-minute horizon** (all |t| ≤ 1.05).

## Caveats

One 4-day window in one market phase (recovery); 30-min horizon (the
scalp-relevant one, but exits run longer); labels may still add value as
*setup context* (e.g. a compression break needs a compression) even where
they don't predict direction standalone. Re-run over a longer archive span
before any gate removals.

## Implications (feeds the cohort-ranker design + future gate reviews)

- **Cohort key** (`SCORING_AUDIT_2026_07_03.md` STEP 1): collapse
  `regime_family` to **{QUIET, ACTIVE}** (+VOLATILE if it ever fires) instead
  of 5 states, and use the **BTC-macro direction** — which separated outcomes
  decisively in the S40 studies — as the directional context dimension. Five
  regime states in the key would fragment samples across distinctions the
  data says don't exist.
- The **regime scoring dimension** (8-vs-18 affinity points) is spending a
  fifth of the score on a distinction with no forward validity — consistent
  with the scorer's measured inability to rank.
- **Regime-per-exit** (§3.2b TRAIL/CANCEL branching on the post-pre-TP
  regime) is built on the same label; with TP1-full now the default exit this
  is mostly dormant, but re-validate before any revival.
- The 5m label is a *rear-view* instrument. Where forward direction matters,
  the macro_direction classifier (weekly/daily slope+structure) is the
  validated tool — it called both sides of this month's bleed correctly.
