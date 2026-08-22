"""A pair may be in BOTH universes — regular and promoted.

Owner, 2026-08-22, after three days of a +20% BTC melt-up during which the
delivered book was 90% ``MOVER_TREND_PULLBACK``: *"if something is moved to
promoted pairs, but by volume it should still keep in regular pairs too, so
one pair can be there in two universes"*.

The scanner restricted a promoted mover to four evaluators and decided that
on membership of ``_mover_promoted_pairs`` **alone**, so a core top-N pair up
15% on the day silently lost **fifteen of its nineteen** evaluators for the
whole promotion window.  Only movers from OUTSIDE the core set are capped
(``MOVER_PROMOTION_MAX_PAIRS`` = 30) — core ones are exempt from that cap and
accumulate — so the live box held 163 promotions inside a 330-pair universe
with at most 30 of them synthetic.

In a broad rally the pairs a subscriber recognises are exactly the pairs that
qualify as movers.  That is how "only MVRTP produces" and "nothing fires on
the regular pairs" turned out to be one sentence, and why the delivered book
was full of LTC / DOT / ADA / FIL / APT stamped ``MOVER_TREND_PULLBACK``.

The restriction's own written argument — a mover is a trending context, the
anti-thesis of fading an extension — is about a pair that is **only** a mover,
and still holds for one.  These tests pin the distinction.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import pytest

import config
import src.scanner as scanner_mod
from src.scanner import _MOVER_EVALUATORS, _all_scalp_evaluators


# ---------------------------------------------------------------------------
# A scanner stub carrying only the state the role resolver reads.
# ---------------------------------------------------------------------------

class _Info:
    def __init__(self, volume_24h_usd: float) -> None:
        self.volume_24h_usd = volume_24h_usd
        self.tier = "TIER1"
        self.volatility_24h = 18.0
        self.change_24h_signed_pct = 18.0


class _PairMgr:
    def __init__(self, pairs: Dict[str, _Info]) -> None:
        self.pairs = pairs


def _scanner(
    promoted: Dict[str, float],
    synthetic: set,
    pairs: Dict[str, _Info],
) -> Any:
    """A real ``Scanner`` with only the attributes the resolver touches.

    Built through ``__new__`` rather than a hand-written double so the methods
    under test are the **real** ones — a stub with a ``mover_universe_role`` of
    its own would assert this file's assumptions back at itself.
    """
    sc = scanner_mod.Scanner.__new__(scanner_mod.Scanner)
    sc._mover_promoted_pairs = promoted
    sc._synthetic_mover_pairs = synthetic
    sc.pair_mgr = _PairMgr(pairs)
    return sc


CORE_VOL = 400_000_000.0
BIG_SYNTH_VOL = 90_000_000.0
SMALL_SYNTH_VOL = 4_000_000.0


# ---------------------------------------------------------------------------
# The role resolver
# ---------------------------------------------------------------------------

def test_a_core_pair_that_is_also_igniting_is_dual_not_mover_only():
    sc = _scanner(
        promoted={"LTCUSDT": 1.0},
        synthetic=set(),
        pairs={"LTCUSDT": _Info(CORE_VOL)},
    )
    assert sc.mover_universe_role("LTCUSDT") == sc.MOVER_ROLE_DUAL_CORE


def test_a_synthetic_mover_below_the_volume_floor_stays_mover_only():
    """The restriction was written for this pair and still applies to it."""
    sc = _scanner(
        promoted={"NEWCOINUSDT": 1.0},
        synthetic={"NEWCOINUSDT"},
        pairs={"NEWCOINUSDT": _Info(SMALL_SYNTH_VOL)},
    )
    assert sc.mover_universe_role("NEWCOINUSDT") == sc.MOVER_ROLE_MOVER_ONLY


def test_a_synthetic_mover_trading_at_core_volume_is_dual_by_volume():
    """Never earning a top-N slot is a fact about the last universe refresh."""
    sc = _scanner(
        promoted={"BIGUSDT": 1.0},
        synthetic={"BIGUSDT"},
        pairs={"BIGUSDT": _Info(BIG_SYNTH_VOL)},
    )
    assert sc.mover_universe_role("BIGUSDT") == sc.MOVER_ROLE_DUAL_VOLUME


def test_an_unpromoted_pair_reports_no_role_rather_than_a_role():
    """"Not a mover" must not be readable as "not dual"."""
    sc = _scanner(promoted={}, synthetic=set(), pairs={"BTCUSDT": _Info(CORE_VOL)})
    assert sc.mover_universe_role("BTCUSDT") == sc.MOVER_ROLE_NONE
    assert sc.MOVER_ROLE_NONE not in (
        sc.MOVER_ROLE_DUAL_CORE, sc.MOVER_ROLE_DUAL_VOLUME, sc.MOVER_ROLE_MOVER_ONLY,
    )


def test_a_synthetic_pair_whose_info_vanished_is_not_promoted_to_dual():
    """Absence of a volume reading is not evidence of a large one."""
    sc = _scanner(promoted={"GONEUSDT": 1.0}, synthetic={"GONEUSDT"}, pairs={})
    assert sc.mover_universe_role("GONEUSDT") == sc.MOVER_ROLE_MOVER_ONLY


# ---------------------------------------------------------------------------
# The evaluator sets — the thing the roles decide
# ---------------------------------------------------------------------------

def test_the_mover_restriction_withholds_fifteen_of_nineteen_evaluators():
    """The number that makes the owner's question answerable.

    Derived from the class rather than asserted as a literal roster, so a new
    evaluator lands in this count without anyone updating a list.
    """
    every = _all_scalp_evaluators()
    withheld = every - _MOVER_EVALUATORS

    assert len(every) == 19, "evaluator count changed — is the census still right?"
    assert _MOVER_EVALUATORS <= every, "the mover set names an evaluator that does not exist"
    assert len(withheld) == 15
    # The two the owner asked about by name, and the two the funnel showed
    # dying at the regime gate rather than at an evaluator ban.
    assert "_evaluate_mean_revert" in withheld
    assert "_evaluate_range_fade" in withheld


def test_the_mover_set_is_defined_once():
    """One definition, three readers — asserted by SYNTAX TREE, not substring.

    The set used to be built inside the scan loop, which is how a second
    reader becomes a copy: ``MEASUREMENT_SUFFIXES`` drifted for a week exactly
    that way.  The first cut of this guard counted a member name in the source
    text and failed on ``_YOUNG_PAIR_EVALUATORS``, which legitimately names
    two of the same evaluators — a substring assertion answering a question
    about a *set*.  Walking the tree asks the real question: does any other
    literal in this module spell out the same collection?
    """
    import ast

    src = (scanner_mod.__file__ or "").replace(".pyc", ".py")
    tree = ast.parse(open(src, encoding="utf-8").read())

    def _literal_strs(node: ast.AST) -> Optional[frozenset]:
        """The string set a ``{...}`` or ``frozenset({...})`` literal spells."""
        if isinstance(node, ast.Call):
            fn = node.func
            if not (isinstance(fn, ast.Name) and fn.id == "frozenset"):
                return None
            if len(node.args) != 1:
                return None
            node = node.args[0]
        if not isinstance(node, (ast.Set, ast.List, ast.Tuple)):
            return None
        elts = node.elts
        if not elts or not all(
            isinstance(e, ast.Constant) and isinstance(e.value, str) for e in elts
        ):
            return None
        return frozenset(e.value for e in elts)  # type: ignore[attr-defined]

    # ``frozenset({...})`` is two nodes — the Call and the Set inside it — and
    # both spell the same collection, so the inner one is not a second
    # definition.  Count the outermost literal only.
    wrapped = {
        id(node.args[0])
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "frozenset"
        and len(node.args) == 1
    }
    matches = [
        node for node in ast.walk(tree)
        if id(node) not in wrapped and _literal_strs(node) == _MOVER_EVALUATORS
    ]
    assert len(matches) == 1, (
        f"the mover evaluator roster is spelled out {len(matches)} times — "
        "one of them will drift"
    )


# ---------------------------------------------------------------------------
# The census — measured whether or not the effect is enabled
# ---------------------------------------------------------------------------

def test_the_census_counts_dual_pairs_while_the_effect_is_off(monkeypatch):
    monkeypatch.setattr(scanner_mod, "DUAL_UNIVERSE_ENABLED", False)
    sc = _scanner(
        promoted={"LTCUSDT": 1.0, "DOTUSDT": 1.0, "NEWUSDT": 1.0},
        synthetic={"NEWUSDT"},
        pairs={
            "LTCUSDT": _Info(CORE_VOL),
            "DOTUSDT": _Info(CORE_VOL),
            "NEWUSDT": _Info(SMALL_SYNTH_VOL),
            "BTCUSDT": _Info(CORE_VOL),
        },
    )
    census = sc._dual_universe_census()

    assert census["enabled"] is False
    assert census["promoted"] == 3
    assert census["dual_candidates"] == 2, "two core pairs are being narrowed"
    assert census["by_role"]["dual_core"] == 2
    assert census["by_role"]["mover_only"] == 1
    assert census["universe_size"] == 4
    assert census["dual_share_of_universe"] == pytest.approx(0.5)
    # Named, not counted: "15 evaluators" says nothing about which paths
    # went quiet, and the owner's question was about the paths.
    assert "_evaluate_mean_revert" in census["withheld_evaluators"]
    assert len(census["withheld_evaluators"]) == 15


def test_the_census_bounds_its_symbol_lists():
    """It rides the snapshot; an unbounded list on a hot payload is the
    cost rule's own shape."""
    promoted = {f"SYM{i}USDT": 1.0 for i in range(80)}
    pairs = {s: _Info(CORE_VOL) for s in promoted}
    census = _scanner(promoted, set(), pairs)._dual_universe_census()

    assert len(census["symbols"]["dual_core"]) == 60
    assert census["symbols_truncated"]["dual_core"] == 20
    assert census["by_role"]["dual_core"] == 80, "the COUNT is not truncated"


def test_an_empty_promotion_set_reports_zero_rather_than_nothing():
    """A census that appears only when it has something to say teaches the
    reader that its absence means "nothing promoted"."""
    census = _scanner({}, set(), {"BTCUSDT": _Info(CORE_VOL)})._dual_universe_census()
    assert census["promoted"] == 0
    assert census["dual_candidates"] == 0
    assert census["by_role"] == {}


# ---------------------------------------------------------------------------
# The pairs payload — the display half of the same defect
# ---------------------------------------------------------------------------

class _EngineForPairs:
    def __init__(self, sc: Any) -> None:
        self._scanner = sc
        self.pair_mgr = sc.pair_mgr
        self._channels: list = []
        self._mover_ignition = None


def _pairs_payload(sc: Any) -> Dict[str, Any]:
    from src.api.snapshot import collect_pairs_live

    return collect_pairs_live(_EngineForPairs(sc))


def test_a_dual_pair_appears_under_regular_as_well_as_promoting():
    """Literally what the owner asked for, and what the tab denied him.

    ``collect_pairs_live`` skipped every promoted symbol from ``regular``
    under a comment about *synthetically-admitted* movers — right about a
    synthetic one, applied to all of them, so 163 of a 330-pair universe were
    hidden behind a tab reading "Regular (167)".
    """
    sc = _scanner(
        promoted={"LTCUSDT": 1.0, "NEWUSDT": 1.0},
        synthetic={"NEWUSDT"},
        pairs={
            "LTCUSDT": _Info(CORE_VOL),
            "NEWUSDT": _Info(SMALL_SYNTH_VOL),
            "BTCUSDT": _Info(CORE_VOL),
        },
    )
    payload = _pairs_payload(sc)
    regular = {r["symbol"] for r in payload["regular"]}
    promoting = {r["symbol"] for r in payload["promoting"]}

    assert "LTCUSDT" in regular, "a core pair vanished from Regular while promoted"
    assert "LTCUSDT" in promoting, "…and it is genuinely in both"
    assert "BTCUSDT" in regular

    # The opposite error: a pair the mover path invented is NOT a regular pair.
    assert "NEWUSDT" not in regular
    assert "NEWUSDT" in promoting


def test_every_row_says_which_universes_it_is_in():
    """The two lists overlap now, so a reader must not double-count silently."""
    sc = _scanner(
        promoted={"LTCUSDT": 1.0},
        synthetic=set(),
        pairs={"LTCUSDT": _Info(CORE_VOL), "BTCUSDT": _Info(CORE_VOL)},
    )
    payload = _pairs_payload(sc)
    by_sym = {r["symbol"]: r for r in payload["regular"]}

    assert by_sym["LTCUSDT"]["also_promoted"] is True
    assert by_sym["LTCUSDT"]["universe_role"] == "dual_core"
    assert by_sym["BTCUSDT"]["also_promoted"] is False
    assert by_sym["BTCUSDT"]["universe_role"] == ""
    assert payload["dual_count"] == 1

    promo = {r["symbol"]: r for r in payload["promoting"]}
    assert promo["LTCUSDT"]["universe_role"] == "dual_core"


def test_the_payload_carries_the_census():
    sc = _scanner(
        promoted={"LTCUSDT": 1.0},
        synthetic=set(),
        pairs={"LTCUSDT": _Info(CORE_VOL)},
    )
    census = _pairs_payload(sc)["dual_universe"]
    assert census["dual_candidates"] == 1
    assert "enabled" in census, "the page must be able to say which mode it is reading"


def test_an_engine_with_no_scanner_reports_no_census_rather_than_an_empty_one():
    from src.api.snapshot import collect_pairs_live

    class _Bare:
        _scanner = None
        pair_mgr = _PairMgr({"BTCUSDT": _Info(CORE_VOL)})
        _channels: list = []
        _mover_ignition = None

    payload = collect_pairs_live(_Bare())
    assert payload["dual_universe"] == {}
    assert payload["regular"], "a bare engine still lists its regular pairs"


# ---------------------------------------------------------------------------
# The flag
# ---------------------------------------------------------------------------

def test_the_effect_ships_default_off():
    """An evaluator-path change on a live money path ships dark.

    The census above runs regardless — that is the half the activation
    decision is read from.
    """
    assert config.DUAL_UNIVERSE_ENABLED is False


def test_the_volume_floor_is_the_tiering_boundary_that_already_existed():
    """Not a number chosen while looking at one window.

    50M is ``pair_manager``'s MIDCAP boundary, in the tree since it was
    written.
    """
    assert config.DUAL_UNIVERSE_MIN_VOLUME_USD == 50_000_000.0
