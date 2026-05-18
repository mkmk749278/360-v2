"""Invalidation Quality Audit — classify trade-monitor kills as protective/premature/neutral.

The trade-monitor invalidation gate (regime flip / momentum loss / EMA crossover)
fires on every closed signal that didn't hit TP or SL.  Without ground truth on
*what would have happened* if the signal hadn't been killed, every threshold-tuning
decision is opinion-driven.

This module writes a record per kill to ``data/invalidation_records.json``, then
periodically classifies each record by examining price 30 minutes after the kill:

* PROTECTIVE  – price moved further against the position by more than 0.3 × SL
                distance.  The kill saved real money.
* PREMATURE   – price would have hit TP1 within the post-kill window.  The kill
                destroyed real value.
* NEUTRAL     – price stayed within ±0.3 × SL distance.  The kill was a wash.
* INSUFFICIENT_DATA – not enough post-kill data yet (will reclassify later).

The runtime truth report renders a histogram per setup × kill_reason, surfacing
which invalidation triggers are systematically protective vs systematically
premature.  This data drives the invalidation-tuning decisions in the next phase.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.utils import get_logger

log = get_logger("invalidation_audit")


# Window after kill within which we evaluate "would TP1 have been hit?"
_POST_KILL_WINDOW_SEC: float = float(os.getenv("INVALIDATION_AUDIT_WINDOW_SEC", "1800"))

# Distance beyond entry (in fractions of SL distance) that defines PROTECTIVE.
# 0.3 means: if price moved 0.3 × SL_distance further against position, kill was
# protective.  Tight enough to avoid false-positive PROTECTIVE labels in chop.
_PROTECTIVE_THRESHOLD_R: float = float(os.getenv("INVALIDATION_AUDIT_PROTECTIVE_R", "0.3"))

# Path conventions match performance_tracker.py.
_DEFAULT_STORAGE_PATH: str = os.getenv(
    "INVALIDATION_AUDIT_PATH", "data/invalidation_records.json"
)


@dataclass
class InvalidationRecord:
    """A single trade-monitor invalidation event with post-kill classification."""

    signal_id: str
    symbol: str
    channel: str
    setup_class: str
    direction: str  # "LONG" or "SHORT"
    entry: float
    stop_loss: float
    tp1: float
    sl_distance: float
    kill_price: float
    kill_reason: str
    kill_reason_family: str  # "momentum_loss" | "regime_shift" | "ema_crossover" | "other"
    kill_timestamp: float
    pnl_pct_at_kill: float

    # Filled by classify_pending_records once the post-kill window has elapsed.
    classified_at: Optional[float] = None
    classification: Optional[str] = None  # PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT_DATA
    post_kill_price_max: Optional[float] = None
    post_kill_price_min: Optional[float] = None
    post_kill_price_final: Optional[float] = None


# ---------------------------------------------------------------------------
# Reason-family categorisation — keeps the histogram low-cardinality.
# ---------------------------------------------------------------------------


def categorise_kill_reason(reason: str) -> str:
    """Map a free-text invalidation reason to a low-cardinality family token.

    Examples:
        "momentum loss (|momentum|=0.000 < 0.1, 2 consecutive readings) ..."
            -> "momentum_loss"
        "regime shift to TRENDING_DOWN – LONG thesis no longer valid"
            -> "regime_shift"
        "EMA bearish crossover (EMA9 < EMA21) – LONG thesis invalidated"
            -> "ema_crossover"
        "trailing invalidation (MFE peak +0.42%, retraced 50%...) ..."
            -> "trailing_invalidation"   # OWNER_BRIEF B17 tight-mode kill
        "momentum against thesis (...) – signal thesis invalidated"
            -> "momentum_loss"   # direction-aware momentum-kill alias
    """
    text = (reason or "").lower()
    if "trailing invalidation" in text:
        return "trailing_invalidation"
    if "momentum loss" in text or "momentum against thesis" in text:
        return "momentum_loss"
    if "regime shift" in text:
        return "regime_shift"
    if "ema" in text and "crossover" in text:
        return "ema_crossover"
    return "other"


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


def _load_records(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    try:
        raw = path.read_text(encoding="utf-8")
        if not raw.strip():
            return []
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("Failed to load invalidation records from %s: %s", path, exc)
        return []


def _save_records(path: Path, records: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def record_invalidation(
    *,
    signal_id: str,
    symbol: str,
    channel: str,
    setup_class: str,
    direction: str,
    entry: float,
    stop_loss: float,
    tp1: float,
    kill_price: float,
    kill_reason: str,
    pnl_pct_at_kill: float,
    storage_path: Optional[str] = None,
) -> Optional[InvalidationRecord]:
    """Append a kill record to the audit file.  No-ops on partial inputs."""
    if entry <= 0 or stop_loss <= 0:
        return None
    sl_distance = abs(entry - stop_loss)
    if sl_distance <= 0:
        return None
    record = InvalidationRecord(
        signal_id=signal_id,
        symbol=symbol,
        channel=channel,
        setup_class=setup_class,
        direction=direction.upper(),
        entry=float(entry),
        stop_loss=float(stop_loss),
        tp1=float(tp1),
        sl_distance=float(sl_distance),
        kill_price=float(kill_price),
        kill_reason=kill_reason,
        kill_reason_family=categorise_kill_reason(kill_reason),
        kill_timestamp=time.time(),
        pnl_pct_at_kill=float(pnl_pct_at_kill),
    )
    path = Path(storage_path or _DEFAULT_STORAGE_PATH)
    try:
        records = _load_records(path)
        records.append(asdict(record))
        _save_records(path, records)
    except OSError as exc:
        log.warning("Failed to persist invalidation record for %s: %s", symbol, exc)
        return None
    return record


def classify_record(
    record: Dict[str, Any],
    post_kill_high: float,
    post_kill_low: float,
    post_kill_close: float,
    *,
    protective_threshold_r: float = _PROTECTIVE_THRESHOLD_R,
) -> str:
    """Return the classification label for a kill given post-kill price extremes.

    Pure function — easy to unit test independently.
    """
    direction = str(record.get("direction") or "").upper()
    entry = float(record.get("entry") or 0.0)
    tp1 = float(record.get("tp1") or 0.0)
    sl_distance = float(record.get("sl_distance") or 0.0)
    if entry <= 0 or sl_distance <= 0:
        return "INSUFFICIENT_DATA"

    protective_offset = sl_distance * protective_threshold_r

    if direction == "LONG":
        # PREMATURE: post-kill HIGH reached or exceeded TP1 (would have closed in profit)
        if tp1 > 0 and post_kill_high >= tp1:
            return "PREMATURE"
        # PROTECTIVE: post-kill LOW dropped further by > 0.3R (would have lost more)
        if post_kill_low <= entry - protective_offset:
            return "PROTECTIVE"
        return "NEUTRAL"
    else:  # SHORT
        if tp1 > 0 and post_kill_low <= tp1:
            return "PREMATURE"
        if post_kill_high >= entry + protective_offset:
            return "PROTECTIVE"
        return "NEUTRAL"


def classify_pending_records(
    *,
    fetch_ohlc_since: Callable[[str, float], Optional[Dict[str, List[float]]]],
    now_ts: Optional[float] = None,
    storage_path: Optional[str] = None,
    window_sec: float = _POST_KILL_WINDOW_SEC,
) -> Dict[str, int]:
    """Look at every unclassified record and try to classify it.

    Args:
        fetch_ohlc_since: callable(symbol, since_ts) -> {"high": [...], "low": [...],
            "close": [...]} returning OHLC arrays for the symbol since the given
            timestamp.  Returns None if data unavailable.
        now_ts: clock override for tests.
        storage_path: file path override for tests.
        window_sec: how long after kill to wait before classifying.

    Returns: counters dict {classification: count} for this run.
    """
    now_ts = now_ts if now_ts is not None else time.time()
    path = Path(storage_path or _DEFAULT_STORAGE_PATH)
    records = _load_records(path)
    if not records:
        return {}

    counters: Dict[str, int] = {}
    dirty = False
    for record in records:
        if record.get("classification") is not None:
            continue
        kill_ts = float(record.get("kill_timestamp") or 0.0)
        if kill_ts <= 0:
            record["classification"] = "INSUFFICIENT_DATA"
            record["classified_at"] = now_ts
            counters["INSUFFICIENT_DATA"] = counters.get("INSUFFICIENT_DATA", 0) + 1
            dirty = True
            continue
        if now_ts - kill_ts < window_sec:
            continue  # not yet
        symbol = str(record.get("symbol") or "")
        if not symbol:
            record["classification"] = "INSUFFICIENT_DATA"
            record["classified_at"] = now_ts
            counters["INSUFFICIENT_DATA"] = counters.get("INSUFFICIENT_DATA", 0) + 1
            dirty = True
            continue
        ohlc = fetch_ohlc_since(symbol, kill_ts)
        if not ohlc or not ohlc.get("high") or not ohlc.get("low"):
            record["classification"] = "INSUFFICIENT_DATA"
            record["classified_at"] = now_ts
            counters["INSUFFICIENT_DATA"] = counters.get("INSUFFICIENT_DATA", 0) + 1
            dirty = True
            continue
        high = max(ohlc["high"])
        low = min(ohlc["low"])
        close = ohlc.get("close", [])
        final = float(close[-1]) if close else 0.0
        label = classify_record(record, high, low, final)
        record["classification"] = label
        record["classified_at"] = now_ts
        record["post_kill_price_max"] = high
        record["post_kill_price_min"] = low
        record["post_kill_price_final"] = final
        counters[label] = counters.get(label, 0) + 1
        dirty = True

    if dirty:
        _save_records(path, records)
    return counters


def load_classified_records(
    storage_path: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return records that have been classified (for the truth-report parser)."""
    path = Path(storage_path or _DEFAULT_STORAGE_PATH)
    records = _load_records(path)
    return [r for r in records if r.get("classification") is not None]


# ---------------------------------------------------------------------------
# Per-rule ablation metrics — answer "which kill rules are net-bleeding?"
# ---------------------------------------------------------------------------
#
# The classifier above buckets every kill into PROTECTIVE / PREMATURE / NEUTRAL.
# To decide whether a rule should be DROPPED we need an EV estimate in R-units
# per kill, not just counts: a rule with 10 PROTECTIVE and 8 PREMATURE looks
# "net-helping" on counts but is net-hurting if each PREMATURE missed +1.8R
# while each PROTECTIVE saved only +0.4R.
#
# Counterfactual model per record (R-units of sl_distance):
#   * PREMATURE → counterfactual exit at TP1.  missed_R = R_to_tp1 - R_at_kill.
#   * PROTECTIVE → counterfactual exit at worst post-kill excursion, floored at
#                  full SL (-1R).  saved_R = R_at_kill - counterfactual_R.
#   * NEUTRAL    → no EV contribution (counterfactual ambiguous, ~0 by design).
#
# ev_per_kill_R = (saved_R_total - missed_R_total) / total_classified
# Recommendations are thresholded; see ``_ABLATION_*`` constants below.

# DROP when each kill on average destroys more than this much R.  Rationale:
# B17 capital-preservation doctrine values pre-TP+BE at ~-0.5%/10x margin and
# a clean TP1 at ~+1.3-4.3%/10x.  A rule that bleeds 0.2R/kill on average is
# silently giving back the partial-bank edge across the cohort.
_ABLATION_DROP_EV_THRESHOLD: float = -0.20
# KEEP when each kill on average preserves more than this much R.
_ABLATION_KEEP_EV_THRESHOLD: float = 0.10
# Minimum classified records per family before any recommendation lands —
# below this, surfaces as INSUFFICIENT_SAMPLE so we don't drop a rule on noise.
_ABLATION_MIN_SAMPLE_DEFAULT: int = 20


def _favorable_r(price: float, entry: float, sl_distance: float, direction: str) -> float:
    """Convert a raw price into R-units of favorable excursion from entry.

    LONG : (price - entry) / sl_distance.   SHORT : (entry - price) / sl_distance.
    Both yield positive R when ``price`` is on the favorable side of entry.
    Returns 0.0 on invalid inputs to keep the EV math defensive.
    """
    if sl_distance <= 0 or entry <= 0 or price <= 0:
        return 0.0
    if direction == "LONG":
        return (price - entry) / sl_distance
    return (entry - price) / sl_distance


def _record_value_delta_r(record: Dict[str, Any]) -> Optional[float]:
    """Return the R-unit value-delta of THIS kill vs its counterfactual.

    Positive = kill was net-good (saved R), negative = kill was net-bad (missed R).
    Returns None when inputs are insufficient (skip in aggregation).
    """
    label = str(record.get("classification") or "")
    if label not in ("PROTECTIVE", "PREMATURE", "NEUTRAL"):
        return None
    direction = str(record.get("direction") or "").upper()
    if direction not in ("LONG", "SHORT"):
        return None
    entry = float(record.get("entry") or 0.0)
    sl_distance = float(record.get("sl_distance") or 0.0)
    if entry <= 0 or sl_distance <= 0:
        return None
    kill_price = float(record.get("kill_price") or 0.0)
    tp1 = float(record.get("tp1") or 0.0)
    if kill_price <= 0:
        return None
    r_at_kill = _favorable_r(kill_price, entry, sl_distance, direction)
    if label == "PREMATURE":
        if tp1 <= 0:
            return None
        r_to_tp1 = _favorable_r(tp1, entry, sl_distance, direction)
        return -(r_to_tp1 - r_at_kill)  # negative: we missed this many R
    if label == "PROTECTIVE":
        # Worst excursion price = post_kill min (LONG) or max (SHORT).
        if direction == "LONG":
            worst_price = float(record.get("post_kill_price_min") or 0.0)
        else:
            worst_price = float(record.get("post_kill_price_max") or 0.0)
        if worst_price <= 0:
            return None
        worst_r = _favorable_r(worst_price, entry, sl_distance, direction)
        # Floor at -1R: SL would have fired before price went deeper.
        counterfactual_r = max(worst_r, -1.0)
        return r_at_kill - counterfactual_r  # positive: we saved this many R
    return 0.0  # NEUTRAL


def compute_rule_ablation_metrics(
    records: List[Dict[str, Any]],
    *,
    min_sample_per_family: int = _ABLATION_MIN_SAMPLE_DEFAULT,
) -> Dict[str, Any]:
    """Per-kill-rule-family EV in R-units → DROP / TUNE / KEEP recommendation.

    Answers the OWNER_BRIEF B17 ablation question: "If we remove kill rule X,
    does the historical cohort's MFE-give-back get worse?"  A rule with
    ev_per_kill_R < -0.20 is silently cutting winners across the cohort and
    is a DROP candidate.

    Aggregates over every classified record (PROTECTIVE / PREMATURE / NEUTRAL).
    INSUFFICIENT_DATA records and unclassified records are excluded.

    Returns ``{by_family, drop_candidates, min_sample_per_family}`` where
    ``by_family[family]`` carries:

    * ``protective_n``, ``premature_n``, ``neutral_n``, ``total``
    * ``saved_R_total``, ``missed_R_total``, ``ev_total_R``, ``ev_per_kill_R``
    * ``recommendation``: "DROP" | "TUNE" | "KEEP" | "INSUFFICIENT_SAMPLE"
    * ``verdict``: one-line human summary string for the truth-report row
    """
    by_family: Dict[str, Dict[str, Any]] = {}
    if not records:
        return {
            "by_family": {},
            "drop_candidates": [],
            "min_sample_per_family": min_sample_per_family,
        }

    for r in records:
        if not isinstance(r, dict):
            continue
        label = r.get("classification")
        if label not in ("PROTECTIVE", "PREMATURE", "NEUTRAL"):
            continue
        family = str(r.get("kill_reason_family") or "other")
        bucket = by_family.setdefault(family, {
            "protective_n": 0,
            "premature_n": 0,
            "neutral_n": 0,
            "total": 0,
            "saved_R_total": 0.0,
            "missed_R_total": 0.0,
        })
        bucket["total"] += 1
        if label == "PROTECTIVE":
            bucket["protective_n"] += 1
        elif label == "PREMATURE":
            bucket["premature_n"] += 1
        else:
            bucket["neutral_n"] += 1
        delta = _record_value_delta_r(r)
        if delta is None:
            continue
        if delta >= 0:
            bucket["saved_R_total"] += delta
        else:
            bucket["missed_R_total"] += -delta

    drop_candidates: List[str] = []
    for family, bucket in by_family.items():
        total = bucket["total"]
        ev_total = bucket["saved_R_total"] - bucket["missed_R_total"]
        ev_per_kill = ev_total / total if total > 0 else 0.0
        bucket["ev_total_R"] = round(ev_total, 3)
        bucket["ev_per_kill_R"] = round(ev_per_kill, 3)
        if total < min_sample_per_family:
            bucket["recommendation"] = "INSUFFICIENT_SAMPLE"
            bucket["verdict"] = (
                f"only {total} classified kills (need >= {min_sample_per_family}); "
                "let data accumulate before tuning"
            )
        elif ev_per_kill < _ABLATION_DROP_EV_THRESHOLD:
            bucket["recommendation"] = "DROP"
            bucket["verdict"] = (
                f"net-hurting: avg {ev_per_kill:+.2f}R/kill across {total} kills "
                f"(missed {bucket['missed_R_total']:.1f}R vs saved {bucket['saved_R_total']:.1f}R)"
            )
            drop_candidates.append(family)
        elif ev_per_kill > _ABLATION_KEEP_EV_THRESHOLD:
            bucket["recommendation"] = "KEEP"
            bucket["verdict"] = (
                f"net-helping: avg {ev_per_kill:+.2f}R/kill across {total} kills "
                f"(saved {bucket['saved_R_total']:.1f}R vs missed {bucket['missed_R_total']:.1f}R)"
            )
        else:
            bucket["recommendation"] = "TUNE"
            bucket["verdict"] = (
                f"marginal: avg {ev_per_kill:+.2f}R/kill across {total} kills — "
                "consider per-setup exemption or threshold adjustment, not full drop"
            )

    return {
        "by_family": by_family,
        "drop_candidates": drop_candidates,
        "min_sample_per_family": min_sample_per_family,
    }


def prune_old_records(
    *,
    retention_sec: float = 7 * 24 * 3600.0,
    now_ts: Optional[float] = None,
    storage_path: Optional[str] = None,
) -> int:
    """Drop records older than `retention_sec`.  Returns count pruned."""
    now_ts = now_ts if now_ts is not None else time.time()
    path = Path(storage_path or _DEFAULT_STORAGE_PATH)
    records = _load_records(path)
    if not records:
        return 0
    cutoff = now_ts - retention_sec
    kept = [r for r in records if float(r.get("kill_timestamp") or 0.0) >= cutoff]
    pruned = len(records) - len(kept)
    if pruned > 0:
        _save_records(path, kept)
    return pruned
