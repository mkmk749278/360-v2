"""Phase 1a: the analyst's rendered chart (docs/ANALYST_DESK_PLAN_2026_11_28.md)."""
import base64
import time

from src import diag_catalog
from src.historical_data import HistoricalDataStore

NOW = time.time()
H_MS = 3_600_000


def _engine(n=60, symbol="XYZUSDT", tf="1h"):
    st = HistoricalDataStore()
    last_open = (int(NOW * 1000) // H_MS - 1) * H_MS
    for i in range(n):
        p = 100.0 + (i % 7) - 3
        st.update_candle(symbol, tf, {"open": p, "high": p + 1.5, "low": p - 1.5,
                                      "close": p + 0.5, "volume": 10 + i,
                                      "open_time": last_open - (n - 1 - i) * H_MS})
    return type("E", (), {"data_store": st})()


def test_renders_a_png_of_the_closed_bars_through_the_catalog():
    out = diag_catalog.run("read.analyst_chart_image", _engine(),
                           {"symbol": "xyzusdt", "tf": "1h", "bars": 40, "levels": [99, "x", 101.5]})
    assert out["ok"], out
    res = out["result"]
    assert res["readable"] and res["bars"] == 40 and res["mime_type"] == "image/png"
    png = base64.b64decode(res["png_base64"])
    assert png[:8] == b"\x89PNG\r\n\x1a\n" and len(png) == res["png_bytes"]
    assert res["levels_drawn"] == [99.0, 101.5], "an unreadable level is dropped, not guessed"
    assert res["last_close"] == 100.0 + ((59 % 7) - 3) + 0.5
    assert len(res["png_base64"]) < 400_000, "bounded so it fits the diag channel"


async def test_the_render_runs_in_a_thread_and_the_loop_only_copies():
    import threading
    seen = {}
    from src import analyst_chart_image as aci
    real = aci.render

    def spy(prep):
        seen["thread"] = threading.current_thread() is threading.main_thread()
        return real(prep)

    entry = diag_catalog._REGISTRY["read.analyst_chart_image"]
    orig = entry.offload
    entry.offload = spy
    try:
        out = await diag_catalog.run_async("read.analyst_chart_image", _engine(),
                                           {"symbol": "XYZUSDT"})
    finally:
        entry.offload = orig
    assert out["ok"] and out["result"]["png_base64"]
    assert seen["thread"] is False, "the PNG must not be drawn on the event loop's thread"


async def test_a_refusal_is_named_and_never_drawn():
    out = await diag_catalog.run_async("read.analyst_chart_image", _engine(n=10),
                                       {"symbol": "XYZUSDT", "tf": "1h"})
    assert out["ok"] and out["result"] == {
        "symbol": "XYZUSDT", "tf": "1h", "readable": False, "reason": "short_series",
        "bars_available": 10}
    bad_tf = diag_catalog.run("read.analyst_chart_image", _engine(), {"symbol": "XYZUSDT",
                                                                       "tf": "5m"})
    assert bad_tf["result"]["readable"] is False and "tf must be" in bad_tf["result"]["reason"]
    none = diag_catalog.run("read.analyst_chart_image", _engine(), {"symbol": "NOPEUSDT"})
    assert none["result"]["reason"] == "no_candles"
