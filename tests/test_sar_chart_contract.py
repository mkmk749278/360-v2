"""Cross-repo pin: the Lumin chart draws the SAR this engine measures.

Added 2026-07-28 with the Parabolic SAR chart study in ``mkmk749278/lumin-app``
(``lib/features/charts/indicators.dart::parabolicSar``). That Dart function is a
line-for-line port of :func:`src.sar_exit_shadow.parabolic_sar`, and a port with
nothing holding it to its original is a copy that drifts.

The failure mode this exists to prevent is the one this codebase has already
paid for in other shapes (#817): **a cross-repo contract that no test on the
producing side pins fails silently and looks fine.** Nobody would see a
divergence here. The app would keep drawing dots, the engine would keep
stamping alignment, and the owner — reading a chart to sanity-check what the
SAR study reported — would be comparing two different indicators with no
symptom anywhere. So the producing side pins it: change ``parabolic_sar``'s
seeding, its two-bar clamp, or its reversal branch and this test goes red,
naming the app file that must change with it.

``HIGHS``/``LOWS``/``EXPECTED`` below are byte-identical to the vector in the
app's ``test/features/charts/indicators_test.dart``. The series is synthetic and
deliberately flips the SAR twice (bar 14 bearish, bar 29 back to bullish) — a
single-trend series never exercises the reversal branch, which is the half of
the algorithm worth pinning. ``EXPECTED`` was generated from *this* function, so
this test asserts the app matches the engine, never the reverse.
"""
from __future__ import annotations

import pytest

from src.sar_exit_shadow import parabolic_sar

# The app's default step / max step (``kSarStep`` / ``kSarMaxStep``) are these
# config defaults. They travel together or the vector below means nothing.
_STEP = 0.02
_MAX_STEP = 0.2

HIGHS = [
    100.8, 102.0454, 103.2632, 104.4266, 105.5102, 106.4911, 107.3488,
    108.0667, 108.6316, 109.035, 109.2724, 109.3444, 109.2558, 109.016,
    108.6385, 108.1408, 107.5436, 106.8704, 106.1467, 105.3996, 104.6566,
    103.9453, 103.2923, 102.7227, 102.2592, 101.9215, 101.7259, 101.6848,
    101.8063, 102.0938, 102.5465, 103.1585, 103.92, 104.8168, 105.8308,
    106.941, 108.1235, 109.3525, 110.6008, 111.8407,
]
LOWS = [
    99.2, 100.4454, 101.6632, 102.8266, 103.9102, 104.8911, 105.7488,
    106.4667, 107.0316, 107.435, 107.6724, 107.7444, 107.6558, 107.416,
    107.0385, 106.5408, 105.9436, 105.2704, 104.5467, 103.7996, 103.0566,
    102.3453, 101.6923, 101.1227, 100.6592, 100.3215, 100.1259, 100.0848,
    100.2063, 100.4938, 100.9465, 101.5585, 102.32, 103.2168, 104.2308,
    105.341, 106.5235, 107.7525, 109.0008, 110.2407,
]
EXPECTED = [
    None, 99.2, 99.2, 99.362528, 99.66637232, 100.1338785344,
    100.76960068096, 101.55910459924479, 102.47016795535052,
    103.45599708249443, 104.46021760764543, 105.42265408611635,
    106.20700326889308, 106.83448261511445, 109.3444, 109.298282,
    109.18798272, 108.99331975679999, 108.695486176256, 108.2806075586304,
    107.74288665159474, 107.08680652037148, 106.32816547711204,
    105.49370969123187, 104.6195077529855, 103.8274462023884,
    103.12625696191073, 102.52618556952858, 102.03790845562287, 100.0848,
    100.12498000000001, 100.22184080000001, 100.39804035200001,
    100.67979712384, 101.093497411456, 101.66197372208129,
    102.4010374009899, 103.31663141683153, 104.40308776180186,
    105.64263020944149,
]

_APP_FILE = "lumin-app lib/features/charts/indicators.dart::parabolicSar"


class TestChartPortContract:
    """The vector the Lumin chart's Dart port is held to."""

    def test_vector_reproduces_bar_for_bar(self):
        out = parabolic_sar(HIGHS, LOWS, _STEP, _MAX_STEP)
        assert len(out) == len(EXPECTED)
        for i, want in enumerate(EXPECTED):
            got = out[i]
            if want is None:
                assert got is None, (
                    f"bar {i} gained a level the pinned vector does not have; "
                    f"update {_APP_FILE} and its test in the same change"
                )
            else:
                assert got is not None, f"bar {i} lost its level"
                assert got == pytest.approx(want, abs=1e-9), (
                    f"SAR changed at bar {i}: {got} != {want}. This is a "
                    f"cross-repo contract — {_APP_FILE} draws this series to "
                    f"users and must be updated in the same change"
                )

    def test_vector_actually_exercises_both_reversals(self):
        """A vector that never flips would pin only half the algorithm."""
        out = parabolic_sar(HIGHS, LOWS, _STEP, _MAX_STEP)
        bearish = [
            i for i, v in enumerate(out) if v is not None and v > HIGHS[i]
        ]
        assert bearish == list(range(14, 29)), (
            "the pinned series no longer contains exactly one bearish leg — "
            "the reversal branch is what this vector exists to cover"
        )
        # ...and it returns to bullish afterwards rather than simply ending.
        assert out[29] is not None and out[29] < LOWS[29]
        assert out[-1] is not None and out[-1] < LOWS[-1]

    def test_step_defaults_match_the_config_the_app_mirrors(self):
        from config import SAR_EXIT_SHADOW_MAX_STEP, SAR_EXIT_SHADOW_STEP

        assert SAR_EXIT_SHADOW_STEP == _STEP
        assert SAR_EXIT_SHADOW_MAX_STEP == _MAX_STEP

    def test_bar_minutes_match_the_timeframe_the_app_discloses(self):
        """The app's ``kSarStudyTf`` is '15m' and its caption says so.

        If the study ever moves off 15m, the app's caption starts telling users
        the wrong timeframe — silently, since the string is a constant there.
        """
        from config import SAR_EXIT_SHADOW_BAR_MINUTES

        assert SAR_EXIT_SHADOW_BAR_MINUTES == 15, (
            "the app discloses '15m' as the study timeframe "
            "(lumin-app lib/features/charts/indicators.dart::kSarStudyTf); "
            "change both together"
        )
