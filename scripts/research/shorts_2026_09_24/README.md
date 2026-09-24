# Shorts research, 2026-09-24

Reproduces every number in `docs/SHORTS_RESEARCH_2026_09_24.md`.

This is research code. It is not imported by the engine and changes nothing
on the money path.

```bash
export SHORTS_DATA_DIR=~/shorts_research_data     # ~1 GB when complete
cp <delivered-book export>.json "$SHORTS_DATA_DIR/rows.json"
python fetch.py          # public Binance archive only; resumable
python run_all.py        # all sections, ~40 min
python run_all.py book attribution   # or pick sections
```

## `rows.json`

`rows.json` is the delivered book: one closed signal per row, with `symbol`,
`direction`, `setup`, `outcome`, `pnl_pct`, `net_pct` and `closed_at`. The
2026-09-24 run used the audit's export of the public track record. It covers
1,678 rows from 2026-07-26 to 2026-09-24.

There is **no entry time** in it, so the entry-side questions in §5.4 of the
doc need the engine's own closed-signal record.

## Files

| File | Role |
|---|---|
| `paths.py` | the data directory (`SHORTS_DATA_DIR`) |
| `fetch.py`, `prepare.py` | download from `data.binance.vision`, then build panels |
| `load.py`, `panel.py`, `feat.py`, `fundpanel.py` | kline loading, the aligned 1h panel, indicators, funding |
| `sim.py` | short-trade simulator and statistics (day-clustered bootstrap) |
| `strat.py`, `negfund.py` | 1h mechanisms and the negative-funding trade |
| `m15.py`, `m15y.py`, `f15.py`, `f15y.py` | 15m panels (book window / 12 months) and 15m mechanisms |
| `yr_mvrtp.py`, `yr_bds.py`, `yr_trap.py` | 12-month 15m replicas |
| `run_all.py` | one function per table in the doc |

## Conventions

- Entry is at the next bar's open.
- The stop is checked before the target: a bar that touches both is booked as
  a stop.
- Every trade has a stop.
- Costs are 0.07% round trip plus 0.05% slippage per fill. Funding carry is
  charged hourly while held.
- **TradFi perps are excluded structurally**: weekend volume below 0.35× the
  weekday volume. The live `contractType` is not reachable from every network.
- **Calibration:**
  - the 1h MVRTP approximation fails; it is kept in `calib1h` on purpose;
  - the 15m replica matches the book's sign and ranking.

  So 15m results are read for direction, never quoted as expected live PnL.
