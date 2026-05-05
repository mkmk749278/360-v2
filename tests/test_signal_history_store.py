"""Tests for ``src.signal_history_store``.

Covers serialization round-trip, cap behaviour, malformed-record
tolerance, atomic-write guarantees, and env-var path override.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from src.channels.base import Signal
from src.smc import Direction
from src.signal_history_store import (
    DEFAULT_PATH,
    HISTORY_CAP,
    load_history,
    save_history,
)


def _make_signal(
    *,
    signal_id: str = "sig-001",
    setup_class: str = "SR_FLIP_RETEST",
    status: str = "TP1_HIT",
    direction: Direction = Direction.LONG,
    timestamp: datetime | None = None,
    terminal_outcome_timestamp: datetime | None = None,
) -> Signal:
    ts = timestamp or datetime.now(timezone.utc)
    return Signal(
        channel="360_SCALP",
        symbol="BTCUSDT",
        direction=direction,
        entry=78000.0,
        stop_loss=77400.0,
        tp1=78500.0,
        tp2=79000.0,
        tp3=79500.0,
        signal_id=signal_id,
        setup_class=setup_class,
        status=status,
        confidence=72.5,
        timestamp=ts,
        terminal_outcome_timestamp=terminal_outcome_timestamp,
    )


def test_save_then_load_round_trip(tmp_path: Path) -> None:
    p = tmp_path / "history.json"
    sig = _make_signal()
    save_history([sig], path=str(p))
    loaded = load_history(path=str(p))
    assert len(loaded) == 1
    assert loaded[0].signal_id == sig.signal_id
    assert loaded[0].symbol == sig.symbol
    assert loaded[0].direction == Direction.LONG
    assert loaded[0].setup_class == sig.setup_class
    assert loaded[0].status == sig.status
    assert loaded[0].timestamp == sig.timestamp


def test_load_missing_file_returns_empty_list(tmp_path: Path) -> None:
    p = tmp_path / "nope.json"
    assert load_history(path=str(p)) == []


def test_save_creates_parent_directory(tmp_path: Path) -> None:
    p = tmp_path / "data" / "nested" / "history.json"
    save_history([_make_signal()], path=str(p))
    assert p.exists()
    assert p.parent.is_dir()


def test_load_skips_malformed_records(tmp_path: Path) -> None:
    p = tmp_path / "history.json"
    # Mix one valid record with one malformed (missing required fields).
    valid = _make_signal()
    p.write_text(
        json.dumps(
            [
                {"this_is_not_a_signal": True},
                # Manually serialise the valid one
                {
                    "channel": valid.channel,
                    "symbol": valid.symbol,
                    "direction": valid.direction.value,
                    "entry": valid.entry,
                    "stop_loss": valid.stop_loss,
                    "tp1": valid.tp1,
                    "tp2": valid.tp2,
                    "signal_id": valid.signal_id,
                    "setup_class": valid.setup_class,
                    "status": valid.status,
                    "timestamp": valid.timestamp.isoformat(),
                },
            ]
        ),
        encoding="utf-8",
    )
    loaded = load_history(path=str(p))
    assert len(loaded) == 1
    assert loaded[0].signal_id == valid.signal_id


def test_load_handles_non_list_json(tmp_path: Path) -> None:
    p = tmp_path / "history.json"
    p.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
    assert load_history(path=str(p)) == []


def test_load_handles_corrupt_json(tmp_path: Path) -> None:
    p = tmp_path / "history.json"
    p.write_text("{ this is not valid json", encoding="utf-8")
    assert load_history(path=str(p)) == []


def test_save_caps_at_history_cap(tmp_path: Path) -> None:
    p = tmp_path / "history.json"
    over_cap = HISTORY_CAP + 50
    sigs = [_make_signal(signal_id=f"sig-{i:04d}") for i in range(over_cap)]
    save_history(sigs, path=str(p))
    loaded = load_history(path=str(p))
    assert len(loaded) == HISTORY_CAP
    # Latest entries should be retained — earliest dropped.
    assert loaded[-1].signal_id == f"sig-{over_cap - 1:04d}"


def test_save_atomic_no_partial_file(tmp_path: Path, monkeypatch) -> None:
    """If json.dump fails, the target file is not corrupted."""
    p = tmp_path / "history.json"
    save_history([_make_signal(signal_id="sig-good")], path=str(p))
    original_dump = json.dump

    def boom(*args, **kwargs):
        raise RuntimeError("simulated flush failure")

    monkeypatch.setattr(json, "dump", boom)
    with pytest.raises(RuntimeError):
        save_history(
            [_make_signal(signal_id="sig-bad")],
            path=str(p),
        )
    monkeypatch.setattr(json, "dump", original_dump)
    # Original file is intact.
    loaded = load_history(path=str(p))
    assert len(loaded) == 1
    assert loaded[0].signal_id == "sig-good"
    # No leftover .sig_hist_ tmp files in the directory.
    leftover = [f for f in p.parent.iterdir() if f.name.startswith(".sig_hist_")]
    assert leftover == []


def test_env_var_path_override(tmp_path: Path, monkeypatch) -> None:
    p = tmp_path / "from-env.json"
    monkeypatch.setenv("SIGNAL_HISTORY_PATH", str(p))
    save_history([_make_signal()])
    assert p.exists()
    loaded = load_history()
    assert len(loaded) == 1


def test_default_path_used_when_no_override(monkeypatch) -> None:
    """Sanity: with no env var and no path arg, DEFAULT_PATH is used."""
    monkeypatch.delenv("SIGNAL_HISTORY_PATH", raising=False)
    # We don't actually write to data/ in tests — just verify the resolver.
    from src.signal_history_store import _resolve_path

    assert str(_resolve_path(None)) == DEFAULT_PATH


def test_round_trip_preserves_terminal_timestamp(tmp_path: Path) -> None:
    p = tmp_path / "history.json"
    term_ts = datetime(2026, 5, 5, 12, 0, 0, tzinfo=timezone.utc)
    sig = _make_signal(terminal_outcome_timestamp=term_ts)
    save_history([sig], path=str(p))
    loaded = load_history(path=str(p))
    assert loaded[0].terminal_outcome_timestamp == term_ts


def test_save_drops_none_entries(tmp_path: Path) -> None:
    """Defensive: a None slipping into the history list must not crash."""
    p = tmp_path / "history.json"
    save_history([None, _make_signal(), None], path=str(p))
    loaded = load_history(path=str(p))
    assert len(loaded) == 1
