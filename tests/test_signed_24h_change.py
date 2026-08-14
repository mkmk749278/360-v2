"""The 24h move keeps its SIGN alongside the absolute one ops ranks on.

``PairInfo.volatility_24h`` is deliberately absolute — ``_rank_pairs``
normalises by it and the mover threshold compares ``>= MOVER_PROMOTION_MIN_PCT``
against it, and both of those are magnitude questions.  Taking ``abs()`` at the
only point the sign exists meant no surface downstream could tell a pair up 30%
from one down 30%, so ops rendered a *signed* promotion stamp beside this
field's absolute value with both labelled "24h Δ%" — one row read
``top loser −15.3%`` next to ``15.3%`` (owner-visible on ops.luminapp.org,
2026-08-14).

These pin the contract on the PRODUCING side, per #817: a field one repo reads
and no repo writes fails silently and looks full.
"""
from __future__ import annotations

from src.pair_manager import PairInfo, _signed_change_pct


def test_absent_change_is_none_not_zero():
    """Absence and zero are different facts about a pair."""
    assert _signed_change_pct({}) is None
    assert _signed_change_pct({"priceChangePercent": ""}) is None
    assert _signed_change_pct({"priceChangePercent": None}) is None
    # ...and an unparseable value refuses rather than defaulting to 0.0,
    # which would render as "this pair did not move".
    assert _signed_change_pct({"priceChangePercent": "n/a"}) is None


def test_zero_is_reported_as_zero():
    """A genuine 0.00% move is a reading, and must not read as 'no data'."""
    assert _signed_change_pct({"priceChangePercent": "0.000"}) == 0.0


def test_sign_survives_both_directions():
    assert _signed_change_pct({"priceChangePercent": "-15.3"}) == -15.3
    assert _signed_change_pct({"priceChangePercent": "31.4"}) == 31.4


def test_pairinfo_defaults_to_not_reported():
    """An older construction path leaves it None rather than claiming 0%."""
    assert PairInfo(symbol="XUSDT", market="futures").change_24h_signed_pct is None


def test_absolute_and_signed_disagree_only_in_sign():
    """The two fields describe the same move, and that is the whole point.

    If these ever diverge in magnitude the page is rendering two different
    quantities under one heading, which is the defect this field repairs.
    """
    for raw in ("-15.3", "31.4", "0.0"):
        info = PairInfo(
            symbol="XUSDT",
            market="futures",
            volatility_24h=abs(float(raw)),
            change_24h_signed_pct=_signed_change_pct({"priceChangePercent": raw}),
        )
        assert info.change_24h_signed_pct is not None
        assert abs(info.change_24h_signed_pct) == info.volatility_24h


def test_snapshot_emits_the_signed_field_for_ops():
    """Ops reads this key; pin the NAME here so a rename fails loudly.

    Asserted against the module source rather than a live snapshot because the
    assembler needs a full engine — what matters is that the key ops reads is
    the key this repo writes.
    """
    import inspect
    from src.api import snapshot

    src = inspect.getsource(snapshot)
    assert src.count('"change_24h_signed_pct"') >= 2, (
        "both the promoting and the regular pair tables must carry the signed "
        "24h move — ops renders the same column on each"
    )
