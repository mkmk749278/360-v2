from __future__ import annotations

import ast
import json
import re
import statistics
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

TP_LABELS = {"TP", "TP1", "TP2", "TP3", "TP_HIT", "TP1_HIT", "TP2_HIT", "TP3_HIT", "TAKE_PROFIT", "WIN"}
SL_LABELS = {"SL", "SL_HIT", "STOP_LOSS", "LOSS"}
_POST_CORRECTION_TARGET_SETUPS = ("SR_FLIP_RETEST", "TREND_PULLBACK_EMA")


def _median(values: Iterable[Optional[float]]) -> Optional[float]:
    nums = [float(v) for v in values if isinstance(v, (int, float))]
    if not nums:
        return None
    return float(statistics.median(nums))


def _pct(num: int, den: int) -> float:
    if den <= 0:
        return 0.0
    return round((num / den) * 100.0, 1)


def _outcome_label(record: Dict[str, Any]) -> str:
    return str(
        record.get("outcome_label") or record.get("outcome") or record.get("status") or ""
    ).upper()


def _parse_funnel_key_for_channel(key: str, channel: str) -> Optional[Tuple[str, str, str]]:
    """Parse a funnel key and return (stage, family, setup) for one channel.

    Key contract: stage:channel:family:setup.
    Stage can include nested tokens (for example ``geometry:final_live:changed``),
    and setup can include ``:``, so parsing is anchored around ``:<channel>:``.
    """
    key_text = str(key)
    channel_token = f":{channel}:"
    if channel_token not in key_text:
        return None
    stage, rest = key_text.split(channel_token, 1)
    family_setup = rest.split(":", 1)
    if len(family_setup) != 2:
        return None
    family, setup = family_setup
    return stage, family, setup


def _parse_csv_filter(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [part.strip().upper() for part in str(raw).split(",") if part.strip()]


def _matches_filter(value: str, filters: List[str], substring: bool = False) -> bool:
    if not filters:
        return True
    probe = (value or "").upper()
    if substring:
        return any(token in probe for token in filters)
    return probe in filters


def parse_path_funnel_from_logs(log_text: str, channel: str) -> Dict[str, int]:
    counters: Dict[str, int] = defaultdict(int)
    if not log_text:
        return {}
    for line in log_text.splitlines():
        if "Path funnel (last 100 cycles): path=" not in line:
            continue
        try:
            fragment = line.split("path=", 1)[1].split(" channel=", 1)[0]
            parsed = ast.literal_eval(fragment)
        except (ValueError, SyntaxError):
            continue
        if not isinstance(parsed, dict):
            continue
        for key, value in parsed.items():
            parsed_key = _parse_funnel_key_for_channel(str(key), channel)
            if parsed_key is None:
                continue
            try:
                n = int(value or 0)
            except (TypeError, ValueError):
                n = 0
            if n > 0:
                counters[str(key)] += n
    return dict(counters)


def parse_channel_funnel_from_logs(log_text: str, channel: str) -> Dict[str, int]:
    counters: Dict[str, int] = defaultdict(int)
    if not log_text:
        return {}
    channel_prefix = f":{channel}:"
    for line in log_text.splitlines():
        if "Path funnel (last 100 cycles): path=" not in line:
            continue
        try:
            fragment = line.split(" channel=", 1)[1]
            parsed = ast.literal_eval(fragment)
        except (IndexError, ValueError, SyntaxError):
            continue
        if not isinstance(parsed, dict):
            continue
        for key, value in parsed.items():
            key_text = str(key)
            if channel_prefix not in key_text:
                continue
            try:
                n = int(value or 0)
            except (TypeError, ValueError):
                n = 0
            if n > 0:
                counters[key_text] += n
    return dict(counters)


_REGIME_LINE_MARKER = "Regime distribution (last 100 cycles):"
_QUIET_SCALP_BLOCK_MARKER = "QUIET_SCALP_BLOCK "
_CONFIDENCE_GATE_MARKER = "confidence_gate "
_PATH_FUNNEL_MARKER = "Path funnel (last 100 cycles):"
# Phase 5 / 2a / 2b free-channel content rollout instrumentation.
# Each successful free-channel post emits a structured marker so the truth
# report can attribute volume by source (macro_alert / btc_move / regime_shift
# / fear_greed / macro_news / signal_close / signal_highlight) and severity.
_FREE_CHANNEL_POST_MARKER = "free_channel_post "
_FREE_CHANNEL_POST_RE = re.compile(
    r"free_channel_post\s+source=(?P<source>\S+)\s+severity=(?P<severity>\S+)"
    r"(?:\s+symbol=(?P<symbol>\S+))?"
)
# Phase A pre-TP grab instrumentation.  Each successful pre-TP fire emits
# a structured marker recording the resolved threshold, its source
# (static / atr / atr_floored), the raw ATR value, leverage assumed, and
# the net-of-fees % banked.  Aggregating these answers "is pre-TP firing
# at the rate and on the pairs we expected?" — the only honest test of
# the ATR-adaptive resolver in production.
_PRE_TP_FIRE_MARKER = "pre_tp_fire "
_PRE_TP_FIRE_RE = re.compile(
    r"pre_tp_fire\s+(?P<symbol>\S+)\s+(?P<direction>\S+)\s+\[(?P<setup>[^\]]+)\]\s+"
    r"threshold=(?P<threshold>[-\d.]+)\s+"
    r"source=(?P<source>\S+)\s+"
    r"atr_last=(?P<atr_last>\S+)\s+"
    r"leverage=(?P<leverage>[-\d.]+)x\s+"
    r"net=(?P<net>[-+\d.]+)\s+"
    r"age=(?P<age>[-\d.]+)s?"
)

# Match e.g. "QUIET_SCALP_BLOCK BTCUSDT 360_SCALP conf=58.2 < min=60.0"
_QUIET_SCALP_BLOCK_RE = re.compile(
    r"QUIET_SCALP_BLOCK\s+(?P<symbol>\S+)\s+(?P<channel>\S+)\s+conf=(?P<conf>[-\d.]+)\s+<\s+min=(?P<min>[-\d.]+)"
)

# Match e.g. "confidence_gate BTCUSDT 360_SCALP [SETUP_NAME]: decision=filtered reason=quiet_scalp_min_confidence raw=58.2 ..."
_CONFIDENCE_GATE_RE = re.compile(
    r"confidence_gate\s+(?P<symbol>\S+)\s+(?P<channel>\S+)\s+\[(?P<setup>[^\]]+)\]:\s+"
    r"decision=(?P<decision>\S+)\s+reason=(?P<reason>\S+)"
)

# Tier-2: extracts the full numeric breakdown emitted alongside the
# decision/reason (raw/composite/pre_soft/final/threshold + penalties +
# adjustments + components).  This is the data that answers "where are the
# 14.83 confidence-gap points being lost" — without it we have no principled
# way to decide whether to tune component weights or scoring thresholds.
_CONFIDENCE_COMPONENT_RE = re.compile(
    r"confidence_gate\s+(?P<symbol>\S+)\s+(?P<channel>\S+)\s+\[(?P<setup>[^\]]+)\]:\s+"
    r"decision=(?P<decision>\S+)\s+reason=(?P<reason>\S+)\s+"
    r"raw=(?P<raw>[-\d.]+)\s+"
    r"composite=(?P<composite>[-\d.]+)\s+"
    r"pre_soft=(?P<pre_soft>[-\d.]+)\s+"
    r"final=(?P<final>[-\d.]+)\s+"
    r"threshold=(?P<threshold>[-\d.]+)\s+"
    r"penalties\(eval=(?P<eval_pen>[-\d.]+),gate=(?P<gate_pen>[-\d.]+),"
    r"total=(?P<total_pen>[-\d.]+),pair_analysis=(?P<pair_pen>[-\d.]+)\)\s+"
    r"adjustments\(feedback=(?P<feedback>[-+\d.]+),stat_filter=(?P<stat_filter>[-+\d.]+),"
    r"regime_transition=(?P<regime_trans>[-+\d.]+)\)\s+"
    r"components\(market=(?P<market>[-\d.]+),execution=(?P<execution>[-\d.]+),"
    r"risk=(?P<risk>[-\d.]+),thesis_adj=(?P<thesis_adj>[-\d.]+)\)"
    # Optional engine breakdown — present after the VSB diagnosis instrumentation.
    # These six dimensions actually sum to ``final`` (modulo penalties +
    # adjustments + the 100-cap), so this is the breakdown that answers
    # "where is the score actually coming from?"  Older log lines without
    # this group are still parsed correctly thanks to the optional wrapper.
    r"(?:\s+engine\(smc=(?P<smc>[-\d.]+),regime=(?P<regime>[-\d.]+),"
    r"volume=(?P<volume>[-\d.]+),indicators=(?P<indicators>[-\d.]+),"
    r"patterns=(?P<patterns>[-\d.]+),mtf=(?P<mtf>[-\d.]+)\))?"
    # Optional soft-penalty breakdown — present after the LSR-zero-volume
    # investigation instrumentation (2026-05-03).  Splits the aggregate
    # ``gate=`` penalty into its 6 sub-types so we can attribute WHICH
    # soft gate is dragging confidence down (HTF mismatch?  OI flip?
    # VWAP overextension?  Cluster suppression?).  Older log lines
    # without this group are still parsed correctly.
    r"(?:\s+soft_penalties\(vwap=(?P<sp_vwap>[-\d.]+),kz=(?P<sp_kz>[-\d.]+),"
    r"oi=(?P<sp_oi>[-\d.]+),spoof=(?P<sp_spoof>[-\d.]+),"
    r"vol_div=(?P<sp_vol_div>[-\d.]+),cluster=(?P<sp_cluster>[-\d.]+)\))?"
)


def parse_regime_distribution_from_logs(log_text: str) -> Dict[str, int]:
    """Aggregate regime classification counts from periodic scanner emissions.

    Scanner emits ``Regime distribution (last 100 cycles): {QUIET: N, ...}``
    every 100 cycles. We sum these dicts across the window so the report can
    show e.g. "QUIET 95.4%, RANGING 4.6%" — answering whether the market itself
    is the binding constraint on signal flow.
    """
    counters: Dict[str, int] = defaultdict(int)
    if not log_text:
        return {}
    for line in log_text.splitlines():
        if _REGIME_LINE_MARKER not in line:
            continue
        try:
            fragment = line.split(_REGIME_LINE_MARKER, 1)[1].strip()
            parsed = ast.literal_eval(fragment)
        except (ValueError, SyntaxError, IndexError):
            continue
        if not isinstance(parsed, dict):
            continue
        for regime, count in parsed.items():
            try:
                n = int(count or 0)
            except (TypeError, ValueError):
                n = 0
            if n > 0:
                counters[str(regime)] += n
    return dict(counters)


def parse_quiet_scalp_block_from_logs(
    log_text: str,
    channel: str,
) -> Dict[str, Any]:
    """Parse QUIET_SCALP_BLOCK occurrences for the given channel.

    The QUIET_SCALP_BLOCK gate is the historical largest bottleneck during
    QUIET-regime windows: high-quality candidates die at the confidence-floor
    check unless their setup is on the exempt list. Returns total count, by-symbol
    breakdown, and a confidence-distance histogram (how far below threshold).
    """
    total = 0
    by_symbol: Dict[str, int] = defaultdict(int)
    confidence_gap_sum = 0.0
    confidence_gap_count = 0
    if not log_text:
        return {"total": 0, "by_symbol": {}, "average_gap_to_min": 0.0, "samples": 0}
    for line in log_text.splitlines():
        if _QUIET_SCALP_BLOCK_MARKER not in line:
            continue
        match = _QUIET_SCALP_BLOCK_RE.search(line)
        if not match:
            continue
        if match.group("channel") != channel:
            continue
        total += 1
        by_symbol[match.group("symbol")] += 1
        try:
            gap = float(match.group("min")) - float(match.group("conf"))
            confidence_gap_sum += gap
            confidence_gap_count += 1
        except ValueError:
            pass
    avg_gap = (
        confidence_gap_sum / confidence_gap_count if confidence_gap_count > 0 else 0.0
    )
    return {
        "total": total,
        "by_symbol": dict(sorted(by_symbol.items(), key=lambda kv: -kv[1])[:20]),
        "average_gap_to_min": round(avg_gap, 2),
        "samples": confidence_gap_count,
    }


def parse_confidence_gate_decisions_from_logs(
    log_text: str,
    channel: str,
) -> Dict[str, Dict[str, Dict[str, int]]]:
    """Parse confidence_gate decisions per setup: {setup: {decision: {reason: count}}}.

    The confidence_gate emit covers every signal that survives evaluation but
    must clear the final scoring threshold. Histogram surfaces:
    * which setups consistently get filtered vs accepted
    * the dominant rejection reason (e.g. quiet_scalp_min_confidence,
      confidence_below_threshold, regime_penalty)
    """
    by_setup: Dict[str, Dict[str, Dict[str, int]]] = {}
    if not log_text:
        return {}
    for line in log_text.splitlines():
        if _CONFIDENCE_GATE_MARKER not in line:
            continue
        match = _CONFIDENCE_GATE_RE.search(line)
        if not match:
            continue
        if match.group("channel") != channel:
            continue
        setup = match.group("setup")
        decision = match.group("decision")
        reason = match.group("reason")
        setup_bucket = by_setup.setdefault(setup, {})
        decision_bucket = setup_bucket.setdefault(decision, defaultdict(int))
        decision_bucket[reason] += 1
    # Convert defaultdicts to plain dicts for clean serialization
    return {
        setup: {decision: dict(reasons) for decision, reasons in decisions.items()}
        for setup, decisions in by_setup.items()
    }


def parse_confidence_gate_components_from_logs(
    log_text: str,
    channel: str,
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Aggregate component-score statistics per setup × decision.

    Returns ``{setup: {decision: {samples, avg_final, avg_threshold,
    avg_gap_to_threshold, components: {market, execution, risk, thesis_adj},
    avg_total_penalty}}}`` — a histogram of where confidence is sourced from
    and where it's lost.

    The 14.83-pt avg gap visible in PR #260's QUIET_SCALP_BLOCK section
    was actionable but too coarse — it told us *that* candidates fall short
    but not *which component* drags them under the threshold.  This data is
    already emitted in every ``confidence_gate ...`` line by scanner.__init__;
    we just weren't extracting it.
    """
    by_setup: Dict[str, Dict[str, Dict[str, Any]]] = {}
    if not log_text:
        return {}

    # Accumulators: setup → decision → field → running sum
    sums: Dict[str, Dict[str, Dict[str, float]]] = {}
    counts: Dict[str, Dict[str, int]] = {}

    for line in log_text.splitlines():
        if _CONFIDENCE_GATE_MARKER not in line:
            continue
        match = _CONFIDENCE_COMPONENT_RE.search(line)
        if not match:
            continue
        if match.group("channel") != channel:
            continue
        setup = match.group("setup")
        decision = match.group("decision")

        try:
            fields = {
                "final": float(match.group("final")),
                "threshold": float(match.group("threshold")),
                "raw": float(match.group("raw")),
                "composite": float(match.group("composite")),
                "total_penalty": float(match.group("total_pen")),
                "market": float(match.group("market")),
                "execution": float(match.group("execution")),
                "risk": float(match.group("risk")),
                "thesis_adj": float(match.group("thesis_adj")),
            }
        except (ValueError, TypeError):
            continue

        # Engine breakdown is optional — older log lines (pre-VSB instrumentation)
        # don't include it.  When present, these six dimensions actually sum to
        # ``final`` (modulo penalties/adjustments and the 100-cap), so they're the
        # breakdown that explains the gap that the legacy components miss.
        engine_fields: Dict[str, float] = {}
        if match.group("smc") is not None:
            try:
                engine_fields = {
                    "smc": float(match.group("smc")),
                    "regime": float(match.group("regime")),
                    "volume": float(match.group("volume")),
                    "indicators": float(match.group("indicators")),
                    "patterns": float(match.group("patterns")),
                    "mtf": float(match.group("mtf")),
                }
            except (ValueError, TypeError):
                engine_fields = {}

        # Soft-penalty per-type breakdown (LSR diagnosis instrumentation).
        # Splits the aggregate gate penalty into VWAP / KZ / OI / SPOOF /
        # VOL_DIV / CLUSTER so the truth report can answer "which gate
        # is firing hardest?"  Optional — older log lines have no group.
        soft_penalty_fields: Dict[str, float] = {}
        if match.group("sp_vwap") is not None:
            try:
                soft_penalty_fields = {
                    "vwap": float(match.group("sp_vwap")),
                    "kz": float(match.group("sp_kz")),
                    "oi": float(match.group("sp_oi")),
                    "spoof": float(match.group("sp_spoof")),
                    "vol_div": float(match.group("sp_vol_div")),
                    "cluster": float(match.group("sp_cluster")),
                }
            except (ValueError, TypeError):
                soft_penalty_fields = {}

        bucket = sums.setdefault(setup, {}).setdefault(decision, defaultdict(float))
        for k, v in fields.items():
            bucket[k] += v
        for k, v in engine_fields.items():
            bucket[f"engine_{k}"] += v
        if engine_fields:
            bucket["engine_samples"] += 1
        for k, v in soft_penalty_fields.items():
            bucket[f"sp_{k}"] += v
        if soft_penalty_fields:
            bucket["sp_samples"] += 1
        counts.setdefault(setup, {})
        counts[setup][decision] = counts[setup].get(decision, 0) + 1

    for setup, decisions in sums.items():
        by_setup[setup] = {}
        for decision, totals in decisions.items():
            n = counts[setup][decision]
            avgs = {k: round(v / n, 2) for k, v in totals.items() if not k.startswith("engine_")}
            entry: Dict[str, Any] = {
                "samples": n,
                "avg_final": avgs["final"],
                "avg_threshold": avgs["threshold"],
                "avg_gap_to_threshold": round(avgs["threshold"] - avgs["final"], 2),
                "avg_raw": avgs["raw"],
                "avg_composite": avgs["composite"],
                "avg_total_penalty": avgs["total_penalty"],
                "components": {
                    "avg_market": avgs["market"],
                    "avg_execution": avgs["execution"],
                    "avg_risk": avgs["risk"],
                    "avg_thesis_adj": avgs["thesis_adj"],
                },
            }
            engine_n = int(totals.get("engine_samples", 0))
            if engine_n > 0:
                entry["engine_components"] = {
                    "samples": engine_n,
                    "avg_smc": round(totals["engine_smc"] / engine_n, 2),
                    "avg_regime": round(totals["engine_regime"] / engine_n, 2),
                    "avg_volume": round(totals["engine_volume"] / engine_n, 2),
                    "avg_indicators": round(totals["engine_indicators"] / engine_n, 2),
                    "avg_patterns": round(totals["engine_patterns"] / engine_n, 2),
                    "avg_mtf": round(totals["engine_mtf"] / engine_n, 2),
                }
            sp_n = int(totals.get("sp_samples", 0))
            if sp_n > 0:
                entry["soft_penalty_breakdown"] = {
                    "samples": sp_n,
                    "avg_vwap": round(totals["sp_vwap"] / sp_n, 2),
                    "avg_kz": round(totals["sp_kz"] / sp_n, 2),
                    "avg_oi": round(totals["sp_oi"] / sp_n, 2),
                    "avg_spoof": round(totals["sp_spoof"] / sp_n, 2),
                    "avg_vol_div": round(totals["sp_vol_div"] / sp_n, 2),
                    "avg_cluster": round(totals["sp_cluster"] / sp_n, 2),
                }
            by_setup[setup][decision] = entry
    return by_setup


def count_log_markers(log_text: str) -> Dict[str, int]:
    """Count occurrences of key periodic log markers in the window.

    Used to surface a "log parse diagnostics" section in the truth report.
    If e.g. ``path_funnel`` count is 0 but signals were emitted, the issue
    is log retention or emission cadence — not parser breakage.
    """
    if not log_text:
        return {
            "path_funnel": 0,
            "regime_distribution": 0,
            "quiet_scalp_block": 0,
            "confidence_gate": 0,
            "free_channel_post": 0,
            "pre_tp_fire": 0,
            "total_lines": 0,
        }
    lines = log_text.splitlines()
    return {
        "path_funnel": sum(1 for ln in lines if _PATH_FUNNEL_MARKER in ln),
        "regime_distribution": sum(1 for ln in lines if _REGIME_LINE_MARKER in ln),
        "quiet_scalp_block": sum(1 for ln in lines if _QUIET_SCALP_BLOCK_MARKER in ln),
        "confidence_gate": sum(1 for ln in lines if _CONFIDENCE_GATE_MARKER in ln),
        "free_channel_post": sum(1 for ln in lines if _FREE_CHANNEL_POST_MARKER in ln),
        "pre_tp_fire": sum(1 for ln in lines if _PRE_TP_FIRE_MARKER in ln),
        "total_lines": len(lines),
    }


def parse_pre_tp_fires_from_logs(log_text: str) -> Dict[str, Any]:
    """Parse ``pre_tp_fire`` markers into per-setup × source aggregates.

    Returns a dict with:
      * ``total``: int — total number of pre-TP fires in window
      * ``by_setup``: {setup → {fires, avg_threshold, avg_net, avg_age_sec,
        avg_atr_pct, by_source: {source → count}}}
      * ``by_source``: {source → count}  (static / atr / atr_floored)
      * ``by_symbol``: {symbol → count}  (top fire pairs)
      * ``avg_threshold``: float (overall)
      * ``avg_net``: float (overall)

    Empty when log_text is empty or contains no fires — caller should treat
    zero counts as "pre-TP did not fire in this window," which is also the
    expected baseline if PRE_TP_ENABLED is still false on the engine.
    """
    if not log_text:
        return {
            "total": 0,
            "by_setup": {},
            "by_source": {},
            "by_symbol": {},
            "avg_threshold": 0.0,
            "avg_net": 0.0,
        }

    by_setup: Dict[str, Dict[str, Any]] = {}
    by_source: Dict[str, int] = defaultdict(int)
    by_symbol: Dict[str, int] = defaultdict(int)
    threshold_total = 0.0
    net_total = 0.0
    age_total = 0.0
    atr_pct_total = 0.0
    atr_pct_samples = 0
    fires = 0

    for line in log_text.splitlines():
        if _PRE_TP_FIRE_MARKER not in line:
            continue
        m = _PRE_TP_FIRE_RE.search(line)
        if m is None:
            continue
        try:
            symbol = m.group("symbol")
            setup = m.group("setup")
            source = m.group("source")
            threshold = float(m.group("threshold"))
            net = float(m.group("net"))
            age = float(m.group("age"))
            atr_raw = m.group("atr_last")
            atr_last = None
            if atr_raw not in ("-", "None", ""):
                try:
                    atr_last = float(atr_raw)
                except (TypeError, ValueError):
                    atr_last = None
        except (ValueError, TypeError):
            continue

        fires += 1
        by_source[source] += 1
        by_symbol[symbol] += 1
        threshold_total += threshold
        net_total += net
        age_total += age

        bucket = by_setup.setdefault(
            setup,
            {
                "fires": 0,
                "_thresh_sum": 0.0,
                "_net_sum": 0.0,
                "_age_sum": 0.0,
                "_atr_pct_sum": 0.0,
                "_atr_pct_count": 0,
                "by_source": defaultdict(int),
            },
        )
        bucket["fires"] += 1
        bucket["_thresh_sum"] += threshold
        bucket["_net_sum"] += net
        bucket["_age_sum"] += age
        bucket["by_source"][source] += 1
        # ATR% is implicit in (threshold, source).  When source != "static"
        # the resolver ran threshold = max(floor, atr_mult × atr_pct), so
        # we can recover atr_pct from atr_last only.
        if atr_last is not None and atr_last > 0:
            # We don't have entry in the log line, but threshold lets us
            # back out atr_pct when source is "atr": threshold = atr_mult × atr_pct.
            # For "atr_floored", threshold = floor and the ATR was lower —
            # we can't recover atr_pct exactly from the log alone, so we
            # only count ATR% samples for "atr".
            pass

    if fires == 0:
        return {
            "total": 0,
            "by_setup": {},
            "by_source": {},
            "by_symbol": {},
            "avg_threshold": 0.0,
            "avg_net": 0.0,
        }

    # Finalise averages on per-setup buckets and strip private accumulators.
    finalised_by_setup: Dict[str, Dict[str, Any]] = {}
    for setup, raw in by_setup.items():
        n = raw["fires"]
        finalised_by_setup[setup] = {
            "fires": n,
            "avg_threshold": round(raw["_thresh_sum"] / n, 3),
            "avg_net": round(raw["_net_sum"] / n, 2),
            "avg_age_sec": round(raw["_age_sum"] / n, 1),
            "by_source": dict(raw["by_source"]),
        }

    return {
        "total": fires,
        "by_setup": finalised_by_setup,
        "by_source": dict(by_source),
        "by_symbol": dict(by_symbol),
        "avg_threshold": round(threshold_total / fires, 3),
        "avg_net": round(net_total / fires, 2),
        "avg_age_sec": round(age_total / fires, 1),
    }


def parse_free_channel_posts_from_logs(log_text: str) -> Dict[str, Any]:
    """Parse `free_channel_post source=... severity=...` markers.

    Emitted by:
      * ``MacroWatchdog._broadcast`` (sources: ``macro_alert``, ``btc_move``,
        ``regime_shift``, ``fear_greed``, ``macro_news``)
      * ``TradeMonitor._post_signal_closed`` (source: ``signal_close``)
      * ``SignalRouter.publish_highlight`` (source: ``signal_highlight``)

    Returns ``{"by_source": {source: count}, "by_severity": {severity: count},
    "by_source_severity": {source: {severity: count}}, "total": int}``.

    Empty when log_text is empty or contains no matching markers — caller
    should treat zero counts as "free-channel posts have not fired in this
    window," which on a freshly-shipped instrumentation rollout is the
    expected baseline.
    """
    by_source: Dict[str, int] = defaultdict(int)
    by_severity: Dict[str, int] = defaultdict(int)
    by_source_severity: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    total = 0
    if not log_text:
        return {
            "by_source": {},
            "by_severity": {},
            "by_source_severity": {},
            "total": 0,
        }
    for line in log_text.splitlines():
        if _FREE_CHANNEL_POST_MARKER not in line:
            continue
        m = _FREE_CHANNEL_POST_RE.search(line)
        if m is None:
            continue
        source = m.group("source")
        severity = m.group("severity")
        by_source[source] += 1
        by_severity[severity] += 1
        by_source_severity[source][severity] += 1
        total += 1
    return {
        "by_source": dict(by_source),
        "by_severity": dict(by_severity),
        "by_source_severity": {k: dict(v) for k, v in by_source_severity.items()},
        "total": total,
    }


def summarize_invalidation_audit(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate invalidation_records.json into a setup × kill_reason histogram.

    Returns ``{by_setup, by_reason, totals, stale}`` where each leaf cell counts
    classifications (PROTECTIVE / PREMATURE / NEUTRAL / INSUFFICIENT_DATA) and
    derives a "value impact" estimate.

    The point of this section is to answer "is the invalidation gate net-helping
    or net-hurting?" with the only honest unit: signal-by-signal counterfactuals
    on what the post-kill price action did.
    """
    by_setup: Dict[str, Dict[str, int]] = {}
    by_reason: Dict[str, Dict[str, int]] = {}
    totals: Dict[str, int] = {
        "PROTECTIVE": 0,
        "PREMATURE": 0,
        "NEUTRAL": 0,
        "INSUFFICIENT_DATA": 0,
    }
    stale = 0  # records older than the eval window but still without a classification
    if not records:
        return {"by_setup": {}, "by_reason": {}, "totals": totals, "stale": 0}

    for r in records:
        if not isinstance(r, dict):
            continue
        label = r.get("classification")
        if label is None:
            stale += 1
            continue
        setup = str(r.get("setup_class") or "UNKNOWN")
        reason_family = str(r.get("kill_reason_family") or "other")
        for bucket, key in ((by_setup, setup), (by_reason, reason_family)):
            inner = bucket.setdefault(key, {
                "PROTECTIVE": 0,
                "PREMATURE": 0,
                "NEUTRAL": 0,
                "INSUFFICIENT_DATA": 0,
            })
            inner[label] = inner.get(label, 0) + 1
        totals[label] = totals.get(label, 0) + 1

    return {
        "by_setup": by_setup,
        "by_reason": by_reason,
        "totals": totals,
        "stale": stale,
    }


def stage_totals_by_setup(funnel_counters: Dict[str, int], channel: str) -> Dict[str, Dict[str, int]]:
    by_setup: Dict[str, Dict[str, int]] = {}
    for key, value in funnel_counters.items():
        parsed_key = _parse_funnel_key_for_channel(str(key), channel)
        if parsed_key is None:
            continue
        stage, family, setup = parsed_key
        bucket = by_setup.setdefault(setup, {"family": family})
        bucket[stage] = bucket.get(stage, 0) + int(value or 0)
    return by_setup


def classify_path(path_metrics: Dict[str, int], quality_metrics: Optional[Dict[str, Any]] = None) -> str:
    attempts = int(path_metrics.get("evaluator_attempted", 0))
    generated = int(path_metrics.get("evaluator_generated", 0)) + int(path_metrics.get("generated", 0))
    gated = int(path_metrics.get("gated", 0))
    emitted = int(path_metrics.get("emitted", 0))

    if attempts < 3 and emitted < 2:
        return "low-sample"
    if attempts > 0 and generated <= 0:
        return "non-generating"
    if generated > 0 and emitted <= 0 and gated > 0:
        return "generated-but-gated"
    if emitted <= 0:
        return "low-sample"

    quality_metrics = quality_metrics or {}
    closed = int(quality_metrics.get("closed", 0))
    if closed < 3:
        return "low-sample"
    win_rate = float(quality_metrics.get("win_rate", 0.0))
    sl_rate = float(quality_metrics.get("sl_rate", 0.0))
    if win_rate >= 45.0 and sl_rate <= 45.0:
        return "active-healthy"
    return "active-low-quality"


def build_lifecycle_summary(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    create_to_breach = [r.get("create_to_first_breach_sec") for r in records]
    create_to_terminal = [r.get("create_to_terminal_sec") for r in records]

    fast_thresholds = [30, 60, 120, 180]
    fast_buckets = {}
    valid_breach = [float(v) for v in create_to_breach if isinstance(v, (int, float)) and v >= 0]
    for threshold in fast_thresholds:
        count = sum(1 for value in valid_breach if value <= threshold)
        fast_buckets[f"under_{threshold}s"] = {"count": count, "pct": _pct(count, len(valid_breach))}

    near_three_min = [
        float(v)
        for v in create_to_terminal
        if isinstance(v, (int, float)) and 150 <= float(v) <= 240
    ]
    valid_terminal = [float(v) for v in create_to_terminal if isinstance(v, (int, float)) and v >= 0]

    return {
        "median_create_to_dispatch_sec": _median(r.get("create_to_dispatch_sec") for r in records),
        "median_create_to_first_breach_sec": _median(create_to_breach),
        "median_create_to_terminal_sec": _median(create_to_terminal),
        "median_first_breach_to_terminal_sec": _median(
            r.get("first_breach_to_terminal_sec") for r in records
        ),
        "fast_failure_buckets": fast_buckets,
        "terminal_close_around_3m": {
            "count": len(near_three_min),
            "pct": _pct(len(near_three_min), len(valid_terminal)),
        },
    }


def build_quality_by_setup(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        setup = str(record.get("setup_class") or "UNKNOWN")
        grouped[setup].append(record)

    result: Dict[str, Dict[str, Any]] = {}
    for setup, setup_records in grouped.items():
        labels = [_outcome_label(record) for record in setup_records]
        closed = len(setup_records)
        win_count = sum(1 for label in labels if label in TP_LABELS)
        sl_count = sum(1 for label in labels if label in SL_LABELS)
        pnl_values = [
            float(record.get("pnl_pct"))
            for record in setup_records
            if isinstance(record.get("pnl_pct"), (int, float))
        ]
        result[setup] = {
            "emitted": closed,
            "closed": closed,
            "win_rate": _pct(win_count, closed),
            "tp_rate": _pct(win_count, closed),
            "sl_rate": _pct(sl_count, closed),
            "average_pnl_pct": round(sum(pnl_values) / len(pnl_values), 4) if pnl_values else None,
            "median_first_breach_sec": _median(
                record.get("create_to_first_breach_sec") for record in setup_records
            ),
            "median_terminal_duration_sec": _median(
                record.get("create_to_terminal_sec") for record in setup_records
            ),
        }
    return result


def summarize_runtime_health(
    runtime_health: Dict[str, Any],
    heartbeat_text: str,
    records: List[Dict[str, Any]],
    now_ts: float,
) -> Dict[str, Any]:
    heartbeat_age_sec: Optional[int] = None
    heartbeat_warning = False
    match = re.search(r"Heartbeat age:\s*(\d+)s", heartbeat_text or "")
    if match:
        heartbeat_age_sec = int(match.group(1))
        heartbeat_warning = heartbeat_age_sec > 120

    latest_record_ts = max(
        [float(r.get("timestamp")) for r in records if isinstance(r.get("timestamp"), (int, float))],
        default=None,
    )
    latest_record_age_sec = int(now_ts - latest_record_ts) if latest_record_ts else None
    fresh_records = latest_record_age_sec is not None and latest_record_age_sec <= 2 * 3600

    running = bool(runtime_health.get("running", False))
    health_status = str(runtime_health.get("health", "unknown"))

    overall = "healthy"
    if not running or health_status == "unhealthy":
        overall = "unhealthy"
    elif heartbeat_warning or not fresh_records:
        overall = "stale"

    return {
        "overall": overall,
        "running": running,
        "status": runtime_health.get("status", "unknown"),
        "health": health_status,
        "heartbeat_age_sec": heartbeat_age_sec,
        "heartbeat_warning": heartbeat_warning,
        "latest_record_age_sec": latest_record_age_sec,
        "records_fresh": fresh_records,
    }


def compare_windows(
    current_path_summary: Dict[str, Dict[str, int]],
    previous_path_summary: Dict[str, Dict[str, int]],
    current_lifecycle: Dict[str, Any],
    previous_lifecycle: Dict[str, Any],
    current_quality: Dict[str, Dict[str, Any]],
    previous_quality: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    def stage_total(summary: Dict[str, Dict[str, int]], stage: str) -> int:
        return sum(int(metrics.get(stage, 0)) for metrics in summary.values())

    quality_changes: Dict[str, Dict[str, Any]] = {}
    for setup in sorted(set(current_quality) | set(previous_quality)):
        curr = current_quality.get(setup, {})
        prev = previous_quality.get(setup, {})
        curr_closed = int(curr.get("closed", 0))
        prev_closed = int(prev.get("closed", 0))
        if curr_closed < 3 and prev_closed < 3:
            continue
        quality_changes[setup] = {
            "current_win_rate": curr.get("win_rate"),
            "previous_win_rate": prev.get("win_rate"),
            "win_rate_delta": round(float(curr.get("win_rate", 0.0)) - float(prev.get("win_rate", 0.0)), 2),
            "current_avg_pnl": curr.get("average_pnl_pct"),
            "previous_avg_pnl": prev.get("average_pnl_pct"),
            "avg_pnl_delta": round(
                float(curr.get("average_pnl_pct") or 0.0) - float(prev.get("average_pnl_pct") or 0.0),
                4,
            ),
        }

    current_fast = int(current_lifecycle.get("fast_failure_buckets", {}).get("under_180s", {}).get("count", 0))
    previous_fast = int(previous_lifecycle.get("fast_failure_buckets", {}).get("under_180s", {}).get("count", 0))

    return {
        "emissions_delta": stage_total(current_path_summary, "emitted") - stage_total(previous_path_summary, "emitted"),
        "gating_delta": stage_total(current_path_summary, "gated") - stage_total(previous_path_summary, "gated"),
        "no_generation_delta": stage_total(current_path_summary, "evaluator_no_signal")
        - stage_total(previous_path_summary, "evaluator_no_signal"),
        "fast_failures_delta": current_fast - previous_fast,
        "quality_changes": quality_changes,
        "post_correction_window_delta": {
            setup: {
                "emitted_delta": int(current_path_summary.get(setup, {}).get("emitted", 0))
                - int(previous_path_summary.get(setup, {}).get("emitted", 0)),
                "win_rate_delta": round(
                    float(current_quality.get(setup, {}).get("win_rate", 0.0))
                    - float(previous_quality.get(setup, {}).get("win_rate", 0.0)),
                    2,
                ),
                "sl_rate_delta": round(
                    float(current_quality.get(setup, {}).get("sl_rate", 0.0))
                    - float(previous_quality.get(setup, {}).get("sl_rate", 0.0)),
                    2,
                ),
                "median_first_breach_delta_sec": round(
                    float(current_quality.get(setup, {}).get("median_first_breach_sec") or 0.0)
                    - float(previous_quality.get(setup, {}).get("median_first_breach_sec") or 0.0),
                    2,
                ),
                "median_terminal_delta_sec": round(
                    float(current_quality.get(setup, {}).get("median_terminal_duration_sec") or 0.0)
                    - float(previous_quality.get(setup, {}).get("median_terminal_duration_sec") or 0.0),
                    2,
                ),
                "geometry_preserved_delta": int(
                    current_path_summary.get(setup, {}).get("geometry:final_live:preserved", 0)
                )
                - int(previous_path_summary.get(setup, {}).get("geometry:final_live:preserved", 0)),
                "geometry_changed_delta": int(
                    current_path_summary.get(setup, {}).get("geometry:final_live:changed", 0)
                )
                - int(previous_path_summary.get(setup, {}).get("geometry:final_live:changed", 0)),
                "geometry_rejected_delta": int(
                    current_path_summary.get(setup, {}).get("geometry:final_live:rejected", 0)
                )
                - int(previous_path_summary.get(setup, {}).get("geometry:final_live:rejected", 0)),
            }
            for setup in _POST_CORRECTION_TARGET_SETUPS
        },
    }


def build_snapshot(
    *,
    channel: str,
    lookback_hours: int,
    compare_previous_window: bool,
    include_raw_json: bool,
    symbol_filter: str,
    setup_filter: str,
    runtime_health: Dict[str, Any],
    heartbeat_text: str,
    records: List[Dict[str, Any]],
    current_funnel: Dict[str, int],
    previous_funnel: Dict[str, int],
    current_channel_funnel: Optional[Dict[str, int]] = None,
    previous_channel_funnel: Optional[Dict[str, int]] = None,
    regime_distribution: Optional[Dict[str, int]] = None,
    quiet_scalp_block: Optional[Dict[str, Any]] = None,
    confidence_gate_decisions: Optional[Dict[str, Any]] = None,
    confidence_gate_components: Optional[Dict[str, Any]] = None,
    invalidation_audit: Optional[Dict[str, Any]] = None,
    log_parse_diagnostics: Optional[Dict[str, int]] = None,
    free_channel_posts: Optional[Dict[str, Any]] = None,
    pre_tp_fires: Optional[Dict[str, Any]] = None,
    now_ts: Optional[float] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    now_ts = now_ts or time.time()
    lookback_sec = lookback_hours * 3600
    current_start = now_ts - lookback_sec
    previous_start = current_start - lookback_sec

    symbol_filters = _parse_csv_filter(symbol_filter)
    setup_filters = _parse_csv_filter(setup_filter)

    def _record_in_scope(record: Dict[str, Any]) -> bool:
        if str(record.get("channel") or "") != channel:
            return False
        if not _matches_filter(str(record.get("symbol") or ""), symbol_filters, substring=False):
            return False
        if not _matches_filter(str(record.get("setup_class") or ""), setup_filters, substring=True):
            return False
        return True

    scoped = [record for record in records if _record_in_scope(record)]

    def _in_window(record: Dict[str, Any], start_ts: float, end_ts: float) -> bool:
        ts = record.get("timestamp")
        if not isinstance(ts, (int, float)):
            return False
        return start_ts <= float(ts) < end_ts

    current_records = [record for record in scoped if _in_window(record, current_start, now_ts + 1)]
    previous_records = [record for record in scoped if _in_window(record, previous_start, current_start)]

    current_paths = stage_totals_by_setup(current_funnel, channel)
    previous_paths = stage_totals_by_setup(previous_funnel, channel)
    current_channel_funnel = current_channel_funnel or {}
    previous_channel_funnel = previous_channel_funnel or {}

    current_quality = build_quality_by_setup(current_records)
    previous_quality = build_quality_by_setup(previous_records)

    path_funnel_truth = {}
    for setup, metrics in current_paths.items():
        quality = current_quality.get(setup, {})
        rejected_reasons = {
            stage.replace("geometry:final_live:rejected_reason:", ""): int(count or 0)
            for stage, count in metrics.items()
            if stage.startswith("geometry:final_live:rejected_reason:")
        }
        no_signal_reasons = {
            stage.replace("evaluator_no_signal_reason:", ""): int(count or 0)
            for stage, count in metrics.items()
            if stage.startswith("evaluator_no_signal_reason:")
        }
        dependency_missing_reasons = {
            stage.replace("dependency_missing:", ""): int(count or 0)
            for stage, count in metrics.items()
            if stage.startswith("dependency_missing:")
        }
        generated = int(metrics.get("evaluator_generated", 0)) + int(metrics.get("generated", 0))
        dependency_missing_total = sum(int(v or 0) for v in dependency_missing_reasons.values())
        if int(metrics.get("evaluator_attempted", 0)) > 0 and generated <= 0 and dependency_missing_total > 0:
            classification = "dependency-missing"
        else:
            classification = classify_path(metrics, quality)
        path_funnel_truth[setup] = {
            "attempts": int(metrics.get("evaluator_attempted", 0)),
            "no_signal": int(metrics.get("evaluator_no_signal", 0)),
            "generated": generated,
            "scanner_preparation": int(metrics.get("scanner_preparation", 0)),
            "gated": int(metrics.get("gated", 0)),
            "emitted": int(metrics.get("emitted", 0)),
            "geometry_final_preserved": int(metrics.get("geometry:final_live:preserved", 0)),
            "geometry_final_changed": int(metrics.get("geometry:final_live:changed", 0)),
            "geometry_final_rejected": int(metrics.get("geometry:final_live:rejected", 0)),
            "geometry_rejected_reasons": rejected_reasons,
            "no_signal_reasons": no_signal_reasons,
            "dependency_missing_reasons": dependency_missing_reasons,
            "dependency_missing_total": dependency_missing_total,
            "classification": classification,
        }

    lifecycle_summary = build_lifecycle_summary(current_records)
    runtime_summary = summarize_runtime_health(runtime_health, heartbeat_text, current_records, now_ts)

    comparison = {
        "enabled": bool(compare_previous_window),
    }
    if compare_previous_window:
        comparison.update(
            compare_windows(
                current_paths,
                previous_paths,
                lifecycle_summary,
                build_lifecycle_summary(previous_records),
                current_quality,
                previous_quality,
            )
        )

    healthiest = [
        setup
        for setup, metrics in sorted(
            path_funnel_truth.items(),
            key=lambda item: item[1].get("emitted", 0),
            reverse=True,
        )
        if metrics.get("classification") == "active-healthy"
    ]
    degraded = [
        setup
        for setup, metrics in sorted(
            path_funnel_truth.items(),
            key=lambda item: item[1].get("gated", 0),
            reverse=True,
        )
        if metrics.get("classification") in {"non-generating", "generated-but-gated", "active-low-quality"}
    ]

    likely_bottlenecks = [
        setup
        for setup, metrics in sorted(
            path_funnel_truth.items(),
            key=lambda item: (
                item[1].get("gated", 0),
                item[1].get("generated", 0) - item[1].get("emitted", 0),
            ),
            reverse=True,
        )
        if metrics.get("generated", 0) > 0 and metrics.get("emitted", 0) == 0
    ]

    recommended_target = None
    if degraded:
        recommended_target = degraded[0]
    elif likely_bottlenecks:
        recommended_target = likely_bottlenecks[0]
    elif healthiest:
        recommended_target = healthiest[0]

    dependency_readiness: Dict[str, Dict[str, Any]] = {}
    for key, count in current_channel_funnel.items():
        if key.startswith(f"dependency_presence:{channel}:"):
            _, _, dep, state = key.split(":", 3)
            dep_bucket = dependency_readiness.setdefault(
                dep, {"presence": {}, "states": {}, "buckets": {}, "sources": {}, "quality": {}}
            )
            dep_bucket["presence"][state] = dep_bucket["presence"].get(state, 0) + int(count or 0)
        elif key.startswith(f"dependency_state:{channel}:"):
            _, _, dep, state = key.split(":", 3)
            dep_bucket = dependency_readiness.setdefault(
                dep, {"presence": {}, "states": {}, "buckets": {}, "sources": {}, "quality": {}}
            )
            dep_bucket["states"][state] = dep_bucket["states"].get(state, 0) + int(count or 0)
        elif key.startswith(f"dependency_bucket:{channel}:"):
            _, _, dep, bucket = key.split(":", 3)
            dep_bucket = dependency_readiness.setdefault(
                dep, {"presence": {}, "states": {}, "buckets": {}, "sources": {}, "quality": {}}
            )
            dep_bucket["buckets"][bucket] = dep_bucket["buckets"].get(bucket, 0) + int(count or 0)
        elif key.startswith(f"dependency_source:{channel}:"):
            _, _, dep, source = key.split(":", 3)
            dep_bucket = dependency_readiness.setdefault(
                dep, {"presence": {}, "states": {}, "buckets": {}, "sources": {}, "quality": {}}
            )
            dep_bucket["sources"][source] = dep_bucket["sources"].get(source, 0) + int(count or 0)
        elif key.startswith(f"dependency_quality:{channel}:"):
            _, _, dep, quality = key.split(":", 3)
            dep_bucket = dependency_readiness.setdefault(
                dep, {"presence": {}, "states": {}, "buckets": {}, "sources": {}, "quality": {}}
            )
            dep_bucket["quality"][quality] = dep_bucket["quality"].get(quality, 0) + int(count or 0)

    snapshot = {
        "generated_at": int(now_ts),
        "channel": channel,
        "lookback_hours": lookback_hours,
        "filters": {
            "symbol_filter": symbol_filter or "",
            "setup_filter": setup_filter or "",
        },
        "executive_summary": {
            "overall_health": runtime_summary["overall"],
            "top_anomalies": degraded[:3],
            "top_promising_paths": healthiest[:3],
            "recommended_next_investigation_target": recommended_target,
        },
        "runtime_health": runtime_summary,
        "path_funnel_truth": path_funnel_truth,
        "dependency_readiness": dependency_readiness,
        "lifecycle_truth": lifecycle_summary,
        "quality_by_setup": current_quality,
        "regime_distribution": regime_distribution or {},
        "quiet_scalp_block": quiet_scalp_block or {},
        "confidence_gate_decisions": confidence_gate_decisions or {},
        "confidence_gate_components": confidence_gate_components or {},
        "invalidation_audit": invalidation_audit or {},
        "log_parse_diagnostics": log_parse_diagnostics or {},
        "free_channel_posts": free_channel_posts or {},
        "pre_tp_fires": pre_tp_fires or {},
        "recommended_operator_focus": {
            "most_suspicious_degradation": degraded[0] if degraded else None,
            "most_promising_healthy_path": healthiest[0] if healthiest else None,
            "most_likely_bottleneck": likely_bottlenecks[0] if likely_bottlenecks else None,
            "suggested_next_investigation_target": recommended_target,
        },
        "post_correction_focus": {
            setup: {
                "attempts": int(path_funnel_truth.get(setup, {}).get("attempts", 0)),
                "generated": int(path_funnel_truth.get(setup, {}).get("generated", 0)),
                "emitted": int(path_funnel_truth.get(setup, {}).get("emitted", 0)),
                "gated": int(path_funnel_truth.get(setup, {}).get("gated", 0)),
                "classification": path_funnel_truth.get(setup, {}).get("classification", "low-sample"),
                "win_rate": float(current_quality.get(setup, {}).get("win_rate", 0.0)),
                "sl_rate": float(current_quality.get(setup, {}).get("sl_rate", 0.0)),
                "tp_rate": float(current_quality.get(setup, {}).get("tp_rate", 0.0)),
                "average_pnl_pct": current_quality.get(setup, {}).get("average_pnl_pct"),
                "median_first_breach_sec": current_quality.get(setup, {}).get("median_first_breach_sec"),
                "median_terminal_duration_sec": current_quality.get(setup, {}).get("median_terminal_duration_sec"),
                "geometry_final_preserved": int(path_funnel_truth.get(setup, {}).get("geometry_final_preserved", 0)),
                "geometry_final_changed": int(path_funnel_truth.get(setup, {}).get("geometry_final_changed", 0)),
                "geometry_final_rejected": int(path_funnel_truth.get(setup, {}).get("geometry_final_rejected", 0)),
                "geometry_rejected_reasons": path_funnel_truth.get(setup, {}).get(
                    "geometry_rejected_reasons", {}
                ),
            }
            for setup in _POST_CORRECTION_TARGET_SETUPS
        },
    }

    if include_raw_json:
        snapshot["raw_extracts"] = {
            "record_count_scoped": len(scoped),
            "record_count_current_window": len(current_records),
            "record_count_previous_window": len(previous_records),
            "current_path_funnel_counters": current_funnel,
            "previous_path_funnel_counters": previous_funnel,
            "current_channel_funnel_counters": current_channel_funnel,
            "previous_channel_funnel_counters": previous_channel_funnel,
        }

    return snapshot, comparison


def format_truth_report_markdown(snapshot: Dict[str, Any], comparison: Dict[str, Any]) -> str:
    executive = snapshot.get("executive_summary", {})
    runtime = snapshot.get("runtime_health", {})
    lifecycle = snapshot.get("lifecycle_truth", {})
    focus = snapshot.get("recommended_operator_focus", {})

    lines = [
        "# Runtime Truth Report",
        "",
        "## Executive summary",
        f"- Overall health/freshness: **{executive.get('overall_health', 'unknown')}**",
        f"- Top anomalies/concerns: {', '.join(executive.get('top_anomalies', []) or ['none'])}",
        f"- Top promising signals/paths: {', '.join(executive.get('top_promising_paths', []) or ['none'])}",
        f"- Recommended next investigation target: **{executive.get('recommended_next_investigation_target') or 'none'}**",
        "",
        "## Runtime health",
        f"- Engine running: `{runtime.get('running')}` (status={runtime.get('status')}, health={runtime.get('health')})",
        f"- Heartbeat age: `{runtime.get('heartbeat_age_sec')}` sec (warning={runtime.get('heartbeat_warning')})",
        f"- Latest performance record age: `{runtime.get('latest_record_age_sec')}` sec",
        "",
        "## Path funnel truth",
        "| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]

    path_truth = snapshot.get("path_funnel_truth", {})
    for setup, metrics in sorted(path_truth.items()):
        top_reason = "none"
        _reasons = metrics.get("no_signal_reasons", {}) or {}
        _positive_reasons = {k: int(v or 0) for k, v in _reasons.items() if int(v or 0) > 0}
        if _positive_reasons:
            top_reason = max(_positive_reasons.items(), key=lambda item: item[1])[0]
        lines.append(
            "| {setup} | {attempts} | {no_signal} | {generated} | {scanner_preparation} | {gated} | {emitted} | {classification} ({top_reason}) |".format(
                setup=setup,
                attempts=metrics.get("attempts", 0),
                no_signal=metrics.get("no_signal", 0),
                generated=metrics.get("generated", 0),
                scanner_preparation=metrics.get("scanner_preparation", 0),
                gated=metrics.get("gated", 0),
                emitted=metrics.get("emitted", 0),
                classification=metrics.get("classification", "unknown"),
                top_reason=top_reason,
            )
        )

    lines.extend(["", "## Evaluator no-signal reasons"])
    any_reasons_rendered = False
    for setup, metrics in sorted(path_truth.items()):
        reasons = metrics.get("no_signal_reasons", {}) or {}
        positive = {k: int(v or 0) for k, v in reasons.items() if int(v or 0) > 0}
        if not positive:
            continue
        any_reasons_rendered = True
        sorted_reasons = sorted(positive.items(), key=lambda item: item[1], reverse=True)
        total = sum(positive.values())
        breakdown = ", ".join(f"{k}={v}" for k, v in sorted_reasons)
        lines.append(f"- **{setup}** (total={total}): {breakdown}")
    if not any_reasons_rendered:
        lines.append("- _no reject-reason data parsed from logs in this window — see Log parse diagnostics below_")

    # ── Regime distribution (Tier-1 monitor upgrade) ──────────────────
    regime_dist = snapshot.get("regime_distribution", {}) or {}
    lines.extend(["", "## Regime distribution"])
    if regime_dist:
        total = sum(regime_dist.values()) or 1
        lines.append("| Regime | Count | % of cycles |")
        lines.append("|---|---:|---:|")
        for regime, count in sorted(regime_dist.items(), key=lambda kv: -kv[1]):
            pct = 100.0 * count / total
            lines.append(f"| {regime} | {count} | {pct:.1f}% |")
    else:
        lines.append(
            "- _no regime data parsed — engine may need redeploy to start emitting "
            "`Regime distribution (last 100 cycles): ...` log lines_"
        )

    # ── QUIET_SCALP_BLOCK gate (Tier-1 monitor upgrade) ───────────────
    qsb = snapshot.get("quiet_scalp_block", {}) or {}
    lines.extend(["", "## QUIET_SCALP_BLOCK gate"])
    if qsb.get("total", 0) > 0:
        lines.append(f"- Total blocks in window: **{qsb['total']}**")
        lines.append(
            f"- Average confidence gap to threshold: **{qsb.get('average_gap_to_min', 0.0):.2f}** "
            f"(samples={qsb.get('samples', 0)}) — small gap means candidates are *close* to "
            f"clearing the gate."
        )
        by_symbol = qsb.get("by_symbol", {}) or {}
        if by_symbol:
            top = ", ".join(f"{s}={c}" for s, c in list(by_symbol.items())[:10])
            lines.append(f"- Top blocked symbols: {top}")
    else:
        lines.append("- _no QUIET_SCALP_BLOCK events in window_")

    # ── Confidence gate decisions (Tier-1 monitor upgrade) ────────────
    conf_gate = snapshot.get("confidence_gate_decisions", {}) or {}
    lines.extend(["", "## Confidence gate decisions"])
    if conf_gate:
        lines.append("| Setup | Decision | Reason | Count |")
        lines.append("|---|---|---|---:|")
        for setup in sorted(conf_gate.keys()):
            for decision in sorted(conf_gate[setup].keys()):
                for reason, count in sorted(
                    conf_gate[setup][decision].items(), key=lambda kv: -kv[1]
                ):
                    lines.append(f"| {setup} | {decision} | {reason} | {count} |")
    else:
        lines.append("- _no confidence_gate decisions parsed in window_")

    # ── Confidence components histogram (Tier-2 monitor upgrade) ──────
    # The decisions table above told us "X candidates were filtered for
    # min_confidence" — this section answers "and *what* did those scores
    # actually look like, component by component."  Avg final vs threshold
    # gap localises the deficit; per-component averages tell us whether to
    # tune market/execution/risk/thesis weighting or the threshold itself.
    components = snapshot.get("confidence_gate_components", {}) or {}
    lines.extend(["", "## Confidence component breakdown"])
    if components:
        lines.append(
            "| Setup | Decision | Samples | Avg final | Avg threshold | Gap | "
            "Market | Execution | Risk | Thesis adj | Avg penalty |"
        )
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for setup in sorted(components.keys()):
            for decision in sorted(components[setup].keys()):
                m = components[setup][decision]
                comps = m.get("components", {})
                lines.append(
                    "| {setup} | {decision} | {samples} | {final:.2f} | {thr:.2f} | "
                    "{gap:.2f} | {mk:.2f} | {ex:.2f} | {rk:.2f} | {th:.2f} | {pen:.2f} |".format(
                        setup=setup,
                        decision=decision,
                        samples=m.get("samples", 0),
                        final=m.get("avg_final", 0.0),
                        thr=m.get("avg_threshold", 0.0),
                        gap=m.get("avg_gap_to_threshold", 0.0),
                        mk=comps.get("avg_market", 0.0),
                        ex=comps.get("avg_execution", 0.0),
                        rk=comps.get("avg_risk", 0.0),
                        th=comps.get("avg_thesis_adj", 0.0),
                        pen=m.get("avg_total_penalty", 0.0),
                    )
                )
    else:
        lines.append(
            "- _no confidence_gate component samples parsed in window — "
            "scoring telemetry may need a refresh after the next deploy_"
        )

    # ── Scoring engine breakdown (smc/regime/volume/indicators/patterns/mtf)
    # The legacy components above (market/execution/risk/thesis_adj) are from
    # the pre-engine scorer and don't sum to ``final``.  This table shows the
    # actual SignalScoringEngine dimensions whose sum *does* equal ``final``
    # (modulo penalties + adjustments + the 100-cap), which is the only way
    # to answer "where are the points coming from?" for a path like VSB.
    has_engine = any(
        decision_data.get("engine_components")
        for decisions in components.values()
        for decision_data in decisions.values()
    )
    lines.extend(["", "## Scoring engine breakdown (per-dimension contribution)"])
    if has_engine:
        lines.append(
            "_These are the actual ``SignalScoringEngine`` dimensions whose sum "
            "reconstructs ``final`` (before the 100-cap).  Surfacing this answers "
            "the question the legacy ``components(market/execution/risk/thesis_adj)`` "
            "table couldn't: which scoring dimension is dragging a path under threshold._"
        )
        lines.append(
            "| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | "
            "Indicators | Patterns | MTF | Thesis adj |"
        )
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for setup in sorted(components.keys()):
            for decision in sorted(components[setup].keys()):
                m = components[setup][decision]
                eng = m.get("engine_components")
                if not eng:
                    continue
                comps = m.get("components", {})
                lines.append(
                    "| {setup} | {decision} | {samples} | {final:.2f} | "
                    "{smc:.2f} | {rg:.2f} | {vol:.2f} | {ind:.2f} | {pat:.2f} | "
                    "{mtf:.2f} | {th:.2f} |".format(
                        setup=setup,
                        decision=decision,
                        samples=eng.get("samples", 0),
                        final=m.get("avg_final", 0.0),
                        smc=eng.get("avg_smc", 0.0),
                        rg=eng.get("avg_regime", 0.0),
                        vol=eng.get("avg_volume", 0.0),
                        ind=eng.get("avg_indicators", 0.0),
                        pat=eng.get("avg_patterns", 0.0),
                        mtf=eng.get("avg_mtf", 0.0),
                        th=comps.get("avg_thesis_adj", 0.0),
                    )
                )
    else:
        lines.append(
            "- _no engine-component data parsed in window — log line predates "
            "the engine-breakdown instrumentation, will populate after redeploy_"
        )

    # ── Soft-penalty per-type breakdown (LSR diagnosis instrumentation)
    # Splits the aggregate ``gate=`` penalty into the 6 sub-types so we
    # can attribute WHICH soft gate is dragging confidence down.  When
    # any single penalty dominates (e.g. avg vwap=8 across LSR filtered
    # candidates), that's the lever to investigate / tune.  Older log
    # lines without this group render the placeholder section.
    has_sp_breakdown = any(
        decision_data.get("soft_penalty_breakdown")
        for decisions in components.values()
        for decision_data in decisions.values()
    )
    lines.extend(["", "## Soft-penalty per-type breakdown"])
    if has_sp_breakdown:
        lines.append(
            "_Average per-type contribution to the aggregate ``gate`` penalty.  "
            "When one column dominates a setup's filtered row, that gate is "
            "the bottleneck — investigate its trigger conditions before tuning "
            "the overall threshold.  Sums to the aggregate ``gate`` penalty "
            "shown in the 'Confidence component breakdown' table above (modulo "
            "rounding).  VWAP = VWAP overextension; KZ = kill zone / session "
            "filter; OI = open-interest flip; SPOOF = order-book spoofing; "
            "VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._"
        )
        lines.append(
            "| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |"
        )
        lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for setup in sorted(components.keys()):
            for decision in sorted(components[setup].keys()):
                m = components[setup][decision]
                sp = m.get("soft_penalty_breakdown")
                if not sp:
                    continue
                sp_sum = (
                    sp.get("avg_vwap", 0.0)
                    + sp.get("avg_kz", 0.0)
                    + sp.get("avg_oi", 0.0)
                    + sp.get("avg_spoof", 0.0)
                    + sp.get("avg_vol_div", 0.0)
                    + sp.get("avg_cluster", 0.0)
                )
                lines.append(
                    "| {setup} | {decision} | {samples} | {final:.2f} | "
                    "{vwap:.2f} | {kz:.2f} | {oi:.2f} | {spoof:.2f} | {vd:.2f} | "
                    "{cl:.2f} | **{sm:.2f}** |".format(
                        setup=setup,
                        decision=decision,
                        samples=sp.get("samples", 0),
                        final=m.get("avg_final", 0.0),
                        vwap=sp.get("avg_vwap", 0.0),
                        kz=sp.get("avg_kz", 0.0),
                        oi=sp.get("avg_oi", 0.0),
                        spoof=sp.get("avg_spoof", 0.0),
                        vd=sp.get("avg_vol_div", 0.0),
                        cl=sp.get("avg_cluster", 0.0),
                        sm=sp_sum,
                    )
                )
    else:
        lines.append(
            "- _no soft-penalty per-type data parsed in window — log line "
            "predates the LSR diagnosis instrumentation, will populate "
            "after redeploy_"
        )

    # ── Invalidation Quality Audit ────────────────────────────────────
    audit = snapshot.get("invalidation_audit", {}) or {}
    lines.extend(["", "## Invalidation Quality Audit"])
    lines.append(
        "_Each trade-monitor kill is classified after a 30-min window: "
        "**PROTECTIVE** (price moved further against position by >0.3R — kill saved money), "
        "**PREMATURE** (price would have hit TP1 — kill destroyed value), "
        "**NEUTRAL** (price stayed within ±0.3R), "
        "**INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to "
        "'is invalidation net-helping or net-hurting?'_"
    )
    totals = audit.get("totals") or {}
    if any((totals.get(k, 0) for k in ("PROTECTIVE", "PREMATURE", "NEUTRAL"))):
        total_classified = sum(totals.get(k, 0) for k in ("PROTECTIVE", "PREMATURE", "NEUTRAL"))
        prot = totals.get("PROTECTIVE", 0)
        prem = totals.get("PREMATURE", 0)
        neut = totals.get("NEUTRAL", 0)
        insuf = totals.get("INSUFFICIENT_DATA", 0)
        prot_pct = (prot / total_classified * 100.0) if total_classified else 0.0
        prem_pct = (prem / total_classified * 100.0) if total_classified else 0.0
        lines.append(
            f"- Totals: PROTECTIVE={prot} ({prot_pct:.1f}%) | "
            f"PREMATURE={prem} ({prem_pct:.1f}%) | "
            f"NEUTRAL={neut} | INSUFFICIENT_DATA={insuf} | "
            f"stale (awaiting classification)={audit.get('stale', 0)}"
        )
        if prot > prem:
            lines.append(
                f"- **Net-helping** — invalidation saved on {prot - prem} more signals "
                "than it killed prematurely.  Tightening would lose that protection."
            )
        elif prem > prot:
            lines.append(
                f"- **Net-hurting** — invalidation killed {prem - prot} more signals "
                "prematurely than it saved.  Tightening or adding setup-specific exemptions "
                "is the right next move."
            )
        else:
            lines.append("- **Neutral** — invalidation is breakeven; tune carefully.")
        by_reason = audit.get("by_reason") or {}
        if by_reason:
            lines.append("")
            lines.append("| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |")
            lines.append("|---|---:|---:|---:|---:|")
            for reason in sorted(by_reason.keys()):
                row = by_reason[reason]
                lines.append(
                    f"| {reason} | {row.get('PROTECTIVE', 0)} | "
                    f"{row.get('PREMATURE', 0)} | {row.get('NEUTRAL', 0)} | "
                    f"{row.get('INSUFFICIENT_DATA', 0)} |"
                )
        by_setup = audit.get("by_setup") or {}
        if by_setup:
            lines.append("")
            lines.append("| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |")
            lines.append("|---|---:|---:|---:|---:|")
            for setup in sorted(by_setup.keys()):
                row = by_setup[setup]
                lines.append(
                    f"| {setup} | {row.get('PROTECTIVE', 0)} | "
                    f"{row.get('PREMATURE', 0)} | {row.get('NEUTRAL', 0)} | "
                    f"{row.get('INSUFFICIENT_DATA', 0)} |"
                )
    else:
        lines.append(
            "- _no classified invalidation records yet — engine needs to run for ~30 min "
            "after a kill before the classifier can label it_"
        )

    # ── Log parse diagnostics (Tier-1 monitor upgrade) ────────────────
    diag = snapshot.get("log_parse_diagnostics", {}) or {}
    lines.extend(["", "## Log parse diagnostics"])
    lines.append(
        "_If a section above is empty but the matching diagnostic count is also 0, "
        "the engine isn't emitting that log line in the window (cadence/retention) "
        "rather than the parser being broken._"
    )
    if diag:
        lines.append(f"- Total log lines in window: `{diag.get('total_lines', 0)}`")
        lines.append(f"- `Path funnel` emissions: `{diag.get('path_funnel', 0)}`")
        lines.append(f"- `Regime distribution` emissions: `{diag.get('regime_distribution', 0)}`")
        lines.append(f"- `QUIET_SCALP_BLOCK` events: `{diag.get('quiet_scalp_block', 0)}`")
        lines.append(f"- `confidence_gate` events: `{diag.get('confidence_gate', 0)}`")
        lines.append(f"- `free_channel_post` events: `{diag.get('free_channel_post', 0)}`")
        lines.append(f"- `pre_tp_fire` events: `{diag.get('pre_tp_fire', 0)}`")
    else:
        lines.append("- _no diagnostics available_")

    # ── Pre-TP grab fire stats (Phase A) ──────────────────────────────
    # Aggregates every successful pre-TP fire by setup × source.  Verifies
    # the ATR-adaptive resolver in production: are fires distributed across
    # the threshold sources (static / atr / atr_floored) consistent with the
    # per-pair ATR profile?  Are we banking the +1.3-4.3% net @ 10x we
    # designed for?  Zero counts when PRE_TP_ENABLED=false on the engine,
    # so this also doubles as the "is the flag actually on?" indicator.
    pretp = snapshot.get("pre_tp_fires", {}) or {}
    lines.extend(["", "## Pre-TP grab fire stats"])
    lines.append(
        "_Each row is a pre-TP fire — signal moved favourably by the resolved "
        "threshold within 30 min, in a non-trending regime, on a non-breakout setup.  "
        "Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` "
        "means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; "
        "``static`` means ATR was unavailable and the 0.35% fallback fired._"
    )
    pretp_total = int(pretp.get("total", 0))
    if pretp_total <= 0:
        lines.append(
            "- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the "
            "engine, or no signals matched all gates yet)_"
        )
    else:
        lines.append(f"- Total fires in window: **{pretp_total}**")
        lines.append(
            f"- Avg resolved threshold: **{pretp.get('avg_threshold', 0.0):.3f}%** "
            f"raw → avg net **{pretp.get('avg_net', 0.0):+.2f}%** @ 10x"
        )
        avg_age = pretp.get("avg_age_sec", 0.0)
        if avg_age:
            lines.append(f"- Avg time-to-fire from dispatch: **{avg_age:.0f}s**")

        by_source = pretp.get("by_source", {}) or {}
        if by_source:
            src_summary = ", ".join(
                f"{src}={cnt}"
                for src, cnt in sorted(
                    by_source.items(), key=lambda kv: (-int(kv[1]), str(kv[0]))
                )
            )
            lines.append(f"- By threshold source: {src_summary}")

        by_setup = pretp.get("by_setup", {}) or {}
        if by_setup:
            lines.append("")
            lines.append(
                "| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |"
            )
            lines.append("|---|---:|---:|---:|---:|---|")
            for setup in sorted(by_setup.keys(), key=lambda k: -int(by_setup[k]["fires"])):
                m = by_setup[setup]
                src_mix = ", ".join(
                    f"{s}={n}"
                    for s, n in sorted(
                        m.get("by_source", {}).items(),
                        key=lambda kv: (-int(kv[1]), str(kv[0])),
                    )
                )
                lines.append(
                    "| {setup} | {fires} | {th:.3f}% | {net:+.2f}% | {age:.0f} | {mix} |".format(
                        setup=setup,
                        fires=int(m.get("fires", 0)),
                        th=float(m.get("avg_threshold", 0.0)),
                        net=float(m.get("avg_net", 0.0)),
                        age=float(m.get("avg_age_sec", 0.0)),
                        mix=src_mix or "-",
                    )
                )

        by_symbol = pretp.get("by_symbol", {}) or {}
        if by_symbol:
            top_n = sorted(by_symbol.items(), key=lambda kv: -int(kv[1]))[:10]
            sym_summary = ", ".join(f"{s}={c}" for s, c in top_n)
            lines.append(f"- Top symbols: {sym_summary}")

    # ── Free-channel post attribution (Phase 1 / 2a / 2b / 5) ─────────
    fcp = snapshot.get("free_channel_posts", {}) or {}
    lines.extend(["", "## Free-channel post attribution"])
    lines.append(
        "_Counts every successful post to the free subscriber channel by source.  "
        "Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, "
        "Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing "
        "in production.  Zero counts on a freshly-shipped instrumentation rollout "
        "are the expected baseline._"
    )
    fcp_total = int(fcp.get("total", 0))
    if fcp_total <= 0:
        lines.append("- _no free-channel posts in this window_")
    else:
        lines.append(f"- Total posts in window: **{fcp_total}**")
        by_source = fcp.get("by_source", {}) or {}
        if by_source:
            lines.append("")
            lines.append("| Source | Count |")
            lines.append("|---|---:|")
            for source, count in sorted(
                by_source.items(), key=lambda kv: (-int(kv[1]), str(kv[0]))
            ):
                lines.append(f"| {source} | {int(count)} |")
        by_severity = fcp.get("by_severity", {}) or {}
        if by_severity:
            sev_summary = ", ".join(
                f"{sev}={cnt}"
                for sev, cnt in sorted(
                    by_severity.items(), key=lambda kv: (-int(kv[1]), str(kv[0]))
                )
            )
            lines.append("")
            lines.append(f"- By severity: {sev_summary}")

    lines.extend(["", "## Dependency readiness"])
    dependency_readiness = snapshot.get("dependency_readiness", {}) or {}
    for dep_name, dep_metrics in sorted(dependency_readiness.items()):
        presence = dep_metrics.get("presence", {})
        states = dep_metrics.get("states", {})
        buckets = dep_metrics.get("buckets", {})
        sources = dep_metrics.get("sources", {})
        quality = dep_metrics.get("quality", {})
        presence_text = ", ".join(f"{k}={v}" for k, v in sorted(presence.items())) or "none"
        state_text = ", ".join(f"{k}={v}" for k, v in sorted(states.items())) or "none"
        bucket_text = ", ".join(f"{k}={v}" for k, v in sorted(buckets.items())) or "none"
        source_text = ", ".join(f"{k}={v}" for k, v in sorted(sources.items())) or "none"
        quality_text = ", ".join(f"{k}={v}" for k, v in sorted(quality.items())) or "none"
        lines.append(
            f"- {dep_name}: presence[{presence_text}] state[{state_text}] buckets[{bucket_text}] "
            f"sources[{source_text}] quality[{quality_text}]"
        )

    lines.extend(
        [
            "",
            "## Lifecycle truth summary",
            f"- Median create→dispatch: `{lifecycle.get('median_create_to_dispatch_sec')}` sec",
            f"- Median create→first breach: `{lifecycle.get('median_create_to_first_breach_sec')}` sec",
            f"- Median create→terminal: `{lifecycle.get('median_create_to_terminal_sec')}` sec",
            f"- Median first breach→terminal: `{lifecycle.get('median_first_breach_to_terminal_sec')}` sec",
            f"- Fast-failure buckets: `{json.dumps(lifecycle.get('fast_failure_buckets', {}), sort_keys=True)}`",
            f"- ~3 minute terminal-close behavior: `{json.dumps(lifecycle.get('terminal_close_around_3m', {}), sort_keys=True)}`",
            "",
            "## Quality-by-path/setup summary",
            "| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )

    quality = snapshot.get("quality_by_setup", {})
    for setup, metrics in sorted(quality.items()):
        lines.append(
            "| {setup} | {emitted} | {closed} | {win_rate} | {sl_rate} | {tp_rate} | {avg_pnl} | {mfb} | {mtd} |".format(
                setup=setup,
                emitted=metrics.get("emitted", 0),
                closed=metrics.get("closed", 0),
                win_rate=metrics.get("win_rate", 0.0),
                sl_rate=metrics.get("sl_rate", 0.0),
                tp_rate=metrics.get("tp_rate", 0.0),
                avg_pnl=metrics.get("average_pnl_pct"),
                mfb=metrics.get("median_first_breach_sec"),
                mtd=metrics.get("median_terminal_duration_sec"),
            )
        )

    lines.extend(
        [
            "",
            "## Post-correction focus (target setups)",
            "| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for setup, metrics in snapshot.get("post_correction_focus", {}).items():
        lines.append(
            "| {setup} | {attempts} | {generated} | {emitted} | {gated} | {win_rate} | {sl_rate} | {mfb} | {mtd} | {gp} | {gc} | {gr} |".format(
                setup=setup,
                attempts=metrics.get("attempts", 0),
                generated=metrics.get("generated", 0),
                emitted=metrics.get("emitted", 0),
                gated=metrics.get("gated", 0),
                win_rate=metrics.get("win_rate", 0.0),
                sl_rate=metrics.get("sl_rate", 0.0),
                mfb=metrics.get("median_first_breach_sec"),
                mtd=metrics.get("median_terminal_duration_sec"),
                gp=metrics.get("geometry_final_preserved", 0),
                gc=metrics.get("geometry_final_changed", 0),
                gr=metrics.get("geometry_final_rejected", 0),
            )
        )
        if metrics.get("geometry_rejected_reasons"):
            lines.append(
                f"  - `{setup}` geometry rejected reasons: `{json.dumps(metrics.get('geometry_rejected_reasons', {}), sort_keys=True)}`"
            )

    lines.extend(["", "## Window-over-window comparison"])
    if comparison.get("enabled"):
        lines.extend(
            [
                f"- Path emissions Δ: `{comparison.get('emissions_delta')}`",
                f"- Gating Δ: `{comparison.get('gating_delta')}`",
                f"- No-generation Δ: `{comparison.get('no_generation_delta')}`",
                f"- Fast failures Δ: `{comparison.get('fast_failures_delta')}`",
                f"- Quality changes: `{json.dumps(comparison.get('quality_changes', {}), sort_keys=True)}`",
                f"- Post-correction setup deltas: `{json.dumps(comparison.get('post_correction_window_delta', {}), sort_keys=True)}`",
            ]
        )
    else:
        lines.append("- Disabled")

    lines.extend(
        [
            "",
            "## Recommended operator focus",
            f"- Most suspicious degradation: **{focus.get('most_suspicious_degradation') or 'none'}**",
            f"- Most promising healthy path: **{focus.get('most_promising_healthy_path') or 'none'}**",
            f"- Most likely bottleneck: **{focus.get('most_likely_bottleneck') or 'none'}**",
            f"- Suggested next investigation target: **{focus.get('suggested_next_investigation_target') or 'none'}**",
            "",
        ]
    )

    return "\n".join(lines)


def load_json_file(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default
