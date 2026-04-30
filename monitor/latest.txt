# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **QUIET_COMPRESSION_BREAK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `26691` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 12 | 12 | 10 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 3805 | 3805 | 3802 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 384 | 384 | 19 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 4817410 | 4817398 | 12 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 4817410 | 4813605 | 3805 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 4817410 | 4817026 | 384 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 4817410 | 4430222 | 387188 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FUNDING_EXTREME | 4817410 | 4806731 | 10679 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 4817410 | 4817410 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 4817410 | 4817410 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 4817410 | 4817410 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 4817410 | 4727123 | 90287 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 4817410 | 4606025 | 211385 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::STANDARD | 4817410 | 4731754 | 85656 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 4817410 | 4816754 | 656 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 4817410 | 4817410 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 4817410 | 4817410 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 387188 | 387188 | 327927 | 38 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 10679 | 10679 | 10457 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 85656 | 85656 | 81045 | 8 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 90287 | 90287 | 19583 | 85 | active-low-quality (none) |
| SR_FLIP_RETEST | 0 | 0 | 211385 | 211385 | 170992 | 44 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 656 | 656 | 656 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=4817398): regime_blocked=2957141, volume_spike_missing=1260616, basic_filters_failed=432575, breakout_not_found=121084, retest_proximity_failed=45921, insufficient_candles=61
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=4813605): regime_blocked=4668825, ema_alignment_reject=65090, basic_filters_failed=36609, sweeps_not_detected=25330, adx_reject=13356, momentum_reject=4222, reclaim_confirmation_failed=171, rsi_reject=2
- **EVAL::DIVERGENCE_CONTINUATION** (total=4817026): regime_blocked=4668825, cvd_divergence_failed=65346, basic_filters_failed=36609, missing_cvd=33670, ema_alignment_reject=6774, retest_proximity_failed=5752, cvd_insufficient=50
- **EVAL::FAILED_AUCTION_RECLAIM** (total=4430222): regime_blocked=1548707, basic_filters_failed=1183309, auction_not_detected=901209, reclaim_hold_failed=413889, tail_too_small=362440, adx_reject=18791, rsi_reject=1877
- **EVAL::FUNDING_EXTREME** (total=4806731): funding_not_extreme=3039332, basic_filters_failed=1478781, missing_funding_rate=190423, ema_alignment_reject=45724, rsi_reject=40482, cvd_divergence_failed=10173, momentum_reject=1816
- **EVAL::LIQUIDATION_REVERSAL** (total=4817410): cascade_threshold_not_met=3266348, basic_filters_failed=1522995, cvd_divergence_failed=25223, missing_cvd=2844
- **EVAL::OPENING_RANGE_BREAKOUT** (total=4817410): regime_blocked=4562945, feature_disabled=254465
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=4817410): regime_blocked=4668825, ema_alignment_reject=65090, basic_filters_failed=36609, breakout_not_found=33530, adx_reject=13356
- **EVAL::QUIET_COMPRESSION_BREAK** (total=4727123): regime_blocked=1697292, breakout_not_detected=1280227, basic_filters_failed=1146700, compression_not_detected=310252, volume_reject=193089, missing_fvg_or_orderblock=51038, macd_reject=39724, rsi_reject=8801
- **EVAL::SR_FLIP_RETEST** (total=4606025): regime_blocked=1548707, basic_filters_failed=1169760, reclaim_hold_failed=664528, flip_close_not_confirmed=535744, retest_out_of_zone=423626, wick_quality_failed=160068, missing_fvg_or_orderblock=62825, rsi_reject=16829, insufficient_candles=16229, ema_alignment_reject=7709
- **EVAL::STANDARD** (total=4731754): momentum_reject=1841623, basic_filters_failed=1193796, adx_reject=888693, sweeps_not_detected=557724, ema_alignment_reject=183929, insufficient_candles=42264, rsi_reject=22343, invalid_sl_geometry=731, macd_reject=641, htf_ema_reject=10
- **EVAL::TREND_PULLBACK** (total=4816754): regime_blocked=4668825, ema_alignment_reject=65090, basic_filters_failed=36608, rsi_reject=16746, ema_not_tested_prev=11358, no_ema_reclaim_close=7849, body_conviction_fail=7617, prev_already_above_emas=2638, prev_already_below_emas=7, missing_fvg_or_orderblock=4, no_prev_low_break=4, momentum_flat=4, ema21_not_tagged=2, insufficient_candles=1, no_prev_high_break=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=4817410): regime_blocked=2957141, volume_spike_missing=1167804, basic_filters_failed=432575, breakout_not_found=133840, retest_proximity_failed=125988, insufficient_candles=61, ema_alignment_reject=1
- **EVAL::WHALE_MOMENTUM** (total=4817410): regime_blocked=2957141, momentum_reject=1860269

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| VOLATILE | 117948 | 83.9% |
| QUIET | 22609 | 16.1% |
| TRENDING_UP | 43 | 0.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **19085**
- Average confidence gap to threshold: **14.83** (samples=19085) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BCHUSDT=2510, TRXUSDT=2492, SUIUSDT=2189, AVAXUSDT=2060, ENSOUSDT=1891, LTCUSDT=1397, HUSDT=741, NOTUSDT=591, LYNUSDT=548, 1000BONKUSDT=438

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 2 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 1 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | watchlist_tier_keep | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 362 |
| DIVERGENCE_CONTINUATION | kept | watchlist_tier_keep | 2 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 1 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 39616 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 6572 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 3213 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 187 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 36 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 2547 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 857 |
| LIQUIDITY_SWEEP_REVERSAL | kept | watchlist_tier_keep | 872 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 49392 |
| QUIET_COMPRESSION_BREAK | kept | watchlist_tier_keep | 21687 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 4 |
| SR_FLIP_RETEST | filtered | min_confidence | 10465 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 9779 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 1522 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `23259716`
- `Path funnel` emissions: `830`
- `Regime distribution` emissions: `19`
- `QUIET_SCALP_BLOCK` events: `88808`
- `confidence_gate` events: `147126`

## Dependency readiness
- cvd: presence[absent=1841969, present=2975441] state[empty=1841969, populated=2975441] buckets[few=47, many=1603609, none=1841969, some=1371785] sources[none] quality[none]
- funding_rate: presence[absent=190423, present=4626987] state[empty=190423, populated=4626987] buckets[few=4626987, none=190423] sources[none] quality[none]
- liquidation_clusters: presence[absent=4817410] state[empty=4817410] buckets[none=4817410] sources[none] quality[none]
- oi_snapshot: presence[absent=81688, present=4735722] state[empty=81688, populated=4735722] buckets[few=2738, many=4718359, none=81688, some=14625] sources[none] quality[none]
- order_book: presence[absent=320097, present=4497313] state[populated=4497313, unavailable=320097] buckets[few=4497313, none=320097] sources[book_ticker=4497313, unavailable=320097] quality[none=320097, top_of_book_only=4497313]
- orderblocks: presence[absent=4817410] state[empty=4817410] buckets[none=4817410] sources[not_implemented=4817410] quality[none]
- recent_ticks: presence[absent=252212, present=4565198] state[empty=252212, populated=4565198] buckets[many=4565198, none=252212] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.8918771743774414` sec
- Median create→first breach: `None` sec
- Median create→terminal: `610.3321421146393` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.2838 | None | 610.3321421146393 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 0.0 | 0.0 | 0.0 | -0.0558 | None | 609.8672565221786 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 211385 | 44 | 170992 | 0.0 | 0.0 | None | None | 40393 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 656 | 0 | 656 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-706`
- Gating Δ: `496026`
- No-generation Δ: `51324027`
- Fast failures Δ: `0`
- Quality changes: `{"QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.0558, "current_avg_pnl": -0.0558, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.0872, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.0872, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -396, "geometry_changed_delta": 0, "geometry_preserved_delta": 15075, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -1615.47, "median_terminal_delta_sec": -810.16, "sl_rate_delta": -3.7, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -8, "geometry_changed_delta": 0, "geometry_preserved_delta": -50, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -629.84, "median_terminal_delta_sec": -631.06, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **QUIET_COMPRESSION_BREAK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **QUIET_COMPRESSION_BREAK**
