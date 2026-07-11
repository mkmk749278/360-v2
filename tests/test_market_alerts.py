"""Market Alerts — detectors, AlertService lifecycle, FCM push contract.

Detectors are exercised on synthetic candle arrays; the RSI-divergence
test monkeypatches the RSI series so the test pins the divergence
GEOMETRY logic (pivots, zone gates, recency) rather than re-deriving
Wilder's RSI numerically.
"""
from __future__ import annotations

import json
from typing import List, Optional

import numpy as np
import pytest

import src.push_notifications as push
from src.alerts import detectors
from src.alerts.models import Alert, AlertType, make_alert
from src.alerts.service import AlertService, _cooldown_seconds


# ---------------------------------------------------------------------------
# Candle factories
# ---------------------------------------------------------------------------


def _candles(closes: List[float], highs=None, lows=None, volumes=None) -> dict:
    close = np.asarray(closes, dtype=np.float64)
    return {
        "open": close.copy(),
        "high": np.asarray(highs, dtype=np.float64) if highs is not None else close * 1.001,
        "low": np.asarray(lows, dtype=np.float64) if lows is not None else close * 0.999,
        "close": close,
        "volume": (
            np.asarray(volumes, dtype=np.float64)
            if volumes is not None
            else np.full(len(close), 100.0)
        ),
    }


def _rising(n: int = 120, start: float = 100.0, step: float = 0.5) -> List[float]:
    return [start + i * step for i in range(n)]


def _falling(n: int = 120, start: float = 100.0, step: float = 0.5) -> List[float]:
    return [start - i * step for i in range(n)]


# ---------------------------------------------------------------------------
# RSI extremes
# ---------------------------------------------------------------------------


def test_rsi_overbought_fires_on_monotonic_rally():
    alert = detectors.detect_rsi_extreme("BTCUSDT", "1h", _candles(_rising()))
    assert alert is not None
    assert alert.alert_type == AlertType.RSI_OVERBOUGHT.value
    assert alert.timeframe == "1h"
    assert alert.symbol == "BTCUSDT"
    assert alert.bias == "BEARISH"
    assert alert.metrics["rsi"] >= 80.0


def test_rsi_oversold_fires_on_monotonic_dump():
    alert = detectors.detect_rsi_extreme("XRPUSDT", "4h", _candles(_falling()))
    assert alert is not None
    assert alert.alert_type == AlertType.RSI_OVERSOLD.value
    assert alert.metrics["rsi"] <= 20.0


def test_rsi_extreme_silent_on_flat_series():
    closes = [100.0 + (0.1 if i % 2 else -0.1) for i in range(120)]
    assert detectors.detect_rsi_extreme("BTCUSDT", "1h", _candles(closes)) is None


def test_rsi_extreme_needs_min_candles():
    assert detectors.detect_rsi_extreme("BTCUSDT", "1h", _candles(_rising(20))) is None
    assert detectors.detect_rsi_extreme("BTCUSDT", "1h", None) is None


# ---------------------------------------------------------------------------
# RSI divergence — pivots + zone gates via a controlled RSI series
# ---------------------------------------------------------------------------


def _divergence_fixture(monkeypatch, *, bearish: bool) -> dict:
    """Price makes a second extreme BEYOND the first; injected RSI makes a
    weaker second extreme.  Pivot2 sits close to the right edge so the
    recency gate passes (k=2 → pivot confirmed 2 candles back)."""
    n = 80
    base = np.full(n, 100.0)
    rsi = np.full(n, 50.0)
    p1, p2 = n - 20, n - 3  # pivot indices within the 40-candle lookback
    if bearish:
        base[p1], base[p2] = 110.0, 112.0          # price higher high
        rsi[p1], rsi[p2] = 75.0, 62.0               # RSI lower high, zone ≥ 60
        candles = _candles(list(base), highs=list(base), lows=list(base - 1))
    else:
        base[p1], base[p2] = 90.0, 88.0             # price lower low
        rsi[p1], rsi[p2] = 25.0, 38.0               # RSI higher low, zone ≤ 40
        candles = _candles(list(base), highs=list(base + 1), lows=list(base))
    monkeypatch.setattr(detectors, "_rsi", lambda close, period: rsi[: len(close)])
    return candles


def test_bearish_divergence_detected(monkeypatch):
    candles = _divergence_fixture(monkeypatch, bearish=True)
    alert = detectors.detect_rsi_divergence("BTCUSDT", "4h", candles)
    assert alert is not None
    assert alert.alert_type == AlertType.RSI_BEARISH_DIVERGENCE.value
    assert alert.bias == "BEARISH"


def test_bullish_divergence_detected(monkeypatch):
    candles = _divergence_fixture(monkeypatch, bearish=False)
    alert = detectors.detect_rsi_divergence("ETHUSDT", "1h", candles)
    assert alert is not None
    assert alert.alert_type == AlertType.RSI_BULLISH_DIVERGENCE.value
    assert alert.bias == "BULLISH"


def test_divergence_zone_gate_blocks_midrange_rsi(monkeypatch):
    """Same geometry but the first RSI pivot sits mid-range → no alert."""
    n = 80
    base = np.full(n, 100.0)
    rsi = np.full(n, 50.0)
    p1, p2 = n - 20, n - 3
    base[p1], base[p2] = 110.0, 112.0
    rsi[p1], rsi[p2] = 55.0, 45.0  # below the 60 zone-high gate
    candles = _candles(list(base), highs=list(base), lows=list(base - 1))
    monkeypatch.setattr(detectors, "_rsi", lambda close, period: rsi[: len(close)])
    assert detectors.detect_rsi_divergence("BTCUSDT", "4h", candles) is None


def test_divergence_stale_pivot_blocked(monkeypatch):
    """Second pivot far from the right edge → archaeology, not an alert."""
    n = 80
    base = np.full(n, 100.0)
    rsi = np.full(n, 50.0)
    p1, p2 = n - 30, n - 15
    base[p1], base[p2] = 110.0, 112.0
    rsi[p1], rsi[p2] = 75.0, 62.0
    candles = _candles(list(base), highs=list(base), lows=list(base - 1))
    monkeypatch.setattr(detectors, "_rsi", lambda close, period: rsi[: len(close)])
    assert detectors.detect_rsi_divergence("BTCUSDT", "4h", candles) is None


# ---------------------------------------------------------------------------
# Abnormal volatility + volume spike
# ---------------------------------------------------------------------------


def test_abnormal_volatility_fires_on_range_expansion():
    n = 100
    closes = [100.0] * n
    highs = [100.5] * n
    lows = [99.5] * n
    closes[-1], highs[-1], lows[-1] = 95.0, 100.5, 94.5  # 6-point range vs 1-point ATR
    alert = detectors.detect_abnormal_volatility(
        "BTCUSDT", "15m", _candles(closes, highs=highs, lows=lows)
    )
    assert alert is not None
    assert alert.alert_type == AlertType.ABNORMAL_VOLATILITY.value
    assert alert.metrics["tr_mult"] >= 3.0
    assert alert.metrics["move_pct"] < 0


def test_abnormal_volatility_silent_on_normal_candle():
    n = 100
    candles = _candles([100.0] * n, highs=[100.5] * n, lows=[99.5] * n)
    assert detectors.detect_abnormal_volatility("BTCUSDT", "15m", candles) is None


def test_volume_spike_fires():
    n = 100
    volumes = [100.0] * n
    volumes[-1] = 900.0
    alert = detectors.detect_volume_spike(
        "DOGEUSDT", "15m", _candles([100.0] * n, volumes=volumes)
    )
    assert alert is not None
    assert alert.alert_type == AlertType.VOLUME_SPIKE.value
    assert alert.metrics["volume_mult"] >= 5.0


def test_volume_spike_silent_on_average_volume():
    n = 100
    candles = _candles([100.0] * n, volumes=[100.0] * n)
    assert detectors.detect_volume_spike("DOGEUSDT", "15m", candles) is None


# ---------------------------------------------------------------------------
# Near horizontal S/R
# ---------------------------------------------------------------------------


class _FakeBook:
    def __init__(self, *levels) -> None:
        self._levels = list(levels)

    def get_levels(self, symbol):
        return list(self._levels)


def _level(price: float, type_: str, touches: int = 4):
    from src.level_book import Level

    return Level(price=price, type=type_, source_tf="1d", touches=touches, score=5.0)


def _touch_candles(
    level: float, *, kind: str = "resistance", touches: int = 3, n: int = 60
) -> dict:
    """Series that tags ``level`` in ``touches`` DISTINCT events (prominent
    ~1% excursions between them) and ends 0.2% away, ready to fire."""
    sign = -1.0 if kind == "resistance" else 1.0
    away = level * (1.0 + sign * 0.01)
    closes = [away] * n
    highs = [away * 1.001] * n
    lows = [away * 0.999] * n
    for k in range(touches):
        i = n - 1 - 6 * k  # ≥5 out-of-band bars between events
        closes[i] = level * (1.0 + sign * 0.002)
        if kind == "resistance":
            highs[i], lows[i] = level, level * 0.995
        else:
            highs[i], lows[i] = level * 1.005, level
    return _candles(closes, highs=highs, lows=lows)


def test_near_resistance_fires_below_level():
    candles = _touch_candles(100.2, kind="resistance", touches=3)
    alert = detectors.detect_near_level(
        "BTCUSDT", "1h", candles, _FakeBook(_level(100.2, "resistance"))
    )
    assert alert is not None
    assert alert.alert_type == AlertType.NEAR_RESISTANCE.value
    assert alert.metrics["level_price"] == 100.2
    # `touches` is the honest distinct re-count, not the book's tally.
    assert alert.metrics["touches"] == 3


def test_near_support_fires_above_level():
    candles = _touch_candles(99.8, kind="support", touches=3)
    alert = detectors.detect_near_level(
        "BTCUSDT", "1h", candles, _FakeBook(_level(99.8, "support"))
    )
    assert alert is not None
    assert alert.alert_type == AlertType.NEAR_SUPPORT.value


def test_crossed_level_is_skipped():
    """A 'resistance' sitting BELOW price is broken — not a near-resistance."""
    candles = _candles([100.0] * 60)
    alert = detectors.detect_near_level(
        "BTCUSDT", "1h", candles, _FakeBook(_level(99.8, "resistance"))
    )
    assert alert is None


def test_no_book_no_alert():
    candles = _candles([100.0] * 60)
    assert detectors.detect_near_level("BTCUSDT", "1h", candles, None) is None


def test_near_level_metrics_carry_zone_geometry():
    """The app draws the 100eyes-style zone box + zooms to the setup from
    these fields — wire contract, not decoration."""
    candles = _touch_candles(100.2, kind="resistance", touches=3, n=60)
    alert = detectors.detect_near_level(
        "BTCUSDT", "1h", candles, _FakeBook(_level(100.2, "resistance"))
    )
    assert alert is not None
    m = alert.metrics
    assert m["touch_count"] == m["touches"] == 3
    assert m["zone_low"] <= 100.2 <= m["zone_high"]
    # first touch sits 12 bars back (n-1-6·2), last is the final bar
    assert m["first_touch_bars_ago"] == 12
    assert m["last_touch_bars_ago"] == 0
    assert "(3 touches)" in alert.message


def test_chop_range_rejected():
    """Price living AT the level is a trading range, not S/R — the
    '523 touches' spam class must never fire."""
    candles = _candles([100.2] * 60)  # every bar straddles the level
    alert = detectors.detect_near_level(
        "BTCUSDT", "1h", candles, _FakeBook(_level(100.2, "resistance", touches=523))
    )
    assert alert is None


def test_rejected_candidate_never_shadows_a_clean_level():
    """The old ``nearest_level`` picked ONE (score-biased) candidate; if it
    was junk, a genuinely clean level nearby never alerted.  The detector
    now enumerates: a candidate that fails the floors must not shadow a
    survivor."""
    candles = _touch_candles(100.2, kind="resistance", touches=3)
    # Book-side junk: far side of price (a "support" above price is a
    # crossed level) — filtered out, clean resistance still fires.
    junk = _level(100.25, "support", touches=523)
    clean = _level(100.2, "resistance", touches=4)
    alert = detectors.detect_near_level(
        "BTCUSDT", "1h", candles, _FakeBook(junk, clean)
    )
    assert alert is not None
    assert alert.metrics["level_price"] == 100.2


# ---------------------------------------------------------------------------
# _distinct_touch_events — the state machine behind honest touch counts
# ---------------------------------------------------------------------------


def _touch_arrays(candles: dict):
    return candles["high"], candles["low"], candles["close"]


def test_distinct_touches_counts_separated_events():
    h, l, c = _touch_arrays(_touch_candles(100.0, touches=3))
    events, in_band, _, _ = detectors._distinct_touch_events(
        100.0, h, l, c, tol_pct=0.15, min_sep_bars=3, min_leave_pct=0.5
    )
    assert len(events) == 3
    assert in_band == 3  # each event is a single bar in this fixture


def test_consecutive_in_band_bars_are_one_event():
    closes = [99.0] * 40 + [100.0] * 5  # ends hovering at the level
    highs = [x * 1.001 for x in closes]
    lows = [x * 0.999 for x in closes]
    events, in_band, _, _ = detectors._distinct_touch_events(
        100.0,
        np.asarray(highs), np.asarray(lows), np.asarray(closes),
        tol_pct=0.15, min_sep_bars=3, min_leave_pct=0.5,
    )
    assert len(events) == 1
    assert in_band == 5


def test_retouch_without_prominence_not_counted():
    """Leaving the band for long enough but staying CLOSE to the level is
    hovering, not a re-test."""
    level = 100.0
    closes = [level] * 3 + [level * 1.003] * 5 + [level] * 3  # 0.3% < 0.5%
    highs = [x * 1.0005 for x in closes]
    lows = [x * 0.9995 for x in closes]
    events, _, _, _ = detectors._distinct_touch_events(
        level,
        np.asarray(highs), np.asarray(lows), np.asarray(closes),
        tol_pct=0.15, min_sep_bars=3, min_leave_pct=0.5,
    )
    assert len(events) == 1


def test_retouch_without_separation_not_counted():
    """A single-bar spike away (even a big one) doesn't re-arm."""
    level = 100.0
    closes = [level] * 3 + [level * 1.02] * 1 + [level] * 3  # 1 bar < 3
    highs = [x * 1.0005 for x in closes]
    lows = [x * 0.9995 for x in closes]
    events, _, _, _ = detectors._distinct_touch_events(
        level,
        np.asarray(highs), np.asarray(lows), np.asarray(closes),
        tol_pct=0.15, min_sep_bars=3, min_leave_pct=0.5,
    )
    assert len(events) == 1


def test_zone_bounds_from_touch_extremes_within_band():
    level = 100.0
    candles = _touch_candles(level, kind="resistance", touches=3)
    h, l, c = _touch_arrays(candles)
    _, _, zone_low, zone_high = detectors._distinct_touch_events(
        level, h, l, c, tol_pct=0.15, min_sep_bars=3, min_leave_pct=0.5
    )
    lo, hi = level * (1 - 0.0015), level * (1 + 0.0015)
    assert lo <= zone_low <= zone_high <= hi
    assert zone_low <= level <= zone_high


# ---------------------------------------------------------------------------
# AlertService — sweep, cooldown, staleness, persistence, feed
# ---------------------------------------------------------------------------


class _FakeStore:
    """Data store stub: overbought rally on every timeframe, fresh klines."""

    def __init__(self, age: Optional[float] = 5.0) -> None:
        self._age = age
        self.candles = _candles(_rising())

    def get_candles(self, symbol, interval):
        return self.candles

    def last_kline_age_seconds(self, symbol, interval):
        return self._age


def _service(
    tmp_path, store=None, on_alert=None, symbols=None, volume_24h_getter=None
) -> AlertService:
    return AlertService(
        data_store=store or _FakeStore(),
        level_book_getter=lambda: None,
        symbols_getter=lambda: symbols or ["BTCUSDT"],
        on_alert=on_alert,
        persist_path=str(tmp_path / "alerts.json"),
        volume_24h_getter=volume_24h_getter,
    )


async def test_sweep_fires_and_invokes_callback(tmp_path):
    received: List[Alert] = []
    service = _service(tmp_path, on_alert=received.append)
    fired = await service.sweep()
    assert any(a.alert_type == AlertType.RSI_OVERBOUGHT.value for a in fired)
    assert received == fired
    assert service.recent(limit=10)  # feed populated, newest first
    assert service.recent(limit=10)[0]["symbol"] == "BTCUSDT"


async def test_cooldown_blocks_immediate_refire(tmp_path):
    service = _service(tmp_path)
    first = await service.sweep()
    assert first
    # Same conditions, new closed candle: cooldown must swallow the refire.
    service._last_eval_ts.clear()
    second = await service.sweep()
    assert second == []


async def test_cooldown_expires(tmp_path):
    service = _service(tmp_path)
    await service.sweep()
    horizon = max(_cooldown_seconds(t.value, "4h") for t in AlertType) + 1
    service._last_fired = {k: v - horizon for k, v in service._last_fired.items()}
    service._symbol_fires.clear()  # the per-symbol window also ages out
    service._last_eval_ts.clear()
    assert await service.sweep()


async def test_same_candle_not_reevaluated(tmp_path):
    service = _service(tmp_path)
    fired = await service.sweep()
    assert fired
    # No new kline (same update ts) → detectors skipped entirely.
    fired2 = await service.sweep()
    assert fired2 == []


async def test_stale_feed_never_alerts(tmp_path):
    service = _service(tmp_path, store=_FakeStore(age=10 * 24 * 3600.0))
    assert await service.sweep() == []


async def test_persistence_roundtrip(tmp_path):
    service = _service(tmp_path)
    await service.sweep()
    service._last_persist = 0.0  # defeat the write throttle
    await service._persist_maybe()
    path = tmp_path / "alerts.json"
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["alerts"] and data["last_fired"]

    restored = _service(tmp_path)
    assert restored.recent(limit=10)
    assert restored._last_fired  # cooldowns survive a restart → no re-push
    restored._last_eval_ts.clear()
    fired = await restored.sweep()
    # The 4h/1h alerts were delivered pre-restart — their persisted
    # cooldowns block a refire.  The 15m alert was budget-dropped (never
    # delivered), so it may legitimately fire now.
    assert all(a.timeframe == "15m" for a in fired)


async def test_recent_filters(tmp_path):
    service = _service(tmp_path)
    service._publish(make_alert(AlertType.VOLUME_SPIKE, "ETHUSDT", "15m", 1.0, "x"))
    service._publish(make_alert(AlertType.RSI_OVERSOLD, "BTCUSDT", "1h", 2.0, "y"))
    assert len(service.recent(limit=10)) == 2
    assert service.recent(limit=10, symbol="ethusdt")[0]["symbol"] == "ETHUSDT"
    only = service.recent(limit=10, alert_type=AlertType.RSI_OVERSOLD.value)
    assert len(only) == 1 and only[0]["alert_type"] == "RSI_OVERSOLD"


async def test_sweep_survives_broken_symbol_getter(tmp_path):
    service = AlertService(
        data_store=_FakeStore(),
        level_book_getter=lambda: None,
        symbols_getter=lambda: (_ for _ in ()).throw(RuntimeError("boom")),
        persist_path=str(tmp_path / "alerts.json"),
    )
    assert await service.sweep() == []


# ---------------------------------------------------------------------------
# Universe gate — alerts only for liquid pairs (majors + midcaps)
# ---------------------------------------------------------------------------


async def test_universe_gate_skips_low_volume_symbol(tmp_path):
    vols = {"BTCUSDT": 900_000_000.0, "SMALLUSDT": 10_000_000.0}
    service = _service(
        tmp_path,
        symbols=["BTCUSDT", "SMALLUSDT"],
        volume_24h_getter=vols.get,
    )
    fired = await service.sweep()
    assert fired and all(a.symbol == "BTCUSDT" for a in fired)


async def test_universe_gate_threshold_boundary(tmp_path):
    """Exactly at the threshold passes (>= semantics)."""
    from src.alerts import service as service_mod

    service = _service(
        tmp_path, volume_24h_getter=lambda s: float(
            service_mod.ALERTS_MIN_VOLUME_24H_USD
        )
    )
    assert await service.sweep()


async def test_universe_gate_unknown_volume_skips(tmp_path):
    service = _service(tmp_path, volume_24h_getter=lambda s: None)
    assert await service.sweep() == []


async def test_universe_gate_absent_getter_is_open(tmp_path):
    service = _service(tmp_path)  # no getter injected
    assert await service.sweep()


async def test_universe_gate_disabled_when_threshold_zero(tmp_path, monkeypatch):
    from src.alerts import service as service_mod

    monkeypatch.setattr(service_mod, "ALERTS_MIN_VOLUME_24H_USD", 0.0)
    service = _service(tmp_path, volume_24h_getter=lambda s: 1_000.0)
    assert await service.sweep()


async def test_universe_getter_exception_skips_symbol_not_sweep(tmp_path):
    def getter(symbol: str):
        if symbol == "BROKENUSDT":
            raise RuntimeError("boom")
        return 900_000_000.0

    service = _service(
        tmp_path, symbols=["BROKENUSDT", "BTCUSDT"], volume_24h_getter=getter
    )
    fired = await service.sweep()
    assert fired and all(a.symbol == "BTCUSDT" for a in fired)


# ---------------------------------------------------------------------------
# Feed hygiene — restored-feed cleanup on deploy
# ---------------------------------------------------------------------------


def _write_feed(tmp_path, alerts: List[Alert]) -> None:
    (tmp_path / "alerts.json").write_text(
        json.dumps({"alerts": [a.to_dict() for a in alerts], "last_fired": {}})
    )


def test_load_drops_pre_geometry_near_level_alerts(tmp_path):
    """Pre-v3 near-level alerts (no distinct-touch geometry) are the
    '523 touches' junk cohort — gone on the first post-deploy restart."""
    _write_feed(tmp_path, [
        make_alert(
            AlertType.NEAR_SUPPORT, "BTCUSDT", "1h", 100.0, "old junk",
            {"level_price": 100.0, "touches": 523},
        ),
        make_alert(AlertType.RSI_OVERSOLD, "BTCUSDT", "1h", 100.0, "keep"),
    ])
    service = _service(tmp_path)
    feed = service.recent(limit=10)
    assert len(feed) == 1
    assert feed[0]["alert_type"] == "RSI_OVERSOLD"


def test_load_keeps_v3_near_level_alerts(tmp_path):
    _write_feed(tmp_path, [
        make_alert(
            AlertType.NEAR_SUPPORT, "BTCUSDT", "1h", 100.0, "v3",
            {
                "level_price": 100.0, "touches": 4, "touch_count": 4,
                "zone_low": 99.9, "zone_high": 100.1,
                "first_touch_bars_ago": 30, "last_touch_bars_ago": 2,
            },
        ),
    ])
    service = _service(tmp_path)
    assert len(service.recent(limit=10)) == 1


async def test_first_sweep_purges_small_cap_restored_alerts(tmp_path):
    """A restored feed full of small caps cleans on the first sweep (the
    purge can't run in _load — volume data only exists after the boot
    pair refresh) and the persisted file follows."""
    _write_feed(tmp_path, [
        make_alert(AlertType.RSI_OVERSOLD, "SMALLUSDT", "1h", 1.0, "small cap"),
        make_alert(AlertType.RSI_OVERSOLD, "ETHUSDT", "1h", 100.0, "major"),
    ])
    vols = {"BTCUSDT": 900_000_000.0, "ETHUSDT": 500_000_000.0}
    service = _service(tmp_path, volume_24h_getter=vols.get)
    assert len(service.recent(limit=10)) == 2  # restore is gate-blind
    await service.sweep()
    feed = service.recent(limit=10)
    symbols = {a["symbol"] for a in feed}
    assert "SMALLUSDT" not in symbols and "ETHUSDT" in symbols
    service._last_persist = 0.0
    await service._persist_maybe()
    on_disk = json.loads((tmp_path / "alerts.json").read_text())
    assert all(a["symbol"] != "SMALLUSDT" for a in on_disk["alerts"])


async def test_restored_feed_order_survives_purge(tmp_path):
    """The purge rebuild must keep the feed newest-first."""
    old = make_alert(AlertType.RSI_OVERSOLD, "ETHUSDT", "1h", 1.0, "older")
    new = make_alert(AlertType.RSI_OVERBOUGHT, "ETHUSDT", "1h", 2.0, "newer")
    _write_feed(tmp_path, [new, old])  # feed serializes newest-first
    vols = {"BTCUSDT": 900_000_000.0, "ETHUSDT": 500_000_000.0}
    service = _service(tmp_path, volume_24h_getter=vols.get)
    await service.sweep()
    feed = service.recent(limit=10)
    eth = [a for a in feed if a["symbol"] == "ETHUSDT"]
    assert [a["message"] for a in eth][-2:] == ["newer", "older"]


# ---------------------------------------------------------------------------
# Spam controls — quality floor, coalescing, symbol budget, push curation
# ---------------------------------------------------------------------------


def test_near_level_touch_floor_blocks_junk_levels():
    """A once-touched 'level' is a visited price, not a level (the '1
    touches' cards were the worst of the feed spam).  The floor applies to
    the DISTINCT re-count — a book tally of 9 can't rescue a price the
    series only visited once."""
    candles = _touch_candles(100.2, kind="resistance", touches=1)
    alert = detectors.detect_near_level(
        "BTCUSDT", "1h", candles, _FakeBook(_level(100.2, "resistance", touches=9))
    )
    assert alert is None


def test_divergence_metrics_carry_pivot_geometry(monkeypatch):
    """The app draws the divergence line from these fields — they are a
    wire contract, not decoration."""
    closes = [100.0] * 80
    highs = list(closes)
    highs[70] = 110.0  # pivot A
    highs[77] = 112.0  # pivot B (higher high, near right edge)
    fake_rsi = np.full(80, 50.0)
    fake_rsi[70] = 75.0
    fake_rsi[77] = 65.0  # lower RSI high → bearish divergence
    monkeypatch.setattr(detectors, "_rsi", lambda closes_, period: fake_rsi)
    alert = detectors.detect_rsi_divergence(
        "BTCUSDT", "1h", _candles(closes, highs=highs)
    )
    assert alert is not None
    assert alert.alert_type == AlertType.RSI_BEARISH_DIVERGENCE.value
    m = alert.metrics
    lookback = len(closes)
    assert m["pivot_a_price"] == 110.0 and m["pivot_b_price"] == 112.0
    assert m["pivot_a_bars_ago"] == lookback - 1 - 70
    assert m["pivot_b_bars_ago"] == lookback - 1 - 77


async def test_same_candle_volume_and_volatility_coalesce(tmp_path):
    service = _service(tmp_path)
    found = [
        make_alert(AlertType.ABNORMAL_VOLATILITY, "RAVEUSDT", "15m", 1.0, "vol"),
        make_alert(AlertType.VOLUME_SPIKE, "RAVEUSDT", "15m", 1.0, "spike"),
    ]
    out = service._coalesce_same_candle(found)
    assert [a.alert_type for a in out] == [AlertType.VOLUME_SPIKE.value]
    # Different timeframe pairs never coalesce.
    found2 = [
        make_alert(AlertType.ABNORMAL_VOLATILITY, "RAVEUSDT", "1h", 1.0, "vol"),
        make_alert(AlertType.VOLUME_SPIKE, "RAVEUSDT", "15m", 1.0, "spike"),
    ]
    assert len(service._coalesce_same_candle(found2)) == 2


async def test_symbol_budget_caps_burst_and_keeps_priority(tmp_path):
    """The rally store trips RSI-overbought on 15m/1h/4h at once; the
    default budget (2/window) must keep the higher timeframes and drop
    the 15m echo."""
    service = _service(tmp_path)
    fired = await service.sweep()
    assert len(fired) == 2
    assert {a.timeframe for a in fired} == {"4h", "1h"}


async def test_budget_rejection_does_not_consume_cooldown(tmp_path):
    service = _service(tmp_path)
    await service.sweep()  # consumes the 2-alert budget (4h + 1h)
    # The 15m alert was budget-dropped: its cooldown must NOT be stamped,
    # so once the window clears it fires on the next closed candle.
    assert not any("|15m" in k for k in service._last_fired)
    service._symbol_fires.clear()
    service._last_eval_ts.clear()
    fired = await service.sweep()
    assert [a.timeframe for a in fired] == ["15m"]


async def test_push_gated_to_configured_timeframes(tmp_path):
    received: List[Alert] = []
    service = _service(tmp_path, on_alert=received.append)
    fired = await service.sweep()  # 4h + 1h under the default budget
    assert {a.timeframe for a in fired} == {"4h", "1h"}
    assert {a.timeframe for a in received} == {"4h", "1h"}
    # A 15m publish lands in the feed but never pushes.
    received.clear()
    service._publish(
        make_alert(AlertType.VOLUME_SPIKE, "ETHUSDT", "15m", 1.0, "x")
    )
    assert received == []
    assert service.recent(limit=1)[0]["symbol"] == "ETHUSDT"


async def test_push_hourly_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "src.alerts.service.ALERTS_PUSH_MAX_PER_HOUR", 2
    )
    received: List[Alert] = []
    service = _service(tmp_path, on_alert=received.append)
    for i in range(4):
        service._publish(
            make_alert(AlertType.RSI_OVERSOLD, f"S{i}USDT", "1h", 1.0, "y")
        )
    assert len(received) == 2  # pushes capped
    assert len(service.recent(limit=10)) == 4  # feed keeps everything


# ---------------------------------------------------------------------------
# FCM push contract
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_push(monkeypatch):
    push._reset_rate_window_for_tests()
    yield
    push._reset_rate_window_for_tests()


def _capture_sends(monkeypatch):
    sent = []
    monkeypatch.setattr(push, "_firebase_ready", lambda: True)
    monkeypatch.setattr(
        push,
        "_send_blocking",
        lambda topic, title, body, data, channel_id: sent.append(
            {"topic": topic, "title": title, "body": body, "data": data, "channel": channel_id}
        ),
    )
    return sent


def test_push_alert_payload(monkeypatch):
    sent = _capture_sends(monkeypatch)
    alert = make_alert(
        AlertType.RSI_OVERBOUGHT, "BTCUSDT", "1h", 64000.0, "RSI(14) at 83.2", {"rsi": 83.2}
    )
    push.push_alert(alert)
    assert len(sent) == 1
    msg = sent[0]
    assert msg["topic"] == push.FCM_ALERTS_TOPIC
    assert msg["title"] == "[BTCUSDT] RSI Extremely Overbought (1h)"
    assert msg["channel"] == "market_alerts"
    assert msg["data"]["route"] == "pulse_alerts"
    assert all(isinstance(v, str) for v in msg["data"].values())


class _Sig:
    class _Dir:
        value = "LONG"

    direction = _Dir()
    symbol = "BTCUSDT"
    entry = 64000.0
    stop_loss = 63400.0
    tp1 = 64600.0
    confidence = 78.0
    signal_id = "abc123"
    status = "TP2_HIT"
    pnl_pct = 2.41


def test_push_signal_published_payload(monkeypatch):
    sent = _capture_sends(monkeypatch)
    push.push_signal_published(_Sig())
    assert len(sent) == 1
    msg = sent[0]
    assert msg["topic"] == push.FCM_SIGNALS_TOPIC
    assert msg["title"] == "New Signal: LONG BTCUSDT"
    assert "64000" in msg["body"] and "63400" in msg["body"]
    assert msg["data"]["signal_id"] == "abc123"


def test_push_signal_outcome_uses_explicit_label(monkeypatch):
    sent = _capture_sends(monkeypatch)
    push.push_signal_outcome(_Sig(), "PROFIT_LOCKED")
    assert sent[0]["title"] == "BTCUSDT LONG closed — PROFIT LOCKED"
    assert sent[0]["data"]["status"] == "PROFIT_LOCKED"
    assert "+2.41%" in sent[0]["body"]


def test_push_never_raises_when_send_fails(monkeypatch):
    monkeypatch.setattr(push, "_firebase_ready", lambda: True)

    def _boom(*a, **k):
        raise RuntimeError("fcm down")

    monkeypatch.setattr(push, "_send_blocking", _boom)
    push.push_alert(
        make_alert(AlertType.VOLUME_SPIKE, "ETHUSDT", "15m", 1800.0, "vol")
    )  # must not raise


def test_push_noop_without_firebase(monkeypatch):
    sent = []
    monkeypatch.setattr(push, "_firebase_ready", lambda: False)
    monkeypatch.setattr(
        push, "_send_blocking", lambda *a, **k: sent.append(1)
    )
    push.push_signal_published(_Sig())
    assert sent == []


def test_rate_cap_drops_excess(monkeypatch):
    sent = _capture_sends(monkeypatch)
    monkeypatch.setattr(push, "FCM_MAX_SENDS_PER_MIN", 3)
    alert = make_alert(AlertType.VOLUME_SPIKE, "ETHUSDT", "15m", 1800.0, "vol")
    for _ in range(10):
        push.push_alert(alert)
    assert len(sent) == 3


def test_push_class_gates(monkeypatch):
    sent = _capture_sends(monkeypatch)
    monkeypatch.setattr(push, "FCM_PUSH_ALERTS_ENABLED", False)
    push.push_alert(make_alert(AlertType.VOLUME_SPIKE, "E", "15m", 1.0, "x"))
    monkeypatch.setattr(push, "FCM_PUSH_SIGNALS_ENABLED", False)
    push.push_signal_published(_Sig())
    monkeypatch.setattr(push, "FCM_PUSH_OUTCOMES_ENABLED", False)
    push.push_signal_outcome(_Sig(), "SL_HIT")
    assert sent == []


def test_master_switch_off(monkeypatch):
    sent = _capture_sends(monkeypatch)
    monkeypatch.setattr(push, "FCM_PUSH_ENABLED", False)
    push.push_alert(make_alert(AlertType.VOLUME_SPIKE, "E", "15m", 1.0, "x"))
    assert sent == []
