#!/usr/bin/env python3
"""Phase-1 replay: the engine's real evaluators over a year of Binance klines.

    python scripts/research/market_first_2026_10_23/replay.py \\
        --zips /path/to/bn/zip --out /path/to/out --symbol SOLUSDT \\
        --start 2025-09-20 --end 2026-10-21

For every closed 5m bar it hands `ScalpChannel.evaluate` the same inputs the
live scanner builds in `_build_scan_context`, *aligned by time*: for each
timeframe, the last 500 bars whose close is at or before that 5m close. The
stock `src/backtester.py` slices every timeframe by one bar index, which feeds
a 5m strategy 1h bars from a different date; it is not used for that reason.

What the replay reproduces: candles, `compute_indicators_for_candle_dict`, the
SMC detector, the regime service and its context, the pair tier, the LevelBook
(hourly refresh, clock pinned to replay time), and the stop geometry the
scanner applies after the evaluator: `build_risk_plan` (the per-setup stop cap,
reject or compress, and the TP rebuild), the noise floor, then the 0.8% / 1xATR
clamp. The CT macro gates that run just before `build_risk_plan` are not
replayed (they cover LSR/SR_FLIP longs and LSR/FAR/BDS shorts).
What it cannot: order flow (CVD, depth, aggTrades, liquidations), funding,
order blocks, chart patterns, the scoring engine's >= 65 floor, the gate chain
after the evaluator and the router. Evaluators that branch on a missing input
take their fallback branch, exactly as they would live when that input is
absent. The calibration step reports, per path, how far that moves the result.

Each candidate is walked forward on 5m bars with the engine's default exit
(`BE_THEN_TP1_DEFAULT_ENABLED`): break-even arm at max(1%, 1R, 0.75 x noise),
capped at max(1%, 0.5 x TP1 distance), parked 0.15% on the loss side; full close
at TP1; a bar touching both the stop and TP1 counts as the stop. Gross PnL %
is written; the 0.07% round-trip fee is charged in analysis.

Output: one CSV of candidates per symbol. Book-level rules (one active signal
per symbol, per-path same-direction budget) are applied afterwards in book.py,
because they depend on every symbol at once.
"""
from __future__ import annotations

import argparse
import csv
import glob
import io
import os
import sys
import time
import zipfile
from datetime import datetime, timezone

import numpy as np
from loguru import logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import src.level_book as level_book_mod  # noqa: E402
from config import SMC_SCALP_LOOKBACK, SMC_SCALP_TOLERANCE_PCT  # noqa: E402
from src.channels.scalp import ScalpChannel  # noqa: E402
from src.detector import SMCDetector  # noqa: E402
from src.level_book import LevelBook  # noqa: E402
from src.pair_manager import classify_pair_tier  # noqa: E402
from src.regime import RegimeService  # noqa: E402
from src.chart_patterns import detect_all_patterns  # noqa: E402
from src.mtf import check_mtf_gate, compute_mtf_confluence  # noqa: E402
from src.scanner import Scanner  # noqa: E402
from src.signal_quality import ScoringInput, SetupClass, SignalScoringEngine, build_risk_plan  # noqa: E402
import src.scanner.indicator_compute as indicator_compute_mod  # noqa: E402
from src.scanner.indicator_compute import compute_indicators_for_candle_dict  # noqa: E402

# Half the indicator time goes to four indicators that no code this replay runs
# reads (grep: scalp.py, regime.py, detector.py, level_book.py). They feed the
# auxiliary channels and the scorer, which are not replayed. Their keys become
# None instead of being computed.
def _nan1(h, *_a, **_k):
    return np.full(len(h), np.nan)


def _nan2(h, *_a, **_k):
    return np.full(len(h), np.nan), np.full(len(h), np.nan)


def _nan_ichimoku(h, *_a, **_k):
    x = np.full(len(h), np.nan)
    return {"tenkan_sen": x, "kijun_sen": x, "senkou_span_a": x, "senkou_span_b": x}


indicator_compute_mod.supertrend = _nan2
indicator_compute_mod.stochastic_rsi = _nan2
indicator_compute_mod.mfi = _nan1
indicator_compute_mod.ichimoku = _nan_ichimoku

TFS = ("5m", "15m", "1h", "4h", "1d")
WINDOW = 500
FIVE_MIN_MS = 300_000
MAX_HOLD_BARS = 7 * 288  # a week of 5m bars; live has no expiry, this bounds the walk

# Engine defaults (config/__init__.py), copied rather than imported where the
# live value is a runtime tunable the replay must hold fixed.
NOISE_MULT, NOISE_MAX = 1.0, 3.0
BE_FLAT, BE_R, BE_NOISE, BE_PARK, BE_TP1_CAP = 1.0, 1.0, 0.75, 0.15, 0.5
SPREAD_PCT = 0.02

FIELDS = ["symbol", "t_ms", "setup", "direction", "entry", "sl", "tp1", "sl_pct",
          "tp1_pct", "noise_pct", "confidence", "score", "mtf_score", "mtf_pass", "regime",
          "outcome", "pnl_pct", "exit_ms", "mfe_pct", "mae_pct",
          "c_smc", "c_regime", "c_volume", "c_indicators", "c_patterns", "c_mtf", "c_thesis"]
COMPONENTS = ("smc", "regime", "volume", "indicators", "patterns", "mtf", "thesis_adj")
SCORER = SignalScoringEngine()


def composite_score(sig, win: dict, ind: dict, res, regime: str, regime_ctx) -> tuple:
    """Mirror of the scanner's pre-penalty composite score (Scanner, ~L8870-8937).

    Inputs the replay has no source for take the scanner's own defaults: no
    CVD divergence, OI trend NEUTRAL, no liquidation volume, no funding rate.
    Returns (total, mtf_score, basic MTF gate pass). The gate flag uses the
    generic 0.55 floor only; the regime/family/semantic relaxations are not
    mirrored, so it is reported, never filtered on.
    """
    direction = sig.direction.value
    mtf_data = {}
    for tf in ("5m", "15m", "1h", "4h"):
        i = ind.get(tf, {})
        if i.get("ema9_last") is not None and i.get("ema21_last") is not None and tf in win:
            mtf_data[tf] = {"ema_fast": float(i["ema9_last"]), "ema_slow": float(i["ema21_last"]),
                            "close": float(win[tf]["close"][-1])}
    mtf_score = compute_mtf_confluence(direction, mtf_data).score if mtf_data else 0.0
    mtf_pass = bool(check_mtf_gate(direction, mtf_data, min_score=0.55)[0]) if mtf_data else True
    ptf = Scanner._get_primary_timeframe("360_SCALP", getattr(sig, "setup_class", ""))
    pcd = win.get(ptf) or win["5m"]
    pind = ind.get(ptf, {})
    usd = [c * v for c, v in zip(pcd["close"][-20:], pcd["volume"][-20:])]
    try:
        patterns = detect_all_patterns(np.asarray(pcd["open"]), np.asarray(pcd["high"]),
                                       np.asarray(pcd["low"]), np.asarray(pcd["close"]),
                                       np.asarray(pcd["volume"]))
    except Exception:  # noqa: BLE001 — the scanner fails open here too
        patterns = []
    try:
        atr_pctile = float(regime_ctx.atr_percentile)
    except (AttributeError, TypeError, ValueError):
        atr_pctile = 50.0
    inp = ScoringInput(
        sweeps=res.sweeps, mss=res.mss, fvg_zones=res.fvg, regime=regime,
        setup_class=sig.setup_class, htf_trend_aligned=getattr(sig, "htf_trend_aligned", False),
        atr_percentile=atr_pctile, volume_last_usd=float(usd[-1]) if usd else 0.0,
        volume_avg_usd=float(np.mean(usd)) if usd else 0.0,
        breakout_volume_ratio=getattr(sig, "breakout_volume_ratio", 0.0) or 0.0,
        macd_histogram_last=pind.get("macd_histogram_last"), macd_histogram_prev=pind.get("macd_histogram_prev"),
        rsi_last=pind.get("rsi_last"), ema_fast=pind.get("ema9_last"), ema_slow=pind.get("ema21_last"),
        adx_last=pind.get("adx_last"), direction=direction, chart_patterns=patterns, mtf_score=mtf_score,
    )
    out = SCORER.score(inp)
    return float(out["total"]), float(mtf_score), mtf_pass, {k: float(out.get(k, 0.0)) for k in COMPONENTS}


def load_tf(zdir: str, symbol: str, tf: str) -> dict:
    """Concatenate every archive file for (symbol, tf), sorted and de-duplicated."""
    rows = []
    for path in glob.glob(os.path.join(zdir, f"{symbol}__{tf}__*.zip")):
        try:
            with zipfile.ZipFile(path) as z:
                raw = z.read(z.namelist()[0]).decode()
        except (zipfile.BadZipFile, IndexError, OSError):
            continue
        for r in csv.reader(io.StringIO(raw)):
            if not r or not r[0].isdigit():
                continue  # header row in newer archive files
            rows.append((int(r[0]), float(r[1]), float(r[2]), float(r[3]),
                         float(r[4]), float(r[5]), int(r[6]), float(r[7])))
    if not rows:
        return {}
    a = np.array(sorted(set(rows)), dtype=float)
    _, keep = np.unique(a[:, 0], return_index=True)
    a = a[keep]
    return {"open_time": a[:, 0], "open": a[:, 1], "high": a[:, 2], "low": a[:, 3],
            "close": a[:, 4], "volume": a[:, 5], "close_time": a[:, 6], "qvol": a[:, 7]}


def window(series: dict, n: int) -> dict:
    lo = max(0, n - WINDOW)
    return {k: series[k][lo:n].tolist() for k in ("open", "high", "low", "close", "volume", "open_time")}


def atr_pct(cd: dict, entry: float, period: int = 14) -> float:
    """Mirror of Scanner._atr_pct_from_candles."""
    h, lo, c = cd["high"], cd["low"], cd["close"]
    n = len(c)
    if n < period + 1 or entry <= 0:
        return 0.0
    trs = [max(h[i] - lo[i], abs(h[i] - c[i - 1]), abs(lo[i] - c[i - 1])) for i in range(n - period, n)]
    return sum(trs) / len(trs) / entry * 100.0


def noise_floor_pct(win: dict, entry: float) -> float:
    """Mirror of Scanner._measure_noise_floor_pct."""
    for tf, scale in (("1h", 1.0), ("15m", 2.0), ("5m", 3.46)):
        if tf in win:
            p = atr_pct(win[tf], entry)
            if p > 0:
                return p * scale
    return 0.0


def shape(sig, win: dict) -> tuple:
    """Apply the scanner's post-evaluator geometry; return (sl, tp1, noise%)."""
    entry, sl, tp1 = float(sig.entry), float(sig.stop_loss), float(sig.tp1)
    long_ = sig.direction.value == "LONG"
    noise = noise_floor_pct(win, entry)
    dist = abs(sl - entry) / entry * 100.0
    floor = min(noise * NOISE_MULT, NOISE_MAX)
    if noise > 0 and dist > 0 and floor > dist:  # _apply_noise_floor_stop, TPs untouched
        sl = entry * (1 - floor / 100) if long_ else entry * (1 + floor / 100)
    atr = float(getattr(sig, "atr_val", 0) or 0)
    min_dist = max(entry * 0.008, atr if atr > 0 else 0.0)  # _enqueue_signal clamp
    d = abs(entry - sl)
    if 0 < d < min_dist:
        ratio = min_dist / d
        sl = entry - min_dist if long_ else entry + min_dist
        tp1 = entry + abs(entry - tp1) * ratio if long_ else entry - abs(entry - tp1) * ratio
    return sl, tp1, noise


def walk(s5: dict, k: int, long_: bool, entry: float, sl: float, tp1: float, noise: float) -> tuple:
    """Engine default exit on 5m bars after bar k. Returns outcome, pnl%, exit_ms, mfe%, mae%."""
    sl_pct = abs(entry - sl) / entry * 100.0
    tp_pct = abs(tp1 - entry) / entry * 100.0
    arm = max(BE_FLAT, BE_R * sl_pct, BE_NOISE * noise)
    arm = min(arm, max(BE_FLAT, BE_TP1_CAP * tp_pct))
    stop, armed, mfe, mae = sl, False, 0.0, 0.0
    hi, lo, cl, ct = s5["high"], s5["low"], s5["close"], s5["close_time"]
    end = min(len(cl), k + 1 + MAX_HOLD_BARS)
    for j in range(k + 1, end):
        fav = (hi[j] / entry - 1) * 100 if long_ else (1 - lo[j] / entry) * 100
        adv = (1 - lo[j] / entry) * 100 if long_ else (hi[j] / entry - 1) * 100
        hit_stop = lo[j] <= stop if long_ else hi[j] >= stop
        hit_tp = hi[j] >= tp1 if long_ else lo[j] <= tp1
        if hit_stop:  # stop first when both touch in one bar
            pnl = (stop / entry - 1) * 100 if long_ else (1 - stop / entry) * 100
            return ("BREAKEVEN_EXIT" if armed else "SL_HIT"), pnl, int(ct[j]), max(mfe, fav), max(mae, adv)
        if hit_tp:
            return "TP1_HIT", tp_pct, int(ct[j]), max(mfe, fav), max(mae, adv)
        mfe, mae = max(mfe, fav), max(mae, adv)
        if not armed and mfe >= arm:
            armed = True
            stop = entry * (1 - BE_PARK / 100) if long_ else entry * (1 + BE_PARK / 100)
    if end <= k + 1:
        return "NO_DATA", 0.0, 0, 0.0, 0.0
    j = end - 1
    pnl = (cl[j] / entry - 1) * 100 if long_ else (1 - cl[j] / entry) * 100
    return ("TIMEOUT" if end == k + 1 + MAX_HOLD_BARS else "OPEN_AT_END"), pnl, int(ct[j]), mfe, mae


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zips", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--start", default="2025-09-20")
    ap.add_argument("--end", default="2026-10-21")
    ap.add_argument("--limit-bars", type=int, default=0, help="stop after N bars (timing runs)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    sym = a.symbol

    data = {tf: load_tf(a.zips, sym, tf) for tf in TFS}
    s5 = data["5m"]
    if not s5:
        print(sym, "no 5m data")
        return
    t0 = datetime.fromisoformat(a.start).replace(tzinfo=timezone.utc).timestamp() * 1000
    t1 = datetime.fromisoformat(a.end).replace(tzinfo=timezone.utc).timestamp() * 1000

    # The LevelBook ages levels on the wall clock; pin it to replay time.
    # Swap the module's `time` binding for a shim. Assigning to
    # `level_book_mod.time.time` would rebind time.time for the whole process.
    clock = {"now": 0.0}

    class _ReplayClock:
        @staticmethod
        def time() -> float:
            return clock["now"]

        def __getattr__(self, name):  # monotonic, sleep, ... stay real
            return getattr(time, name)

    level_book_mod.time = _ReplayClock()
    logger.remove()  # evaluators log every fire at INFO; keep stdout readable
    logger.add(sys.stderr, level="WARNING")

    chan, smc, regime_svc, book = ScalpChannel(), SMCDetector(), RegimeService(), LevelBook()
    ind_cache: dict = {}
    last_lb_refresh = -1e18
    out_path = os.path.join(a.out, f"{sym}.csv")
    f = open(out_path, "w", newline="")
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()

    ks = np.where((s5["close_time"] >= t0) & (s5["close_time"] < t1))[0]
    if a.limit_bars:
        ks = ks[: a.limit_bars]
    started, n_sig, n_risk_rej = time.time(), 0, 0
    for k in ks:
        t = s5["close_time"][k]
        clock["now"] = t / 1000.0
        win, counts = {}, {}
        for tf in TFS:
            s = data[tf]
            if not s:
                continue
            n = int(np.searchsorted(s["close_time"], t, side="right"))
            if n < 30:
                continue
            counts[tf] = n
            win[tf] = window(s, n)
        if "5m" not in win or "15m" not in win:
            continue
        ind = {}
        for tf, n in counts.items():
            hit = ind_cache.get(tf)
            if hit is None or hit[0] != n:  # recompute only when that TF gained a bar
                hit = (n, compute_indicators_for_candle_dict({tf: win[tf]})[tf])
                ind_cache[tf] = hit
            ind[tf] = hit[1]

        # 24h quote volume from the 1h series, as the live pair list would carry it.
        h1 = data["1h"]
        n1 = counts.get("1h", 0)
        vol24 = float(h1["qvol"][max(0, n1 - 24):n1].sum()) if n1 else 0.0

        if t - last_lb_refresh >= 3_600_000:  # LEVEL_BOOK_REFRESH_SEC = 1h
            book.refresh(sym, {tf: win[tf] for tf in ("1d", "4h", "1h") if tf in win})
            last_lb_refresh = t

        res = smc.detect(sym, win, [], None, lookback=SMC_SCALP_LOOKBACK,
                         tolerance_pct=SMC_SCALP_TOLERANCE_PCT)
        smc_data = res.as_dict()
        profile = classify_pair_tier(sym, volume_24h_usd=vol24)
        smc_data["pair_profile"] = profile
        rr = regime_svc.classify(ind["5m"], win["5m"], timeframe="5m", symbol=sym,
                                 pair_tier=getattr(profile, "tier", "MIDCAP"))
        smc_data["regime_context"] = regime_svc.build_regime_context(
            rr, win["5m"], ind["5m"], vwap=0.0, symbol=sym,
            pair_tier=getattr(profile, "tier", "MIDCAP"))
        smc_data["level_book_levels"] = book.get_levels(sym)
        regime = rr.regime.value

        try:
            sigs = chan.evaluate(symbol=sym, candles=win, indicators=ind, smc_data=smc_data,
                                 spread_pct=SPREAD_PCT, volume_24h_usd=vol24, regime=regime)
        except Exception as exc:  # noqa: BLE001 — counted, never silent
            print(sym, int(t), "evaluate raised", type(exc).__name__, exc, file=sys.stderr)
            continue
        for sig in sigs or []:
            # Scanner order: build_risk_plan (per-setup SL cap: reject or compress,
            # TP rebuild) -> noise floor -> enqueue clamp. A rejected plan never
            # reaches the queue live, so it is counted and dropped here.
            try:
                risk = build_risk_plan(sig, ind, win, smc_data, SetupClass(sig.setup_class),
                                       SPREAD_PCT, channel="360_SCALP")
            except (ValueError, TypeError, KeyError, IndexError):
                n_risk_rej += 1
                continue
            if not risk.passed:
                n_risk_rej += 1
                continue
            sig.stop_loss, sig.tp1 = float(risk.stop_loss), float(risk.tp1)
            try:
                sl, tp1, noise = shape(sig, win)
            except (TypeError, ValueError, ZeroDivisionError):
                continue
            entry = float(sig.entry)
            long_ = sig.direction.value == "LONG"
            if entry <= 0 or (long_ and not (sl < entry < tp1)) or (not long_ and not (tp1 < entry < sl)):
                continue
            score, mtf_score, mtf_pass, comps = composite_score(sig, win, ind, res, regime,
                                                                smc_data["regime_context"])
            outcome, pnl, exit_ms, mfe, mae = walk(s5, int(k), long_, entry, sl, tp1, noise)
            w.writerow({
                "symbol": sym, "t_ms": int(t), "setup": getattr(sig, "setup_class", ""),
                "direction": sig.direction.value, "entry": entry, "sl": sl, "tp1": tp1,
                "sl_pct": round(abs(entry - sl) / entry * 100, 4),
                "tp1_pct": round(abs(tp1 - entry) / entry * 100, 4),
                "noise_pct": round(noise, 4), "confidence": round(float(getattr(sig, "confidence", 0) or 0), 2),
                "score": round(score, 2), "mtf_score": round(mtf_score, 3), "mtf_pass": int(mtf_pass),
                "regime": regime, "outcome": outcome, "pnl_pct": round(pnl, 4),
                "exit_ms": exit_ms, "mfe_pct": round(mfe, 4), "mae_pct": round(mae, 4),
                **{f"c_{k.replace('_adj', '')}": round(v, 2) for k, v in comps.items()},
            })
            n_sig += 1
    f.close()
    print(f"{sym} bars={len(ks)} signals={n_sig} risk_plan_rejected={n_risk_rej} secs={time.time() - started:.0f}")


if __name__ == "__main__":
    main()
