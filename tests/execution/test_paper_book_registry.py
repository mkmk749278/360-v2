"""Unit tests for the per-user paper book registry + fan-out facade.

Validates the core logic of "isolated paper registry" without a running
engine: lazy per-user books, paper eligibility filtering, per-symbol
management (full vs entry-only), invalidation survival, aggregate status,
and per-user failure isolation.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.execution import paper_book_registry as pbr


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------


class FakeBook:
    def __init__(self, uid, pnl_path):
        self.uid = uid
        self.pnl_path = pnl_path
        self.opened: list = []
        self.partials: list = []
        self.fulls: list = []
        self.fail_open = False
        self._pnl = 0.0
        self._equity = 1000.0
        self._open = 0

    async def place_market_order(self, signal, *, quantity=None):
        if self.fail_open:
            raise RuntimeError("boom")
        self.opened.append(signal.signal_id)
        self._open += 1
        return f"o-{self.uid}"

    async def close_partial(self, signal, fraction, tp_level=0, *, current_price=None):
        self.partials.append((signal.signal_id, fraction, tp_level))
        return f"p-{self.uid}"

    async def close_full(self, signal, *, reason, current_price=None):
        self.fulls.append((signal.signal_id, reason))
        self._open = max(0, self._open - 1)
        return f"f-{self.uid}"

    async def add_dca_entry(self, signal, *, current_price=None):
        return f"d-{self.uid}"

    async def close_all_open_positions(self):
        n = self._open
        self._open = 0
        return n

    def reset_state(self):
        self._pnl = 0.0

    @property
    def simulated_pnl_total(self):
        return self._pnl

    @property
    def current_equity_usd(self):
        return self._equity

    @property
    def open_position_count(self):
        return self._open


def _signal(symbol="BTCUSDT", setup="SR_FLIP_RETEST", regime="RANGING", sid="sig-1"):
    return SimpleNamespace(
        signal_id=sid, symbol=symbol, setup_class=setup, entry_regime=regime,
        direction="LONG",
    )


class _FakeOverrides:
    def __init__(self, user_ids):
        self._ids = user_ids

    def list_user_ids_with_mode(self, modes):
        return list(self._ids)


class _FakeUsers:
    def get_by_id(self, uid):
        return SimpleNamespace(firebase_uid=f"fb-{uid}")


@pytest.fixture
def registry(tmp_path):
    return pbr.PaperBookRegistry(
        books_dir=tmp_path / "books",
        factory=lambda uid, path: FakeBook(uid, path),
    )


@pytest.fixture
def fanout(registry):
    return pbr.PaperBookFanout(
        registry,
        overrides_store=_FakeOverrides([1, 2, 3]),
        user_store=_FakeUsers(),
    )


def _patch_resolvers(monkeypatch, *, prefs: dict, mgmt: dict):
    """prefs: fb_uid -> (sym_fs, path_fs, regime_fs); mgmt: fb_uid -> mode."""
    import src.api.user_overrides as uo
    monkeypatch.setattr(
        uo, "resolve_paper_preferences_uid",
        lambda fb: prefs.get(fb, (None, None, None)),
    )
    monkeypatch.setattr(
        uo, "resolve_symbol_management_uid",
        lambda fb, sym: mgmt.get(fb, "full"),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_registry_lazy_and_isolated(registry):
    b1 = registry.get(1)
    assert registry.get(1) is b1          # same instance on re-get
    b2 = registry.get(2)
    assert b2 is not b1                    # distinct per user
    assert b1.pnl_path != b2.pnl_path      # isolated ledgers
    assert registry.get_if_exists(99) is None


# ---------------------------------------------------------------------------
# Fan-out: eligibility
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_execute_fans_out_to_eligible_only(fanout, registry, monkeypatch):
    _patch_resolvers(
        monkeypatch,
        prefs={
            "fb-1": (None, None, None),                       # all → eligible
            "fb-2": (frozenset({"ETHUSDT"}), None, None),     # symbol excludes BTC
            "fb-3": (None, frozenset({"SR_FLIP_RETEST"}), None),  # path matches
        },
        mgmt={},
    )
    res = await fanout.execute_signal(_signal())
    assert res is not None
    assert registry.get(1).opened == ["sig-1"]
    assert registry.get(3).opened == ["sig-1"]
    # User 2 was filtered out by their paper symbol preference.
    assert registry.get(2).opened == []
    assert fanout.holders_for_signal("sig-1") == {1, 3}


@pytest.mark.asyncio
async def test_execute_returns_none_when_nobody_eligible(fanout, monkeypatch):
    _patch_resolvers(
        monkeypatch,
        prefs={uid: (frozenset(), None, None) for uid in ("fb-1", "fb-2", "fb-3")},
        mgmt={},
    )
    res = await fanout.execute_signal(_signal())
    assert res is None
    assert fanout.holders_for_signal("sig-1") == set()


# ---------------------------------------------------------------------------
# Fan-out: management mode
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_entry_only_skips_partials_but_closes_on_sl(
    fanout, registry, monkeypatch
):
    _patch_resolvers(monkeypatch, prefs={}, mgmt={"fb-2": "entry"})
    await fanout.execute_signal(_signal())  # users 1,2,3 all eligible (no prefs)

    # Pre-TP / TP partial: entry-only user 2 is skipped; 1 & 3 partial.
    await fanout.close_partial(_signal(), 0.5, tp_level=0)
    assert registry.get(1).partials and registry.get(3).partials
    assert registry.get(2).partials == []

    # SL hit closes EVERYONE incl. the entry-only book (protective stop).
    await fanout.close_full(_signal(), reason="sl_hit")
    assert ("sig-1", "sl_hit") in registry.get(2).fulls
    assert ("sig-1", "sl_hit") in registry.get(1).fulls
    assert fanout.holders_for_signal("sig-1") == set()


@pytest.mark.asyncio
async def test_entry_only_survives_invalidation(fanout, registry, monkeypatch):
    _patch_resolvers(monkeypatch, prefs={}, mgmt={"fb-2": "entry"})
    await fanout.execute_signal(_signal())

    # Invalidation closes full-managed holders but the entry-only user rides on.
    await fanout.close_full(_signal(), reason="invalidated")
    assert ("sig-1", "invalidated") in registry.get(1).fulls
    assert registry.get(2).fulls == []                 # survived
    assert fanout.holders_for_signal("sig-1") == {2}   # only entry-only remains

    # A later SL still closes the survivor.
    await fanout.close_full(_signal(), reason="sl_hit")
    assert ("sig-1", "sl_hit") in registry.get(2).fulls
    assert fanout.holders_for_signal("sig-1") == set()


# ---------------------------------------------------------------------------
# Status + resilience
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_aggregate_status_sums_books(fanout, registry, monkeypatch):
    _patch_resolvers(monkeypatch, prefs={}, mgmt={})
    await fanout.execute_signal(_signal())
    registry.get(1)._pnl = 5.0
    registry.get(2)._pnl = -2.0
    registry.get(3)._pnl = 1.0
    assert fanout.simulated_pnl_total == 4.0
    assert fanout.open_position_count == 3  # one open per book


@pytest.mark.asyncio
async def test_per_user_failure_isolation(fanout, registry, monkeypatch):
    _patch_resolvers(monkeypatch, prefs={}, mgmt={})
    # Pre-create user 2's book and make its open fail.
    registry.get(2).fail_open = True
    res = await fanout.execute_signal(_signal())
    assert res is not None                       # others still opened
    assert 2 not in fanout.holders_for_signal("sig-1")
    assert {1, 3}.issubset(fanout.holders_for_signal("sig-1"))


@pytest.mark.asyncio
async def test_close_full_unknown_signal_is_noop(fanout):
    assert await fanout.close_full(_signal(sid="nope"), reason="sl_hit") is None
    assert await fanout.close_partial(_signal(sid="nope"), 0.5) is None


def test_registry_threads_sizing_and_per_user_risk_manager():
    from src.execution.paper_book_registry import PaperBookRegistry

    made = {}

    def rm_factory(uid):
        rm = object()
        made[uid] = rm
        return rm

    reg = PaperBookRegistry(
        books_dir="/tmp/pbr_test_books",
        starting_equity_usd=2500.0,
        position_size_pct=3.5,
        max_position_usd=250.0,
        risk_manager_factory=rm_factory,
    )
    b1 = reg.get(1)
    b2 = reg.get(2)
    assert b1._position_size_pct == 3.5
    assert b1._max_position_usd == 250.0
    # Each user got its OWN risk manager.
    assert b1._risk_manager is made[1]
    assert b2._risk_manager is made[2]
    assert made[1] is not made[2]
    assert b1._pnl_history_mode == "paper:1"
