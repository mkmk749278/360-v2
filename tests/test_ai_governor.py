"""Guards for the post-emission AI Trade Governor.

These are not coverage for its own sake. Each one is a defect this repo has
already paid for, arriving at the new lane:

* the budget that only bounded the branch doing the work (Session 137, four
  hours of auto-trade down),
* the mock whose keys the author chose, asserting an assumption back at itself
  one repo short of the reader (`zone_distance_atr`, 0 of 57 rows),
* flush without load, which deletes the window while the page reports health,
* the blended figure that moves with a refusal rate rather than a mechanism.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import pytest

from src import ai_governor_ledger, llm_client
from src.execution import ai_governor as gov
from src.execution import ai_governor_menu as menu
from src.execution import ai_governor_snapshot as snap


# ── Fakes that mirror the REAL shapes, never invented ones ──────────────────

@dataclass
class FakeSignal:
    signal_id: str = "sig-1"
    symbol: str = "ARBUSDT"
    direction: str = "LONG"
    entry: float = 100.0
    stop_loss: float = 98.0
    tp1: float = 104.0
    setup_class: str = "MOVER_TREND_PULLBACK"
    entry_regime: str = "TRENDING_UP"
    status: str = "ACTIVE"
    max_favorable_excursion_pct: float = 1.2
    max_adverse_excursion_pct: float = -0.4
    original_sl_distance: float = 2.0


@dataclass
class FakePosition:
    signal_id: str = "sig-1"
    firebase_uid: str = "uid-1"
    symbol: str = "ARBUSDT"
    side: str = "LONG"
    state: str = "OPEN"
    sl_price: float = 98.0
    filled_qty: float = 10.0
    closed_qty: float = 0.0
    tp1_order_id: int = 555
    exit_mechanism: str = ""


def _series(n: int = 60) -> Dict[str, Any]:
    """The store's REAL shape, including `open`.

    The first cut of this fixture omitted `open`, and
    `sar_live_shadow._series_with_reason` — which the governor actually calls —
    refuses a series missing any of the five arrays. A fixture that chooses a
    shape and then agrees with you about it is the `zone_distance_atr` failure;
    here the real collaborator rejected it immediately, which is what driving
    the real one buys.
    """
    base = 100.0
    opens, highs, lows, closes, times = [], [], [], [], []
    for i in range(n):
        drift = (i % 7) * 0.3
        opens.append(base + drift - 0.1)
        closes.append(base + drift)
        highs.append(base + drift + 0.6)
        lows.append(base + drift - 0.6)
        times.append(1_700_000_000_000 + i * 900_000)
    return {"open": opens, "high": highs, "low": lows,
            "close": closes, "open_time": times}


@pytest.fixture(autouse=True)
def _isolate():
    gov.reset_state_for_test()
    gov.reset_health_for_test()
    ai_governor_ledger.reset_ledger(ai_governor_ledger.GovernorLedger(path=""))
    yield
    gov.reset_state_for_test()
    gov.reset_health_for_test()
    ai_governor_ledger.reset_ledger(None)


# ── The menu is closed, and monotone by construction ────────────────────────

def _menu_for(**kw) -> menu.Menu:
    s = _series()
    return menu.build_menu(
        side=kw.get("side", "LONG"),
        entry=kw.get("entry", 100.0),
        current_sl=kw.get("current_sl", 98.0),
        current_tp1=kw.get("current_tp1", 104.0),
        highs=s["high"], lows=s["low"], closes=s["close"],
        last_price=kw.get("last_price", 101.0),
    )


def test_every_tp_candidate_is_nearer_than_the_current_target():
    """Nearer-only is what makes this arm decidable from the record at all."""
    m = _menu_for()
    current = m.lookup("tp_0")
    assert current is not None
    for cand in m.tp:
        if cand.key == "tp_0":
            continue
        assert 0 < cand.dist_pct < current.dist_pct, cand


def test_every_sl_candidate_is_tighter_than_the_current_stop():
    m = _menu_for()
    current = m.lookup("sl_0")
    assert current is not None
    for cand in m.sl:
        if cand.key == "sl_0":
            continue
        assert cand.dist_pct > current.dist_pct, cand


def test_short_side_is_signed_toward_the_trade():
    """A menu where 'nearer' inverts on a SHORT is the raw-CVD bug on the one
    path that moves real orders. The delivered book is ~50/50 by side, so this
    would never show up as an empty column."""
    m = menu.build_menu(
        side="SHORT", entry=100.0, current_sl=102.0, current_tp1=96.0,
        highs=_series()["high"], lows=_series()["low"], closes=_series()["close"],
        last_price=99.0,
    )
    assert m.lookup("tp_0").dist_pct > 0  # the target is in the trade's favour
    for cand in m.sl:
        if cand.key != "sl_0":
            assert cand.price < 102.0  # tighter for a SHORT means LOWER


def test_a_stop_already_through_the_mark_is_never_offered():
    """Binance rejects it (-2021). Offering one makes our defect surface as the
    model's mistake."""
    m = _menu_for(last_price=97.0, current_sl=95.0)
    for cand in m.sl:
        if cand.key == "sl_0":
            continue
        assert cand.price < 97.0


def test_menu_refuses_rather_than_returning_an_empty_set_on_a_short_series():
    m = menu.build_menu(
        side="LONG", entry=100.0, current_sl=98.0, current_tp1=104.0,
        highs=[1, 2], lows=[1, 2], closes=[1, 2], last_price=101.0,
    )
    assert m.refusal == menu.REFUSE_SHORT_SERIES
    # ...and still offers the mechanical stops, because the blind case is
    # exactly when a governor is most likely to want out.
    assert any(c.kind == menu.KIND_BREAKEVEN for c in m.sl)


def test_lookup_cannot_resolve_a_key_from_another_positions_menu():
    a = _menu_for(entry=100.0)
    b = _menu_for(entry=50.0, current_sl=49.0, current_tp1=52.0, last_price=50.5)
    swing_keys = [c.key for c in b.tp if c.kind == menu.KIND_SWING]
    for key in swing_keys:
        # Same key STRING, different menu object: resolution must come from the
        # position's own menu, and the governor refuses when it does not.
        assert a.lookup(key) is None or a.lookup(key).price != b.lookup(key).price


# ── Readability: unknown is never a value ───────────────────────────────────

def test_an_unreadable_field_carries_no_value_and_a_reason():
    r = snap.Readable.unknown(snap.WHY_NOT_SUBSCRIBED)
    assert r.value is None and not r.readable
    assert r.as_dict() == {"readable": False, "reason": snap.WHY_NOT_SUBSCRIBED}
    assert "value" not in r.as_dict()


def test_snapshot_reports_blindness_when_the_context_feeds_are_absent():
    s = snap.build_snapshot(
        signal=FakeSignal(), trigger_tf="15m", as_of_bar_ms=1, bars_since_entry=3,
        last_price=101.0, menu=_menu_for(),
    )
    assert s.blind_fraction() == 1.0
    assert s.as_dict()["book"]["readable"] is False


def test_r_multiple_uses_the_designed_risk_not_the_moving_stop():
    """#848: `trade_monitor` moves `sig.stop_loss` in place, so dividing by it
    reports a BE-shifted -0.1% loser as exactly -1.00R."""
    sig = FakeSignal(stop_loss=99.9, original_sl_distance=2.0)  # BE-shifted
    s = snap.build_snapshot(
        signal=sig, trigger_tf="15m", as_of_bar_ms=1, bars_since_entry=1,
        last_price=101.0, menu=_menu_for(),
    )
    assert s.r_multiple_now == pytest.approx(0.5)  # 1.0 / 2.0, not 1.0 / 0.1


# ── Parsing: a hallucinated key is harmless ─────────────────────────────────

def _result(payload: Dict[str, Any]) -> llm_client.LLMResult:
    return llm_client.LLMResult(
        status=llm_client.OK, data=payload, served_model="gemini-3.7-flash-002",
        requested_model="gemini-3.7-flash", latency_ms=900,
        usage={"input_tokens": 1200, "output_tokens": 100},
    )


def _batch() -> Dict[str, Any]:
    m = _menu_for()
    s = snap.with_menu(
        snap.build_snapshot(
            signal=FakeSignal(), trigger_tf="15m", as_of_bar_ms=1,
            bars_since_entry=2, last_price=101.0, menu=m,
        ),
        m,
    )
    return {"sig-1": (s, m)}


def test_a_key_not_in_the_menu_is_refused_and_counted():
    batch = _batch()
    out = gov.parse_verdicts(
        {"verdicts": [{"signal_id": "sig-1", "verdict": "ADJUST_TP",
                       "choice": "tp_does_not_exist", "rationale": "x"}]},
        result=_result({}), batch=batch, now=1000.0,
    )
    assert out == []
    assert gov.health()["refusals"][gov.REFUSE_UNKNOWN_CHOICE] == 1


def test_a_verdict_for_an_unknown_signal_is_refused():
    out = gov.parse_verdicts(
        {"verdicts": [{"signal_id": "somebody-elses-signal", "verdict": "MAINTAIN",
                       "rationale": "x"}]},
        result=_result({}), batch=_batch(), now=1000.0,
    )
    assert out == []


def test_an_unknown_action_is_refused_never_coerced():
    out = gov.parse_verdicts(
        {"verdicts": [{"signal_id": "sig-1", "verdict": "SELL_EVERYTHING",
                       "rationale": "x"}]},
        result=_result({}), batch=_batch(), now=1000.0,
    )
    assert out == []
    assert gov.health()["refusals"][gov.REFUSE_UNKNOWN_ACTION] == 1


def test_maintain_and_panic_carry_no_choice():
    out = gov.parse_verdicts(
        {"verdicts": [{"signal_id": "sig-1", "verdict": "MAINTAIN",
                       "choice": "tp_1", "rationale": "steady"}]},
        result=_result({}), batch=_batch(), now=1000.0,
    )
    assert len(out) == 1 and out[0][0].choice is None


def test_the_served_model_is_stamped_not_the_alias_we_asked_for():
    """A silently rotated alias would otherwise redefine every row with no diff
    in our repo."""
    out = gov.parse_verdicts(
        {"verdicts": [{"signal_id": "sig-1", "verdict": "MAINTAIN", "rationale": "x"}]},
        result=_result({}), batch=_batch(), now=1000.0,
    )
    row = out[0][0].as_row()
    assert row["served_model"] == "gemini-3.7-flash-002"
    assert row["requested_model"] == "gemini-3.7-flash"
    assert row["rate_table_version"] == llm_client.RATE_TABLE_VERSION


def test_premise_broken_is_a_closed_vocabulary():
    out = gov.parse_verdicts(
        {"verdicts": [{"signal_id": "sig-1", "verdict": "MAINTAIN", "rationale": "x",
                       "premise_broken": ["macro_regime_flip", "invented_reason"]}]},
        result=_result({}), batch=_batch(), now=1000.0,
    )
    assert out[0][0].premise_broken == ("macro_regime_flip",)
