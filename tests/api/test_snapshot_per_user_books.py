"""Per-user-book read path in snapshot builders (2026-06-20).

Covers the PAPER_PER_USER_BOOKS=ON branch that repoints pulse / positions /
auto-mode / pnl-history reads from the shared ledger + subscription windows
to each user's own PaperBookFanout book + ``paper:<uid>`` pnl bucket.
"""
from __future__ import annotations

import importlib
from datetime import date

import pytest

import config
from src.api import snapshot
from src.auto_trade import pnl_history
from src.execution.paper_book_registry import PaperBookFanout, PaperBookRegistry


class _Router:
    def __init__(self):
        self.active_signals = {}


class _Engine:
    def __init__(self, order_manager):
        self._current_auto_mode = "paper"
        self._order_manager = order_manager
        self.router = _Router()

    def get_auto_execution_status(self):
        return {
            "mode": "paper",
            "open_positions": 0,
            "daily_pnl_usd": 0.0,
            "daily_loss_pct": 0.0,
            "daily_kill_tripped": False,
            "manual_paused": False,
            "current_equity_usd": 0.0,
        }


@pytest.fixture
def wired(tmp_path, monkeypatch):
    monkeypatch.setenv("PNL_HISTORY_PATH", str(tmp_path / "pnl_history.json"))
    importlib.reload(pnl_history)
    monkeypatch.setattr(config, "PAPER_PER_USER_BOOKS", True, raising=False)
    registry = PaperBookRegistry(books_dir=str(tmp_path / "books"))
    fanout = PaperBookFanout(registry)
    # Materialise user 7's book so the fanout can resolve it.
    registry.get(7)
    engine = _Engine(fanout)
    return engine, registry, pnl_history


async def test_pnl_history_reads_per_user_bucket(wired):
    engine, registry, ph = wired
    today = date.today()
    ph.record_close("paper:7", 12.5, when=today)
    ph.record_close("paper:9", 99.0, when=today)   # another user — must not leak

    out = await snapshot.build_pnl_history(engine, user_id=7, days=7)
    assert out["mode"] == "paper"
    assert out["items"][-1] == {"date": today.strftime("%Y-%m-%d"), "pnl_usd": 12.5}
    assert out["weekly_pnl_usd"] == 12.5          # user 9's 99.0 excluded


async def test_pnl_history_flag_off_uses_shared_ledger(wired, monkeypatch):
    engine, registry, ph = wired
    monkeypatch.setattr(config, "PAPER_PER_USER_BOOKS", False, raising=False)
    today = date.today()
    ph.record_close("paper", 4.0, when=today)      # shared bucket
    ph.record_close("paper:7", 12.5, when=today)   # per-user — ignored when OFF

    out = await snapshot.build_pnl_history(engine, user_id=7, days=7)
    # Falls through to engine-wide "paper" bucket (no windows wired → shared).
    assert out["items"][-1]["pnl_usd"] == 4.0


class _Pos:
    def __init__(self, qty, closed=0.0):
        self.quantity = qty
        self.closed_quantity = closed


async def test_auto_mode_header_reads_per_user_book(wired):
    engine, registry, ph = wired
    today = date.today()
    ph.record_close("paper:7", 8.0, when=today)
    # Two open positions in user 7's book, one fully closed (residual 0).
    registry.get(7)._positions = {
        "a": _Pos(10.0), "b": _Pos(5.0, 5.0), "c": _Pos(3.0),
    }
    status = await snapshot.build_auto_mode(
        engine, user_id=7, starting_equity_usd=1000.0,
    )
    assert status.daily_pnl_usd == 8.0
    assert status.open_positions == 2          # 'b' excluded (residual 0)


async def test_pulse_open_count_and_daily_per_user(wired):
    engine, registry, ph = wired
    today = date.today()
    ph.record_close("paper:7", -3.0, when=today)
    registry.get(7)._positions = {"a": _Pos(10.0), "b": _Pos(1.0)}
    pulse = await snapshot.build_pulse(engine, user_id=7)
    assert pulse.open_positions == 2
    assert pulse.today_pnl_usd == -3.0
