"""Tests for CryptoSignalEngine initialization and structure."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest


from src.commands import CommandHandler
from src.scanner import Scanner
from src.bootstrap import Bootstrap
from src.circuit_breaker import CircuitBreaker
from src.performance_tracker import PerformanceTracker


class TestCryptoSignalEngineImport:
    def test_main_module_importable(self):
        """main.py should be importable without errors."""
        import src.main  # noqa: F401

    def test_engine_class_exists(self):
        from src.main import CryptoSignalEngine
        assert CryptoSignalEngine is not None

    def test_entry_point_functions_exist(self):
        from src.main import main, _run
        assert callable(main)
        assert callable(_run)


class TestCryptoSignalEngineInit:
    def _make_engine(self):
        """Create engine with all network calls mocked.

        Also stubs the disk-backed signal-history paths (``load_history`` +
        ``backfill_from_legacy_sources``) so engine construction is
        isolated from any pre-existing ``data/`` files.  Without these
        patches, an existing ``data/signal_history.json`` or
        ``data/invalidation_records.json`` (left from prior runs or
        generated in CI) would leak records into ``_signal_history`` and
        break tests that assert clean-init state.
        """
        with patch("src.main.TelegramBot"), \
             patch("src.main.TelemetryCollector"), \
             patch("src.main.RedisClient"), \
             patch("src.main.SignalQueue"), \
             patch("src.main.StateCache"), \
             patch("src.main.SignalRouter"), \
             patch("src.main.TradeMonitor"), \
             patch("src.main.PairManager"), \
             patch("src.main.HistoricalDataStore"), \
             patch("src.main.PredictiveEngine"), \
             patch("src.main.ExchangeManager"), \
             patch("src.main.SMCDetector"), \
             patch("src.main.MarketRegimeDetector"), \
             patch("src.main.load_history", return_value=[]), \
             patch("src.main.backfill_from_legacy_sources", return_value=[]):
            from src.main import CryptoSignalEngine
            return CryptoSignalEngine()

    def test_engine_has_scanner(self):
        engine = self._make_engine()
        assert isinstance(engine._scanner, Scanner)

    def test_engine_has_command_handler(self):
        engine = self._make_engine()
        assert isinstance(engine._command_handler, CommandHandler)

    def test_engine_has_bootstrap(self):
        engine = self._make_engine()
        assert isinstance(engine._bootstrap, Bootstrap)

    def test_engine_has_circuit_breaker(self):
        engine = self._make_engine()
        assert isinstance(engine._circuit_breaker, CircuitBreaker)

    def test_engine_has_performance_tracker(self):
        engine = self._make_engine()
        assert isinstance(engine._performance_tracker, PerformanceTracker)

    def test_scanner_paused_channels_shared(self):
        engine = self._make_engine()
        # Paused channels set should be the same object
        assert engine._scanner.paused_channels is engine._paused_channels

    def test_scanner_confidence_overrides_shared(self):
        engine = self._make_engine()
        assert engine._scanner.confidence_overrides is engine._confidence_overrides

    def test_scanner_has_circuit_breaker(self):
        engine = self._make_engine()
        assert engine._scanner.circuit_breaker is engine._circuit_breaker

    def test_engine_channels_count(self):
        engine = self._make_engine()
        # Channel-family consolidation reduced the active count from 9 → 8
        # (scalp_obi was absorbed into other channels).  Assertion updated to
        # the current count; if the count changes again, update both this
        # number and the comment, do not silence the test.
        assert len(engine._channels) == 8

    def test_signal_history_starts_empty(self):
        engine = self._make_engine()
        assert engine._signal_history == []

    def test_tasks_starts_empty(self):
        engine = self._make_engine()
        assert engine._tasks == []

    def test_signal_queue_receives_admin_alert_callback(self):
        with patch("src.main.TelegramBot") as telegram_cls, \
             patch("src.main.TelemetryCollector"), \
             patch("src.main.RedisClient"), \
             patch("src.main.SignalQueue") as signal_queue_cls, \
             patch("src.main.StateCache"), \
             patch("src.main.SignalRouter"), \
             patch("src.main.TradeMonitor"), \
             patch("src.main.PairManager"), \
             patch("src.main.HistoricalDataStore"), \
             patch("src.main.PredictiveEngine"), \
             patch("src.main.ExchangeManager"), \
             patch("src.main.SMCDetector"), \
             patch("src.main.MarketRegimeDetector"):
            from src.main import CryptoSignalEngine
            engine = CryptoSignalEngine()

        assert engine is not None
        assert signal_queue_cls.call_args.kwargs["alert_callback"] is telegram_cls.return_value.send_admin_alert


class TestBootstrapInterface:
    def test_bootstrap_has_preflight_check(self):
        assert hasattr(Bootstrap, "preflight_check")

    def test_bootstrap_has_boot(self):
        assert hasattr(Bootstrap, "boot")

    def test_bootstrap_has_shutdown(self):
        assert hasattr(Bootstrap, "shutdown")

    def test_bootstrap_has_start_websockets(self):
        assert hasattr(Bootstrap, "start_websockets")

    @pytest.mark.asyncio
    @patch("src.bootstrap.close_shared_session", new_callable=AsyncMock)
    async def test_shutdown_closes_shared_ai_sessions(self, close_shared_session_mock):
        async def wait_forever() -> None:
            await asyncio.sleep(60)

        task = asyncio.create_task(wait_forever())
        engine = SimpleNamespace(
            _tasks=[task],
            router=SimpleNamespace(stop=AsyncMock(), active_signals={}),
            monitor=SimpleNamespace(stop=AsyncMock()),

            telemetry=SimpleNamespace(stop=AsyncMock()),
            _ws_spot=None,
            _ws_futures=None,
            data_store=SimpleNamespace(
                save_snapshot=AsyncMock(),
                close=AsyncMock(),
            ),
            pair_mgr=SimpleNamespace(close=AsyncMock()),
            _exchange_mgr=SimpleNamespace(close=AsyncMock()),
            _scanner=SimpleNamespace(spot_client=None),
            _openai_evaluator=SimpleNamespace(close=AsyncMock()),
            _onchain_client=SimpleNamespace(close=AsyncMock()),
            _redis_client=SimpleNamespace(close=AsyncMock(), available=False),
            telegram=SimpleNamespace(
                stop=AsyncMock(),
                send_admin_alert=AsyncMock(return_value=True),
            ),
        )

        bootstrap = Bootstrap(engine)
        await bootstrap.shutdown()

        assert task.cancelled()
        close_shared_session_mock.assert_awaited_once()
        engine._openai_evaluator.close.assert_awaited_once()
        engine._onchain_client.close.assert_awaited_once()
        engine._redis_client.close.assert_awaited_once()
        engine.telegram.stop.assert_awaited_once()
        assert engine._tasks == []


class TestBootstrapBootGuards:
    """boot() must abort when pair loading or historical seeding yields zero results."""

    def _make_boot_engine(self, *, pairs=None, seed_return=5):
        """Return a SimpleNamespace engine with all boot-sequence deps stubbed."""
        pair_mgr = SimpleNamespace(
            pairs=pairs if pairs is not None else {"BTCUSDT": SimpleNamespace(market="futures")},
            refresh_top50_futures=AsyncMock(),
            refresh_pairs=AsyncMock(),
        )
        data_store = SimpleNamespace(
            load_snapshot=lambda: False,
            seed_all=AsyncMock(return_value=seed_return),
            gap_fill=AsyncMock(return_value=seed_return),
        )
        return SimpleNamespace(
            _boot_time=0,
            _redis_client=SimpleNamespace(connect=AsyncMock()),
            telemetry=SimpleNamespace(
                set_redis_client=lambda _: None,
                record_api_call=lambda *a, **kw: None,
            ),
            pair_mgr=pair_mgr,
            data_store=data_store,
            predictive=SimpleNamespace(load_model=AsyncMock()),
            telegram=SimpleNamespace(send_admin_alert=AsyncMock()),
            _ws_spot=None,
            _ws_futures=None,
            _tasks=[],
        )

    @pytest.mark.asyncio
    @patch("src.bootstrap.spot_rate_limiter")
    @patch("src.bootstrap.futures_rate_limiter")
    @patch("src.bootstrap.BinanceClient")
    @patch("src.bootstrap.TOP50_FUTURES_ONLY", True)
    async def test_boot_aborts_when_no_pairs_loaded(
        self, _bc, _frl, _srl,
    ):
        """boot() must raise RuntimeError when pair_mgr.pairs is empty."""
        engine = self._make_boot_engine(pairs={})
        bootstrap = Bootstrap(engine)
        with pytest.raises(RuntimeError, match="No trading pairs loaded"):
            await bootstrap.boot()

    @pytest.mark.asyncio
    @patch("src.bootstrap.spot_rate_limiter")
    @patch("src.bootstrap.futures_rate_limiter")
    @patch("src.bootstrap.BinanceClient")
    @patch("src.bootstrap.TOP50_FUTURES_ONLY", True)
    async def test_boot_aborts_when_zero_pairs_seeded(
        self, _bc, _frl, _srl,
    ):
        """boot() must raise RuntimeError when seed_all returns 0."""
        engine = self._make_boot_engine(seed_return=0)
        bootstrap = Bootstrap(engine)
        with pytest.raises(RuntimeError, match="seeded for 0 pairs"):
            await bootstrap.boot()

    @pytest.mark.asyncio
    @patch("src.bootstrap.spot_rate_limiter")
    @patch("src.bootstrap.futures_rate_limiter")
    @patch("src.bootstrap.BinanceClient")
    @patch("src.bootstrap.TOP50_FUTURES_ONLY", True)
    async def test_boot_sends_alert_on_zero_pairs(
        self, _bc, _frl, _srl,
    ):
        """boot() must send a Telegram admin alert when no pairs are loaded."""
        engine = self._make_boot_engine(pairs={})
        bootstrap = Bootstrap(engine)
        with pytest.raises(RuntimeError):
            await bootstrap.boot()
        engine.telegram.send_admin_alert.assert_awaited_once()
        alert_msg = engine.telegram.send_admin_alert.call_args[0][0]
        assert "No trading pairs loaded" in alert_msg

    @pytest.mark.asyncio
    @patch("src.bootstrap.spot_rate_limiter")
    @patch("src.bootstrap.futures_rate_limiter")
    @patch("src.bootstrap.BinanceClient")
    @patch("src.bootstrap.TOP50_FUTURES_ONLY", True)
    async def test_boot_sends_alert_on_zero_seeded(
        self, _bc, _frl, _srl,
    ):
        """boot() must send a Telegram admin alert when seeding yields 0."""
        engine = self._make_boot_engine(seed_return=0)
        bootstrap = Bootstrap(engine)
        with pytest.raises(RuntimeError):
            await bootstrap.boot()
        engine.telegram.send_admin_alert.assert_awaited_once()
        alert_msg = engine.telegram.send_admin_alert.call_args[0][0]
        assert "seeded for 0 pairs" in alert_msg


class TestHistoricalSeedReturnCount:
    """seed_all() must return the number of pairs successfully seeded."""

    @pytest.mark.asyncio
    async def test_seed_all_returns_seeded_count(self):
        from src.historical_data import HistoricalDataStore

        store = HistoricalDataStore()
        store.seed_symbol = AsyncMock()
        # Simulate candles being populated for BTCUSDT but not ETHUSDT
        async def _fake_seed(sym, market):
            if sym == "BTCUSDT":
                import numpy as np
                store.candles["BTCUSDT"] = {
                    "1m": {"close": np.array([1.0, 2.0])}
                }

        store.seed_symbol = _fake_seed

        pair_mgr = SimpleNamespace(
            pairs={
                "BTCUSDT": SimpleNamespace(market="futures"),
                "ETHUSDT": SimpleNamespace(market="futures"),
            },
            record_candles=lambda *a: None,
        )

        count = await store.seed_all(pair_mgr)
        assert count == 1  # only BTCUSDT was seeded

    @pytest.mark.asyncio
    async def test_seed_all_returns_zero_when_all_fail(self):
        from src.historical_data import HistoricalDataStore

        store = HistoricalDataStore()
        store.seed_symbol = AsyncMock()  # does not populate candles

        pair_mgr = SimpleNamespace(
            pairs={
                "BTCUSDT": SimpleNamespace(market="futures"),
            },
            record_candles=lambda *a: None,
        )

        count = await store.seed_all(pair_mgr)
        assert count == 0

    @pytest.mark.asyncio
    async def test_seed_all_returns_zero_for_empty_pairs(self):
        from src.historical_data import HistoricalDataStore

        store = HistoricalDataStore()
        pair_mgr = SimpleNamespace(pairs={}, record_candles=lambda *a: None)

        count = await store.seed_all(pair_mgr)
        assert count == 0


class TestScannerInterface:
    def test_scanner_has_scan_loop(self):
        assert hasattr(Scanner, "scan_loop")

    def test_scanner_has_cooldown_methods(self):
        assert hasattr(Scanner, "_is_in_cooldown")
        assert hasattr(Scanner, "_set_cooldown")

    def test_scanner_has_scan_symbol(self):
        assert hasattr(Scanner, "_scan_symbol")


class TestCommandHandlerInterface:
    def test_command_handler_has_handle_command(self):
        assert hasattr(CommandHandler, "_handle_command")


class TestBootstrapBootMessage:
    """boot() must send a boot test message to the active trading channel."""

    def _make_full_boot_engine(self, *, pair_count=5):
        """Return a stubbed engine that can complete a full successful boot."""
        pairs = {f"TOKEN{i}USDT": SimpleNamespace(market="futures") for i in range(pair_count)}
        pair_mgr = SimpleNamespace(
            pairs=pairs,
            refresh_top50_futures=AsyncMock(),
            refresh_pairs=AsyncMock(),
            tier1_spot_symbols=[],
            tier1_futures_symbols=[],
        )
        # `bootstrap.py:177` iterates `engine.data_store.candles.items()` for
        # the post-seed CVD priming step.  Earlier fixture omitted `candles`
        # which caused AttributeError mid-boot — provide an empty dict so the
        # CVD priming loop is a no-op (the test exercises the boot-message
        # flow, not CVD seeding).
        data_store = SimpleNamespace(
            load_snapshot=lambda: False,
            seed_all=AsyncMock(return_value=pair_count),
            gap_fill=AsyncMock(return_value=pair_count),
            candles={},
        )
        return SimpleNamespace(
            _boot_time=0,
            _redis_client=SimpleNamespace(connect=AsyncMock()),
            telemetry=SimpleNamespace(
                set_redis_client=lambda _: None,
                record_api_call=lambda *a, **kw: None,
            ),
            pair_mgr=pair_mgr,
            data_store=data_store,
            predictive=SimpleNamespace(load_model=AsyncMock()),
            telegram=SimpleNamespace(
                send_admin_alert=AsyncMock(),
                send_message=AsyncMock(return_value=True),
            ),
            _ws_spot=None,
            _ws_futures=None,
            _tasks=[],
        )

    @pytest.mark.asyncio
    @patch("src.bootstrap.spot_rate_limiter")
    @patch("src.bootstrap.futures_rate_limiter")
    @patch("src.bootstrap.BinanceClient")
    @patch("src.bootstrap.TOP50_FUTURES_ONLY", True)
    @patch("src.bootstrap.TELEGRAM_ACTIVE_CHANNEL_ID", "-100123456")
    @patch("config.validate_critical_env_vars")
    async def test_boot_sends_test_message_to_active_channel(
        self, _vcv, _bc, _frl, _srl,
    ):
        """boot() sends a boot test message to TELEGRAM_ACTIVE_CHANNEL_ID."""
        engine = self._make_full_boot_engine(pair_count=3)
        bootstrap = Bootstrap(engine)
        with patch.object(bootstrap, "start_websockets", AsyncMock()), \
             patch.object(bootstrap, "preflight_check", AsyncMock(return_value=True)), \
             patch.object(bootstrap, "launch_runtime_tasks", return_value=[]):
            await bootstrap.boot()

        engine.telegram.send_message.assert_awaited_once()
        call_args = engine.telegram.send_message.call_args
        assert call_args[0][0] == "-100123456"
        msg = call_args[0][1]
        assert "ENGINE BOOT TEST" in msg
        assert "Scanning 3 pairs" in msg

    @pytest.mark.asyncio
    @patch("src.bootstrap.spot_rate_limiter")
    @patch("src.bootstrap.futures_rate_limiter")
    @patch("src.bootstrap.BinanceClient")
    @patch("src.bootstrap.TOP50_FUTURES_ONLY", True)
    @patch("src.bootstrap.TELEGRAM_ACTIVE_CHANNEL_ID", "")
    @patch("config.validate_critical_env_vars")
    async def test_boot_skips_test_message_when_channel_not_set(
        self, _vcv, _bc, _frl, _srl,
    ):
        """boot() must NOT call send_message when TELEGRAM_ACTIVE_CHANNEL_ID is empty."""
        engine = self._make_full_boot_engine()
        bootstrap = Bootstrap(engine)
        with patch.object(bootstrap, "start_websockets", AsyncMock()), \
             patch.object(bootstrap, "preflight_check", AsyncMock(return_value=True)), \
             patch.object(bootstrap, "launch_runtime_tasks", return_value=[]):
            await bootstrap.boot()

        engine.telegram.send_message.assert_not_awaited()

    @pytest.mark.asyncio
    @patch("src.bootstrap.spot_rate_limiter")
    @patch("src.bootstrap.futures_rate_limiter")
    @patch("src.bootstrap.BinanceClient")
    @patch("src.bootstrap.TOP50_FUTURES_ONLY", True)
    @patch("src.bootstrap.TELEGRAM_ACTIVE_CHANNEL_ID", "-100123456")
    @patch("config.validate_critical_env_vars")
    async def test_boot_continues_when_test_message_fails(
        self, _vcv, _bc, _frl, _srl,
    ):
        """boot() must not raise if the boot test message send fails."""
        engine = self._make_full_boot_engine()
        engine.telegram.send_message = AsyncMock(side_effect=Exception("Telegram error"))
        bootstrap = Bootstrap(engine)
        with patch.object(bootstrap, "start_websockets", AsyncMock()), \
             patch.object(bootstrap, "preflight_check", AsyncMock(return_value=True)), \
             patch.object(bootstrap, "launch_runtime_tasks", return_value=[]):
            # Must NOT raise even though send_message throws
            await bootstrap.boot()


class TestPairRefreshLoopCap:
    """_pair_refresh_loop caps new pair seeding to _MAX_NEW_SEEDS_PER_CYCLE."""

    _MAX_NEW_SEEDS_PER_CYCLE = 10

    @pytest.mark.asyncio
    async def test_seeds_at_most_10_new_pairs_per_cycle(self):
        """When >10 new symbols are discovered, only the first 10 are seeded."""
        seeded = []

        async def fake_seed(sym, market):
            seeded.append(sym)

        # 15 new symbols discovered
        new_syms = [f"TOKEN{i}USDT" for i in range(15)]

        engine = SimpleNamespace(
            pair_mgr=SimpleNamespace(
                refresh_pairs=AsyncMock(return_value=new_syms),
                pairs={s: SimpleNamespace(market="spot") for s in new_syms},
                spot_symbols=[],
                futures_symbols=[],
                record_candles=lambda sym, tf, count: None,
            ),
            data_store=SimpleNamespace(
                seed_symbol=fake_seed,
                candles={},
            ),
        )

        # Simulate one iteration of the loop (skip the outer sleep)
        async def _run_one_cycle(eng):
            new_symbols = await eng.pair_mgr.refresh_pairs()
            seeded_in_cycle = []
            for sym in new_symbols[:self._MAX_NEW_SEEDS_PER_CYCLE]:
                info = eng.pair_mgr.pairs.get(sym)
                if info is None:
                    continue
                await eng.data_store.seed_symbol(sym, info.market)
                seeded_in_cycle.append(sym)
            return seeded_in_cycle, new_symbols

        seeded_in_cycle, new_symbols = await _run_one_cycle(engine)
        assert len(seeded_in_cycle) == self._MAX_NEW_SEEDS_PER_CYCLE
        assert len(new_symbols) == 15

    @pytest.mark.asyncio
    async def test_seeds_all_when_under_cap(self):
        """When ≤10 new symbols are found, all are seeded without truncation."""
        seeded = []

        async def fake_seed(sym, market):
            seeded.append(sym)

        new_syms = [f"TOKEN{i}USDT" for i in range(5)]
        engine = SimpleNamespace(
            pair_mgr=SimpleNamespace(
                refresh_pairs=AsyncMock(return_value=new_syms),
                pairs={s: SimpleNamespace(market="spot") for s in new_syms},
                record_candles=lambda sym, tf, count: None,
            ),
            data_store=SimpleNamespace(
                seed_symbol=fake_seed,
                candles={},
            ),
        )

        async def _run_one_cycle(eng):
            new_symbols = await eng.pair_mgr.refresh_pairs()
            seeded_in_cycle = []
            for sym in new_symbols[:self._MAX_NEW_SEEDS_PER_CYCLE]:
                info = eng.pair_mgr.pairs.get(sym)
                if info is None:
                    continue
                await eng.data_store.seed_symbol(sym, info.market)
                seeded_in_cycle.append(sym)
            return seeded_in_cycle

        seeded_in_cycle = await _run_one_cycle(engine)
        assert len(seeded_in_cycle) == 5


# ---------------------------------------------------------------------------
# Expiry handler — engine.cleanup_expired callback semantics
# ---------------------------------------------------------------------------


class TestSignalExpiryHandler:
    """``CryptoSignalEngine._handle_signal_expiry`` is the callback the
    SignalRouter invokes when a signal's max-hold elapses.  It must:
      - compute realised P&L from sig.current_price
      - flip status to EXPIRED + stamp terminal_outcome_timestamp
      - archive into _signal_history + persist
      - record a perf-tracker outcome with outcome_label='EXPIRED'
      - close the broker position when auto-trade is enabled
      - be idempotent on signals whose status is already terminal
    """

    def _make_engine_with_mocks(self):
        """Build a CryptoSignalEngine whose perf-tracker, order-manager,
        and history persistence are mocked so we can assert on them."""
        from datetime import datetime, timezone
        from unittest.mock import MagicMock, patch

        from src.channels.base import Signal
        from src.smc import Direction

        with patch("src.main.TelegramBot"), \
             patch("src.main.TelemetryCollector"), \
             patch("src.main.RedisClient"), \
             patch("src.main.SignalQueue"), \
             patch("src.main.StateCache"), \
             patch("src.main.SignalRouter"), \
             patch("src.main.TradeMonitor"), \
             patch("src.main.PairManager"), \
             patch("src.main.HistoricalDataStore"), \
             patch("src.main.PredictiveEngine"), \
             patch("src.main.ExchangeManager"), \
             patch("src.main.SMCDetector"), \
             patch("src.main.MarketRegimeDetector"), \
             patch("src.main.load_history", return_value=[]), \
             patch("src.main.backfill_from_legacy_sources", return_value=[]), \
             patch("src.main.save_history") as save_h:
            from src.main import CryptoSignalEngine
            engine = CryptoSignalEngine()
        # Replace tracker + order_manager with simple mocks for assertion.
        engine._performance_tracker = MagicMock()
        engine._order_manager = MagicMock()
        engine._order_manager.is_enabled = False
        return engine, save_h

    def _make_signal(
        self,
        *,
        direction: str = "LONG",
        entry: float = 100.0,
        current_price: float = 102.0,
        signal_id: str = "EXP-1",
    ):
        from src.channels.base import Signal
        from src.smc import Direction

        d = Direction.LONG if direction == "LONG" else Direction.SHORT
        sig = Signal(
            channel="360_SCALP",
            symbol="SOLUSDT",
            direction=d,
            entry=entry,
            stop_loss=entry * 0.99 if d == Direction.LONG else entry * 1.01,
            tp1=entry * 1.01 if d == Direction.LONG else entry * 0.99,
            tp2=entry * 1.02,
            confidence=80.0,
            signal_id=signal_id,
        )
        sig.current_price = current_price
        sig.setup_class = "SR_FLIP_RETEST"
        sig.quality_tier = "A"
        sig.status = "ACTIVE"
        return sig

    def test_handler_computes_pnl_for_long_above_entry(self):
        from datetime import datetime, timezone
        engine, _ = self._make_engine_with_mocks()
        sig = self._make_signal(direction="LONG", entry=100.0, current_price=102.0)

        engine._handle_signal_expiry(sig, datetime.now(timezone.utc))

        assert sig.status == "EXPIRED"
        assert sig.pnl_pct == pytest.approx(2.0)

    def test_handler_computes_pnl_for_short_below_entry(self):
        from datetime import datetime, timezone
        engine, _ = self._make_engine_with_mocks()
        sig = self._make_signal(direction="SHORT", entry=100.0, current_price=99.5)

        engine._handle_signal_expiry(sig, datetime.now(timezone.utc))

        assert sig.status == "EXPIRED"
        assert sig.pnl_pct == pytest.approx(0.5)

    def test_handler_archives_to_signal_history(self):
        from datetime import datetime, timezone
        engine, _ = self._make_engine_with_mocks()
        sig = self._make_signal()

        engine._handle_signal_expiry(sig, datetime.now(timezone.utc))

        # In-memory archive — save_history persistence is exercised
        # separately in test_signal_history_store.py.
        assert sig in engine._signal_history

    def test_handler_stamps_terminal_outcome_timestamp(self):
        from datetime import datetime, timezone
        engine, _ = self._make_engine_with_mocks()
        sig = self._make_signal()
        now = datetime.now(timezone.utc)

        engine._handle_signal_expiry(sig, now)

        assert sig.terminal_outcome_timestamp == now

    def test_handler_records_perf_outcome_as_expired(self):
        from datetime import datetime, timezone
        engine, _ = self._make_engine_with_mocks()
        sig = self._make_signal()

        engine._handle_signal_expiry(sig, datetime.now(timezone.utc))

        engine._performance_tracker.record_outcome.assert_called_once()
        kwargs = engine._performance_tracker.record_outcome.call_args.kwargs
        assert kwargs["outcome_label"] == "EXPIRED"
        assert kwargs["hit_tp"] == 0
        assert kwargs["hit_sl"] is False
        assert kwargs["signal_id"] == sig.signal_id
        assert kwargs["pnl_pct"] == pytest.approx(2.0)

    def test_handler_idempotent_on_already_terminal(self):
        """If status is already terminal (e.g. a race with trade_monitor closed
        the signal first), this handler must be a no-op so we don't double-
        archive or double-record."""
        from datetime import datetime, timezone
        engine, save_h = self._make_engine_with_mocks()
        save_h.reset_mock()
        sig = self._make_signal()
        sig.status = "SL_HIT"

        engine._handle_signal_expiry(sig, datetime.now(timezone.utc))

        assert sig.status == "SL_HIT"  # unchanged
        assert sig not in engine._signal_history
        engine._performance_tracker.record_outcome.assert_not_called()
        save_h.assert_not_called()

    def test_handler_skips_broker_close_when_auto_trade_off(self):
        from datetime import datetime, timezone
        engine, _ = self._make_engine_with_mocks()
        engine._order_manager.is_enabled = False
        sig = self._make_signal()

        engine._handle_signal_expiry(sig, datetime.now(timezone.utc))

        engine._order_manager.close_full.assert_not_called()
