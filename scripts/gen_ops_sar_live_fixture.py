#!/usr/bin/env python3
"""Generate ops' live-SAR freshness fixture from THIS engine.

Ops cannot import the engine, so its tests run against saved engine output. That
output has to be *produced*, not typed: a fixture whose keys and values the test
author chose asserts the author's assumption back at itself and goes green over
dead code (#798), and it is how ops read ``entry_regime`` for months while
nothing wrote it (#817).

So this script drives the real ``sar_live_shadow`` — ``new_arm``, ``sweep``,
``SarLiveLedger.flush``, including the ``anchor_bars_behind`` stamp
``observe_signal`` computes — against a real ``HistoricalDataStore``, and writes what
the engine actually wrote. Regenerate after any change to the arm row shape:

    python3 scripts/gen_ops_sar_live_fixture.py \
        ../360ce-ops/tests/fixtures_sar_live_freshness.json

The scenario is the owner's 2026-07-30 export, reproduced: two KORUUSDT SHORT
arms whose candles stopped arriving (the symbol rotated out of the scan
universe), beside one SLXUSDT arm that is still advancing. On the old code all
three rendered identically, as "running".

The clock stops at **50 minutes** past entry rather than the owner's 2h19m, and
that is deliberate: past ``SAR_LIVE_SHADOW_ABANDON_SEC`` (1h) the engine now
retires a stalled arm as ``INSUFFICIENT / candle_feed_stalled``, so a 2h19m
snapshot would contain no stalled-but-open row at all. The window this fixture
captures is the one where the ops page has to tell the truth on its own — the
first hour, while the arm is still in the book.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import sar_live_shadow as live  # noqa: E402
from src.historical_data import HistoricalDataStore  # noqa: E402
from src.sar_exit_shadow import parabolic_sar_live  # noqa: E402

STEP, MAX_STEP = 0.02, 0.2
T0 = 1_700_000_000_000.0
WIDTHS = {"5m": 300_000.0, "15m": 900_000.0}


def _falling(n: int, start: float, dn: float) -> list[tuple[float, float, float, float]]:
    """A clean downtrend, so SAR sits above price and agrees with a SHORT."""
    out = []
    for i in range(n):
        c = start - i * dn
        out.append((c + dn * 0.3, c + dn * 0.8, c - dn * 0.8, c - dn * 0.3))
    return out


#: Every series ends on the same instant, so "how far behind is this arm" is a
#: fact about the feed rather than an artefact of where the fixture starts.
T_END = T0 + 400 * WIDTHS["15m"]

# KORUUSDT's price ran 5.9% against the trade while its candles were frozen —
# the parked stop is behind price and the arm never acted. SLXUSDT is the
# control: still below its parked stop, so nothing should have fired there.
PRICES = {"KORUUSDT": 12.47, "SLXUSDT": 0.0855}


def _seed(store, symbol: str, tf: str, bars) -> float:
    """Seed ``bars`` so the LAST one closes exactly at ``T_END``."""
    width = WIDTHS[tf]
    first = T_END - len(bars) * width
    for i, (o, h, lo, c) in enumerate(bars):
        store.update_candle(symbol, tf, {
            "open": o, "high": h, "low": lo, "close": c, "volume": 1.0,
            "open_time": first + i * width,
        })
    return first + (len(bars) - 1) * width


def main(out_path: str) -> None:
    store = HistoricalDataStore()
    ledger = live.SarLiveLedger(path="/tmp/gen_ops_sar_live_fixture.json")
    opened_at = T_END / 1000.0

    # --- The two stalled arms: KORUUSDT SHORT, 5m and 15m --------------------
    for tf, bars in (("5m", _falling(240, 12.60, 0.004)),
                     ("15m", _falling(80, 13.00, 0.015))):
        last = _seed(store, "KORUUSDT", tf, bars)
        sar = parabolic_sar_live([b[1] for b in bars], [b[2] for b in bars],
                                 STEP, MAX_STEP, last_closed_ms=last)
        ledger.add(live.new_arm(
            signal_id="BRKDN-C74F2BE4", symbol="KORUUSDT", side="SHORT",
            setup_class="BREAKDOWN_SHORT", timeframe=tf,
            entry=11.77, stop_loss=12.1231, tp1=11.26,
            sar=sar, opened_ms=last,
            anchor_bars_behind=live.bars_behind(last, tf, opened_at),
            now_ts=opened_at,
        ))

    # --- The advancing arm: SLXUSDT SHORT, 15m ------------------------------
    slx = _falling(80, 0.0900, 0.00005)
    slx_last = _seed(store, "SLXUSDT", "15m", slx)
    slx_sar = parabolic_sar_live([b[1] for b in slx], [b[2] for b in slx],
                                 STEP, MAX_STEP, last_closed_ms=slx_last)
    ledger.add(live.new_arm(
        signal_id="MVRTP-F22476CD", symbol="SLXUSDT", side="SHORT",
        setup_class="MOVER_TREND_PULLBACK", timeframe="15m",
        entry=0.08592, stop_loss=0.08787286, tp1=0.083565987072,
        sar=slx_sar, opened_ms=slx_last,
        anchor_bars_behind=live.bars_behind(slx_last, "15m", opened_at),
        now_ts=opened_at,
    ))

    # Three more SLX bars close over the next 45 minutes. KORUUSDT's candles
    # never move again — the arms differ only in what the feed did to them.
    close = slx[-1][3]
    for k in range(3):
        close -= 0.00005
        store.update_candle("SLXUSDT", "15m", {
            "open": close + 0.00002, "high": close + 0.00004,
            "low": close - 0.00004, "close": close - 0.00002, "volume": 1.0,
            "open_time": T_END + k * WIDTHS["15m"],
        })
        live.sweep(store, price_fn=PRICES.get, ledger=ledger,
                   now_ts=opened_at + (k + 1) * 900.0)

    # 50 minutes past entry: SLX is mid-bar and current, KORUUSDT is stalled and
    # still inside the abandon bound, so both states are in one fixture.
    live.sweep(store, price_fn=PRICES.get, ledger=ledger,
               now_ts=opened_at + 50 * 60)
    ledger.flush(force=True)

    payload = json.load(open("/tmp/gen_ops_sar_live_fixture.json"))
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)
    for row in payload["open"]:
        print(f"{row['symbol']:9} {row['timeframe']:3} bars={row['bars_seen']} "
              f"behind={row['bars_behind']:.2f} stalled={row['stalled']} "
              f"stop={row['sar_stop']:.6g} price={row['current_price']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "fixtures_sar_live_freshness.json")
