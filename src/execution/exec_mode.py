"""Auto-trade execution mode — the one place that knows what a mode MEANS.

Modes are ``off`` / ``paper`` / ``live`` / ``both``, and ``both`` is the
reason this module exists.

``both`` was already a first-class value on the write path
(``schemas.UserAutoTradeSettingsRequest``, documented as "live orders fire
AND paper simulation runs for side-by-side comparison") and in the live
dispatcher (``signal_dispatch``, ``worker_manager`` both test
``mode in ("live", "both")``).  Everywhere else in the codebase tested
modes by **exact string equality** — ``mode == "paper"``, or membership of
a hand-written ``{"off", "paper", "live"}`` set.  Those two spellings
disagree about ``both``, and the disagreement was silent:

* every response schema rejected ``both``, so a stored ``both`` could not
  be serialised back to the app;
* both mode-command validators rejected it, one of them *after* deleting
  the command key, so the command was consumed and dropped;
* every paper surface tested ``active_mode == "paper"``, which ``both``
  fails — so under ``both`` the live orders fired and the paper book went
  silent, which is the exact opposite of what ``both`` promises.

Worse than any single site: the paper *subscription window*.  Switching a
user to ``both`` runs ``prior_mode == "paper"`` → **closes** their paper
subscription, so their paper trade history stops being readable even
though they asked for more, not less.  A string comparison quietly
deciding what a user can see about their own money.

Rule adopted here: **no call site may compare a mode to a literal.**
Ask this module a question instead.  A fifth mode then costs one edit,
and the money path cannot drift from the display path because both read
the same predicate.

``off`` is not "no mode" — it is a real value meaning explicitly
disabled, distinct from ``None`` meaning "no row / lookup failed".  The
resolver returns ``None`` on failure and every predicate here treats
``None`` as **not enabled**, which is the fail-closed direction B12
requires: a Firestore blip must never be readable as consent to trade.
"""

from __future__ import annotations

from typing import FrozenSet, Optional

#: Every accepted mode. The single source of truth for validators and for
#: the ``Literal`` types in ``src/api/schemas.py`` — when this grows, the
#: schemas must grow with it or a stored value becomes unserialisable.
VALID_MODES: FrozenSet[str] = frozenset({"off", "paper", "live", "both"})

#: Modes under which REAL Binance orders may be placed.
_LIVE_MODES: FrozenSet[str] = frozenset({"live", "both"})

#: Modes under which the SIMULATED book runs.
_PAPER_MODES: FrozenSet[str] = frozenset({"paper", "both"})


def normalise(mode: Optional[str]) -> Optional[str]:
    """Lower-case and strip *mode*; ``None``/empty/unknown → ``None``.

    Unknown strings collapse to ``None`` rather than raising or passing
    through: callers are gates, and an unrecognised mode must read as
    "not enabled" everywhere rather than as itself somewhere.
    """
    if not isinstance(mode, str):
        return None
    cleaned = mode.strip().lower()
    if not cleaned or cleaned not in VALID_MODES:
        return None
    return cleaned


def is_valid(mode: Optional[str]) -> bool:
    """True when *mode* is a recognised mode string.

    For **input validation** only. Do not use it to decide behaviour —
    ``off`` is valid and enables nothing.
    """
    return normalise(mode) is not None


def places_live_orders(mode: Optional[str]) -> bool:
    """True when this mode may place real orders on a real account.

    The money-path gate. ``None`` → False (fail closed).
    """
    return normalise(mode) in _LIVE_MODES


def runs_paper_book(mode: Optional[str]) -> bool:
    """True when this mode runs the simulated book.

    Note ``both`` satisfies BOTH this and :func:`places_live_orders` —
    that is the whole point of ``both`` and the property every
    ``== "paper"`` comparison used to break.
    """
    return normalise(mode) in _PAPER_MODES


def is_enabled(mode: Optional[str]) -> bool:
    """True when the mode does anything at all (i.e. is not off/unknown)."""
    m = normalise(mode)
    return m is not None and m != "off"


def paper_subscription_should_be_open(mode: Optional[str]) -> bool:
    """Whether the user's paper-subscription window should be OPEN in *mode*.

    Separate from :func:`runs_paper_book` despite currently agreeing with
    it, because they answer different questions and could diverge: this
    one governs what a user may **read** about their own past paper
    trades, and the answer must never narrow just because they enabled
    something additional. Keeping it named makes that intent reviewable
    rather than implied by an ``==``.
    """
    return runs_paper_book(mode)
