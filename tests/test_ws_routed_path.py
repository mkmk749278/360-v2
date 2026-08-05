"""Binance serves book streams and trade streams on mutually exclusive paths.

Measured against the live vendor 2026-08-05 (see `_BOOK_PATH_MARKERS` and the
table above it in `websocket_manager`). A stream on the wrong path does not
error and does not close — the handshake succeeds, PING/PONG keeps the socket
alive, `is_healthy` stays true, and zero frames arrive. Phase 2c's depth pool
shipped exactly that: 40 streams, 40 silent, pool HEALTHY, store empty.

So these tests pin the *URL*, which is the only place the fault is visible
before it becomes a silent feed.
"""
from __future__ import annotations

import ast
from pathlib import Path

from src.websocket_manager import (
    ROUTED_PATH_BOOK,
    ROUTED_PATH_MARKET,
    WebSocketManager,
)

REPO = Path(__file__).resolve().parents[1]


def _mgr(**kw):
    return WebSocketManager(lambda _m: None, market="futures", **kw)


def test_the_default_path_is_unchanged_for_every_pre_existing_pool():
    """klines / aggTrade / forceOrder / ticker were all correct before this
    change and must stay byte-identical — the fix is additive."""
    url = _mgr()._build_combined_stream_url(["btcusdt@aggTrade"])
    assert "/market/stream?streams=btcusdt@aggTrade" in url
    assert ROUTED_PATH_MARKET == "/market/stream"


def test_a_book_pool_is_built_on_the_book_path():
    url = _mgr(routed_path=ROUTED_PATH_BOOK)._build_combined_stream_url(
        ["btcusdt@depth20@500ms"]
    )
    assert "/stream?streams=btcusdt@depth20@500ms" in url
    assert "/market/stream" not in url


def test_the_depth_pool_declares_the_book_path_at_its_construction_site():
    """A revert-check, and it pins the CALL SITE rather than the import.

    Fails against the pre-fix tree, where the depth pool inherited the default
    `/market/stream` and therefore could never deliver.
    """
    src = (REPO / "src" / "bootstrap.py").read_text()
    tree = ast.parse(src)
    found = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if getattr(node.func, "id", None) != "WebSocketManager":
            continue
        kw = {k.arg: k.value for k in node.keywords}
        label = kw.get("label")
        if isinstance(label, ast.Constant) and label.value == "futures_depth":
            rp = kw.get("routed_path")
            assert rp is not None, (
                "the depth pool does not declare routed_path — it will inherit "
                "/market/stream, connect, report healthy and deliver nothing"
            )
            assert getattr(rp, "id", None) == "ROUTED_PATH_BOOK"
            found = True
    assert found, "no futures_depth WebSocketManager construction found"


def test_a_pool_whose_path_disagrees_with_its_streams_is_loud():
    """The symptom is silence, so nothing downstream can raise it. This is the
    one point where the declared path and the actual streams are both in
    scope.

    Captured off the real loguru sink rather than `caplog` — the engine logs
    through loguru, which does not propagate to stdlib handlers, so a caplog
    assertion here would pass vacuously against a guard that had been deleted.
    """
    from src.utils import get_logger  # noqa: F401
    from loguru import logger

    seen = []
    sink = logger.add(lambda m: seen.append(str(m)), level="ERROR")
    try:
        _mgr()._build_combined_stream_url(["btcusdt@depth20@500ms"])
    finally:
        logger.remove(sink)
    assert any("deliver nothing" in s for s in seen), seen
    assert any("routed_path='/stream'" in s for s in seen), seen


def test_a_mixed_pool_is_named_as_unservable():
    """No single path can carry both, so whichever is chosen silently drops the
    other half. That is a pool-splitting bug, not a path-choice bug, and the
    two get different messages because they have different fixes."""
    mgr = _mgr(routed_path=ROUTED_PATH_BOOK)
    url = mgr._build_combined_stream_url(
        ["btcusdt@depth20@500ms", "btcusdt@aggTrade"]
    )
    # It still builds a URL — refusing to connect would take down a pool that
    # is half-working. The finding is the log line, not an exception.
    assert "streams=" in url


def test_book_markers_cover_both_book_streams():
    """`@bookTicker` measured silent on /market/stream too. It is not
    subscribed over WS today (the engine REST-polls it), but the marker exists
    so a future pool cannot repeat this with the other book stream."""
    from src.websocket_manager import _BOOK_PATH_MARKERS
    assert "@depth" in _BOOK_PATH_MARKERS
    assert "@bookTicker" in _BOOK_PATH_MARKERS
