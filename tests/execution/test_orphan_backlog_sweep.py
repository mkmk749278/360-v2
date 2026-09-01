"""The orphans that were ALREADY resting when the terminal-close sweep shipped.

``position_fsm.cancel_protective_orders`` retires a bracket at the moment a
position goes terminal, so no new orphan can be created.  It says nothing about
the ones already on the account: ``reconcile_user`` filters to non-terminal
positions, so a document that closed before that fix landed is never looked at
again and its orders rest forever.

The owner's account carried 24 of them on 2026-09-01 — Positions (0) beside
Open Orders → Conditional (24), the oldest 15 hours old.  Shipping the
prevention without the cleanup leaves exactly that screen, which is why this is
part of the same repair rather than a follow-up.

The sweep is EVIDENCE-BASED and that is its whole safety argument: an id is
cancelled only when it appears BOTH on one of our own closed position documents
AND in Binance's list of open algo orders for that symbol.  So it can never
reach an order we did not place, never act on a stale id, and never touch
anything protecting a live position.

Pinned here:

* a closed position's resting orders are cancelled, and the id is zeroed on the
  document so the sweep converges to nothing;
* an id Binance does NOT report as open is never cancelled — it is cleared;
* a FAILED fetch is not an empty answer.  "Binance confirmed nothing is open"
  and "we could not ask" have opposite consequences here, and conflating them
  would silently declare the backlog clean;
* the per-cycle cancel cap drains rather than drops — this account has been
  IP-banned for hammering before;
* a clean account pays one bounded read and then nothing, forever;
* a live (non-terminal) position is never touched.
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.execution import position_state
from src.execution import reconciler as reconciler_mod

NOW = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


def _closed(signal_id: str, symbol: str = "BTCUSDT", **ids):
    base = dict(
        signal_id=signal_id, firebase_uid="fb-o", symbol=symbol, side="LONG",
        state=position_state.PositionState.CLOSED,
        entry_price_target=29000.0, entry_price_filled=29000.0,
        sl_price=28500.0, tp1_price=29500.0, tp2_price=30000.0,
        tp3_price=30500.0, total_qty=1.0, tp1_qty=0.3, tp2_qty=0.4,
        tp3_qty=0.3, closed_at=NOW, close_reason="SL",
    )
    base.update(ids)
    return position_state.Position(**base)


@pytest.fixture
def store(monkeypatch):
    docs: dict = {}
    monkeypatch.setattr(
        position_state, "put_position",
        lambda p: docs.__setitem__((p.firebase_uid, p.signal_id), p),
    )
    monkeypatch.setattr(
        position_state, "get_position", lambda uid, sid: docs[(uid, sid)],
    )
    return docs


def _reconciler(*, closed=(), open_ids=None, placer=None, store=None):
    """A reconciler with the history read and the exchange stubbed.

    ``open_ids`` is what Binance answers for algoOpenOrders: a set, or None to
    mean the fetch failed.
    """
    placer = placer or MagicMock(cancel_algo_order=AsyncMock(return_value=None))
    r = reconciler_mod.Reconciler(
        signing_client_factory=lambda: MagicMock(),
        order_placer_factory=lambda uid: placer,
        positions_for_user=lambda uid: [],
    )
    for p in closed:
        if store is not None:
            store[(p.firebase_uid, p.signal_id)] = p

    async def _fetch(uid, client, symbol):  # noqa: ARG001
        return open_ids

    r._fetch_open_algo_ids = _fetch  # type: ignore[assignment]
    return r, placer


@pytest.fixture(autouse=True)
def _patch_history(monkeypatch):
    """Stub the bounded closed-history query at its module seam."""
    holder: dict = {"rows": []}
    monkeypatch.setattr(
        position_state, "list_recent_closed_positions_for_user",
        lambda uid, limit=50: list(holder["rows"]),
    )
    return holder


@pytest.mark.asyncio
async def test_a_resting_orphan_is_cancelled_and_the_id_cleared(
    store, _patch_history
):
    pos = _closed("sig-1", tp1_order_id=3001, tp2_order_id=3002)
    _patch_history["rows"] = [pos]
    r, placer = _reconciler(closed=[pos], open_ids={3001, 3002}, store=store)

    await r._sweep_orphan_backlog("fb-o")

    cancelled = {c.kwargs["algo_id"] for c in placer.cancel_algo_order.call_args_list}
    assert cancelled == {3001, 3002}
    assert r.orphan_counts["cancelled"] == 2
    # Zeroed on the document, so the next process finds no suspect at all.
    stored = store[("fb-o", "sig-1")]
    assert stored.tp1_order_id == 0
    assert stored.tp2_order_id == 0


@pytest.mark.asyncio
async def test_an_id_binance_does_not_report_open_is_never_cancelled(
    store, _patch_history
):
    """Filled, already cancelled, or expired.  Cancelling it would spend a
    round trip to be told -2011, and the point of the intersect is that we act
    only on what the exchange confirms is there."""
    pos = _closed("sig-1", tp1_order_id=3001)
    _patch_history["rows"] = [pos]
    r, placer = _reconciler(closed=[pos], open_ids=set(), store=store)

    await r._sweep_orphan_backlog("fb-o")

    placer.cancel_algo_order.assert_not_awaited()
    assert r.orphan_counts["already_gone"] == 1
    assert r.orphan_counts["cancelled"] == 0
    # Still cleared, so it stops being a suspect.
    assert store[("fb-o", "sig-1")].tp1_order_id == 0


@pytest.mark.asyncio
async def test_a_failed_fetch_is_not_an_empty_answer(store, _patch_history):
    """The single most dangerous confusion here.  An empty set means Binance
    confirmed nothing is open; None means we could not ask.  Treating the
    second as the first would clear every id and declare a backlog clean that
    is still sitting on the account."""
    pos = _closed("sig-1", tp1_order_id=3001)
    _patch_history["rows"] = [pos]
    r, placer = _reconciler(closed=[pos], open_ids=None, store=store)

    await r._sweep_orphan_backlog("fb-o")

    placer.cancel_algo_order.assert_not_awaited()
    assert r.orphan_counts["already_gone"] == 0
    assert store[("fb-o", "sig-1")].tp1_order_id == 3001  # untouched
    # Carried, so the next cycle retries rather than forgetting.
    assert r._orphan_pending["fb-o"]


@pytest.mark.asyncio
async def test_the_cap_drains_the_backlog_rather_than_dropping_it(
    store, _patch_history
):
    """A bound you cannot compute in advance is a blast-radius cap. The
    residue carries; it is never discarded."""
    rows = [
        _closed(f"sig-{n}", tp1_order_id=5000 + n, tp2_order_id=6000 + n,
                tp3_order_id=7000 + n, sl_order_id=8000 + n)
        for n in range(5)
    ]
    _patch_history["rows"] = rows
    every_id = {5000 + n for n in range(5)} | {6000 + n for n in range(5)} \
        | {7000 + n for n in range(5)} | {8000 + n for n in range(5)}
    r, placer = _reconciler(closed=rows, open_ids=every_id, store=store)

    await r._sweep_orphan_backlog("fb-o")

    first = placer.cancel_algo_order.await_count
    assert first == reconciler_mod._ORPHAN_SWEEP_MAX_CANCELS
    assert r._orphan_pending["fb-o"]  # the rest is carried

    await r._sweep_orphan_backlog("fb-o")
    assert placer.cancel_algo_order.await_count > first


@pytest.mark.asyncio
async def test_a_clean_account_pays_one_read_and_then_nothing(
    store, _patch_history
):
    """The convergence property.  Every id already zero → no suspect, no
    exchange call, and the user is never read again this process."""
    _patch_history["rows"] = [_closed("sig-1")]
    r, placer = _reconciler(closed=[], open_ids=set(), store=store)

    await r._sweep_orphan_backlog("fb-o")
    await r._sweep_orphan_backlog("fb-o")
    await r._sweep_orphan_backlog("fb-o")

    placer.cancel_algo_order.assert_not_awaited()
    assert r.orphan_counts["history_reads"] == 1
    assert r.orphan_counts["suspects_found"] == 0


@pytest.mark.asyncio
async def test_a_failed_history_read_is_retried_not_marked_done(
    store, monkeypatch
):
    """"Swept" and "could not read" must not become the same state."""
    def _boom(uid, limit=50):
        raise RuntimeError("firestore down")

    monkeypatch.setattr(
        position_state, "list_recent_closed_positions_for_user", _boom
    )
    r, _placer = _reconciler(open_ids=set(), store=store)

    await r._sweep_orphan_backlog("fb-o")

    assert "fb-o" not in r._orphan_history_read  # will retry next cycle


@pytest.mark.asyncio
async def test_the_sweep_never_raises_into_reconciliation(store, monkeypatch):
    """Cleanup runs beside real reconciliation. A failure to tidy must never
    stop a naked position being healed."""
    monkeypatch.setattr(
        position_state, "list_recent_closed_positions_for_user",
        lambda uid, limit=50: (_ for _ in ()).throw(ValueError("boom")),
    )
    r, _ = _reconciler(open_ids=set(), store=store)
    await r._sweep_orphan_backlog("fb-o")  # no exception = pass
