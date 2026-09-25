# Shorts from market structure — reproduction (2026-09-25)

Report: `docs/SHORTS_MARKET_RESEARCH_2026_09_25.md`.
Pre-registration: `HYPOTHESES.md`, committed before any test ran.

**Public data only.** Nothing here reads an engine artifact.

```bash
pip install pandas numpy requests
export SHORTS_MKT_DIR=~/shorts_data
python fetch.py                 # archive pull, ~2.7 GB, ~1.5 h (the 5m metrics are most of it)
curl -o $SHORTS_MKT_DIR/emissionsIndex.json https://defillama-datasets.llama.fi/emissionsIndex
python events.py                # H1 unlocks, H2 listings
python h1_detail.py             # H1 tails, stops, size, event-vs-control
python h1_explore.py            # E1-E4 (exploratory, declared before running)
python h2_detail.py             # H2 tails and stops
python intraday.py H5           # premium dislocation
python intraday.py H3 H4 H7     # needs the metrics
python others.py H6 H6b H8 H9 H10
python h10_detail.py            # H10 robustness (delay, control, slippage, hold, days)
python oi_stamp_check.py        # which price bar an archive OI stamp describes
```

| File | What |
|---|---|
| `fetch.py` | archive download (klines 1d/1h/5m, spot 1h, premium 1h, funding, 5m metrics) |
| `load.py` | loaders, costs, IS/OOS split, cluster bootstrap, pass bar |
| `events.py` | H1, H2 daily event studies |
| `intraday.py` | H3, H4, H5, H7 on 1h bars |
| `others.py` | H6, H8, H9, H10 |
| `h1_detail.py`, `h1_explore.py`, `h2_detail.py`, `h10_detail.py` | robustness |
| `oi_stamp_check.py` | shows archive `metrics` rows describe stamp + 5m; `load.metrics` re-times them |

**Note on the DefiLlama file.** It is a live dataset; a later download may
differ from the one used on 2026-09-25. It carries 370 tokens, 195 of which map
to a Binance perp by ticker, and H1's selection used 340 insider cliff events.

**Note on `h10_detail.py`.** It was run once on the archive's raw stamps, and
that run is the one the report quotes for the delay test. `load.metrics` now
re-times the stamps, so its `delay=1` column is today the honest one.
