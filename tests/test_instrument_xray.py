"""The instrument X-ray — driven by the real `PairInfo`, and wired end to end.

`docs/PLAN_AI_TRADE_GOVERNOR_V2.md` §8. Two days of manual analysis over nine
open signals produced one actionable finding, and it came from three numbers,
not from a model: BULLAUSDT, a micro-cap meme, **+48.6% on the day** on very
little volume, treated by the governor exactly like an $8.4B LINK.

Two things these tests hold that are easy to lose:

* the classification is **stamped and consumed by nothing** — every fact in the
  manual BULLA thesis was true and the conclusion drawn from it was wrong by
  2.3 points, so identifying an instrument is a measurement and acting on it is
  a separate question;
* absence is **named**, never zero — a pair missing from the universe is not a
  pair with no volume, and market cap is recorded as unobtainable rather than
  omitted, because an absent row reads as an ordinary instrument.
"""
from __future__ import annotations

import ast
import inspect
import pathlib

import pytest

from src import instrument_xray as xray
from src.execution import ai_governor as gov
from src.pair_manager import PairInfo


def _pair(**kw) -> PairInfo:
    """The REAL PairInfo, not a stand-in whose fields I chose."""
    base = dict(symbol="BULLAUSDT", market="futures", base_asset="BULLA",
                quote_asset="USDT")
    base.update(kw)
    return PairInfo(**base)


# ---------------------------------------------------------------------------
# The classification
# ---------------------------------------------------------------------------


def test_the_bulla_case_is_visible():
    """The instrument that prompted the module."""
    out = xray.classify("BULLAUSDT", _pair(
        volume_24h_usd=2_800_000.0, change_24h_signed_pct=48.6, is_new=True))
    assert out.readable is True
    assert out.liquidity == "altcoin"
    assert out.parabolic is True
    assert out.thin is True
    assert out.change_24h_pct == pytest.approx(48.6)


def test_a_major_reads_as_a_major():
    out = xray.classify("BTCUSDT", _pair(
        symbol="BTCUSDT", volume_24h_usd=9_000_000_000.0,
        change_24h_signed_pct=1.3, is_new=False))
    assert out.liquidity == "major"
    assert out.parabolic is False
    assert out.thin is False


def test_the_signed_change_is_read_not_the_absolute_one():
    """`volatility_24h` is deliberately absolute, and a reader taking it would
    render a token down 30% identically to one up 30% — a defect
    `pair_manager`'s own comment records having shipped once already."""
    out = xray.classify("XUSDT", _pair(
        volume_24h_usd=1_000_000.0, change_24h_signed_pct=-31.0,
        volatility_24h=31.0))
    assert out.change_24h_pct == pytest.approx(-31.0)
    assert out.parabolic is True, "a crash is as parabolic as a pump"


def test_an_unreported_move_is_none_never_false():
    """`None` is "the source did not say"; `False` is "it did not move"."""
    out = xray.classify("XUSDT", _pair(volume_24h_usd=1_000_000.0,
                                       change_24h_signed_pct=None))
    assert out.change_24h_pct is None
    assert out.parabolic is None, "unknown must not render as calm"
    assert out.reason == xray.WHY_NOT_REPORTED


def test_a_pair_outside_the_universe_is_a_named_unknown_not_a_zero():
    out = xray.classify("GHOSTUSDT", None)
    assert out.readable is False
    assert out.reason == xray.WHY_NO_PAIR
    assert out.volume_24h_usd is None and out.liquidity == "unknown"
    assert out.parabolic is None and out.thin is None


def test_market_cap_is_named_absent_rather_than_omitted():
    """The one figure no engine surface carries. Fetching it means mapping a
    Binance symbol onto a vendor coin id, which is *silently* wrong rather than
    loudly wrong — several listed tokens share the ticker BULLA. So the block
    says we cannot see it, and why."""
    out = xray.classify("BULLAUSDT", _pair(volume_24h_usd=2_800_000.0,
                                           change_24h_signed_pct=48.6))
    assert out.market_cap_usd is None
    assert out.market_cap_reason == xray.WHY_NO_VENDOR
    assert "market_cap_reason" in out.as_dict()


def test_a_raising_getter_is_counted_not_propagated():
    def boom(_symbol):
        raise RuntimeError("pair store down")

    out = xray.from_getter("XUSDT", boom)
    assert out.readable is False and out.reason == xray.WHY_NO_PAIR


def test_no_getter_is_a_named_unknown():
    assert xray.from_getter("XUSDT", None).reason == xray.WHY_NO_PAIR


def test_the_bands_match_pair_managers_own_thresholds():
    """A second opinion about a question the engine has already answered is a
    mirror, and mirrors drift."""
    from src import pair_manager as pm

    src = inspect.getsource(pm.classify_pair_tier)
    assert "500_000_000" in src and "50_000_000" in src
    assert xray.MAJOR_VOLUME_USD == 500_000_000.0
    assert xray.MIDCAP_VOLUME_USD == 50_000_000.0


# ---------------------------------------------------------------------------
# The wire
# ---------------------------------------------------------------------------


def test_the_snapshot_carries_the_instrument_block():
    from src.execution import ai_governor_menu as menu
    from src.execution import ai_governor_snapshot as snap

    class _Sig:
        signal_id = "s1"; symbol = "BULLAUSDT"; direction = "LONG"
        entry = 100.0; stop_loss = 98.0; tp1 = 104.0
        setup_class = "MOVER_TREND_PULLBACK"; entry_regime = "VOLATILE"
        original_sl_distance = 2.0

    built = snap.build_snapshot(
        signal=_Sig(), trigger_tf="15m", as_of_bar_ms=1, bars_since_entry=3,
        last_price=101.0, menu=menu.Menu(tp=(), sl=()),
        instrument={"symbol": "BULLAUSDT", "parabolic": True},
    )
    assert built.as_dict()["instrument"]["parabolic"] is True


def test_the_governor_passes_the_pair_getter_into_the_snapshot():
    """AST, not a read: a parameter accepted and dropped is the defect this
    whole item repairs."""
    tree = ast.parse(inspect.getsource(gov.sweep).lstrip())
    kwargs = {
        kw.arg for node in ast.walk(tree)
        if isinstance(node, ast.Call) for kw in node.keywords if kw.arg
    }
    assert "instrument" in kwargs, "sweep must pass the instrument block"


def test_main_hands_the_pair_universe_to_the_monitor():
    source = (pathlib.Path(__file__).resolve().parents[1] / "src" / "main.py").read_text()
    tree = ast.parse(source)
    assigns = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for t in node.targets
        if isinstance(t, ast.Attribute) and t.attr == "_pair_getter"
    ]
    assert assigns, "main.py must set monitor._pair_getter"
    assert "pair_mgr" in ast.unparse(assigns[0])


def test_the_monitor_forwards_its_pair_getter():
    from src import trade_monitor

    assert "pair_getter=self._pair_getter" in inspect.getsource(trade_monitor)
