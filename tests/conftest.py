"""Shared pytest fixtures for the test suite.

Per-test isolation of disk-backed registries.  Without this, tests
that exercise ``Scanner._dispatch_cooldown`` or
``ScalpChannel._ma_cross_last_fire_ts`` would share state via their
JSON files in ``data/`` — a fire in one test would block fires in
later tests.

Cooldown + staleness: disabled by default in tests (set via env var
before scanner module loads).  Tests of the cooldown / staleness
behaviour itself construct fresh state and bypass the autouse
fixture by re-enabling.
"""

from __future__ import annotations

import os

# Disable dispatch cooldown for the test suite — set BEFORE any test
# imports ``src.scanner`` so the module-level ``DISPATCH_COOLDOWN_SEC``
# is initialised to 0 from the env var.  Tests of cooldown behaviour
# manage their own state via the in-memory dict directly.
os.environ.setdefault("DISPATCH_COOLDOWN_SEC", "0")

import pytest


@pytest.fixture(autouse=True)
def _isolate_disk_backed_registries(tmp_path, monkeypatch):
    """Per-test tmp path for every disk-backed cooldown / persistence file
    in the engine.  Autouse so individual tests don't have to opt in.
    """
    # Scanner dispatch cooldown — point persistence to tmp path so
    # ``data/signal_dispatch_cooldown.json`` doesn't accumulate across
    # test runs.  Cooldown SEC is already 0 via env var (above).
    import src.scanner as _scanner_mod
    from src.scanner import Scanner

    monkeypatch.setattr(
        _scanner_mod,
        "DISPATCH_COOLDOWN_PATH",
        str(tmp_path / "signal_dispatch_cooldown.json"),
    )
    # Skip the disk read/write in tests entirely; persistence isn't
    # part of any unit-test contract here.
    monkeypatch.setattr(Scanner, "_load_dispatch_cooldown", lambda self: None)
    monkeypatch.setattr(Scanner, "_persist_dispatch_cooldown", lambda self: None)
    # Level-rearm state machine — same isolation pattern as the
    # dispatch cooldown above.  Per-test tmp file + skip disk I/O on
    # mutations so unit tests can mutate the in-memory dict freely.
    monkeypatch.setattr(
        _scanner_mod,
        "LEVEL_IN_PLAY_PATH",
        str(tmp_path / "level_in_play.json"),
    )
    monkeypatch.setattr(Scanner, "_load_level_in_play", lambda self: None)
    monkeypatch.setattr(Scanner, "_persist_level_in_play", lambda self: None)
    # Default: level-rearm gate disabled in tests so unrelated lifecycle
    # tests (which often dispatch repeated entries at the same price) don't
    # trip it.  TestLevelRearmStateMachine re-enables the production
    # method explicitly via the ``_real_level_rearm`` fixture.
    monkeypatch.setattr(Scanner, "_is_level_in_play", lambda self, sig: False)
    monkeypatch.setattr(Scanner, "_record_level_in_play", lambda self, sig: None)
    # Default: staleness check passes (tests use mocked data_store
    # whose ``.candles`` attribute is a MagicMock that doesn't
    # behave like real candle data).
    monkeypatch.setattr(
        Scanner, "_is_entry_fresh", lambda self, sig, current_price=None: True
    )
    # Belt-and-braces: nuke any stale ``data/signal_dispatch_cooldown.json``
    # that might exist from a misconfigured run BEFORE the conftest landed.
    # Without this, ``Scanner._load_dispatch_cooldown`` (when conftest
    # accidentally fails to patch — e.g. across importlib.reload boundaries)
    # could pick up stale entries and trip cooldown guards in unrelated tests.
    from pathlib import Path
    stale_path = Path("data/signal_dispatch_cooldown.json")
    if stale_path.exists():
        try:
            stale_path.unlink()
        except OSError:
            pass
    # Same belt-and-braces for the level-rearm registry — other tests
    # (e.g. ``test_pr04_portfolio_governance.py``) reload ``src.scanner``
    # mid-suite, leaving stale class references on previously-imported
    # test modules; scanners built from those stale references run the
    # REAL ``_load_level_in_play`` even though the autouse monkeypatch
    # no-op'd the new class.  Nuking the on-disk file before each test
    # gives the load a clean baseline regardless of which class the
    # current scanner was constructed from.
    stale_level_path = Path("data/level_in_play.json")
    if stale_level_path.exists():
        try:
            stale_level_path.unlink()
        except OSError:
            pass

    # ScalpChannel MA-cross cooldown (PR #318).
    from src.channels.scalp import ScalpChannel
    monkeypatch.setattr(
        ScalpChannel,
        "_MA_CROSS_COOLDOWN_PATH",
        str(tmp_path / "ma_cross_cooldown.json"),
    )

    # PaperOrderManager cumulative-PnL persistence (2026-05-08).  Without
    # isolation, the on-disk ledger at ``data/paper_pnl_state.json``
    # accumulates across tests and the broker's ``__init__`` picks up
    # leftover state — every paper test sees PnL from prior runs.
    # ``_resolve_paper_pnl_path`` reads ``PAPER_PNL_STATE_PATH`` lazily
    # per call, so setting the env var here takes effect immediately.
    monkeypatch.setenv(
        "PAPER_PNL_STATE_PATH",
        str(tmp_path / "paper_pnl_state.json"),
    )

    # SignalRouter active-state JSON fallback (2026-05-08).  Same pattern —
    # ``_resolve_active_state_path`` reads ``ACTIVE_ROUTER_STATE_PATH``
    # lazily so this env override isolates each test against the production
    # ``data/active_router_state.json`` ledger.
    monkeypatch.setenv(
        "ACTIVE_ROUTER_STATE_PATH",
        str(tmp_path / "active_router_state.json"),
    )

    # PnL history ledger (2026-05-08).  Daily buckets + weekly/monthly
    # aggregates persist across restarts; isolate per-test so paper /
    # live PnL doesn't leak between cases.
    monkeypatch.setenv(
        "PNL_HISTORY_PATH",
        str(tmp_path / "pnl_history.json"),
    )

    # Per-trade SQLite ledger (paper-trade visibility, 2026-05-16).
    # Same env-override pattern — ``trade_records._resolve_db_path`` reads
    # the env var lazily so test-level monkeypatch works without re-import.
    # Test modules that exercise this store also call
    # ``trade_records.reset_for_test()`` between tests to drop the cached
    # connection (a stale cached conn would otherwise serve a prior
    # test's tmp_path file).
    monkeypatch.setenv(
        "PAPER_TRADES_DB_PATH",
        str(tmp_path / "paper_trades.sqlite"),
    )
    try:
        from src.auto_trade import trade_records as _tr
        _tr.reset_for_test()
    except Exception:
        # First boot or stale import — safe to swallow; the next access
        # opens a fresh connection against the just-set env var.
        pass

    yield


@pytest.fixture()
def numpy_seeded_store():
    """A real ``HistoricalDataStore`` filled through ``update_candle``.

    THE canonical candle fixture shape (2026-07-14 incident, PRs #726/#727):
    the production store holds ``Dict[str, np.ndarray]``, and eight features
    died silently because list-based fixtures never exercised numpy
    truthiness.  New tests that feed candles into store-consuming code MUST
    use this fixture (or seed their own store via ``update_candle``) instead
    of hand-built list dicts.

    Returns a factory: ``store = numpy_seeded_store(symbol, intervals, n)``.
    """
    from src.historical_data import HistoricalDataStore

    def _make(
        symbol: str = "BTCUSDT",
        intervals: tuple = ("5m", "15m"),
        n: int = 120,
        close: float = 100.0,
        spread: float = 0.5,
    ) -> HistoricalDataStore:
        store = HistoricalDataStore()
        for interval in intervals:
            for _ in range(n):
                store.update_candle(
                    symbol,
                    interval,
                    {
                        "open": close,
                        "high": close + spread,
                        "low": close - spread,
                        "close": close,
                        "volume": 1.0,
                    },
                )
        return store

    return _make
