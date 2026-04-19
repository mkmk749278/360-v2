# ACTIVE CONTEXT

## Current Phase
The repository is in **post-correction runtime validation mode** after merged PR #193–#197. The doctrine correction chain is complete; the current task is runtime evidence review, not opening another immediate doctrine PR.

## Current Active Priority
1) Review runtime truth reports for corrected target paths (`SR_FLIP_RETEST`, `TREND_PULLBACK_EMA`)  
2) Validate emitted/win/SL/first-breach/terminal timing behavior by target path  
3) Validate geometry preserved/changed/rejected patterns and explicit reject-not-compress reason occurrences  
4) Verify family-aware setups no longer fail late on generic RR mismatch after PR #197 harmonization

## Current Known Live Issues
- Runtime evidence is still required to determine whether `SR_FLIP_RETEST` quality improved vs. emission-only change.
- Runtime evidence is still required to determine whether `TREND_PULLBACK_EMA` quality improved vs. emission-only drop.
- Runtime evidence is still required to confirm protected structural setups are being honestly rejected (not cosmetically compressed).
- Runtime evidence is still required to confirm RR harmonization removed late-stage generic RR mismatch for family-aware paths.

## Next PR Queue
- Priority 1: Runtime validation review cycle over merged PR #193–#197 outcomes  
- Priority 2: Evidence summary decision: confirm “quality improved” vs “emission shifted only” for corrected paths  
- Priority 3: Only if runtime evidence shows a dominant unresolved defect, scope a new bounded doctrine PR  
- Priority 4: Otherwise continue observability-led stabilization / monitoring

## Roadmap Truth (Current)
- PR-1: Family-aware 360_SCALP MTF gate refinement with per-family suppression telemetry — merged.
- PR-2: Post-predictive SL/TP geometry revalidation with geometry delta telemetry — merged.
- PR-3: Channel runtime-role truth made explicit and volatile pre-skip scoping refined — merged.
- PR-4: End-to-end setup-path observability across the scanner funnel and lifecycle outcomes — merged.
- PR-5: Fail-closed specialist rollout states with limited-live divergence pilot — merged.
- PR-7A: Family-aware scoring correction (regime-affinity + thesis adjustments + pre/post-penalty telemetry) — merged.
- PR-7B: Path-aware soft-penalty modulation (path-targeted only; penalties preserved) — merged.
- PR-7C: Runtime validation hardening / observability refinement — merged (PR #195).
- PR-2 doctrine correction: protected-structural reject-not-compress enforcement — merged (PR #196).
- PR-3 doctrine correction: family-aware RR harmonization with downstream enforcement — merged (PR #197).
- Current roadmap move: runtime-validation-first operation across merged doctrine stack (no immediate next doctrine PR).

## Open Risks
- Continuity drift can still mis-sequence future sessions if ACTIVE_CONTEXT is not kept aligned with merged roadmap truth.
- Opening a fresh doctrine PR without runtime evidence could reintroduce speculative correction churn.
- `SR_FLIP_RETEST` truthful structural stops can reduce cosmetic viability; lower emissions alone are not proof of failure.
- `TREND_PULLBACK_EMA` stronger finish confirmation may reduce emissions; quality and timing behavior must decide whether correction succeeded.
- Protected structural reject-not-compress behavior must stay explicit and attributable (`protected_structural_sl_cap_exceeded_reject_not_compress`).
- RR harmonization gains could be overstated unless family-aware paths are checked for residual late-stage RR mismatch at runtime.
- Healthy telemetry alone can create false confidence if emitted/win/SL/timing + geometry outcomes are not reviewed together.

ACTIVE_CONTEXT synced to post-correction runtime-validation truth as of 2026-04-19.
