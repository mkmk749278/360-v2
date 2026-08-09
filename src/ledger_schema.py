"""Whether a stored ledger can be read by today's code — one decision, one place.

**Paid for on 2026-08-09, by me, on the same day I wrote the rule down.**
`sar_live_shadow.LEDGER_SCHEMA` went 1 → 2 to add the held-to-stop arm. The bump
was purely **additive**: no existing field changed meaning, and the constant's
own comment said so in as many words —

    2 (2026-08-09) — ... No existing field changed meaning, so nothing is
    purged and every schema-1 row keeps its full standing in the SAR verdict.

That sentence was false. `load()` compared `stored != CURRENT` and returned,
so the first flush after the deploy **overwrote 371 rows** — 4 live arms and 367
resolved ones, the entire measurement window an adoption decision reads. Nothing
crashed. The page rendered every panel correctly over zero rows, which is
indistinguishable from a quiet lane.

This is the same shape as *"flush without load is worse than neither"*, one
level up: there the window was destroyed because nothing restored it; here it is
destroyed because the restore **declined** to. And it is `LANE_PROVENANCE_FIELDS`
verbatim — a docstring asserting a property the code beneath it does not have,
where the property was checkable in one command and nobody ran it.

Five ledgers carried the identical loader (`sar_live_shadow`, `dark_emission`,
`entry_features`, `structural_snap`, `structural_veto`), so this was not one
mistake but one mistake waiting in five places for whoever bumped next.

The rule
--------
**A schema bump has two kinds and they have opposite correct behaviours.**

* **Additive** — fields appear; every existing field means what it meant. Old
  rows are still true, still comparable, and are most of the evidence. A purge
  here makes the estimate *smaller*, not cleaner, and the readers already handle
  a missing field as its own bucket (a schema-1 SAR arm has no `hold_status` and
  renders as `pre_arm`, which is exactly correct — it is owed nothing).
* **Redefining** — a field's meaning changed. Old and new rows now disagree
  about what a column *is*, so pooling them misdescribes both and the drop is
  the right call.

The declaration is per-ledger and explicit: a bump that does not say it is
additive is treated as redefining, because that is the safe direction — you lose
a window rather than silently average two populations that mean different things.

Corollary, and it is why this is a module rather than a fixed `if`: **the check
must be impossible to write as `!=` again.** `accepts()` takes the additive set
as a required argument, so a new ledger cannot get the old behaviour by
forgetting something — it has to state which prior schemas it can read, even if
the answer is "none".
"""

from __future__ import annotations

from typing import Any, FrozenSet, Optional, Tuple

#: Reasons a stored ledger was refused, named because the next move differs.
REFUSE_NEWER = "newer_schema"        # written by a newer build — never guess forward
REFUSE_REDEFINED = "redefined_schema"  # an older schema whose fields mean something else
REFUSE_UNREADABLE = "unreadable"     # no usable schema value at all


def accepts(
    stored: Any,
    current: int,
    additive_from: FrozenSet[int],
) -> Tuple[bool, Optional[str]]:
    """May today's code read a ledger stamped ``stored``?

    Returns ``(True, None)`` to load, or ``(False, reason)`` to start clean.

    ``additive_from`` is the set of **older** schemas whose rows this build can
    read unchanged. It is required rather than defaulted: a caller that has not
    thought about it must say ``frozenset()`` out loud, so "we drop everything on
    every bump" is a decision somebody made rather than one nobody noticed.

    A **newer** schema is always refused. Reading forward means guessing what a
    field the writer added is going to mean, and a wrong guess pools two
    populations silently — the failure this module exists to stop, arriving from
    the other direction. This matters on a rollback, where an old build meets a
    file a newer one wrote.
    """
    try:
        value = int(stored or 0)
    except (TypeError, ValueError):
        return False, REFUSE_UNREADABLE
    if value == int(current):
        return True, None
    if value <= 0:
        return False, REFUSE_UNREADABLE
    if value > int(current):
        return False, REFUSE_NEWER
    if value in additive_from:
        return True, None
    return False, REFUSE_REDEFINED
