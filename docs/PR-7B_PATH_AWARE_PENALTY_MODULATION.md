# PR-7B: Path-aware penalty modulation

## What changed

PR-7B introduces a narrow modulation layer for scanner soft penalties in `src/scanner/__init__.py`.

- Penalties still exist and remain active.
- Hard safety gates are unchanged.
- Threshold/tier/router doctrine is unchanged.
- Modulation is explicit and bounded through auditable mappings:
  - `_PENALTY_MODULATION_BY_SETUP`
  - `_PENALTY_MODULATION_BY_FAMILY` (fallback only)

### Targeted modulation scope

- Reclaim / retest
  - `SR_FLIP_RETEST`: VWAP `×0.60`
  - `FAILED_AUCTION_RECLAIM`: VWAP `×0.60`
- Breakout / displacement
  - `VOLUME_SURGE_BREAKOUT`: volume divergence `×0.60`
  - `POST_DISPLACEMENT_CONTINUATION`: volume divergence `×0.65`
  - `POST_DISPLACEMENT_CONTINUATION`: VWAP `×0.80`
- Trend-pullback
  - `TREND_PULLBACK_EMA`: kill zone `×0.70`
- Continuation liquidity sweep
  - `CONTINUATION_LIQUIDITY_SWEEP`: volume divergence `×0.75`

## Telemetry added

Scanner now tracks explicit modulation hits in:

- `_penalty_modulation_counters`
- log line every 100 cycles:
  - `Penalty modulation distribution (last 100 cycles): {...}`

Each key records:
- penalty gate
- channel
- setup family
- setup class/path
- source (`path` or `family`)
- scale factor

Pre/post penalty tier migration telemetry from PR-7A remains unchanged and should be read together with this PR-7B telemetry.

## Runtime validation checklist

1. Confirm modulation usage appears in logs:
   - `Penalty modulation distribution (last 100 cycles): {...}`
2. For target paths, compare:
   - `pre_penalty:tier:*` vs `post_penalty:tier:*`
3. Validate doctrine is preserved:
   - no hard-gate changes
   - no threshold or tier-boundary changes
   - no router doctrine changes
4. Confirm modulation is narrow:
   - target paths show bounded reductions
   - unrelated paths retain baseline penalty behavior
