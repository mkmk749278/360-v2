# OWNER_BRIEF.md Integrity Record

This file is the canonical reference for OWNER_BRIEF.md integrity checking.
Every Copilot session must check this file if OWNER_BRIEF.md appears short or corrupted.

## Current Canonical Version

| Field | Value |
|---|---|
| Canonical redesign date | 2026-04-10 |
| Line count | 509 |
| Minimum acceptable lines | 300 |
| Format | Fresh canonical owner-operating manual (8-part structure) |
| Verified by | Copilot + owner (mkmk749278) |

## Important — Redesign Note (2026-04-10)

OWNER_BRIEF.md was **intentionally redesigned** on 2026-04-10 from a rolling diary format (801 lines)
into a fresh canonical owner-operating manual (509 lines). This was a deliberate, owner-instructed
reduction — not data corruption.

The prior rolling diary content is preserved in `docs/OWNER_BRIEF_ARCHIVE.md`.

## Restoration Instructions

If OWNER_BRIEF.md is found to be under 300 lines at session start:

1. **Stop immediately** — do not proceed with the session
2. **Alert the owner** — "OWNER_BRIEF.md appears corrupted (N lines). Restoring."
3. **Fetch the canonical version** from the most recent merge commit on main branch
4. **Compare** — identify what is missing vs the 509-line canonical structure
5. **Restore** — write the restored version back to main via PR
6. **Update this file** — update the line count after restoration

## Update Instructions

After every session that deliberately updates OWNER_BRIEF.md:
1. Note the new line count of OWNER_BRIEF.md
2. Update the line count in this file via the same PR or follow-up commit
3. The minimum acceptable lines threshold is 300 — do not raise this unless the brief grows significantly

## Why This Exists

Copilot sessions receive OWNER_BRIEF.md as a chat context attachment tied to a specific commit.
If that commit is older or shorter than main, and Copilot writes back using that as its base,
lines added in later sessions may be silently lost.

This file provides a hard checkpoint: if the brief is ever shorter than the minimum threshold,
something may have gone wrong and must be verified before any work proceeds.

## Rule

> OWNER_BRIEF.md must not be accidentally truncated between sessions.
> The minimum threshold is 300 lines.
> Deliberate updates (redesigns, restructures) are permitted by explicit owner instruction.
> If the brief falls below 300 lines without a known redesign, treat it as potential corruption and verify immediately.