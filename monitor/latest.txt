# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `16625` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 38 | 38 | 38 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 17 | 17 | 17 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 2865 | 2865 | 2535 | 9 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1607651 | 1607613 | 38 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1607651 | 1607634 | 17 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1607651 | 1604786 | 2865 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1607651 | 1531086 | 76565 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1607651 | 1602331 | 5320 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1607651 | 1607651 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 1607651 | 1607651 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1607651 | 1607651 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1607651 | 1597007 | 10644 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1607651 | 1532646 | 75005 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1607651 | 1522814 | 84837 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1607651 | 1607645 | 6 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1607651 | 1607642 | 9 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 1607651 | 1607651 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 76565 | 76565 | 64622 | 35 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 5320 | 5320 | 5320 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 84837 | 84837 | 73317 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 10644 | 10644 | 9626 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 75005 | 75005 | 31942 | 133 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 6 | 6 | 5 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 9 | 9 | 7 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1607613): regime_blocked=786676, breakout_not_found=516214, basic_filters_failed=211456, retest_proximity_failed=91751, volume_spike_missing=1474, ema_alignment_reject=41, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1607634): regime_blocked=1090596, sweeps_not_detected=195031, basic_filters_failed=150727, ema_alignment_reject=149677, adx_reject=19317, momentum_reject=1781, reclaim_confirmation_failed=491, rsi_reject=14
- **EVAL::DIVERGENCE_CONTINUATION** (total=1604786): regime_blocked=1090596, cvd_divergence_failed=285383, basic_filters_failed=150727, missing_cvd=53812, ema_alignment_reject=14700, retest_proximity_failed=9546, missing_fvg_or_orderblock=22
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1531086): auction_not_detected=540873, basic_filters_failed=448675, regime_blocked=302056, reclaim_hold_failed=133385, tail_too_small=105522, rsi_reject=575
- **EVAL::FUNDING_EXTREME** (total=1602331): funding_not_extreme=1064219, basic_filters_failed=507151, rsi_reject=11287, ema_alignment_reject=11121, missing_funding_rate=6642, momentum_reject=1707, cvd_divergence_failed=204
- **EVAL::LIQUIDATION_REVERSAL** (total=1607651): cascade_threshold_not_met=1061719, basic_filters_failed=509370, cvd_divergence_failed=35947, rsi_reject=614, missing_cvd=1
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1607651): feature_disabled=1607651
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1607651): regime_blocked=1090596, breakout_not_found=197334, basic_filters_failed=150727, ema_alignment_reject=149677, adx_reject=19317
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1597007): regime_blocked=819111, basic_filters_failed=297948, breakout_not_detected=286164, compression_not_detected=166770, rsi_reject=15970, missing_fvg_or_orderblock=6578, macd_reject=4466
- **EVAL::SR_FLIP_RETEST** (total=1532646): basic_filters_failed=444397, retest_out_of_zone=406770, regime_blocked=302056, flip_close_not_confirmed=181107, reclaim_hold_failed=155791, wick_quality_failed=15749, missing_fvg_or_orderblock=9959, rsi_reject=7581, insufficient_candles=7230, ema_alignment_reject=2006
- **EVAL::STANDARD** (total=1522814): momentum_reject=448234, basic_filters_failed=424744, adx_reject=263194, sweeps_not_detected=190102, ema_alignment_reject=146407, macd_reject=18473, insufficient_candles=13278, rsi_reject=9938, invalid_sl_geometry=8439, htf_ema_reject=5
- **EVAL::TREND_PULLBACK** (total=1607645): regime_blocked=1090596, ema_not_tested_prev=152938, ema_alignment_reject=149654, basic_filters_failed=147834, no_ema_reclaim_close=26232, body_conviction_fail=13381, rsi_reject=10986, prev_already_above_emas=10335, insufficient_candles=5303, ema21_not_tagged=353, prev_already_below_emas=17, no_prev_high_break=9, no_prev_low_break=4, missing_fvg_or_orderblock=2, momentum_flat=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1607642): regime_blocked=786676, breakout_not_found=358735, retest_proximity_failed=231552, basic_filters_failed=211456, volume_spike_missing=19205, ema_alignment_reject=11, rsi_reject=7
- **EVAL::WHALE_MOMENTUM** (total=1607651): momentum_reject=820975, regime_blocked=786676

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 910058 | 46.3% |
| TRENDING_UP | 646306 | 32.9% |
| VOLATILE | 396395 | 20.2% |
| TRENDING_DOWN | 11680 | 0.6% |
| RANGING | 1891 | 0.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **4606**
- Average confidence gap to threshold: **18.89** (samples=4606) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=1315, SIRENUSDT=572, ZENUSDT=431, TRXUSDT=426, EWYUSDT=321, FILUSDT=268, ONDOUSDT=233, WLFIUSDT=224, SOLUSDT=101, 币安人生USDT=86

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 115 |
| DIVERGENCE_CONTINUATION | kept | watchlist_tier_keep | 230 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 5491 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 706 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 5531 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 10068 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 895 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 641 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 396 |
| QUIET_COMPRESSION_BREAK | kept | watchlist_tier_keep | 1 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 2364 |
| SR_FLIP_RETEST | filtered | min_confidence | 1410 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 12489 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 68 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 1 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 1 |
| VOLUME_SURGE_BREAKOUT | kept | watchlist_tier_keep | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 115 | 49.20 | 80.00 | 30.80 | 20.72 | 19.91 | 19.89 | 1.14 | 4.38 |
| DIVERGENCE_CONTINUATION | kept | 230 | 50.84 | 50.00 | -0.84 | 20.81 | 19.90 | 20.00 | 0.14 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 6197 | 65.57 | 78.29 | 12.72 | 20.08 | 19.59 | 14.00 | 4.17 | 1.87 |
| FAILED_AUCTION_RECLAIM | kept | 5531 | 50.31 | 50.00 | -0.31 | 23.10 | 18.00 | 14.00 | 1.00 | 5.99 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 10963 | 70.10 | 78.78 | 8.68 | 21.03 | 19.15 | 15.20 | 3.02 | 0.44 |
| QUIET_COMPRESSION_BREAK | filtered | 1037 | 52.69 | 70.73 | 18.04 | 19.42 | 18.74 | 15.86 | 0.00 | 3.81 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 53.70 | 50.00 | -3.70 | 21.60 | 20.00 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 3774 | 44.37 | 70.60 | 26.23 | 21.34 | 20.00 | 15.22 | 1.66 | 4.97 |
| SR_FLIP_RETEST | kept | 12557 | 57.26 | 50.16 | -7.10 | 21.20 | 20.00 | 15.20 | 1.33 | 10.70 |
| TREND_PULLBACK_EMA | kept | 1 | 80.50 | 80.00 | -0.50 | 20.20 | 18.90 | 17.70 | 5.50 | 0.00 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 68.50 | 80.00 | 11.50 | 21.40 | 20.00 | 16.00 | 1.50 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 53.50 | 50.00 | -3.50 | 22.90 | 19.10 | 20.00 | 1.50 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 115 | 49.20 | 25.00 | 18.00 | 3.00 | 10.31 | 5.00 | 4.83 | 1.14 |
| DIVERGENCE_CONTINUATION | kept | 230 | 50.84 | 24.90 | 18.00 | 3.01 | 10.01 | 5.00 | 4.71 | 0.14 |
| FAILED_AUCTION_RECLAIM | filtered | 6197 | 65.57 | 23.02 | 14.00 | 3.16 | 10.28 | 7.67 | 7.33 | 4.17 |
| FAILED_AUCTION_RECLAIM | kept | 5531 | 50.31 | 17.00 | 14.00 | 3.00 | 11.00 | 5.00 | 5.30 | 1.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 10963 | 70.10 | 24.33 | 14.00 | 3.17 | 12.14 | 7.75 | 6.75 | 3.02 |
| QUIET_COMPRESSION_BREAK | filtered | 1037 | 52.69 | 18.20 | 18.00 | 3.62 | 15.39 | 5.60 | 4.24 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 53.70 | 17.00 | 8.00 | 3.00 | 17.00 | 5.00 | 3.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 3774 | 44.37 | 19.48 | 11.64 | 3.35 | 14.35 | 5.04 | 5.23 | 1.66 |
| SR_FLIP_RETEST | kept | 12557 | 57.26 | 16.90 | 18.00 | 3.05 | 11.06 | 7.67 | 9.95 | 1.33 |
| TREND_PULLBACK_EMA | kept | 1 | 80.50 | 17.00 | 18.00 | 3.00 | 17.00 | 10.00 | 10.00 | 5.50 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 68.50 | 17.00 | 18.00 | 3.00 | 14.00 | 8.00 | 10.00 | 1.50 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 53.50 | 2.00 | 18.00 | 6.00 | 11.00 | 5.00 | 10.00 | 1.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 115 | 49.20 | 0.00 | 0.00 | 4.38 | 0.00 | 0.00 | 0.00 | **4.38** |
| DIVERGENCE_CONTINUATION | kept | 230 | 50.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 6197 | 65.57 | 0.00 | 0.00 | 1.13 | 0.00 | 0.11 | 0.00 | **1.24** |
| FAILED_AUCTION_RECLAIM | kept | 5531 | 50.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 10963 | 70.10 | 0.00 | 0.00 | 0.44 | 0.00 | 0.00 | 0.00 | **0.44** |
| QUIET_COMPRESSION_BREAK | filtered | 1037 | 52.69 | 0.08 | 0.00 | 0.17 | 0.00 | 0.21 | 0.00 | **0.46** |
| QUIET_COMPRESSION_BREAK | kept | 1 | 53.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 3774 | 44.37 | 0.03 | 0.00 | 0.07 | 0.00 | 0.10 | 0.00 | **0.20** |
| SR_FLIP_RETEST | kept | 12557 | 57.26 | 0.00 | 0.00 | 2.00 | 0.00 | 0.00 | 0.00 | **2.00** |
| TREND_PULLBACK_EMA | kept | 1 | 80.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 68.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 53.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=5 (50.0%) | PREMATURE=0 (0.0%) | NEUTRAL=5 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 5 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| momentum_loss | 5 | 0 | 5 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| QUIET_COMPRESSION_BREAK | 2 | 0 | 2 | 0 |
| SR_FLIP_RETEST | 3 | 0 | 3 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `8060657`
- `Path funnel` emissions: `266`
- `Regime distribution` emissions: `266`
- `QUIET_SCALP_BLOCK` events: `4606`
- `confidence_gate` events: `40408`
- `free_channel_post` events: `8`
- `pre_tp_fire` events: `1`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **1**
- Avg resolved threshold: **0.350%** raw → avg net **+2.80%** @ 10x
- Avg time-to-fire from dispatch: **48s**
- By threshold source: static=1

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| TREND_PULLBACK_EMA | 1 | 0.350% | +2.80% | 48 | static=1 |
- Top symbols: SKYAIUSDT=1

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **8**

| Source | Count |
|---|---:|
| regime_shift | 6 |
| pre_tp | 1 |
| signal_close | 1 |

- By severity: HIGH=8

## Dependency readiness
- cvd: presence[absent=248284, present=1359367] state[empty=248284, populated=1359367] buckets[few=3, many=570162, none=248284, some=789202] sources[none] quality[none]
- funding_rate: presence[absent=6642, present=1601009] state[empty=6642, populated=1601009] buckets[few=1601009, none=6642] sources[none] quality[none]
- liquidation_clusters: presence[absent=1607651] state[empty=1607651] buckets[none=1607651] sources[none] quality[none]
- oi_snapshot: presence[absent=175, present=1607476] state[empty=175, populated=1607476] buckets[few=702, many=1602937, none=175, some=3837] sources[none] quality[none]
- order_book: presence[absent=86885, present=1520766] state[populated=1520766, unavailable=86885] buckets[few=1520766, none=86885] sources[book_ticker=1520766, unavailable=86885] quality[none=86885, top_of_book_only=1520766]
- orderblocks: presence[absent=1607651] state[empty=1607651] buckets[none=1607651] sources[not_implemented=1607651] quality[none]
- recent_ticks: presence[absent=119681, present=1487970] state[empty=119681, populated=1487970] buckets[many=1487970, none=119681] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `0.9086143970489502` sec
- Median create→first breach: `49.18510413169861` sec
- Median create→terminal: `641.3619529008865` sec
- Median first breach→terminal: `0.21996188163757324` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 100.0}, "under_180s": {"count": 1, "pct": 100.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 100.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 5 | 5 | 0.0 | 0.0 | 0.0 | -0.1748 | None | 643.4388978481293 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 49.18510413169861 | 49.40506601333618 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 75005 | 133 | 31942 | 0.0 | 0.0 | None | 643.4388978481293 | 43063 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 6 | 1 | 5 | 0.0 | 0.0 | 49.18510413169861 | 49.40506601333618 | 1 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-11`
- Gating Δ: `57128`
- No-generation Δ: `1756595`
- Fast failures Δ: `1`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": -0.2109, "current_avg_pnl": -0.1748, "current_win_rate": 0.0, "previous_avg_pnl": 0.0361, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 27, "geometry_changed_delta": 0, "geometry_preserved_delta": 8580, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 36.41, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 49.19, "median_terminal_delta_sec": 49.41, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **SR_FLIP_RETEST**
