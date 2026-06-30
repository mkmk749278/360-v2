#!/usr/bin/env python3
"""BTC-State backfill validator — does BTC's directional state explain our long bleed?

WHY THIS EXISTS
---------------
Live data (≈1 month, 305 signals) shows the book loses entirely on the LONG side
(−25%) while SHORTs are net positive (+9.65%), and counter-trend reversal longs
(SR_FLIP / LSR / MOVER_TREND_PULLBACK) bleed −44% — they reach +1.3–2.8% MFE then
reverse *through* entry to the stop. The owner's thesis: this is not broken long
logic, it is longs fighting a BTC macro downtrend (BTC broke its 200-week MA in
June 2026). Alts couple to BTC *harder on the downside than the upside*, so a
counter-trend long into a falling, high-beta-correlated market is structurally
doomed — while the same setup short works.

Before we change any scoring code (an owner-sign-off item), we validate that thesis
on our OWN closed signals. This harness reconstructs, point-in-time and with NO
look-ahead, two numbers for every historical signal:

  * BTC_STATE  ∈ [-1, +1]  — how hostile BTC's direction was to a LONG at emit time
                             (−1 = strongly short-favourable, +1 = strongly long-favourable)
  * W_PAIR     ∈ [0, 1]    — how tightly THIS pair followed BTC on the downside
                             (downside beta × downside correlation; decoupled ≈ 0)

then stratifies realized outcomes by (side × BTC_STATE bucket × W_PAIR band).

ACCEPTANCE TEST (the thesis is validated iff):
  1. LONG win-rate / expectancy falls ~monotonically as BTC_STATE turns hostile.
  2. The collapse concentrates in HIGH-W_PAIR longs; DECOUPLED-pair longs survive.
  3. SHORTs do NOT show the same collapse (ideally improve as BTC turns hostile).
If (1)+(2) hold we proceed to the graded soft-confirmation wiring; if not, we retune
the design before shipping.

SCOPE (v1, price-only): BTC_STATE uses 5m/15m/1h EMA(8/21/55) stack + ATR-normalised
EMA21 slope + re-centred RSI, fast-weighted, then shrunk in extreme-ATR chop. BTC.D
dominance and market-structure/VWAP terms are deferred to v2 (BTC.D needs an external
market-cap feed). This is enough to test the core hypothesis.

WHERE IT RUNS
-------------
On the VPS (Binance reachable, signal history present):
    docker exec 360scalp-v2-engine python scripts/btc_state_backfill.py \
        --signals /app/data/<signal_history>.json --out /app/data/btc_state_backfill.csv

Reads a signal export (JSON or CSV) that MUST carry, per signal: symbol, side,
setup_class, an emission timestamp, and a realized outcome (real_pnl_pct and/or a
win flag). Column/field names are auto-detected (see _load_signals).

This script is a read-only diagnostic: it makes only public-market GET requests and
writes one CSV report. It never touches engine state, keys, or orders.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------------------
# Binance public kline fetch (time-ranged, paginated). Self-contained on purpose:
# the engine client (src/binance.fetch_klines) returns only the most-recent N candles,
# which cannot reconstruct a PAST signal's state. Runs on the VPS where Binance is
# reachable directly (no agent proxy).
# --------------------------------------------------------------------------------------
_FAPI = "https://fapi.binance.com/fapi/v1/klines"
_SPOT = "https://api.binance.com/api/v3/klines"
_INTERVAL_MS = {"5m": 300_000, "15m": 900_000, "1h": 3_600_000, "4h": 14_400_000}


def _http_get_json(url: str, timeout: float = 30.0) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "btc-state-backfill/1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_klines_range(
    symbol: str, interval: str, start_ms: int, end_ms: int, *, market: str = "futures"
) -> List[List[Any]]:
    """All klines for [start_ms, end_ms]. Paginated at 1000/call. Returns raw rows.

    Each row: [openTime, open, high, low, close, volume, closeTime, ...].
    """
    base = _FAPI if market == "futures" else _SPOT
    step = _INTERVAL_MS[interval]
    out: List[List[Any]] = []
    cur = start_ms
    while cur <= end_ms:
        url = f"{base}?symbol={symbol}&interval={interval}&startTime={cur}&endTime={end_ms}&limit=1000"
        try:
            rows = _http_get_json(url)
        except Exception as exc:  # noqa: BLE001 - diagnostic, surface and skip pair
            print(f"  ! kline fetch failed {symbol} {interval} @ {cur}: {exc}", file=sys.stderr)
            break
        if not rows:
            break
        out.extend(rows)
        last_open = int(rows[-1][0])
        nxt = last_open + step
        if nxt <= cur:  # no progress guard
            break
        cur = nxt
        if len(rows) < 1000:
            break
        time.sleep(0.12)  # be polite to the weight budget
    return out


# --------------------------------------------------------------------------------------
# Candle series — closed candles only, indexable point-in-time (no look-ahead).
# --------------------------------------------------------------------------------------
@dataclass
class Series:
    """Closed-candle OHLC series for one (symbol, interval), ascending by open time."""

    open_ms: List[int] = field(default_factory=list)
    close_ms: List[int] = field(default_factory=list)
    open: List[float] = field(default_factory=list)
    high: List[float] = field(default_factory=list)
    low: List[float] = field(default_factory=list)
    close: List[float] = field(default_factory=list)

    @classmethod
    def from_rows(cls, rows: Sequence[Sequence[Any]]) -> "Series":
        s = cls()
        for r in rows:
            s.open_ms.append(int(r[0]))
            s.open.append(float(r[1]))
            s.high.append(float(r[2]))
            s.low.append(float(r[3]))
            s.close.append(float(r[4]))
            s.close_ms.append(int(r[6]))
        return s

    def last_closed_idx(self, ts_ms: int) -> int:
        """Index of the most recent candle CLOSED at or before ts_ms (−1 if none).

        Binary search on close_ms; using close (not open) is what enforces
        no-look-ahead — a candle is only usable once it has closed.
        """
        lo, hi, ans = 0, len(self.close_ms) - 1, -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if self.close_ms[mid] <= ts_ms:
                ans = mid
                lo = mid + 1
            else:
                hi = mid - 1
        return ans


# --------------------------------------------------------------------------------------
# Pure indicators (operate on a closes/highs/lows window ending at a point-in-time idx).
# --------------------------------------------------------------------------------------
def ema(values: Sequence[float], period: int) -> Optional[float]:
    if len(values) < period:
        return None
    k = 2.0 / (period + 1.0)
    e = sum(values[:period]) / period
    for v in values[period:]:
        e = v * k + e * (1.0 - k)
    return e


def rsi(closes: Sequence[float], period: int = 14) -> Optional[float]:
    if len(closes) < period + 1:
        return None
    gains = losses = 0.0
    for i in range(-period, 0):
        d = closes[i] - closes[i - 1]
        if d >= 0:
            gains += d
        else:
            losses -= d
    avg_g, avg_l = gains / period, losses / period
    if avg_l == 0:
        return 100.0
    rs = avg_g / avg_l
    return 100.0 - 100.0 / (1.0 + rs)


def atr(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], period: int = 14) -> Optional[float]:
    n = len(closes)
    if n < period + 1:
        return None
    trs = []
    for i in range(n - period, n):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        trs.append(tr)
    return sum(trs) / period


def _clip(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# --------------------------------------------------------------------------------------
# BTC-State score (v1, price-only). Per-TF sub-score in [-1,+1], fast-weighted blend,
# shrunk by an extreme-volatility modulator. Faithful to the converged classifier spec
# (5m/15m/1h; EMA 8/21/55 stack + ATR-normalised slope + re-centred RSI).
# --------------------------------------------------------------------------------------
_TF_WEIGHTS = {"5m": 0.50, "15m": 0.32, "1h": 0.18}
_COMP_W = {"stack": 0.45, "slope": 0.35, "rsi": 0.20}  # sums to 1
_SLOPE_GAIN = 6.0  # tanh gain on ATR-normalised slope → |~1| in a strong trend


def _tf_subscore(s: Series, idx: int) -> Optional[float]:
    """Directional sub-score in [-1,+1] for one timeframe at candle index idx."""
    if idx < 0:
        return None
    closes = s.close[: idx + 1]
    highs = s.high[: idx + 1]
    lows = s.low[: idx + 1]
    e8, e21, e55 = ema(closes, 8), ema(closes, 21), ema(closes, 55)
    if e8 is None or e21 is None or e55 is None:
        return None
    price = closes[-1]

    # 1) EMA stack ordering: full bull = +1, full bear = -1, partial proportional.
    pts = 0.0
    pts += 1.0 if e8 > e21 else -1.0
    pts += 1.0 if e21 > e55 else -1.0
    pts += 1.0 if price > e8 else -1.0
    stack = pts / 3.0

    # 2) ATR-normalised EMA21 slope through tanh (direction + velocity, scale-free).
    e21_prev = ema(closes[:-3], 21) if len(closes) > 24 else None
    a = atr(highs, lows, closes, 14)
    if e21_prev is not None and a and a > 0:
        slope = math.tanh(_SLOPE_GAIN * (e21 - e21_prev) / a)
    else:
        slope = 0.0

    # 3) Re-centred RSI(14) → [-1,+1].
    r = rsi(closes, 14)
    mom = _clip((r - 50.0) / 50.0, -1.0, 1.0) if r is not None else 0.0

    return _clip(_COMP_W["stack"] * stack + _COMP_W["slope"] * slope + _COMP_W["rsi"] * mom, -1.0, 1.0)


def _atr_percentile(s: Series, idx: int, lookback: int = 200) -> Optional[float]:
    """Percentile (0..1) of current ATR within trailing window — chop detector."""
    if idx < 30:
        return None
    series = []
    start = max(15, idx - lookback)
    for j in range(start, idx + 1):
        a = atr(s.high[: j + 1], s.low[: j + 1], s.close[: j + 1], 14)
        if a is not None:
            series.append(a)
    if len(series) < 20:
        return None
    cur = series[-1]
    return sum(1 for v in series if v <= cur) / len(series)


def btc_state_score(
    btc: Dict[str, Series], ts_ms: int, *, vol_lookback: int = 200
) -> Optional[float]:
    """Graded BTC directional state in [-1,+1] at ts_ms (no look-ahead). None if cold."""
    subs: Dict[str, float] = {}
    for tf, s in btc.items():
        if tf not in _TF_WEIGHTS:
            continue
        sub = _tf_subscore(s, s.last_closed_idx(ts_ms))
        if sub is not None:
            subs[tf] = sub
    if not subs:
        return None
    wsum = sum(_TF_WEIGHTS[tf] for tf in subs)
    blended = sum(_TF_WEIGHTS[tf] * v for tf, v in subs.items()) / wsum

    # Volatility modulator: shrink magnitude toward 0 in extreme chop (low conviction).
    vol_scale = 1.0
    if "15m" in btc:
        pct = _atr_percentile(btc["15m"], btc["15m"].last_closed_idx(ts_ms), vol_lookback)
        if pct is not None:
            if pct > 0.85:
                vol_scale = 0.4
            elif pct < 0.15:
                vol_scale = 0.8
    return _clip(blended * vol_scale, -1.0, 1.0)


# --------------------------------------------------------------------------------------
# Per-pair downside coupling weight: downside beta × downside correlation on 15m returns.
# Computed on the trailing window ending at the signal (no look-ahead). Decoupled ≈ 0.
# --------------------------------------------------------------------------------------
def _returns_aligned(pair: Series, btc: Series, end_ms: int, lookback: int) -> Tuple[List[float], List[float]]:
    pi, bi = pair.last_closed_idx(end_ms), btc.last_closed_idx(end_ms)
    if pi < 2 or bi < 2:
        return [], []
    # Align by open time so the same bars are compared.
    btc_by_open = {btc.open_ms[j]: j for j in range(max(0, bi - lookback - 2), bi + 1)}
    rp: List[float] = []
    rb: List[float] = []
    start = max(1, pi - lookback)
    for j in range(start, pi + 1):
        ot = pair.open_ms[j]
        bj = btc_by_open.get(ot)
        if bj is None or bj < 1:
            continue
        if pair.close[j - 1] <= 0 or btc.close[bj - 1] <= 0:
            continue
        rp.append(math.log(pair.close[j] / pair.close[j - 1]))
        rb.append(math.log(btc.close[bj] / btc.close[bj - 1]))
    return rp, rb


def pair_downside_weight(
    pair: Series, btc15: Series, end_ms: int, *, lookback: int = 96, min_pts: int = 20
) -> Optional[Tuple[float, float, float]]:
    """(beta_down, corr_down, w_pair) on BTC-negative 15m bars. None if too few points."""
    rp, rb = _returns_aligned(pair, btc15, end_ms, lookback)
    dp = [(p, b) for p, b in zip(rp, rb) if b < 0]
    if len(dp) < min_pts:
        return None
    xs = [b for _, b in dp]  # BTC returns
    ys = [p for p, _ in dp]  # pair returns
    n = len(dp)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / n
    vx = sum((x - mx) ** 2 for x in xs) / n
    vy = sum((y - my) ** 2 for y in ys) / n
    if vx <= 0 or vy <= 0:
        return None
    beta_down = cov / vx
    corr_down = cov / math.sqrt(vx * vy)
    w_pair = _clip(_clip(beta_down, 0.0, 2.0) * max(0.0, corr_down), 0.0, 1.0)
    return beta_down, corr_down, w_pair


# --------------------------------------------------------------------------------------
# Signal loading — flexible field/column auto-detection.
# --------------------------------------------------------------------------------------
@dataclass
class Sig:
    symbol: str
    side: str
    setup_class: str
    ts_ms: int
    real_pnl: Optional[float]
    is_win: Optional[bool]


_TS_KEYS = ["emitted_at", "created_at", "signal_ts", "timestamp", "ts", "entry_ts", "open_time", "time"]
_SYM_KEYS = ["symbol", "pair"]
_SIDE_KEYS = ["side", "direction"]
_SETUP_KEYS = ["setup_class", "setup", "channel", "path"]
_PNL_KEYS = ["real_pnl_pct", "real_pnl", "pnl_pct", "result_pct", "strategy_pct"]


def _first(d: Dict[str, Any], keys: Sequence[str]) -> Optional[Any]:
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
        for dk in d:
            if dk.lower() == k:
                if d[dk] not in (None, ""):
                    return d[dk]
    return None


def _to_ms(v: Any) -> Optional[int]:
    """Epoch s/ms or ISO-8601 → epoch ms."""
    if v is None:
        return None
    try:
        f = float(v)
        return int(f * 1000) if f < 1e12 else int(f)  # seconds vs ms heuristic
    except (TypeError, ValueError):
        pass
    try:
        import datetime as _dt

        s = str(v).replace("Z", "+00:00")
        return int(_dt.datetime.fromisoformat(s).timestamp() * 1000)
    except Exception:  # noqa: BLE001
        return None


def _load_signals(path: str) -> List[Sig]:
    raw: List[Dict[str, Any]]
    if path.endswith(".json"):
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict):
            for key in ("signals", "records", "completed", "rows", "history"):
                if isinstance(data.get(key), list):
                    data = data[key]
                    break
        raw = data if isinstance(data, list) else []
    else:
        with open(path) as f:
            raw = list(csv.DictReader(f))

    out: List[Sig] = []
    skipped_ts = 0
    for d in raw:
        ts = _to_ms(_first(d, _TS_KEYS))
        sym = _first(d, _SYM_KEYS)
        side = _first(d, _SIDE_KEYS)
        if ts is None:
            skipped_ts += 1
            continue
        if not sym or not side:
            continue
        pnl_raw = _first(d, _PNL_KEYS)
        try:
            pnl = float(pnl_raw) if pnl_raw is not None else None
        except (TypeError, ValueError):
            pnl = None
        win = None
        if "is_win" in d:
            win = str(d["is_win"]).lower() in ("1", "true", "yes")
        elif pnl is not None:
            win = pnl > 0
        out.append(
            Sig(
                symbol=str(sym).upper(),
                side=str(side).upper(),
                setup_class=str(_first(d, _SETUP_KEYS) or "").upper(),
                ts_ms=ts,
                real_pnl=pnl,
                is_win=win,
            )
        )
    if skipped_ts:
        print(
            f"  ! {skipped_ts} rows skipped (no emission timestamp). The harness REQUIRES a "
            f"per-signal timestamp — re-export including one of {_TS_KEYS}.",
            file=sys.stderr,
        )
    return out


# --------------------------------------------------------------------------------------
# Stratification + report.
# --------------------------------------------------------------------------------------
def _bucket_state(b: float) -> str:
    if b <= -0.6:
        return "5_strong_short"
    if b <= -0.25:
        return "4_short"
    if b < 0.25:
        return "3_neutral"
    if b < 0.6:
        return "2_long"
    return "1_strong_long"


def _wband(w: float) -> str:
    if w >= 0.6:
        return "BTC_LED"
    if w >= 0.3:
        return "INFLUENCED"
    return "DECOUPLED"


def _agg(rows: List[Dict[str, Any]]) -> Tuple[int, float, float]:
    n = len(rows)
    if n == 0:
        return 0, 0.0, 0.0
    pnls = [r["real_pnl"] for r in rows if r["real_pnl"] is not None]
    wins = [r for r in rows if r["is_win"]]
    wr = len(wins) / n * 100.0
    avg = sum(pnls) / len(pnls) if pnls else 0.0
    return n, wr, avg


def main() -> int:
    ap = argparse.ArgumentParser(description="BTC-State backfill validator")
    ap.add_argument("--signals", required=True, help="signal history export (.json or .csv) WITH timestamps")
    ap.add_argument("--out", default="btc_state_backfill.csv", help="per-signal enriched output CSV")
    ap.add_argument("--market", default="futures", choices=["futures", "spot"])
    ap.add_argument("--min-n", type=int, default=5, help="min cohort size to print a stratified row")
    ap.add_argument("--warmup-candles", type=int, default=260, help="pre-window candles for indicator warmup")
    args = ap.parse_args()

    sigs = _load_signals(args.signals)
    if not sigs:
        print("No usable signals (need symbol, side, timestamp). Aborting.", file=sys.stderr)
        return 2
    print(f"Loaded {len(sigs)} signals with timestamps.")

    t_min = min(s.ts_ms for s in sigs)
    t_max = max(s.ts_ms for s in sigs)
    span_days = (t_max - t_min) / 86_400_000
    print(f"Span: {span_days:.1f} days. Fetching BTC 5m/15m/1h + {len({s.symbol for s in sigs})} pairs…")

    # Pre-fetch BTC reference series across the whole span (+warmup) once.
    btc: Dict[str, Series] = {}
    for tf in ("5m", "15m", "1h"):
        start = t_min - args.warmup_candles * _INTERVAL_MS[tf]
        rows = fetch_klines_range("BTCUSDT", tf, start, t_max, market=args.market)
        btc[tf] = Series.from_rows(rows)
        print(f"  BTC {tf}: {len(btc[tf].close)} candles")
    if not btc["15m"].close:
        print("BTC fetch failed — cannot reconstruct state. Aborting.", file=sys.stderr)
        return 3

    # Per-pair 15m series (for downside beta), fetched once per unique symbol.
    pair_series: Dict[str, Series] = {}
    start15 = t_min - (96 + 8) * _INTERVAL_MS["15m"]
    for sym in sorted({s.symbol for s in sigs}):
        rows = fetch_klines_range(sym, "15m", start15, t_max, market=args.market)
        pair_series[sym] = Series.from_rows(rows)

    enriched: List[Dict[str, Any]] = []
    for s in sigs:
        b = btc_state_score(btc, s.ts_ms)
        w = None
        ps = pair_series.get(s.symbol)
        if ps and ps.close:
            res = pair_downside_weight(ps, btc["15m"], s.ts_ms)
            if res is not None:
                w = res[2]
        if b is None:
            continue
        align = (1.0 if s.side == "LONG" else -1.0) * b  # >0 with BTC, <0 against
        enriched.append(
            {
                "symbol": s.symbol,
                "side": s.side,
                "setup_class": s.setup_class,
                "ts_ms": s.ts_ms,
                "btc_state": round(b, 4),
                "w_pair": round(w, 4) if w is not None else "",
                "alignment": round(align, 4),
                "state_bucket": _bucket_state(b),
                "wband": _wband(w) if w is not None else "UNKNOWN",
                "real_pnl": s.real_pnl,
                "is_win": bool(s.is_win),
            }
        )

    # Write per-signal CSV (feeds the ops Profit page slice-by-btc_state).
    if enriched:
        with open(args.out, "w", newline="") as f:
            wri = csv.DictWriter(f, fieldnames=list(enriched[0].keys()))
            wri.writeheader()
            wri.writerows(enriched)
    print(f"\nWrote {len(enriched)} enriched rows → {args.out}\n")

    _report(enriched, args.min_n)
    return 0


def _report(rows: List[Dict[str, Any]], min_n: int) -> None:
    def fmt(title: str, groups: Dict[str, List[Dict[str, Any]]]) -> None:
        print(f"\n=== {title} ===")
        print(f"{'cohort':26} {'n':>4} {'win%':>6} {'avg_pnl':>9}")
        for k in sorted(groups):
            n, wr, avg = _agg(groups[k])
            if n < min_n:
                continue
            print(f"{k:26} {n:>4} {wr:>6.0f} {avg:>+9.3f}")

    for side in ("LONG", "SHORT"):
        side_rows = [r for r in rows if r["side"] == side]
        g: Dict[str, List[Dict[str, Any]]] = {}
        for r in side_rows:
            g.setdefault(r["state_bucket"], []).append(r)
        fmt(f"{side}  by BTC_STATE bucket  (hostile→favourable: 5_strong_short … 1_strong_long)", g)

    # The core test: counter-trend longs (BTC short-favourable) by pair coupling band.
    ct_long = [r for r in rows if r["side"] == "LONG" and r["btc_state"] <= -0.25 and r["wband"] != "UNKNOWN"]
    g2: Dict[str, List[Dict[str, Any]]] = {}
    for r in ct_long:
        g2.setdefault(r["wband"], []).append(r)
    fmt("COUNTER-TREND LONGS (BTC short-favourable) by pair coupling band", g2)

    print("\n--- ACCEPTANCE TEST ---")
    print("Thesis validated iff: (1) LONG win-rate falls monotonically 1_strong_long→5_strong_short,")
    print("(2) the collapse is in BTC_LED longs while DECOUPLED longs survive, (3) SHORTs don't collapse.")
    print("Read the tables above against those three conditions before approving the wiring.")


if __name__ == "__main__":
    raise SystemExit(main())
