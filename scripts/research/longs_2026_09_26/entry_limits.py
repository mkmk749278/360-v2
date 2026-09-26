"""§11.3 of the report: how the entry ORDER is placed, priced on Binance 1m tape.

Population: `signal_history.json` — the engine's last 500 signals — joined to
`signal_performance.json` for the dispatch time and the first observed price.
It is the only source carrying each signal's exact TP1, entry zone and
validity window. Needs `fetch_ops.sh`, then the 1m klines:

    python entry_limits.py --fetch      # data.binance.vision, dispatch day .. close+2d
    python entry_limits.py              # BE arm cap 0.6 (calibrated)
    CAPF=0.5 python entry_limits.py     # the engine's configured cap, for sensitivity

Every method is walked by ONE simulator, so their differences are the order
placement and nothing else:

* stop = stamped entry -/+ the SHIPPED stop distance, TP1 = the signal's TP1;
  both absolute prices, as the resting orders are;
* break-even arms at `be_policy.arm_threshold_pct` measured from the FILL and
  parks at the fill — a live position's semantics (`pretp_dispatcher` uses
  `entry_price_filled`);
* a bar touching stop and target books the stop; walk up to 72h, then mark.

Calibration: replaying the market fill with the BOOK's semantics (BE anchored
at the stamped entry) reproduces the recorded outcome class on 84% of signals
with the configured cap 0.5 and 88% with 0.6 — the 1m high overshoots the
mark price the engine watches, so the cap is raised to compensate. Both are
reported.

Fees: 0.07% round trip on a market fill; 0.04% on a resting limit fill (maker
entry saves 0.03%). A marketable limit is a market fill.
"""
import collections as C
import glob
import json
import os
import random
import statistics as st
import subprocess
import sys
import urllib.parse
import zipfile
import datetime as dt

import numpy as np

from common import DATA

CAPF = float(os.environ.get("CAPF", "0.6"))
HOR = 72 * 60
KL = os.path.join(DATA, "kl")


def load():
    h = json.load(open(os.path.join(DATA, "sighist.json")))
    p = {r["signal_id"]: r for r in json.load(open(os.path.join(DATA, "sigperf.json")))}
    return [(r, p[r["signal_id"]]) for r in h if r["signal_id"] in p]


def fetch(pairs):
    need = set()
    for r, q in pairs:
        t0 = dt.datetime.fromtimestamp(q["create_timestamp"], tz=dt.timezone.utc)
        t1 = dt.datetime.fromtimestamp(q["terminal_outcome_timestamp"] or q["create_timestamp"],
                                       tz=dt.timezone.utc)
        d = t0.date()
        while d <= min((t1 + dt.timedelta(days=2)).date(), dt.date(2026, 9, 25)):
            need.add((r["symbol"], d.isoformat()))
            d += dt.timedelta(days=1)
    os.makedirs(KL, exist_ok=True)
    lst = os.path.join(DATA, "urls_entry.txt")
    with open(lst, "w") as f:
        for s, d in sorted(need):
            qq = urllib.parse.quote(s)
            f.write(f"https://data.binance.vision/data/futures/um/daily/klines/{qq}/1m/"
                    f"{qq}-1m-{d}.zip {KL}/{s}__{d}.zip\n")
    subprocess.run(f"cat {lst} | xargs -P 12 -n 2 sh -c "
                   "'[ -s \"$1\" ] || curl -sS -m 60 -f -o \"$1\" \"$0\" 2>/dev/null; true'",
                   shell=True, check=False)


_c = {}


def klines(sym):
    if sym in _c:
        return _c[sym]
    parts = []
    for f in sorted(glob.glob(os.path.join(KL, f"{sym}__*.zip"))):
        try:
            z = zipfile.ZipFile(f)
            raw = z.read(z.namelist()[0]).decode().strip().splitlines()
        except Exception:  # noqa: BLE001 — a missing day shows up as no coverage
            continue
        if raw and raw[0].startswith("open_time"):
            raw = raw[1:]
        if raw:
            parts.append(np.array([ln.split(",")[:5] for ln in raw], dtype=float))
    a = None
    if parts:
        a = np.concatenate(parts)
        a[:, 0] = np.where(a[:, 0] > 1e14, a[:, 0] / 1000, a[:, 0])
        a = a[np.argsort(a[:, 0])]
        a = a[np.concatenate([[True], np.diff(a[:, 0]) > 0])]
    _c[sym] = a
    return a


def walk(a, i0, lng, sl, tp, arm, anchor):
    stop = sl
    end = min(len(a), i0 + HOR)
    lvl = anchor * (1 + arm / 100) if lng else anchor * (1 - arm / 100)
    for i in range(i0, end):
        hi, lo = a[i, 2], a[i, 3]
        if lng:
            if lo <= stop:
                return stop, "BE" if stop >= anchor * 0.9999 else "SL"
            if hi >= tp:
                return tp, "TP"
            if hi >= lvl and stop < anchor:
                stop = anchor
        else:
            if hi >= stop:
                return stop, "BE" if stop <= anchor * 1.0001 else "SL"
            if lo <= tp:
                return tp, "TP"
            if lo <= lvl and stop > anchor:
                stop = anchor
    if end <= i0:
        return None, "nodata"
    return a[end - 1, 4], "MTM"


def pnl(lng, f, x):
    return ((x / f - 1) if lng else (1 - x / f)) * 100


def arm_pct(r):
    sl = r["sl_distance_pct_at_entry"] or 0
    tp = abs(r["tp1"] - r["entry"]) / r["entry"] * 100
    return min(max(1.0, sl, 0.75 * (r.get("noise_floor_pct") or 0)), max(CAPF * tp, 1.0))


def simulate(pairs):
    out, calib, skipped = {}, C.Counter(), C.Counter()
    for r, q in pairs:
        lng = r["direction"] == "LONG"
        a = klines(r["symbol"])
        E, O, tobs, tdis = r["entry"], q["first_observed_price"], q["first_observed_at"], q["dispatch_timestamp"]
        s = r["sl_distance_pct_at_entry"]
        if a is None or not O or not tobs or not s or not r["tp1"]:
            skipped["no_data_or_levels"] += 1
            continue
        i0 = int(np.searchsorted(a[:, 0], tobs * 1000, side="right"))
        if i0 >= len(a) or a[i0, 0] - tobs * 1000 > 180_000:
            skipped["no_1m_coverage"] += 1
            continue
        SL = E * (1 - s / 100) if lng else E * (1 + s / 100)
        TP, ARM = r["tp1"], arm_pct(r)
        x, how = walk(a, i0, lng, SL, TP, ARM, E)  # book semantics, for calibration only
        rc = {"SL_HIT": "SL", "TP1_HIT": "TP", "PROFIT_LOCKED": "TP", "FULL_TP_HIT": "TP",
              "BREAKEVEN_EXIT": "BE"}.get(q["outcome_label"], "?")
        calib[rc == how] += 1
        drift = ((O / E - 1) if lng else (1 - O / E)) * 100
        row = dict(sym=r["symbol"], lng=lng, setup=r["setup_class"], drift=drift)
        x, how = walk(a, i0, lng, SL, TP, ARM, O)
        row["M"] = (pnl(lng, O, x) - 0.07, how, 1)

        def limit(L, ttl_min):
            if (lng and O <= L) or ((not lng) and O >= L):
                return row["M"]  # marketable: fills at market
            end = int(np.searchsorted(a[:, 0], (tdis + ttl_min * 60) * 1000, side="right"))
            for i in range(i0, min(end, len(a))):
                hi, lo = a[i, 2], a[i, 3]
                touched = lo <= L if lng else hi >= L
                target_first = (hi >= TP and lo > L) if lng else (lo <= TP and hi < L)
                if target_first:
                    return (0.0, "TP_before_fill", 0)
                if touched:
                    if (lng and lo <= SL) or ((not lng) and hi >= SL):
                        return (pnl(lng, L, SL) - 0.04, "SL_samebar", 1)
                    x, how = walk(a, i + 1, lng, SL, TP, ARM, L)
                    return (pnl(lng, L, x) - 0.04, how, 1)
            return (0.0, "no_fill", 0)

        edge = r["entry_zone_high"] if lng else r["entry_zone_low"]
        row["Z"] = limit(edge, r.get("valid_for_minutes") or 15)
        row["E15"] = limit(E, 15)
        row["E60"] = limit(E, 60)
        row["S05"] = row["M"] if drift < 0.5 else (0.0, "skipped", 0)
        row["H"] = row["M"] if drift < 0.5 else limit(E, 15)
        row["marketable_at_zone"] = (O <= edge) if lng else (O >= edge)
        out[r["signal_id"]] = row
    return out, calib, skipped


ARMS = [("M", "Market at dispatch (today)"),
        ("Z", "FSM_LIMIT_ENTRY design: limit at zone edge, validity TTL"),
        ("E15", "Limit at the signal price, 15 min"),
        ("E60", "Limit at the signal price, 60 min"),
        ("S05", "Skip when drift >= 0.5%"),
        ("H", "Market if drift < 0.5%, else limit at signal price 15 min")]


def ci(rs, f, n=2000):
    by = C.defaultdict(list)
    for r in rs:
        by[r["sym"]].append(f(r))
    g = list(by.values())
    rnd = random.Random(11)
    ms = sorted(sum(map(sum, s)) / sum(map(len, s)) for s in ([rnd.choice(g) for _ in g] for _ in range(n)))
    return ms[int(.025 * n)], ms[int(.975 * n)]


def report(rows, title):
    print(f"\n== {title} (signals={len(rows)})")
    for k, label in ARMS:
        v = [r[k][0] for r in rows]
        filled = sum(r[k][2] for r in rows)
        if k == "M":
            lo, hi = ci(rows, lambda r: r["M"][0])
            d = ""
        else:
            lo, hi = ci(rows, lambda r, k=k: r[k][0] - r["M"][0])
            d = f" vs market {st.mean(r[k][0] - r['M'][0] for r in rows):+.3f}"
        print(f"  {label:58s} filled {filled/len(rows):4.0%} per signal {st.mean(v):+.3f} "
              f"total {sum(v):+7.1f}{d} CI[{lo:+.2f},{hi:+.2f}]")
    print("   limit@60m outcomes:", dict(C.Counter(r["E60"][1] for r in rows)))


def main():
    pairs = load()
    if "--fetch" in sys.argv:
        fetch(pairs)
        return
    res, calib, skipped = simulate(pairs)
    print(f"BE arm cap {CAPF}; simulated {len(res)}; skipped {dict(skipped)}; "
          f"calibration agreement {calib[True]}/{calib[True] + calib[False]}")
    rows = list(res.values())
    M = [r for r in rows if r["setup"] == "MOVER_TREND_PULLBACK" and r["lng"]]
    print(f"MVRTP LONG marketable at the zone edge at dispatch: {sum(r['marketable_at_zone'] for r in M)/len(M):.0%}")
    report(M, "MVRTP LONG")
    report([r for r in rows if r["lng"]], "ALL LONG")
    report([r for r in rows if not r["lng"]], "ALL SHORT")
    report(rows, "ALL")


if __name__ == "__main__":
    main()
