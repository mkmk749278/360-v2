"""Paper fan-out counters + the ``paper_dispatch`` liveness predicate.

Owner, 2026-08-31: *"live and paper trading not happening at the same
time"*.  The engine supports both at once — ``signal_dispatch`` gates on
``mode in ("live","both")``, this fan-out on ``("paper","both")``, and
the app's two toggles compose to ``'both'`` — so the question is which
half stopped, and no surface could say.

``ACTIVE_CONTEXT`` records the same question on 2026-07-16, closed as
*"not resolved from here — needs the VPS reads"*.  It was unresolvable
for a structural reason: ``_eligible`` returned ``False`` with no
counter, no log and no stamp; an empty roster was equally silent; and
there was no liveness probe for this fan-out at all.  A filtered-out
roster and a quiet tape produced an identical empty book.

Pinned:

* every user × signal pair is counted, and a decline is counted UNDER
  THE NAME of the preference that declined it;
* an empty paper roster is counted apart from a skip and never pages —
  "nobody has paper on" is a legitimate state, and pooling it with
  "paper users exist and were all filtered" is the conflation that made
  this undiagnosable;
* a book that declines without raising is its own bucket — the user
  changed nothing and only the book's risk manager can release it;
* the probe violates on a sustained open-gap and names the reasons.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.execution import paper_book_registry as pbr


@pytest.fixture(autouse=True)
def _reset():
    pbr.reset_paper_totals_for_test()
    yield
    pbr.reset_paper_totals_for_test()


def _signal(symbol="BTCUSDT", setup="MOVER_TREND_PULLBACK", regime="TRENDING_UP"):
    return SimpleNamespace(
        signal_id="sig-1",
        symbol=symbol,
        setup_class=setup,
        entry_regime=regime,
    )


_UNSET = object()


def _fanout(monkeypatch, *, users, prefs, place=_UNSET):
    registry = MagicMock()
    book = MagicMock()
    book.place_market_order = AsyncMock(
        return_value="oid-1" if place is _UNSET else place
    )
    registry.get.return_value = book
    fan = pbr.PaperBookFanout(registry)
    monkeypatch.setattr(fan, "_paper_users", lambda: dict(users))
    monkeypatch.setattr(fan, "_management_mode", lambda fb, sig: "full")
    from src.api import user_overrides as _uo
    monkeypatch.setattr(
        _uo, "resolve_paper_preferences_uid", lambda fb: prefs[fb]
    )
    return fan, book


@pytest.mark.asyncio
async def test_opened_and_considered_are_counted(monkeypatch) -> None:
    fan, _ = _fanout(
        monkeypatch,
        users={1: "fb-A", 2: "fb-B"},
        prefs={"fb-A": (None, None, None), "fb-B": (None, None, None)},
    )
    await fan.place_market_order(_signal())
    t = pbr.paper_dispatch_totals()
    assert t["fanouts_total"] == 1
    assert t["fanouts_with_users_total"] == 1
    assert t["considered_total"] == 2
    assert t["opened_total"] == 2
    assert t.get("skipped_total", 0) == 0


@pytest.mark.asyncio
async def test_each_preference_is_counted_under_its_own_name(
    monkeypatch,
) -> None:
    """Three declines, three different fixes.  A single ``skipped`` total
    would say the roster was filtered and not which filter did it."""
    fan, _ = _fanout(
        monkeypatch,
        users={1: "fb-sym", 2: "fb-path", 3: "fb-regime"},
        prefs={
            "fb-sym": ({"ETHUSDT"}, None, None),
            "fb-path": (None, {"RANGE_FADE"}, None),
            "fb-regime": (None, None, {"RANGING"}),
        },
    )
    await fan.place_market_order(_signal())
    t = pbr.paper_dispatch_totals()
    assert t["skip:symbol_pref"] == 1
    assert t["skip:path_pref"] == 1
    assert t["skip:regime_pref"] == 1
    assert t["skipped_total"] == 3
    assert t.get("opened_total", 0) == 0


@pytest.mark.asyncio
async def test_empty_roster_is_not_a_skip(monkeypatch) -> None:
    """"Nobody has paper on" is a legitimate state and must never read as
    "every paper user was filtered out"."""
    fan, _ = _fanout(monkeypatch, users={}, prefs={})
    await fan.place_market_order(_signal())
    t = pbr.paper_dispatch_totals()
    assert t["fanouts_total"] == 1
    assert t.get("fanouts_with_users_total", 0) == 0
    assert t.get("skipped_total", 0) == 0
    assert t.get("considered_total", 0) == 0


@pytest.mark.asyncio
async def test_book_declining_is_its_own_bucket(monkeypatch) -> None:
    """The user's preferences admitted the signal and the book's own risk
    manager refused.  Nothing the user set caused it, so it must not be
    counted as a preference skip."""
    fan, _ = _fanout(
        monkeypatch,
        users={1: "fb-A"},
        prefs={"fb-A": (None, None, None)},
        place=None,
    )
    fan_book = fan  # noqa: F841 — readability
    await fan.place_market_order(_signal())
    t = pbr.paper_dispatch_totals()
    assert t["rejected:book_declined"] == 1
    assert t.get("skipped_total", 0) == 0


# ---------------------------------------------------------------------------
# The probe
# ---------------------------------------------------------------------------


def test_probe_baseline_then_ok_while_books_open() -> None:
    state: dict = {}
    totals = {
        "fanouts_total": 4.0, "fanouts_with_users_total": 4.0,
        "considered_total": 4.0, "opened_total": 4.0,
    }
    assert pbr.paper_dispatch_health_check(state, totals)[0]
    ok, detail = pbr.paper_dispatch_health_check(state, totals)
    assert ok
    assert "opened=4" in detail


def test_probe_violates_when_every_paper_user_is_filtered_out() -> None:
    state: dict = {}
    totals = {
        "fanouts_total": 1.0, "fanouts_with_users_total": 1.0,
        "considered_total": 1.0, "opened_total": 1.0,
    }
    pbr.paper_dispatch_health_check(state, totals)
    pbr.paper_dispatch_health_check(state, totals)
    starved = {
        "fanouts_total": 9.0, "fanouts_with_users_total": 9.0,
        "considered_total": 9.0, "opened_total": 1.0,
        "skipped_total": 8.0, "skip:symbol_pref": 8.0,
    }
    ok, detail = pbr.paper_dispatch_health_check(state, starved)
    assert ok is False
    assert "symbol_pref=8" in detail


def test_probe_never_violates_on_an_empty_roster_alone() -> None:
    """A roster nobody has opted into would otherwise page forever.  The
    count is reported in the message instead."""
    state: dict = {}
    totals = {"fanouts_total": 50.0, "fanouts_with_users_total": 0.0}
    pbr.paper_dispatch_health_check(state, totals)
    ok, detail = pbr.paper_dispatch_health_check(state, totals)
    assert ok is True
    assert "50 with no paper users" in detail
