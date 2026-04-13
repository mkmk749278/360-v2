# PR-16 Audit Report — WHALE_MOMENTUM QUIET Regime Block

**Date:** 2026-04-13  
**Model:** Claude Sonnet 4.6 (coding agent)  
**PR branch:** `copilot/pr-16-implement-whale-momentum-quiet-block`  
**Scope:** Setup-specific QUIET regime hard-block for `WHALE_MOMENTUM` evaluator path only.

---

## Executive Summary

`WHALE_MOMENTUM` was the only volume-momentum evaluator in `ScalpChannel` that lacked a hard-block for QUIET market regime. This PR adds the smallest correct fix: an early `return None` at the top of `_evaluate_whale_momentum()` when `regime == "QUIET"` (case-insensitive). No other evaluator, threshold, or gate is changed.

---

## Pre-Existing Doctrine Context

From `docs/SIGNAL_ENGINE_AUDIT_2026-04-12.md` (PATH 4 — WHALE_MOMENTUM):

> "The path fires in ANY regime, including QUIET where whale activity is rare and more likely to be noise."  
> **Recommended action:** Consider adding QUIET regime block.

From live monitor evidence (`monitor-logs/monitor/latest.txt`):

> Repeated `QUIET_SCALP_BLOCK` events confirmed that QUIET regime suppression was already active at the scanner governance layer for scalp signals generally, but `WHALE_MOMENTUM` was not blocked at the evaluator level — relying on downstream confidence filtering, which is a weaker and less intentional gate.

---

## What Changed

### `src/channels/scalp.py` — `_evaluate_whale_momentum()`

**Added** (8 lines including comment) at the very beginning of the evaluator body:

```python
# Block in QUIET regime — whale momentum setups require directional flow and
# volume that QUIET markets structurally lack.  This is a setup-specific gate
# that mirrors the same pattern used by VOLUME_SURGE_BREAKOUT and
# BREAKDOWN_SHORT.  It does not affect any other evaluator path.
regime_upper = regime.upper() if regime else ""
if regime_upper == "QUIET":
    return None
```

**Removed** the redundant duplicate `regime_upper = regime.upper() if regime else ""` assignment that previously existed inside the OBI block (now superseded by the earlier assignment above).

**Net change:** 7 lines added, 1 line removed (net +6 lines in a 3500-line file).

---

## Pattern Alignment

The fix mirrors the identical pattern already used by:

| Evaluator | QUIET block location | Pattern |
|---|---|---|
| `_evaluate_volume_surge_breakout` | Top of function | `if regime_upper == "QUIET": return None` |
| `_evaluate_breakdown_short` | Top of function | `if regime_upper == "QUIET": return None` |
| `_evaluate_whale_momentum` | **Added by PR-16** | Same pattern |

This is deliberately family-aware and setup-specific — it does not alter any shared gate, threshold, or regime-wide policy.

---

## What Was NOT Changed

- No confidence thresholds
- No MTF gate logic
- No spread gate logic
- No QUIET_SCALP_BLOCK scanner-level governance
- No `RANGING`, `VOLATILE`, `STRONG_TREND`, or other regime behaviour
- No other evaluator paths
- No score computation
- No signal construction pipeline

---

## Tests Added

**File:** `tests/test_pr16_whale_momentum_quiet_block.py`  
**Count:** 8 focused tests across 2 test classes.

### `TestWhaleMomentumQuietBlock`

| Test | What it proves |
|---|---|
| `test_whale_momentum_blocked_in_quiet_long` | LONG candidate → `None` in `QUIET` |
| `test_whale_momentum_blocked_in_quiet_short` | SHORT candidate → `None` in `QUIET` |
| `test_whale_momentum_blocked_in_quiet_case_insensitive` | `quiet`/`Quiet`/`QUIET` all blocked |
| `test_whale_momentum_not_blocked_in_strong_trend` | QUIET guard does not fire in `STRONG_TREND` |
| `test_whale_momentum_not_blocked_in_volatile` | QUIET guard does not fire in `VOLATILE` |
| `test_whale_momentum_not_blocked_in_ranging` | QUIET guard does not fire in `RANGING` |

### `TestUnrelatedEvaluatorsUnaffected`

| Test | What it proves |
|---|---|
| `test_volume_surge_breakout_still_blocked_in_quiet` | Pre-existing block unchanged |
| `test_breakdown_short_still_blocked_in_quiet` | Pre-existing block unchanged |

---

## Regression Confirmation

All pre-existing WHALE_MOMENTUM tests pass with zero regressions:

- `tests/test_whale_momentum_tp.py` — 4/4 passed
- `tests/test_pr07_specialist_path_quality.py` — 28/28 passed

---

## Business Impact

| Before PR-16 | After PR-16 |
|---|---|
| WHALE_MOMENTUM could generate candidates in QUIET regime | WHALE_MOMENTUM hard-blocked at evaluator entry in QUIET regime |
| Downstream QUIET_SCALP_BLOCK was the only suppression layer | Block is now applied earlier, at path level, consistently with other volume-surge paths |
| Noise risk from whale-alert false positives in compressed markets | Eliminated for QUIET regime |

The change does not alter live output in non-QUIET conditions. In QUIET conditions, signals that were previously reaching the scanner governance layer before being suppressed by `QUIET_SCALP_BLOCK` will now be discarded earlier and more efficiently.

---

## Scope Confirmation

This PR does **not** include:
- PR-18, PR-19, PR-20 content
- Spread threshold changes
- MTF gate changes
- Monitor/diagnostic doc refresh
- General zero-signal suppression tuning
- Any cleanup unrelated to the WHALE_MOMENTUM QUIET block
