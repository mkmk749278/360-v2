"""Which 5m bar does a metrics OI stamp describe?

During liquidations OI falls in the same minutes price falls. So the bar
whose return correlates most with a stamp-to-stamp OI change is the bar that
change happened in. If that is the bar STARTING at the stamp rather than the
one ENDING at it, the stamp leads the price and any rule reading the stamp at
that time has seen the future.
"""
import numpy as np
import pandas as pd
from load import klines, metrics

rows = []
for sym in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT", "XRPUSDT", "SUIUSDT", "LINKUSDT", "AVAXUSDT",
            "WIFUSDT", "ENAUSDT", "ARBUSDT", "OPUSDT", "INJUSDT", "TIAUSDT", "SEIUSDT", "NEARUSDT"]:
    k = klines("k5m", sym)
    m = metrics(sym, raw=True)  # the archive's own stamps, as published
    if k is None or m is None:
        continue
    oi = m.oi[~m.oi.index.duplicated()]
    d_oi = np.log(oi).diff()
    d_oi = d_oi[(oi.index.to_series().diff() == pd.Timedelta(minutes=5)).values]
    r = np.log(k.close / k.open)  # indexed by bar OPEN time
    out = {"sym": sym}
    # lag L: correlate the OI change stamped at s with the bar opening at s + L*5m
    for L in (-2, -1, 0, 1):
        rr = r.reindex(d_oi.index + pd.Timedelta(minutes=5 * L))
        ok = ~np.isnan(rr.values) & ~np.isnan(d_oi.values)
        out[L] = np.corrcoef(d_oi.values[ok], rr.values[ok])[0, 1]
    rows.append(out)
df = pd.DataFrame(rows).set_index("sym")
df.columns = ["bar [s-10,s-5)", "bar [s-5,s) ends at stamp", "bar [s,s+5) starts at stamp", "bar [s+5,s+10)"]
print(df.round(3).to_string())
print("mean", df.mean().round(3).to_dict())
