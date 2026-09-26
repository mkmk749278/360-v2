# Longs research, 2026-09-26

Reproduces every number in `docs/LONGS_RESEARCH_2026_09_26.md`.

This is research code. It is not imported by the engine and changes nothing
on the money path.

```bash
export LONGS_DATA_DIR=~/longs_research_data     # ~85 MB when complete
./fetch_book.sh          # the delivered book, one UTC day per call (curl)
python fetch_klines.py   # 1m klines from data.binance.vision; resumable
python book.py           # §2–§4, §6–§8 (or: python book.py sides paths ...)
python exits.py          # §5, the exit counterfactuals on the 1m tape

# §11 — the engine's own record, through an ops guest session
OPS_GUEST_CODE=... ./fetch_ops.sh
python entry_drift.py              # §11.1–11.2
python entry_limits.py --fetch     # 1m klines for the last 500 signals
python entry_limits.py             # §11.3, break-even cap 0.6 (calibrated)
CAPF=0.5 python entry_limits.py    # §11.3, the configured cap
```

`exits.py` needs `numpy`; the rest is stdlib.

## Files

| File | Role |
|---|---|
| `common.py` | data dir, the fixed `END` every window counts back from, symbol-clustered bootstrap |
| `fetch_book.sh` | `/api/track-record/signals`, one call per UTC day so no day is truncated |
| `fetch_klines.py` | close day + next day of every long closed in the last 62 days |
| `book.py` | the book tables, one function per section |
| `exits.py` | no-BE / wider-stop / runner walks from each trade's actual exit |
| `fetch_ops.sh` | `signal_performance` + `signal_history` through an ops guest session |
| `entry_drift.py` | recorded vs rebased vs break-even-at-fill, by path, drift, signal age, admission |
| `entry_limits.py` | market vs limit entries on the 1m tape, one simulator for every method |

## Things to know before rerunning

- **Use curl for the engine endpoint.** Cloudflare answers Python's default
  `urllib` client with 403.
- **Every window counts back from `END` (2026-09-26 06:00 UTC)**, not from
  now, so a later rerun against a fresh export moves the window on purpose,
  not by accident.
- **The public record has no entry or dispatch time.** So §2–§8 use the
  recorded drift figure, and §7's "previous trade" means the previous
  *close*. §11 measures drift from the engine's own record.
- **`signal_history` holds only the last 500 signals.** A later rerun of
  `entry_limits.py` sees a different window than the report's 14–25 Sep.
- **Levels the record lacks are fixed from the book's medians** (stop 3.0%,
  TP1 4.0%). The BE test is repeated at TP 3.0% to show the answer does not
  hinge on it.
