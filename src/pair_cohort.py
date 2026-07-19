"""Pair-cohort dimension for the edge matrix (Phase 5 of the autonomous emission plan).

The Strategy×Context matrix keys on market context (session / phase / volatility /
rotation) — it does not know *what kind of pair* a signal is on.  A path's edge on a
$1B-a-day major behaves nothing like its edge on a thin altcoin, yet both land in the
same cell.  Per-symbol cells would be far too sparse to ever pass the n≥15 floor, so
the tractable dimension is a **liquidity cohort** (MAJOR / MIDCAP / ALTCOIN), reusing
the engine's own volume-tier thresholds.

This module is deliberately tiny and side-effect-free: it maps a symbol+volume to a
cohort bucket and composes the cohort-refined context key
(``"<base_context_key>/<COHORT>"``).  Cohort cells accumulate **in parallel** with the
base cells (additive dual-write at the edge-store feed points) so the base matrix — the
one the live emission policy reads by default — is never fragmented.  The policy reads
the cohort-refined cell only when ``context_emission_cohort_aware`` is flipped ON in ops,
falling back to the base cell when the cohort cell is still thin.
"""
from __future__ import annotations

COHORT_MAJOR = "MAJOR"
COHORT_MIDCAP = "MIDCAP"
COHORT_ALTCOIN = "ALTCOIN"

_COHORTS = frozenset({COHORT_MAJOR, COHORT_MIDCAP, COHORT_ALTCOIN})

# Volume thresholds mirror src/pair_manager.classify_pair_tier — the single source of
# truth for the tier baseline.  Kept in sync here so classification never requires the
# heavy pair_manager import on the pure emission-policy path.
_MAJOR_MIN_USD = 500_000_000.0
_MIDCAP_MIN_USD = 50_000_000.0


def classify_cohort(symbol: str, volume_24h_usd: float = 0.0) -> str:
    """Liquidity cohort for ``symbol``: MAJOR / MIDCAP / ALTCOIN.

    Prefers the canonical per-symbol tier map (``pair_manager.PAIR_TIER_MAP``) when it
    is importable; otherwise falls back to the volume thresholds.  Never raises.
    """
    sym = (symbol or "").upper()
    try:
        from src.pair_manager import PAIR_TIER_MAP

        mapped = PAIR_TIER_MAP.get(sym)
        if mapped in _COHORTS:
            return str(mapped)
    except Exception:
        pass
    try:
        vol = float(volume_24h_usd)
    except (TypeError, ValueError):
        vol = 0.0
    if vol >= _MAJOR_MIN_USD:
        return COHORT_MAJOR
    if vol >= _MIDCAP_MIN_USD:
        return COHORT_MIDCAP
    return COHORT_ALTCOIN


def cohort_context_key(base_context_key: str, cohort: str) -> str:
    """Compose the cohort-refined context key, or the base key if either part is empty."""
    if not base_context_key or not cohort:
        return base_context_key or ""
    return f"{base_context_key}/{cohort}"
