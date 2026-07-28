"""CI guard: runtime state under data/ must never be tracked in git.

Everything the engine writes to ``data/`` is regenerated state — dispatch
logs, invalidation records, watchdog state, the pricing-freshness snapshot.
``.gitignore`` lists them one by one, and that per-file list is exactly why
this guard exists: a *new* runtime writer gets a new filename, and nothing
forces the matching ignore line to be added with it.

``data/feature_liveness.json`` is the one that slipped through.  It landed
as the sole tracked file under data/, so every local ``pytest`` run rewrote
it and left the working tree dirty on a diff whose only real content was
``generated_at`` moving a few minutes.  The cost is not the noise itself —
it is that reviewers learn to wave through changes to the file whose entire
job is to page when a measurement flat-lines.  A tracked liveness snapshot
is a watchdog nobody reads.

Nothing needs these files in the checkout: production reads them from the
``360scalp-v2-data`` volume, the writers recreate them (``makedirs`` +
atomic replace), and ``scripts/monitor_heartbeat.py`` treats a missing
liveness file as a pre-rollout build and stays quiet.

If this test fails on your new code: add the file to ``.gitignore`` beside
the other ``data/`` entries and ``git rm --cached`` it.  If a file under
data/ is a genuine committed *input* rather than runtime output — a seed,
a fixture, a schema — add it to ``_ALLOWED`` below with a comment saying
which code reads it and why a fresh clone needs it.
"""
from __future__ import annotations

import pathlib
import subprocess

_ROOT = pathlib.Path(__file__).resolve().parent.parent

# Committed inputs under data/ that a fresh clone legitimately needs.
# Empty today — every current data/ file is regenerated at runtime.
_ALLOWED: set[str] = set()


def test_no_tracked_files_under_data() -> None:
    """No runtime state under data/ is tracked in git."""
    out = subprocess.run(
        ["git", "ls-files", "data/"],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    tracked = {line.strip() for line in out.splitlines() if line.strip()}
    offenders = sorted(tracked - _ALLOWED)

    assert not offenders, (
        "Runtime state under data/ is tracked in git: "
        f"{offenders}.\nThese are rewritten on every engine run (and by the "
        "test suite), so they dirty the working tree on timestamp-only diffs "
        "and train reviewers to ignore them.\nAdd each to .gitignore and run "
        "`git rm --cached <path>` — or, if it is a genuine committed input, "
        "add it to _ALLOWED in this file with a comment saying what reads it."
    )
