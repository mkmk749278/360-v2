"""Phase 6 — a delivered row must outlive the flood of undelivered ones.

The arithmetic: 4,000-row rings, filled by enqueues of which ~0.5% deliver.
Evict-by-recency therefore spends the cap destroying the rare population to
make room for the common one, and does it invisibly — the ledger stays exactly
full and the ops page keeps rendering.

Every test here drives the real ring and the real ledgers. The two revert-checks
at the bottom fail against the pre-fix tree.
"""
from __future__ import annotations

import ast
from pathlib import Path

from src.delivery_retention import (
    DELIVERED_KEY,
    DeliveryRetainedRing,
    mark_delivered,
)

REPO = Path(__file__).resolve().parents[1]


def _row(i: int, t: float = 0.0) -> dict:
    return {"signal_id": f"s{i}", "stamped_at": t or float(i)}


# ── the policy ────────────────────────────────────────────────────────────

def test_a_delivered_row_survives_a_flood_of_undelivered_ones():
    """The whole point. Pre-fix this row is gone after `max_pending` more
    stamps, and nothing anywhere says so."""
    ring = DeliveryRetainedRing(name="t", max_pending=10, max_delivered=10)
    ring.add(_row(0))
    assert ring.mark_delivered("s0")

    for i in range(1, 200):          # 20x the pending cap
        ring.add(_row(i))

    assert ring.row_for("s0") is not None, "the confirmed row was evicted"
    assert "s0" in ring
    st = ring.stats()
    assert st["n_delivered"] == 1
    assert st["evicted_pending"] >= 180
    assert st["evicted_delivered"] == 0


def test_undelivered_rows_still_evict_oldest_first():
    """Cheap evidence rotating out is correct and must not change."""
    ring = DeliveryRetainedRing(name="t", max_pending=3, max_delivered=10)
    for i in range(5):
        ring.add(_row(i))
    assert ring.row_for("s0") is None      # oldest gone
    assert ring.row_for("s1") is None
    assert ring.row_for("s4") is not None
    assert ring.stats()["evicted_pending"] == 2


def test_the_two_evictions_are_counted_apart():
    """One is designed rotation; the other is the retention policy losing a
    verdict. A single figure covering both would move with enqueue volume and
    say nothing about the thing worth knowing."""
    ring = DeliveryRetainedRing(name="t", max_pending=100, max_delivered=2)
    for i in range(4):
        ring.add(_row(i))
        ring.mark_delivered(f"s{i}")
    st = ring.stats()
    assert st["evicted_delivered"] == 2    # cap is 2, four were delivered
    assert st["evicted_pending"] == 0      # pending never overflowed
    assert st["delivered_full"] is True


def test_delivered_rows_are_still_bounded():
    """Unbounded growth is a cost defect whatever it is holding."""
    ring = DeliveryRetainedRing(name="t", max_pending=50, max_delivered=5)
    for i in range(100):
        ring.add(_row(i))
        ring.mark_delivered(f"s{i}")
    assert ring.stats()["n_delivered"] == 5
    assert len(ring) <= 55


def test_mark_delivered_is_idempotent():
    ring = DeliveryRetainedRing(name="t", max_pending=10, max_delivered=10)
    ring.add(_row(0))
    assert ring.mark_delivered("s0") is True
    assert ring.mark_delivered("s0") is True     # not a miss, not a second move
    st = ring.stats()
    assert st["promoted"] == 1
    assert st["n_delivered"] == 1
    assert st["promote_misses"] == 0


def test_a_promotion_for_an_evicted_row_is_counted_as_a_miss():
    """This is the measurement of whether `max_pending` is adequate: it can
    only happen when a row was evicted between its stamp and the router
    confirming delivery."""
    ring = DeliveryRetainedRing(name="t", max_pending=2, max_delivered=10)
    ring.add(_row(0))
    ring.add(_row(1))
    ring.add(_row(2))                 # evicts s0
    assert ring.mark_delivered("s0") is False
    assert ring.stats()["promote_misses"] == 1


def test_rows_come_back_in_one_chronological_order():
    """Two rings under the hood must not surface as two blocks — a consumer
    reads one ledger."""
    ring = DeliveryRetainedRing(name="t", max_pending=10, max_delivered=10)
    for i in range(6):
        ring.add(_row(i))
    ring.mark_delivered("s1")
    ring.mark_delivered("s4")
    order = [r["signal_id"] for r in ring.rows()]
    assert order == ["s0", "s1", "s2", "s3", "s4", "s5"]


# ── the restart, which is where this could have silently reverted ─────────

def test_delivery_is_a_field_on_the_row_so_it_survives_the_round_trip():
    """Retention state kept only in the ring would be correct until the first
    restart and then silently back to evict-by-recency, with a full-looking
    ledger (#842's class: a field the serializer drops is invisible at both
    ends)."""
    ring = DeliveryRetainedRing(name="t", max_pending=10, max_delivered=10)
    ring.add(_row(0))
    ring.mark_delivered("s0")
    serialized = [dict(r) for r in ring.rows()]      # what flush() writes
    assert serialized[0][DELIVERED_KEY] is True

    revived = DeliveryRetainedRing(name="t2", max_pending=2, max_delivered=10)
    for r in serialized:
        revived.restore(r)
    for i in range(1, 50):
        revived.add(_row(i))
    assert revived.row_for("s0") is not None, (
        "a restored delivered row was evicted — retention did not survive the "
        "round trip"
    )


def test_restore_routes_an_undelivered_row_to_pending():
    ring = DeliveryRetainedRing(name="t", max_pending=2, max_delivered=10)
    ring.restore({"signal_id": "a", "stamped_at": 1.0})
    assert ring.stats()["n_pending"] == 1
    assert ring.stats()["n_delivered"] == 0


# ── the registry: one router call reaches every lane ──────────────────────

def test_one_call_promotes_across_every_live_lane():
    a = DeliveryRetainedRing(name="lane_a", max_pending=10, max_delivered=10)
    b = DeliveryRetainedRing(name="lane_b", max_pending=10, max_delivered=10)
    a.add(_row(7))
    b.add(_row(7))
    assert mark_delivered("s7") >= 2
    assert a.row_for("s7")[DELIVERED_KEY] is True
    assert b.row_for("s7")[DELIVERED_KEY] is True


def test_a_lane_that_never_stamped_the_candidate_is_not_an_error():
    """A return of 0 from a lane is legitimate — its gate simply never stamped
    this candidate."""
    ring = DeliveryRetainedRing(name="lane_c", max_pending=10, max_delivered=10)
    ring.add(_row(1))
    mark_delivered("s999")
    assert ring.stats()["promoted"] == 0


# ── the real ledgers ──────────────────────────────────────────────────────

def test_both_live_ledgers_use_the_shared_policy():
    """Driving the real ledgers, not a hand-built stand-in."""
    from src.entry_features import EntryFeatureLedger
    from src.structural_snap import SnapLedger

    for led in (SnapLedger(path="", max_rows=3), EntryFeatureLedger(path="", max_rows=3)):
        led.add({"signal_id": "keep", "stamped_at": 1.0})
        assert led.mark_delivered("keep") is True
        for i in range(30):
            led.add({"signal_id": f"x{i}", "stamped_at": float(i + 2)})
        ids = {r["signal_id"] for r in led.rows()}
        assert "keep" in ids, f"{type(led).__name__} evicted a delivered row"
        assert led.retention()["n_delivered"] == 1


# ── revert-checks: these fail against the pre-fix tree ────────────────────

def test_the_router_marks_delivery_at_the_confirmed_delivery_point():
    """Pins the CALL SITE. An import proves only that a name resolves, and
    Phase 2a's entire finding was a complete handler with nothing calling it."""
    src = (REPO / "src" / "signal_router.py").read_text()
    assert "delivery_retention" in src
    assert "_dr.mark_delivered(signal.signal_id)" in src

    tree = ast.parse(src)
    # It must sit in the same function that registers a delivered signal —
    # i.e. after `self._delivered_total += 1`, not in some helper that a
    # dropped candidate also reaches.
    fn = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = ast.dump(node)
            if "_delivered_total" in body and "mark_delivered" in body:
                fn = node
    assert fn is not None, (
        "mark_delivered is not in the function that confirms delivery — "
        "enqueue is not delivery"
    )


def test_neither_ledger_evicts_by_recency_any_more():
    """A plain `deque(maxlen=…)` of rows is the pre-fix shape and cannot
    protect anything, so its absence is the fix."""
    for mod in ("structural_snap.py", "entry_features.py"):
        src = (REPO / "src" / mod).read_text()
        assert "DeliveryRetainedRing" in src, f"{mod} does not use the policy"
        assert "self._rows: Deque[dict] = deque(maxlen=" not in src, (
            f"{mod} still holds a recency-evicting ring"
        )
