#!/usr/bin/env python3
"""Generate ops' SAR coverage fixture from THIS engine.

Ops cannot import the engine, so its tests run against saved engine output —
and that output has to be **produced, not typed**. A fixture whose keys the
test author chose asserts the author's assumption back at itself: that is #798
(a mocked ``exit_reason`` key going green over dead code), #817 (ops reading
``entry_regime`` for months while nothing wrote it), and most recently the
price-action lane card, whose ops fixture put the block at the payload's top
level while the engine nests it under ``derived`` — every ops test green over a
card that would have rendered NOT REPORTED against the real engine.

So this drives the real ``observe_signal`` against a real
``HistoricalDataStore``, and writes what ``SarLiveLedger.flush`` actually
wrote — including **where** the coverage block lands in the payload.

    python3 scripts/gen_ops_sar_coverage_fixture.py \
        ../360ce-ops/tests/fixtures_sar_coverage.json

The scenario is the production defect, reproduced rather than described. The
lane is configured for 5m and 15m; the store holds:

* ``BICOUSDT`` — both timeframes  → fully armed
* ``KORUUSDT`` — 15m only         → partly armed (``no_series`` on 5m)
* ``PIPPINUSDT`` — neither        → unarmed

That is the shape a guest-session audit found on 2026-08-08 by joining the
ledger to the closed-signal record: 124 of 152 delivered trades armed (81.6%),
and the 28 without running −1.643%/trade at 10.7% win against +0.753% and 43.5%
for the armed ones. The missing slice was overwhelmingly promoted movers, which
carry no WS kline subscription and are re-seeded by REST on a throttle — so
"no series for this symbol/timeframe" is not an exotic failure, it is the
normal state of the part of the book that loses the most money.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import sar_live_shadow as live  # noqa: E402
from src.channels.base import Signal  # noqa: E402
from src.historical_data import HistoricalDataStore  # noqa: E402
from src.smc import Direction  # noqa: E402

WIDTHS = {"5m": 300_000.0, "15m": 900_000.0}
T0 = 1_753_000_000_000.0


def _rising(n, start, step_up):
    return [
        (start + i * step_up, start + i * step_up + step_up * 0.5,
         start + i * step_up - step_up * 0.5, start + i * step_up)
        for i in range(n)
    ]


def _seed(store, symbol, tf, bars):
    width = WIDTHS[tf]
    last = 0.0
    for i, (o, h, lo, c) in enumerate(bars):
        last = T0 + i * width
        store.update_candle(symbol, tf, {
            "open": o, "high": h, "low": lo, "close": c,
            "volume": 1.0, "open_time": last,
        })
    return last


def main(out_path: str) -> None:
    tmp = "/tmp/gen_ops_sar_coverage_fixture.json"
    if os.path.exists(tmp):
        os.unlink(tmp)
    live.reset_sar_cache()
    ledger = live.SarLiveLedger(path=tmp)
    store = HistoricalDataStore()

    # Both timeframes present — this one arms fully.
    _seed(store, "BICOUSDT", "5m", _rising(240, 0.0500, 0.00002))
    last15 = _seed(store, "BICOUSDT", "15m", _rising(80, 0.0500, 0.00006))
    # 15m only — the 5m arm cannot open, and until now that left no trace.
    _seed(store, "KORUUSDT", "15m", _rising(80, 11.50, 0.01))
    # PIPPINUSDT is deliberately absent from the store entirely.

    now = (last15 + WIDTHS["15m"]) / 1000.0
    cases = [
        ("MVRTP-BICO01", "BICOUSDT", 0.05480, 0.05320, 0.05700),
        ("BRKDN-KORU01", "KORUUSDT", 12.290, 11.930, 12.800),
        ("MVRTP-PIPP01", "PIPPINUSDT", 0.31400, 0.30500, 0.32600),
    ]
    for signal_id, symbol, entry, sl, tp1 in cases:
        sig = Signal(
            channel="scalp", symbol=symbol, direction=Direction.LONG,
            entry=entry, stop_loss=sl, tp1=tp1, tp2=tp1 * 1.02,
            signal_id=signal_id, setup_class="MOVER_TREND_PULLBACK",
        )
        # The stop the evaluator SIZED for, which is what the arm's risk
        # denominator must come from (#848) — not the live `stop_loss` the
        # monitor moves in place.
        sig.original_sl_distance = abs(entry - sl)
        live.observe_signal(sig, store, price=entry, ledger=ledger, now_ts=now)

    ledger.flush(force=True)
    payload = json.load(open(tmp))
    with open(out_path, "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=True)

    cov = payload["coverage"]
    print(f"signals_seen={cov['signals_seen']} fully={cov['fully_armed']} "
          f"partly={cov['partly_armed']} unarmed={cov['unarmed']}")
    print(f"reasons={cov['reasons']}")
    for m in cov["misses"]:
        print(f"  {m['symbol']:12} armed={m['armed']} missing={m['missing']}")
    for arm in payload["open"]:
        print(f"  arm {arm['symbol']:12} {arm['timeframe']:3} "
              f"sl_src={arm['sl_distance_source']} "
              f"sl_dist={arm['sl_distance_pct']:.4f}%")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "fixtures_sar_coverage.json")
