"""The 15m timeframe must have a live feed — regression cover for 2026-07-27.

Every core pair's 15m candle array was frozen at boot for as long as the engine
had been up.  Nothing refreshed it: ``bootstrap.start_websockets`` subscribed
1m/5m/1h/4h and not 15m, ``WS_FALLBACK_POLL_INTERVALS`` is 1m/5m,
``_gap_refill`` only refills *subscribed* streams, and ``seed_symbol`` runs on
universe entry — which, under ``TOP50_FUTURES_ONLY``, never happens again after
boot.  Only mover pairs stayed current, because they are re-seeded every
``MOVER_CANDLE_REFRESH_SEC`` precisely because they sit outside the WS set.

That is not a shadow-arm problem.  15m ATR feeds live SL/TP geometry
(``channels/scalp.py``), MTF weights, structure state, BTC-State and the BTC
regime kill switch, and the SAR exit ledger could not resolve a single core-pair
row: replayed against real candles, 245 of 272 "RUNNING" rows had already hit
their trail, median 4.4h earlier.

The test drives the real ``Bootstrap.start_websockets`` and reads the stream
list the real WebSocketManager was started with — asserting the *behaviour*,
not a copy of the list, so a future edit to the subscription set cannot pass by
agreeing with a mirror in the test file.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.bootstrap import Bootstrap


class _RecordingWSManager:
    """Stands in for WebSocketManager, recording what it was started with."""

    instances: list["_RecordingWSManager"] = []

    def __init__(self, *args, **kwargs):
        self.label = kwargs.get("label", "futures")
        self.streams: list[str] = []
        self.critical_pairs: list[str] = []
        _RecordingWSManager.instances.append(self)

    async def start(self, streams):
        self.streams = list(streams)

    def set_critical_pairs(self, pairs):
        self.critical_pairs = list(pairs)


@pytest.fixture
def started_streams(monkeypatch):
    """Run the real start_websockets over a stub engine; return {label: streams}."""
    _RecordingWSManager.instances = []
    monkeypatch.setattr("src.bootstrap.WebSocketManager", _RecordingWSManager)
    monkeypatch.setattr("src.bootstrap.MOVER_IGNITION_ENABLED", False, raising=False)

    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    engine = SimpleNamespace(
        pair_mgr=SimpleNamespace(tier1_futures_symbols=symbols),
        _on_ws_message=lambda data: None,
        telegram=SimpleNamespace(send_admin_alert=lambda *a, **k: None),
        data_store=SimpleNamespace(),
        _scanner=SimpleNamespace(),
        _mover_ignition=object(),
        _mover_ignition_pending={},
        _ws_futures=None,
        _ws_futures_liq=None,
        _ws_futures_mover=None,
        _oi_poller=None,
    )

    async def _run():
        await Bootstrap(engine).start_websockets()
        return {inst.label: inst.streams for inst in _RecordingWSManager.instances}

    return _run, symbols


class TestFifteenMinuteSubscription:
    async def test_every_tier1_symbol_gets_a_15m_kline_stream(self, started_streams):
        run, symbols = started_streams
        by_label = await run()
        kline_streams = by_label["futures"]

        missing = [s for s in symbols if f"{s.lower()}@kline_15m" not in kline_streams]
        assert not missing, (
            f"no live 15m feed for {missing} — 15m ATR drives live SL/TP geometry, "
            "the BTC regime kill switch and the SAR exit ledger"
        )

    async def test_15m_stream_count_matches_symbol_count(self, started_streams):
        run, symbols = started_streams
        by_label = await run()
        n_15m = sum(1 for s in by_label["futures"] if s.endswith("@kline_15m"))
        assert n_15m == len(symbols)

    async def test_15m_rides_the_kline_pool_not_the_liquidation_pool(
        self, started_streams
    ):
        """A kline stream in the forceOrder pool would inherit its 100x staleness
        multiplier and stop being watched for freshness at all."""
        run, _ = started_streams
        by_label = await run()
        assert not any("kline" in s for s in by_label["futures_liq"])
        assert all("forceOrder" not in s for s in by_label["futures"])

    async def test_every_seeded_scan_timeframe_has_a_live_feed(self, started_streams):
        """The real invariant behind the bug: any intraday timeframe the scanner
        seeds and computes indicators on must also be streamed, or it silently
        freezes at boot.  1d/1w are excluded — they are LevelBook seeding data,
        refreshed by design on the seed path rather than the tape."""
        from config import SEED_TIMEFRAMES

        run, symbols = started_streams
        by_label = await run()
        streams = set(by_label["futures"])
        intraday = [tf.interval for tf in SEED_TIMEFRAMES if tf.interval not in ("1d", "1w")]
        for tf in intraday:
            unfed = [s for s in symbols if f"{s.lower()}@kline_{tf}" not in streams]
            assert not unfed, f"{tf} candles have no live feed for {unfed}"
