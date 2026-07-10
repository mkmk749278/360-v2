"""/api/signals open/closed truth (2026-07-10).

The status string alone cannot distinguish open from closed any more:

* BE-then-TP1 default — a non-mover CLOSES with final status ``TP1_HIT``
  (popped from the active book).
* Mover runner exit (#707) — a mover with status ``TP1_HIT``/``TP2_HIT`` is
  still OPEN, the ATR trail riding the final slice.

Pre-fix the API's ``status == "ACTIVE"`` open filter made an open runner
mover VANISH from the app's Open tab mid-trade, and the app showed closed
TP1 signals as "open 8h" (EIGENUSDT).  ``is_open`` — active-book membership
minus terminal statuses — is the discriminator every client uses now.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from src.api.snapshot import build_signals


def _sig(signal_id: str, status: str, **kw) -> SimpleNamespace:
    return SimpleNamespace(
        signal_id=signal_id,
        symbol=kw.get("symbol", "MVLLUSDT"),
        direction=SimpleNamespace(value="LONG"),
        entry=36.49,
        stop_loss=38.0697,
        original_sl_distance=1.0,
        tp1=37.5138,
        tp2=38.3013,
        tp3=None,
        confidence=70.5,
        quality_tier="B",
        setup_class=kw.get("setup_class", "MOVER_TREND_PULLBACK"),
        status=status,
        current_price=38.18,
        pnl_pct=4.63,
        max_favorable_excursion_pct=4.63,
        max_adverse_excursion_pct=-0.5,
        best_tp_pnl_pct=2.81,
        pre_tp_hit=False,
        pre_tp_threshold_pct=0.0,
        pre_tp_trigger_price=None,
        timestamp=kw.get("timestamp", datetime.now(timezone.utc)),
        dispatch_timestamp=None,
        terminal_outcome_timestamp=None,
        entry_regime="TRENDING_UP",
        entry_regime_15m="",
        market_phase="",
    )


def _engine(active: list, history: list) -> SimpleNamespace:
    return SimpleNamespace(
        router=SimpleNamespace(
            active_signals={s.signal_id: s for s in active}
        ),
        _signal_history=history,
    )


def test_open_runner_mover_at_tp1_stays_in_open_view():
    runner = _sig("MVRTP-1", "TP1_HIT")  # in the book, trail riding
    engine = _engine([runner], [])
    items = build_signals(engine, status="open", limit=10)
    assert [i.signal_id for i in items] == ["MVRTP-1"]
    assert items[0].is_open is True


def test_closed_tp1_signal_in_history_is_not_open():
    closed = _sig("FAR-1", "TP1_HIT", setup_class="FAILED_AUCTION_RECLAIM")
    engine = _engine([], [closed])
    open_items = build_signals(engine, status="open", limit=10)
    assert open_items == []
    closed_items = build_signals(engine, status="closed", limit=10)
    assert [i.signal_id for i in closed_items] == ["FAR-1"]
    assert closed_items[0].is_open is False


def test_terminal_status_lingering_in_book_is_closed():
    # Defensive path: TradeMonitor hasn't popped an SL_HIT yet / restart
    # restored a mid-shutdown close.
    lingering = _sig("FAR-2", "SL_HIT")
    engine = _engine([lingering], [])
    assert build_signals(engine, status="open", limit=10) == []
    closed_items = build_signals(engine, status="closed", limit=10)
    assert [i.signal_id for i in closed_items] == ["FAR-2"]
    assert closed_items[0].is_open is False


def test_all_view_stamps_is_open_per_item():
    runner = _sig("MVRTP-1", "TP1_HIT")
    active = _sig("FAR-3", "ACTIVE")
    closed = _sig("FAR-4", "TP1_HIT")
    engine = _engine([runner, active], [closed])
    items = build_signals(engine, status="all", limit=10)
    by_id = {i.signal_id: i for i in items}
    assert by_id["MVRTP-1"].is_open is True
    assert by_id["FAR-3"].is_open is True
    assert by_id["FAR-4"].is_open is False
