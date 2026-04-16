# Operating Manual

## Date: 2026-04-16

### Part I: Introduction
... (rest of the content) 

### Part II: Executive Summary / Current Business Truth
PR-1 through PR-5 are already merged and deployed, infrastructure is healthy, observability materially improved, the engine is still not validation-ready, geometry rejection on reclaim/retest families is now the likely binding bottleneck, and MTF remains relevant but is no longer the best first lever.

### Part VI: Roadmap
The authoritative ordered roadmap is now:
- PR-6: reclaim/retest geometry policy repair
- PR-7: active-path scoring ceiling correction
- PR-8: duplicate lifecycle/terminal event integrity hardening
- PR-9: continuity and operating truth sync
- PR-10: specialist pilot reassessment

PR #166 exists as the first implementation attempt for PR-6, review concluded direction is correct but scope is too broad, near_zero_sl doctrine must remain unchanged in the first pass, and the intended narrowed implementation is reclaim/retest-specific risk_distance_too_tight repair plus only strictly necessary targeted SL-cap/R:R interaction repair.

### Part VII: Current System Snapshot
Reflects PR-1 through PR-5 merged and deployed, executive review reports added to docs on 2026-04-16 via PRs #163, #164, and #165, the active main blocker is geometry rejection on reclaim/retest paths, PR #166 is in draft and revision-blocked, and a GitHub Actions/Copilot billing or spending issue blocked the follow-up revision agent run.