# PR-7C: Runtime validation hardening and observability refinement

## What changed

PR-7C adds operator-facing runtime summaries in `src/scanner/__init__.py` without changing scoring or penalty doctrine.

- Added explicit PR-7C target-path scope:
  - `SR_FLIP_RETEST`
  - `FAILED_AUCTION_RECLAIM`
  - `TREND_PULLBACK_EMA`
  - `VOLUME_SURGE_BREAKOUT`
  - `POST_DISPLACEMENT_CONTINUATION`
  - `CONTINUATION_LIQUIDITY_SWEEP`
- Added rolling (100-cycle) target-path tier migration counters:
  - `pre -> post` tier transitions
  - explicit compression signal: `pre_B_or_A+_compressed`
- Added rolling (100-cycle) target-path penalty hit aggregation by gate.
- Added rolling (100-cycle) target-path funnel + lifecycle outcome summaries derived from existing low-cardinality funnel telemetry.

## New runtime log output

Every 100 cycles, scanner now emits:

- `PR-7C target-path runtime summary (last 100 cycles): tier_migration=... penalty_hits=... funnel=... outcomes=...`

This is additive to existing PR-7A and PR-7B telemetry:

- `Scoring pre/post distribution (last 100 cycles): {...}`
- `Penalty modulation distribution (last 100 cycles): {...}`
- `Path funnel (last 100 cycles): path={...} channel={...}`

## Runtime validation usage

Use the PR-7C summary to answer:

1. Which target paths had `pre` tier `B/A+` but compressed below `B` post-penalty?
2. Which target paths are receiving penalty modulation hits (by gate) most often?
3. Which target paths are most often filtered vs emitted in funnel stages?
4. Which target paths are showing downstream lifecycle outcomes (`TP1_HIT`, `TP2_HIT`, `SL_HIT`, etc.)?

## Doctrine safety

PR-7C does **not** change:

- thresholds
- score weights
- family thesis policy
- penalty scales or modulation mappings
- router doctrine
- hard/soft gate selection logic
