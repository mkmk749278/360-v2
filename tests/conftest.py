"""Shared pytest fixtures for the test suite.

Per-test isolation of disk-backed registries.  Without this, tests
that exercise ``Scanner._dispatch_cooldown`` or
``ScalpChannel._ma_cross_last_fire_ts`` would share state via their
JSON files in ``data/`` — a fire in one test would block fires in
later tests.

Cooldown + staleness: disabled by default in tests (set via env var
before scanner module loads).  Tests of the cooldown / staleness
behaviour itself construct fresh state and bypass the autouse
fixture by re-enabling.
"""

from __future__ import annotations

import os

# Disable dispatch cooldown for the test suite — set BEFORE any test
# imports ``src.scanner`` so the module-level ``DISPATCH_COOLDOWN_SEC``
# is initialised to 0 from the env var.  Tests of cooldown behaviour
# manage their own state via the in-memory dict directly.
os.environ.setdefault("DISPATCH_COOLDOWN_SEC", "0")

import pytest


@pytest.fixture(autouse=True)
def _isolate_disk_backed_registries(tmp_path, monkeypatch):
    """Per-test tmp path for every disk-backed cooldown / persistence file
    in the engine.  Autouse so individual tests don't have to opt in.
    """
    # Scanner dispatch cooldown — point persistence to tmp path so
    # ``data/signal_dispatch_cooldown.json`` doesn't accumulate across
    # test runs.  Cooldown SEC is already 0 via env var (above).
    import src.scanner as _scanner_mod
    from src.scanner import Scanner

    monkeypatch.setattr(
        _scanner_mod,
        "DISPATCH_COOLDOWN_PATH",
        str(tmp_path / "signal_dispatch_cooldown.json"),
    )
    # Skip the disk read/write in tests entirely; persistence isn't
    # part of any unit-test contract here.
    monkeypatch.setattr(Scanner, "_load_dispatch_cooldown", lambda self: None)
    monkeypatch.setattr(Scanner, "_persist_dispatch_cooldown", lambda self: None)
    # Default: staleness check passes (tests use mocked data_store
    # whose ``.candles`` attribute is a MagicMock that doesn't
    # behave like real candle data).
    monkeypatch.setattr(Scanner, "_is_entry_fresh", lambda self, sig: True)
    # Belt-and-braces: nuke any stale ``data/signal_dispatch_cooldown.json``
    # that might exist from a misconfigured run BEFORE the conftest landed.
    # Without this, ``Scanner._load_dispatch_cooldown`` (when conftest
    # accidentally fails to patch — e.g. across importlib.reload boundaries)
    # could pick up stale entries and trip cooldown guards in unrelated tests.
    from pathlib import Path
    stale_path = Path("data/signal_dispatch_cooldown.json")
    if stale_path.exists():
        try:
            stale_path.unlink()
        except OSError:
            pass

    # ScalpChannel MA-cross cooldown (PR #318).
    from src.channels.scalp import ScalpChannel
    monkeypatch.setattr(
        ScalpChannel,
        "_MA_CROSS_COOLDOWN_PATH",
        str(tmp_path / "ma_cross_cooldown.json"),
    )

    yield
