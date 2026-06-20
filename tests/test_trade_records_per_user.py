"""Per-user paper trade store isolation + aggregate readers (2026-06-20)."""
from __future__ import annotations

import importlib

import pytest

tr = importlib.import_module("src.auto_trade.trade_records")


@pytest.fixture
def books_dir(tmp_path, monkeypatch):
    d = tmp_path / "paper_books"
    d.mkdir()
    monkeypatch.setenv("PAPER_BOOKS_DIR", str(d))
    tr.reset_for_test()
    yield d
    tr.reset_for_test()


def _open_close(db_path, *, sid, symbol, net):
    tr.open_trade(
        signal_id=sid, symbol=symbol, side="LONG", entry=100.0, qty=1.0,
        leverage=10.0, position_size_pct=1.0, db_path=db_path,
    )
    tr.close_trade(
        signal_id=sid, close_reason="full_tp_hit", close_price=110.0,
        gross_pnl_usd=net, fees_usd=0.0, net_pnl_usd=net, db_path=db_path,
    )


def test_per_user_db_isolation(books_dir):
    db1 = books_dir / "paper_trades_user_1.sqlite"
    db2 = books_dir / "paper_trades_user_2.sqlite"
    # SAME signal_id can exist in two users' books (no UNIQUE collision).
    _open_close(db1, sid="sig-1", symbol="BTCUSDT", net=5.0)
    _open_close(db2, sid="sig-1", symbol="BTCUSDT", net=-3.0)

    u1 = tr.list_trades(db_path=db1)
    u2 = tr.list_trades(db_path=db2)
    assert len(u1) == 1 and len(u2) == 1
    assert u1[0]["net_pnl_usd"] == 5.0       # user 1 sees only their own
    assert u2[0]["net_pnl_usd"] == -3.0      # user 2 sees only their own


def test_aggregate_across_users(books_dir):
    db1 = books_dir / "paper_trades_user_1.sqlite"
    db2 = books_dir / "paper_trades_user_7.sqlite"
    _open_close(db1, sid="a", symbol="BTCUSDT", net=5.0)
    _open_close(db1, sid="b", symbol="ETHUSDT", net=2.0)
    _open_close(db2, sid="c", symbol="SOLUSDT", net=-1.0)

    rows = tr.list_trades_all_users(limit=50)
    assert len(rows) == 3
    # user_id is attributed from the source db filename.
    by_uid = {r["symbol"]: r["user_id"] for r in rows}
    assert by_uid["BTCUSDT"] == 1 and by_uid["SOLUSDT"] == 7
    assert tr.count_trades_all_users() == 3


def test_aggregate_empty_when_no_books(books_dir):
    assert tr.list_trades_all_users() == []
    assert tr.count_trades_all_users() == 0
    assert tr.iter_user_db_paths() == []
