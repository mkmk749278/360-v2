# OWNER_BRIEF.md Integrity Record

This file is the canonical reference for OWNER_BRIEF.md integrity checking.
Every Copilot session must check this file if OWNER_BRIEF.md appears short or corrupted.

## Current Canonical Version

| Field | Value |
|---|---|
| Commit SHA | efad0286557e342194453606b2bd94a073b1ff43 |
| Blob SHA | 60860afdef86a39c6014260429d4278806741ffd |
| Line count | 801 |
| Date verified | 2026-04-09 |
| Verified by | Copilot + owner (mkmk749278) |

## Restoration Instructions

If OWNER_BRIEF.md is found to be under 700 lines at session start:

1. **Stop immediately** — do not proceed with the session
2. **Alert the owner** — "OWNER_BRIEF.md appears corrupted (N lines). Restoring from canonical commit."
3. **Fetch the canonical version** using:
   - Repo: mkmk749278/360-v2
   - File: OWNER_BRIEF.md
   - Ref: 90d02391ecd296a476a6740ddbeff4ab9cac34da
4. **Compare** — identify what is missing vs current main
5. **Restore** — write the restored + updated version back to main via PR
6. **Update this file** — update the commit SHA, blob SHA, and line count after restoration

## Update Instructions

After every session that updates OWNER_BRIEF.md:
1. Note the new commit SHA of main after the merge
2. Note the new line count of OWNER_BRIEF.md
3. Update this file with the new values via the same PR or a follow-up commit

## Why This Exists

Copilot sessions receive OWNER_BRIEF.md as a chat context attachment tied to a specific commit.
If that commit is older or shorter than main, and Copilot writes back using that as its base,
lines added in later sessions are silently lost.

This file provides a hard checkpoint: if the brief is ever shorter than the canonical line count,
something went wrong and must be fixed before any work proceeds.

## Rule

> OWNER_BRIEF.md must NEVER get shorter between sessions.
> Every session appends. Nothing is ever removed except by explicit owner instruction.
> If it shrinks, treat it as data corruption and restore immediately.