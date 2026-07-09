"""Tests for the 2026-07-09 mover-path profitability package.

Ships ACTIVE (owner sign-off in-session 2026-07-09); every flag remains an
ops-reversible runtime tunable whose OFF state shadow-logs. Covers:
1. runtime_tunables — new registry keys + active defaults.
2. runner_policy + TradeMonitor — mover runner exit fork, banked-slice
   PnL accounting, shadow stamp while the flag is off.
3. Scanner loss-streak escalation — streak bookkeeping, doubling + cap,
   shadow while off, reset on wins.
4. Scanner active-duplicate guard — blocks when enabled, shadow-logs when
   off.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from src import runtime_tunables as rt
from src.channels.base import Signal
from src.execution import runner_policy
from src.smc import Direction
from src.trade_monitor import TradeMonitor
from src.utils import utcnow


@pytest.fixture(autouse=True)
def _reset_tunables():
    rt.reset_for_test()
    yield
    rt.reset_for_test()


class _FakeDoc:
    def __init__(self, data):
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return self._data


class _FakeFirestore:
    def __init__(self):
        self.data = {}

    def collection(self, name):
        return self

    def document(self, name):
        return self

    def get(self):
        return _FakeDoc(dict(self.data))

    def set(self, payload, merge=False):
        self.data.update(payload)


def _tunables(**values):
    fs = _FakeFirestore()
    rt.init_runtime_tunables(fs)
    if values:
        rt.set_values(values)
    return fs


# ---------------------------------------------------------------------------
# runtime_tunables — new keys ship with dark / behaviour-neutral defaults
# ---------------------------------------------------------------------------

def test_new_tunables_active_defaults():
    # Owner sign-off 2026-07-09: ships ACTIVE, reversible from ops.
    assert rt.get("mover_runner_exit_enabled") is True
    assert rt.get("loss_streak_escalation_enabled") is True
    assert rt.get("active_dup_guard_enabled") is True
    # Live-flags default to the current env behaviour (ON) — neutral.
    assert rt.get("mover_trend_pullback_live") is True
    assert rt.get("mover_avwap_scalp_live") is True
    assert rt.get("loss_streak_cap_hours") == pytest.approx(12.0)


def test_new_tunables_in_snapshot():
    keys = {e["key"] for e in rt.snapshot()}
    for key in (
        "mover_runner_exit_enabled",
        "mover_trend_pullback_live",
        "mover_avwap_scalp_live",
        "loss_streak_escalation_enabled",
        "loss_streak_cap_hours",
        "active_dup_guard_enabled",
    ):
        assert key in keys


# ---------------------------------------------------------------------------
# runner_policy
# ---------------------------------------------------------------------------

def test_runner_policy_scope():
    assert runner_policy.is_mover_setup("MOVER_TREND_PULLBACK")
    assert runner_policy.is_mover_setup("MOVER_AVWAP_SCALP")
    assert not runner_policy.is_mover_setup("SR_FLIP_RETEST")
    assert not runner_policy.is_mover_setup("")


def test_runner_policy_active_by_default():
    assert runner_policy.runner_exit_active("MOVER_TREND_PULLBACK") is True
    assert runner_policy.runner_exit_shadow("MOVER_TREND_PULLBACK") is False
    # Non-movers never shadow (nothing to stamp) and never activate.
    assert runner_policy.runner_exit_shadow("SR_FLIP_RETEST") is False
    assert runner_policy.runner_exit_active("SR_FLIP_RETEST") is False


def test_runner_policy_shadows_when_flag_off():
    _tunables(mover_runner_exit_enabled=False)
    assert runner_policy.runner_exit_active("MOVER_TREND_PULLBACK") is False
    assert runner_policy.runner_exit_shadow("MOVER_TREND_PULLBACK") is True


def test_runner_policy_activates_via_tunable():
    _tunables(mover_runner_exit_enabled=True)
    assert runner_policy.runner_exit_active("MOVER_AVWAP_SCALP") is True
    assert runner_policy.runner_exit_shadow("MOVER_AVWAP_SCALP") is False
    assert runner_policy.runner_exit_active("SR_FLIP_RETEST") is False


# ---------------------------------------------------------------------------
# TradeMonitor — runner exit fork + banked accounting
# ---------------------------------------------------------------------------

def _make_signal(
    *,
    symbol: str = "MONUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 100.0,
    stop_loss: float = 98.0,
    tp1: float = 102.0,
    tp2: float = 103.2,
    tp3: float = 105.0,
    setup_class: str = "MOVER_TREND_PULLBACK",
    current_price: float = 100.0,
) -> Signal:
    sig = Signal(
        channel="360_SCALP",
        symbol=symbol,
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=tp2,
        confidence=80.0,
        signal_id=f"RUNNER-{symbol}-001",
    )
    sig.tp3 = tp3
    sig.original_entry = entry
    sig.original_sl_distance = abs(entry - stop_loss)
    sig.current_price = current_price
    sig.setup_class = setup_class
    sig.signal_tier = "B"
    sig.timestamp = utcnow() - timedelta(seconds=600)
    sig.status = "ACTIVE"
    return sig


def _data_store_with_candle(high: float, low: float):
    ds = MagicMock()
    ds.get_candles.return_value = {
        "high": [high],
        "low": [low],
        "close": [(high + low) / 2],
        "open": [(high + low) / 2],
        "volume": [1000.0],
    }
    ds.ticks = {}
    return ds


def _build_monitor(*, order_manager=None, data_store=None):
    regime_detector = MagicMock()
    regime_detector.classify.return_value = MagicMock(
        regime=MagicMock(value="TRENDING_UP")
    )
    return TradeMonitor(
        data_store=data_store or MagicMock(),
        send_telegram=AsyncMock(return_value=True),
        get_active_signals=lambda: {},
        remove_signal=lambda sid: None,
        update_signal=MagicMock(),
        regime_detector=regime_detector,
        indicators_fn=lambda sym: {"adx": 18.0, "ema_slope": 0.0},
        order_manager=order_manager,
    )


def _enabled_order_manager():
    om = MagicMock()
    om.is_enabled = True
    om.close_full = AsyncMock(return_value="ccxt-close-id")
    om.close_partial = AsyncMock(return_value="ccxt-part-id")
    om.add_dca_entry = AsyncMock(return_value="ccxt-dca-id")
    return om


async def test_mover_tp1_full_closes_while_dark_with_shadow_stamp(monkeypatch):
    """Flag turned OFF from ops: mover full-closes at TP1 (BE_THEN_TP1
    behaviour) and the fork moment is stamped for the shadow window."""
    monkeypatch.setattr("src.trade_monitor.BE_THEN_TP1_DEFAULT_ENABLED", True)
    _tunables(mover_runner_exit_enabled=False)
    om = _enabled_order_manager()
    ds = _data_store_with_candle(high=102.5, low=99.9)
    monitor = _build_monitor(order_manager=om, data_store=ds)

    sig = _make_signal(current_price=102.1)
    await monitor._evaluate_signal(sig)

    om.close_full.assert_awaited()
    assert om.close_full.await_args.kwargs.get("reason") == "full_tp_hit"
    om.close_partial.assert_not_called()
    assert "runner-shadow@TP1" in sig.execution_note


async def test_non_mover_tp1_full_close_has_no_shadow_stamp(monkeypatch):
    monkeypatch.setattr("src.trade_monitor.BE_THEN_TP1_DEFAULT_ENABLED", True)
    om = _enabled_order_manager()
    ds = _data_store_with_candle(high=102.5, low=99.9)
    monitor = _build_monitor(order_manager=om, data_store=ds)

    sig = _make_signal(setup_class="SR_FLIP_RETEST", current_price=102.1)
    await monitor._evaluate_signal(sig)

    om.close_full.assert_awaited()
    assert "runner-shadow" not in sig.execution_note


async def test_mover_tp1_banks_partial_when_runner_active(monkeypatch):
    """Flag ON: mover banks 40% at TP1, stays open, trail owns the rest."""
    monkeypatch.setattr("src.trade_monitor.BE_THEN_TP1_DEFAULT_ENABLED", True)
    _tunables(mover_runner_exit_enabled=True)
    om = _enabled_order_manager()
    ds = _data_store_with_candle(high=102.5, low=99.9)
    monitor = _build_monitor(order_manager=om, data_store=ds)

    sig = _make_signal(current_price=102.1)
    await monitor._evaluate_signal(sig)

    assert sig.status == "TP1_HIT"
    assert sig.runner_banked_fraction == pytest.approx(0.40)
    # Banked slice carries 0.4 × the +2% TP1 move.
    assert sig.runner_banked_pnl_pct == pytest.approx(0.4 * 2.0)
    om.close_partial.assert_awaited()
    assert om.close_partial.await_args.args[1] == pytest.approx(0.40)
    om.close_full.assert_not_called()
    # Stop lifted to the profit-side TP1 buffer, never left below entry.
    assert sig.stop_loss >= sig.entry


async def test_mover_short_tp1_banks_partial_when_runner_active(monkeypatch):
    monkeypatch.setattr("src.trade_monitor.BE_THEN_TP1_DEFAULT_ENABLED", True)
    _tunables(mover_runner_exit_enabled=True)
    om = _enabled_order_manager()
    ds = _data_store_with_candle(high=100.1, low=97.9)
    monitor = _build_monitor(order_manager=om, data_store=ds)

    sig = _make_signal(
        direction=Direction.SHORT,
        entry=100.0, stop_loss=102.0, tp1=98.0, tp2=96.8, tp3=95.0,
        current_price=97.95,
    )
    await monitor._evaluate_signal(sig)

    assert sig.status == "TP1_HIT"
    assert sig.runner_banked_fraction == pytest.approx(0.40)
    assert sig.runner_banked_pnl_pct == pytest.approx(0.4 * 2.0)
    om.close_full.assert_not_called()


async def test_non_mover_still_full_closes_when_runner_active(monkeypatch):
    """The runner flag scopes to mover paths only."""
    monkeypatch.setattr("src.trade_monitor.BE_THEN_TP1_DEFAULT_ENABLED", True)
    _tunables(mover_runner_exit_enabled=True)
    om = _enabled_order_manager()
    ds = _data_store_with_candle(high=102.5, low=99.9)
    monitor = _build_monitor(order_manager=om, data_store=ds)

    sig = _make_signal(setup_class="FAILED_AUCTION_RECLAIM", current_price=102.1)
    await monitor._evaluate_signal(sig)

    om.close_full.assert_awaited()
    assert om.close_full.await_args.kwargs.get("reason") == "full_tp_hit"
    assert sig.runner_banked_fraction == 0.0


async def test_mover_tp3_does_not_close_runner_rides(monkeypatch):
    """NO fixed TP3 cap for movers: crossing TP3 stamps best_tp=3 and banks
    the cumulative 70% via the TP2 leg, but the last slice stays open on the
    trail — no full close."""
    monkeypatch.setattr("src.trade_monitor.BE_THEN_TP1_DEFAULT_ENABLED", True)
    om = _enabled_order_manager()
    # Single mega-candle clears TP3 (105) without dipping to the stop.
    ds = _data_store_with_candle(high=106.0, low=101.5)
    monitor = _build_monitor(order_manager=om, data_store=ds)

    sig = _make_signal(current_price=105.8)
    sig.max_favorable_excursion_pct = 5.8
    await monitor._evaluate_signal(sig)

    om.close_full.assert_not_called()           # remainder still riding
    assert sig.status == "TP2_HIT"              # trail phase (0.35× mult)
    assert sig.best_tp_hit == 3                 # TP3-cleared stamped, not downgraded
    assert sig.runner_banked_fraction == pytest.approx(0.70)
    assert sig.stop_loss >= sig.tp1             # floor locked at TP1


async def test_non_mover_tp3_still_full_closes(monkeypatch):
    monkeypatch.setattr("src.trade_monitor.BE_THEN_TP1_DEFAULT_ENABLED", False)
    om = _enabled_order_manager()
    ds = _data_store_with_candle(high=106.0, low=101.5)
    monitor = _build_monitor(order_manager=om, data_store=ds)

    sig = _make_signal(setup_class="SR_FLIP_RETEST", current_price=105.8)
    await monitor._evaluate_signal(sig)

    om.close_full.assert_awaited()
    assert om.close_full.await_args.kwargs.get("reason") == "full_tp_hit"


def test_realized_pnl_runner_trail_out_beyond_tp3():
    """HMSTR-shaped run: 40% @ TP1 (+2%), 30% @ TP2 (+3.2%), remainder
    trails out at +25% — honest blend, no 2.5R cap."""
    sig = _make_signal()
    TradeMonitor._runner_bank(sig, 0.40, 102.0)
    TradeMonitor._runner_bank(sig, 0.30, 103.2)
    TradeMonitor._set_realized_pnl(sig, 125.0)
    expected = 0.4 * 2.0 + 0.3 * 3.2 + 0.3 * 25.0
    assert sig.pnl_pct == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Banked-slice PnL accounting
# ---------------------------------------------------------------------------

def test_runner_bank_accumulates_and_clamps():
    sig = _make_signal()
    booked = TradeMonitor._runner_bank(sig, 0.40, 102.0)   # +2% move
    assert booked == pytest.approx(0.40)
    booked = TradeMonitor._runner_bank(sig, 0.90, 103.2)   # clamps to 0.60
    assert booked == pytest.approx(0.60)
    assert sig.runner_banked_fraction == pytest.approx(1.0)
    assert TradeMonitor._runner_bank(sig, 0.10, 105.0) == 0.0  # nothing left


def test_realized_pnl_blends_runner_banks():
    """Bank 40% at +2% (TP1) then trail out at entry → ~+0.8%, not 0%."""
    sig = _make_signal()
    TradeMonitor._runner_bank(sig, 0.40, 102.0)
    TradeMonitor._set_realized_pnl(sig, 100.0)   # residual exits at entry
    assert sig.pnl_pct == pytest.approx(0.4 * 2.0)


def test_realized_pnl_runner_full_ride_to_tp3():
    """40% @ TP1 (+2%), 30% @ TP2 (+3.2%), remainder @ TP3 (+5%)."""
    sig = _make_signal()
    TradeMonitor._runner_bank(sig, 0.40, 102.0)
    TradeMonitor._runner_bank(sig, 0.30, 103.2)
    TradeMonitor._set_realized_pnl(sig, 105.0)
    expected = 0.4 * 2.0 + 0.3 * 3.2 + 0.3 * 5.0
    assert sig.pnl_pct == pytest.approx(expected)


def test_realized_pnl_unchanged_without_runner_banks():
    # Plain residual exit.
    sig = _make_signal()
    TradeMonitor._set_realized_pnl(sig, 98.0)
    assert sig.pnl_pct == pytest.approx(-2.0)
    # Pre-TP blend (PR #411 semantics) untouched.
    sig2 = _make_signal()
    sig2.partial_close_pct = 0.25
    sig2.pre_tp_pct = 0.45
    TradeMonitor._set_realized_pnl(sig2, 100.0)
    assert sig2.pnl_pct == pytest.approx(0.25 * 0.45)


def test_realized_pnl_composes_pre_tp_and_runner_banks():
    """Pre-TP grabbed 25% at +0.45%, runner banked 40% at +2%, residual at
    entry — pre-TP owns at most the non-banked slice."""
    sig = _make_signal()
    sig.partial_close_pct = 0.25
    sig.pre_tp_pct = 0.45
    TradeMonitor._runner_bank(sig, 0.40, 102.0)
    TradeMonitor._set_realized_pnl(sig, 100.0)
    expected = 0.4 * 2.0 + 0.25 * 0.45 + 0.35 * 0.0
    assert sig.pnl_pct == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Scanner — loss-streak escalation (dark) + active-duplicate guard (dark)
# ---------------------------------------------------------------------------

def _stub_scanner(tmp_path, monkeypatch):
    """Minimal Scanner stub: real methods, no boot."""
    from src.scanner import Scanner

    monkeypatch.chdir(tmp_path)  # persistence files land in tmp
    sc = Scanner.__new__(Scanner)
    sc._loss_streaks = {}
    sc._dispatch_cooldown = {}
    sc._path_funnel_counters = defaultdict(int)
    sc._suppression_counters = defaultdict(int)
    sc.router = MagicMock()
    sc.router.active_signals = {}
    return sc


def _outcome_sig(pnl: float, *, symbol="MONUSDT", setup="MOVER_TREND_PULLBACK",
                 direction=Direction.LONG):
    sig = _make_signal(symbol=symbol, setup_class=setup, direction=direction)
    sig.pnl_pct = pnl
    return sig


def test_loss_streak_counts_resets_and_ignores_scratches(tmp_path, monkeypatch):
    sc = _stub_scanner(tmp_path, monkeypatch)
    key = ("MONUSDT", "MOVER_TREND_PULLBACK", "LONG")

    assert sc._update_loss_streak(_outcome_sig(-1.0), "SL_HIT") == 1
    assert sc._update_loss_streak(_outcome_sig(-0.9), "EXPIRED") == 2
    # BE-park scratch (−0.15%) leaves the streak unchanged.
    assert sc._update_loss_streak(_outcome_sig(-0.15), "SL_HIT") == 2
    assert sc._loss_streaks[key] == 2
    # A profitable outcome resets.
    assert sc._update_loss_streak(_outcome_sig(1.2), "TP1_HIT") == 0
    assert key not in sc._loss_streaks


def test_loss_streak_persists_and_reloads(tmp_path, monkeypatch):
    sc = _stub_scanner(tmp_path, monkeypatch)
    sc._update_loss_streak(_outcome_sig(-1.0), "SL_HIT")
    sc._update_loss_streak(_outcome_sig(-1.0), "SL_HIT")

    sc2 = _stub_scanner(tmp_path, monkeypatch)
    sc2._load_loss_streaks()
    assert sc2._loss_streaks[("MONUSDT", "MOVER_TREND_PULLBACK", "LONG")] == 2


def test_loss_streak_shadow_does_not_extend_cooldown(tmp_path, monkeypatch):
    """Flag turned OFF from ops: streak ≥2 shadow-logs, cooldown stays flat."""
    import time as _time
    _tunables(loss_streak_escalation_enabled=False)
    sc = _stub_scanner(tmp_path, monkeypatch)
    sc.on_signal_lifecycle_outcome(_outcome_sig(-1.0), "SL_HIT")
    sc.on_signal_lifecycle_outcome(_outcome_sig(-1.0), "SL_HIT")

    key = ("MONUSDT", "MOVER_TREND_PULLBACK", "LONG")
    remaining = sc._dispatch_cooldown[key] - _time.time()
    assert remaining <= 3600 + 5  # flat 1h SL extension, not doubled
    assert sc._path_funnel_counters["loss_streak_shadow:MOVER_TREND_PULLBACK"] == 1


def test_loss_streak_escalates_when_enabled(tmp_path, monkeypatch):
    import time as _time
    _tunables(loss_streak_escalation_enabled=True)
    sc = _stub_scanner(tmp_path, monkeypatch)
    sc.on_signal_lifecycle_outcome(_outcome_sig(-1.0), "SL_HIT")   # streak 1 → 1h
    sc.on_signal_lifecycle_outcome(_outcome_sig(-1.0), "SL_HIT")   # streak 2 → 2h

    key = ("MONUSDT", "MOVER_TREND_PULLBACK", "LONG")
    remaining = sc._dispatch_cooldown[key] - _time.time()
    assert 7200 - 5 <= remaining <= 7200 + 5
    assert sc._path_funnel_counters["loss_streak_escalated:MOVER_TREND_PULLBACK"] == 1


def test_loss_streak_escalation_capped(tmp_path, monkeypatch):
    import time as _time
    _tunables(loss_streak_escalation_enabled=True, loss_streak_cap_hours=4.0)
    sc = _stub_scanner(tmp_path, monkeypatch)
    for _ in range(6):
        sc.on_signal_lifecycle_outcome(_outcome_sig(-1.0), "SL_HIT")

    key = ("MONUSDT", "MOVER_TREND_PULLBACK", "LONG")
    remaining = sc._dispatch_cooldown[key] - _time.time()
    assert remaining <= 4 * 3600 + 5  # capped, not 2^5 hours


async def test_active_dup_guard_blocks_when_enabled(tmp_path, monkeypatch):
    _tunables(active_dup_guard_enabled=True)
    sc = _stub_scanner(tmp_path, monkeypatch)
    open_dup = _make_signal()
    sc.router.active_signals = {open_dup.signal_id: open_dup}

    incoming = _make_signal()
    incoming.signal_id = "RUNNER-MONUSDT-002"
    ok = await sc._enqueue_signal(incoming)

    assert ok is False
    assert sc._suppression_counters["active_dup:MOVER_TREND_PULLBACK"] == 1


async def test_active_dup_guard_shadow_lets_signal_through(tmp_path, monkeypatch):
    """Flag turned OFF from ops: the duplicate is shadow-counted but still
    dispatches."""
    _tunables(active_dup_guard_enabled=False)
    sc = _stub_scanner(tmp_path, monkeypatch)
    open_dup = _make_signal()
    sc.router.active_signals = {open_dup.signal_id: open_dup}
    sc.signal_queue = MagicMock()
    sc.signal_queue.put = AsyncMock(return_value=True)

    incoming = _make_signal()
    incoming.signal_id = "RUNNER-MONUSDT-002"
    ok = await sc._enqueue_signal(incoming)

    assert ok is True
    assert sc._suppression_counters["active_dup_shadow:MOVER_TREND_PULLBACK"] == 1
    sc.signal_queue.put.assert_awaited()


async def test_no_dup_no_counters(tmp_path, monkeypatch):
    _tunables(active_dup_guard_enabled=True)
    sc = _stub_scanner(tmp_path, monkeypatch)
    sc.signal_queue = MagicMock()
    sc.signal_queue.put = AsyncMock(return_value=True)

    incoming = _make_signal()
    ok = await sc._enqueue_signal(incoming)

    assert ok is True
    assert not any(k.startswith("active_dup") for k in sc._suppression_counters)


# ---------------------------------------------------------------------------
# Evaluator live/shadow runtime switch
# ---------------------------------------------------------------------------

def test_mover_path_live_reads_tunable():
    from src.channels.scalp import ScalpChannel

    # Uninitialised registry → env boot default (True).
    assert ScalpChannel._mover_path_live("mover_avwap_scalp_live", True) is True
    _tunables(mover_avwap_scalp_live=False)
    assert ScalpChannel._mover_path_live("mover_avwap_scalp_live", True) is False
    # MVRTP untouched by the AVWAP flip.
    assert ScalpChannel._mover_path_live("mover_trend_pullback_live", True) is True
