# OWNER_BRIEF.md Integrity Record

This file is the canonical reference for OWNER_BRIEF.md integrity checking.
Every Copilot session must check this file if OWNER_BRIEF.md appears short or corrupted.

## Current Canonical Version

| Field | Value |
|---|---|
| Canonical baseline date | 2026-04-19 |
| Line count | 918 |
| Minimum acceptable lines | 480 |
| Format | Fresh canonical owner-operating manual (8-part structure) |
| Verified by | Copilot + owner (mkmk749278) |

## Important — Documentation Integrity Refresh Note (2026-04-15)

OWNER_BRIEF.md was updated on 2026-04-15 as a requirements-first owner/CTO roadmap refresh to make
the brief the canonical next-phase execution plan. Key updates: header canonical date set to
2026-04-15, Part II fully rewritten into executive summary + product doctrine + runtime reality +
strategic objective, Part III channel-governance truth corrected to reflect config-default-disabled
auxiliary channels, Part VI replaced with ordered PR-1..PR-5 roadmap (family-aware gating, geometry
integrity, governance cleanup, path observability, controlled expansion), explicit KPI framework,
explicit anti-patterns, and final execution-order decision rationale. No truncation — structure
remains intact and line count is 896.

## Important — Scoring Architecture Status Refresh Note (2026-04-17)

OWNER_BRIEF.md was updated on 2026-04-17 to reflect merged PR-7A and PR-7B scoring architecture
changes plus the in-flight PR-7C observability/validation hardening step. Key updates: Part VII
snapshot date refreshed, status rows added for PR-7A/PR-7B merged and PR-7C in progress/next,
current-question and direction rows updated to runtime validation focus, and a new Part VII
sequencing section clarifies what changed in PR-7A vs PR-7B, what PR-7C is for, and what operators
must validate next (WATCHLIST→B migration, modulation hit frequency, downstream outcomes, broad-drift
guard). No truncation — canonical length is now 916 lines.

## Important — Documentation Integrity Refresh Note (2026-04-14)

OWNER_BRIEF.md was updated on 2026-04-14 to reflect the completed 2026-04-14 WATCHLIST lifecycle
investigation and merged fixes (PR #144, PR #145). Key updates: header date updated to 2026-04-14,
§2.1 top priorities refreshed to WATCHLIST-fix-complete / live-verification-pending phase, §2.2
doctrine updated to reference 2026-04-14 canonical audit and corrected the stale PR-18 WATCHLIST
claim, §3.5 signal flow step 8 corrected, §3.6 confidence table note corrected, §6.3 extended with
new §6.3.1 section for PR #144 and #145, §6.5 Next Likely Action replaced (MTF refinement →
lifecycle idempotency/duplicate-post hardening, evidence-gated), Part VII snapshot fully refreshed.
No truncation — the brief grew from 875 to 901 lines.

## Important — Audit Alignment Note (2026-04-11)

OWNER_BRIEF.md was deliberately updated on 2026-04-11 to align the canonical doctrine with
`docs/SIGNAL_ENGINE_AUDIT_2026-04-11.md`. The brief now records that the engine has a strong core,
but still requires one more correction pass before trusted redeploy due to strategy-expression
integrity issues in downstream preservation, arbitration, and portfolio governance.

The 8-part structure remains intact. The major updates were in Part II (owner doctrine / deploy
judgment / portfolio doctrine), Part III (current operating-state accuracy), Part IV–VI
(architecture-reality correction, pre-redeploy roadmap, formal redeploy gate), and Part VII
(current snapshot).

## Important — Roadmap Refresh Note (2026-04-10)

OWNER_BRIEF.md was **updated** on 2026-04-10 (roadmap refresh) from its 768-line operating-contract form
into a 739-line version. This was a deliberate, owner-instructed roadmap refresh to replace the stale
Stage A–E observability-gated expansion sequence with the current business-first signal-engine path
roadmap. The PR15 / PR16 sections were reframed as "Future Enhancement" items, removing the old PR
implementation-map labeling.

The full 8-part structure is preserved. All business rules (B1–B14), hard limits, and operating-contract
sections (Parts I–V, VII–VIII) are unchanged. Only Part VI section 6.2 and the 6.3/6.4 section titles
were updated. `docs/ACTIVE_CONTEXT.md` Next PR Queue was updated to match the new roadmap sequence.

## Restoration Instructions

If OWNER_BRIEF.md is found to be under 480 lines at session start:

1. **Stop immediately** — do not proceed with the session
2. **Alert the owner** — "OWNER_BRIEF.md appears corrupted or truncated (N lines, minimum is 480). Restoring."
3. **Fetch the canonical version** from the most recent merge commit on main branch
4. **Compare** — identify what is missing vs the 8-part canonical structure
5. **Restore** — write the restored version back to main via PR
6. **Update this file** — update the line count after restoration

## Update Instructions

After every session that deliberately updates OWNER_BRIEF.md:
1. Note the new line count of OWNER_BRIEF.md
2. Update the line count field above via the same PR or follow-up commit
3. The minimum acceptable lines threshold is 480 — update this only if the brief grows or shrinks significantly by explicit owner decision

## Why This Exists

Copilot sessions receive OWNER_BRIEF.md as a chat context attachment tied to a specific commit.
If that commit is older or shorter than main, and Copilot writes back using that as its base,
lines added in later sessions may be silently lost.

This file provides a hard checkpoint: if the brief is ever shorter than the minimum threshold,
something went wrong and must be resolved before any work proceeds.

## Rule

> OWNER_BRIEF.md must not be accidentally truncated between sessions.
> The minimum threshold is 480 lines — approximately 54% of the current canonical length (896 lines).
> Deliberate updates (including redesigns and upgrades) are permitted by explicit owner instruction only.
> If the brief falls below 480 lines without a known redesign, treat it as corruption and restore immediately.
