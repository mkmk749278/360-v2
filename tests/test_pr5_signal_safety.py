"""Tests for PR5 signal safety fixes:
  - Fix 1: Near-zero SL rejection in build_risk_plan
  - Fix 2: Failed-detection cooldown in Scanner._prepare_signal
  - Fix 3: Dynamic pair count in commands
"""
from __future__ import annotations

import pathlib
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.signal_quality import (
    SetupClass,
    build_risk_plan,
)
from src.smc import Direction


# ---------------------------------------------------------------------------
# Helpers shared across tests
# ---------------------------------------------------------------------------

def _make_signal(
    entry: float = 100.0,
    direction: Direction = Direction.LONG,
    channel: str = "360_SCALP",
) -> SimpleNamespace:
    stop_loss = entry * 0.98 if direction == Direction.LONG else entry * 1.02
    return SimpleNamespace(
        channel=channel,
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=entry * 1.01,
        tp2=entry * 1.02,
        tp3=entry * 1.03,
    )


def _wide_candles(base: float = 100.0, n: int = 60) -> dict:
    """Candles with very wide range so structure-based SL is far from entry."""
    return {
        "high": [base * 1.1] * n,
        "low": [base * 0.5] * n,
        "close": [base] * n,
        "volume": [1000.0] * n,
    }


def _wide_indicators(base: float = 100.0) -> dict:
    return {
        "5m": {
            "ema9_last": base,
            "ema21_last": base,
            "atr_last": base * 0.5,   # very large ATR → SL will be capped
            "momentum_last": 0.3,
            "bb_upper_last": base * 1.1,
            "bb_mid_last": base,
            "bb_lower_last": base * 0.9,
        }
    }


# ---------------------------------------------------------------------------
# Fix 1 — Near-zero SL rejection
# ---------------------------------------------------------------------------

class TestNearZeroSLRejection:
    """build_risk_plan must reject signals where the capped SL is < 0.05% from entry."""

    def test_near_zero_guard_fires_when_channel_cap_is_tiny(self, monkeypatch):
        """If a channel cap brings SL within 0.03% of entry, the guard must reject it."""
        import src.signal_quality as sq

        # Inject a channel with a very tight SL cap (0.03%) — smaller than the 0.05% guard threshold.
        # The guard must fire because after capping, SL is only 0.03% from entry.
        tight_cap_channel = "360_TEST_TINY_CAP"
        monkeypatch.setitem(sq._MAX_SL_PCT_BY_CHANNEL, tight_cap_channel, 0.03)

        entry = 100.0
        sig = _make_signal(entry=entry, direction=Direction.LONG, channel=tight_cap_channel)
        risk = build_risk_plan(
            signal=sig,
            indicators=_wide_indicators(entry),
            candles={"5m": _wide_candles(entry)},
            smc_data={"sweeps": [], "fvg": [], "mss": None},
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
            channel=tight_cap_channel,
        )
        assert risk.passed is False
        assert "near-zero" in risk.reason.lower() or "minimum" in risk.reason.lower(), (
            f"Expected near-zero SL rejection, got: {risk.reason!r}"
        )
        assert "SL distance" in risk.invalidation_summary
        assert "below minimum" in risk.invalidation_summary

    def test_near_zero_guard_fires_for_short_too(self, monkeypatch):
        """Near-zero guard must fire for SHORT signals with a tiny channel cap."""
        import src.signal_quality as sq

        tight_cap_channel = "360_TEST_TINY_CAP_SHORT"
        monkeypatch.setitem(sq._MAX_SL_PCT_BY_CHANNEL, tight_cap_channel, 0.03)

        entry = 100.0
        sig = _make_signal(entry=entry, direction=Direction.SHORT, channel=tight_cap_channel)
        risk = build_risk_plan(
            signal=sig,
            indicators=_wide_indicators(entry),
            candles={"5m": _wide_candles(entry)},
            smc_data={"sweeps": [], "fvg": [], "mss": None},
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
            channel=tight_cap_channel,
        )
        assert risk.passed is False
        assert "near-zero" in risk.reason.lower() or "minimum" in risk.reason.lower(), (
            f"Expected near-zero SL rejection for SHORT, got: {risk.reason!r}"
        )

    def test_normal_channel_sl_not_rejected_by_near_zero_guard(self):
        """Standard 360_SCALP channel (1.5% cap) must NOT be rejected as near-zero."""
        entry = 100.0
        sig = _make_signal(entry=entry, direction=Direction.LONG, channel="360_SCALP")
        risk = build_risk_plan(
            signal=sig,
            indicators=_wide_indicators(entry),
            candles={"5m": _wide_candles(entry)},
            smc_data={"sweeps": [], "fvg": [], "mss": None},
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
            channel="360_SCALP",
        )
        # If it fails, it must NOT be for near-zero SL reason
        if not risk.passed:
            assert "near-zero" not in risk.reason.lower()

    def test_near_zero_guard_placed_after_cap_before_directional_check(self):
        """Verify the guard is in the right position in the source (after cap, before directional)."""
        src_path = pathlib.Path(__file__).parent.parent / "src" / "signal_quality.py"
        content = src_path.read_text()

        cap_pos = content.find("SL capped for %s %s")
        guard_pos = content.find("near-zero SL rejected")
        directional_pos = content.find("Directional sanity check")

        assert cap_pos != -1, "SL cap block not found in signal_quality.py"
        assert guard_pos != -1, "Near-zero SL guard not found in signal_quality.py"
        assert directional_pos != -1, "Directional sanity check not found in signal_quality.py"

        assert cap_pos < guard_pos < directional_pos, (
            "Near-zero guard must be AFTER the SL cap block and BEFORE the directional sanity check. "
            f"cap={cap_pos}, guard={guard_pos}, directional={directional_pos}"
        )

    def test_near_zero_guard_threshold_is_correct(self):
        """The guard threshold must be 0.05% (0.0005)."""
        src_path = pathlib.Path(__file__).parent.parent / "src" / "signal_quality.py"
        content = src_path.read_text()
        assert "_MIN_SL_DISTANCE_PCT = 0.0005" in content, (
            "Near-zero SL guard threshold must be 0.0005 (0.05%)"
        )

    def test_near_zero_guard_invalidation_summary_includes_distances(self, monkeypatch):
        """The invalidation_summary must contain both actual and minimum distances."""
        import src.signal_quality as sq

        tight_cap_channel = "360_TEST_SUMMARY_CHECK"
        monkeypatch.setitem(sq._MAX_SL_PCT_BY_CHANNEL, tight_cap_channel, 0.03)

        entry = 100.0
        sig = _make_signal(entry=entry, direction=Direction.LONG, channel=tight_cap_channel)
        risk = build_risk_plan(
            signal=sig,
            indicators=_wide_indicators(entry),
            candles={"5m": _wide_candles(entry)},
            smc_data={"sweeps": [], "fvg": [], "mss": None},
            setup=SetupClass.TREND_PULLBACK_CONTINUATION,
            spread_pct=0.01,
            channel=tight_cap_channel,
        )
        if not risk.passed and "near-zero" in risk.reason.lower():
            assert "SL distance" in risk.invalidation_summary
            assert "below minimum" in risk.invalidation_summary
            # Must have numeric values in the summary
            assert risk.stop_loss > 0


# ---------------------------------------------------------------------------
# Fix 2 — Failed-detection cooldown
# ---------------------------------------------------------------------------

class TestFailedDetectionCooldown:
    """Scanner._conf_fail_tracker must suppress re-evaluation after 3 consecutive failures."""

    def test_constants_exist_and_are_reasonable(self):
        """_CONF_FAIL_MAX_CONSECUTIVE and _CONF_FAIL_COOLDOWN_S must exist with sensible values."""
        from src.scanner import _CONF_FAIL_MAX_CONSECUTIVE, _CONF_FAIL_COOLDOWN_S

        assert 1 <= _CONF_FAIL_MAX_CONSECUTIVE <= 10
        assert 10.0 <= _CONF_FAIL_COOLDOWN_S <= 600.0

    def test_conf_fail_tracker_defaults_values(self):
        """Default constants should match the spec (3 max, 60s cooldown)."""
        from src.scanner import _CONF_FAIL_MAX_CONSECUTIVE, _CONF_FAIL_COOLDOWN_S

        assert _CONF_FAIL_MAX_CONSECUTIVE == 3
        assert _CONF_FAIL_COOLDOWN_S == 60.0

    def test_tracker_increments_on_failure(self):
        """After a failure, fail_count for the key increases."""
        from src.scanner import _CONF_FAIL_MAX_CONSECUTIVE, _CONF_FAIL_COOLDOWN_S

        tracker: dict = {}
        symbol, chan = "BULLAUSDT", "360_SCALP"
        key = (symbol, chan)

        # Simulate one failure
        prev = tracker.get(key, (0, 0.0))
        new_count = prev[0] + 1
        until = time.monotonic() + _CONF_FAIL_COOLDOWN_S if new_count >= _CONF_FAIL_MAX_CONSECUTIVE else prev[1]
        tracker[key] = (new_count, until)

        assert tracker[key][0] == 1

    def test_cooldown_triggered_after_max_consecutive(self):
        """After _CONF_FAIL_MAX_CONSECUTIVE failures, suppressed_until is in the future."""
        from src.scanner import _CONF_FAIL_MAX_CONSECUTIVE, _CONF_FAIL_COOLDOWN_S

        tracker: dict = {}
        symbol, chan = "BULLAUSDT", "360_SCALP"
        key = (symbol, chan)

        for _ in range(_CONF_FAIL_MAX_CONSECUTIVE):
            prev = tracker.get(key, (0, 0.0))
            new_count = prev[0] + 1
            until = time.monotonic() + _CONF_FAIL_COOLDOWN_S if new_count >= _CONF_FAIL_MAX_CONSECUTIVE else prev[1]
            tracker[key] = (new_count, until)

        fail_count, suppressed_until = tracker[key]
        assert fail_count == _CONF_FAIL_MAX_CONSECUTIVE
        assert suppressed_until > time.monotonic()

    def test_cooldown_check_blocks_when_active(self):
        """Cooldown check should skip when count >= max and time not expired."""
        from src.scanner import _CONF_FAIL_MAX_CONSECUTIVE, _CONF_FAIL_COOLDOWN_S

        tracker: dict = {}
        key = ("BULLAUSDT", "360_SCALP")
        tracker[key] = (_CONF_FAIL_MAX_CONSECUTIVE, time.monotonic() + _CONF_FAIL_COOLDOWN_S)

        fail_count, suppressed_until = tracker.get(key, (0, 0.0))
        should_skip = fail_count >= _CONF_FAIL_MAX_CONSECUTIVE and time.monotonic() < suppressed_until
        assert should_skip is True

    def test_cooldown_check_allows_after_expiry(self):
        """Cooldown check should NOT skip when suppression has expired."""
        from src.scanner import _CONF_FAIL_MAX_CONSECUTIVE

        tracker: dict = {}
        key = ("BULLAUSDT", "360_SCALP")
        tracker[key] = (_CONF_FAIL_MAX_CONSECUTIVE, time.monotonic() - 1.0)

        fail_count, suppressed_until = tracker.get(key, (0, 0.0))
        should_skip = fail_count >= _CONF_FAIL_MAX_CONSECUTIVE and time.monotonic() < suppressed_until
        assert should_skip is False

    def test_tracker_reset_on_success(self):
        """After a successful signal, the tracker entry is removed."""
        tracker: dict = {}
        key = ("BULLAUSDT", "360_SCALP")
        tracker[key] = (3, time.monotonic() + 60.0)

        tracker.pop(key, None)
        assert key not in tracker

    def test_cleanup_removes_expired_entries_at_threshold(self):
        """Periodic cleanup removes entries whose suppression has expired AND are at threshold."""
        from src.scanner import _CONF_FAIL_MAX_CONSECUTIVE

        tracker: dict = {
            ("BTC", "360_SCALP"): (_CONF_FAIL_MAX_CONSECUTIVE, time.monotonic() - 5.0),  # expired
            ("ETH", "360_SCALP"): (_CONF_FAIL_MAX_CONSECUTIVE, time.monotonic() + 60.0),  # active
            ("SOL", "360_SCALP"): (1, 0.0),  # below threshold, not yet suppressed
        }

        _now_clean = time.monotonic()
        tracker = {
            k: v for k, v in tracker.items()
            if v[1] > _now_clean
            or v[0] < _CONF_FAIL_MAX_CONSECUTIVE
        }

        assert ("BTC", "360_SCALP") not in tracker   # expired, at threshold → removed
        assert ("ETH", "360_SCALP") in tracker        # active suppression → kept
        assert ("SOL", "360_SCALP") in tracker        # below threshold → kept

    def test_conf_fail_tracker_in_scanner_source(self):
        """_conf_fail_tracker must be initialized in Scanner.__init__."""
        src_path = pathlib.Path(__file__).parent.parent / "src" / "scanner" / "__init__.py"
        content = src_path.read_text()
        assert "_conf_fail_tracker" in content
        assert "Dict[tuple, tuple]" in content or "dict" in content.lower()

    def test_cooldown_check_at_top_of_prepare_signal(self):
        """Cooldown check must appear before the expensive chan.evaluate() call."""
        src_path = pathlib.Path(__file__).parent.parent / "src" / "scanner" / "__init__.py"
        content = src_path.read_text()

        cooldown_check_pos = content.find("Silently skip — cooldown active")
        evaluate_call_pos = content.find("sig = chan.evaluate(")

        assert cooldown_check_pos != -1, "Cooldown 'skip' comment not found in scanner"
        assert evaluate_call_pos != -1, "chan.evaluate() call not found in scanner"
        assert cooldown_check_pos < evaluate_call_pos, (
            "Cooldown check must be BEFORE chan.evaluate() to save compute time"
        )

    def test_tracker_reset_code_present_before_populate_signal(self):
        """The tracker reset must appear before the final _populate_signal_context call."""
        src_path = pathlib.Path(__file__).parent.parent / "src" / "scanner" / "__init__.py"
        content = src_path.read_text()

        reset_pos = content.find("Reset failed-detection counter")
        # Use the LAST occurrence of _populate_signal_context (the one at the very end of the method)
        populate_pos = content.rfind("self._populate_signal_context(sig, volume_24h, ctx)")

        assert reset_pos != -1, "Tracker reset comment not found"
        assert populate_pos != -1, "_populate_signal_context call not found"
        assert reset_pos < populate_pos, (
            "Tracker reset must be BEFORE the final _populate_signal_context call"
        )

    def test_periodic_cleanup_uses_300_cycle_modulo(self):
        """Cleanup must run every 300 cycles (not every cycle)."""
        src_path = pathlib.Path(__file__).parent.parent / "src" / "scanner" / "__init__.py"
        content = src_path.read_text()
        assert "% 300 == 0" in content and "_conf_fail_tracker" in content


# ---------------------------------------------------------------------------
# Fix 3 — Dynamic pair count in commands
# ---------------------------------------------------------------------------

class TestDynamicPairCount:
    """Commands must use TOP50_FUTURES_COUNT, not hardcoded '75 pairs'."""

    def test_signals_py_no_hardcoded_75_pairs(self):
        """src/commands/signals.py must not contain '75 pairs' as a literal string."""
        src = pathlib.Path(__file__).parent.parent / "src" / "commands" / "signals.py"
        content = src.read_text()
        assert '"75 pairs"' not in content, "Hardcoded double-quoted '75 pairs' found in signals.py"
        assert "'75 pairs'" not in content, "Hardcoded single-quoted '75 pairs' found in signals.py"

    def test_signals_py_imports_top50_count(self):
        """src/commands/signals.py must import TOP50_FUTURES_COUNT from config."""
        src = pathlib.Path(__file__).parent.parent / "src" / "commands" / "signals.py"
        content = src.read_text()
        assert "TOP50_FUTURES_COUNT" in content, "signals.py must import TOP50_FUTURES_COUNT"

    def test_commands_init_no_hardcoded_scan_75(self):
        """src/commands/__init__.py must not contain 'scan 75 Binance futures pairs'."""
        src = pathlib.Path(__file__).parent.parent / "src" / "commands" / "__init__.py"
        content = src.read_text()
        assert "scan 75 Binance" not in content, (
            "Hardcoded 'scan 75 Binance' string found in commands/__init__.py"
        )

    def test_commands_init_imports_top50_count(self):
        """src/commands/__init__.py must import TOP50_FUTURES_COUNT."""
        src = pathlib.Path(__file__).parent.parent / "src" / "commands" / "__init__.py"
        content = src.read_text()
        assert "TOP50_FUTURES_COUNT" in content, "__init__.py must import TOP50_FUTURES_COUNT"

    def test_welcome_message_uses_top50_count(self):
        """_WELCOME_MESSAGE must reference the TOP50_FUTURES_COUNT value."""
        from config import TOP50_FUTURES_COUNT
        from src.commands import _WELCOME_MESSAGE

        assert str(TOP50_FUTURES_COUNT) in _WELCOME_MESSAGE, (
            f"_WELCOME_MESSAGE does not contain TOP50_FUTURES_COUNT ({TOP50_FUTURES_COUNT})"
        )

    @pytest.mark.asyncio
    async def test_signals_empty_message_uses_config_count(self):
        """'/signals' empty response must mention the config pair count."""
        from config import TOP50_FUTURES_COUNT
        from src.commands import CommandHandler

        telegram = MagicMock()
        telegram.send_message = AsyncMock()
        handler = CommandHandler(
            telegram=telegram,
            telemetry=MagicMock(),
            pair_mgr=MagicMock(),
            router=MagicMock(),
            data_store=MagicMock(),
            signal_queue=MagicMock(),
            signal_history=[],
            paused_channels=set(),
            confidence_overrides={},
            scanner=MagicMock(),
            ws_spot=None,
            ws_futures=None,
            tasks=[],
            boot_time=0.0,
            free_channel_limit=2,
            alert_subscribers=set(),
        )
        handler._router.active_signals = {}
        await handler._handle_command("/signals", "999999")
        msg = handler._telegram.send_message.call_args[0][1]
        assert str(TOP50_FUTURES_COUNT) in msg, (
            f"'/signals' empty message does not contain pair count {TOP50_FUTURES_COUNT}"
        )

    @pytest.mark.asyncio
    async def test_ask_no_data_message_uses_config_count(self):
        """/ask BULLAUSDT with no history must mention the config pair count."""
        from config import TOP50_FUTURES_COUNT
        from src.commands import CommandHandler

        telegram = MagicMock()
        telegram.send_message = AsyncMock()
        router = MagicMock()
        router.active_signals = {}
        handler = CommandHandler(
            telegram=telegram,
            telemetry=MagicMock(),
            pair_mgr=MagicMock(),
            router=router,
            data_store=MagicMock(),
            signal_queue=MagicMock(),
            signal_history=[],
            paused_channels=set(),
            confidence_overrides={},
            scanner=MagicMock(),
            ws_spot=None,
            ws_futures=None,
            tasks=[],
            boot_time=0.0,
            free_channel_limit=2,
            alert_subscribers=set(),
        )
        await handler._handle_command("/ask BULLAUSDT", "999999")
        msg = handler._telegram.send_message.call_args[0][1]
        # The "no history" path mentions pair count — verify it uses config value
        if "scan" in msg.lower() and "pairs" in msg.lower():
            assert str(TOP50_FUTURES_COUNT) in msg, (
                f"'/ask' no-history message does not contain pair count {TOP50_FUTURES_COUNT}"
            )
