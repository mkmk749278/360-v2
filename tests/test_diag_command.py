"""Tests for the /diag Telegram admin command + TelegramBot.send_document."""

from __future__ import annotations

from collections import Counter
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.commands import CommandHandler


ADMIN_CHAT_ID = "710718010"
USER_CHAT_ID = "999999"


def _make_handler(**kwargs) -> CommandHandler:
    telegram = MagicMock()
    telegram.send_message = AsyncMock(return_value=True)
    telegram.send_document = AsyncMock(return_value=True)

    defaults = dict(
        telegram=telegram,
        telemetry=MagicMock(),
        pair_mgr=MagicMock(),
        router=MagicMock(active_signals={}),
        data_store=MagicMock(),
        signal_queue=MagicMock(),
        signal_history=[],
        paused_channels=set(),
        confidence_overrides={},
        scanner=MagicMock(spec=[]),  # bare scanner; per-test we attach attrs
        ws_spot=None,
        ws_futures=None,
        tasks=[],
        boot_time=0.0,
        free_channel_limit=2,
        alert_subscribers=set(),
    )
    defaults.update(kwargs)
    return CommandHandler(**defaults)


def _stub_scanner_with_chartist_eye(level_count: int = 10, history_count: int = 20):
    """Build a Scanner-shaped mock that has all chartist-eye sub-objects."""
    scanner = MagicMock()
    # LevelBook
    scanner.level_book = MagicMock()
    scanner.level_book._levels = {
        f"PAIR{i}USDT": [MagicMock(score=10.0 + i)] * 5 for i in range(level_count)
    }
    scanner.level_book._refresh_ts = {
        f"PAIR{i}USDT": 1700000000.0 + i for i in range(level_count)
    }
    scanner.level_book.stats = MagicMock(
        return_value={"total": 5, "support": 2, "resistance": 3, "round_numbers": 1, "from_1d": 1, "from_4h": 2, "from_1h": 2}
    )
    # Volume profile stores
    scanner.volume_profile_store = MagicMock()
    scanner.volume_profile_store._results = {f"PAIR{i}USDT": MagicMock() for i in range(3)}
    scanner.volume_profile_store.stats = MagicMock(
        return_value={"poc": 100.0, "vah": 102.0, "val": 98.0, "total_volume": 1000.0, "value_area_width_pct": 4.0}
    )
    scanner.volume_profile_store_macro = MagicMock()
    scanner.volume_profile_store_macro._results = {f"PAIR{i}USDT": MagicMock() for i in range(2)}
    scanner.volume_profile_store_macro.stats = MagicMock(
        return_value={"poc": 90.0, "vah": 95.0, "val": 85.0, "total_volume": 5000.0, "value_area_width_pct": 11.0}
    )
    # Structure tracker
    scanner.structure_tracker = MagicMock()
    bull_state = MagicMock(state="BULL_LEG", confidence=0.75)
    bear_state = MagicMock(state="BEAR_LEG", confidence=0.85)
    range_state = MagicMock(state="RANGE", confidence=0.5)
    scanner.structure_tracker._state = {
        ("BTCUSDT", "4h"): bull_state,
        ("ETHUSDT", "4h"): bear_state,
        ("SOLUSDT", "4h"): range_state,
    }
    # Scalp channel with MA-cross cooldown
    scalp_ch = MagicMock()
    scalp_ch._ma_cross_last_fire_ts = {
        ("BTCUSDT", "LONG"): 1700000000.0,
        ("ETHUSDT", "SHORT"): 1700001000.0,
    }
    scanner.channels = [scalp_ch]
    # Suppression counters
    scanner._suppression_counters = {
        "mtf_semantic_fail:360_SCALP:reclaim_retest": 12,
        "score_below50:360_SCALP": 4,
        "candidate_reached_scoring:SR_FLIP_RETEST": 6,
    }
    return scanner


# ---------------------------------------------------------------------------
# /diag command — basic dispatch
# ---------------------------------------------------------------------------


class TestDiagCommand:
    @pytest.mark.asyncio
    async def test_diag_admin_only(self):
        handler = _make_handler()
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", USER_CHAT_ID)
        # Non-admin: no document upload, no diag content.
        assert not handler._telegram.send_document.called

    @pytest.mark.asyncio
    async def test_diag_uploads_document_when_available(self):
        handler = _make_handler(scanner=_stub_scanner_with_chartist_eye())
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        # send_document was called once with reasonable args.
        handler._telegram.send_document.assert_called_once()
        call = handler._telegram.send_document.call_args
        kwargs = call.kwargs
        assert kwargs["filename"].startswith("chartist_eye_diag_")
        assert kwargs["filename"].endswith(".txt")
        assert isinstance(kwargs["document"], bytes)
        body = kwargs["document"].decode("utf-8")
        # Sanity: each section header present.
        for header in (
            "LEVEL BOOK",
            "VOLUME PROFILE",
            "STRUCTURE TRACKER",
            "MA-CROSS COOLDOWN",
            "ACTIVE SIGNAL FLAGS",
            "RECENT TERMINAL FLAGS",
            "LAST SUPPRESSION SUMMARY",
            "WIRING HEALTH",
        ):
            assert header in body, f"missing section: {header}"

    @pytest.mark.asyncio
    async def test_diag_reports_chartist_eye_present(self):
        handler = _make_handler(scanner=_stub_scanner_with_chartist_eye())
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        body = handler._telegram.send_document.call_args.kwargs["document"].decode("utf-8")
        assert "level_book present:          True" in body
        assert "volume_profile_store present: True" in body
        assert "volume_profile_store_macro present: True" in body
        assert "structure_tracker present:   True" in body
        assert "ScalpChannel + MA-cross cooldown registry: True" in body

    @pytest.mark.asyncio
    async def test_diag_reports_chartist_eye_absent_when_old_engine(self):
        """If the running engine predates the chartist-eye PRs, /diag must
        still produce a report and call out the missing pieces."""
        # `spec=[]` means every getattr raises AttributeError → the
        # ``getattr(scanner, X, None)`` fallback returns None as it would
        # on a real pre-PR engine.
        old_scanner = MagicMock(spec=[])
        # We do need `channels` (non-iterable would crash the dispatcher).
        # Manually attach an empty list and an empty suppression dict.
        old_scanner.channels = []
        old_scanner._suppression_counters = {}
        handler = _make_handler(scanner=old_scanner)
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        body = handler._telegram.send_document.call_args.kwargs["document"].decode("utf-8")
        # Wiring-health section calls out every absent piece.
        assert "level_book present:          False" in body
        assert "structure_tracker present:   False" in body

    @pytest.mark.asyncio
    async def test_diag_warns_when_no_confluence_in_recent_history(self):
        history = []
        for i in range(10):
            sig = MagicMock()
            sig.soft_gate_flags = "VWAP,OI"  # no CONFLUENCE/STRUCT_ALIGN
            history.append(sig)
        handler = _make_handler(
            scanner=_stub_scanner_with_chartist_eye(),
            signal_history=history,
        )
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        body = handler._telegram.send_document.call_args.kwargs["document"].decode("utf-8")
        assert "NO CONFLUENCE bonuses across" in body
        assert "NO STRUCT_ALIGN bonuses across" in body

    @pytest.mark.asyncio
    async def test_diag_quiet_when_confluence_present(self):
        history = []
        for i in range(10):
            sig = MagicMock()
            sig.soft_gate_flags = "CONFLUENCE×2,STRUCT_ALIGN:BULL_LEG"
            history.append(sig)
        handler = _make_handler(
            scanner=_stub_scanner_with_chartist_eye(),
            signal_history=history,
        )
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        body = handler._telegram.send_document.call_args.kwargs["document"].decode("utf-8")
        # Warning text should NOT appear when all 10 history rows have the flag.
        assert "NO CONFLUENCE bonuses across" not in body
        assert "NO STRUCT_ALIGN bonuses across" not in body

    @pytest.mark.asyncio
    async def test_diag_includes_active_flag_distribution(self):
        active = {
            "id1": MagicMock(soft_gate_flags="CONFLUENCE×3,VWAP"),
            "id2": MagicMock(soft_gate_flags="STRUCT_ALIGN:BULL_LEG"),
            "id3": MagicMock(soft_gate_flags="OI"),
        }
        scanner = _stub_scanner_with_chartist_eye()
        router = MagicMock()
        router.active_signals = active
        handler = _make_handler(scanner=scanner, router=router)
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        body = handler._telegram.send_document.call_args.kwargs["document"].decode("utf-8")
        assert "Active signals: 3" in body
        # Counter stringification has key=count format.
        assert "CONFLUENCE" in body
        assert "STRUCT_ALIGN" in body

    @pytest.mark.asyncio
    async def test_diag_falls_back_to_text_when_send_document_fails(self):
        handler = _make_handler(scanner=_stub_scanner_with_chartist_eye())
        # Force send_document to return False.
        handler._telegram.send_document = AsyncMock(return_value=False)
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        # Fallback path: a send_message reply containing the body.
        handler._telegram.send_message.assert_called()
        last_call = handler._telegram.send_message.call_args_list[-1]
        text = last_call[0][1]
        assert "Document upload failed" in text or "LEVEL BOOK" in text


# ---------------------------------------------------------------------------
# Self-diagnose enhancements: boot/uptime, threshold table, history timestamps
# ---------------------------------------------------------------------------


class TestDiagSelfDiagnose:
    """The /diag report must answer:
    - When did the running build boot?
    - What is each channel's effective min_confidence (incl. overrides)?
    - Are recent history signals pre- or post-deploy?
    """

    @pytest.mark.asyncio
    async def test_engine_boot_and_uptime_section_present(self):
        from datetime import datetime, timezone
        boot_ts = (datetime(2026, 5, 6, 10, 0, 0, tzinfo=timezone.utc).timestamp())
        handler = _make_handler(
            scanner=_stub_scanner_with_chartist_eye(),
            boot_time=boot_ts,
        )
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        body = handler._telegram.send_document.call_args.kwargs["document"].decode("utf-8")
        assert "--- ENGINE ---" in body
        assert "Boot:" in body
        assert "2026-05-06" in body
        assert "Uptime:" in body

    @pytest.mark.asyncio
    async def test_threshold_table_lists_every_channel(self):
        scanner = _stub_scanner_with_chartist_eye()
        # Stub channels with config.name + config.min_confidence
        ch_main = MagicMock()
        ch_main.config = MagicMock(name="360_SCALP", min_confidence=65)
        ch_main.config.name = "360_SCALP"
        ch_main._ma_cross_last_fire_ts = {}
        ch_fvg = MagicMock()
        ch_fvg.config = MagicMock(name="360_SCALP_FVG", min_confidence=78)
        ch_fvg.config.name = "360_SCALP_FVG"
        scanner.channels = [ch_main, ch_fvg]
        handler = _make_handler(scanner=scanner)
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        body = handler._telegram.send_document.call_args.kwargs["document"].decode("utf-8")
        assert "EFFECTIVE THRESHOLDS PER CHANNEL" in body
        assert "360_SCALP: 65" in body
        assert "360_SCALP_FVG: 78" in body

    @pytest.mark.asyncio
    async def test_threshold_table_shows_override_when_set(self):
        scanner = _stub_scanner_with_chartist_eye()
        ch = MagicMock()
        ch.config = MagicMock(min_confidence=65)
        ch.config.name = "360_SCALP"
        ch._ma_cross_last_fire_ts = {}
        scanner.channels = [ch]
        handler = _make_handler(
            scanner=scanner,
            confidence_overrides={"360_SCALP": 80},
        )
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        body = handler._telegram.send_document.call_args.kwargs["document"].decode("utf-8")
        # Active overrides surfaced.
        assert "Active /confidence overrides: {'360_SCALP': 80}" in body
        # Channel line shows override + default.
        assert "360_SCALP: 80 (override; default 65)" in body

    @pytest.mark.asyncio
    async def test_history_timestamp_range_when_present(self):
        from datetime import datetime, timezone
        boot_ts = datetime(2026, 5, 6, 10, 0, 0, tzinfo=timezone.utc).timestamp()
        history = []
        for i, ts_offset in enumerate([-7200, -3600, -1800, 600, 1200]):
            sig = MagicMock()
            sig.timestamp = datetime.fromtimestamp(
                boot_ts + ts_offset, tz=timezone.utc,
            )
            sig.soft_gate_flags = ""
            history.append(sig)
        handler = _make_handler(
            scanner=_stub_scanner_with_chartist_eye(),
            signal_history=history,
            boot_time=boot_ts,
        )
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        body = handler._telegram.send_document.call_args.kwargs["document"].decode("utf-8")
        assert "Timestamp range:" in body
        assert "Pre-deploy: 3 signals; post-deploy: 2 signals" in body

    @pytest.mark.asyncio
    async def test_warning_suppressed_when_only_pre_deploy_signals(self):
        """If every history signal predates boot_ts, the ⚠ warning shouldn't
        fire — instead an info note explains why."""
        from datetime import datetime, timezone
        boot_ts = datetime(2026, 5, 6, 10, 0, 0, tzinfo=timezone.utc).timestamp()
        history = []
        for ts_offset in (-7200, -3600, -1800, -900, -600):
            sig = MagicMock()
            sig.timestamp = datetime.fromtimestamp(boot_ts + ts_offset, tz=timezone.utc)
            sig.soft_gate_flags = ""
            history.append(sig)
        handler = _make_handler(
            scanner=_stub_scanner_with_chartist_eye(),
            signal_history=history,
            boot_time=boot_ts,
        )
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        body = handler._telegram.send_document.call_args.kwargs["document"].decode("utf-8")
        assert "NO CONFLUENCE bonuses across" not in body
        assert "All recent signals predate the running build" in body

    @pytest.mark.asyncio
    async def test_warning_fires_when_post_deploy_signals_present_and_no_flags(self):
        from datetime import datetime, timezone
        boot_ts = datetime(2026, 5, 6, 10, 0, 0, tzinfo=timezone.utc).timestamp()
        # 10 post-deploy signals, all with no chartist-eye flags
        history = []
        for i in range(10):
            sig = MagicMock()
            sig.timestamp = datetime.fromtimestamp(boot_ts + 60 * (i + 1), tz=timezone.utc)
            sig.soft_gate_flags = "VWAP,OI"
            history.append(sig)
        handler = _make_handler(
            scanner=_stub_scanner_with_chartist_eye(),
            signal_history=history,
            boot_time=boot_ts,
        )
        with patch("src.commands.TELEGRAM_ADMIN_CHAT_ID", ADMIN_CHAT_ID):
            await handler._handle_command("/diag", ADMIN_CHAT_ID)
        body = handler._telegram.send_document.call_args.kwargs["document"].decode("utf-8")
        assert "NO CONFLUENCE bonuses across 10 post-deploy signals" in body
        assert "NO STRUCT_ALIGN bonuses across 10 post-deploy signals" in body


# ---------------------------------------------------------------------------
# TelegramBot.send_document
# ---------------------------------------------------------------------------


class TestSendDocument:
    @pytest.mark.asyncio
    async def test_send_document_no_token_returns_false(self):
        from src.telegram_bot import TelegramBot
        bot = TelegramBot()
        bot._token = ""
        ok = await bot.send_document("123", b"hello", "x.txt")
        assert ok is False

    @pytest.mark.asyncio
    async def test_send_document_success_path(self):
        from src.telegram_bot import TelegramBot
        bot = TelegramBot()
        bot._token = "T"
        # Build a fake aiohttp session with a 200 response.
        resp = MagicMock()
        resp.status = 200
        resp.text = AsyncMock(return_value="ok")
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=resp)
        cm.__aexit__ = AsyncMock(return_value=None)
        session = MagicMock()
        session.post = MagicMock(return_value=cm)
        session.closed = False
        bot._session = session

        ok = await bot.send_document("123", b"hello", "x.txt", caption="test")
        assert ok is True
        session.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_document_4xx_returns_false(self):
        from src.telegram_bot import TelegramBot
        bot = TelegramBot()
        bot._token = "T"
        resp = MagicMock()
        resp.status = 400
        resp.text = AsyncMock(return_value="bad request")
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=resp)
        cm.__aexit__ = AsyncMock(return_value=None)
        session = MagicMock()
        session.post = MagicMock(return_value=cm)
        session.closed = False
        bot._session = session

        ok = await bot.send_document("123", b"hello", "x.txt")
        assert ok is False


# ---------------------------------------------------------------------------
# confidence_gate INFO log surfaces chartist-eye contributions + flags=[]
# ---------------------------------------------------------------------------


class TestConfidenceGateLogSurfacesChartistEye:
    """The INFO-level confidence_gate log must include:
      - confluence={signed:.1f}
      - struct_align={signed:.1f}
      - flags=[<full soft_gate_flags string>]

    These are the diagnostic surface that lets ``docker compose logs |
    grep`` reveal whether the chartist-eye wiring is firing without
    needing DEBUG level enabled.
    """

    def test_truth_report_regex_matches_new_format(self):
        """Backward-compat: parser handles both old and new formats."""
        from src.runtime_truth_report import _CONFIDENCE_COMPONENT_RE
        new_line = (
            "confidence_gate BTCUSDT 360_SCALP [SR_FLIP_RETEST]: decision=filtered "
            "reason=min_confidence raw=79.6 composite=69.8 pre_soft=69.8 "
            "final=54.8 threshold=80.0 "
            "penalties(eval=0.0,gate=0.0,total=0.0,pair_analysis=0.0) "
            "adjustments(feedback=+0.0,stat_filter=+0.0,regime_transition=+0.0) "
            "components(market=20.4,execution=20.0,risk=15.2,thesis_adj=2.5) "
            "engine(smc=25.0,regime=18.0,volume=3.0,indicators=11.0,patterns=5.0,mtf=5.3) "
            "soft_penalties(vwap=0.0,kz=0.0,oi=0.0,spoof=0.0,vol_div=0.0,cluster=0.0,"
            "confluence=-3.0,struct_align=-3.0) "
            "flags=[CONFLUENCE×2,STRUCT_ALIGN:BULL_LEG]"
        )
        m = _CONFIDENCE_COMPONENT_RE.search(new_line)
        assert m is not None
        assert m.group("sp_confluence") == "-3.0"
        assert m.group("sp_struct_align") == "-3.0"
        assert m.group("flags") == "CONFLUENCE×2,STRUCT_ALIGN:BULL_LEG"

    def test_truth_report_regex_matches_legacy_format(self):
        """Old log lines (no confluence/struct_align/flags/decay) still parse."""
        from src.runtime_truth_report import _CONFIDENCE_COMPONENT_RE
        legacy_line = (
            "confidence_gate ETHUSDT 360_SCALP [TREND_PULLBACK_EMA]: decision=filtered "
            "reason=min_confidence raw=70.0 composite=65.0 pre_soft=65.0 "
            "final=50.0 threshold=65.0 "
            "penalties(eval=0.0,gate=15.0,total=15.0,pair_analysis=0.0) "
            "adjustments(feedback=+0.0,stat_filter=+0.0,regime_transition=+0.0) "
            "components(market=20.4,execution=20.0,risk=15.2,thesis_adj=0.0) "
            "engine(smc=25.0,regime=18.0,volume=3.0,indicators=11.0,patterns=5.0,mtf=5.3) "
            "soft_penalties(vwap=0.0,kz=0.0,oi=15.0,spoof=0.0,vol_div=0.0,cluster=0.0)"
        )
        m = _CONFIDENCE_COMPONENT_RE.search(legacy_line)
        assert m is not None
        # Old format → optional groups are None (parser unaware).
        assert m.group("sp_confluence") is None
        assert m.group("sp_struct_align") is None
        assert m.group("flags") is None
        assert m.group("decay") is None
        # Existing fields still extracted.
        assert m.group("sp_oi") == "15.0"

    def test_truth_report_regex_captures_decay_field(self):
        """New log lines surface ``decay={signed:.1f}`` in adjustments(...)."""
        from src.runtime_truth_report import _CONFIDENCE_COMPONENT_RE
        new_line = (
            "confidence_gate LINKUSDT 360_SCALP [SR_FLIP_RETEST]: decision=filtered "
            "reason=min_confidence raw=79.6 composite=69.8 pre_soft=69.8 "
            "final=54.8 threshold=80.0 "
            "penalties(eval=0.0,gate=0.0,total=0.0,pair_analysis=0.0) "
            "adjustments(feedback=+0.0,stat_filter=+0.0,regime_transition=+0.0,decay=-15.0) "
            "components(market=20.4,execution=20.0,risk=15.2,thesis_adj=2.5) "
            "engine(smc=25.0,regime=18.0,volume=3.0,indicators=11.0,patterns=5.0,mtf=5.3) "
            "soft_penalties(vwap=0.0,kz=0.0,oi=0.0,spoof=0.0,vol_div=0.0,cluster=0.0,"
            "confluence=+0.0,struct_align=+0.0) "
            "flags=[]"
        )
        m = _CONFIDENCE_COMPONENT_RE.search(new_line)
        assert m is not None
        assert m.group("decay") == "-15.0"
        assert m.group("sp_confluence") == "+0.0"

    def test_decay_field_explains_unaccounted_drop(self):
        """The decay value plus declared penalties should sum to composite-final."""
        # composite=69.8, final=54.8 → drop of 15.0
        # All declared penalties total=0.0 ; only decay=-15.0 explains the gap.
        from src.runtime_truth_report import _CONFIDENCE_COMPONENT_RE
        line = (
            "confidence_gate LINKUSDT 360_SCALP [SR_FLIP_RETEST]: decision=filtered "
            "reason=min_confidence raw=79.6 composite=69.8 pre_soft=69.8 "
            "final=54.8 threshold=80.0 "
            "penalties(eval=0.0,gate=0.0,total=0.0,pair_analysis=0.0) "
            "adjustments(feedback=+0.0,stat_filter=+0.0,regime_transition=+0.0,decay=-15.0) "
            "components(market=20.4,execution=20.0,risk=15.2,thesis_adj=2.5) "
            "engine(smc=25.0,regime=18.0,volume=3.0,indicators=11.0,patterns=5.0,mtf=5.3) "
            "soft_penalties(vwap=0.0,kz=0.0,oi=0.0,spoof=0.0,vol_div=0.0,cluster=0.0,"
            "confluence=+0.0,struct_align=+0.0) flags=[]"
        )
        m = _CONFIDENCE_COMPONENT_RE.search(line)
        assert m is not None
        composite = float(m.group("composite"))
        final = float(m.group("final"))
        decay = float(m.group("decay"))
        total_penalty = float(m.group("total_pen"))
        # composite - final ≈ total_penalty + |decay|
        accounted = total_penalty + abs(decay)
        unaccounted = (composite - final) - accounted
        assert abs(unaccounted) < 0.5, (
            f"After surfacing decay, unaccounted drop should be ~0. "
            f"Got {unaccounted:.2f} (composite={composite}, final={final}, "
            f"penalty={total_penalty}, decay={decay})"
        )
