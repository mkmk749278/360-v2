# Market-first research (2026-10-23)

Reproduces §1 of `docs/MARKET_FIRST_METHODOLOGY_2026_10_23.md`.

```bash
python scripts/research/market_first_2026_10_23/fetch.py --out /tmp/mf --end 1792720800
python scripts/research/market_first_2026_10_23/study.py --data /tmp/mf
```

`--end 1792720800` (2026-10-23 01:00 UTC) pins the window the doc was written
from; omit it to run up to now. Gate.io is used because Binance returns 451 from
cloud containers. Read-only, public endpoints, no engine state.
