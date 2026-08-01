"""MOVER_AVWAP_SCALP — anchored-VWAP continuation scalp for movers.

Drives the evaluator end-to-end (real ScalpChannel + builder) to prove it
fires with its own identity on a confirmed mover pullback-to-AVWAP, and that
the slope/leg/shadow gates reject correctly.
"""
from __future__ import annotations

import numpy as np
import pytest

from src.channels.scalp import ScalpChannel
from src.smc import Direction


def _short_mover_candles():
    """15m series: swing high early → ~8% down-leg → pullback that tags the
    anchored VWAP → final bar rejects back below it on a volume spike."""
    n = 60
    close = np.zeros(n)
    for i in range(n):
        if i < 13:
            close[i] = 110 - i * 0.2          # swing-high region (leg origin)
        elif i < 53:
            close[i] = 107.4 - (i - 13) * 0.28  # the down-leg
        elif i < 59:
            close[i] = 96.2 + (i - 53) * 1.05   # pullback up toward AVWAP
        else:
            close[i] = 101.0                    # reject bar: below AVWAP + prev
    close[58] = 102.2                            # prev bar tags AVWAP from below
    high = close + 0.5
    low = close - 0.5
    vol = np.ones(n) * 1000.0
    vol[-1] = 3000.0                             # reclaim-bar volume spike
    return {"15m": {"open": close - 0.1, "high": high, "low": low,
                    "close": close, "volume": vol}}


_IND = {"15m": {"atr_last": 0.5}}
_SMC = {"pair_profile": None, "regime_context": None}


def test_fires_short_with_own_identity_and_tradeable_sl():
    ch = ScalpChannel()
    sig = ch._evaluate_mover_avwap_scalp(
        "ABCUSDT", _short_mover_candles(), _IND, _SMC, 0.001, 50_000_000,
        regime="TRENDING_DOWN",
    )
    assert sig is not None, f"expected a signal, got reject {ch._active_no_signal_reason!r}"
    assert sig.setup_class == "MOVER_AVWAP_SCALP"   # identity preserved
    assert sig.direction == Direction.SHORT
    assert sig.entry_trigger == "avwap_reclaim"
    sl_dist_pct = abs(sig.stop_loss - sig.entry) / sig.entry * 100.0
    assert sl_dist_pct < 3.0                        # under the path's max SL


def test_insufficient_candles_rejects():
    ch = ScalpChannel()
    short = {"15m": {k: np.ones(10) for k in ("open", "high", "low", "close", "volume")}}
    assert ch._evaluate_mover_avwap_scalp("X", short, {}, {}, 0.001, 1e6) is None
    assert ch._active_no_signal_reason == "insufficient_candles"


def test_flat_market_rejects_no_mover_leg():
    ch = ScalpChannel()
    n = 60
    close = np.full(n, 100.0) + np.random.default_rng(0).normal(0, 0.05, n)
    flat = {"15m": {"open": close, "high": close + 0.3, "low": close - 0.3,
                    "close": close, "volume": np.ones(n) * 1000.0}}
    sig = ch._evaluate_mover_avwap_scalp("X", flat, _IND, _SMC, 0.001, 50_000_000,
                                         regime="TRENDING_DOWN")
    assert sig is None
    assert ch._active_no_signal_reason == "no_mover_leg"


def test_shadow_mode_suppresses_when_disabled():
    """Shadowed via the ops runtime tunable (2026-07-09 — the live/shadow
    switch is ops-controlled; the env flag is only the boot default)."""
    from src import runtime_tunables as rt
    from tests.test_mover_runner_exit import _FakeFirestore

    rt.reset_for_test()
    try:
        rt.init_runtime_tunables(_FakeFirestore())
        rt.set_values({"mover_avwap_scalp_live": False})
        ch = ScalpChannel()
        sig = ch._evaluate_mover_avwap_scalp(
            "ABCUSDT", _short_mover_candles(), _IND, _SMC, 0.001, 50_000_000,
            regime="TRENDING_DOWN",
        )
        assert sig is None
        assert ch._active_no_signal_reason == "shadow_mode"
    finally:
        rt.reset_for_test()


def test_evaluator_method_exists():
    ch = ScalpChannel()
    assert callable(getattr(ch, "_evaluate_mover_avwap_scalp", None))


# --------------------------------------------------------------------------- #
# Entry-feature stamp (2026-08-01)
# --------------------------------------------------------------------------- #


class TestEntryFeatureStamp:
    """The stamp reads; it must never be able to change what emits.

    Same safety argument as MVRTP's, and the same method: drive the real
    evaluator both ways and compare the emitted signal. A mock whose keys we
    chose cannot verify a contract we might have got wrong.

    The content assertions are the other half. This path's blindness is not
    MVRTP's — it already gates on volume and AVWAP slope — so what has to be on
    the row is *where in the move* the entry was taken: the anchor's age, how far
    the leg had already run, and how many times price had come back to the
    anchor before this one.
    """

    def _emit(self):
        return ScalpChannel()._evaluate_mover_avwap_scalp(
            "ABCUSDT", _short_mover_candles(), _IND, _SMC, 0.001, 50_000_000,
            regime="TRENDING_DOWN",
        )

    @staticmethod
    def _shape(sig):
        return (
            sig.direction, round(sig.entry, 10), round(sig.stop_loss, 10),
            round(sig.tp1, 10), round(sig.tp2, 10), round(sig.tp3, 10),
            round(sig.confidence, 10), sig.entry_trigger,
            round(sig.original_sl_distance, 10),
        )

    def test_the_emitted_signal_is_identical_with_stamping_on_or_off(self):
        import os

        from src import entry_features as ef

        led = ef.EntryFeatureLedger(path="")
        ef.reset_ledger(led)
        try:
            on = self._emit()
            assert on is not None
            stamped = len(led.rows())

            prev = os.environ.get("ENTRY_FEATURES_ENABLED")
            os.environ["ENTRY_FEATURES_ENABLED"] = "false"
            try:
                from src import runtime_tunables as rt

                rt.reset_for_test()
                off = self._emit()
            finally:
                if prev is None:
                    os.environ.pop("ENTRY_FEATURES_ENABLED", None)
                else:
                    os.environ["ENTRY_FEATURES_ENABLED"] = prev

            assert off is not None
            assert self._shape(on) == self._shape(off), (
                "the entry-feature stamp changed the emitted signal — it is "
                "supposed to be a pure read"
            )
            assert stamped == 1
        finally:
            ef.reset_ledger(None)

    def test_a_raising_stamp_costs_the_measurement_not_the_trade(self, monkeypatch):
        """A broken measurement must never cost a signal."""
        from src import entry_features as ef

        def _boom(**_kwargs):
            raise RuntimeError("capture exploded")

        monkeypatch.setattr(ef, "capture", _boom)
        assert self._emit() is not None

    def test_it_records_where_in_the_move_the_entry_was_taken(self):
        """The variables this path computes and then never consults.

        The anchor is calculated to produce a VWAP and its *age* is discarded;
        the leg's size is tested against a floor and then dropped; the number of
        prior returns to the anchor is never counted at all. A first pullback
        into a young leg and a fourth into an old one are the same object to the
        evaluator, and until now to every artifact downstream of it.
        """
        from src import entry_features as ef

        led = ef.EntryFeatureLedger(path="")
        ef.reset_ledger(led)
        try:
            sig = self._emit()
            assert sig is not None
            rows = led.rows()
            assert len(rows) == 1
            row = rows[0]

            assert row["setup_class"] == "MOVER_AVWAP_SCALP"
            assert row["tf_name"] == "15m"
            assert row["entry_ref_name"] == "avwap_anchored"

            # Path-specific: present, and actually measured rather than defaulted.
            assert row["anchor_age_bars"] > 0
            assert row["leg_move_pct"] > 0
            assert row["avwap_touches_in_leg"] is not None
            assert row["avwap_slope_pct"] is not None
            # The exact ratio `vol_ok` thresholds on — the fixture spikes the
            # trigger bar to 3x, so this must read well above 1.
            assert row["vol_ratio_at_trigger"] > 1.0

            # TP1 is `close +/- sl_dist` on this path, so the designed geometry
            # is 1.0R by construction. Stamped anyway, so the constant is a fact
            # in the data rather than something a reader must know from source.
            assert row["tp1_r_multiple"] == pytest.approx(1.0, rel=1e-6)

            # ...and no other path's questions leaked onto this row.
            assert "h1_trend_sep_atr" not in row
            assert "rsi_at_entry" not in row
        finally:
            ef.reset_ledger(None)
