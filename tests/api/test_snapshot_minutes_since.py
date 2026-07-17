"""Regression tests for :func:`src.api.snapshot._minutes_since`.

Origin: 2026-05-20 prod traceback ``AttributeError: 'str' object
has no attribute 'tzinfo'`` on a snapshot endpoint when a
``Signal.timestamp`` had been serialised through JSON (likely a
Firestore round-trip) and came back as a string.

These tests pin the tolerant-input contract:

* ``datetime`` (tz-aware OR naive)  → correct minutes count
* ISO-8601 ``str`` (Z-suffix, ``+00:00``, naive)  → parsed + counted
* ``None``                          → 0 (not an error)
* Unparseable input                 → 0 (not a 5xx)

The "don't 5xx the snapshot on a malformed timestamp" rule is the
key invariant — a stale or weirdly-serialised record on one
position shouldn't blank the entire snapshot for a user.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from src.api.snapshot import _minutes_since


def _now() -> datetime:
    """Fresh per-assertion 'now'.

    Was a module-level ``_NOW`` captured at import — but pytest imports
    every test module during collection, so on a slow run (full suite
    under coverage) more than a minute elapsed between import and
    execution and the exact-equality assertions drifted by one
    (CI flake 2026-07-17: ``assert 8 == 7``).  ``_minutes_since``
    floors, so an offset computed microseconds before the call is
    always exact.
    """
    return datetime.now(timezone.utc)


def test_none_returns_zero() -> None:
    assert _minutes_since(None) == 0


def test_datetime_tz_aware_returns_correct_minutes() -> None:
    ts = _now() - timedelta(minutes=7)
    assert _minutes_since(ts) == 7


def test_datetime_naive_treated_as_utc() -> None:
    ts = (_now() - timedelta(minutes=12)).replace(tzinfo=None)
    assert _minutes_since(ts) == 12


def test_future_timestamp_clamps_to_zero() -> None:
    """A clock-skew situation (record ts is slightly in the future)
    shouldn't yield negative minutes — clamped to 0."""
    ts = _now() + timedelta(minutes=3)
    assert _minutes_since(ts) == 0


def test_iso_string_z_suffix() -> None:
    ts = (_now() - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert _minutes_since(ts) == 5


def test_iso_string_offset_suffix() -> None:
    ts = (_now() - timedelta(minutes=9)).isoformat()
    assert _minutes_since(ts) == 9


def test_iso_string_naive_treated_as_utc() -> None:
    naive = (_now() - timedelta(minutes=15)).replace(tzinfo=None)
    assert _minutes_since(naive.isoformat()) == 15


def test_unparseable_string_returns_zero_not_exception() -> None:
    """The crash-fix invariant: an unparseable string must not
    bubble up — it returns 0 so the surrounding snapshot path
    keeps serving the rest of the response."""
    assert _minutes_since("not a date") == 0
    assert _minutes_since("") == 0


def test_unexpected_type_returns_zero() -> None:
    """Defensive: an int, list, dict — whatever — returns 0 rather
    than tracebacking.  Same crash-fix invariant."""
    assert _minutes_since(12345) == 0  # type: ignore[arg-type]
    assert _minutes_since(["2026-05-20"]) == 0  # type: ignore[arg-type]
