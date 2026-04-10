# OWNER_BRIEF.md Integrity Record

This file is the canonical reference for OWNER_BRIEF.md integrity checking.
Every Copilot session must check this file if OWNER_BRIEF.md appears short or corrupted.

## Current Canonical Version

| Field | Value |
|---|---|
| Canonical redesign date | 2026-04-10 |
| Line count | 739 |
| Minimum acceptable lines | 480 |
| Format | Fresh canonical owner-operating manual (8-part structure) |
| Verified by | Copilot + owner (mkmk749278) |

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
> The minimum threshold is 480 lines — approximately 65% of the current canonical length (739 lines).
> Deliberate updates (including redesigns and upgrades) are permitted by explicit owner instruction only.
> If the brief falls below 480 lines without a known redesign, treat it as corruption and restore immediately.