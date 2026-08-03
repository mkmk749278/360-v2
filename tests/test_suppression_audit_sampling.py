"""A capped per-gate ring makes every verdict on it a sample. Say so.

Owner, 2026-08-02, on cooldown-suppressed signals: *"we don't know how they
perform after cooldown, so why don't we measure them rather than completely
ignoring?"*

Part of the answer is that `dispatch_cooldown` **is** measured — it carries a
row in the Suppression Quality Audit. The rest of the answer is that the row
read `n=396` against a ring capped at 400, and nothing on screen said whether
that was the whole population or a slice of tens of thousands. The store had
computed the eviction counts all along (`sampling()`), and:

* they were never persisted, so any reader in another process — the truth report
  is built by a separate script — saw every gate as unsampled;
* they were never rendered, so a sampled EV read exactly like a census.

Both halves are pinned here, because fixing only the render would have shipped a
column that says "all" for every gate forever.
"""
from __future__ import annotations

import json

from src import suppression_audit as sa


def _rec(gate: str, i: int) -> sa.SuppressedCandidateRecord:
    return sa.stamp_candidate(
        gate_name=gate, symbol=f"AAA{i}USDT", channel="360_SCALP",
        setup_class="MOVER_TREND_PULLBACK", side="LONG",
        entry=100.0, stop_loss=98.0, tp1=104.0, confidence=70.0,
        store=_STORE,
    )


_STORE: sa.SuppressedCandidateStore


class TestEvictionCountsSurviveTheRoundTrip:
    """A round trip is a contract — pinned by driving the real serializer."""

    def test_evictions_are_written_and_read_back(self, tmp_path):
        global _STORE
        path = str(tmp_path / "sup.json")
        _STORE = sa.SuppressedCandidateStore(persist_path=path, per_gate_max=5)
        for i in range(12):                      # 12 stamps into a ring of 5
            _rec("dispatch_cooldown", i)
        _STORE._save()

        before = _STORE.sampling()["dispatch_cooldown"]
        assert before["held"] == 5
        assert before["evicted"] == 7, "the ring must count what it dropped"

        reloaded = sa.SuppressedCandidateStore(persist_path=path, per_gate_max=5)
        after = reloaded.sampling()["dispatch_cooldown"]
        assert after["evicted"] == before["evicted"], (
            "eviction counts died on the round trip — a reader in another "
            "process would report this sampled gate as a census"
        )
        assert after["held"] == before["held"]

    def test_a_pre_schema_list_file_still_loads(self, tmp_path):
        """The old format is a bare list. It must not fail closed."""
        path = str(tmp_path / "old.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump([{
                "gate_name": "dispatch_cooldown", "symbol": "BTCUSDT",
                "channel": "360_SCALP", "setup_class": "X", "side": "LONG",
                "entry": 100.0, "stop_loss": 98.0, "tp1": 104.0,
                "sl_distance": 2.0,
            }], fh)
        store = sa.SuppressedCandidateStore(persist_path=path)
        assert len(store.records()) == 1
        assert store.sampling()["dispatch_cooldown"]["evicted"] == 0


class TestTheReportStatesTheDenominator:
    def test_a_sampled_gate_is_rendered_as_a_share_not_a_census(self):
        """Driven through the real markdown formatter, not a source grep."""
        from src.runtime_truth_report import format_truth_report_markdown

        snapshot = {
            "suppression_audit": {
                "totals": {"WOULD_WIN": 10, "WOULD_LOSE": 20, "WOULD_EXPIRE": 5},
                "pending": 0,
                "by_gate": {
                    "dispatch_cooldown": {
                        "n": 396, "would_win_pct": 21.2, "saved_r": 70.0,
                        "missed_r": 69.0, "ev_per_suppression_r": 0.0,
                        "verdict": "TUNE",
                    },
                    "data_stale": {
                        "n": 17, "would_win_pct": 0.0, "saved_r": 17.9,
                        "missed_r": 0.0, "ev_per_suppression_r": 1.05,
                        "verdict": "KEEP",
                    },
                },
                "sampling": {
                    "dispatch_cooldown": {"held": 396, "evicted": 23604, "cap": 400},
                    "data_stale": {"held": 17, "evicted": 0, "cap": 400},
                },
            },
        }
        text = format_truth_report_markdown(snapshot, {})

        assert "of 24000" in text, (
            "a gate at its ring cap must state the population its EV was "
            "measured on — 'n=396' alone reads as a census"
        )
        assert "is a SAMPLE" in text
        assert "dispatch_cooldown" in text.split("is a SAMPLE")[1]
        # An unsampled gate must not be labelled as sampled.
        assert "| all |" in text
