"""Phase 2c — the live depth book.

Three of these are revert-checks: they fail against the tree as it was before
this change, which is the only thing that makes them tests of the fix rather
than restatements of the code. "Verify a fix by reverting it" (#798, and again
on 2026-08-02) — a test written from the same assumption as the code asserts
that assumption back at itself.
"""
from __future__ import annotations

import ast
import time
from pathlib import Path

import pytest

from src.depth_book import (
    DEFAULT_LEVELS,
    DEFAULT_SPEED_MS,
    VALID_LEVELS,
    VALID_SPEEDS_MS,
    DepthBookStore,
    stale_after_s,
)

REPO = Path(__file__).resolve().parents[1]


def _msg(bids, asks, event_ms: int = 1_700_000_000_000):
    """A payload in the vendor's real shape.

    Hand-built here because this IS the vendor seam and there is no producer in
    the repo to drive — the shape is taken from the futures partial-depth
    stream (`e`/`s`/`E`/`b`/`a`, string-encoded numbers), not invented. Every
    other collaborator in these tests is the real object.
    """
    return {
        "e": "depthUpdate",
        "s": "BTCUSDT",
        "E": event_ms,
        "b": [[str(p), str(q)] for p, q in bids],
        "a": [[str(p), str(q)] for p, q in asks],
    }


# ── the store ─────────────────────────────────────────────────────────────

def test_update_parses_the_vendor_shape():
    st = DepthBookStore()
    snap = st.update("BTCUSDT", _msg([(100.0, 2.0), (99.0, 3.0)], [(101.0, 1.0)]))
    assert snap is not None
    assert snap.bids == [(100.0, 2.0), (99.0, 3.0)]
    assert snap.asks == [(101.0, 1.0)]
    assert snap.levels == 1  # min(2, 1) — reported, not the requested 20


def test_a_snapshot_replaces_rather_than_accumulates():
    """The property that makes a dropped message survivable.

    The partial stream was chosen over the diff stream precisely because state
    is replaced wholesale, so there is no sequence to desync. If this ever
    became an append the store would grow without bound AND a gap would corrupt
    it silently — the two failures the choice was made to avoid.
    """
    st = DepthBookStore()
    st.update("BTCUSDT", _msg([(100.0, 2.0)], [(101.0, 1.0)]))
    st.update("BTCUSDT", _msg([(200.0, 5.0)], [(201.0, 4.0)]))
    snap = st.get("BTCUSDT")
    assert snap is not None
    assert snap.bids == [(200.0, 5.0)]
    assert snap.asks == [(201.0, 4.0)]


def test_an_unreadable_payload_is_counted_not_swallowed():
    st = DepthBookStore()
    assert st.update("BTCUSDT", {"b": "not-a-list", "a": []}) is None
    assert st.update("BTCUSDT", {"b": [["x", "y"]], "a": [[1, 1]]}) is None
    h = st.health()
    assert h["messages_rejected"] == 2
    assert h["messages_total"] == 0


def test_zero_quantity_levels_are_dropped():
    """A zero-qty level is a delete in the diff protocol. Keeping one would
    understate a side by a phantom empty level."""
    st = DepthBookStore()
    snap = st.update("BTCUSDT", _msg([(100.0, 2.0), (99.0, 0.0)], [(101.0, 1.0)]))
    assert snap is not None
    assert snap.bids == [(100.0, 2.0)]


def test_a_book_with_one_empty_side_is_refused():
    """A missing side is not a balanced book, and returning 0.0 would say the
    opposite of what we know."""
    st = DepthBookStore()
    assert st.update("BTCUSDT", _msg([(100.0, 2.0)], [])) is None
    assert st.get("BTCUSDT") is None


# ── refusing, rather than clamping ────────────────────────────────────────

def test_notional_reports_the_levels_it_actually_used():
    """A 3-level answer labelled 20 is the quiet mislabelling this lane exists
    to stop. `levels_used` is returned rather than assumed."""
    st = DepthBookStore()
    st.update(
        "BTCUSDT",
        _msg([(100.0, 1.0), (99.0, 1.0), (98.0, 1.0)], [(101.0, 1.0), (102.0, 1.0)]),
    )
    snap = st.get("BTCUSDT")
    assert snap is not None
    b, a, used = snap.notional(20)
    assert used == 2                       # min(20, 3 bids, 2 asks)
    assert b == pytest.approx(297.0)       # 100+99+98
    assert a == pytest.approx(203.0)       # 101+102


def test_an_invalid_level_or_speed_is_refused_at_construction():
    """A value outside the vendor menu subscribes a stream that silently never
    delivers, which reads exactly like a dead feed. Refuse loudly instead."""
    with pytest.raises(ValueError):
        DepthBookStore(levels=17)
    with pytest.raises(ValueError):
        DepthBookStore(speed_ms=333)
    assert DEFAULT_LEVELS in VALID_LEVELS
    assert DEFAULT_SPEED_MS in VALID_SPEEDS_MS


# ── staleness: silence is a fault here ────────────────────────────────────

def test_stale_bound_is_derived_from_the_stream_clock():
    """Not guessed. Depth publishes unconditionally at `speed_ms`, so the
    bound is twenty intervals — floored so a fast speed cannot produce a
    threshold that fires on ordinary scheduling jitter."""
    assert stale_after_s(500) == 10.0
    assert stale_after_s(100) == 5.0       # floor, not 2.0


def test_a_stale_book_is_refused_rather_than_returned_with_a_flag():
    """A stale book is not a degraded answer — it describes a market that has
    moved, and every consumer reads it to make a decision."""
    st = DepthBookStore(speed_ms=500)
    st.update("BTCUSDT", _msg([(100.0, 1.0)], [(101.0, 1.0)]))
    assert st.get("BTCUSDT") is not None
    # Age the snapshot past the bound rather than sleeping for it.
    st._by_symbol["BTCUSDT"].snapshot.recv_at = time.monotonic() - 11.0
    assert st.is_stale("BTCUSDT")
    assert st.get("BTCUSDT") is None
    assert st.order_book("BTCUSDT") is None
    assert st.get("BTCUSDT", allow_stale=True) is not None


def test_health_keeps_subscribed_and_delivering_as_separate_denominators():
    """A feed that dies leaves the store full of snapshots, so a probe counting
    what the store HOLDS reads healthy while nothing arrives (#815's shape)."""
    st = DepthBookStore(speed_ms=500)
    st.note_subscribed(["BTCUSDT", "ETHUSDT", "SOLUSDT"])
    st.update("BTCUSDT", _msg([(100.0, 1.0)], [(101.0, 1.0)]))
    h = st.health()
    assert h["symbols_subscribed"] == 3
    assert h["delivering"] == 1
    assert h["never_delivered"] == 2       # asked for, never arrived
    assert "ETHUSDT" in h["never_symbols"]


# ── the measurement the phase turns on ────────────────────────────────────

def test_comparison_reads_both_depths_off_one_snapshot():
    """Top-1 against top-N from the SAME message. A comparison across two
    sources would measure their timing as much as their depth."""
    st = DepthBookStore()
    # Touch favours the bid; the size behind it favours the ask.
    st.update(
        "BTCUSDT",
        _msg(
            [(100.0, 10.0), (99.0, 1.0)],
            [(101.0, 1.0), (102.0, 50.0)],
        ),
    )
    cmp = st.comparison("BTCUSDT")
    assert cmp is not None
    assert cmp["imb_top1"] > 0             # one quote says bids
    assert cmp["imb_topn"] < 0             # the book says asks
    assert cmp["sign_flip"] is True
    assert cmp["delta"] == pytest.approx(cmp["imb_topn"] - cmp["imb_top1"])


def test_comparison_census_counts_flips_over_fresh_books_only():
    st = DepthBookStore(speed_ms=500)
    st.update("BTCUSDT", _msg([(100.0, 10.0), (99.0, 1.0)], [(101.0, 1.0), (102.0, 50.0)]))
    st.update("ETHUSDT", _msg([(100.0, 1.0)], [(101.0, 1.0)]))
    st._by_symbol["ETHUSDT"].snapshot.recv_at = time.monotonic() - 999.0
    census = st.comparison_census()
    assert census["n"] == 1                # the stale one is not evidence
    assert census["sign_flips"] == 1


# ── revert-checks: these must fail against the pre-fix tree ───────────────

def test_the_depth_handler_is_wired_at_the_dispatcher():
    """Phase 2a's whole finding was a complete handler with NO subscription.
    A store nothing feeds is the same defect one module over, so pin the call
    site rather than the import — an import proves only that a name resolves.
    """
    src = (REPO / "src" / "main.py").read_text()
    tree = ast.parse(src)

    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        if not (isinstance(node.left, ast.Name) and node.left.id == "event"):
            continue
        for c in node.comparators:
            if isinstance(c, ast.Constant) and c.value == "depthUpdate":
                found = True
    assert found, "main.py does not dispatch on the depthUpdate event"
    assert "get_depth_store().update(symbol, data)" in src


def test_the_depth_subscription_exists_and_is_bounded():
    """The subscription Phase 2a found missing for aggTrade. Also pins that it
    is bounded — an unbounded rollout is a cost decision nobody took."""
    src = (REPO / "src" / "bootstrap.py").read_text()
    assert "@depth{DEPTH_STREAM_LEVELS}@{DEPTH_STREAM_SPEED_MS}ms" in src
    assert "DEPTH_MAX_SYMBOLS" in src
    assert "_ws_futures_depth.start(futures_depth_streams)" in src


def test_the_consumer_handover_is_flag_gated_and_defaults_off():
    """Four consumers read this book, one of them the final execution gate
    before dispatch. The measurement runs from the moment it ships; the effect
    waits for sign-off (§ Project Phase)."""
    import config

    assert config.DEPTH_STREAM_ENABLED is True      # measurement ON
    assert config.DEPTH_LIVE_FOR_CONSUMERS is False  # effect OFF

    scanner_src = (REPO / "src" / "scanner" / "__init__.py").read_text()
    assert "if _order_book is None and DEPTH_LIVE_FOR_CONSUMERS:" in scanner_src


def test_book_source_is_stamped_so_one_column_is_not_two_measurements():
    """`book_imbalance` sums bids[:10] and has been summing a list of length
    one. When the handover flips, the same column starts describing twenty
    levels — the exact thing `cvd_source` exists to keep separable."""
    from src.entry_features import ROW_METADATA_KEYS, capture

    assert "book_source" in ROW_METADATA_KEYS

    row = capture(
        symbol="BTCUSDT",
        direction_is_long=True,
        entry=100.0,
        sl_dist=1.0,
        tp1=102.0,
        trigger="TEST",
        tf=None,
        tf_name="15m",
        atr=1.0,
        smc_data={
            "order_book": {
                "bids": [[100.0, 5.0]],
                "asks": [[101.0, 1.0]],
                "source": "book_ticker",
                "depth_quality": "top_of_book_only",
            }
        },
    )
    assert row["book_source"] == "top_of_book_only"
    # And it is metadata, not a feature: it is populated on a HEALTHY row, so
    # counting it would mark every good row incomplete.
    assert "book_source" not in row.get("missing", [])
