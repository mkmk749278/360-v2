"""Reproduce every table in docs/SHORTS_RESEARCH_2026_09_24.md.

    SHORTS_DATA_DIR=~/shorts_research_data python fetch.py      # once
    SHORTS_DATA_DIR=~/shorts_research_data python run_all.py [section ...]

Sections: book flush attribution calib1h shorts1h funding negfund daily
          calib15 cand15 year_mvrtp year_bds year_trap   (default: all)

Conventions (see the doc, section 1): entry at the next bar's open, stop
checked before target, fees 0.07% round trip + 0.05% slippage per fill,
funding carry charged hourly where held, PnL % per trade (fixed notional).
"""
import collections
import datetime as dt
import json
import os
import sys
import warnings

import numpy as np

from paths import DATA

warnings.filterwarnings("ignore")


def _rows():
    return json.load(open(os.path.join(DATA, "rows.json")))


def _market():
    from panel import build, rolling_sum
    P = build()
    C = P["C"]
    syms = list(P["syms"])
    liq = rolling_sum(P["QV"], 24) >= 10e6
    r1 = np.clip(C / np.roll(C, 1, axis=0) - 1, -0.3, 0.3)
    r1[0] = np.nan
    ib = syms.index("BTCUSDT")
    alt = np.where(liq, r1, np.nan)
    alt[:, ib] = np.nan
    return P, syms, liq, r1, ib, np.nanmean(alt, axis=1)


def book():
    """§2.1-2.2 — red days against BTC, the alt index, breadth and the movers."""
    P, syms, liq, r1, ib, alt_ret = _market()
    ts, C, O = P["ts"], P["C"], P["O"]
    r24 = C / np.roll(C, 24, axis=0) - 1
    breadth = np.nanmean(np.where(liq, (r24 > 0).astype(float), np.nan), axis=1)
    day = ts // 86_400_000
    D = collections.defaultdict(lambda: [0.0, 0.0])
    for r in _rows():
        d = int(dt.datetime.fromisoformat(r["closed_at"]).timestamp() // 86400)
        D[d][0 if r["direction"] == "LONG" else 1] += r["net_pct"]
    feats = []
    for d in sorted(D):
        idx = np.where(day == d)[0]
        if len(idx) < 20:
            continue
        a, b = idx[0], idx[-1]
        r72 = C[a - 1] / C[a - 73] - 1
        cand = np.where(liq[a - 1] & np.isfinite(r72) & np.isfinite(C[b]))[0]
        top = cand[np.argsort(-r72[cand])[:20]]
        bot = cand[np.argsort(r72[cand])[:20]]
        L, S = D[d]
        feats.append((L, S, L + S, (C[b, ib] / O[a, ib] - 1) * 100,
                      (np.nanprod(1 + alt_ret[a:b + 1]) - 1) * 100, np.nanmean(breadth[a:b + 1]),
                      np.nanmean(C[b, top] / O[a, top] - 1) * 100, np.nanmean(C[b, bot] / O[a, bot] - 1) * 100))
    F = np.array(feats)
    names = ["long", "short", "book", "btc", "alt", "breadth", "top20mov", "bot20"]
    cc = np.corrcoef(F.T)
    red = F[:, 2] < 0
    print(f"days {len(F)}, red {red.sum()}, red-day total {F[red, 2].sum():+.1f}%, green {F[~red, 2].sum():+.1f}%")
    print("corr with LONG daily net: " + "  ".join(f"{n}={cc[0, i]:+.2f}" for i, n in enumerate(names) if i > 2))
    for i, n in enumerate(names[3:], start=3):
        print(f"  {n:9s} red-day mean {F[red, i].mean():+6.2f}   green-day mean {F[~red, i].mean():+6.2f}")


def flush():
    """§2.3 — long stops against alt-flush hours; stop clusters."""
    P, syms, liq, r1, ib, alt_ret = _market()
    ts = P["ts"]
    altr = alt_ret * 100
    rows = _rows()

    def hidx(iso):
        return int((dt.datetime.fromisoformat(iso).timestamp() * 1000 - ts[0]) // 3600000)
    base = altr[hidx("2026-07-26T00:00:00+00:00"):hidx("2026-09-23T23:00:00+00:00")]
    base = base[np.isfinite(base)]
    print(f"baseline: share of hours with alt < -0.5%: {(base < -0.5).mean() * 100:.1f}%")
    for side in ("LONG", "SHORT"):
        for oc in ("SL_HIT", "TP1_HIT"):
            h = [hidx(r["closed_at"]) for r in rows if r["direction"] == side and r["outcome"] == oc]
            a = altr[[x for x in h if 0 < x < len(altr)]]
            print(f"  {side:5s} {oc:8s} n={len(a):4d} share in flush hours {(a < -0.5).mean() * 100:4.1f}%")
    D = collections.defaultdict(float)
    for r in rows:
        D[r["closed_at"][:10]] += r["net_pct"]
    red = {d for d, v in D.items() if v < 0}
    hrs = collections.defaultdict(list)
    for r in rows:
        if r["direction"] == "LONG":
            hrs[r["closed_at"][:13]].append(r)
    clus = [(h, v) for h, v in hrs.items() if sum(1 for r in v if r["outcome"] == "SL_HIT") >= 3]
    loss = sum(r["net_pct"] for _, v in clus for r in v if r["outcome"] == "SL_HIT")
    print(f"long stop clusters (>=3 SL same hour): {len(clus)} hours, {loss:+.1f}%; "
          f"red days with one: {len({h[:10] for h, _ in clus} & red)} of {len(red)}")


def attribution():
    """§2.4 — the short side by path, on red days, and the counterfactual since 14 Aug."""
    rows = _rows()
    D = collections.defaultdict(float)
    for r in rows:
        D[r["closed_at"][:10]] += r["net_pct"]
    red = {d for d, v in D.items() if v < 0}
    agg = collections.defaultdict(list)
    for r in rows:
        if r["direction"] == "SHORT":
            agg[r["setup"]].append(r)
    for s, rs in sorted(agg.items(), key=lambda kv: sum(r["net_pct"] for r in kv[1])):
        by = collections.defaultdict(list)
        for r in rs:
            by[r["symbol"]].append(r["net_pct"])
        g = list(by.values())
        rng = np.random.default_rng(5)
        bs = [np.concatenate([g[i] for i in rng.integers(0, len(g), len(g))]).mean() for _ in range(4000)]
        tot = sum(r["net_pct"] for r in rs)
        rd = sum(r["net_pct"] for r in rs if r["closed_at"][:10] in red)
        print(f"  {s:26s} n={len(rs):3d} mean={tot / len(rs):+.3f} CI[{np.percentile(bs, 2.5):+.2f},"
              f"{np.percentile(bs, 97.5):+.2f}] total={tot:+7.1f} red-days={rd:+7.1f} last={max(r['closed_at'] for r in rs)[:10]}")
    since = [r for r in rows if r["closed_at"] >= "2026-08-14"]
    for name, ex in (("as delivered", set()), ("MVAVW SHORT off", {"MOVER_AVWAP_SCALP"}),
                     ("MVAVW+QCB SHORT off", {"MOVER_AVWAP_SCALP", "QUIET_COMPRESSION_BREAK"})):
        d2 = collections.defaultdict(float)
        for r in since:
            if r["direction"] == "SHORT" and r["setup"] in ex:
                continue
            d2[r["closed_at"][:10]] += r["net_pct"]
        rd = [d for d, v in d2.items() if v < 0]
        print(f"  since 14 Aug, {name:20s}: red {len(rd)}/{len(d2)} book {sum(d2.values()):+.1f}% "
              f"red-loss {sum(d2[d] for d in rd):+.1f}% worst {min(d2.values()):+.1f}%")


def calib1h():
    """§1 — the 1h MVRTP approximation that FAILED calibration (kept on purpose)."""
    import strat as S
    for lab, (a, b) in (("IS", S.IS), ("OOS", S.OOS)):
        print(S.fmt(S.stats(S.simulate_long(S.gen(S.c_tpb("L"), a, b)), S.ts, f"MVRTP~1h LONG [{lab}]")))

        def slf(t, j, e):
            _, B, _ = S.smas()
            s = max(B[t, j], S.H[t - 1, j]) + 0.125 * S.F["atr"][t, j]
            return s if s > e else None
        print(S.fmt(S.stats(S.simulate(S.P, S.gen(S.c_tpb("S"), a, b), slf, tp_r=1.0, hold=24), S.ts,
                            f"MVRTP~1h SHORT [{lab}]")))


def shorts1h():
    """§3 rows 1-5."""
    import strat as S
    S.report("1 breakdown ungated", S.c_breakdown(False), S.sl_hi6())
    S.report("2 breakdown gated", S.c_breakdown(True), S.sl_hi6())
    S.report("3 failed mover", S.c_failed_mover, S.sl_hi6())
    S.report("4 relative weakness", S.c_relweak, S.sl_hi6(), per_bar=5, rank=lambda t: S.F["r24"][t])
    S.report("5 pump fade", S.c_pumpfade, S.sl_bar_high(), tp_r=1.5, hold=12)


def funding():
    """§4 — forward returns by funding bucket; listing age."""
    import strat as S
    Fr = np.load(os.path.join(DATA, "funding8h.npy")) * 100
    C, O = S.C, S.O
    T, N = C.shape
    liq, ts = S.F["liq"], S.ts
    fwd = {h: (C[np.minimum(np.arange(T) + h, T - 1)] / O[np.minimum(np.arange(T) + 1, T - 1)] - 1) * 100
           for h in (24, 72, 168)}
    first = np.array([np.argmax(np.isfinite(C[:, j])) if np.isfinite(C[:, j]).any() else T for j in range(N)])
    new = first > 200
    samp = np.arange(200, T - 170, 4)

    def row(name, fn):
        for lab, (a, b) in (("ALL", (200, T - 170)), ("IS", S.IS), ("OOS", (S.OOS[0], T - 170))):
            v = {h: [] for h in fwd}
            d = []
            sy = collections.Counter()
            for t in samp:
                if not (a <= t < b):
                    continue
                for j in np.where(np.nan_to_num(liq[t] & fn(t)).astype(bool))[0]:
                    if all(np.isfinite(fwd[h][t, j]) for h in fwd):
                        for h in fwd:
                            v[h].append(np.clip(fwd[h][t, j], -90, 400))
                        d.append(ts[t] // 86400000)
                        sy[j] += 1
            if len(d) < 20:
                continue
            v24, dd = np.array(v[24]), np.array(d)
            g = [v24[dd == x] for x in np.unique(dd)]
            rng = np.random.default_rng(1)
            bs = [np.concatenate([g[i] for i in rng.integers(0, len(g), len(g))]).mean() for _ in range(1000)]
            print(f"  {name:36s} {lab:3s} n={len(d):6d} syms={len(sy):3d} top1={sy.most_common(1)[0][1] / len(d) * 100:4.1f}% "
                  f"f24={np.mean(v[24]):+.2f} [{np.percentile(bs, 2.5):+.2f},{np.percentile(bs, 97.5):+.2f}] "
                  f"f72={np.mean(v[72]):+.2f} f168={np.mean(v[168]):+.2f}")
    row("baseline (all liquid)", lambda t: np.ones(N, bool))
    row("funding >= +0.10%", lambda t: Fr[t] >= 0.10)
    row("funding <= -0.05%", lambda t: Fr[t] <= -0.05)
    row("funding <= -0.10%", lambda t: Fr[t] <= -0.10)
    age = lambda t: (t - first) / 24.0   # noqa: E731
    for lo, hi in ((1, 7), (7, 30), (30, 60), (60, 120)):
        row(f"listing age {lo}-{hi}d", lambda t, lo=lo, hi=hi: new & (age(t) >= lo) & (age(t) < hi))


def negfund():
    """§3 row 6 / §4 — the negative-funding short as a trade, with carry."""
    import negfund as NF
    import strat as S
    for lab, (a, b) in (("IS", S.IS), ("OOS", S.OOS)):
        for hold in (24, 72):
            print(NF.summary(NF.run(thr=-0.05, hold=hold, t0=a, t1=b), f"6 neg funding hold{hold}h [{lab}]"))


def daily():
    """§3 rows 7-8 — random-short baseline and the daily trend short."""
    import negfund as NF
    import strat as S
    from feat import ema
    from sim import fmt, stats
    C, O, H = S.C, S.O, S.H
    T, N = C.shape
    F, liq, ts, Fr = S.F, S.F["liq"], S.ts, NF.Fr
    alt = F["altidx"]
    aE = ema(alt[:, None], 480)[:, 0]
    bear = lambda t: alt[t] < aE[t] and aE[t] < aE[t - 24]   # noqa: E731
    cs = np.nancumsum(np.nan_to_num(C), axis=0)
    d20 = np.full_like(C, np.nan)
    d20[480:] = (cs[480:] - cs[:-480]) / 480
    r7 = C / np.roll(C, 168, axis=0) - 1
    Z = np.zeros(N, bool)

    def run(cond, hold, label, every=24):
        for lab, (a, b) in (("IS", S.IS), ("OOS", S.OOS)):
            trades, busy = [], {}
            for t in range(max(a, 700), b, every):
                for j in np.where(np.nan_to_num(cond(t)).astype(bool))[0]:
                    if busy.get(j, -1) >= t:
                        continue
                    e, at = O[t + 1, j], F["atr"][t, j]
                    if not (np.isfinite(e) and np.isfinite(at)):
                        continue
                    sl = min(e + 4.0 * at, e * 1.15)
                    px, carry = None, 0.0
                    for k in range(t + 1, min(T, t + 1 + hold)):
                        if not np.isfinite(H[k, j]):
                            continue
                        carry += Fr[k, j] / 8 if np.isfinite(Fr[k, j]) else 0
                        if H[k, j] >= sl:
                            px = max(sl, O[k, j])
                            break
                    if px is None:
                        k = min(T - 1, t + hold)
                        px = C[k, j]
                    if not np.isfinite(px):
                        continue
                    trades.append(dict(t=t, j=j, net=(e - px) / e * 100 + carry - 0.17,
                                       risk_pct=(sl - e) / e * 100, exit_t=k))
                    busy[j] = k
            print(fmt(stats(trades, ts, f"{label} [{lab}]")))
    run(lambda t: liq[t], 24, "7 random short, all liquid")
    run(lambda t: liq[t] if bear(t) else Z, 24, "7 random short, alt-bear only")
    run(lambda t: liq[t] & (C[t] < d20[t]) & (r7[t] < 0), 24, "8 trend short")


def calib15():
    """§1 — the 15m MVRTP calibration against the book window (PASSED)."""
    import f15 as X
    import m15 as M
    from sim import fmt, stats
    band = 0.0035
    for side, name in ((1, "LONG"), (-1, "SHORT")):
        trades, busy = [], {}
        a, b = M.BOOK
        for t in range(max(a, 110), b):
            s7, s25, s99, c, pl, ph, pc = M.S7[t], M.S25[t], M.S99[t], M.C[t], M.L[t - 1], M.H[t - 1], M.C[t - 1]
            sep = np.abs(s7 - s99) / s99 >= 0.03
            if side > 0:
                fast = (pl <= s7 * (1 + band)) & (c > s7) & (c > pc)
                deep = (pl <= s25 * (1 + band)) & (c > s25) & (c > pc)
                base = M.LIQ[t] & sep & (s25 > s99)
            else:
                fast = (ph >= s7 * (1 - band)) & (c < s7) & (c < pc)
                deep = (ph >= s25 * (1 - band)) & (c < s25) & (c < pc)
                base = M.LIQ[t] & sep & (s25 < s99)
            for j in np.where(np.nan_to_num(base & (fast | deep)).astype(bool))[0]:
                if busy.get(j, -1) >= t:
                    continue
                buf = 0.5 * M.ATR[t, j]
                if side > 0:
                    sl = (min(s25[j], pl[j]) if fast[j] else min(s99[j], pl[j])) - buf
                else:
                    sl = (max(s25[j], ph[j]) if fast[j] else max(s99[j], ph[j])) + buf
                e = c[j]
                if not (np.isfinite(e) and np.isfinite(sl)) or (sl - e) * side >= 0:
                    continue
                r = abs(e - sl)
                pct, k, why = M.walk(side, t, j, e, sl, [e + side * r, e + side * 1.6 * r], 192, "ladder")
                if np.isfinite(pct):
                    trades.append(dict(t=t, j=j, net=pct - 0.07, risk_pct=r / e * 100, why=why, exit_t=k))
                busy[j] = k
        print(fmt(stats(trades, M.ts, f"MVRTP-15m {name} (book window)")))
    L = X.mvrtp_long(guard=lambda t: not (X.ALT1H[t] <= -0.6 or X.BTC1H[t] <= -0.6))
    print(fmt(stats([x for x in L if not x["blocked"]], M.ts, "  longs entered outside a flush")))
    print(fmt(stats([x for x in L if x["blocked"]], M.ts, "  longs entered during a flush")))


def cand15():
    """§3 rows 9-11 and the upside trap on the book window."""
    import f15 as X
    import m15 as M
    from sim import fmt, stats
    liq = M.LIQ
    N = M.C.shape[1]

    def clean(tr):
        return [x for x in tr if np.isfinite(x["net"])]
    flush = lambda t: X.ALT1H[t] <= -0.6 and M.ALT[t] <= -0.2   # noqa: E731
    F1 = lambda t: (liq[t] & (M.C[t] < X.LO16[t])) if flush(t) else np.zeros(N, bool)   # noqa: E731
    slh = lambda t, j: X.HI4[t, j] + 0.25 * M.ATR[t, j]   # noqa: E731
    print(fmt(stats(clean(X.short_run(F1, slh)), M.ts, "9 flush continuation")))

    def F3(t):
        was = (M.S25[t - 8] > M.S99[t - 8]) & (np.abs(M.S7[t - 8] - M.S99[t - 8]) / M.S99[t - 8] >= 0.03)
        return liq[t] & was & (M.C[t] < M.S99[t]) & (M.C[t - 1] >= M.S99[t - 1])
    slm = lambda t, j: X.HI8[t, j] + 0.25 * M.ATR[t, j]   # noqa: E731
    for tp in (1.0, 1.5, 2.0):
        print(fmt(stats(clean(X.short_run(F3, slm, tp_r=tp, hold=32)), M.ts, f"10 failed mover 15m tp{tp}R")))

    def F4(t):
        return liq[t] & (M.C[t] < M.O[t]) if M.BTC[t] <= -0.5 else np.zeros(N, bool)
    print(fmt(stats(clean(X.short_run(F4, slh, per_bar=5, rank=lambda t: M.C[t] / M.C[t - 4] - 1, hold=8)),
                    M.ts, "11 BTC-led alt short")))


def year_mvrtp():
    """§3 rows 12/12a and §5.5 — MVRTP both sides over 12 months, by alt regime."""
    import m15y as M
    import yr_mvrtp as Y
    from sim import fmt, stats
    for side, name in ((1, "LONG"), (-1, "SHORT")):
        for lab, (a, b) in (("IS", M.IS), ("OOS", M.OOS)):
            print(fmt(stats(Y.mvrtp(side, a, b), M.ts, f"MVRTP {name} core [{lab}]")))
            print(fmt(stats(Y.mvrtp(side, a, b, Y.bear), M.ts, f"   alt-bear only [{lab}]")))


def year_bds():
    """§3 row 13."""
    import m15y as M
    import yr_bds as B
    from sim import fmt, stats
    for lab, (a, b) in (("IS", M.IS), ("OOS", M.OOS)):
        tr = [x for x in B.bds(a, b) if np.isfinite(x["net"])]
        print(fmt(stats(tr, M.ts, f"13 BDS replica [{lab}]")))


def year_trap():
    """§3 rows 14/14a."""
    import m15y as M
    import yr_trap as Y
    from sim import fmt, stats
    for mb in (None, 0.42):
        for lab, (a, b) in (("IS", M.IS), ("OOS", M.OOS)):
            print(fmt(stats(Y.trap(a, b, max_buy=mb), M.ts, f"14 trap buy<={mb} [{lab}]")))


SECTIONS = dict(book=book, flush=flush, attribution=attribution, calib1h=calib1h, shorts1h=shorts1h,
                funding=funding, negfund=negfund, daily=daily, calib15=calib15, cand15=cand15,
                year_mvrtp=year_mvrtp, year_bds=year_bds, year_trap=year_trap)

if __name__ == "__main__":
    for name in (sys.argv[1:] or list(SECTIONS)):
        print(f"\n===== {name} =====")
        SECTIONS[name]()
