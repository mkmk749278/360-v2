# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: FAILED_AUCTION_RECLAIM, LIQUIDITY_SWEEP_REVERSAL, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **FAILED_AUCTION_RECLAIM**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `1346` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 247 | 247 | 245 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 446 | 446 | 446 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1970049 | 1970049 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1970049 | 1969802 | 247 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1970049 | 1969603 | 446 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1970049 | 1939086 | 30963 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FUNDING_EXTREME | 1970049 | 1968836 | 1213 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1970049 | 1970049 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1970049 | 1970049 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1970049 | 1970049 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1970049 | 1970049 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1970049 | 1969274 | 775 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1970049 | 1947194 | 22855 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::STANDARD | 1970049 | 1964958 | 5091 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1970049 | 1970048 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1970049 | 1970037 | 12 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1970049 | 1970049 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 30963 | 30963 | 10116 | 68 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1213 | 1213 | 1213 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 5091 | 5091 | 4255 | 6 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 775 | 775 | 576 | 7 | active-low-quality (none) |
| SR_FLIP_RETEST | 0 | 0 | 22855 | 22855 | 1080 | 22 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 12 | 12 | 12 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1970049): breakout_not_found=1475879, basic_filters_failed=415097, retest_proximity_failed=77644, volume_spike_missing=790, ema_alignment_reject=326, missing_fvg_or_orderblock=313
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1969802): regime_blocked=1581378, sweeps_not_detected=126796, basic_filters_failed=109797, ema_alignment_reject=99434, rsi_reject=40226, momentum_reject=10154, adx_reject=2002, reclaim_confirmation_failed=15
- **EVAL::DIVERGENCE_CONTINUATION** (total=1969603): regime_blocked=1581378, cvd_divergence_failed=196035, basic_filters_failed=109797, retest_proximity_failed=62927, cvd_insufficient=13893, missing_cvd=4677, ema_alignment_reject=896
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1939086): regime_blocked=1262361, auction_not_detected=315492, basic_filters_failed=188030, reclaim_hold_failed=114013, tail_too_small=58708, rsi_reject=482
- **EVAL::FUNDING_EXTREME** (total=1968836): funding_not_extreme=1493866, basic_filters_failed=413632, rsi_reject=28150, ema_alignment_reject=24750, missing_funding_rate=5899, momentum_reject=1874, cvd_divergence_failed=665
- **EVAL::LIQUIDATION_REVERSAL** (total=1970049): cascade_threshold_not_met=1531519, basic_filters_failed=415097, cvd_divergence_failed=23433
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1970049): no_ma_cross=1554952, basic_filters_failed=415097
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1970049): feature_disabled=1970049
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1970049): regime_blocked=1581378, breakout_not_found=177438, basic_filters_failed=109797, ema_alignment_reject=99434, adx_reject=2002
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1969274): regime_blocked=1651032, compression_not_detected=96874, breakout_not_detected=88718, basic_filters_failed=78233, macd_reject=30280, rsi_reject=23396, missing_fvg_or_orderblock=741
- **EVAL::SR_FLIP_RETEST** (total=1947194): regime_blocked=1262361, basic_filters_failed=188030, flip_close_not_confirmed=179106, retest_out_of_zone=117815, reclaim_hold_failed=113202, wick_quality_failed=53106, rsi_reject=29038, missing_fvg_or_orderblock=2374, ema_alignment_reject=2162
- **EVAL::STANDARD** (total=1964958): momentum_reject=979323, basic_filters_failed=386756, adx_reject=198431, ema_alignment_reject=176048, sweeps_not_detected=143865, rsi_reject=76654, macd_reject=3518, invalid_sl_geometry=361, htf_ema_reject=2
- **EVAL::TREND_PULLBACK** (total=1970048): regime_blocked=1581378, ema_not_tested_prev=145125, basic_filters_failed=109797, ema_alignment_reject=99434, rsi_reject=15201, body_conviction_fail=9997, no_ema_reclaim_close=8768, prev_already_above_emas=334, prev_already_below_emas=7, no_prev_low_break=3, no_prev_high_break=3, ema21_not_tagged=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1970037): breakout_not_found=1048155, retest_proximity_failed=446593, basic_filters_failed=415097, rsi_reject=31087, volume_spike_missing=29105
- **EVAL::WHALE_MOMENTUM** (total=1970049): momentum_reject=1968652, recent_ticks_insufficient=1397

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| VOLATILE | 1468314 | 63.5% |
| QUIET | 380522 | 16.5% |
| TRENDING_UP | 365967 | 15.8% |
| TRENDING_DOWN | 87071 | 3.8% |
| RANGING | 10141 | 0.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **18**
- Average confidence gap to threshold: **14.06** (samples=18) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ZECUSDT=6, SKYAIUSDT=5, DOGEUSDT=3, SOLUSDT=2, ETHUSDT=1, BTCUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 10 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 19718 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 84 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 3 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 122 |
| SR_FLIP_RETEST | filtered | min_confidence | 193 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1948 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 10 | 47.88 | 65.00 | 17.12 | 20.31 | 20.00 | 14.00 | 3.80 | 19.12 |
| FAILED_AUCTION_RECLAIM | kept | 19718 | 72.00 | 65.00 | -7.00 | 21.04 | 20.00 | 14.00 | 5.01 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 6 | 50.62 | 65.00 | 14.38 | 21.25 | 20.00 | 15.20 | 2.83 | 20.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 84 | 74.56 | 65.00 | -9.56 | 23.43 | 19.86 | 15.20 | 0.06 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 3 | 63.40 | 65.00 | 1.60 | 23.53 | 17.90 | 15.80 | 0.00 | 4.30 |
| QUIET_COMPRESSION_BREAK | kept | 122 | 75.55 | 65.00 | -10.55 | 23.28 | 17.49 | 15.80 | 0.00 | -2.90 |
| SR_FLIP_RETEST | filtered | 193 | 45.84 | 65.00 | 19.16 | 21.15 | 20.00 | 15.21 | 2.46 | 8.99 |
| SR_FLIP_RETEST | kept | 1948 | 66.94 | 65.00 | -1.94 | 21.70 | 20.00 | 15.46 | 2.50 | 3.58 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 10 | 47.88 | 17.00 | 14.00 | 9.90 | 10.40 | 7.20 | 7.70 | 3.80 |
| FAILED_AUCTION_RECLAIM | kept | 19718 | 72.00 | 25.00 | 14.11 | 3.02 | 12.00 | 4.99 | 7.87 | 5.01 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 6 | 50.62 | 23.67 | 15.00 | 6.00 | 11.83 | 2.92 | 8.37 | 2.83 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 84 | 74.56 | 24.98 | 14.00 | 8.61 | 14.01 | 4.97 | 7.93 | 0.06 |
| QUIET_COMPRESSION_BREAK | filtered | 3 | 63.40 | 17.00 | 18.00 | 9.00 | 14.00 | 5.00 | 4.70 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 122 | 75.55 | 17.00 | 18.00 | 11.61 | 14.00 | 5.09 | 9.85 | 0.00 |
| SR_FLIP_RETEST | filtered | 193 | 45.84 | 24.75 | 18.00 | 3.06 | 11.12 | 5.02 | 5.34 | 2.46 |
| SR_FLIP_RETEST | kept | 1948 | 66.94 | 24.98 | 8.07 | 3.17 | 16.82 | 8.29 | 6.89 | 2.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 10 | 47.88 | 0.00 | 0.00 | 0.00 | 0.00 | 15.12 | 0.00 | **15.12** |
| FAILED_AUCTION_RECLAIM | kept | 19718 | 72.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 6 | 50.62 | 0.00 | 0.00 | 2.00 | 0.00 | 18.00 | 0.00 | **20.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 84 | 74.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 3 | 63.40 | 0.00 | 0.00 | 0.00 | 0.00 | 4.30 | 0.00 | **4.30** |
| QUIET_COMPRESSION_BREAK | kept | 122 | 75.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 193 | 45.84 | 0.03 | 0.00 | 1.17 | 0.00 | 0.00 | 0.00 | **1.20** |
| SR_FLIP_RETEST | kept | 1948 | 66.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=12 (27.3%) | PREMATURE=2 (4.5%) | NEUTRAL=30 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 10 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| ema_crossover | 6 | 1 | 28 | 0 |
| other | 5 | 0 | 1 | 0 |
| regime_shift | 1 | 1 | 1 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 6 | 0 | 27 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 2 | 2 | 0 |
| QUIET_COMPRESSION_BREAK | 1 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 4 | 0 | 1 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `10021911`
- `Path funnel` emissions: `309`
- `Regime distribution` emissions: `309`
- `QUIET_SCALP_BLOCK` events: `18`
- `confidence_gate` events: `22084`
- `free_channel_post` events: `15`
- `pre_tp_fire` events: `5`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **5**
- Avg resolved threshold: **0.200%** raw → avg net **+1.30%** @ 10x
- Avg time-to-fire from dispatch: **811s**
- By threshold source: stamped=5

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 2 | 0.200% | +1.30% | 925 | stamped=2 |
| QUIET_COMPRESSION_BREAK | 1 | 0.200% | +1.30% | 925 | stamped=1 |
| FAILED_AUCTION_RECLAIM | 1 | 0.200% | +1.30% | 357 | stamped=1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 0.200% | +1.30% | 923 | stamped=1 |
- Top symbols: SOLUSDT=3, BZUSDT=1, DOGEUSDT=1

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **62**
- Total REST-fallback activations: **74**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 60 | 2302 | 3849 | 4372 | 0 |
| futures_liq | 2 | 1610 | 1610 | 1915 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 74 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **15**

| Source | Count |
|---|---:|
| pre_tp | 5 |
| regime_shift | 5 |
| signal_close | 4 |
| signal_highlight | 1 |

- By severity: HIGH=15

## Dependency readiness
- cvd: presence[absent=97358, present=1872692] state[empty=97358, populated=1872692] buckets[many=1758763, none=97358, some=113929] sources[none] quality[none]
- funding_rate: presence[absent=5900, present=1964150] state[empty=5900, populated=1964150] buckets[few=1964150, none=5900] sources[none] quality[none]
- liquidation_clusters: presence[absent=1970050] state[empty=1970050] buckets[none=1970050] sources[none] quality[none]
- oi_snapshot: presence[absent=698, present=1969352] state[empty=698, populated=1969352] buckets[few=1329, many=1961453, none=698, some=6570] sources[none] quality[none]
- order_book: presence[absent=61890, present=1908160] state[populated=1908160, unavailable=61890] buckets[few=1908160, none=61890] sources[book_ticker=1908160, unavailable=61890] quality[none=61890, top_of_book_only=1908160]
- orderblocks: presence[absent=1970050] state[empty=1970050] buckets[none=1970050] sources[not_implemented=1970050] quality[none]
- recent_ticks: presence[absent=75462, present=1894588] state[empty=75462, populated=1894588] buckets[many=1894588, none=75462] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.0675389766693115` sec
- Median create→first breach: `1861.2719069719315` sec
- Median create→terminal: `1503.5180308818817` sec
- Median first breach→terminal: `0.3891880512237549` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 7 | 7 | 0.0 | 14.3 | 0.0 | -0.1021 | 2629.010556936264 | 1835.2621788978577 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 4 | 0.0 | 0.0 | 0.0 | -0.0317 | 1887.537822008133 | 607.129791021347 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 0.0 | 0.0 | 0.4506 | 925.4697618484497 | 937.8723014593124 |
| SR_FLIP_RETEST | 13 | 13 | 0.0 | 0.0 | 0.0 | 0.2147 | None | 2904.7124609947205 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 22855 | 22 | 1080 | 0.0 | 0.0 | None | 2904.7124609947205 | 21775 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1 | 0 | 1 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-16`
- Gating Δ: `-75659`
- No-generation Δ: `6931135`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.1056, "current_avg_pnl": -0.1021, "current_win_rate": 0.0, "previous_avg_pnl": 0.0035, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.1796, "current_avg_pnl": -0.0317, "current_win_rate": 0.0, "previous_avg_pnl": 0.1479, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.4734, "current_avg_pnl": 0.4506, "current_win_rate": 0.0, "previous_avg_pnl": -0.0228, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.2098, "current_avg_pnl": 0.2147, "current_win_rate": 0.0, "previous_avg_pnl": 0.0049, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -10, "geometry_changed_delta": 0, "geometry_preserved_delta": -23370, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 2000.19, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": -1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **FAILED_AUCTION_RECLAIM**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **FAILED_AUCTION_RECLAIM**
