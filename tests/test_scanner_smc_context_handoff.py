"""Every scalp channel rebuilds ``smc_data``, and it must not lose anything.

The scan context assembles ``smc_data`` once — detector output plus the
LevelBook, order flow, the pair profile and the regime context. Then every
scalp channel re-runs SMC detection with its own timeframe preference and
rebuilds that dict from ``SMCResult.as_dict()``, which knows only what the
detector produces. Whatever the context added has to be carried across.

That carry used to be a hand-written list of twelve key names and it had
silently lost two: ``level_book_levels`` and ``cvd_15m``. Because
``smc_data.get`` answers ``None`` for an absent key exactly as it does for an
empty one, nothing could tell the difference — and all eight scalp channels
take the re-detect branch unconditionally, so this was every evaluator, every
scan, since the key was introduced.

The cost was not only measurement. Three live evaluators read
``level_book_levels`` and each treats absent as "LevelBook not refreshed", a
sentinel whose comment claims it "only triggers in tests":

* LSR skipped its HTF POI anchor check entirely (§3.4a's hard-block never
  applied),
* SR_FLIP fell back to the legacy 5m pivot detector — replaced 2026-05-17
  because 43% of its signals had MFE=0,
* FAR fell back to the 5m struct-scan — replaced because 115 FAR signals ran
  39% MFE=0 at −0.72% NET/sig.

The first test below is the one that matters: it derives the contract from
``_build_scan_context``'s own source, so a key added there tomorrow is covered
without anybody remembering to update a list.
"""
from __future__ import annotations

import ast
import inspect
import textwrap

import pytest

from src import scanner as scanner_mod
from src.detector import SMCResult
from src.level_book import Level
from src.scanner import (
    _CHANNEL_SMC_TIMEFRAMES,
    _SMC_CONTEXT_OVERRIDE_KEYS,
    _merge_context_smc_data,
)


def _keys_build_scan_context_writes() -> set:
    """Every ``smc_data["..."] = ...`` target inside ``_build_scan_context``.

    Parsed from the real source rather than listed here, because a list in a
    test is the same hand-maintained floor that caused the bug. The whole
    point is to notice a key nobody told us about.
    """
    src = inspect.getsource(scanner_mod.Scanner._build_scan_context)
    tree = ast.parse(textwrap.dedent(src))
    found = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (
                isinstance(target, ast.Subscript)
                and isinstance(target.value, ast.Name)
                and target.value.id == "smc_data"
                and isinstance(target.slice, ast.Constant)
                and isinstance(target.slice.value, str)
            ):
                found.add(target.slice.value)
    return found


class TestTheHandoffContract:
    def test_every_key_the_scan_context_writes_survives_the_redetect(self):
        """The regression guard, derived from the producer's own source."""
        written = _keys_build_scan_context_writes()
        # Sanity: if the parse silently found nothing, this test would pass
        # while checking nothing at all — the failure mode it exists to stop.
        assert len(written) >= 10, f"parser found only {written!r}"

        ctx_smc = {key: f"value-of-{key}" for key in written}
        merged = _merge_context_smc_data(SMCResult().as_dict(), ctx_smc)

        lost = sorted(k for k in written if merged.get(k) != f"value-of-{k}")
        assert not lost, f"per-channel re-detect drops {lost}"

    def test_the_two_keys_that_were_actually_lost(self):
        """Named explicitly, because a generic assertion would not say which."""
        written = _keys_build_scan_context_writes()
        assert {"level_book_levels", "cvd_15m"} <= written

    def test_every_scalp_channel_takes_the_redetect_branch(self):
        """Why the drop was universal rather than an edge case: there is no
        scalp channel that keeps the scan context's own smc_data."""
        assert _CHANNEL_SMC_TIMEFRAMES
        assert all(
            name.startswith("360_SCALP") for name in _CHANNEL_SMC_TIMEFRAMES
        )
        assert "360_SCALP" in _CHANNEL_SMC_TIMEFRAMES


class TestTheMergeItself:
    def test_a_level_book_survives_as_the_real_producer_made_it(self):
        """Driven from ``LevelBook``'s own dataclass, not a hand-written dict —
        the check ``zone_distance_atr`` did not get."""
        levels = [
            Level(price=104.0, type="resistance", source_tf="1h"),
            Level(price=96.0, type="support", source_tf="4h"),
        ]
        merged = _merge_context_smc_data(
            SMCResult().as_dict(), {"level_book_levels": levels}
        )
        assert merged["level_book_levels"] is levels

        # ...and the feature that could not compute on 4,000 rows now can.
        from src import entry_features as ef

        val, why = ef.level_distance_r_with_reason(
            merged.get("level_book_levels"), 100.0, 110.0, 10.0, True
        )
        assert why is None
        assert val == pytest.approx(0.4)

    def test_an_absent_level_book_still_reads_as_absent(self):
        """The fix must not invent a key. A context that genuinely has no
        LevelBook must still produce the `no_levels` cause, or the liveness
        probe stops being able to see the failure recur."""
        merged = _merge_context_smc_data(SMCResult().as_dict(), {})
        assert "level_book_levels" not in merged

    def test_the_context_wins_for_the_declared_override_keys(self):
        merged = _merge_context_smc_data(
            {"orderblocks": ["from-redetect"]}, {"orderblocks": ["from-context"]}
        )
        assert merged["orderblocks"] == ["from-context"]
        assert "orderblocks" in _SMC_CONTEXT_OVERRIDE_KEYS

    def test_the_redetect_wins_for_everything_else_it_produces(self):
        """The re-detect exists to give each channel its own timeframe view;
        carrying the context over the top of that would undo the whole point."""
        merged = _merge_context_smc_data(
            {"sweeps": ["channel-specific"]}, {"sweeps": ["generic"]}
        )
        assert merged["sweeps"] == ["channel-specific"]

    def test_it_does_not_mutate_either_input(self):
        fresh = SMCResult().as_dict()
        ctx = {"level_book_levels": [1]}
        before = dict(fresh)
        _merge_context_smc_data(fresh, ctx)
        assert fresh == before
        assert ctx == {"level_book_levels": [1]}

    def test_a_missing_context_is_not_a_crash(self):
        assert _merge_context_smc_data(SMCResult().as_dict(), None) == SMCResult().as_dict()
